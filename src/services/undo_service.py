import json
from typing import Optional
from src.database import AuditLogRepository, ExpenseRepository, StaffRepository
from src.models import Expense


class UndoService:
    def __init__(self, audit_repo: AuditLogRepository, expense_repo: ExpenseRepository,
                 staff_repo: StaffRepository):
        self._audit_repo = audit_repo
        self._expense_repo = expense_repo
        self._staff_repo = staff_repo

    def log_create(self, staff_id: int, entity_type: str, entity_id: int, new_value: dict) -> int:
        return self._audit_repo.log(staff_id, "create", entity_type, entity_id,
                                     new_value=json.dumps(new_value))

    def log_update(self, staff_id: int, entity_type: str, entity_id: int,
                   old_value: dict, new_value: dict) -> int:
        return self._audit_repo.log(staff_id, "update", entity_type, entity_id,
                                     old_value=json.dumps(old_value),
                                     new_value=json.dumps(new_value))

    def log_delete(self, staff_id: int, entity_type: str, entity_id: int, old_value: dict) -> int:
        return self._audit_repo.log(staff_id, "delete", entity_type, entity_id,
                                     old_value=json.dumps(old_value))

    def undo_last(self, staff_id: int) -> Optional[str]:
        log = self._audit_repo.delete_last(staff_id)
        if not log:
            return None

        if log.action == "delete" and log.entity_type == "expense" and log.old_value:
            data = json.loads(log.old_value)
            self._expense_repo.add(
                staff_id=data.get("staff_id", staff_id),
                amount=data.get("amount", 0),
                category=data.get("category", "Other"),
                description=data.get("description", ""),
                expense_date=data.get("expense_date", ""),
            )
            return f"Undo: restored deleted expense (${data.get('amount', 0):.2f})"

        elif log.action == "update" and log.entity_type == "expense" and log.old_value:
            data = json.loads(log.old_value)
            self._expense_repo.update(log.entity_id, **data)
            return f"Undo: reverted expense #{log.entity_id} to previous values"

        elif log.action == "create" and log.entity_type == "expense":
            self._expense_repo.delete(log.entity_id)
            return f"Undo: removed created expense #{log.entity_id}"

        return f"Undo: reverted {log.action} on {log.entity_type}"
