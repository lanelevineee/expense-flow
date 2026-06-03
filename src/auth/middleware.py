from typing import Optional
from dataclasses import dataclass

from src.auth.session import SessionManager
from src.database import StaffRepository, DatabaseConnection

try:
    from fastapi import Depends, HTTPException, Header
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


@dataclass
class CurrentUser:
    staff_id: int
    role: str
    name: str = ""
    department: str = ""


_session_manager: Optional[SessionManager] = None
_db: Optional[DatabaseConnection] = None


def init_auth(db: DatabaseConnection):
    global _session_manager, _db
    _db = db
    _session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def verify_token(token: str) -> Optional[CurrentUser]:
    sm = get_session_manager()
    payload = sm.verify_access(token)
    if payload is None:
        return None
    staff_id = payload.get("sub")
    role = payload.get("role", "staff")
    name = ""
    department = ""
    if _db:
        repo = StaffRepository(_db)
        staff = repo.get_by_id(staff_id)
        if staff:
            name = staff.name
            department = staff.department
    return CurrentUser(staff_id=staff_id, role=role, name=name, department=department)


if _HAS_FASTAPI:
    def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
        if not authorization:
            raise HTTPException(status_code=401, detail="Not authenticated")
        token = authorization.replace("Bearer ", "")
        user = verify_token(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user

    def require_auth(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        return user

    def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
else:
    def get_current_user(token: str = "") -> Optional[CurrentUser]:
        return verify_token(token)

    def require_auth(token: str = "") -> CurrentUser:
        user = verify_token(token)
        if user is None:
            raise PermissionError("Not authenticated")
        return user

    def require_admin(token: str = "") -> CurrentUser:
        user = verify_token(token)
        if user is None:
            raise PermissionError("Not authenticated")
        if user.role != "admin":
            raise PermissionError("Admin access required")
        return user
