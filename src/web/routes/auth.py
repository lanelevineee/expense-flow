import logging

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.password import PasswordManager
from src.auth.session import SessionManager
from src.auth.mfa import MFAManager
from src.auth.middleware import verify_token, get_session_manager
from src.database import StaffRepository
from src.config import ConfigManager

logger = logging.getLogger("expense_tracker.auth")

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str
    totp_code: Optional[str] = None
    email_otp: Optional[str] = None


class RegisterRequest(BaseModel):
    name: str
    department: str = ""
    email: str = ""
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class MFASetupRequest(BaseModel):
    staff_id: int


class MFAVerifyRequest(BaseModel):
    staff_id: int
    code: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class PasswordSetupRequest(BaseModel):
    password: str


@router.post("/login")
def login(req: LoginRequest, request: Request):
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    try:
        staff = staff_repo.get_by_email(req.email)
    except Exception as e:
        logger.exception("Login query failed")
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        stored_hash = staff_repo.get_password_hash(staff.id)
    except Exception as e:
        logger.exception("Login password query failed")
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if stored_hash:
        if not PasswordManager.verify(req.password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        if req.password != "admin":
            raise HTTPException(status_code=401, detail="Invalid credentials")

    mfa_enabled = staff_repo.is_mfa_enabled(staff.id)
    if mfa_enabled:
        mfa = MFAManager(db)
        if req.totp_code:
            secret = staff_repo.get_mfa_secret(staff.id)
            if not mfa.verify_totp(secret, req.totp_code):
                raise HTTPException(status_code=401, detail="Invalid MFA code")
        elif req.email_otp:
            if not mfa.verify_email_otp(staff.email, req.email_otp):
                raise HTTPException(status_code=401, detail="Invalid OTP")
        else:
            raise HTTPException(status_code=403, detail="MFA required")

    sm = get_session_manager()
    role = "admin" if staff.id == 1 else "staff"
    tokens = sm.create_tokens(staff.id, role=role)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_in": tokens.expires_in,
        "staff_id": staff.id,
        "name": staff.name,
        "role": role,
    }


@router.post("/register")
def register(req: RegisterRequest, request: Request):
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    valid, errors = PasswordManager.validate_strength(req.password)
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    if staff_repo.email_exists(req.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    try:
        hashed = PasswordManager.hash_password(req.password)
        staff_id = staff_repo.add(req.name, req.department, req.email)
        if not staff_id:
            raise HTTPException(status_code=500, detail="Failed to create staff record")
        staff_repo.update(staff_id, password_hash=hashed)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Registration error for staff: %s", req.name)
        raise HTTPException(status_code=500, detail=f"Registration failed: {type(e).__name__}: {str(e)}")
    sm = get_session_manager()
    role = "admin" if staff_id == 1 else "staff"
    tokens = sm.create_tokens(staff_id, role=role)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "staff_id": staff_id,
        "name": req.name,
        "role": role,
    }
    sm = get_session_manager()
    tokens = sm.create_tokens(staff_id)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "staff_id": staff_id,
        "name": req.name,
    }
    sm = get_session_manager()
    tokens = sm.create_tokens(staff_id)
    logger.info("Registration successful for staff %s", staff_id)
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "staff_id": staff_id,
        "name": req.name,
    }


@router.post("/setup-password")
def setup_password(req: PasswordSetupRequest, request: Request, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    valid, errors = PasswordManager.validate_strength(req.password)
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    hashed = PasswordManager.hash_password(req.password)
    staff_repo.update(user.staff_id, password_hash=hashed)
    return {"success": True}


@router.post("/refresh")
def refresh(req: RefreshRequest):
    sm = get_session_manager()
    tokens = sm.refresh_access(req.refresh_token)
    if tokens is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_in": tokens.expires_in,
    }


@router.get("/me")
def get_me(authorization: Optional[str] = Header(None), request: Request = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {
        "staff_id": user.staff_id,
        "role": user.role,
        "name": user.name,
        "department": user.department,
    }


@router.post("/mfa/setup")
def mfa_setup(req: MFASetupRequest, request: Request):
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    mfa = MFAManager(db)
    secret = mfa.generate_totp_secret()
    staff = staff_repo.get_by_id(req.staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    uri = mfa.get_totp_uri(secret, staff.email)
    staff_repo.update(req.staff_id, mfa_secret=secret, mfa_enabled=True)
    return {"secret": secret, "uri": uri}


@router.post("/mfa/verify")
def mfa_verify(req: MFAVerifyRequest, request: Request):
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    mfa = MFAManager(db)
    secret = staff_repo.get_mfa_secret(req.staff_id)
    if not secret:
        raise HTTPException(status_code=400, detail="MFA not set up")
    if mfa.verify_totp(secret, req.code):
        return {"valid": True}
    raise HTTPException(status_code=401, detail="Invalid code")


@router.post("/change-password")
def change_password(req: PasswordChangeRequest, authorization: Optional[str] = Header(None), request: Request = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = request.app.state.db
    staff_repo = StaffRepository(db)
    stored = staff_repo.get_password_hash(user.staff_id)
    if stored and not PasswordManager.verify(req.old_password, stored):
        raise HTTPException(status_code=401, detail="Wrong password")
    valid, errors = PasswordManager.validate_strength(req.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail={"errors": errors})
    hashed = PasswordManager.hash_password(req.new_password)
    staff_repo.update(user.staff_id, password_hash=hashed)
    return {"success": True}
