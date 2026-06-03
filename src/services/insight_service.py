from typing import Optional

from src.database import ExpenseRepository, StaffRepository
from src.config import ConfigManager
from src.providers.factory import ProviderFactory


class InsightService:
    def __init__(
        self,
        config: ConfigManager,
        expense_repo: ExpenseRepository,
        staff_repo: StaffRepository,
    ):
        self._config = config
        self._expense_repo = expense_repo
        self._staff_repo = staff_repo

    def _build_provider(self):
        return ProviderFactory.create(self._config)

    def _build_data_summary(self, staff_id: Optional[int] = None) -> str:
        stats = self._expense_repo.get_total_stats(staff_id)
        if stats.total_expenses == 0:
            return ""

        cat_stats = self._expense_repo.get_category_stats(staff_id)
        mon_stats = self._expense_repo.get_monthly_stats(staff_id)

        staff_name = "you"
        if staff_id:
            s = self._staff_repo.get_by_id(staff_id)
            if s:
                staff_name = s.name

        cat_lines = "\n".join(
            f"- {c.category}: ${c.total:.2f} ({c.count} txns, avg ${c.avg:.2f})"
            for c in cat_stats
        )
        mon_lines = "\n".join(
            f"- {m.month}: ${m.total:.2f} ({m.count} txns)"
            for m in mon_stats
        )

        return (
            f"Expense Analysis for {staff_name}:\n"
            f"- Total spent: ${stats.total_amount:.2f}\n"
            f"- Transactions: {stats.total_expenses}\n"
            f"- Average per transaction: ${stats.avg_amount:.2f}\n"
            f"- Min: ${stats.min_amount:.2f} | Max: ${stats.max_amount:.2f}\n\n"
            f"Spending by Category:\n{cat_lines}\n\n"
            f"Monthly Spending:\n{mon_lines}"
        )

    def get_spending_insights(self, staff_id: Optional[int] = None) -> dict:
        summary = self._build_data_summary(staff_id)
        if not summary:
            return {"error": "No expense data available for analysis."}

        provider = self._build_provider()
        return provider.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an expert financial analyst. Analyze the expense data "
                        "and provide concise, actionable insights. Use markdown with "
                        "sections: **Spending Summary**, **Key Observations**, "
                        "**Recommendations**. Be specific with numbers. Keep it under "
                        "500 words."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Analyze this expense data and provide personalized insights:\n\n{summary}",
                },
            ]
        )

    def detect_anomalies(self, staff_id: Optional[int] = None) -> dict:
        cat_stats = self._expense_repo.get_category_stats(staff_id)
        recent = self._expense_repo.get_recent(staff_id)

        if not recent:
            return {"error": "No recent expense data available."}

        lines = "Recent expenses (last 30 days):\n"
        for e in recent:
            lines += (
                f"- ${e.amount:.2f} | {e.category} | "
                f"{e.description or 'N/A'} | {e.expense_date}\n"
            )

        lines += "\nCategory averages:\n"
        for c in cat_stats:
            lines += f"- {c.category}: avg ${c.avg:.2f}, max ${c.max:.2f}\n"

        provider = self._build_provider()
        return provider.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an AI auditor. Analyze expenses for anomalies, "
                        "unusual patterns, or concerning habits. Be specific about "
                        "which transactions look unusual and why. Use markdown with "
                        "**Anomalies Found** or **No Anomalies** header."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Analyze these expenses for anomalies:\n\n{lines}",
                },
            ],
            temperature=0.3,
        )

    def get_budget_recommendations(
        self,
        staff_id: Optional[int] = None,
        monthly_budget: Optional[float] = None,
    ) -> dict:
        stats = self._expense_repo.get_total_stats(staff_id)
        cat_stats = self._expense_repo.get_category_stats(staff_id)
        mon_stats = self._expense_repo.get_monthly_stats(staff_id)

        if stats.total_expenses == 0:
            return {"error": "No expense data available."}

        avg_monthly = stats.total_amount / max(len(mon_stats), 1)

        cat_lines = "\n".join(
            f"- {c.category}: ${c.total:.2f} total, ${c.avg:.2f}/txn"
            for c in cat_stats
        )
        mon_lines = "\n".join(
            f"- {m.month}: ${m.total:.2f}" for m in mon_stats
        )

        summary = (
            f"Average monthly spending: ${avg_monthly:.2f}\n"
            f"Monthly budget target: "
            f"{'$' + f'{monthly_budget:.2f}' if monthly_budget else 'Not set'}\n\n"
            f"Category breakdown:\n{cat_lines}\n\n"
            f"Monthly history:\n{mon_lines}"
        )

        budget_context = (
            f"The user has a monthly budget of ${monthly_budget:.2f}."
            if monthly_budget
            else "The user has no monthly budget set."
        )

        provider = self._build_provider()
        return provider.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a budgeting expert. Provide personalized budget "
                        "recommendations. Use markdown with **Budget Analysis** and "
                        "**Recommended Budget** sections. Suggest specific category "
                        "limits."
                    ),
                },
                {
                    "role": "user",
                    "content": f"{budget_context} Recommend a practical budget:\n\n{summary}",
                },
            ]
        )

    def test_connection(self):
        provider = self._build_provider()
        result = provider.chat(
            [
                {
                    "role": "user",
                    "content": "Reply with exactly 'OK' if you receive this.",
                }
            ],
            temperature=0,
        )
        if result.get("success"):
            return True, result.get("content", "")
        return False, result.get("error", "Connection failed")
