from typing import Optional, List

from src.database import ExpenseRepository
from src.models import OverallStats, CategoryStats, MonthlyStats


class AnalyticsService:
    def __init__(self, expense_repo: ExpenseRepository):
        self._expense_repo = expense_repo

    def get_overall_stats(self, staff_id: Optional[int] = None) -> OverallStats:
        return self._expense_repo.get_total_stats(staff_id)

    def get_category_breakdown(
        self, staff_id: Optional[int] = None
    ) -> List[CategoryStats]:
        return self._expense_repo.get_category_stats(staff_id)

    def get_monthly_trend(
        self, staff_id: Optional[int] = None
    ) -> List[MonthlyStats]:
        return self._expense_repo.get_monthly_stats(staff_id)
