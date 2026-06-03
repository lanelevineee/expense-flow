from typing import Optional, List
from src.models import PaymentMethod


class PaymentMethodRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self):
        return "%s" if self._db.is_postgres else "?"

    def _to_pm(self, row) -> Optional[PaymentMethod]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        is_default = d.get("is_default", False)
        if isinstance(is_default, int):
            is_default = bool(is_default)
        return PaymentMethod(
            id=d.get("id"),
            staff_id=d.get("staff_id", 0),
            name=d.get("name", ""),
            type=d.get("type", "cash"),
            is_default=is_default,
        )

    def add(self, staff_id: int, name: str, type: str = "cash") -> int:
        ph = self._ph()
        if self._db.is_postgres:
            row = self._db.execute_one(
                f"INSERT INTO payment_methods (staff_id, name, type) VALUES ({ph}, {ph}, {ph}) RETURNING id",
                (staff_id, name, type),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            f"INSERT INTO payment_methods (staff_id, name, type) VALUES ({ph}, {ph}, {ph})",
            (staff_id, name, type),
        )

    def get_all(self, staff_id: int) -> List[PaymentMethod]:
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT * FROM payment_methods WHERE staff_id = {ph} ORDER BY is_default DESC, name",
            (staff_id,),
        )
        return [self._to_pm(r) for r in rows]

    def set_default(self, pm_id: int, staff_id: int):
        ph = self._ph()
        with self._db.transaction() as cur:
            cur.execute(f"UPDATE payment_methods SET is_default = FALSE WHERE staff_id = {ph}", (staff_id,))
            cur.execute(f"UPDATE payment_methods SET is_default = TRUE WHERE id = {ph}", (pm_id,))

    def delete(self, pm_id: int) -> bool:
        ph = self._ph()
        self._db.execute(f"DELETE FROM payment_methods WHERE id = {ph}", (pm_id,))
        return True
