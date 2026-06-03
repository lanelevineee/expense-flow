import io
import os
import sys
import tty
import termios
import select
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich import box

from src.ui.console import console


_key_buffer: str = ""


def _get_key(timeout: Optional[float] = None) -> str:
    global _key_buffer

    if _key_buffer:
        result = _key_buffer
        _key_buffer = ""
        return result

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if not r:
            return ""
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = ch
            ch2 = sys.stdin.read(1)
            seq += ch2
            if ch2 in ("[", "O"):
                ch3 = sys.stdin.read(1)
                seq += ch3
            return seq
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _render_table(
    options: List[str],
    title: str,
    cursor: int,
    shortcuts: Optional[Dict[int, str]],
    return_option: bool,
) -> tuple:
    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style="cyan",
        title_justify="left",
        padding=(0, 1),
    )
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Option", style="white")

    for i, opt in enumerate(options, 1):
        hl = (i - 1) == cursor
        num_style = "reverse bold yellow" if hl else "bold yellow"
        opt_style = "reverse white" if hl else "white"

        label = opt
        if shortcuts and i in shortcuts:
            key_letter = shortcuts[i]
            upper_label = label.upper()
            upper_key = key_letter.upper()
            if upper_key in upper_label:
                idx = upper_label.index(upper_key)
                label = (
                    label[:idx]
                    + f"[bold cyan]{label[idx]}[/bold cyan]"
                    + label[idx + 1:]
                )
            else:
                label += f"  [dim]({key_letter})[/dim]"

        table.add_row(f"[{num_style}]{i}[/]", f"[{opt_style}]{label}[/]")

    if return_option:
        table.add_row("0", "↩  Back")

    return table


class _NullFile:
    def write(self, s):
        return len(s)

    def flush(self):
        pass


def _measure_lines(table: Table) -> int:
    buf = io.StringIO()
    c = Console(file=buf, force_terminal=True, width=80, no_color=True)
    c.print(table)
    return buf.getvalue().count("\n")


def _term_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def _print_table(table: Table) -> int:
    buf = io.StringIO()
    c = Console(file=buf, force_terminal=True, width=_term_width(), no_color=True)
    c.print(table)
    text = buf.getvalue()
    sys.stdout.write(text)
    sys.stdout.flush()
    return text.count("\n")


def _move_up(n: int):
    if n > 0:
        sys.stdout.write(f"\033[{n}A")
        sys.stdout.flush()


def show_menu(
    options: List[str],
    title: str = "Menu",
    return_option: bool = True,
    shortcuts: Optional[Dict[int, str]] = None,
) -> str:
    global _key_buffer

    cursor = 0
    valid_nums = {str(i) for i in range(1, len(options) + 1)}
    if return_option:
        valid_nums.add("0")

    table = _render_table(options, title, cursor, shortcuts, return_option)
    line_count = _measure_lines(table)

    table = _render_table(options, title, cursor, shortcuts, return_option)
    prev_lines = _print_table(table)

    while True:
        key = _get_key()

        if key == "\r":
            return str(cursor + 1)
        elif key in ("\x1b[A", "\x1bOA"):
            cursor = max(0, cursor - 1)
        elif key in ("\x1b[B", "\x1bOB"):
            cursor = min(len(options) - 1, cursor + 1)
        elif key.isdigit():
            buf = key
            while True:
                nxt = _get_key(0.3)
                if not nxt:
                    break
                if nxt.isdigit():
                    buf += nxt
                else:
                    _key_buffer = nxt
                    break
            if buf in valid_nums:
                return buf
            cursor = max(0, min(len(options) - 1, int(buf) - 1))
        else:
            continue

        _move_up(prev_lines)
        table = _render_table(options, title, cursor, shortcuts, return_option)
        prev_lines = _print_table(table)
