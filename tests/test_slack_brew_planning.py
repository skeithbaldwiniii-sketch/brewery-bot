from unittest.mock import patch

from integrations.slack import handle_mention


def test_brew_plan_request_reaches_brew_planning():
    responses = []

    event = {
        "user": "U_TEST",
        "channel": "C_TEST",
        "text": "<@UBREWS> I'd like to brew Festbier and Hefeweizen",
    }

    fake_say = lambda message: responses.append(message)

    fake_result = {
        "feasible": True,
        "beers": [
            {"requested_name": "Festbier"},
            {"requested_name": "Hefeweizen"},
        ],
        "requirements": [],
        "shortages": [],
        "unknown_inventory": [],
        "not_found": [],
        "incomplete_recipes": [],
    }

    with (
        patch(
            "integrations.slack.record_request",
            return_value={"response_delay": 0},
        ),
        patch(
            "integrations.slack.require_capability",
            return_value=True,
        ),
        patch(
            "integrations.slack.check_brew_feasibility",
            return_value=fake_result,
        ) as mock_feasibility,
        patch(
            "integrations.slack.format_brew_plan_response",
            return_value="BREW PLAN RESPONSE",
        ),
        patch(
            "integrations.slack.send_delayed_response",
            side_effect=lambda say, response, delay: say(response),
        ),
    ):
        handle_mention(event, fake_say)

    mock_feasibility.assert_called_once_with(
        ["Festbier", "Hefeweizen"]
    )

    assert responses == ["BREW PLAN RESPONSE"]


def test_brew_plan_request_denied_without_beer30_capability():
    responses = []

    event = {
        "user": "U_TEST",
        "channel": "C_TEST",
        "text": "<@UBREWS> Can we brew Festbier?",
    }

    fake_say = lambda message: responses.append(message)

    with (
        patch(
            "integrations.slack.record_request",
            return_value={"response_delay": 0},
        ),
        patch(
            "integrations.slack.require_capability",
            return_value=False,
        ),
        patch(
            "integrations.slack.access_denied_message",
            return_value="ACCESS DENIED",
        ),
        patch(
            "integrations.slack.check_brew_feasibility",
        ) as mock_feasibility,
        patch(
            "integrations.slack.send_delayed_response",
            side_effect=lambda say, response, delay: say(response),
        ),
    ):
        handle_mention(event, fake_say)

    mock_feasibility.assert_not_called()
    assert responses == ["ACCESS DENIED"]