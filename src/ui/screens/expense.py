from datetime import datetime, timedelta, date
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm

from src.database import StaffRepository, PaymentMethodRepository
from src.services.expense_service import ExpenseService
from src.services.category_service import CategoryService
from src.services.undo_service import UndoService
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class RecordExpenseScreen(BaseScreen):
    def __init__(self, console: Console, expense_service: ExpenseService,
                 staff_repo: StaffRepository, category_service: CategoryService,
                 payment_repo: PaymentMethodRepository, gamification_service=None):
        self._console = console
        self._expense_service = expense_service
        self._staff_repo = staff_repo
        self._category_service = category_service
        self._payment_repo = payment_repo
        self._gami_service = gamification_service

    def show(self, active_staff_id: Optional[int] = None) -> None:
        sid = self._resolve_staff(active_staff_id)
        if sid is None:
            return
        staff = self._staff_repo.get_by_id(sid)
        if not staff:
            return

        console.clear()
        show_logo()
        console.print(Panel(f"[bold cyan]Record New Expense — {staff.name}[/bold cyan]", border_style="cyan"))

        cats = self._category_service.get_category_names()
        if not cats:
            console.print("[yellow]No categories defined. Use Categories menu to add some.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        console.print("\n[bold yellow]Select Category:[/bold yellow]")
        for i, cat in enumerate(cats, 1):
            console.print(f"  [cyan]{i}.[/cyan] {cat}")
            cat_choice = IntPrompt.ask("-  Category", choices=[str(i) for i in range(1, len(cats) + 1)])
        category = cats[cat_choice - 1]

        while True:
            amount = FloatPrompt.ask("-  Amount ($)")
            if amount > 0:
                break
            console.print("[red]Amount must be greater than zero.[/red]")
        description = Prompt.ask("-  Description", default="")

        pms = self._payment_repo.get_all(sid) if staff.currency else []
        payment_method_id = None
        if pms:
            console.print("\n[bold yellow]Payment Method:[/bold yellow]")
            for i, pm in enumerate(pms, 1):
                default_tag = " [dim](default)[/dim]" if pm.is_default else ""
                console.print(f"  [cyan]{i}.[/cyan] {pm.name} ({pm.type}){default_tag}")
            console.print(f"  [cyan]{len(pms)+1}.[/cyan] None")
            pm_choice = IntPrompt.ask("-  Payment method", choices=[str(i) for i in range(1, len(pms) + 2)], default="1")
            if 1 <= pm_choice <= len(pms):
                payment_method_id = pms[pm_choice - 1].id

        if Confirm.ask("-  Use today's date?", default=True):
            expense_date = date.today().isoformat()
        else:
            expense_date = Prompt.ask("-  Date (YYYY-MM-DD)", default=date.today().isoformat())

        if Confirm.ask("\n[bold green]-  Confirm and save?[/bold green]", default=True):
            try:
                self._expense_service.record(sid, amount, category, description, expense_date, payment_method_id)
                console.print(f"[green]Expense recorded: ${amount:.2f} for {category}[/green]")
                if self._gami_service:
                    try:
                        self._gami_service.record_activity(sid)
                        self._gami_service.update_challenge_progress(sid)
                    except Exception:
                        pass
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")

        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _resolve_staff(self, active_staff_id):
        if active_staff_id and self._staff_repo.get_by_id(active_staff_id):
            return active_staff_id
        return self._prompt_staff()

    def _prompt_staff(self):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Staff Selection[/bold cyan]", border_style="cyan"))
        staff_list = self._staff_repo.get_all()
        if not staff_list:
            return None
        for s in staff_list:
            console.print(f"  [yellow]{s.id}.[/yellow] {s.name}")
        sid = IntPrompt.ask("-  Select staff ID", default=1)
        return sid if self._staff_repo.get_by_id(sid) else None


class ViewExpensesScreen(BaseScreen):
    def __init__(self, console: Console, expense_service: ExpenseService,
                 staff_repo: StaffRepository, undo_service: UndoService):
        self._console = console
        self._expense_service = expense_service
        self._staff_repo = staff_repo
        self._undo_service = undo_service

    def show(self, active_staff_id: Optional[int] = None) -> None:
        sid = self._resolve_staff(active_staff_id)
        if sid is None:
            return

        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["All Expenses", "Filter by Category", "Filter by Date Range",
                 "View Recent (30 days)", "Search Expenses", "Edit Expense", "Delete Expense", "↩ Undo Last"],
                title="View Expenses",
            )
            if choice == "0":
                break
            if choice in ("1", "2", "3", "4", "5"):
                self._list_expenses(sid, choice)
            elif choice == "6":
                self._edit_expense(sid)
            elif choice == "7":
                self._delete_expense(sid)
            elif choice == "8":
                self._undo(sid)

    def _resolve_staff(self, active_staff_id):
        if active_staff_id and self._staff_repo.get_by_id(active_staff_id):
            return active_staff_id
        return self._prompt_staff()

    def _prompt_staff(self):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Staff Selection[/bold cyan]", border_style="cyan"))
        staff_list = self._staff_repo.get_all()
        if not staff_list:
            return None
        for s in staff_list:
            console.print(f"  [yellow]{s.id}.[/yellow] {s.name}")
        sid = IntPrompt.ask("-  Select staff ID", default=1)
        return sid if self._staff_repo.get_by_id(sid) else None

    def _list_expenses(self, sid: int, choice: str):
        cats = ["Food & Dining", "Transportation", "Housing & Utilities",
                "Entertainment", "Healthcare", "Shopping", "Education", "Other"]
        category_filter = None
        start_date = None
        end_date = None
        search = None

        if choice == "2":
            console.clear()
            console.print("[bold yellow]Select Category:[/bold yellow]")
            for i, cat in enumerate(cats, 1):
                console.print(f"  [cyan]{i}.[/cyan] {cat}")
            cat_choice = IntPrompt.ask("-  Category", choices=[str(i) for i in range(1, len(cats) + 1)])
            category_filter = cats[cat_choice - 1]
        elif choice == "3":
            start_date = Prompt.ask("-  Start date (YYYY-MM-DD)")
            end_date = Prompt.ask("-  End date (YYYY-MM-DD)")
        elif choice == "4":
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
        elif choice == "5":
            search = Prompt.ask("-  Search (description, category, or amount)")

        sort_by = Prompt.ask("-  Sort",
                             choices=["date_desc", "date_asc", "amount_desc", "amount_asc", "category_asc"],
                             default="date_desc")

        expenses = self._expense_service.get_expenses(
            staff_id=sid, category=category_filter, start_date=start_date,
            end_date=end_date, search=search, sort_by=sort_by,
        )

        console.clear()
        show_logo()

        if expenses:
            total = sum(e.amount for e in expenses)
            stats = Text()
            stats.append(f"Total: ${total:.2f}  │  ", style="bold green")
            stats.append(f"Transactions: {len(expenses)}", style="bold cyan")
            console.print(Panel(stats, border_style="green"))

            table = Table(box=box.ROUNDED, border_style="blue", show_lines=True)
            table.add_column("ID", style="dim", width=4)
            table.add_column("Date", style="cyan")
            table.add_column("Category", style="yellow")
            table.add_column("Amount", style="bold green", justify="right")
            table.add_column("Description", style="white")
            for e in expenses:
                table.add_row(str(e.id), e.expense_date, e.category,
                              f"${e.amount:.2f}", e.description or "-")
            console.print(table)
        else:
            console.print("[yellow]No expenses found matching the criteria.[/yellow]")

        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _edit_expense(self, sid: int):
        eid = IntPrompt.ask("-  Enter expense ID to edit")
        exp = self._expense_service.get_expense(eid)
        if not exp or exp.staff_id != sid:
            console.print("[red]Expense not found.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return

        old = {"amount": exp.amount, "category": exp.category,
               "description": exp.description, "expense_date": exp.expense_date}

        console.clear()
        show_logo()
        console.print(Panel(f"[bold cyan]Editing Expense #{eid}[/bold cyan]", border_style="cyan"))
        console.print(f"Current: ${exp.amount:.2f} | {exp.category} | {exp.description} | {exp.expense_date}")

        amount = FloatPrompt.ask("-  New amount ($)", default=exp.amount)
        category = Prompt.ask("-  New category", default=exp.category)
        description = Prompt.ask("-  New description", default=exp.description)
        expense_date = Prompt.ask("-  New date (YYYY-MM-DD)", default=exp.expense_date)

        if Confirm.ask("\n[bold green]-  Save changes?[/bold green]", default=True):
            self._expense_service.update(eid, amount=amount, category=category,
                                          description=description, expense_date=expense_date)
            self._undo_service.log_update(sid, "expense", eid, old,
                                          {"amount": amount, "category": category,
                                           "description": description, "expense_date": expense_date})
            console.print("[green]Expense updated.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _delete_expense(self, sid: int):
        eid = IntPrompt.ask("-  Enter expense ID to delete")
        exp = self._expense_service.get_expense(eid)
        if not exp or exp.staff_id != sid:
            console.print("[red]Expense not found.[/red]")
            return

        console.print(f"[yellow]Expense: ${exp.amount:.2f} | {exp.category} | {exp.description}[/yellow]")
        if Confirm.ask("[red]Delete this expense?[/red]"):
            self._undo_service.log_delete(sid, "expense", eid,
                                           {"amount": exp.amount, "category": exp.category,
                                            "description": exp.description, "expense_date": exp.expense_date,
                                            "staff_id": sid})
            self._expense_service.delete(eid)
            console.print("[green]Expense deleted. Use Undo to restore.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _undo(self, sid: int):
        msg = self._undo_service.undo_last(sid)
        if msg:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print("[yellow]Nothing to undo.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
