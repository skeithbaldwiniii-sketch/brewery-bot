import pytest

import knowledge.database as database

from intelligence.karma import (
    format_karma_details,
    format_karma_leaderboard,
    get_karma_leaderboard,
    record_request,
)


@pytest.fixture(autouse=True)
def isolated_karma_database(tmp_path, monkeypatch):
    test_database = tmp_path / "karma_inspector_test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    database.initialize_database()


def test_empty_leaderboard():
    assert get_karma_leaderboard() == []

    result = format_karma_leaderboard()

    assert "Karma Score Leaderboard" in result
    assert "No Karma records yet." in result

def test_leaderboard_orders_by_karma():
    record_request("U_BAD", "Do something")
    record_request("U_BAD", "Do something")
    record_request("U_GOOD", "Please do something")

    leaderboard = get_karma_leaderboard()

    assert leaderboard[0]["user_id"] == "U_GOOD"
    assert leaderboard[0]["karma_score"] == 0

    assert leaderboard[1]["user_id"] == "U_BAD"
    assert leaderboard[1]["karma_score"] == -2


def test_leaderboard_contains_user_information():
    record_request("U_TEST", "Do something")

    result = format_karma_leaderboard()

    assert "Karma Score Leaderboard" in result
    assert "<@U_TEST>" in result
    assert "Karma: -1" in result
    assert "Streak: 1" in result
    assert "Delay: 1s" in result
    assert "Courtesy: 0%" in result


def test_karma_details():
    record_request("U_TEST", "Do something")
    record_request("U_TEST", "Do something")
    record_request("U_TEST", "Please do something")

    result = format_karma_details("U_TEST")

    assert "Karma for <@U_TEST>" in result
    assert "Karma Score: 0" in result
    assert "No-please streak: 0" in result
    assert "Current response delay: 0 seconds" in result
    assert "Total requests: 3" in result
    assert "Requests with please: 1" in result
    assert "Courtesy rate: 33%" in result


def test_new_user_details_are_zeroed():
    result = format_karma_details("U_NEW")

    assert "Karma Score: 0" in result
    assert "No-please streak: 0" in result
    assert "Current response delay: 0 seconds" in result
    assert "Total requests: 0" in result
    assert "Requests with please: 0" in result
    assert "Courtesy rate: 0%" in result