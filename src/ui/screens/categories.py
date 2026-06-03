from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.console import Console

from src.services.category_service import CategoryService
from src.ui.screens.base import BaseScreen
from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu


class CategoriesScreen(BaseScreen):
    def __init__(self, console: Console, category_service: CategoryService):
        self._console = console
        self._category_service = category_service

    def show(self) -> None:
        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["View Categories", "Add Category", "Edit Category Budget", "Delete Category"],
                title="Categories"
            )
            if choice == "0":
                return
            if choice == "1":
                self._view_all()
            elif choice == "2":
                self._add()
            elif choice == "3":
                self._edit_budget()
            elif choice == "4":
                self._delete()

    def _view_all(self):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Categories[/bold cyan]", border_style="cyan"))
        cats = self._category_service.get_all()
        if cats:
            table = Table(box=box.ROUNDED, border_style="blue")
            table.add_column("ID", style="bold yellow")
            table.add_column("Icon", style="white")
            table.add_column("Name", style="bold white")
            table.add_column("Budget", style="green", justify="right")
            table.add_column("Default", style="dim")
            for c in cats:
                table.add_row(str(c.id), c.icon, c.name,
                              f"${c.budget:.2f}" if c.budget else "-",
                              "✓" if c.is_default else "")
            console.print(table)
        else:
            console.print("[yellow]No categories defined.[/yellow]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _add(self):
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Add Category[/bold cyan]", border_style="cyan"))
        name = Prompt.ask("-  Category name")
        if not name.strip():
            console.print("[red]Name required.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        icon = Prompt.ask("-  Icon (emoji)", default="other")
        color = Prompt.ask("-  Color", default="white")
        budget = FloatPrompt.ask("-  Monthly budget ($)", default=0)
        try:
            self._category_service.add(name, icon, color, budget)
            console.print(f"[green]Category '{name}' added.[/green]")
        except Exception as e:
            console.print(f"[red]{e}[/red]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _edit_budget(self):
        cats = self._category_service.get_all()
        if not cats:
            console.print("[yellow]No categories defined.[/yellow]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return
        for c in cats:
            console.print(f"  [yellow]{c.id}.[/yellow] {c.icon} {c.name} [dim](budget: ${c.budget:.2f})[/dim]")
        cid = IntPrompt.ask("-  Category ID")
        budget = FloatPrompt.ask("-  Monthly budget ($)", default=0)
        self._category_service.update(cid, budget=budget)
        console.print("[green]Budget updated.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

    def _delete(self):
        cats = self._category_service.get_all()
        if not cats:
            return
        for c in cats:
            tag = " [red](default - cannot delete)[/red]" if c.is_default else ""
            console.print(f"  [yellow]{c.id}.[/yellow] {c.name}{tag}")
        cid = IntPrompt.ask("-  Category ID to delete")
        cat = next((c for c in cats if c.id == cid), None)
        if cat and cat.is_default:
            console.print("[red]Cannot delete default categories.[/red]")
        elif Confirm.ask(f"[red]Delete '{cat.name}'?[/red]"):
            self._category_service.delete(cid)
            console.print("[green]Deleted.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
