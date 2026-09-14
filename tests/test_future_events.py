from unittest.mock import MagicMock, patch

import pytest

from integrations.schedule_writer import add_future_event
from intelligence.schedule_commands import (
    handle_future_event_beer_response,
    handle_future_event_request,
    parse_future_event_request,
    pending_future_events,
)


# -------------------------------------------------
# PARSER
# -------------------------------------------------


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        (
            "add a wedding to the brewers calendar for 5/23",
            {"event": "wedding", "date": "5/23"},
        ),
        (
            "add wedding to the future events for 6/14",
            {"event": "wedding", "date": "6/14"},
        ),
        (
            "schedule a brewery tour for 7/22",
            {"event": "brewery tour", "date": "7/22"},
        ),
        (
            "ADD an anniversary for 8/15/2026",
            {"event": "anniversary", "date": "8/15/2026"},
        ),
    ],
)
def test_parse_future_event_request(question, expected):
    assert parse_future_event_request(question) == expected


@pytest.mark.parametrize(
    "question",
    [
        "",
        "what beers are on tap?",
        "add wedding",
        "schedule brewery tour",
    ],
)
def test_parse_future_event_request_returns_none_for_invalid_requests(question):
    assert parse_future_event_request(question) is None


# -------------------------------------------------
# WRITER
# -------------------------------------------------


def test_add_future_event_appends_after_existing_events():
    worksheet = MagicMock()

    worksheet.col_values.return_value = [
        "Monday",
        "Brewing",
        "Tuesday",
        "Future Events",
        "",
        "",
        "10/28 - Brian Out",
        "11/21 - RR sneak peak release",
    ]

    with patch(
        "integrations.schedule_writer.connect_to_sheet",
        return_value=worksheet,
    ):
        result = add_future_event("12/5 - Holiday Party")

    assert result == {
        "event": "12/5 - Holiday Party",
        "row": 9,
    }

    worksheet.update_acell.assert_called_once_with(
        "A9",
        "12/5 - Holiday Party",
    )


def test_add_future_event_finds_future_events_case_insensitively():
    worksheet = MagicMock()

    worksheet.col_values.return_value = [
        "Monday",
        "future events",
        "",
        "10/28 - Brian Out",
    ]

    with patch(
        "integrations.schedule_writer.connect_to_sheet",
        return_value=worksheet,
    ):
        result = add_future_event("11/1 - Release")

    assert result["row"] == 5

    worksheet.update_acell.assert_called_once_with(
        "A5",
        "11/1 - Release",
    )


def test_add_future_event_raises_when_section_missing():
    worksheet = MagicMock()

    worksheet.col_values.return_value = [
        "Monday",
        "Tuesday",
        "Wednesday",
    ]

    with patch(
        "integrations.schedule_writer.connect_to_sheet",
        return_value=worksheet,
    ):
        with pytest.raises(
            RuntimeError,
            match="Could not find the 'Future Events' section",
        ):
            add_future_event("12/5 - Holiday Party")


def test_add_future_event_rejects_empty_event():
    with pytest.raises(
        ValueError,
        match="Future event cannot be empty",
    ):
        add_future_event("   ")


# -------------------------------------------------
# EVENT WORKFLOW
# -------------------------------------------------


def test_handle_future_event_request_creates_pending_event():
    user_id = "U123"
    pending_future_events.pop(user_id, None)

    with patch(
        "integrations.schedule_writer.add_future_event"
    ) as mock_add:
        response = handle_future_event_request(
            user_id,
            "add a wedding to the future events for 5/23",
        )

    mock_add.assert_called_once_with("5/23 - wedding")

    assert response == (
        'Added "wedding" to Future Events for 5/23. '
        "What beers would you like for this event?"
    )

    assert pending_future_events[user_id] == {
        "event": "wedding",
        "date": "5/23",
    }

    pending_future_events.pop(user_id, None)


def test_handle_future_event_request_returns_error_when_write_fails():
    user_id = "U123"
    pending_future_events.pop(user_id, None)

    with patch(
        "integrations.schedule_writer.add_future_event",
        side_effect=RuntimeError("Sheets unavailable"),
    ):
        response = handle_future_event_request(
            user_id,
            "add a wedding to the future events for 5/23",
        )

    assert response == (
        'I couldn\'t add "wedding" for 5/23: Sheets unavailable'
    )

    assert user_id not in pending_future_events


def test_handle_future_event_beer_response_adds_beers_and_clears_state():
    user_id = "U123"

    pending_future_events[user_id] = {
        "event": "wedding",
        "date": "5/23",
    }

    with patch(
        "integrations.schedule_writer.add_future_event"
    ) as mock_add:
        response = handle_future_event_beer_response(
            user_id,
            "Hacienda and Super Juice",
        )

    mock_add.assert_called_once_with(
        "Beers: Hacienda and Super Juice"
    )

    assert response == (
        'Added the beer selection for "wedding" '
        "on 5/23: Hacienda and Super Juice"
    )

    assert user_id not in pending_future_events


def test_handle_future_event_beer_response_rejects_empty_response():
    user_id = "U123"

    pending_future_events[user_id] = {
        "event": "wedding",
        "date": "5/23",
    }

    with patch(
        "integrations.schedule_writer.add_future_event"
    ) as mock_add:
        response = handle_future_event_beer_response(
            user_id,
            "   ",
        )

    assert response == (
        "Please tell me which beers you'd like for the event."
    )

    mock_add.assert_not_called()
    assert user_id in pending_future_events

    pending_future_events.pop(user_id, None)


def test_handle_future_event_beer_response_returns_none_without_pending_event():
    response = handle_future_event_beer_response(
        "U999",
        "Hacienda",
    )

    assert response is None