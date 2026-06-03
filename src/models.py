from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Staff:
    id: Optional[int] = None
    name: str = ""
    department: str = ""
    email: str = ""
    pin: str = ""
    currency: str = "USD"
    theme: str = "default"
    created_at: Optional[str] = None


@dataclass
class Expense:
    id: Optional[int] = None
    staff_id: int = 0
    amount: float = 0.0
    category: str = ""
    description: str = ""
    expense_date: str = ""
    payment_method_id: Optional[int] = None
    payment_method_name: Optional[str] = None
    created_at: Optional[str] = None
    staff_name: Optional[str] = None


@dataclass
class RecurringExpense:
    id: Optional[int] = None
    staff_id: int = 0
    amount: float = 0.0
    category: str = ""
    description: str = ""
    frequency: str = "monthly"
    interval_days: int = 30
    next_date: str = ""
    active: bool = True
    created_at: Optional[str] = None


@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    icon: str = ""
    color: str = ""
    budget: float = 0.0
    is_default: bool = False
    sort_order: int = 0


@dataclass
class PaymentMethod:
    id: Optional[int] = None
    staff_id: int = 0
    name: str = ""
    type: str = "cash"
    is_default: bool = False


@dataclass
class UserStats:
    staff_id: int = 0
    xp: int = 0
    level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[str] = None
    total_expenses: int = 0
    days_active: int = 0


@dataclass
class Achievement:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    description: str = ""
    icon: str = ""
    criteria_type: str = ""
    criteria_value: int = 0
    xp_reward: int = 0


@dataclass
class UserAchievement:
    id: Optional[int] = None
    staff_id: int = 0
    achievement_id: int = 0
    earned_at: Optional[str] = None
    achievement: Optional[Achievement] = None


@dataclass
class Challenge:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    goal_type: str = ""
    goal_value: int = 0
    xp_reward: int = 0
    starts_at: str = ""
    ends_at: str = ""
    active: bool = True


@dataclass
class ChallengeProgress:
    id: Optional[int] = None
    challenge_id: int = 0
    staff_id: int = 0
    progress: int = 0
    completed: bool = False
    completed_at: Optional[str] = None
    challenge: Optional[Challenge] = None


@dataclass
class AuditLog:
    id: Optional[int] = None
    staff_id: int = 0
    action: str = ""
    entity_type: str = ""
    entity_id: Optional[int] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class CategoryStats:
    category: str = ""
    count: int = 0
    total: float = 0.0
    avg: float = 0.0
    max: float = 0.0
    budget: float = 0.0
    budget_pct: float = 0.0


@dataclass
class MonthlyStats:
    month: str = ""
    total: float = 0.0
    count: int = 0
    avg: float = 0.0


@dataclass
class OverallStats:
    total_expenses: int = 0
    total_amount: float = 0.0
    avg_amount: float = 0.0
    min_amount: float = 0.0
    max_amount: float = 0.0
