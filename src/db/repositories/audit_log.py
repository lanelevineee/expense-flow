from typing import Optional, List
from src.models import AuditLog


class AuditLogRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self) -> str:
        return "%s" if self._db.is_postgres else "?"

    def _to_audit_log(self, row) -> Optional[AuditLog]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return AuditLog(
            id=d.get("id"),
            staff_id=d.get("staff_id", 0),
            action=d.get("action", ""),
            entity_type=d.get("entity_type", ""),
            entity_id=d.get("entity_id"),
            old_value=d.get("old_value"),
            new_value=d.get("new_value"),
            created_at=str(d.get("created_at", "")) if d.get("created_at") else None,
        )

    def log(self, staff_id: int, action: str, entity_type: str,
            entity_id: Optional[int] = None, old_value: Optional[str] = None,
            new_value: Optional[str] = None) -> int:
        ph = self._ph()
        if self._db.is_postgres:
            row = self._db.execute_one(
                "INSERT INTO audit_log (staff_id, action, entity_type, entity_id, old_value, new_value) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}) RETURNING id",
                (staff_id, action, entity_type, entity_id, old_value, new_value),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            "INSERT INTO audit_log (staff_id, action, entity_type, entity_id, old_value, new_value) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (staff_id, action, entity_type, entity_id, old_value, new_value),
        )

    def get_last(self, staff_id: int, limit: int = 10) -> List[AuditLog]:
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT * FROM audit_log WHERE staff_id = {ph} ORDER BY created_at DESC LIMIT {ph}",
            (staff_id, limit),
        )
        return [self._to_audit_log(r) for r in rows]

    def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT * FROM audit_log WHERE id = {ph}", (log_id,))
        return self._to_audit_log(row)

    def delete_last(self, staff_id: int) -> Optional[AuditLog]:
        ph = self._ph()
        row = self._db.execute_one(
            f"SELECT * FROM audit_log WHERE staff_id = {ph} ORDER BY created_at DESC LIMIT 1",
            (staff_id,),
        )
        if row:
            log = self._to_audit_log(row)
            self._db.execute(f"DELETE FROM audit_log WHERE id = {ph}", (log.id,))
            return log
        return None
