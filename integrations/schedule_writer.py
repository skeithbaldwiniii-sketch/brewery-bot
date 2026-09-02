from integrations.google_sheets import connect_to_sheet, DAYS
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_sheets_service():
    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES,
    )

    return build(
        "sheets",
        "v4",
        credentials=credentials,
    )


def _find_day_section(worksheet, day_name):
    """
    Find the row containing the requested weekday and the row
    containing the next weekday.
    """

    day_name = day_name.lower().strip()

    values = worksheet.col_values(1)

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
        raise RuntimeError(
            f"Could not find '{day_name}' on the Board."
        )

    return day_row, next_day_row


def _copy_row_format(worksheet, source_row, destination_row):
    """
    Copy formatting from one row to another without copying its values.
    Rows are 1-based here; Google Sheets API uses 0-based indexes.
    """

    service = _get_sheets_service()

    spreadsheet_id = worksheet.spreadsheet.id

    request = {
        "requests": [
            {
                "copyPaste": {
                    "source": {
                        "sheetId": worksheet.id,
                        "startRowIndex": source_row - 1,
                        "endRowIndex": source_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "destination": {
                        "sheetId": worksheet.id,
                        "startRowIndex": destination_row - 1,
                        "endRowIndex": destination_row,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "pasteType": "PASTE_FORMAT",
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request,
    ).execute()


def add_task_to_day(task, day_name):
    """
    Add a task to the first available blank row within the day's
    existing Board section.

    Never inserts a row when a blank reserved row already exists.
    """

    if not task or not task.strip():
        raise ValueError("Task cannot be empty.")

    task = task.strip()
    day_name = day_name.lower().strip()

    if day_name not in DAYS:
        raise ValueError(f"Invalid day name: {day_name}")

    worksheet = connect_to_sheet()

    day_row, next_day_row = _find_day_section(
        worksheet,
        day_name,
    )

    # Read the actual visible rows in the worksheet rather than
    # relying on col_values(), which ignores trailing blank rows.
    #
    # worksheet.row_count gives us the actual grid size.
    #
    # For a normal day with another weekday after it, the next
    # weekday defines the end of the section.
    if next_day_row is not None:
        section_end = next_day_row - 1

    else:
        # Friday is currently the last scheduled weekday block.
        # Its Board section runs through row 75.
        #
        # This preserves the existing formatted area rather than
        # writing outside the Board.
        if day_name == "friday":
            section_end = 75
        else:
            section_end = worksheet.row_count

    # Find the first blank row after the day header.
    for row_number in range(day_row + 1, section_end + 1):
        value = worksheet.cell(row_number, 1).value

        if not value or not value.strip():
            worksheet.update_acell(
                f"A{row_number}",
                task,
            )

            return {
                "task": task,
                "day": day_name,
                "row": row_number,
            }

    # No available blank row.
    raise RuntimeError(
        f"No available blank rows remain in the {day_name.capitalize()} "
        f"schedule section (through row {section_end})."
    )

def remove_task_from_day(task, day_name):
    """
    Remove an exact task from a specific day's section.

    This is intentionally exact-match only so we don't accidentally
    delete a similarly named task.
    """

    if not task or not task.strip():
        raise ValueError("Task cannot be empty.")

    task = task.strip()
    day_name = day_name.lower().strip()

    if day_name not in DAYS:
        raise ValueError(
            f"Invalid day name: {day_name}"
        )

    worksheet = connect_to_sheet()

    day_row, next_day_row = _find_day_section(
        worksheet,
        day_name,
    )

    values = worksheet.col_values(1)

    section_end = (
        next_day_row - 1
        if next_day_row is not None
        else len(values)
    )

    for row_number in range(day_row + 1, section_end + 1):
        value = values[row_number - 1].strip()

        if value == task:
            worksheet.delete_rows(row_number)

            return {
                "task": task,
                "day": day_name,
                "row": row_number,
                "removed": True,
            }

    return {
        "task": task,
        "day": day_name,
        "row": None,
        "removed": False,
    }

def move_task_between_days(task, from_day, to_day):
    """
    Move an exact task from one day to another.

    The task is written into an existing blank row on the destination
    day, then removed from the source day.

    No spreadsheet rows are inserted.
    """

    if not task or not task.strip():
        raise ValueError("Task cannot be empty.")

    task = task.strip()
    from_day = from_day.lower().strip()
    to_day = to_day.lower().strip()

    if from_day not in DAYS:
        raise ValueError(f"Invalid source day: {from_day}")

    if to_day not in DAYS:
        raise ValueError(f"Invalid destination day: {to_day}")

    if from_day == to_day:
        raise ValueError(
            "Source and destination days cannot be the same."
        )

    worksheet = connect_to_sheet()

    # ------------------------------------------------------------
    # Find source task
    # ------------------------------------------------------------

    source_day_row, source_next_day_row = _find_day_section(
        worksheet,
        from_day,
    )

    values = worksheet.col_values(1)

    source_section_end = (
        source_next_day_row - 1
        if source_next_day_row is not None
        else (
            75
            if from_day == "friday"
            else worksheet.row_count
        )
    )

    source_row = None

    for row_number in range(
        source_day_row + 1,
        source_section_end + 1,
    ):
        value = worksheet.cell(row_number, 1).value

        if value and value.strip().lower() == task.lower():
            source_row = row_number
            break

    if source_row is None:
        raise RuntimeError(
            f'Could not find "{task}" on the '
            f"{from_day.capitalize()} schedule."
        )

    # ------------------------------------------------------------
    # Find destination section
    # ------------------------------------------------------------

    destination_day_row, destination_next_day_row = _find_day_section(
        worksheet,
        to_day,
    )

    destination_section_end = (
        destination_next_day_row - 1
        if destination_next_day_row is not None
        else (
            75
            if to_day == "friday"
            else worksheet.row_count
        )
    )

    destination_row = None

    for row_number in range(
        destination_day_row + 1,
        destination_section_end + 1,
    ):
        value = worksheet.cell(row_number, 1).value

        if not value or not value.strip():
            destination_row = row_number
            break

    if destination_row is None:
        raise RuntimeError(
            f"No available blank rows remain in the "
            f"{to_day.capitalize()} schedule section."
        )

    # ------------------------------------------------------------
    # Write destination first
    # ------------------------------------------------------------

    worksheet.update_acell(
        f"A{destination_row}",
        task,
    )

    # ------------------------------------------------------------
    # Remove source
    # ------------------------------------------------------------

    worksheet.update_acell(
        f"A{source_row}",
        "",
    )

    return {
        "task": task,
        "from_day": from_day,
        "to_day": to_day,
        "source_row": source_row,
        "destination_row": destination_row,
    }