from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.database import StaffRepository
from src.services.insight_service import InsightService
from src.config import ConfigManager
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class InsightsScreen(BaseScreen):
    def __init__(
        self,
        console: Console,
        insight_service: InsightService,
        staff_repo: StaffRepository,
        config: ConfigManager,
    ):
        self._console = console
        self._insight_service = insight_service
        self._staff_repo = staff_repo
        self._config = config

    def _select_staff(self, active_staff_id: Optional[int] = None) -> Optional[int]:
        if active_staff_id:
            staff = self._staff_repo.get_by_id(active_staff_id)
            if staff:
                return staff.id
        return None

    def _check_api_key(self) -> bool:
        provider = self._config.get("ai_provider", "openrouter")
        key = self._config.get(f"{provider}_api_key", "")
        if not key:
            console.print(
                Panel(
                    f"[yellow]No API key configured for {provider.upper()}.[/yellow]\n"
                    "Go to [bold cyan]Settings → Set API Key[/bold cyan] first.",
                    border_style="yellow",
                    title="API Key Required",
                )
            )
            Prompt.ask("\n[dim]Press Enter to go back...[/dim]")
            return False
        return True

    def show(self, active_staff_id: Optional[int] = None) -> None:
        sid = self._select_staff(active_staff_id)
        if sid is None:
            console.print("[yellow]No staff selected. Use Switch Staff first.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        staff = self._staff_repo.get_by_id(sid)
        if not staff:
            return

        if not self._check_api_key():
            return

        while True:
            console.clear()
            show_logo()
            console.print(
                Panel(
                    f"[bold cyan]AI Insights — {staff.name}[/bold cyan]",
                    border_style="cyan",
                )
            )

            choice = show_menu(
                [
                    "General Spending Insights",
                    "Anomaly Detection",
                    "Budget Recommendations",
                    "Set Monthly Budget",
                ],
                title="AI-Powered Analysis",
            )

            if choice == "0":
                break

            if choice == "4":
                budget = FloatPrompt.ask("-  Enter monthly budget target ($)", default=0)
                if budget > 0:
                    self._config.set("monthly_budget", budget)
                    console.print(f"[green]Monthly budget set to ${budget:.2f}[/green]")
                else:
                    self._config.set("monthly_budget", None)
                    console.print("[yellow]Budget target cleared.[/yellow]")
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
                continue

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Analyzing your expenses...", total=None)

                if choice == "1":
                    result = self._insight_service.get_spending_insights(sid)
                elif choice == "2":
                    result = self._insight_service.detect_anomalies(sid)
                elif choice == "3":
                    mb = self._config.get("monthly_budget")
                    result = self._insight_service.get_budget_recommendations(sid, mb)
                else:
                    continue

            console.clear()
            show_logo()

            if "error" in result:
                console.print(
                    Panel(f"[red]{result['error']}[/red]", border_style="red")
                )
            elif result.get("success"):
                model_label = result.get("model", "")
                header = "AI Insights"
                if model_label:
                    header += f"  [dim]({model_label})[/dim]"
                md = Markdown(result["content"])
                console.print(Panel(md, border_style="green", title=header))
            else:
                console.print(
                    Panel(
                        f"[red]{result.get('error', 'Unknown error')}[/red]",
                        border_style="red",
                    )
                )

            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
