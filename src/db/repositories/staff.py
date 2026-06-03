from typing import Optional, List
from src.models import Staff


class StaffRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self):
        return "%s" if self._db.is_postgres else "?"

    def _to_staff(self, row) -> Optional[Staff]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return Staff(
            id=d.get("id"),
            name=d.get("name", ""),
            department=d.get("department", ""),
            email=d.get("email", ""),
            pin=d.get("pin", ""),
            currency=d.get("currency", "USD"),
            theme=d.get("theme", "default"),
            created_at=str(d.get("created_at", "")) if d.get("created_at") else None,
        )

    def add(self, name: str, department: str = "", email: str = "", pin: str = "") -> int:
        ph = self._ph()
        if self._db.is_postgres:
            row = self._db.execute_one(
                f"INSERT INTO staff (name, department, email, pin) VALUES ({ph}, {ph}, {ph}, {ph}) RETURNING id",
                (name, department, email, pin),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            f"INSERT INTO staff (name, department, email, pin) VALUES ({ph}, {ph}, {ph}, {ph})",
            (name, department, email, pin),
        )

    def get_all(self) -> List[Staff]:
        rows = self._db.execute("SELECT * FROM staff ORDER BY name")
        return [self._to_staff(r) for r in rows]

    def get_by_id(self, staff_id: int) -> Optional[Staff]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT * FROM staff WHERE id = {ph}", (staff_id,))
        return self._to_staff(row)

    def get_by_email(self, email: str) -> Optional[Staff]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT * FROM staff WHERE email = {ph}", (email,))
        return self._to_staff(row)

    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        if not email:
            return False
        ph = self._ph()
        if exclude_id:
            row = self._db.execute_one(
                f"SELECT id FROM staff WHERE email = {ph} AND id != {ph}",
                (email, exclude_id),
            )
        else:
            row = self._db.execute_one(
                f"SELECT id FROM staff WHERE email = {ph}", (email,)
            )
        return row is not None

    def update(self, staff_id: int, **kwargs):
        allowed = {"name", "department", "email", "pin", "currency", "theme",
                    "password_hash", "mfa_enabled", "mfa_secret", "otp_email"}
        sets = {k: v for k, v in kwargs.items() if k in allowed}
        if not sets:
            return
        ph = self._ph()
        placeholders = ", ".join(f"{k} = {ph}" for k in sets)
        vals = list(sets.values()) + [staff_id]
        self._db.execute(f"UPDATE staff SET {placeholders} WHERE id = {ph}", vals)

    def delete(self, staff_id: int) -> bool:
        ph = self._ph()
        with self._db.transaction() as cur:
            for tbl in ("otp_codes", "audit_log", "challenge_progress", "user_achievements",
                         "user_stats", "payment_methods", "recurring_expenses", "expenses"):
                cur.execute(f"DELETE FROM {tbl} WHERE staff_id = {ph}", (staff_id,))
            cur.execute(f"DELETE FROM staff WHERE id = {ph}", (staff_id,))
        return True

    def verify_pin(self, staff_id: int, pin: str) -> bool:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT pin FROM staff WHERE id = {ph}", (staff_id,))
        return row and dict(row).get("pin") == pin

    def get_password_hash(self, staff_id: int) -> Optional[str]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT password_hash FROM staff WHERE id = {ph}", (staff_id,))
        d = dict(row) if row else None
        return d.get("password_hash") if d else None

    def get_mfa_secret(self, staff_id: int) -> Optional[str]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT mfa_secret FROM staff WHERE id = {ph}", (staff_id,))
        d = dict(row) if row else None
        return d.get("mfa_secret") if d else None

    def is_mfa_enabled(self, staff_id: int) -> bool:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT mfa_enabled FROM staff WHERE id = {ph}", (staff_id,))
        d = dict(row) if row else None
        if not d:
            return False
        val = d.get("mfa_enabled")
        if isinstance(val, bool):
            return val
        return val == 1 or val == "1" or val is True
