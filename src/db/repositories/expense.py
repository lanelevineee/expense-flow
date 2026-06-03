from datetime import datetime, timedelta
from typing import Optional, List
from src.models import Expense, CategoryStats, MonthlyStats, OverallStats


class ExpenseRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self) -> str:
        return "%s" if self._db.is_postgres else "?"

    def _to_expense(self, row) -> Optional[Expense]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        amount = d.get("amount", 0)
        if hasattr(amount, "quantize"):
            amount = float(amount)
        return Expense(
            id=d.get("id"),
            staff_id=d.get("staff_id", 0),
            amount=amount,
            category=d.get("category", ""),
            description=d.get("description", ""),
            expense_date=str(d.get("expense_date", "")),
            payment_method_id=d.get("payment_method_id"),
            created_at=str(d.get("created_at", "")) if d.get("created_at") else None,
        )

    def add(self, staff_id: int, amount: float, category: str,
            description: str = "", expense_date: str = "",
            payment_method_id: Optional[int] = None) -> int:
        ph = self._ph()
        if not expense_date:
            expense_date = datetime.now().strftime("%Y-%m-%d")
        if self._db.is_postgres:
            row = self._db.execute_one(
                "INSERT INTO expenses (staff_id, amount, category, description, expense_date, payment_method_id) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}) RETURNING id",
                (staff_id, amount, category, description, expense_date, payment_method_id),
            )
            return row["id"] if row else None
        return self._db.execute_insert(
            "INSERT INTO expenses (staff_id, amount, category, description, expense_date, payment_method_id) "
            f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (staff_id, amount, category, description, expense_date, payment_method_id),
        )

    def update(self, expense_id: int, **kwargs) -> bool:
        allowed = {"amount", "category", "description", "expense_date", "payment_method_id"}
        sets = {k: v for k, v in kwargs.items() if k in allowed}
        if not sets:
            return False
        ph = self._ph()
        placeholders = ", ".join(f"{k} = {ph}" for k in sets)
        vals = list(sets.values()) + [expense_id]
        self._db.execute(f"UPDATE expenses SET {placeholders} WHERE id = {ph}", vals)
        return True

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        ph = self._ph()
        row = self._db.execute_one(f"SELECT * FROM expenses WHERE id = {ph}", (expense_id,))
        return self._to_expense(row)

    def get_all(self, staff_id: Optional[int] = None, category: Optional[str] = None,
                start_date: Optional[str] = None, end_date: Optional[str] = None,
                search: Optional[str] = None, sort_by: str = "date_desc",
                limit: Optional[int] = None) -> List[Expense]:
        ph = self._ph()
        conditions = []
        params = []

        if staff_id:
            conditions.append(f"e.staff_id = {ph}")
            params.append(staff_id)
        if category:
            conditions.append(f"e.category = {ph}")
            params.append(category)
        if start_date:
            conditions.append(f"e.expense_date >= {ph}")
            params.append(start_date)
        if end_date:
            conditions.append(f"e.expense_date <= {ph}")
            params.append(end_date)
        if search:
            if self._db.is_postgres:
                conditions.append(f"(e.description ILIKE {ph} OR e.category ILIKE {ph} OR CAST(e.amount AS TEXT) LIKE {ph})")
            else:
                conditions.append(f"(e.description LIKE {ph} OR e.category LIKE {ph} OR CAST(e.amount AS TEXT) LIKE {ph})")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        sort_map = {
            "date_desc": "e.expense_date DESC, e.id DESC",
            "date_asc": "e.expense_date ASC, e.id ASC",
            "amount_desc": "e.amount DESC",
            "amount_asc": "e.amount ASC",
            "category_asc": "e.category ASC",
        }
        order = sort_map.get(sort_by, "e.expense_date DESC, e.id DESC")

        query = f"SELECT e.* FROM expenses e{where} ORDER BY {order}"
        if limit:
            query += f" LIMIT {limit}"

        rows = self._db.execute(query, params)
        return [self._to_expense(r) for r in rows]

    def get_category_stats(self, staff_id: int) -> List[CategoryStats]:
        ph = self._ph()
        rows = self._db.execute(
            "SELECT e.category, COUNT(*) as count, SUM(e.amount) as total, "
            "AVG(e.amount) as avg, MAX(e.amount) as max, "
            "COALESCE(c.budget, 0) as budget "
            "FROM expenses e "
            "LEFT JOIN categories c ON e.category = c.name "
            f"WHERE e.staff_id = {ph} "
            "GROUP BY e.category, c.budget "
            "ORDER BY total DESC",
            (staff_id,),
        )
        result = []
        for r in rows:
            d = dict(r) if not isinstance(r, dict) else r
            total = float(d.get("total", 0) or 0)
            budget = float(d.get("budget", 0) or 0)
            result.append(CategoryStats(
                category=d.get("category", ""),
                count=d.get("count", 0),
                total=total,
                avg=float(d.get("avg", 0) or 0),
                max=float(d.get("max", 0) or 0),
                budget=budget,
                budget_pct=round(total / budget * 100, 1) if budget > 0 else 0,
            ))
        return result

    def get_monthly_stats(self, staff_id: int, months: int = 6) -> List[MonthlyStats]:
        ph = self._ph()
        if self._db.is_postgres:
            rows = self._db.execute(
                "SELECT TO_CHAR(expense_date::date, 'YYYY-MM') as month, "
                f"SUM(amount) as total, COUNT(*) as count, AVG(amount) as avg "
                f"FROM expenses WHERE staff_id = {ph} "
                f"GROUP BY month ORDER BY month DESC LIMIT {ph}",
                (staff_id, months),
            )
        else:
            rows = self._db.execute(
                "SELECT strftime('%Y-%m', expense_date) as month, "
                f"SUM(amount) as total, COUNT(*) as count, AVG(amount) as avg "
                f"FROM expenses WHERE staff_id = {ph} "
                f"GROUP BY month ORDER BY month DESC LIMIT {ph}",
                (staff_id, months),
            )
        return [MonthlyStats(
            month=dict(r).get("month", ""),
            total=float(dict(r).get("total", 0) or 0),
            count=dict(r).get("count", 0),
            avg=float(dict(r).get("avg", 0) or 0),
        ) for r in rows]

    def get_period_comparison(self, staff_id: int) -> dict:
        ph = self._ph()
        now = datetime.now()
        current_month_start = now.replace(day=1).strftime("%Y-%m-%d")
        last_month_end = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        last_month_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")

        current = self._db.execute_one(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses "
            f"WHERE staff_id = {ph} AND expense_date >= {ph}",
            (staff_id, current_month_start),
        )
        previous = self._db.execute_one(
            "SELECT COALESCE(SUM(amount), 0) as total FROM expenses "
            f"WHERE staff_id = {ph} AND expense_date >= {ph} AND expense_date <= {ph}",
            (staff_id, last_month_start, last_month_end),
        )

        cur_total = float(dict(current).get("total", 0)) if current else 0
        prev_total = float(dict(previous).get("total", 0)) if previous else 0
        change_pct = ((cur_total - prev_total) / prev_total * 100) if prev_total > 0 else 0

        return {
            "current_month": cur_total,
            "previous_month": prev_total,
            "change_pct": round(change_pct, 1),
        }

    def get_total_stats(self, staff_id: Optional[int] = None) -> OverallStats:
        ph = self._ph()
        if staff_id is not None:
            row = self._db.execute_one(
                "SELECT COUNT(*) as total_expenses, COALESCE(SUM(amount), 0) as total_amount, "
                "COALESCE(AVG(amount), 0) as avg_amount, COALESCE(MIN(amount), 0) as min_amount, "
                f"COALESCE(MAX(amount), 0) as max_amount "
                f"FROM expenses WHERE staff_id = {ph}",
                (staff_id,),
            )
        else:
            row = self._db.execute_one(
                "SELECT COUNT(*) as total_expenses, COALESCE(SUM(amount), 0) as total_amount, "
                "COALESCE(AVG(amount), 0) as avg_amount, COALESCE(MIN(amount), 0) as min_amount, "
                "COALESCE(MAX(amount), 0) as max_amount "
                "FROM expenses",
            )
        d = dict(row) if row else {}
        return OverallStats(
            total_expenses=d.get("total_expenses", 0),
            total_amount=float(d.get("total_amount", 0) or 0),
            avg_amount=float(d.get("avg_amount", 0) or 0),
            min_amount=float(d.get("min_amount", 0) or 0),
            max_amount=float(d.get("max_amount", 0) or 0),
        )

    def delete(self, expense_id: int) -> bool:
        ph = self._ph()
        self._db.execute(f"DELETE FROM expenses WHERE id = {ph}", (expense_id,))
        return True

    def get_recent(self, staff_id: int, days: int = 30) -> List[Expense]:
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return self.get_all(staff_id=staff_id, start_date=start, sort_by="date_desc")

    def clear_all(self):
        self._db.execute("DELETE FROM expenses")
