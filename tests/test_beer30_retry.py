import requests

from integrations.beer30 import _get_with_retry


def test_get_with_retry_succeeds_after_temporary_connection_failure(
    monkeypatch,
):
    responses = [
        requests.ConnectionError("temporary DNS failure"),
        requests.ConnectionError("temporary DNS failure"),
        "success",
    ]

    def fake_get(*args, **kwargs):
        result = responses.pop(0)

        if isinstance(result, Exception):
            raise result

        return result

    sleep_calls = []

    monkeypatch.setattr(
        "integrations.beer30.requests.get",
        fake_get,
    )
    monkeypatch.setattr(
        "integrations.beer30.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    result = _get_with_retry(
        "http://api.b30.app/test",
        params={"key": "test"},
    )

    assert result == "success"
    assert sleep_calls == [5, 5]


def test_get_with_retry_raises_after_three_failures(
    monkeypatch,
):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("DNS failure")

    sleep_calls = []

    monkeypatch.setattr(
        "integrations.beer30.requests.get",
        fake_get,
    )
    monkeypatch.setattr(
        "integrations.beer30.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )

    try:
        _get_with_retry(
            "http://api.b30.app/test",
            params={"key": "test"},
        )
    except requests.ConnectionError as exc:
        assert "DNS failure" in str(exc)
    else:
        raise AssertionError("Expected ConnectionError")

    assert sleep_calls == [5, 5]