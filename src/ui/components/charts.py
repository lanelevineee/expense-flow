from typing import List, Any

from src.ui.console import console


def render_bar_chart(
    items: List[Any],
    label_attr: str,
    value_attr: str,
    max_width: int = 25,
    label_width: int = 25,
):
    if not items:
        return

    max_val = max((getattr(i, value_attr, 0) or 0) for i in items)
    total = sum((getattr(i, value_attr, 0) or 0) for i in items)

    for item in items:
        val = getattr(item, value_attr, 0) or 0
        label = getattr(item, label_attr, "")
        bar_len = max(1, int((val / max_val) * max_width)) if max_val > 0 else 1
        bar = "█" * bar_len
        pct = (val / total * 100) if total > 0 else 0
        console.print(
            f"  [cyan]{str(label):{label_width}s}[/cyan] "
            f"[green]{bar}[/green] ${val:.2f} ({pct:.1f}%)"
        )
