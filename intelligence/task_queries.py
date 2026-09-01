from datetime import datetime, timedelta
import re

from integrations.google_sheets import (
    get_schedule_for_day,
    learn_current_schedule,
)
from knowledge.task_knowledge import (
    find_tasks,
    find_tasks_by_component,
)


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


# Common brewery task actions.
#
# These are not a dictionary of brewery tasks.
# They are generic English actions that help interpret
# questions about tasks.
TASK_ACTIONS = {
    "transfer": [
        "transfer",
        "transferring",
        "transferred",
    ],
    "brew": [
        "brew",
        "brewing",
        "brewed",
    ],
    "keg": [
        "keg",
        "kegging",
        "kegged",
    ],
    "release": [
        "release",
        "releasing",
        "released",
    ],
    "clean": [
        "clean",
        "cleaning",
        "cleaned",
    ],
    "wash": [
        "wash",
        "washing",
        "washed",
    ],
    "sanitize": [
        "sanitize",
        "sanitizing",
        "sanitized",
        "sani",
    ],
    "cip": [
        "cip",
    ],
    "pull": [
        "pull",
        "pulling",
        "pulled",
    ],
    "make": [
        "make",
        "making",
        "made",
    ],
    "can": [
        "can",
        "canning",
        "canned",
    ],
    "ferry": [
        "ferry",
    ],
    "stack": [
        "stack",
        "stacking",
        "stacked",
    ],
    "flip": [
        "flip",
        "flipping",
        "flipped",
    ],
    "mix": [
        "mix",
        "mixing",
        "mixed",
    ],
    "carb": [
        "carb",
        "carbing",
        "carbonating",
    ],
}


def get_today_name():
    """Return today's weekday name."""

    return datetime.now().strftime("%A").lower()


def get_remaining_tasks_for_today():
    """Return unfinished tasks for today."""

    today = get_today_name()

    tasks = get_schedule_for_day(today)

    return [
        task["task"]
        for task in tasks
        if not task["completed"]
    ]


def format_remaining_tasks():
    """Format unfinished tasks for Slack."""

    today = get_today_name()

    tasks = get_remaining_tasks_for_today()

    lines = [
        f"REMAINING TASKS - {today.upper()}",
        "------------------------",
    ]

    if not tasks:
        lines.append(
            "Everything on today's list is complete. "
        )

    else:
        for task in tasks:
            lines.append(f"- {task}")

    return "\n".join(lines)


def get_schedule(day_name):
    """Return all tasks for a specific day."""

    tasks = get_schedule_for_day(day_name)

    return [
        task["task"]
        for task in tasks
    ]


def format_schedule(day_name):
    """Format a day's schedule."""

    day_name = day_name.lower()

    tasks = get_schedule(day_name)

    lines = [
        f"SCHEDULE FOR {day_name.upper()}",
        "------------------------",
    ]

    if not tasks:
        lines.append("No tasks found.")

    else:
        for task in tasks:
            lines.append(f"- {task}")

    return "\n".join(lines)


