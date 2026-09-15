import pytest
import knowledge.database as database

from intelligence.karma import (
    contains_please,
    get_karma,
    get_response_delay,
    record_request,
)

@pytest.fixture(autouse=True)
def isolated_karma_database(tmp_path, monkeypatch):
    """
    Give every Karma test its own temporary SQLite database.
    """
    test_database = tmp_path / "karma_test.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database,
    )

    database.initialize_database()

# -------------------------------------------------
# PLEASE DETECTION
# -------------------------------------------------


def test_contains_please_detects_word():
    assert contains_please("Please tell me how much Citra we have.") is True


def test_contains_please_is_case_insensitive():
    assert contains_please("PLEASE tell me how much Citra we have.") is True


def test_contains_please_detects_please_mid_sentence():
    assert contains_please(
        "Can you please tell me how much Citra we have?"
    ) is True


def test_contains_please_does_not_match_partial_word():
    assert contains_please("What is the pleasing aroma of Citra?") is False


def test_contains_please_rejects_empty_input():
    assert contains_please("") is False
    assert contains_please(None) is False


# -------------------------------------------------
# KARMA
# -------------------------------------------------


def test_new_user_starts_with_zero_karma():
    user_id = "karma_test_new_user"

    karma = get_karma(user_id)

    assert karma["user_id"] == user_id
    assert karma["karma_score"] == 0
    assert karma["consecutive_no_please"] == 0
    assert karma["total_requests"] == 0
    assert karma["total_please_requests"] == 0


def test_first_request_without_please_creates_one_second_delay():
    user_id = "karma_test_first"

    result = record_request(
        user_id,
        "How much Citra do we have?",
    )

    assert result["karma_score"] == -1
    assert result["consecutive_no_please"] == 1
    assert result["total_requests"] == 1
    assert result["total_please_requests"] == 0
    assert result["response_delay"] == 1
    assert result["contains_please"] is False


def test_second_consecutive_request_increases_delay():
    user_id = "karma_test_second"

    record_request(user_id, "How much Citra do we have?")
    result = record_request(user_id, "How much Mosaic do we have?")

    assert result["karma_score"] == -2
    assert result["consecutive_no_please"] == 2
    assert result["response_delay"] == 2


def test_third_consecutive_request_has_three_second_delay():
    user_id = "karma_test_third"

    record_request(user_id, "How much Citra do we have?")
    record_request(user_id, "How much Mosaic do we have?")
    result = record_request(user_id, "How much Simcoe do we have?")

    assert result["karma_score"] == -3
    assert result["consecutive_no_please"] == 3
    assert result["response_delay"] == 3


def test_fourth_consecutive_request_has_five_second_delay():
    user_id = "karma_test_fourth"

    for question in [
        "How much Citra?",
        "How much Mosaic?",
        "How much Simcoe?",
    ]:
        record_request(user_id, question)

    result = record_request(
        user_id,
        "How much Amarillo?",
    )

    assert result["karma_score"] == -4
    assert result["consecutive_no_please"] == 4
    assert result["response_delay"] == 5


def test_fifth_consecutive_request_has_seven_second_delay():
    user_id = "karma_test_fifth"

    for question in [
        "How much Citra?",
        "How much Mosaic?",
        "How much Simcoe?",
        "How much Amarillo?",
    ]:
        record_request(user_id, question)

    result = record_request(
        user_id,
        "How much Centennial?",
    )

    assert result["karma_score"] == -5
    assert result["consecutive_no_please"] == 5
    assert result["response_delay"] == 7


def test_sixth_consecutive_request_reaches_maximum_delay():
    user_id = "karma_test_max"

    for number in range(5):
        record_request(
            user_id,
            f"How much hop {number}?",
        )

    result = record_request(
        user_id,
        "How much hop 6?",
    )

    assert result["karma_score"] == -6
    assert result["consecutive_no_please"] == 6
    assert result["response_delay"] == 10


def test_delay_remains_capped_at_ten_seconds():
    user_id = "karma_test_cap"

    for number in range(20):
        result = record_request(
            user_id,
            f"How much hop {number}?",
        )

    assert result["karma_score"] == -20
    assert result["consecutive_no_please"] == 20
    assert result["response_delay"] == 10


# -------------------------------------------------
# PLEASE RESET
# -------------------------------------------------


def test_please_resets_karma_and_delay():
    user_id = "karma_test_reset"

    record_request(user_id, "How much Citra?")
    record_request(user_id, "How much Mosaic?")
    record_request(user_id, "How much Simcoe?")

    result = record_request(
        user_id,
        "Please tell me how much Amarillo we have.",
    )

    assert result["karma_score"] == 0
    assert result["consecutive_no_please"] == 0
    assert result["response_delay"] == 0
    assert result["contains_please"] is True


def test_please_increments_total_please_requests():
    user_id = "karma_test_please_count"

    record_request(user_id, "How much Citra?")
    result = record_request(
        user_id,
        "Please tell me how much Mosaic we have.",
    )

    assert result["total_requests"] == 2
    assert result["total_please_requests"] == 1


# -------------------------------------------------
# PERSISTENCE
# -------------------------------------------------


def test_karma_persists_between_reads():
    user_id = "karma_test_persistence"

    record_request(
        user_id,
        "How much Citra do we have?",
    )

    karma = get_karma(user_id)

    assert karma["karma_score"] == -1
    assert karma["consecutive_no_please"] == 1
    assert karma["total_requests"] == 1


def test_response_delay_matches_persisted_karma():
    user_id = "karma_test_delay"

    record_request(user_id, "How much Citra?")
    record_request(user_id, "How much Mosaic?")

    assert get_response_delay(user_id) == 2


# -------------------------------------------------
# VALIDATION
# -------------------------------------------------


def test_get_karma_rejects_empty_user_id():
    import pytest

    with pytest.raises(ValueError, match="Karma user ID cannot be empty"):
        get_karma("")


def test_record_request_rejects_empty_user_id():
    import pytest

    with pytest.raises(ValueError, match="Karma user ID cannot be empty"):
        record_request("", "How much Citra?")


def test_record_request_rejects_empty_question():
    import pytest

    with pytest.raises(ValueError, match="Karma question cannot be empty"):
        record_request("karma_test_empty_question", "   ")
