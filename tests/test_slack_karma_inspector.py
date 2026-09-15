from unittest.mock import patch

import knowledge.database as database

from integrations.slack import handle_mention
from intelligence.access_control import TEST_CHANNEL_ID


def setup_database(tmp_path, monkeypatch):
    test_database = tmp_path / "slack_karma_inspector.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    database.initialize_database()


def test_karma_command_does_not_record_request(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karma",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch("integrations.slack.record_request") as mock_record:
        handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "Karma Score Leaderboard" in responses[0]
    mock_record.assert_not_called()


def test_karma_me_command(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karma me",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "Karma for <@U_TEST>" in responses[0]


def test_karma_user_command(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karma <@U_TARGET>",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "Karma for <@U_TARGET>" in responses[0]


def test_karma_command_is_case_insensitive(tmp_path, monkeypatch):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> KARMA ME",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "Karma for <@U_TEST>" in responses[0]


def test_karma_command_denied_outside_test_channel(
    tmp_path,
    monkeypatch,
):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karma",
        "user": "U_TEST",
        "channel": "C_SOME_OTHER_CHANNEL",
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch(
        "integrations.slack.record_request"
    ) as mock_record:
        handle_mention(event, fake_say)

    assert len(responses) == 1
    assert "only available in the private test channel" in responses[0]
    mock_record.assert_not_called()


def test_invalid_karma_command_is_not_inspector_command(
    tmp_path,
    monkeypatch,
):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karma beer",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch(
        "integrations.slack.record_request",
        return_value={
            "response_delay": 0,
        },
    ) as mock_record:
        handle_mention(event, fake_say)

    mock_record.assert_called_once()
    assert len(responses) == 1

def test_karmaize_is_not_inspector_command(
    tmp_path,
    monkeypatch,
):
    setup_database(tmp_path, monkeypatch)

    event = {
        "text": "<@BREWSBOT> karmaize this",
        "user": "U_TEST",
        "channel": TEST_CHANNEL_ID,
    }

    responses = []

    def fake_say(message):
        responses.append(message)

    with patch(
        "integrations.slack.record_request",
        return_value={
            "response_delay": 0,
        },
    ) as mock_record:
        handle_mention(event, fake_say)

    mock_record.assert_called_once()
    assert len(responses) == 1