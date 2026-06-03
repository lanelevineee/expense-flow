from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import ConfigManager
from src.services.insight_service import InsightService
from src.services.data_service import DataService
from src.database import StaffRepository, ExpenseRepository, PaymentMethodRepository
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu
from src.ui.components.themes import THEMES


CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "INR", "BRL", "MXN", "GHS"]


class SettingsScreen(BaseScreen):
    def __init__(
        self,
        console: Console,
        config: ConfigManager,
        insight_service: InsightService,
        expense_repo: ExpenseRepository,
        staff_repo: StaffRepository,
        payment_repo: PaymentMethodRepository,
        data_service: DataService,
    ):
        self._console = console
        self._config = config
        self._insight_service = insight_service
        self._expense_repo = expense_repo
        self._staff_repo = staff_repo
        self._payment_repo = payment_repo
        self._data_service = data_service

    @staticmethod
    def _mask_key(key: str) -> str:
        if not key:
            return "[dim](not set)[/dim]"
        return key[:8] + "..." + key[-4:] if len(key) > 12 else key

    def show(self, active_staff_id: Optional[int] = None) -> None:
        while True:
            console.clear()
            show_logo()

            provider = self._config.get("ai_provider", "openrouter")
            or_key = self._config.get("openrouter_api_key", "")
            groq_key = self._config.get("groq_api_key", "")
            or_model = self._config.get("openrouter_model", "openai/gpt-4o-mini")
            groq_model = self._config.get("groq_model", "llama3-70b-8192")
            default_model = self._config.get("default_model", "openai/gpt-4o-mini")
            mb = self._config.get("monthly_budget")

            budget_line = (
                f"[cyan]Monthly Budget:[/cyan]    ${mb:.2f}"
                if mb
                else f"[cyan]Monthly Budget:[/cyan]    [dim]Not set[/dim]"
            )

            staff = self._staff_repo.get_by_id(active_staff_id) if active_staff_id else None
            currency_line = f"[cyan]Currency:[/cyan]          [yellow]{staff.currency}[/yellow]" if staff else ""
            theme_line = f"[cyan]Theme:[/cyan]              [yellow]{staff.theme}[/yellow]" if staff else ""

            info = Panel(
                "[bold]Current Configuration[/bold]\n\n"
                f"[cyan]AI Provider:[/cyan]       [yellow]{provider.upper()}[/yellow]\n"
                f"[cyan]OpenRouter Key:[/cyan]    {self._mask_key(or_key)}\n"
                f"[cyan]Groq Key:[/cyan]          {self._mask_key(groq_key)}\n"
                f"[cyan]Default Model:[/cyan]     {default_model}\n"
                f"[cyan]OpenRouter Model:[/cyan]  {or_model}\n"
                f"[cyan]Groq Model:[/cyan]        {groq_model}\n"
                f"[cyan]Config Source:[/cyan]     [dim]Environment > .env file > runtime[/dim]\n"
                f"{budget_line}\n"
                f"{currency_line}\n"
                f"{theme_line}",
                border_style="cyan",
                title="Settings",
            )
            console.print(info)

            options = [
                "Set OpenRouter API Key",
                "Set Groq API Key",
                "Set AI Provider",
                "Set OpenRouter Model",
                "Set Groq Model",
                "Test API Connection",
                "Set Monthly Budget",
                "Delete All Data",
            ]
            if staff:
                options.extend([
                    "Set Currency",
                    "Set Theme",
                    "Manage Payment Methods",
                    "Backup / Restore",
                ])

            choice = show_menu(options, title="Settings Menu")

            if choice == "0":
                break
            elif choice == "1":
                key = Prompt.ask("-  OpenRouter API Key", password=True)
                if key:
                    self._config.set("openrouter_api_key", key.strip())
                    console.print("[green]OpenRouter API key saved![/green]")
            elif choice == "2":
                key = Prompt.ask("-  Groq API Key", password=True)
                if key:
                    self._config.set("groq_api_key", key.strip())
                    console.print("[green]Groq API key saved![/green]")
            elif choice == "3":
                prov = show_menu(
                    ["OpenRouter", "Groq"],
                    title="Select AI Provider",
                    return_option=False,
                )
                if prov == "1":
                    self._config.set("ai_provider", "openrouter")
                elif prov == "2":
                    self._config.set("ai_provider", "groq")
                console.print("[green]Provider updated![/green]")
            elif choice == "4":
                model = Prompt.ask(
                    "-  OpenRouter model", default="openai/gpt-4o-mini"
                )
                self._config.set("openrouter_model", model.strip())
                console.print("[green]OpenRouter model updated![/green]")
            elif choice == "5":
                model = Prompt.ask("-  Groq model", default="llama3-70b-8192")
                self._config.set("groq_model", model.strip())
                console.print("[green]Groq model updated![/green]")
            elif choice == "6":
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task("Testing API connection...", total=None)
                    ok, msg = self._insight_service.test_connection()
                if ok:
                    console.print("[green]API connection successful![/green]")
                else:
                    console.print(f"[red]Connection failed: {msg}[/red]")
            elif choice == "7":
                budget = FloatPrompt.ask("-  Monthly budget ($)", default=0)
                self._config.set("monthly_budget", budget if budget > 0 else None)
                console.print("[green]Monthly budget set.[/green]")
            elif choice == "8":
                if Confirm.ask(
                    "[bold red]Delete ALL data (expenses and staff)?[/bold red]"
                ):
                    if Confirm.ask("[red]This cannot be undone. Confirm?[/red]"):
                        self._expense_repo.clear_all()
                        for s in self._staff_repo.get_all():
                            self._staff_repo.delete(s.id)
                        self._config.set("active_staff_id", None)
                        console.print("[green]All data cleared.[/green]")
            elif choice == "9" and staff:
                self._set_currency(staff.id)
            elif choice == "10" and staff:
                self._set_theme(staff.id)
            elif choice == "11" and staff:
                self._manage_payment_methods(staff.id)
            elif choice == "12" and staff:
                self._backup_restore()

            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _set_currency(self, staff_id: int):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Select Currency[/bold cyan]", border_style="cyan"))
        for i, c in enumerate(CURRENCIES, 1):
            console.print(f"  [cyan]{i}.[/cyan] {c}")
        cc = IntPrompt.ask("-  Currency", choices=[str(i) for i in range(1, len(CURRENCIES) + 1)])
        currency = CURRENCIES[cc - 1]
        self._staff_repo.update(staff_id, currency=currency)
        console.print(f"[green]Currency set to {currency}[/green]")

    def _set_theme(self, staff_id: int):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Select Theme[/bold cyan]", border_style="cyan"))
        theme_names = list(THEMES.keys())
        for i, t in enumerate(theme_names, 1):
            console.print(f"  [cyan]{i}.[/cyan] {t.capitalize()}")
        tc = IntPrompt.ask("-  Theme", choices=[str(i) for i in range(1, len(theme_names) + 1)])
        theme = theme_names[tc - 1]
        self._staff_repo.update(staff_id, theme=theme)
        console.print(f"[green]Theme set to {theme}[/green]")

    def _manage_payment_methods(self, staff_id: int):
        while True:
            console.clear()
            show_logo()
            pms = self._payment_repo.get_all(staff_id)
            if pms:
                table = Table(box=box.ROUNDED, border_style="blue")
                table.add_column("ID", style="bold yellow", width=4)
                table.add_column("Name", style="bold white")
                table.add_column("Type", style="cyan")
                table.add_column("Default", style="green")
                for pm in pms:
                    table.add_row(str(pm.id), pm.name, pm.type, "★" if pm.is_default else "")
                console.print(table)
            else:
                console.print("[yellow]No payment methods.[/yellow]")

            choice = show_menu(
                ["Add Payment Method", "Set Default", "Delete"],
                title="Payment Methods"
            )
            if choice == "0":
                return
            elif choice == "1":
                name = Prompt.ask("-  Name (e.g. Visa, Cash)")
                ptype = Prompt.ask("-  Type", default="credit")
                self._payment_repo.add(staff_id, name, ptype)
                console.print(f"[green]'{name}' added.[/green]")
            elif choice == "2":
                if pms:
                    pm_id = IntPrompt.ask("-  Payment method ID to set as default")
                    self._payment_repo.set_default(pm_id, staff_id)
                    console.print("[green]Default updated.[/green]")
                else:
                    console.print("[yellow]No payment methods to set.[/yellow]")
            elif choice == "3":
                if pms:
                    pm_id = IntPrompt.ask("-  Payment method ID to delete")
                    if Confirm.ask("[red]Delete?[/red]"):
                        self._payment_repo.delete(pm_id)
                        console.print("[green]Deleted.[/green]")
                else:
                    console.print("[yellow]No payment methods to delete.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _backup_restore(self):
        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["Create Backup", "List Backups", "Restore Backup"],
                title="Backup / Restore"
            )
            if choice == "0":
                return
            elif choice == "1":
                path = self._data_service.export_data()
                console.print(f"[green]Backup saved: {path}[/green]")
            elif choice == "2":
                backups = self._data_service.list_backups()
                if not backups:
                    console.print("[yellow]No backups found.[/yellow]")
                else:
                    for b in backups:
                        size_kb = b["size"] / 1024
                        console.print(f"  {b['name']} ({size_kb:.1f} KB)")
            elif choice == "3":
                backups = self._data_service.list_backups()
                if not backups:
                    console.print("[yellow]No backups found.[/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
                    continue
                for i, b in enumerate(backups, 1):
                    size_kb = b["size"] / 1024
                    console.print(f"  [cyan]{i}.[/cyan] {b['name']} ({size_kb:.1f} KB)")
                idx = IntPrompt.ask("-  Backup number to restore", choices=[str(i) for i in range(1, len(backups) + 1)])
                if Confirm.ask("[bold red]Restore replaces ALL data. Continue?[/bold red]"):
                    ok = self._data_service.restore_backup(backups[idx - 1]["path"])
                    if ok:
                        console.print("[green]Restored. Restart app to apply.[/green]")
                    else:
                        console.print("[red]Restore failed.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
