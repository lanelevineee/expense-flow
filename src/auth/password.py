import secrets
import string
import bcrypt


class PasswordManager:
    MIN_LENGTH = 8

    @staticmethod
    def hash_password(plain: str) -> str:
        if len(plain) < PasswordManager.MIN_LENGTH:
            raise ValueError(
                f"Password must be at least {PasswordManager.MIN_LENGTH} characters"
            )
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            return False

    @staticmethod
    def generate_temporary(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def validate_strength(plain: str) -> tuple:
        errors = []
        if len(plain) < PasswordManager.MIN_LENGTH:
            errors.append(f"Must be at least {PasswordManager.MIN_LENGTH} characters")
        if not any(c.isupper() for c in plain):
            errors.append("Must contain at least one uppercase letter")
        if not any(c.islower() for c in plain):
            errors.append("Must contain at least one lowercase letter")
        if not any(c.isdigit() for c in plain):
            errors.append("Must contain at least one digit")
        return (len(errors) == 0, errors)
