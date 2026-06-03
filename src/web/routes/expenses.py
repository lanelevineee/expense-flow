from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.middleware import verify_token
from src.database import ExpenseRepository

router = APIRouter()


class ExpenseCreate(BaseModel):
    staff_id: int
    amount: float
    category: str
    description: str = ""
    expense_date: str = ""
    payment_method_id: Optional[int] = None


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    payment_method_id: Optional[int] = None


def _require_auth(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/")
def list_expenses(
    request: Request,
    authorization: Optional[str] = Header(None),
    staff_id: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "date_desc",
    limit: Optional[int] = None,
):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = ExpenseRepository(db)
    if staff_id is None:
        staff_id = user.staff_id
    expenses = repo.get_all(
        staff_id=staff_id,
        category=category,
        search=search,
        sort_by=sort_by,
        limit=limit,
    )
    return [
        {
            "id": e.id,
            "staff_id": e.staff_id,
            "amount": e.amount,
            "category": e.category,
            "description": e.description,
            "payment_method_id": e.payment_method_id,
            "payment_method_name": e.payment_method_name or "",
            "expense_date": e.expense_date,
            "created_at": e.created_at,
        }
        for e in expenses
    ]


@router.post("/")
def create_expense(req: ExpenseCreate, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = ExpenseRepository(db)
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    expense_id = repo.add(
        staff_id=req.staff_id,
        amount=req.amount,
        category=req.category,
        description=req.description,
        expense_date=req.expense_date,
        payment_method_id=req.payment_method_id,
    )
    try:
        from src.services.gamification_service import GamificationService
        from src.db.repositories.gamification import GamificationRepository
        gami_repo = GamificationRepository(db)
        gami_service = GamificationService(gami_repo)
        gami_service.record_activity(req.staff_id)
        gami_service.update_challenge_progress(req.staff_id)
    except Exception:
        pass
    return {"id": expense_id}


@router.put("/{expense_id}")
def update_expense(expense_id: int, req: ExpenseUpdate, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = ExpenseRepository(db)
    existing = repo.get_by_id(expense_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    kwargs = {}
    if req.amount is not None:
        kwargs["amount"] = req.amount
    if req.category is not None:
        kwargs["category"] = req.category
    if req.description is not None:
        kwargs["description"] = req.description
    if req.payment_method_id is not None:
        kwargs["payment_method_id"] = req.payment_method_id
    if kwargs:
        repo.update(expense_id, **kwargs)
    return {"success": True}


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = ExpenseRepository(db)
    repo.delete(expense_id)
    return {"success": True}
