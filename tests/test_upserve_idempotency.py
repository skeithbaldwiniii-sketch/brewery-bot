from knowledge.database import get_connection, initialize_database
from knowledge.upserve import (
    is_report_processed,
    mark_report_processed,
)


def test_upserve_report_idempotency():
    initialize_database()

    message_id = "test-upserve-message-id"
    reporting_period = "09-07-2026 to 09-13-2026"

    connection = get_connection()
    connection.execute(
        "DELETE FROM upserve_processed_reports WHERE message_id = ?",
        (message_id,),
    )
    connection.commit()
    connection.close()

    assert is_report_processed(message_id) is False

    mark_report_processed(
        message_id,
        reporting_period,
    )

    assert is_report_processed(message_id) is True

    connection = get_connection()
    row = connection.execute(
        """
        SELECT message_id, reporting_period
        FROM upserve_processed_reports
        WHERE message_id = ?
        """,
        (message_id,),
    ).fetchone()
    connection.close()

    assert row["message_id"] == message_id
    assert row["reporting_period"] == reporting_period