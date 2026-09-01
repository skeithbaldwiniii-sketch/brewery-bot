from datetime import datetime


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def get_today_name():
    """Return today's weekday name."""

    return datetime.now().strftime("%A").lower()


def get_tasks_for_day(column_values, day_name=None):
    """
    Extract tasks belonging to a specific weekday.

    Tasks begin after the matching weekday header and
    continue until the next weekday header.
    """

    if day_name is None:
        day_name = get_today_name()

    day_name = day_name.lower()

    if day_name not in DAYS:
        raise ValueError(f"Invalid day name: {day_name}")

    collecting = False
    tasks = []

    for value in column_values:
        value = value.strip()

        if not value:
            continue

        normalized = value.lower()

        if normalized == day_name:
            collecting = True
            continue

        if collecting and normalized in DAYS:
            break

        if collecting:
            tasks.append(value)

    return tasks


def get_schedule_tasks(day_name):
    """
    Return all tasks scheduled for a specific weekday,
    including completion status.
    """

    from integrations.google_sheets import get_schedule_for_day

    return get_schedule_for_day(day_name)


def get_remaining_tasks(day_name=None):
    """
    Return only unfinished tasks for a specific weekday.
    Defaults to today.
    """

    if day_name is None:
        day_name = get_today_name()

    tasks = get_schedule_tasks(day_name)

    return [
        task["task"]
        for task in tasks
        if not task["completed"]
    ]