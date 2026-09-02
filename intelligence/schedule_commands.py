import re

from integrations.google_sheets import connect_to_sheet, DAYS
from integrations.schedule_writer import (
    add_task_to_day,
    move_task_between_days,
)


DAY_PATTERN = r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"


# Pending confirmations are kept in memory.
# Key = Slack user ID
# Value = {"task": ..., "day": ...}
pending_schedule_actions = {}


def parse_schedule_add_request(question):
    """
    Parse requests such as:

        add canning Hacienda for Thursday
        add canning Hacienda to Thursday
        put canning Hacienda on Thursday
        schedule canning Hacienda for Thursday

    Returns:
        {"task": "...", "day": "..."}
    or:
        None
    """

    text = question.strip()

    patterns = [
        rf"\badd\s+(.+?)\s+(?:for|to|on)\s+{DAY_PATTERN}\b",
        rf"\bput\s+(.+?)\s+(?:for|to|on)\s+{DAY_PATTERN}\b",
        rf"\bschedule\s+(.+?)\s+(?:for|to|on)\s+{DAY_PATTERN}\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            task = match.group(1).strip()
            day = match.group(2).lower().strip()

            if task:
                return {
                    "task": task,
                    "day": day,
                }

    return None

def parse_schedule_move_request(question):
    """
    Parse requests such as:

        move canning Hacienda from Thursday to Friday
        move canning Hacienda from thursday into friday
        move canning Hacienda Thursday to Friday

    Returns:
        {
            "task": "...",
            "from_day": "...",
            "to_day": "..."
        }

    or None.
    """

    text = question.strip()

    pattern = (
        rf"\bmove\s+(.+?)\s+"
        rf"(?:from\s+)?{DAY_PATTERN}\s+"
        rf"(?:to|into|for)\s+{DAY_PATTERN}\b"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    task = match.group(1).strip()
    from_day = match.group(2).lower().strip()
    to_day = match.group(3).lower().strip()

    if not task:
        return None

    if from_day == to_day:
        return None

    return {
        "task": task,
        "from_day": from_day,
        "to_day": to_day,
    }

def is_schedule_move_request(question):
    return parse_schedule_move_request(question) is not None

def request_schedule_move_confirmation(user_id, question):
    """
    Create a pending move action and return a confirmation message.
    """

    parsed = parse_schedule_move_request(question)

    if not parsed:
        return None

    task = parsed["task"]
    from_day = parsed["from_day"]
    to_day = parsed["to_day"]

    pending_schedule_actions[user_id] = {
        "action": "move",
        "task": task,
        "from_day": from_day,
        "to_day": to_day,
    }

    return (
        f'I can move "{task}" from '
        f'{from_day.capitalize()} to {to_day.capitalize()}. '
        f"Proceed? (yes/no)"
    )

def is_schedule_add_request(question):
    return parse_schedule_add_request(question) is not None


def _get_day_tasks(day_name):
    """
    Read the tasks currently listed for a specific day.
    """

    worksheet = connect_to_sheet()
    values = worksheet.col_values(1)

    day_name = day_name.lower().strip()

    day_row = None
    next_day_row = None

    for index, value in enumerate(values, start=1):
        normalized = value.strip().lower()

        if normalized == day_name:
            day_row = index

            for next_index in range(index + 1, len(values) + 1):
                next_value = values[next_index - 1].strip().lower()

                if next_value in DAYS:
                    next_day_row = next_index
                    break

            break

    if day_row is None:
        return []

    section_end = (
        next_day_row - 1
        if next_day_row is not None
        else len(values)
    )

    tasks = []

    for row_number in range(day_row + 1, section_end + 1):
        value = values[row_number - 1].strip()

        if value:
            tasks.append(value)

    return tasks


def task_already_exists(task, day_name):
    """
    Check for an exact case-insensitive task match.
    """

    normalized_task = task.strip().lower()

    for existing_task in _get_day_tasks(day_name):
        if existing_task.strip().lower() == normalized_task:
            return True

    return False


def request_schedule_confirmation(user_id, question):
    """
    Create a pending schedule action and return the confirmation message.
    """

    parsed = parse_schedule_add_request(question)

    if not parsed:
        return None

    task = parsed["task"]
    day = parsed["day"]

    if task_already_exists(task, day):
        return (
            f'"{task}" is already on the {day.capitalize()} schedule.'
        )

    pending_schedule_actions[user_id] = {
        "task": task,
        "day": day,
    }

    return (
        f'I can add "{task}" to the {day.capitalize()} schedule. '
        f"Proceed? (yes/no)"
    )


def confirm_schedule_action(user_id):
    """
    Execute a previously confirmed schedule action.
    """

    action = pending_schedule_actions.get(user_id)

    if not action:
        return None

    # ------------------------------------------------------------
    # MOVE
    # ------------------------------------------------------------

    if action.get("action") == "move":

        task = action["task"]
        from_day = action["from_day"]
        to_day = action["to_day"]

        try:
            result = move_task_between_days(
                task,
                from_day,
                to_day,
            )

        except Exception as exc:
            del pending_schedule_actions[user_id]

            return (
                f"I couldn't move "
                f'"{task}" from {from_day.capitalize()} '
                f"to {to_day.capitalize()}: {exc}"
            )

        del pending_schedule_actions[user_id]

        return (
            f'Moved "{result["task"]}" from '
            f'{result["from_day"].capitalize()} to '
            f'{result["to_day"].capitalize()}.'
        )

    # ------------------------------------------------------------
    # ADD
    # ------------------------------------------------------------

    task = action["task"]
    day = action["day"]

    if task_already_exists(task, day):
        del pending_schedule_actions[user_id]

        return (
            f'"{task}" is already on the '
            f"{day.capitalize()} schedule, "
            f"so I didn't add another copy."
        )

    result = add_task_to_day(
        task,
        day,
    )

    del pending_schedule_actions[user_id]

    return (
        f'Added "{result["task"]}" to the '
        f'{result["day"].capitalize()} schedule '
        f"(row {result['row']})."
    )


def cancel_schedule_action(user_id):
    """
    Cancel a pending schedule modification.
    """

    if user_id in pending_schedule_actions:
        del pending_schedule_actions[user_id]

        return "Okay — I didn't change the schedule."

    return None


def has_pending_schedule_action(user_id):
    return user_id in pending_schedule_actions


def handle_schedule_write_question(user_id, question):
    """
    Main entry point for Slack.

    Returns:
        Response string if this module handled the message.
        None if another part of Brews Springsteen should handle it.
    """

    text = question.strip()
    lowered = text.lower()

    # Handle confirmation responses first.
    if has_pending_schedule_action(user_id):

        if lowered in {
            "yes",
            "y",
            "yeah",
            "yep",
            "yes please",
            "do it",
            "go ahead",
            "proceed",
        }:
            return confirm_schedule_action(user_id)

        if lowered in {
            "no",
            "n",
            "nope",
            "cancel",
            "never mind",
            "nevermind",
        }:
            return cancel_schedule_action(user_id)

        return (
            "I have a schedule change waiting for confirmation. "
            "Reply **yes** to make the change or **no** to cancel."
        )

    # No pending action: check for MOVE first.
    if is_schedule_move_request(text):
        return request_schedule_move_confirmation(
            user_id,
            text,
        )

    # Then check for ADD.
    if is_schedule_add_request(text):
        return request_schedule_confirmation(
            user_id,
            text,
        )

    # No pending action: only handle actual add requests.
    if is_schedule_add_request(text):
        return request_schedule_confirmation(
            user_id,
            text,
        )

    return None