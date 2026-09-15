import time

import pytest

from integrations import slack
from integrations.slack import send_delayed_response


def test_send_delayed_response_immediate():
    responses = []

    def fake_say(response):
        responses.append(response)

    send_delayed_response(
        fake_say,
        "hello",
        0,
    )

    assert responses == ["hello"]


def test_send_delayed_response_delayed():
    responses = []

    def fake_say(response):
        responses.append(response)

    start = time.monotonic()

    send_delayed_response(
        fake_say,
        "hello",
        0.05,
    )

    assert responses == []

    time.sleep(0.15)

    elapsed = time.monotonic() - start

    assert responses == ["hello"]
    assert elapsed >= 0.05


def test_send_delayed_response_empty_response():
    responses = []

    def fake_say(response):
        responses.append(response)

    send_delayed_response(
        fake_say,
        "",
        1,
    )

    assert responses == []


def test_handle_mention_records_karma_once(monkeypatch):
    recorded_requests = []
    responses = []

    def fake_record_request(user_id, question):
        recorded_requests.append((user_id, question))

        return {
            "response_delay": 0,
        }

    def fake_say(response):
        responses.append(response)

    def fake_build_answer(question):
        return "Test answer"

    monkeypatch.setattr(
        slack,
        "record_request",
        fake_record_request,
    )

    monkeypatch.setattr(
        slack,
        "build_answer",
        fake_build_answer,
    )

    monkeypatch.setattr(
        slack,
        "has_capability",
        lambda channel_id, capability: True,
    )

    event = {
        "user": "U_TEST",
        "text": "<@BREWS> what is a lager?",
        "channel": "C_TEST",
    }

    slack.handle_mention(
        event,
        fake_say,
    )

    assert recorded_requests == [
        ("U_TEST", "what is a lager?")
    ]

    assert responses == ["Test answer"]

def test_handle_mention_future_event_response_uses_karma(
    monkeypatch,
):
    recorded_requests = []
    responses = []

    def fake_record_request(user_id, question):
        recorded_requests.append((user_id, question))

        return {
            "response_delay": 0,
        }

    def fake_say(response):
        responses.append(response)

    def fake_handle_future_event_beer_response(
        user_id,
        question,
    ):
        return "Future event updated"

    monkeypatch.setattr(
        slack,
        "record_request",
        fake_record_request,
    )

    monkeypatch.setattr(
        slack,
        "has_pending_future_event",
        lambda user_id: True,
    )

    monkeypatch.setattr(
        slack,
        "handle_future_event_beer_response",
        fake_handle_future_event_beer_response,
    )

    event = {
        "user": "U_TEST",
        "text": "<@BREWS> IPA, Pilsner",
        "channel": "C_TEST",
    }

    slack.handle_mention(
        event,
        fake_say,
    )

    assert recorded_requests == [
        ("U_TEST", "IPA, Pilsner")
    ]

    assert responses == [
        "Future event updated"
    ]


def test_handle_mention_style_selection_uses_karma(
    monkeypatch,
):
    recorded_requests = []
    responses = []

    def fake_record_request(user_id, question):
        recorded_requests.append((user_id, question))

        return {
            "response_delay": 0,
        }

    def fake_say(response):
        responses.append(response)

    def fake_handle_style_selection(
        user_id,
        question,
    ):
        return "Style selected"

    monkeypatch.setattr(
        slack,
        "record_request",
        fake_record_request,
    )

    monkeypatch.setattr(
        slack,
        "has_pending_future_event",
        lambda user_id: False,
    )

    monkeypatch.setattr(
        slack,
        "handle_style_selection",
        fake_handle_style_selection,
    )

    slack.pending_style_selections.clear()

    slack.pending_style_selections["U_TEST"] = {
        1: "American IPA",
        2: "Imperial Stout",
    }

    event = {
        "user": "U_TEST",
        "text": "<@BREWS> 1",
        "channel": "C_TEST",
    }

    slack.handle_mention(
        event,
        fake_say,
    )

    assert recorded_requests == [
        ("U_TEST", "1")
    ]

    assert responses == [
        "Style selected"
    ]

    slack.pending_style_selections.clear()

def test_handle_mention_applies_progressive_karma_delay(
    monkeypatch,
):
    responses = []
    delays = []

    def fake_record_request(user_id, question):
        return {
            "response_delay": {
                "what is a beer?": 1,
                "tell me about ipa": 2,
                "please tell me about stout": 0,
            }[question],
        }

    def fake_send_delayed_response(
        say,
        response,
        delay,
    ):
        delays.append(delay)
        say(response)

    def fake_say(response):
        responses.append(response)

    monkeypatch.setattr(
        slack,
        "record_request",
        fake_record_request,
    )

    monkeypatch.setattr(
        slack,
        "send_delayed_response",
        fake_send_delayed_response,
    )

    monkeypatch.setattr(
        slack,
        "has_pending_future_event",
        lambda user_id: False,
    )

    monkeypatch.setattr(
        slack,
        "has_capability",
        lambda channel_id, capability: True,
    )

    monkeypatch.setattr(
        slack,
        "build_answer",
        lambda question: f"Answer: {question}",
    )

    requests = [
        "what is a beer?",
        "tell me about ipa",
        "please tell me about stout",
    ]

    for question in requests:
        event = {
            "user": "U_TEST",
            "text": f"<@BREWS> {question}",
            "channel": "C_TEST",
        }

        slack.handle_mention(
            event,
            fake_say,
        )

    assert delays == [1, 2, 0]

    assert responses == [
        "Answer: what is a beer?",
        "Answer: tell me about ipa",
        "Answer: please tell me about stout",
    ]
