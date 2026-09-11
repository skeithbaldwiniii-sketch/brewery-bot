from unittest.mock import MagicMock, patch

from integrations.schedule_writer import complete_task_on_day


def test_complete_task_on_day_applies_strikethrough():
    worksheet = MagicMock()
    worksheet.col_values.return_value = [
        "Monday",
        "Clean glycol lines",
        "Check pH",
        "Tuesday",
    ]
    worksheet.cell.side_effect = [
        MagicMock(value="Clean glycol lines"),
    ]
    worksheet.id = 123
    worksheet.spreadsheet.id = "spreadsheet-123"

    service = MagicMock()

    with (
        patch(
            "integrations.schedule_writer.connect_to_sheet",
            return_value=worksheet,
        ),
        patch(
            "integrations.schedule_writer._get_sheets_service",
            return_value=service,
        ),
    ):
        result = complete_task_on_day(
            "Clean glycol lines",
            "Monday",
        )

    assert result == {
        "task": "Clean glycol lines",
        "day": "monday",
        "row": 2,
        "completed": True,
    }

    service.spreadsheets().batchUpdate.assert_called_once()

    call_kwargs = service.spreadsheets().batchUpdate.call_args.kwargs

    assert call_kwargs["spreadsheetId"] == "spreadsheet-123"

    request = call_kwargs["body"]["requests"][0]["repeatCell"]

    assert request["range"]["sheetId"] == 123
    assert request["range"]["startRowIndex"] == 1
    assert request["range"]["endRowIndex"] == 2
    assert request["range"]["startColumnIndex"] == 0
    assert request["range"]["endColumnIndex"] == 1

    assert (
        request["cell"]["userEnteredFormat"]["textFormat"]["strikethrough"]
        is True
    )


def test_complete_task_on_day_returns_false_when_task_not_found():
    worksheet = MagicMock()
    worksheet.col_values.return_value = [
        "Monday",
        "Check pH",
        "Tuesday",
    ]
    worksheet.cell.side_effect = [
        MagicMock(value="Check pH"),
    ]

    service = MagicMock()

    with (
        patch(
            "integrations.schedule_writer.connect_to_sheet",
            return_value=worksheet,
        ),
        patch(
            "integrations.schedule_writer._get_sheets_service",
            return_value=service,
        ),
    ):
        result = complete_task_on_day(
            "Clean glycol lines",
            "Monday",
        )

    assert result == {
        "task": "Clean glycol lines",
        "day": "monday",
        "row": None,
        "completed": False,
    }

    service.spreadsheets().batchUpdate.assert_not_called()
