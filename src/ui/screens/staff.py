from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.console import Console

from src.database import StaffRepository
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class StaffScreen(BaseScreen):
    def __init__(self, console: Console, staff_repo: StaffRepository):
        self._console = console
        self._staff_repo = staff_repo

    def show(self) -> None:
        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["Add New Staff Member", "View All Staff", "Delete Staff Member"],
                title="Staff Management",
            )
            if choice == "0":
                return
            if choice == "1":
                self._add_staff()
            elif choice == "2":
                self._view_all()
            elif choice == "3":
                self._delete_staff()

    def _add_staff(self):
        console.clear()
        show_logo()
        console.print(
            Panel("[bold cyan]Add New Staff Member[/bold cyan]", border_style="cyan")
        )
        name = Prompt.ask("-  Name")
        if not name.strip():
            console.print("[red]Name is required![/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        department = Prompt.ask("-  Department", default="")
        email = Prompt.ask("-  Email", default="")
        try:
            self._staff_repo.add(name, department, email)
            console.print(f"[green]Staff member '{name}' added![/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _view_all(self):
        console.clear()
        show_logo()
        console.print(
            Panel("[bold cyan]All Staff Members[/bold cyan]", border_style="cyan")
        )
        staff_list = self._staff_repo.get_all()
        if staff_list:
            table = Table(box=box.ROUNDED, border_style="blue")
            table.add_column("ID", style="bold yellow")
            table.add_column("Name", style="bold white")
            table.add_column("Department", style="cyan")
            table.add_column("Email", style="dim")
            table.add_column("Joined", style="green")
            for s in staff_list:
                table.add_row(
                    str(s.id),
                    s.name,
                    s.department or "-",
                    s.email or "-",
                    s.created_at[:10] if s.created_at else "-",
                )
            console.print(table)
        else:
            console.print("[yellow]No staff members registered yet.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _delete_staff(self):
        console.clear()
        show_logo()
        console.print(
            Panel("[bold cyan]Delete Staff Member[/bold cyan]", border_style="red")
        )
        staff_list = self._staff_repo.get_all()
        if not staff_list:
            console.print("[yellow]No staff members to delete.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        for s in staff_list:
            console.print(
                f"  [yellow]{s.id}.[/yellow] {s.name} ({s.department or 'No dept'})"
            )
        del_id = IntPrompt.ask("-  Enter staff ID to delete")
        if Confirm.ask("[red]Delete this staff member and all their expenses?[/red]"):
            self._staff_repo.delete(del_id)
            console.print("[green]Staff member deleted.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
