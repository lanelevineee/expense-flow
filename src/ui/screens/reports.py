import os
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.console import Console

from src.services.data_service import DataService
from src.database import StaffRepository
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class ReportsScreen(BaseScreen):
    def __init__(self, console: Console, data_service: DataService, staff_repo: StaffRepository):
        self._console = console
        self._data_service = data_service
        self._staff_repo = staff_repo

    def show(self, active_staff_id: int) -> None:
        if not active_staff_id or not self._staff_repo.get_by_id(active_staff_id):
            console.print("[yellow]No active staff selected.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        staff = self._staff_repo.get_by_id(active_staff_id)
        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["Export CSV", "Import CSV", "Generate HTML Report", "Create Backup", "Restore Backup", "List Backups"],
                title="Reports & Data"
            )
            if choice == "0":
                return
            if choice == "1":
                self._export_csv(active_staff_id)
            elif choice == "2":
                self._import_csv(active_staff_id)
            elif choice == "3":
                self._html_report(active_staff_id, staff)
            elif choice == "4":
                self._backup()
            elif choice == "5":
                self._restore()
            elif choice == "6":
                self._list_backups()

    def _export_csv(self, sid: int):
        path = Prompt.ask("-  File path", default=f"expenses_export_{sid}.csv")
        try:
            self._data_service.export_csv(sid, path)
            console.print(f"[green]Exported to {path}[/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _import_csv(self, sid: int):
        path = Prompt.ask("-  File path")
        if not os.path.exists(path):
            console.print("[red]File not found.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        try:
            count = self._data_service.import_csv(sid, path)
            console.print(f"[green]Imported {count} expenses.[/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _html_report(self, sid: int, staff):
        path = Prompt.ask("-  Save as", default=f"report_{staff.name}.html")
        try:
            html = self._data_service.generate_report_html(sid)
            with open(path, "w") as f:
                f.write(html)
            console.print(f"[green]Report saved to {path}[/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _backup(self):
        path = self._data_service.export_data()
        console.print(f"[green]Backup saved: {path}[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _restore(self):
        backups = self._data_service.list_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        console.print("\n[bold yellow]Available backups:[/bold yellow]")
        for i, b in enumerate(backups, 1):
            size_kb = b["size"] / 1024
            console.print(f"  [cyan]{i}.[/cyan] {b['name']} ({size_kb:.1f} KB)")
        idx = IntPrompt.ask("-  Backup number to restore", choices=[str(i) for i in range(1, len(backups) + 1)])
        if Confirm.ask("[bold red]Restore will replace ALL current data. Continue?[/bold red]"):
            ok = self._data_service.restore_backup(backups[idx - 1]["path"])
            if ok:
                console.print("[green]Restored. Restart the app for changes to take effect.[/green]")
            else:
                console.print("[red]Restore failed.[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _list_backups(self):
        backups = self._data_service.list_backups()
        if not backups:
            console.print("[yellow]No backups found.[/yellow]")
        else:
            for b in backups:
                size_kb = b["size"] / 1024
                console.print(f"  {b['name']} ({size_kb:.1f} KB)")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
