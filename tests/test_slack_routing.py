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

def test_inventory_question_precedes_brewery_beer_knowledge():
    """Inventory questions should not be intercepted by beer knowledge."""

    event = {
        "text": "<@BREWSBOT> How many kegs of Oktoberfest are in the Coldbox?",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch(
        "integrations.slack.answer_inventory_question",
        return_value=(
            "Current wholesale inventory:\n"
            "- Oktoberfest: 6.00 5.16-gal Keg\n"
            "- Oktoberfest: 5.00 15.5-gal Keg"
        ),
    ), patch(
        "integrations.slack.answer_brewery_beer_question"
    ) as mock_beer_answer, patch(
        "integrations.slack.send_delayed_response",
        side_effect=lambda say, response, delay: say(response),
    ):
        handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "Current wholesale inventory:" in responses[0]
    assert "Oktoberfest: 6.00 5.16-gal Keg" in responses[0]
    assert "Oktoberfest: 5.00 15.5-gal Keg" in responses[0]
    mock_beer_answer.assert_not_called()
