from rich.text import Text

from src.ui.console import console

LOGO = (
    "\n"
    "╔══════════════════════════════════════════════════════════════╗\n"
    "║                                                              ║\n"
    "║   ╔═╗╔═╗╦ ╦╔═╗╦  ╦╔═╗  ╔═╗╔═╗╔╦╗╦═╗╦╔╗ ╦╔═╗╔═╗╔╦╗       ║\n"
    "║   ║ ║║  ╠═╣╠═╣║  ║╚═╗  ║  ║ ║║║║╠╦╝║╠╩╗║║╣ ║   ║        ║\n"
    "║   ╚═╝╚═╝╩ ╩╩ ╩╩═╝╩╚═╝  ╚═╝╚═╝╩ ╩╩╚═╩╚═╝╩╚═╝╚═╝ ╩        ║\n"
    "║                                                              ║\n"
    "║              Smart Expense Tracker for Staff                 ║\n"
    "║                   Seamless Technologies                      ║\n"
    "║                                                              ║\n"
    "╚══════════════════════════════════════════════════════════════╝"
)


def show_logo():
    console.print(Text(LOGO), style="bold cyan")
