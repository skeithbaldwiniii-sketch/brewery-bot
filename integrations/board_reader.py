import re
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


def parse_board(values):
    """
    Parse the entire brewery Board into structured sections.

    The Board contains:
        - weekday sections
        - next week sections
        - dated events
        - blank rows
        - occasional notes

    The original task text is preserved.
    """

    schedule = {
        day: []
        for day in DAYS
    }

    future = {
        "next week": [],
        "next next week": [],
        "next next next week": [],
    }

    dated_events = []

    current_section = None

    for raw_value in values:

        value = str(raw_value).strip()

        if not value:
            continue

        # Ignore empty task placeholders.
        if value.lower() in {
            "brewing:",
        }:
            continue

        normalized = value.lower().strip()

        # -------------------------------------------------
        # WEEKDAY
        # -------------------------------------------------

        if normalized in DAYS:

            current_section = normalized

            continue

        # -------------------------------------------------
        # FUTURE WEEK HEADERS
        # -------------------------------------------------

        if normalized.startswith(
            "next next next week"
        ):

            current_section = "next next next week"

            continue

        if normalized.startswith(
            "next next week"
        ):

            current_section = "next next week"

            continue

        if normalized == "next week":

            current_section = "next week"

            continue

        # -------------------------------------------------
        # DATED EVENTS
        # -------------------------------------------------

        dated_match = re.match(
            r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\s*-\s*(.+)$",
            value,
        )

        if dated_match:

            month = int(
                dated_match.group(1)
            )

            day = int(
                dated_match.group(2)
            )

            year = dated_match.group(3)

            description = dated_match.group(4).strip()

            dated_events.append(
                {
                    "month": month,
                    "day": day,
                    "year": (
                        int(year)
                        if year
                        else None
                    ),
                    "task": description,
                    "raw": value,
                }
            )

            continue

        # -------------------------------------------------
        # OTHER DATE / PERSON NOTES
        # -------------------------------------------------

        if re.match(
            r"^[A-Za-z].*\bout\b.*\d{1,2}/\d{1,2}",
            value,
            re.IGNORECASE,
        ):

            dated_events.append(
                {
                    "month": None,
                    "day": None,
                    "year": None,
                    "task": value,
                    "raw": value,
                }
            )

            continue

        # -------------------------------------------------
        # IGNORE STRAY VALUES BEFORE THE FIRST SECTION
        # -------------------------------------------------

        if current_section is None:
            continue

        # -------------------------------------------------
        # CURRENT WEEK
        # -------------------------------------------------

        if current_section in DAYS:

            schedule[current_section].append(
                value
            )

            continue

        # -------------------------------------------------
        # FUTURE WEEKS
        # -------------------------------------------------

        if current_section in future:

            future[current_section].append(
                value
            )

            continue

    return {
        "schedule": schedule,
        "future": future,
        "dated_events": dated_events,
    }


def build_schedule_from_board(values):
    """
    Return only the current weekly schedule.

    This is the format expected by the task
    knowledge database.
    """

    parsed = parse_board(values)

    return parsed["schedule"]


def get_future_schedule(values):
    """Return tasks under future-week sections."""

    parsed = parse_board(values)

    return parsed["future"]


def get_dated_events(values):
    """Return dated events and reminders."""

    parsed = parse_board(values)

    return parsed["dated_events"]


def print_board_summary(values):
    """Print a human-readable summary of the Board."""

    parsed = parse_board(values)

    print()
    print("🍺 BREWS SPRINGSTEEN — BOARD SUMMARY")
    print("=" * 50)

    print()
    print("CURRENT WEEK")
    print("-" * 50)

    for day in DAYS:

        tasks = parsed["schedule"][day]

        print()
        print(day.title())

        if not tasks:
            print("  (no tasks)")
            continue

        for task in tasks:
            print(f"  • {task}")

    print()
    print("FUTURE")
    print("-" * 50)

    for section, tasks in parsed["future"].items():

        if not tasks:
            continue

        print()
        print(section.title())

        for task in tasks:
            print(f"  • {task}")

    print()
    print("DATED EVENTS")
    print("-" * 50)

    if not parsed["dated_events"]:

        print("  (none)")

    else:

        for event in parsed["dated_events"]:

            print(
                f"  • {event['raw']}"
            )

    print()


if __name__ == "__main__":

    from integrations.google_sheets import (
        get_column_a,
    )

    values = get_column_a()

    print_board_summary(values)