from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from src.ui.console import console
from src.ui.components.logo import show_logo
from src.ui.components.menu import show_menu
from src.auth.password import PasswordManager
from src.auth.session import SessionManager
from src.db.repositories.staff import StaffRepository


class AuthScreen:
    def __init__(self, staff_repo: StaffRepository, config):
        self._staff_repo = staff_repo
        self._config = config
        self._session = SessionManager(config)

    def show(self) -> Optional[dict]:
        while True:
            console.clear()
            show_logo()
            choice = show_menu(
                ["Login", "Register", "Exit"],
                title="Authentication",
            )
            if choice == "1":
                result = self._login()
                if result:
                    return result
            elif choice == "2":
                result = self._register()
                if result:
                    return result
            elif choice == "0":
                return None

    def _login(self) -> Optional[dict]:
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Login[/bold cyan]", border_style="cyan"))

        email = Prompt.ask("-  Email")
        if not email:
            return None

        password = Prompt.ask("-  Password", password=True)
        if not password:
            return None

        staff = self._staff_repo.get_by_email(email)
        if not staff:
            console.print("[red]No account found with that email.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return None

        stored_hash = self._staff_repo.get_password_hash(staff.id)
        if stored_hash:
            if not PasswordManager.verify(password, stored_hash):
                console.print("[red]Invalid password.[/red]")
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
                return None
        else:
            if password != "admin":
                console.print("[red]Invalid password.[/red]")
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
                return None

        role = "admin" if staff.id == 1 else "staff"
        tokens = self._session.create_tokens(staff.id, role=role)

        console.print(f"[green]Welcome, {staff.name}![/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

        return {
            "staff_id": staff.id,
            "name": staff.name,
            "role": role,
            "token": tokens.access_token,
        }

    def _register(self) -> Optional[dict]:
        console.clear()
        show_logo()
        console.print(Panel("[bold cyan]Create Account[/bold cyan]", border_style="cyan"))

        name = Prompt.ask("-  Full name")
        if not name:
            return None

        dept = Prompt.ask("-  Department", default="")
        email = Prompt.ask("-  Email")
        if not email:
            return None

        existing = self._staff_repo.get_by_email(email)
        if existing:
            console.print("[red]An account with this email already exists.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return None

        while True:
            password = Prompt.ask("-  Password", password=True)
            if not password:
                return None
            confirm = Prompt.ask("-  Confirm password", password=True)
            if password != confirm:
                console.print("[red]Passwords do not match.[/red]")
                continue
            valid, errors = PasswordManager.validate_strength(password)
            if not valid:
                console.print(f"[red]Weak password: {', '.join(errors)}[/red]")
                continue
            break

        try:
            hashed = PasswordManager.hash_password(password)
            staff_id = self._staff_repo.add(name, dept, email)
            if staff_id:
                self._staff_repo.update(staff_id, password_hash=hashed)
        except Exception as e:
            console.print(f"[red]Registration failed: {e}[/red]")
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]")
            return None

        role = "admin" if staff_id == 1 else "staff"
        tokens = self._session.create_tokens(staff_id, role=role)

        console.print(f"[green]Account created! Welcome, {name}.[/green]")
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]")

        return {
            "staff_id": staff_id,
            "name": name,
            "role": role,
            "token": tokens.access_token,
        }
