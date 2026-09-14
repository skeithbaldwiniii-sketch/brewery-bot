from knowledge.database import get_connection


def is_report_processed(message_id: str) -> bool:
    """Return True if an Upserve email has already been processed."""

    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM upserve_processed_reports
        WHERE message_id = ?
        """,
        (message_id,),
    ).fetchone()

    connection.close()

    return row is not None


def mark_report_processed(
    message_id: str,
    reporting_period: str | None = None,
) -> None:
    """Record an Upserve report as successfully processed."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO upserve_processed_reports (
            message_id,
            reporting_period
        )
        VALUES (?, ?)
        """,
        (message_id, reporting_period),
    )

    connection.commit()
    connection.close()