def find_task_days(search_term):
    """
    Find which days contain tasks matching a search term.
    """

    results = find_tasks(search_term)

    if not results:
        return []

    matches = []

    for result in results:

        task = result["task"]

        for day in result["days"]:

            matches.append(
                {
                    "day": day,
                    "task": task,
                }
            )

    # Remove duplicates.
    unique_matches = []

    seen = set()

    for match in matches:

        key = (
            match["day"],
            match["task"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_matches.append(match)

    return unique_matches


def format_task_days(search_term):
    """
    Answer questions such as:

        When is Festbier?
        What day are we doing Festbier?
        What days have Festbier on the schedule?
    """

    matches = find_task_days(search_term)

    lines = [
        f"SCHEDULE FOR: {search_term.title()}",
        "------------------------",
    ]

    if not matches:

        lines.append(
            f"I couldn't find '{search_term}' "
            "on the learned schedule."
        )

        return "\n".join(lines)

    for match in matches:

        lines.append(
            f"{match['day'].title()}: "
            f"- {match['task']}"
        )

    return "\n".join(lines)


def extract_day(question):
    """
    Find an explicit weekday in a question.
    """

    question = question.lower()

    for day in DAYS:

        if day in question:
            return day

    if "tomorrow" in question:

        tomorrow = datetime.now() + timedelta(days=1)

        return tomorrow.strftime("%A").lower()

    if "today" in question:

        return get_today_name()

    return None


def extract_action(question):
    """
    Try to identify the action being asked about.

    Example:

        "When are we transferring Festbier?"

    returns:

        "transfer"
    """

    normalized = question.lower()

    for action, variations in TASK_ACTIONS.items():

        for variation in variations:

            if re.search(
                rf"\b{re.escape(variation)}\b",
                normalized,
            ):
                return action

    return None


def extract_task_search_term(question):
    """
    Extract the subject of a task or event question.

    Examples:

        When are we transferring Festbier?
        -> festbier

        When is Max's Taphouse event?
        -> max's taphouse event

        "When is Max's Taphouse event?"
        -> max's taphouse event

        When is the Max's Taphouse event?
        -> max's taphouse event
    """

    question = str(question).lower().strip()

    # Remove quotation marks surrounding the entire question.
    # Handles straight and curly quotation marks.
    question = question.strip(
        "\"'“”‘’"
    )

    # Remove common punctuation while preserving apostrophes
    # inside names such as "max's".
    question = re.sub(
        r"[?!.,;:]",
        " ",
        question,
    )

    phrases_to_remove = [
        "what day are we",
        "what days are we",
        "what day is",
        "what days is",
        "what day",
        "what days",

        "when are we",
        "when is",
        "when do we",
        "when does",
        "when do",

        "what is the schedule for",
        "what's the schedule for",
        "what is on the schedule for",
        "what's on the schedule for",

        "tell me when",
        "tell me about",

        "the schedule for",
        "schedule for",
        "on the schedule",

        "this week's",
        "this week",

        "what are we",
        "what do we",
    ]

    for phrase in phrases_to_remove:
        question = question.replace(
            phrase,
            " ",
        )

    # Remove recognized operational actions.
    for variations in TASK_ACTIONS.values():

        for variation in variations:

            question = re.sub(
                rf"\b{re.escape(variation)}\b",
                " ",
                question,
            )

    # Remove conversational filler.
    filler_words = {
        "doing",
        "handle",
        "handling",
        "working",
        "work",
        "on",
        "for",
        "the",
        "a",
        "an",
        "we",
        "are",
        "is",
        "do",
        "does",
        "when",
        "what",
        "day",
        "days",
        "please",
        "tell",
        "me",
    }

    words = question.split()

    words = [
        word.strip("\"'“”‘’")
        for word in words
    ]

    words = [
        word
        for word in words
        if word and word not in filler_words
    ]

    return " ".join(words).strip()
    


def find_action_subject_matches(
    action,
    subject,
):
    """
    Find learned tasks that contain both the requested
    action and subject.

    This currently uses the learned task text itself.

    The database does not need to know what every brewery
    task means.
    """

    results = find_tasks(subject)

    if not results:
        return []

    variations = TASK_ACTIONS.get(
        action,
        [action],
    )

    matches = []

    for result in results:

        task_text = result["task"].lower()

        action_found = any(
            re.search(
                rf"\b{re.escape(variation)}\b",
                task_text,
            )
            for variation in variations
        )

        if not action_found:
            continue

        for day in result["days"]:

            matches.append(
                {
                    "day": day,
                    "task": result["task"],
                }
            )

    # Remove duplicates.
    unique_matches = []

    seen = set()

    for match in matches:

        key = (
            match["day"],
            match["task"],
        )

        if key in seen:
            continue

        seen.add(key)
        unique_matches.append(match)

    return unique_matches

def answer_action_subject_question(action, subject):
    """
    Answer a question using learned task components.

    Example:

        action  = release
        subject = festbier

    searches the learned component relationships rather
    than relying only on raw keyword matching.
    """

    matches = find_tasks_by_component(
        subject=subject,
        action=action,
    )

    lines = [
        f"{action.upper()} - {subject.title()}",
        "------------------------",
    ]

    if matches:

        for match in matches:

            for day in match["days"]:

                lines.append(
                    f"{day.title()}: "
                    f"- {match['task']}"
                )

        return "\n".join(lines)

    # No exact action + subject relationship.
    lines.append(
        f"I couldn't find an explicit '{action}' "
        f"task for {subject.title()}."
    )

    # Give the user useful related information.
    related = find_tasks_by_component(
        subject=subject,
    )

    if related:

        lines.append("")
        lines.append(
            f"Related {subject.title()} tasks:"
        )

        for match in related:

            for day in match["days"]:

                lines.append(
                    f"- {day.title()}: "
                    f"{match['task']}"
                )

    return "\n".join(lines)

def format_action_subject(
    action,
    subject,
    matches,
):
    """
    Format an action + subject query.
    """

    lines = [
        f"{action.upper()} - {subject.title()}",
        "------------------------",
    ]

    if not matches:

        lines.append(
            f"I couldn't find a '{action}' task "
            f"for {subject.title()} on the learnedschedule."
        )

        related = find_task_days(subject)

        if related:

            lines.append("")
            lines.append(
                f"Related {subject.title()} tasks:"
            )

            for match in related:

                lines.append(
                    f"- {match['day'].title()}: "
                    f"{match['task']}"
                )

        return "\n".join(lines)

    for match in matches:

        lines.append(
            f"{match['day'].title()}: "
            f"- {match['task']}"
        )

    return "\n".join(lines)


def answer_task_question(question):
    """
    Interpret and answer brewery schedule questions.

    Handles:
        - remaining tasks
        - a day's schedule
        - future-week schedules
        - upcoming dated events
        - action + subject questions
        - subject-only questions

    Returns:
        String response, or None if the question does not appear
        to be a schedule/task question.
    """

    normalized = str(question).lower().strip()

    # Remove quotation marks surrounding the entire question.
    normalized = normalized.strip("\"'“”‘’").strip()

    # Make sure the task database has the current schedule available.
    try:
        learn_current_schedule()
    except Exception:
        # Existing learned knowledge can still be used if Google Sheets
        # is temporarily unavailable.
        pass

    # -------------------------------------------------
    # REMAINING TASKS
    # -------------------------------------------------

    remaining_phrases = [
        "what's left today",
        "what is left today",
        "what's left for today",
        "what is left for today",
        "what remains today",
        "what remains for today",
        "what haven't we finished",
        "what have we not finished",
        "what is unfinished",
        "what's unfinished",
        "what do i still need to do",
        "what do we still need to do",
        "what's remaining today",
        "what is remaining today",
    ]

    if any(phrase in normalized for phrase in remaining_phrases):
        return format_remaining_tasks()

    # -------------------------------------------------
    # FUTURE WEEK SCHEDULE
    # -------------------------------------------------

    future_section = extract_future_section(question)

    if future_section:
        future_schedule_phrases = [
            "what is on the schedule",
            "what's on the schedule",
            "what is scheduled",
            "what's scheduled",
            "what do we have",
            "what are we doing",
            "what is planned",
            "what's planned",
        ]

        if any(
            phrase in normalized
            for phrase in future_schedule_phrases
        ):
            return format_future_schedule(future_section)

    # -------------------------------------------------
    # GENERAL UPCOMING SCHEDULE
    # -------------------------------------------------

    upcoming_phrases = [
        "what is coming up",
        "what's coming up",
        "what is coming",
        "what's coming",
        "what do we have coming up",
        "what do we have coming",
        "what is coming next",
        "what's coming next",
        "what is planned for next week",
        "what's planned for next week",
    ]

    if any(phrase in normalized for phrase in upcoming_phrases):
        return format_upcoming_schedule()

        # -------------------------------------------------
    # DATED EVENTS
    # -------------------------------------------------

    # First check whether the question matches a known
    # dated event. This allows questions such as:
    #
    #   When is Max's Taphouse?
    #   When is Max's Taphouse event?
    #   When is the Max's Taphouse event?
    #
    # without requiring the user to actually say "event".

    event_search_prefixes = [
        "when is",
        "when are",
        "what day is",
        "what day are",
        "what date is",
        "what date are",
    ]

    if any(
        phrase in normalized
        for phrase in event_search_prefixes
    ):
        event_search_term = extract_task_search_term(normalized)

        # Remove the generic word "event" if present.
        event_search_term = re.sub(
            r"\bevent\b",
            " ",
            event_search_term,
            flags=re.IGNORECASE,
        )

        # Remove surrounding quotation marks and punctuation.
        event_search_term = event_search_term.strip(
            " \"'“”‘’?!.,;:"
        )

        # Collapse multiple spaces.
        event_search_term = re.sub(
            r"\s+",
            " ",
            event_search_term,
        ).strip()

        if event_search_term:
            matches = find_dated_event(event_search_term)

            if matches:
                return format_dated_event_search(
                    event_search_term
                )

    # Explicit event-list questions.
    if "event" in normalized:
        event_list_phrases = [
            "what events are coming up",
            "what events are coming",
            "what events do we have",
            "what are the upcoming events",
            "what's coming up",
            "what is coming up",
        ]

        if any(
            phrase in normalized
            for phrase in event_list_phrases
        ):
            return format_dated_events()
        
    # -------------------------------------------------
    # DAY -> SCHEDULE
    # -------------------------------------------------

    day_name = extract_day(question)

    schedule_phrases = [
        "what is on the schedule",
        "what's on the schedule",
        "what is scheduled",
        "what's scheduled",
        "what are we doing",
        "what do we have",
        "schedule for",
    ]

    if (
        day_name
        and any(
            phrase in normalized
            for phrase in schedule_phrases
        )
    ):
        return format_schedule(day_name)

    # -------------------------------------------------
    # TASK -> DAY
    # -------------------------------------------------

    task_question_phrases = [
        "what day",
        "what days",
        "when is",
        "when are",
        "when do we",
        "when does",
    ]

    if not any(
        phrase in normalized
        for phrase in task_question_phrases
    ):
        return None

    # Extract the subject of the question.
    search_term = extract_task_search_term(question)

    # Event wording is not a learned task.
    # Search the Board's dated-event section directly.
    search_term = re.sub(
        r"\bevent\b",
        " ",
        search_term,
        flags=re.IGNORECASE,
    )

    search_term = search_term.strip(" \"'")


    if not search_term:
        return None

    # Try to identify an operational action.
    action = extract_action(question)

    # -------------------------------------------------
    # ACTION + SUBJECT
    # -------------------------------------------------

    if action:
        return answer_action_subject_question(
            action,
            search_term,
        )

    # -------------------------------------------------
    # SUBJECT ONLY
    # -------------------------------------------------

    return format_task_days(search_term)


# -------------------------------------------------
# FUTURE BOARD HELPERS
# -------------------------------------------------

def extract_future_section(question):
    """Identify a future-week section mentioned in a question."""

    normalized = question.lower()

    if "next next next week" in normalized:
        return "next next next week"

    if "next next week" in normalized:
        return "next next week"

    if "next week" in normalized:
        return "next week"

    return None


def _get_board_future_data():
    """
    Read future-week tasks and dated events directly from the Board.

    The Board remains the source of truth for future schedule information.
    """

    from integrations.google_sheets import get_column_a
    from integrations.board_reader import (
        get_future_schedule,
        get_dated_events,
    )

    values = get_column_a()

    return (
        get_future_schedule(values),
        get_dated_events(values),
    )


def format_future_schedule(section):
    """Format tasks from one future-week Board section."""

    future, _ = _get_board_future_data()

    section = section.lower()
    tasks = future.get(section, [])

    lines = [
        f"{section.upper()}",
        "------------------------",
    ]

    if not tasks:
        lines.append("No tasks found.")
    else:
        for task in tasks:
            lines.append(f"- {task}")

    return "\n".join(lines)


def format_upcoming_schedule():
    """Format all populated future-week sections."""

    future, _ = _get_board_future_data()

    lines = [
        "UPCOMING SCHEDULE",
        "------------------------",
    ]

    found = False

    for section in (
        "next week",
        "next next week",
        "next next next week",
    ):
        tasks = future.get(section, [])

        if not tasks:
            continue

        found = True

        lines.append("")
        lines.append(section.title())

        for task in tasks:
            lines.append(f"- {task}")

    if not found:
        lines.append("No future tasks found.")

    return "\n".join(lines)


def format_dated_events():
    """Format dated events and reminders from the Board."""

    _, events = _get_board_future_data()

    lines = [
        "UPCOMING EVENTS",
        "------------------------",
    ]

    if not events:
        lines.append("No dated events found.")
        return "\n".join(lines)

    for event in events:
        raw = event.get("raw", "").strip()

        if raw:
            lines.append(f"- {raw}")
        else:
            task = event.get("task", "").strip()

            if task:
                lines.append(f"- {task}")

    return "\n".join(lines)


def find_dated_event(search_term):
    """Find dated Board events matching a search term."""

    _, events = _get_board_future_data()

    search_term = search_term.lower().strip()

    if not search_term:
        return []

    matches = []

    for event in events:
        searchable = " ".join(
            [
                str(event.get("task", "")),
                str(event.get("raw", "")),
            ]
        ).lower()

        if search_term in searchable:
            matches.append(event)

    return matches


def format_dated_event_search(search_term):
    """Format dated events matching a search term."""

    matches = find_dated_event(search_term)

    lines = [
        f"EVENT SEARCH: {search_term.title()}",
        "------------------------",
    ]

    if not matches:
        lines.append(
            f"I couldn't find an upcoming dated event "
            f"matching '{search_term}'."
        )
        return "\n".join(lines)

    for event in matches:
        raw = event.get("raw", "").strip()

        if raw:
            lines.append(f"- {raw}")
        else:
            task = event.get("task", "").strip()

            if task:
                lines.append(f"- {task}")

    return "\n".join(lines)
