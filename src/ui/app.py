import os
from typing import Optional

from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt

from src.config import ConfigManager
from src.database import (
    DatabaseConnection,
    StaffRepository,
    ExpenseRepository,
    CategoryRepository,
    PaymentMethodRepository,
    RecurringExpenseRepository,
    GamificationRepository,
    AuditLogRepository,
)
from src.db.schema import init_tables
from src.services.expense_service import ExpenseService
from src.services.analytics_service import AnalyticsService
from src.services.insight_service import InsightService
from src.services.category_service import CategoryService
from src.services.gamification_service import GamificationService
from src.services.recurring_service import RecurringService
from src.services.data_service import DataService
from src.services.budget_service import BudgetService
from src.services.undo_service import UndoService
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu
from src.ui.components.qr import show_qr, get_local_ip
from src.ui.screens.staff import StaffScreen
from src.ui.screens.expense import RecordExpenseScreen, ViewExpensesScreen
from src.ui.screens.categories import CategoriesScreen
from src.ui.screens.recurring import RecurringScreen
from src.ui.screens.gamification import GamificationScreen
from src.ui.screens.analytics import AnalyticsScreen
from src.ui.screens.insights import InsightsScreen
from src.ui.screens.reports import ReportsScreen
from src.ui.screens.settings import SettingsScreen


