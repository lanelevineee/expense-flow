from typing import Optional, List
from src.models import Category


class CategoryRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self, count=None):
        return "%s" if self._db.is_postgres else "?"

    def _to_category(self, row) -> Optional[Category]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        budget = d.get("budget", 0)
        if hasattr(budget, "quantize"):
            budget = float(budget)
        is_default = d.get("is_default", False)
        if isinstance(is_default, int):
            is_default = bool(is_default)
        return Category(
            id=d.get("id"),
            name=d.get("name", ""),
            icon=d.get("icon", ""),
            color=d.get("color", ""),
            budget=budget,
            is_default=is_default,
            sort_order=d.get("sort_order", 0),
        )

    def seed_defaults(self):
        defaults = [
            ("Food & Dining", "food", "#FF6B6B", 500),
            ("Transportation", "transport", "#4ECDC4", 300),
            ("Housing & Utilities", "housing", "#45B7D1", 1500),
            ("Entertainment", "entertainment", "#96CEB4", 200),
            ("Healthcare", "healthcare", "#FFEAA7", 300),
            ("Shopping", "shopping", "#DDA0DD", 400),
            ("Education", "education", "#98D8C8", 200),
            ("Other", "other", "#B0B0B0", 300),
        ]
        ph = self._ph()
        for i, (name, icon, color, budget) in enumerate(defaults):
            try:
                self._db.execute(
                    f"INSERT INTO categories (name, icon, color, budget, is_default, sort_order) "
                    f"VALUES ({ph}, {ph}, {ph}, {ph}, TRUE, {ph})",
                    (name, icon, color, budget, i),
                )
            except Exception:
                pass

    def get_all(self) -> List[Category]:
        rows = self._db.execute("SELECT * FROM categories ORDER BY sort_order, name")
        return [self._to_category(r) for r in rows]

    def get_by_name(self, name: str) -> Optional[Category]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT * FROM categories WHERE name = {ph}", (name,))
        return self._to_category(row)

    def add(self, name: str, icon: str = "", color: str = "", budget: float = 0) -> int:
        ph = self._ph()
        if self._db.is_postgres:
            row = self._db.execute_one(
                f"INSERT INTO categories (name, icon, color, budget) VALUES ({ph}, {ph}, {ph}, {ph}) RETURNING id",
                (name, icon, color, budget),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            f"INSERT INTO categories (name, icon, color, budget) VALUES ({ph}, {ph}, {ph}, {ph})",
            (name, icon, color, budget),
        )

    def update(self, cat_id: int, **kwargs):
        allowed = {"name", "icon", "color", "budget"}
        sets = {k: v for k, v in kwargs.items() if k in allowed}
        if not sets:
            return
        ph = self._ph()
        placeholders = ", ".join(f"{k} = {ph}" for k in sets)
        vals = list(sets.values()) + [cat_id]
        self._db.execute(f"UPDATE categories SET {placeholders} WHERE id = {ph}", vals)

    def delete(self, cat_id: int) -> bool:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT is_default FROM categories WHERE id = {ph}", (cat_id,))
        d = dict(row) if row else {}
        is_default = d.get("is_default", False)
        if isinstance(is_default, int):
            is_default = bool(is_default)
        if is_default:
            return False
        self._db.execute(f"DELETE FROM categories WHERE id = {ph}", (cat_id,))
        return True

    def get_category_names(self) -> List[str]:
        rows = self._db.execute("SELECT name FROM categories ORDER BY sort_order, name")
        return [dict(r).get("name", "") for r in rows]
