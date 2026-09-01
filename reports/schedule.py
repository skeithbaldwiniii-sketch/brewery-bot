from reports.daily_tasks import (
    DAYS,
    get_today_name,
    get_schedule_tasks,
    get_remaining_tasks,
)


def format_schedule(day_name):
    """Format the full schedule for a weekday."""

    day_name = day_name.lower()

    if day_name not in DAYS:
        raise ValueError(f"Invalid day: {day_name}")

    tasks = get_schedule_tasks(day_name)

    if not tasks:
        return f"There are no tasks listed for {day_name.title()}."

    lines = [
        f"SCHEDULE FOR {day_name.upper()}",
        "------------------------",
    ]

    for task in tasks:
        status = "[x]" if task["completed"] else "-"
        lines.append(f"{status} {task['task']}")

    return "\n".join(lines)


def format_remaining_tasks():
    """Format unfinished tasks for today."""

    today = get_today_name()

    tasks = get_remaining_tasks(today)

    if not tasks:
        return (
            f"Nothing left on the {today.title()} list!"
        )

    lines = [
        f"REMAINING TASKS - {today.upper()}",
        "------------------------",
    ]

    for task in tasks:
        lines.append(f"- {task}")

    return "\n".join(lines)


def format_task_days(search_term):
    """
    Format the results of a task-to-day search.
    """

    matches = find_task_days(search_term)

    if not matches:
        return (
            f"I couldn't find anything matching "
            f"'{search_term}'."
        )

    lines = [
        f"SCHEDULE FOR: {search_term.title()}",
        "------------------------",
    ]

    for match in matches:
        status = "[x]" if match["completed"] else "-"

        lines.append(
            f"{match['day'].title()}: "
            f"{status} {match['task']}"
        )

    return "\n".join(lines)

def find_task_days(search_term):
    """
    Search the entire weekly schedule for tasks containing
    the requested term.

    Returns a list of matching days and tasks.
    """

    search_term = search_term.strip().lower()

    if not search_term:
        return []

    matches = []

    for day in DAYS:
        tasks = get_schedule_tasks(day)

        for task in tasks:
            task_text = task["task"]

            if search_term in task_text.lower():
                matches.append(
                    {
                        "day": day,
                        "task": task_text,
                        "completed": task["completed"],
                    }
                )

    return matches


