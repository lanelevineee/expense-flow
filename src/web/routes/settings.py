from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional

from src.auth.middleware import verify_token
from src.database import PaymentMethodRepository, CategoryRepository
from src.config import ConfigManager

router = APIRouter()


class CurrencySet(BaseModel):
    currency: str


class ThemeSet(BaseModel):
    theme: str


class BudgetSet(BaseModel):
    category: str
    amount: float


class PaymentMethodCreate(BaseModel):
    name: str
    type: str = "other"
    is_default: bool = False


def _require_auth(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/currency")
def get_currency(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    config = ConfigManager()
    return {"currency": config.get("currency", "USD")}


@router.put("/currency")
def set_currency(req: CurrencySet, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    config = ConfigManager()
    config.set("currency", req.currency)
    return {"success": True}


@router.get("/theme")
def get_theme(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    config = ConfigManager()
    return {"theme": config.get("theme", "default")}


@router.put("/theme")
def set_theme(req: ThemeSet, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    config = ConfigManager()
    config.set("theme", req.theme)
    return {"success": True}


@router.get("/budgets")
def list_budgets(request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = CategoryRepository(db)
    cats = repo.get_all()
    return [{"name": c.name, "budget": c.budget} for c in cats]


@router.put("/budgets")
def set_budget(req: BudgetSet, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = CategoryRepository(db)
    cat = repo.get_by_name(req.category)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    repo.update(cat.id, budget=req.amount)
    return {"success": True}


@router.get("/payment-methods")
def list_payment_methods(request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = PaymentMethodRepository(db)
    methods = repo.get_all(staff_id=user.staff_id)
    return [
        {"id": m.id, "name": m.name, "type": m.type, "is_default": m.is_default}
        for m in methods
    ]


@router.post("/payment-methods")
def create_payment_method(req: PaymentMethodCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = PaymentMethodRepository(db)
    pm_id = repo.add(user.staff_id, req.name, req.type)
    if req.is_default:
        repo.set_default(pm_id, user.staff_id)
    return {"id": pm_id}


@router.delete("/payment-methods/{pm_id}")
def delete_payment_method(pm_id: int, request: Request, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    db = request.app.state.db
    repo = PaymentMethodRepository(db)
    repo.delete(pm_id)
    return {"success": True}
