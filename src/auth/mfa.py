import secrets
import time
from typing import Optional
from dataclasses import dataclass

try:
    import pyotp
except ImportError:
    pyotp = None

try:
    import smtplib
    from email.mime.text import MIMEText
except ImportError:
    smtplib = None


@dataclass
class OTPResult:
    success: bool
    message: str
    otp: Optional[str] = None


class MFAManager:
    OTP_LENGTH = 6
    OTP_EXPIRY = 300  # 5 minutes
    TOTP_INTERVAL = 30

    def __init__(self, db=None):
        self._db = db

    def generate_totp_secret(self) -> str:
        if pyotp is None:
            return secrets.token_hex(20)
        return pyotp.random_base32()

    def get_totp_uri(self, secret: str, email: str, issuer: str = "ExpenseTracker") -> str:
        if pyotp is None:
            return ""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    def verify_totp(self, secret: str, code: str) -> bool:
        if pyotp is None:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def generate_email_otp(self, email: str) -> OTPResult:
        otp = "".join([str(secrets.randbelow(10)) for _ in range(self.OTP_LENGTH)])
        expires_at = int(time.time()) + self.OTP_EXPIRY
        if self._db:
            if self._db.is_postgres:
                self._db.execute(
                    "INSERT INTO otp_codes (email, code, expires_at) VALUES (%s, %s, %s)",
                    (email, otp, expires_at),
                )
            else:
                self._db.execute(
                    "INSERT INTO otp_codes (email, code, expires_at) VALUES (?, ?, ?)",
                    (email, otp, expires_at),
                )
        sent = self._send_email(email, otp)
        if sent:
            return OTPResult(success=True, message="OTP sent to email", otp=otp)
        return OTPResult(success=False, message="Failed to send email")

    def verify_email_otp(self, email: str, code: str) -> bool:
        if not self._db:
            return False
        now = int(time.time())
        if self._db.is_postgres:
            row = self._db.execute_one(
                "SELECT id FROM otp_codes "
                "WHERE email = %s AND code = %s AND expires_at > %s "
                "ORDER BY id DESC LIMIT 1",
                (email, code, now),
            )
        else:
            row = self._db.execute_one(
                "SELECT id FROM otp_codes "
                "WHERE email = ? AND code = ? AND expires_at > ? "
                "ORDER BY id DESC LIMIT 1",
                (email, code, now),
            )
        if row:
            otp_id = dict(row).get("id")
            if otp_id:
                if self._db.is_postgres:
                    self._db.execute(
                        "DELETE FROM otp_codes WHERE id = %s", (otp_id,)
                    )
                else:
                    self._db.execute(
                        "DELETE FROM otp_codes WHERE id = ?", (otp_id,)
                    )
                return True
        return False

    def cleanup_expired(self):
        if not self._db:
            return
        now = int(time.time())
        if self._db.is_postgres:
            self._db.execute(
                "DELETE FROM otp_codes WHERE expires_at < %s", (now,)
            )
        else:
            self._db.execute(
                "DELETE FROM otp_codes WHERE expires_at < ?", (now,)
            )

    def _send_email(self, to_email: str, otp: str) -> bool:
        try:
            if smtplib is None:
                return True
            from src.config import ConfigManager
            config = ConfigManager()
            smtp_host = config.get("smtp_host", "")
            smtp_port = int(config.get("smtp_port", 587))
            smtp_user = config.get("smtp_user", "")
            smtp_pass = config.get("smtp_password", "")
            from_email = config.get("smtp_from", smtp_user)
            if not smtp_host or not smtp_user:
                return True
            msg = MIMEText(
                f"Your verification code is: {otp}\n\n"
                f"This code expires in 5 minutes.\n"
                f"If you did not request this, please ignore this email."
            )
            msg["Subject"] = "Expense Tracker - Verification Code"
            msg["From"] = from_email
            msg["To"] = to_email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, to_email, msg.as_string())
            return True
        except Exception:
            return True
