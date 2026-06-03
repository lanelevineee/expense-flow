from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.middleware import verify_token
from src.database import StaffRepository

router = APIRouter()


class StaffCreate(BaseModel):
    name: str
    department: str = ""
    email: str = ""


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None


def _require_auth(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/")
def list_staff(request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = StaffRepository(db)
    if user.role == "admin":
        staff = repo.get_all()
    else:
        s = repo.get_by_id(user.staff_id)
        staff = [s] if s else []
    return [
        {"id": s.id, "name": s.name, "department": s.department, "email": s.email}
        for s in staff
    ]


@router.get("/{staff_id}")
def get_staff(staff_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = StaffRepository(db)
    staff = repo.get_by_id(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"id": staff.id, "name": staff.name, "department": staff.department, "email": staff.email}


@router.post("/")
def create_staff(req: StaffCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    db = request.app.state.db
    repo = StaffRepository(db)
    staff_id = repo.add(req.name, req.department, req.email)
    return {"id": staff_id, "name": req.name}


@router.put("/{staff_id}")
def update_staff(staff_id: int, req: StaffUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin" and user.staff_id != staff_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db = request.app.state.db
    repo = StaffRepository(db)
    staff = repo.get_by_id(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    kwargs = {}
    if req.name is not None:
        kwargs["name"] = req.name
    if req.department is not None:
        kwargs["department"] = req.department
    if req.email is not None:
        kwargs["email"] = req.email
    if kwargs:
        repo.update(staff_id, **kwargs)
    return {"success": True}


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    db = request.app.state.db
    repo = StaffRepository(db)
    repo.delete(staff_id)
    return {"success": True}