class App:
    def __init__(self):
        self.config = ConfigManager()
        self.db = DatabaseConnection()
        init_tables(self.db)

        # repositories
        self.staff_repo = StaffRepository(self.db)
        self.expense_repo = ExpenseRepository(self.db)
        self.category_repo = CategoryRepository(self.db)
        self.payment_repo = PaymentMethodRepository(self.db)
        self.rec_repo = RecurringExpenseRepository(self.db)
        self.gami_repo = GamificationRepository(self.db)
        self.audit_repo = AuditLogRepository(self.db)

        # services
        self.category_service = CategoryService(self.category_repo)
        self.expense_service = ExpenseService(self.staff_repo, self.expense_repo)
        self.analytics_service = AnalyticsService(self.expense_repo)
        self.gami_service = GamificationService(self.gami_repo)
        self.recurring_service = RecurringService(self.rec_repo, self.expense_repo)
        self.data_service = DataService(self.expense_repo, self.staff_repo)
        self.budget_service = BudgetService(self.expense_repo)
        self.undo_service = UndoService(self.audit_repo, self.expense_repo, self.staff_repo)
        self.insight_service = InsightService(
            self.config, self.expense_repo, self.staff_repo
        )

        # seed default data
        self.gami_service.ensure_seeded()

        # auto-start web server
        self._web_server = None
        try:
            from src.web.server import start_background_server
            self._web_server = start_background_server(port=7070)
        except Exception as e:
            import logging
            logging.getLogger("expense_tracker").warning("Web server failed to start: %s", e)

        # screens
        self._screens = {
            "staff": StaffScreen(console, self.staff_repo),
            "record_expense": RecordExpenseScreen(
                console, self.expense_service, self.staff_repo,
                self.category_service, self.payment_repo, self.gami_service,
            ),
            "view_expenses": ViewExpensesScreen(
                console, self.expense_service, self.staff_repo, self.undo_service,
            ),
            "categories": CategoriesScreen(console, self.category_service),
            "recurring": RecurringScreen(
                console, self.recurring_service, self.category_service, self.staff_repo,
            ),
            "gamification": GamificationScreen(console, self.gami_service, self.staff_repo),
            "analytics": AnalyticsScreen(
                console, self.analytics_service, self.staff_repo
            ),
            "insights": InsightsScreen(
                console, self.insight_service, self.staff_repo, self.config
            ),
            "reports": ReportsScreen(console, self.data_service, self.staff_repo),
            "settings": SettingsScreen(
                console,
                self.config,
                self.insight_service,
                self.expense_repo,
                self.staff_repo,
                self.payment_repo,
                self.data_service,
            ),
        }

        self._active_staff_id: Optional[int] = self.config.get("active_staff_id")
        self._resolve_initial_staff()

    def _resolve_initial_staff(self):
        if self._active_staff_id:
            staff = self.staff_repo.get_by_id(self._active_staff_id)
            if not staff:
                self._active_staff_id = None
                self.config.set("active_staff_id", None)

        if self._active_staff_id is not None:
            return

        staff_list = self.staff_repo.get_all()
        if staff_list:
            console.clear()
            show_logo()
            console.print(
                "[bold yellow]Select an active staff member to begin:[/bold yellow]"
            )
            sid = self._prompt_staff_selection()
            if sid:
                self._active_staff_id = sid
                self.config.set("active_staff_id", sid)
        else:
            self._create_first_staff()

    def _create_first_staff(self):
        console.clear()
        show_logo()
        console.print(
            "[bold yellow]Welcome! Let's create your first staff profile.[/bold yellow]"
        )
        name = Prompt.ask("-  Your name")
        if name.strip():
            dept = Prompt.ask("-  Department", default="Engineering")
            email = Prompt.ask("-  Email", default="")
            password = Prompt.ask("-  Set a password", password=True)
            sid = self.staff_repo.add(name, dept, email)
            if password:
                from src.auth.password import PasswordManager
                hashed = PasswordManager.hash_password(password)
                self.staff_repo.update(sid, password_hash=hashed)
            self._active_staff_id = sid
            self.config.set("active_staff_id", sid)
            console.print(f"[green]Welcome, {name}![/green]")

    def _prompt_staff_selection(self) -> int:
        staff_list = self.staff_repo.get_all()
        if not staff_list:
            return 0
        for s in staff_list:
            console.print(
                f"  [yellow]{s.id}.[/yellow] {s.name} ({s.department or 'No dept'})"
            )
        sid = IntPrompt.ask("-  Select staff ID", default=1)
        staff = self.staff_repo.get_by_id(sid)
        if staff:
            return staff.id
        return 0

    def _show_active_staff_banner(self):
        if self._active_staff_id:
            staff = self.staff_repo.get_by_id(self._active_staff_id)
            if staff:
                console.print(
                    Panel(
                        f"[bold cyan]Active: {staff.name}[/bold cyan]",
                        border_style="cyan",
                    )
                )

    def _handle_switch_staff(self):
        staff_list = self.staff_repo.get_all()
        if not staff_list:
            console.print("[yellow]No other staff members available.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        console.clear()
        show_logo()
        console.print(
            Panel("[bold cyan]Switch Active Staff[/bold cyan]", border_style="cyan")
        )
        sid = self._prompt_staff_selection()
        if sid:
            self._active_staff_id = sid
            self.config.set("active_staff_id", sid)
            staff = self.staff_repo.get_by_id(sid)
            console.print(f"[green]Switched to {staff.name}[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _handle_backup_restore(self):
        from src.services.backup_service import backup_pg_to_sqlite, restore_sqlite_to_pg
        from src import config as cfg

        console.clear()
        show_logo()
        console.print(
            Panel("[bold cyan]Backup / Restore[/bold cyan]", border_style="cyan")
        )

        if self.db.is_postgres:
            console.print("[green]PostgreSQL connected[/green]")
            console.print("1. Backup PostgreSQL to SQLite")
            console.print("2. Restore SQLite backup to PostgreSQL")
            console.print("0. Back")
            choice = Prompt.ask("Choose", choices=["0", "1", "2"])
            if choice == "1":
                path = os.path.join(cfg.CONFIG_DIR, "backup.db")
                console.print(f"[dim]Backing up to {path}...[/dim]")
                try:
                    result = backup_pg_to_sqlite(self.db, path)
                    console.print(f"[green]Backup complete: {result}[/green]")
                except Exception as e:
                    console.print(f"[red]Backup failed: {e}[/red]")
            elif choice == "2":
                path = os.path.join(cfg.CONFIG_DIR, "backup.db")
                if not os.path.exists(path):
                    console.print(f"[red]No backup found at {path}[/red]")
                else:
                    if Confirm.ask(f"Restore from {path}? This will overwrite current data"):
                        try:
                            count = restore_sqlite_to_pg(path, self.db)
                            console.print(f"[green]Restored {count} rows[/green]")
                        except Exception as e:
                            console.print(f"[red]Restore failed: {e}[/red]")
        else:
            console.print("[yellow]SQLite mode - backup creates a copy[/yellow]")
            console.print("1. Copy database")
            console.print("0. Back")
            choice = Prompt.ask("Choose", choices=["0", "1"])
            if choice == "1":
                import shutil
                src = os.path.join(cfg.CONFIG_DIR, "expenses.db")
                dst = os.path.join(cfg.CONFIG_DIR, "expenses_backup.db")
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    console.print(f"[green]Backup saved to {dst}[/green]")
                else:
                    console.print("[red]Database file not found[/red]")

        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def run(self):
        while True:
            console.clear()
            show_logo()
            self._show_active_staff_banner()

            choice = show_menu(
                [
                    "Staff Management",
                    "Record Expense",
                    "View Expenses",
                    "Categories",
                    "Recurring",
                    "Gamification",
                    "Spending Analytics",
                    "AI Insights",
                    "Reports & Data",
                    "Settings",
                    "Backup / Restore",
                    "Web Access (QR Code)",
                    "Switch Staff",
                ],
                title="Main Menu",
                shortcuts={
                    1: "S",
                    2: "R",
                    3: "V",
                    4: "C",
                    5: "U",
                    6: "G",
                    7: "N",
                    8: "I",
                    9: "E",
                    10: "T",
                    11: "B",
                    12: "W",
                    13: "Q",
                },
            )

            if choice == "0":
                if Confirm.ask("Are you sure you want to exit?"):
                    console.print(
                        "\n[bold green]Thank you for using Smart Expense Tracker![/bold green]"
                    )
                    console.print("[dim]Data stored at ~/.expense_tracker/[/dim]")
                    break
            elif choice == "1":
                self._screens["staff"].show()
            elif choice == "2":
                self._screens["record_expense"].show(self._active_staff_id)
            elif choice == "3":
                self._screens["view_expenses"].show(self._active_staff_id)
            elif choice == "4":
                self._screens["categories"].show()
            elif choice == "5":
                self._screens["recurring"].show(self._active_staff_id)
            elif choice == "6":
                self._screens["gamification"].show(self._active_staff_id)
            elif choice == "7":
                self._screens["analytics"].show(self._active_staff_id)
            elif choice == "8":
                self._screens["insights"].show(self._active_staff_id)
            elif choice == "9":
                self._screens["reports"].show(self._active_staff_id)
            elif choice == "10":
                self._screens["settings"].show(self._active_staff_id)
            elif choice == "11":
                self._handle_backup_restore()
            elif choice == "12":
                qr_text = show_qr(port=7070, label="Scan to open web platform on your phone")
                console.print(qr_text)
                Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")
            elif choice == "13":
                self._handle_switch_staff()

        self.db.close()
