from datetime import datetime, timedelta
from typing import Optional
from src.database import ExpenseRepository
from src.models import OverallStats


class BudgetService:
    def __init__(self, expense_repo: ExpenseRepository):
        self._expense_repo = expense_repo

    def get_monthly_spend(self, staff_id: int, year: Optional[int] = None, month: Optional[int] = None) -> float:
        now = datetime.now()
        y = year or now.year
        m = month or now.month
        start = f"{y}-{m:02d}-01"
        end_date = datetime(y, m + 1, 1) - timedelta(days=1) if m < 12 else datetime(y, 12, 31)
        end = end_date.strftime("%Y-%m-%d")
        stats = self._expense_repo.get_total_stats(staff_id)
        if stats.total_expenses == 0:
            return 0.0
        rows = self._expense_repo.get_all(staff_id=staff_id, start_date=start, end_date=end)
        return sum(e.amount for e in rows)

    def get_budget_status(self, staff_id: int, budget: float) -> dict:
        spent = self.get_monthly_spend(staff_id)
        pct = (spent / budget * 100) if budget > 0 else 0
        return {
            "budget": budget,
            "spent": spent,
            "remaining": max(0, budget - spent),
            "percentage": round(pct, 1),
            "over_budget": spent > budget,
            "days_left": (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1).day - datetime.now().day,
        }
