from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.middleware import verify_token
from src.database import RecurringExpenseRepository

router = APIRouter()

FREQUENCY_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365,
}


class RecurringCreate(BaseModel):
    staff_id: int
    amount: float
    category: str
    description: str = ""
    frequency: str = "monthly"
    next_date: str = ""
    is_active: bool = True


class RecurringUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    next_date: Optional[str] = None
    is_active: Optional[bool] = None


def _require_auth(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/")
def list_recurring(request: Request, authorization: Optional[str] = Header(None), staff_id: Optional[int] = None):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = RecurringExpenseRepository(db)
    sid = staff_id or user.staff_id
    items = repo.get_all(staff_id=sid)
    return [
        {
            "id": r.id, "staff_id": r.staff_id, "amount": r.amount,
            "category": r.category, "description": r.description,
            "frequency": r.frequency, "next_date": r.next_date,
            "is_active": r.active,
        }
        for r in items
    ]


@router.post("/")
def create_recurring(req: RecurringCreate, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = RecurringExpenseRepository(db)
    interval_days = FREQUENCY_DAYS.get(req.frequency, 30)
    rid = repo.add(
        req.staff_id, req.amount, req.category, req.description,
        req.frequency, interval_days, req.next_date,
    )
    return {"id": rid}


@router.delete("/{recurring_id}")
def delete_recurring(recurring_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = RecurringExpenseRepository(db)
    repo.delete(recurring_id)
    return {"success": True}


@router.post("/{recurring_id}/toggle")
def toggle_recurring(recurring_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = RecurringExpenseRepository(db)
    repo.toggle_active(recurring_id)
    return {"success": True}
