from datetime import datetime, timedelta
from typing import List, Optional
from src.database import RecurringExpenseRepository, ExpenseRepository
from src.models import RecurringExpense


FREQUENCY_MAP = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365,
}


class RecurringService:
    def __init__(self, rec_repo: RecurringExpenseRepository, expense_repo: ExpenseRepository):
        self._rec_repo = rec_repo
        self._expense_repo = expense_repo

    def create(self, staff_id: int, amount: float, category: str, description: str,
               frequency: str) -> RecurringExpense:
        interval_days = FREQUENCY_MAP.get(frequency, 30)
        next_date = datetime.now().strftime("%Y-%m-%d")
        rid = self._rec_repo.add(staff_id, amount, category, description,
                                  frequency, interval_days, next_date)
        return RecurringExpense(id=rid, staff_id=staff_id, amount=amount,
                                 category=category, description=description,
                                 frequency=frequency, interval_days=interval_days,
                                 next_date=next_date)

    def get_all(self, staff_id: Optional[int] = None) -> List[RecurringExpense]:
        return self._rec_repo.get_all(staff_id)

    def process_due(self, staff_id: Optional[int] = None) -> int:
        """Auto-create expenses for all due recurring entries. Returns count created."""
        due = self._rec_repo.get_due()
        count = 0
        today = datetime.now().strftime("%Y-%m-%d")
        for rec in due:
            if staff_id is not None and rec.staff_id != staff_id:
                continue
            self._expense_repo.add(
                staff_id=rec.staff_id,
                amount=rec.amount,
                category=rec.category,
                description=f"[Recurring] {rec.description}",
                expense_date=today,
            )
            next_due = (datetime.now() + timedelta(days=rec.interval_days)).strftime("%Y-%m-%d")
            self._rec_repo.update_next_date(rec.id, next_due)
            count += 1
        return count

    def toggle_active(self, rec_id: int) -> bool:
        return self._rec_repo.toggle_active(rec_id)

    def delete(self, rec_id: int) -> bool:
        return self._rec_repo.delete(rec_id)
