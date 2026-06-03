from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

from src.services.gamification_service import GamificationService
from src.database import StaffRepository
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class GamificationScreen(BaseScreen):
    def __init__(self, console: Console, gamification_service: GamificationService,
                 staff_repo: StaffRepository):
        self._console = console
        self._gami = gamification_service
        self._staff_repo = staff_repo

    def show(self, active_staff_id: int) -> None:
        if not active_staff_id or not self._staff_repo.get_by_id(active_staff_id):
            console.print("[yellow]No active staff selected.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["My Stats & Level", "Achievements", "Active Challenges", "Leaderboard"],
                title="Gamification"
            )
            if choice == "0":
                return
            if choice == "1":
                self._stats(active_staff_id)
            elif choice == "2":
                self._achievements(active_staff_id)
            elif choice == "3":
                self._challenges(active_staff_id)
            elif choice == "4":
                self._leaderboard()

    def _stats(self, sid: int):
        stats = self._gami.get_stats(sid)
        staff = self._staff_repo.get_by_id(sid)
        console.clear()
        show_logo()
        console.print(Panel(f"[bold cyan]{staff.name}'s Stats[/bold cyan]", border_style="cyan"))

        level_xp = self._gami.get_level_xp(stats.level)
        next_xp = self._gami.get_level_xp(stats.level + 1)
        xp_in_level = stats.xp - level_xp
        xp_needed = next_xp - level_xp
        xp_pct = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100

        console.print(f"\n[bold yellow]Level {stats.level}[/bold yellow]")
        console.print(f"  XP: {stats.xp} / {next_xp}")
        bar = "█" * int(xp_pct / 4) + "░" * (25 - int(xp_pct / 4))
        console.print(f"  [green]{bar}[/green] {xp_pct:.1f}%")

        console.print(f"\n[bold yellow]Streaks[/bold yellow]")
        console.print(f"  Current: {stats.current_streak} days")
        console.print(f"  Longest: {stats.longest_streak} days")

        console.print(f"\n[bold yellow]Activity[/bold yellow]")
        console.print(f"  Total expenses: {stats.total_expenses}")
        console.print(f"  Active days: {stats.days_active}")

        earned = self._gami.get_earned(sid)
        console.print(f"\n[bold yellow]Badges[/bold yellow] {len(earned)} earned")
        for ua in earned[:5]:
            a = ua.achievement
            if a:
                console.print(f"  {a.icon} [bold]{a.name}[/bold] — {a.description}")

        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _achievements(self, sid: int):
        earned_ids = {ua.achievement_id for ua in self._gami.get_earned(sid)}
        all_ach = self._gami.get_achievements()
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Achievements[/bold cyan]", border_style="cyan"))

        table = Table(box=box.ROUNDED, border_style="yellow")
        table.add_column("Status", width=4)
        table.add_column("Icon", width=4)
        table.add_column("Achievement", style="bold white")
        table.add_column("Description", style="dim")
        table.add_column("XP", justify="right")

        for a in all_ach:
            earned = a.id in earned_ids
            table.add_row(
                "Earned" if earned else "Locked",
                a.icon,
                a.name,
                a.description,
                f"+{a.xp_reward} XP",
            )
        console.print(table)
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _challenges(self, sid: int):
        challenges = self._gami.get_active_challenges()
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Active Challenges[/bold cyan]", border_style="cyan"))

        if not challenges:
            console.print("[yellow]No active challenges right now.[/yellow]")
        else:
            for c in challenges:
                cp = self._gami.get_challenge_progress(c.id, sid)
                progress = cp.progress if cp else 0
                pct = min(100, int(progress / c.goal_value * 100)) if c.goal_value > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                status = "Completed!" if (cp and cp.completed) else f"{pct}%"
                console.print(f"\n[bold]{c.title}[/bold] — {c.description}")
                console.print(f"  [cyan]{bar}[/cyan] {progress}/{c.goal_value} ({status})")
                console.print(f"  Reward: [yellow]+{c.xp_reward} XP[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _leaderboard(self):
        board = self._gami.get_leaderboard()
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Staff Leaderboard[/bold cyan]", border_style="cyan"))

        table = Table(box=box.ROUNDED, border_style="green")
        table.add_column("#", style="bold yellow", width=4)
        table.add_column("Name", style="bold white")
        table.add_column("Department", style="cyan")
        table.add_column("Level", style="magenta", justify="right")
        table.add_column("XP", style="yellow", justify="right")
        table.add_column("Streak", style="green", justify="right")
        table.add_column("Badges", style="blue", justify="right")

        for i, entry in enumerate(board, 1):
            medal = {1: "#1", 2: "#2", 3: "#3"}.get(i, str(i))
            table.add_row(
                medal,
                entry["name"],
                entry.get("department", "") or "-",
                str(entry["level"]),
                str(entry["xp"]),
                f"{entry['streak']}d",
                str(entry["badges"]),
            )
        console.print(table)
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
