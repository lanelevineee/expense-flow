import time
from typing import Optional
from dataclasses import dataclass

from src.config import ConfigManager

try:
    import jwt
except ImportError:
    jwt = None


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int


class SessionManager:
    ACCESS_EXPIRY = 3600  # 1 hour
    REFRESH_EXPIRY = 604800  # 7 days

    def __init__(self, config: Optional[ConfigManager] = None):
        self._config = config or ConfigManager()
        self._secret = self._get_secret()

    def _get_secret(self) -> str:
        secret = self._config.get("jwt_secret", "")
        if not secret:
            import secrets
            secret = secrets.token_hex(32)
            self._config.set("jwt_secret", secret)
        return secret

    def create_tokens(self, staff_id: int, role: str = "staff") -> TokenPair:
        now = int(time.time())
        access_payload = {
            "sub": str(staff_id),
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + self.ACCESS_EXPIRY,
        }
        refresh_payload = {
            "sub": str(staff_id),
            "type": "refresh",
            "iat": now,
            "exp": now + self.REFRESH_EXPIRY,
        }
        if jwt is None:
            import json
            import base64
            access_token = base64.urlsafe_b64encode(
                json.dumps(access_payload).encode()
            ).decode()
            refresh_token = base64.urlsafe_b64encode(
                json.dumps(refresh_payload).encode()
            ).decode()
        else:
            access_token = jwt.encode(access_payload, self._secret, algorithm="HS256")
            refresh_token = jwt.encode(refresh_payload, self._secret, algorithm="HS256")
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.ACCESS_EXPIRY,
        )

    def verify_access(self, token: str) -> Optional[dict]:
        try:
            if jwt is None:
                import json
                import base64
                payload = json.loads(base64.urlsafe_b64decode(token))
            else:
                payload = jwt.decode(token, self._secret, algorithms=["HS256"])
            if payload.get("type") != "access":
                return None
            if payload.get("exp", 0) < time.time():
                return None
            sub = payload.get("sub")
            if sub is not None:
                payload["sub"] = int(sub)
            return payload
        except Exception:
            return None

    def refresh_access(self, refresh_token: str) -> Optional[TokenPair]:
        try:
            if jwt is None:
                import json
                import base64
                payload = json.loads(base64.urlsafe_b64decode(refresh_token))
            else:
                payload = jwt.decode(
                    refresh_token, self._secret, algorithms=["HS256"]
                )
            if payload.get("type") != "refresh":
                return None
            if payload.get("exp", 0) < time.time():
                return None
            staff_id = payload.get("sub")
            if staff_id is None:
                return None
            return self.create_tokens(int(staff_id))
        except Exception:
            return None
