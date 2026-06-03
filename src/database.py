"""
Compatibility layer - imports from the new src.db package.
All existing code that does `from src.database import X` will continue to work.
"""
from src.db.connection import DatabaseConnection
from src.db.schema import init_tables
from src.db.repositories.staff import StaffRepository
from src.db.repositories.expense import ExpenseRepository
from src.db.repositories.category import CategoryRepository
from src.db.repositories.recurring import RecurringExpenseRepository
from src.db.repositories.payment_method import PaymentMethodRepository
from src.db.repositories.gamification import GamificationRepository
from src.db.repositories.audit_log import AuditLogRepository

__all__ = [
    "DatabaseConnection",
    "init_tables",
    "StaffRepository",
    "ExpenseRepository",
    "CategoryRepository",
    "RecurringExpenseRepository",
    "PaymentMethodRepository",
    "GamificationRepository",
    "AuditLogRepository",
]
