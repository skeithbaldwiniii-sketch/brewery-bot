from unittest.mock import patch

from intelligence.task_queries import (
    complete_task_from_question,
)


def test_complete_task_uses_today_when_no_day_is_given():
    with patch(
        "intelligence.task_queries.get_today_name",
        return_value="thursday",
    ), patch(
        "intelligence.task_queries.find_task_days",
        return_value=[
            {
                "day": "thursday",
                "task": "Transfer Festbier to BT3",
            }
        ],
    ), patch(
        "intelligence.task_queries.complete_task_on_day",
        return_value={
            "task": "Transfer Festbier to BT3",
            "day": "thursday",
            "row": 42,
            "completed": True,
        },
    ) as mock_complete:

        result = complete_task_from_question(
            "Brews Springsteen please mark "
            "Transfer Festbier to BT3 as completed"
        )

    assert result == (
        "Marked 'Transfer Festbier to BT3' "
        "as completed on Thursday."
    )

    mock_complete.assert_called_once_with(
        "Transfer Festbier to BT3",
        "thursday",
    )


def test_complete_task_respects_explicit_day():
    with patch(
        "intelligence.task_queries.find_task_days",
        return_value=[
            {
                "day": "thursday",
                "task": "Transfer Festbier to BT3",
            }
        ],
    ), patch(
        "intelligence.task_queries.complete_task_on_day",
        return_value={
            "task": "Transfer Festbier to BT3",
            "day": "thursday",
            "row": 42,
            "completed": True,
        },
    ) as mock_complete:

        result = complete_task_from_question(
            "Please mark Transfer Festbier to BT3 "
            "on Thursday as completed"
        )

    assert result == (
        "Marked 'Transfer Festbier to BT3' "
        "as completed on Thursday."
    )

    mock_complete.assert_called_once_with(
        "Transfer Festbier to BT3",
        "thursday",
    )


def test_complete_task_does_not_mark_task_on_wrong_day():
    with patch(
        "intelligence.task_queries.get_today_name",
        return_value="thursday",
    ), patch(
        "intelligence.task_queries.find_task_days",
        return_value=[
            {
                "day": "friday",
                "task": "Transfer Festbier to BT3",
            }
        ],
    ), patch(
        "intelligence.task_queries.complete_task_on_day",
    ) as mock_complete:

        result = complete_task_from_question(
            "Mark Transfer Festbier to BT3 as completed"
        )

    assert result == (
        "I couldn't find 'transfer festbier to bt3' "
        "on the Thursday schedule."
    )

    mock_complete.assert_not_called()


def test_non_completion_question_returns_none():
    result = complete_task_from_question(
        "When are we transferring Festbier?"
    )

    assert result is None
