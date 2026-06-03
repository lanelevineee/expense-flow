from datetime import datetime, timedelta
from typing import Optional, List
from src.models import (
    UserStats, Achievement, UserAchievement, Challenge, ChallengeProgress,
)


class GamificationRepository:
    def __init__(self, db):
        self._db = db

    def _ph(self) -> str:
        return "%s" if self._db.is_postgres else "?"

    def _to_user_stats(self, row) -> Optional[UserStats]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return UserStats(
            staff_id=d.get("staff_id", 0),
            xp=d.get("xp", 0),
            level=d.get("level", 1),
            current_streak=d.get("current_streak", 0),
            longest_streak=d.get("longest_streak", 0),
            last_activity_date=str(d.get("last_activity_date", "")) if d.get("last_activity_date") else None,
            total_expenses=d.get("total_expenses", 0),
            days_active=d.get("days_active", 0),
        )

    def _to_achievement(self, row) -> Optional[Achievement]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return Achievement(
            id=d.get("id"),
            code=d.get("code", ""),
            name=d.get("name", ""),
            description=d.get("description", ""),
            icon=d.get("icon", ""),
            criteria_type=d.get("criteria_type", ""),
            criteria_value=d.get("criteria_value", 0),
            xp_reward=d.get("xp_reward", 0),
        )

    def _to_user_achievement(self, row) -> Optional[UserAchievement]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return UserAchievement(
            id=d.get("id"),
            staff_id=d.get("staff_id", 0),
            achievement_id=d.get("achievement_id", 0),
            earned_at=str(d.get("earned_at", "")),
        )

    def _to_challenge(self, row) -> Optional[Challenge]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        active = d.get("active", True)
        if isinstance(active, int):
            active = bool(active)
        return Challenge(
            id=d.get("id"),
            title=d.get("title", ""),
            description=d.get("description", ""),
            goal_type=d.get("goal_type", ""),
            goal_value=d.get("goal_value", 0),
            xp_reward=d.get("xp_reward", 0),
            starts_at=str(d.get("starts_at", "")),
            ends_at=str(d.get("ends_at", "")),
            active=active,
        )

    def _to_challenge_progress(self, row) -> Optional[ChallengeProgress]:
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        completed = d.get("completed", False)
        if isinstance(completed, int):
            completed = bool(completed)
        return ChallengeProgress(
            id=d.get("id"),
            challenge_id=d.get("challenge_id", 0),
            staff_id=d.get("staff_id", 0),
            progress=d.get("progress", 0),
            completed=completed,
            completed_at=str(d.get("completed_at", "")) if d.get("completed_at") else None,
        )

    def get_stats(self, staff_id: int) -> Optional[UserStats]:
        ph = self._ph()
        row = self._db.execute_one(
            f"SELECT * FROM user_stats WHERE staff_id = {ph}", (staff_id,)
        )
        if row:
            return self._to_user_stats(row)
        if self._db.is_postgres:
            self._db.execute(
                "INSERT INTO user_stats (staff_id) VALUES (%s) ON CONFLICT DO NOTHING", (staff_id,)
            )
        else:
            self._db.execute(
                "INSERT OR IGNORE INTO user_stats (staff_id) VALUES (?)", (staff_id,)
            )
        return UserStats(staff_id=staff_id)

    def update_stats(self, staff_id: int, **kwargs):
        allowed = {"xp", "level", "current_streak", "longest_streak",
                    "last_activity_date", "total_expenses", "days_active"}
        sets = {k: v for k, v in kwargs.items() if k in allowed}
        if not sets:
            return
        ph = self._ph()
        placeholders = ", ".join(f"{k} = {ph}" for k in sets)
        vals = list(sets.values()) + [staff_id]
        self._db.execute(f"UPDATE user_stats SET {placeholders} WHERE staff_id = {ph}", vals)

    def seed_achievements(self):
        achievements = [
            ("first_expense", "trophy", "First Expense", "Record your first expense", "expense_count", 1, 5),
            ("ten_expenses", "chart", "Data Gatherer", "Record 10 expenses", "expense_count", 10, 10),
            ("fifty_expenses", "growth", "Expense Master", "Record 50 expenses", "expense_count", 50, 25),
            ("hundred_expenses", "crown", "Expense Legend", "Record 100 expenses", "expense_count", 100, 50),
            ("streak_7", "fire", "On Fire", "Maintain a 7-day streak", "streak_days", 7, 15),
            ("streak_14", "strength", "Unstoppable", "Maintain a 14-day streak", "streak_days", 14, 30),
            ("streak_30", "lightning", "Consistency King", "Maintain a 30-day streak", "streak_days", 30, 50),
            ("five_categories", "camera", "Variety Seeker", "Use 5 different categories", "category_count", 5, 10),
            ("all_categories", "cycle", "All-Rounder", "Use all 8 categories", "category_count", 8, 25),
            ("ai_insights_5", "brain", "Insight Seeker", "Run AI analysis 5 times", "ai_count", 5, 15),
            ("challenge_3", "medal", "Challenge Champion", "Complete 3 challenges", "challenge_count", 3, 30),
            ("budget_month", "money", "Budget Hero", "Stay under budget for a month", "budget_months", 1, 20),
            ("budget_3", "target", "Budget Pro", "Stay under budget for 3 months", "budget_months", 3, 50),
        ]
        ph = self._ph()
        for code, icon, name, desc, ctype, cvalue, xp in achievements:
            try:
                if self._db.is_postgres:
                    self._db.execute(
                        "INSERT INTO achievements "
                        "(code, icon, name, description, criteria_type, criteria_value, xp_reward) "
                        f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) ON CONFLICT DO NOTHING",
                        (code, icon, name, desc, ctype, cvalue, xp),
                    )
                else:
                    self._db.execute(
                        "INSERT OR IGNORE INTO achievements "
                        "(code, icon, name, description, criteria_type, criteria_value, xp_reward) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (code, icon, name, desc, ctype, cvalue, xp),
                    )
            except Exception:
                pass

    def get_achievements(self) -> List[Achievement]:
        rows = self._db.execute("SELECT * FROM achievements ORDER BY xp_reward")
        return [self._to_achievement(r) for r in rows]

    def get_user_achievements(self, staff_id: int) -> List[UserAchievement]:
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT ua.* FROM user_achievements ua WHERE ua.staff_id = {ph} ORDER BY ua.earned_at",
            (staff_id,),
        )
        return [self._to_user_achievement(r) for r in rows]

    def award_achievement(self, staff_id: int, achievement_id: int):
        ph = self._ph()
        try:
            if self._db.is_postgres:
                self._db.execute(
                    "INSERT INTO user_achievements (staff_id, achievement_id) "
                    f"VALUES ({ph}, {ph}) ON CONFLICT DO NOTHING",
                    (staff_id, achievement_id),
                )
            else:
                self._db.execute(
                    "INSERT OR IGNORE INTO user_achievements (staff_id, achievement_id) VALUES (?, ?)",
                    (staff_id, achievement_id),
                )
        except Exception:
            pass

    def get_completed_challenge_count(self, staff_id: int) -> int:
        ph = self._ph()
        row = self._db.execute_one(
            "SELECT COUNT(*) as cnt FROM challenge_progress "
            f"WHERE staff_id = {ph} AND completed = 1",
            (staff_id,),
        )
        return dict(row).get("cnt", 0) if row else 0

    def get_categories_used(self, staff_id: int) -> set:
        ph = self._ph()
        rows = self._db.execute(
            f"SELECT DISTINCT category FROM expenses WHERE staff_id = {ph}", (staff_id,)
        )
        return {dict(r).get("category", "") for r in rows}

    def get_leaderboard(self) -> List[dict]:
        rows = self._db.execute(
            "SELECT s.id, s.name, s.department, "
            "COALESCE(us.xp, 0) as xp, COALESCE(us.level, 1) as level, "
            "COALESCE(us.current_streak, 0) as streak, "
            "(SELECT COUNT(*) FROM user_achievements ua WHERE ua.staff_id = s.id) as badges "
            "FROM staff s "
            "LEFT JOIN user_stats us ON s.id = us.staff_id "
            "ORDER BY us.xp DESC"
        )
        return [dict(r) if not isinstance(r, dict) else r for r in rows]

    def seed_challenges(self):
        ph = self._ph()
        today = datetime.now()
        challenges = [
            ("Expense Blitz", "Record 10 expenses in a week", "expense_count", 10, 20,
             today.strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Daily Logger", "Log at least one expense every day for 5 days", "streak_days", 5, 15,
             today.strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d")),
            ("Category Explorer", "Use 5 different categories this week", "category_count", 5, 15,
             today.strftime("%Y-%m-%d"), (today + timedelta(days=7)).strftime("%Y-%m-%d")),
        ]
        for title, desc, gtype, gval, xp, start, end in challenges:
            try:
                if self._db.is_postgres:
                    self._db.execute(
                        "INSERT INTO challenges "
                        "(title, description, goal_type, goal_value, xp_reward, starts_at, ends_at) "
                        f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) ON CONFLICT DO NOTHING",
                        (title, desc, gtype, gval, xp, start, end),
                    )
                else:
                    self._db.execute(
                        "INSERT OR IGNORE INTO challenges "
                        "(title, description, goal_type, goal_value, xp_reward, starts_at, ends_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (title, desc, gtype, gval, xp, start, end),
                    )
            except Exception:
                pass

    def get_active_challenges(self) -> List[Challenge]:
        ph = self._ph()
        today = datetime.now().strftime("%Y-%m-%d")
        rows = self._db.execute(
            f"SELECT * FROM challenges WHERE active = TRUE AND starts_at <= {ph} AND ends_at >= {ph} "
            "ORDER BY ends_at",
            (today, today),
        )
        return [self._to_challenge(r) for r in rows]

    def get_challenge_progress(self, challenge_id: int, staff_id: int) -> Optional[ChallengeProgress]:
        ph = self._ph()
        row = self._db.execute_one(
            f"SELECT * FROM challenge_progress WHERE challenge_id = {ph} AND staff_id = {ph}",
            (challenge_id, staff_id),
        )
        return self._to_challenge_progress(row)

    def upsert_challenge_progress(self, challenge_id: int, staff_id: int,
                                   progress: int, completed: bool = False):
        ph = self._ph()
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed else None
        if self._db.is_postgres:
            self._db.execute(
                "INSERT INTO challenge_progress "
                "(challenge_id, staff_id, progress, completed, completed_at) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}) "
                "ON CONFLICT (challenge_id, staff_id) DO UPDATE SET "
                f"progress = {ph}, completed = {ph}, completed_at = {ph}",
                (challenge_id, staff_id, progress, 1 if completed else 0, completed_at,
                 progress, 1 if completed else 0, completed_at),
            )
        else:
            self._db.execute(
                "INSERT OR REPLACE INTO challenge_progress "
                "(challenge_id, staff_id, progress, completed, completed_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (challenge_id, staff_id, progress, 1 if completed else 0, completed_at),
            )
