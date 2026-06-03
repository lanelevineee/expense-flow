from datetime import datetime, timedelta
from typing import List, Optional
from src.database import GamificationRepository
from src.models import Achievement, UserAchievement, UserStats, Challenge, ChallengeProgress

LEVEL_CURVE = [25 * n * (n - 1) for n in range(0, 51)]


class GamificationService:
    def __init__(self, gamification_repo: GamificationRepository):
        self._repo = gamification_repo

    def ensure_seeded(self):
        self._repo.seed_achievements()
        self._repo.seed_challenges()

    def get_stats(self, staff_id: int) -> UserStats:
        return self._repo.get_stats(staff_id)

    def _compute_level(self, xp: int) -> int:
        for level in range(1, len(LEVEL_CURVE)):
            if xp < LEVEL_CURVE[level]:
                return level
        return 50

    def record_activity(self, staff_id: int, action_xp: int = 2):
        stats = self.get_stats(staff_id)
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        new_streak = 1
        if stats.last_activity_date == today:
            pass  # already logged today
        elif stats.last_activity_date == yesterday:
            new_streak = stats.current_streak + 1
        else:
            new_streak = 1

        longest = max(new_streak, stats.longest_streak)
        days_active = stats.days_active + (0 if stats.last_activity_date == today else 1)
        total_exp = stats.total_expenses + 1
        new_xp = stats.xp + action_xp
        new_level = self._compute_level(new_xp)

        self._repo.update_stats(
            staff_id,
            xp=new_xp,
            level=new_level,
            current_streak=new_streak,
            longest_streak=longest,
            last_activity_date=today,
            total_expenses=total_exp,
            days_active=days_active,
        )
        self.check_and_award(staff_id)

    def get_achievements(self) -> List[Achievement]:
        return self._repo.get_achievements()

    def get_earned(self, staff_id: int) -> List[UserAchievement]:
        return self._repo.get_user_achievements(staff_id)

    def check_and_award(self, staff_id: int):
        stats = self.get_stats(staff_id)
        all_ach = self._repo.get_achievements()
        earned_ids = {ua.achievement_id for ua in self._repo.get_user_achievements(staff_id)}
        categories_used = self._get_categories_used(staff_id)

        for ach in all_ach:
            if ach.id in earned_ids:
                continue
            earned = False
            if ach.criteria_type == "expense_count" and stats.total_expenses >= ach.criteria_value:
                earned = True
            elif ach.criteria_type == "streak_days" and stats.current_streak >= ach.criteria_value:
                earned = True
            elif ach.criteria_type == "category_count" and len(categories_used) >= ach.criteria_value:
                earned = True
            elif ach.criteria_type == "challenge_count":
                count = self._repo.get_completed_challenge_count(staff_id)
                if count >= ach.criteria_value:
                    earned = True

            if earned:
                self._repo.award_achievement(staff_id, ach.id)
                stats = self.get_stats(staff_id)
                new_xp = stats.xp + ach.xp_reward
                new_level = self._compute_level(new_xp)
                self._repo.update_stats(staff_id, xp=new_xp, level=new_level)

    def _get_categories_used(self, staff_id: int) -> set:
        return self._repo.get_categories_used(staff_id)

    def get_active_challenges(self) -> List[Challenge]:
        return self._repo.get_active_challenges()

    def get_challenge_progress(self, challenge_id: int, staff_id: int) -> Optional[ChallengeProgress]:
        cp = self._repo.get_challenge_progress(challenge_id, staff_id)
        if cp:
            chall = next((c for c in self.get_active_challenges() if c.id == challenge_id), None)
            cp.challenge = chall
        return cp

    def update_challenge_progress(self, staff_id: int):
        challenges = self.get_active_challenges()
        stats = self.get_stats(staff_id)
        cats = self._get_categories_used(staff_id)

        for c in challenges:
            cp = self._repo.get_challenge_progress(c.id, staff_id)
            progress = 0
            if c.goal_type == "expense_count":
                progress = stats.total_expenses
            elif c.goal_type == "streak_days":
                progress = stats.current_streak
            elif c.goal_type == "category_count":
                progress = len(cats)

            completed = progress >= c.goal_value
            if completed and cp and not cp.completed:
                st = self.get_stats(staff_id)
                self._repo.update_stats(staff_id, xp=st.xp + c.xp_reward,
                                        level=self._compute_level(st.xp + c.xp_reward))
            self._repo.upsert_challenge_progress(c.id, staff_id, progress, completed)

    def get_leaderboard(self) -> List[dict]:
        return self._repo.get_leaderboard()

    def get_level_xp(self, level: int) -> int:
        return LEVEL_CURVE[level] if level < len(LEVEL_CURVE) else LEVEL_CURVE[-1]
