from knowledge.database import get_connection


# Response delay in seconds based on consecutive requests
# without "please".
DELAY_BY_STREAK = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 5,
    5: 7,
}

MAX_DELAY_SECONDS = 10


def contains_please(question):
    """
    Determine whether a request contains the word 'please'.

    The check is case-insensitive and treats 'please' as a
    standalone word.
    """
    if not question:
        return False

    import re

    return re.search(
        r"\bplease\b",
        question,
        flags=re.IGNORECASE,
    ) is not None


def get_karma(user_id):
    """
    Return the current Karma record for a user.

    Creates a record with zero Karma if the user has not
    been seen before.
    """
    if not user_id:
        raise ValueError("Karma user ID cannot be empty.")

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                user_id,
                karma_score,
                consecutive_no_please,
                total_requests,
                total_please_requests,
                updated_at
            FROM karma_users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            connection.execute(
                """
                INSERT INTO karma_users (
                    user_id,
                    karma_score,
                    consecutive_no_please,
                    total_requests,
                    total_please_requests
                )
                VALUES (?, 0, 0, 0, 0)
                """,
                (user_id,),
            )
            connection.commit()

            row = connection.execute(
                """
                SELECT
                    user_id,
                    karma_score,
                    consecutive_no_please,
                    total_requests,
                    total_please_requests,
                    updated_at
                FROM karma_users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        return dict(row)

    finally:
        connection.close()


def get_response_delay(user_id):
    """
    Return the current response delay for a user.
    """
    karma = get_karma(user_id)

    streak = karma["consecutive_no_please"]

    if streak in DELAY_BY_STREAK:
        return DELAY_BY_STREAK[streak]

    return MAX_DELAY_SECONDS


def record_request(user_id, question):
    """
    Record a user's request and update their Karma.

    Requests containing 'please' reset the current Karma
    penalty and consecutive no-please streak.

    Requests without 'please' increase both the Karma
    penalty and consecutive no-please streak.

    Returns the updated Karma record plus response delay.
    """
    if not user_id:
        raise ValueError("Karma user ID cannot be empty.")

    if not question or not question.strip():
        raise ValueError("Karma question cannot be empty.")

    polite = contains_please(question)

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                karma_score,
                consecutive_no_please,
                total_requests,
                total_please_requests
            FROM karma_users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            karma_score = 0
            consecutive_no_please = 0
            total_requests = 0
            total_please_requests = 0
        else:
            karma_score = row["karma_score"]
            consecutive_no_please = row["consecutive_no_please"]
            total_requests = row["total_requests"]
            total_please_requests = row["total_please_requests"]

        total_requests += 1

        if polite:
            karma_score = 0
            consecutive_no_please = 0
            total_please_requests += 1
        else:
            karma_score -= 1
            consecutive_no_please += 1

        connection.execute(
            """
            INSERT INTO karma_users (
                user_id,
                karma_score,
                consecutive_no_please,
                total_requests,
                total_please_requests
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                karma_score = excluded.karma_score,
                consecutive_no_please = excluded.consecutive_no_please,
                total_requests = excluded.total_requests,
                total_please_requests = excluded.total_please_requests,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                karma_score,
                consecutive_no_please,
                total_requests,
                total_please_requests,
            ),
        )

        connection.commit()

    finally:
        connection.close()

    karma = get_karma(user_id)

    return {
        **karma,
        "contains_please": polite,
        "response_delay": get_response_delay(user_id),
    }
