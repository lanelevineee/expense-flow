from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.console import Console

from src.services.recurring_service import RecurringService, FREQUENCY_MAP
from src.services.category_service import CategoryService
from src.database import StaffRepository
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class RecurringScreen(BaseScreen):
    def __init__(self, console: Console, recurring_service: RecurringService,
                 category_service: CategoryService, staff_repo: StaffRepository):
        self._console = console
        self._recurring_service = recurring_service
        self._category_service = category_service
        self._staff_repo = staff_repo

    def show(self, active_staff_id: int) -> None:
        if not active_staff_id or not self._staff_repo.get_by_id(active_staff_id):
            console.print("[yellow]No active staff. Use Switch Staff first.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["View Recurring", "Add Recurring", "Toggle Active/Inactive", "Process Due", "Delete"],
                title="Recurring Expenses"
            )
            if choice == "0":
                return
            if choice == "1":
                self._view(active_staff_id)
            elif choice == "2":
                self._add(active_staff_id)
            elif choice == "3":
                self._toggle(active_staff_id)
            elif choice == "4":
                self._process(active_staff_id)
            elif choice == "5":
                self._delete(active_staff_id)

    def _view(self, sid: int):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Recurring Expenses[/bold cyan]", border_style="cyan"))
        recs = self._recurring_service.get_all(sid)
        if recs:
            table = Table(box=box.ROUNDED, border_style="blue")
            table.add_column("ID", style="bold yellow", width=4)
            table.add_column("Amount", style="green", justify="right")
            table.add_column("Category", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Frequency", style="magenta")
            table.add_column("Next", style="yellow")
            table.add_column("Active", style="bold")
            for r in recs:
                table.add_row(str(r.id), f"${r.amount:.2f}", r.category,
                              r.description, r.frequency, r.next_date,
                              "Active" if r.active else "Inactive")
            console.print(table)
        else:
            console.print("[yellow]No recurring expenses.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _add(self, sid: int):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Add Recurring Expense[/bold cyan]", border_style="cyan"))
        cats = self._category_service.get_category_names() or ["Other"]
        console.print("[bold yellow]Category:[/bold yellow]")
        for i, cat in enumerate(cats, 1):
            console.print(f"  [cyan]{i}.[/cyan] {cat}")
        cc = IntPrompt.ask("-  Category", choices=[str(i) for i in range(1, len(cats) + 1)])
        category = cats[cc - 1]
        amount = FloatPrompt.ask("-  Amount ($)", min=0.01)
        description = Prompt.ask("-  Description", default="")

        freq_names = list(FREQUENCY_MAP.keys())
        console.print("[bold yellow]Frequency:[/bold yellow]")
        for i, f in enumerate(freq_names, 1):
            console.print(f"  [cyan]{i}.[/cyan] {f}")
        fc = IntPrompt.ask("-  Frequency", choices=[str(i) for i in range(1, len(freq_names) + 1)])
        frequency = freq_names[fc - 1]
        if Confirm.ask("\n[green]-  Save?[/green]", default=True):
            self._recurring_service.create(sid, amount, category, description, frequency)
            console.print("[green]Recurring expense created.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _toggle(self, sid: int):
        rid = IntPrompt.ask("-  Recurring ID to toggle")
        self._recurring_service.toggle_active(rid)
        console.print("[green]Toggled.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _process(self, sid: int):
        count = self._recurring_service.process_due(sid)
        console.print(f"[green]Processed {count} due recurring expenses.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _delete(self, sid: int):
        rid = IntPrompt.ask("-  Recurring ID to delete")
        if Confirm.ask("[red]Delete?[/red]"):
            self._recurring_service.delete(rid)
            console.print("[green]Deleted.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
