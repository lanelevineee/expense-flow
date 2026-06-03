from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, IntPrompt

from src.database import StaffRepository
from src.services.analytics_service import AnalyticsService
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.charts import render_bar_chart


class AnalyticsScreen(BaseScreen):
    def __init__(self, console: Console, analytics_service: AnalyticsService, staff_repo: StaffRepository):
        self._console = console
        self._analytics_service = analytics_service
        self._staff_repo = staff_repo

    def _select_staff(self, active_staff_id: Optional[int] = None) -> Optional[int]:
        if active_staff_id:
            staff = self._staff_repo.get_by_id(active_staff_id)
            if staff:
                return staff.id
        return self._prompt_staff_selection()

    def _prompt_staff_selection(self) -> Optional[int]:
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Staff Selection[/bold cyan]", border_style="cyan"))
        staff_list = self._staff_repo.get_all()
        if not staff_list:
            console.print("[yellow]No staff members found.[/yellow]")
            return None
        console.print("Available staff:")
        for s in staff_list:
            console.print(f"  [yellow]{s.id}.[/yellow] {s.name}")
        sid = IntPrompt.ask("-  Select staff ID", default=1)
        return sid if self._staff_repo.get_by_id(sid) else None

    def show(self, active_staff_id: Optional[int] = None) -> None:
        sid = self._select_staff(active_staff_id)
        if sid is None:
            return

        staff = self._staff_repo.get_by_id(sid)
        if not staff:
            return

        console.clear()
        show_logo()
        console.print(
            Panel(
                f"[bold cyan]Spending Analytics — {staff.name}[/bold cyan]",
                border_style="cyan",
            )
        )

        stats = self._analytics_service.get_overall_stats(sid)
        if stats.total_expenses > 0:
            console.print("\n[bold yellow]Overall Statistics[/bold yellow]")
            st = Table(box=box.SIMPLE, border_style="green")
            st.add_column("Metric", style="bold white")
            st.add_column("Value", style="cyan")
            st.add_row("Total Expenses", f"${stats.total_amount:.2f}")
            st.add_row("Transactions", str(stats.total_expenses))
            st.add_row("Average Transaction", f"${stats.avg_amount:.2f}")
            st.add_row("Smallest", f"${stats.min_amount:.2f}")
            st.add_row("Largest", f"${stats.max_amount:.2f}")
            console.print(st)

            cat_stats = self._analytics_service.get_category_breakdown(sid)
            if cat_stats:
                console.print("\n[bold yellow]Spending by Category[/bold yellow]")
                ct = Table(box=box.SIMPLE, border_style="blue")
                ct.add_column("Category", style="bold white")
                ct.add_column("Total", style="green", justify="right")
                ct.add_column("%", style="cyan", justify="right")
                ct.add_column("Count", justify="right")
                ct.add_column("Avg", style="magenta", justify="right")
                for r in cat_stats:
                    pct = (r.total / stats.total_amount * 100) if stats.total_amount > 0 else 0
                    ct.add_row(
                        r.category,
                        f"${r.total:.2f}",
                        f"{pct:.1f}%",
                        str(r.count),
                        f"${r.avg:.2f}",
                    )
                console.print(ct)

                console.print("\n[bold yellow]Spending Distribution[/bold yellow]")
                render_bar_chart(cat_stats, "category", "total", max_width=25, label_width=25)

            mon_stats = self._analytics_service.get_monthly_trend(sid)
            if mon_stats:
                console.print("\n[bold yellow]Monthly Spending Trend[/bold yellow]")
                render_bar_chart(mon_stats, "month", "total", max_width=25, label_width=10)
        else:
            console.print("[yellow]No expense data available for analysis.[/yellow]")

        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
