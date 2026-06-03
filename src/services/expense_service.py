from datetime import datetime
from typing import Optional, List

from src.models import Expense
from src.database import StaffRepository, ExpenseRepository


class ExpenseService:
    def __init__(self, staff_repo: StaffRepository, expense_repo: ExpenseRepository):
        self._staff_repo = staff_repo
        self._expense_repo = expense_repo

    def record(
        self,
        staff_id: int,
        amount: float,
        category: str,
        description: str = "",
        expense_date: Optional[str] = None,
        payment_method_id: Optional[int] = None,
    ) -> Expense:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        staff = self._staff_repo.get_by_id(staff_id)
        if not staff:
            raise ValueError(f"Staff not found: {staff_id}")

        if expense_date is None:
            expense_date = datetime.now().strftime("%Y-%m-%d")

        eid = self._expense_repo.add(
            staff_id, amount, category, description, expense_date, payment_method_id,
        )
        return Expense(
            id=eid,
            staff_id=staff_id,
            amount=amount,
            category=category,
            description=description,
            expense_date=expense_date,
        )

    def update(self, expense_id: int, **kwargs) -> bool:
        return self._expense_repo.update(expense_id, **kwargs)

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        return self._expense_repo.get_by_id(expense_id)

    def get_expenses(self, **filters) -> List[Expense]:
        return self._expense_repo.get_all(**filters)

    def delete(self, expense_id: int) -> bool:
        return self._expense_repo.delete(expense_id)
