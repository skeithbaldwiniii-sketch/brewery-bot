from datetime import datetime

from integrations.google_sheets import get_schedule_for_day


def build_eod_report(day_name=None):
    """
    Build an end-of-day report from the current Google Sheet.

    Completed tasks are determined by strikethrough formatting.
    Uncompleted tasks are listed as needing rescheduling.
    """

    if day_name is None:
        day_name = datetime.now().strftime("%A").lower()

    tasks = get_schedule_for_day(day_name)

    completed = [
        task["task"]
        for task in tasks
        if task["completed"]
    ]

    remaining = [
        task["task"]
        for task in tasks
        if not task["completed"]
    ]

    lines = [
        f"END OF DAY - {day_name.upper()}",
        "------------------------",
        "",
        "COMPLETED",
    ]

    if completed:
        for task in completed:
            lines.append(f"- {task}")
    else:
        lines.append("- None")

    lines.extend([
        "",
        "NEEDS RESCHEDULING",
    ])

    if remaining:
        for task in remaining:
            lines.append(f"- {task}")
    else:
        lines.append("- None")

    lines.extend([
        "",
        f"SUMMARY: {len(completed)} completed / "
        f"{len(remaining)} remaining",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(build_eod_report())
