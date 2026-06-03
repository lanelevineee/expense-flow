from fastapi import APIRouter, Header, Request
from typing import Optional

from src.auth.middleware import verify_token
from src.database import ExpenseRepository
from src.services.analytics_service import AnalyticsService

router = APIRouter()


def _require_auth(authorization: Optional[str]):
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = verify_token(authorization.replace("Bearer ", ""))
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/overview")
def overview(request: Request, authorization: Optional[str] = Header(None), staff_id: Optional[int] = None):
    user = _require_auth(authorization)
    db = request.app.state.db
    expense_repo = ExpenseRepository(db)
    service = AnalyticsService(expense_repo)
    sid = staff_id or user.staff_id
    overall = service.get_overall_stats(sid)
    categories = service.get_category_breakdown(sid)
    monthly = service.get_monthly_trend(sid)
    return {
        "overall": {
            "total_expenses": overall.total_expenses,
            "total_amount": overall.total_amount,
            "avg_amount": overall.avg_amount,
            "min_amount": overall.min_amount,
            "max_amount": overall.max_amount,
        },
        "categories": [
            {"category": c.category, "count": c.count, "total": c.total, "avg": c.avg, "budget": c.budget}
            for c in categories
        ],
        "monthly": [
            {"month": m.month, "total": m.total, "count": m.count, "avg": m.avg}
            for m in monthly
        ],
    }


@router.get("/stats")
def stats(request: Request, authorization: Optional[str] = Header(None), staff_id: Optional[int] = None):
    user = _require_auth(authorization)
    db = request.app.state.db
    repo = ExpenseRepository(db)
    sid = staff_id or user.staff_id
    total = repo.get_total_stats(sid)
    cats = repo.get_category_stats(sid)
    monthly = repo.get_monthly_stats(sid)
    return {
        "total": {
            "total_expenses": total.total_expenses,
            "total_amount": total.total_amount,
            "avg_amount": total.avg_amount,
        },
        "categories": [
            {"category": c.category, "count": c.count, "total": c.total}
            for c in cats
        ],
        "monthly": [
            {"month": m.month, "total": m.total, "count": m.count}
            for m in monthly
        ],
    }
