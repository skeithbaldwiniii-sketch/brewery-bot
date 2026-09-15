from unittest.mock import patch

from integrations.slack import handle_mention
from intelligence.access_control import (
    BEER30,
    STAFF_CHANNEL_ID,
    TEST_CHANNEL_ID,
)


def test_beer30_question_reaches_slack():
    """Beer30 questions should send their answer through say()."""

    event = {
        "text": "<@BREWSBOT> What is currently fermenting?",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch(
        "integrations.slack.answer_wip_question",
        return_value="There are 5 batches currently fermenting.",
    ), patch(
        "integrations.slack.send_delayed_response",
        side_effect=lambda say, response, delay: say(response),
    ):
        handle_mention(event, fake_say)

    assert len(responses) == 1
    assert responses[0] == "There are 5 batches currently fermenting."


def test_staff_channel_denies_beer30():
    """Staff users should not receive Beer30 information."""

    event = {
        "text": "<@BREWSBOT> What is currently fermenting?",
        "user": "U_TEST",
        "channel": STAFF_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch("integrations.slack.answer_wip_question") as mock_answer, patch(
        "integrations.slack.send_delayed_response",
        side_effect=lambda say, response, delay: say(response),
    ):
        handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "don't have access" in responses[0].lower()
    mock_answer.assert_not_called()