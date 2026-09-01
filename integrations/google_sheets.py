import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from reports.daily_tasks import get_tasks_for_day
from reports.daily_report import build_daily_report


SPREADSHEET_NAME = "Vanish Cellar Ops"
WORKSHEET_NAME = "the Board"


DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def connect_to_sheet():
    """Connect to the brewery operations worksheet."""

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes,
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(SPREADSHEET_NAME)

    for worksheet in spreadsheet.worksheets():
        if worksheet.title.strip() == WORKSHEET_NAME:
            return worksheet

    raise RuntimeError(
        f"Could not find worksheet '{WORKSHEET_NAME}'."
    )


def get_column_a():
    """Return all values from Column A."""

    worksheet = connect_to_sheet()

    return worksheet.col_values(1)


def get_schedule_for_day(day_name):
    """
    Return tasks for a specific weekday, including completion status.

    A task is completed when its Google Sheets cell has
    strikethrough formatting.
    """

    worksheet = connect_to_sheet()
    values = worksheet.col_values(1)

    day_name = day_name.lower()

    valid_days = set(DAYS)

    if day_name not in valid_days:
        raise ValueError(f"Invalid day name: {day_name}")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes,
    )

    service = build(
        "sheets",
        "v4",
        credentials=credentials,
    )

    spreadsheet_id = worksheet.spreadsheet.id

    result = (
        service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            ranges=[
                f"'{worksheet.title}'!A1:A{len(values)}"
            ],
            includeGridData=True,
            fields=(
                "sheets(data(rowData(values("
                "effectiveFormat(textFormat(strikethrough))"
                "))))"
            ),
        )
        .execute()
    )

    struck_rows = {}

    row_data = (
        result.get("sheets", [{}])[0]
        .get("data", [{}])[0]
        .get("rowData", [])
    )

    for row_number, row in enumerate(row_data, start=1):

        values_data = row.get("values", [])

        if not values_data:
            continue

        cell = values_data[0]

        effective_format = cell.get(
            "effectiveFormat",
            {},
        )

        text_format = effective_format.get(
            "textFormat",
            {},
        )

        struck_rows[row_number] = text_format.get(
            "strikethrough",
            False,
        )

    collecting = False
    tasks = []

    for row_number, value in enumerate(values, start=1):

        value = value.strip()

        if not value:
            continue

        normalized = value.lower()

        if normalized == day_name:
            collecting = True
            continue

        if collecting and normalized in valid_days:
            break

        if collecting:
            tasks.append(
                {
                    "task": value,
                    "completed": struck_rows.get(
                        row_number,
                        False,
                    ),
                }
            )

    return tasks


def get_full_schedule():
    """
    Return the complete weekly schedule.

    Returns:

        {
            "monday": [
                {
                    "task": "...",
                    "completed": False
                }
            ],
            "tuesday": [...],
            ...
        }

    The schedule comes directly from Google Sheets.
    """

    schedule = {}

    for day in DAYS:
        schedule[day] = get_schedule_for_day(day)

    return schedule


def learn_current_schedule():
    """
    Read the entire brewery Board and learn the current
    weekly schedule.

    The Board reader is now the authoritative parser for
    schedule structure.
    """

    from integrations.board_reader import (
        build_schedule_from_board,
    )
    from knowledge.task_knowledge import (
        learn_task,
    )

    values = get_column_a()

    schedule = build_schedule_from_board(values)

    learned = 0

    for day, tasks in schedule.items():

        for task in tasks:

            learn_task(
                task,
                day,
                False,
            )

            learned += 1

    return learned

def get_remaining_tasks(day_name):
    """Return only unfinished tasks for a weekday."""

    tasks = get_schedule_for_day(day_name)

    return [
        task["task"]
        for task in tasks
        if not task["completed"]
    ]


if __name__ == "__main__":

    values = get_column_a()

    tasks = get_tasks_for_day(values)

    report = build_daily_report(tasks)

    print()
    print(report)