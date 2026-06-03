from datetime import datetime
from typing import Optional, List
from src.models import RecurringExpense


class RecurringExpenseRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self):
        return "%s" if self._db.is_postgres else "?"

    def _to_recurring(self, row) -> Optional[RecurringExpense]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        amount = d.get("amount", 0)
        if hasattr(amount, "quantize"):
            amount = float(amount)
        active = d.get("active", True)
        if isinstance(active, int):
            active = bool(active)
        return RecurringExpense(
            id=d.get("id"),
            staff_id=d.get("staff_id", 0),
            amount=amount,
            category=d.get("category", ""),
            description=d.get("description", ""),
            frequency=d.get("frequency", "monthly"),
            interval_days=d.get("interval_days", 30),
            next_date=str(d.get("next_date", "")),
            active=active,
            created_at=str(d.get("created_at", "")) if d.get("created_at") else None,
        )

    def add(self, staff_id: int, amount: float, category: str, description: str,
            frequency: str, interval_days: int, next_date: str) -> int:
        ph = self._ph()
        if self._db.is_postgres:
            row = self._db.execute_one(
                f"INSERT INTO recurring_expenses (staff_id, amount, category, description, "
                f"frequency, interval_days, next_date) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) RETURNING id",
                (staff_id, amount, category, description, frequency, interval_days, next_date),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            f"INSERT INTO recurring_expenses (staff_id, amount, category, description, "
            f"frequency, interval_days, next_date) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (staff_id, amount, category, description, frequency, interval_days, next_date),
        )

    def get_all(self, staff_id: int) -> List[RecurringExpense]:
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT * FROM recurring_expenses WHERE staff_id = {ph} ORDER BY next_date",
            (staff_id,),
        )
        return [self._to_recurring(r) for r in rows]

    def get_due(self, staff_id: int) -> List[RecurringExpense]:
        today = datetime.now().strftime("%Y-%m-%d")
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT * FROM recurring_expenses "
            f"WHERE staff_id = {ph} AND active = TRUE AND next_date <= {ph}",
            (staff_id, today),
        )
        return [self._to_recurring(r) for r in rows]

    def update_next_date(self, rec_id: int, next_date: str):
        ph = self._ph()
        self._db.execute(
            f"UPDATE recurring_expenses SET next_date = {ph} WHERE id = {ph}",
            (next_date, rec_id),
        )

    def toggle_active(self, rec_id: int) -> bool:
        ph = self._ph()
        if self._db.is_postgres:
            self._db.execute(
                f"UPDATE recurring_expenses SET active = NOT active WHERE id = {ph}", (rec_id,)
            )
        else:
            self._db.execute(
                f"UPDATE recurring_expenses SET active = CASE WHEN active THEN 0 ELSE 1 END WHERE id = {ph}",
                (rec_id,),
            )
        return True

    def delete(self, rec_id: int) -> bool:
        ph = self._ph()
        self._db.execute(f"DELETE FROM recurring_expenses WHERE id = {ph}", (rec_id,))
        return True
