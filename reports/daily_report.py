from datetime import datetime


def build_daily_report(tasks):
    """Build a formatted daily brewery task report."""

    today = datetime.now().strftime("%A, %B %d, %Y")

    lines = [
        "🍺 VANISH CELLAR — DAILY REPORT",
        today,
        "",
        "TODAY'S TASKS",
        "─────────────",
    ]

    for task in tasks:
        lines.append(f"• {task}")

    return "\n".join(lines)