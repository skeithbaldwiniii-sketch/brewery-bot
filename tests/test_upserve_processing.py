from unittest.mock import patch

from integrations.upserve import process_latest_upserve_report

from knowledge.database import get_connection, initialize_database
from knowledge.upserve import (
    is_report_processed,
    mark_report_processed,
)


def test_processed_report_is_detected():
    initialize_database()

    message_id = "integration-test-message-id"

    connection = get_connection()
    connection.execute(
        """
        DELETE FROM upserve_processed_reports
        WHERE message_id = ?
        """,
        (message_id,),
    )
    connection.commit()
    connection.close()

    assert is_report_processed(message_id) is False

    mark_report_processed(
        message_id,
        "test period",
    )

    assert is_report_processed(message_id) is True
def test_upserve_processing_skips_already_processed_report():
    source = {
        "message_id": "test-already-processed",
        "email_subject": "Vanish Weekly Product Mix",
        "email_date": "Mon, 14 Sep 2026",
        "filename": "report.csv",
        "file_path": "data/upserve/report.csv",
        "report": {
            "reporting_period": "09-07-2026 to 09-13-2026",
            "products": [],
        },
    }

    with patch(
        "integrations.upserve.get_latest_upserve_sales_report_with_source",
        return_value=source,
    ), patch(
        "integrations.upserve.is_report_processed",
        return_value=True,
    ), patch(
        "integrations.slack.send_staff_message"
    ) as mock_send:

        result = process_latest_upserve_report()

    assert result["status"] == "already_processed"
    assert result["message_id"] == "test-already-processed"
    assert result["reporting_period"] == "09-07-2026 to 09-13-2026"

    mock_send.assert_not_called()


def test_upserve_processing_sends_new_report_and_marks_processed():
    source = {
        "message_id": "test-new-upserve-report",
        "email_subject": "Vanish Weekly Product Mix",
        "email_date": "Mon, 14 Sep 2026",
        "filename": "report.csv",
        "file_path": "data/upserve/report.csv",
        "report": {
            "reporting_period": "09-07-2026 to 09-13-2026",
            "products": [
                {
                    "rank": 1,
                    "product": "Test Beer",
                    "sold": 100,
                }
            ],
        },
    }

    slack_response = {
        "ok": True,
        "ts": "1234567890.123456",
    }

    with patch(
        "integrations.upserve.get_latest_upserve_sales_report_with_source",
        return_value=source,
    ), patch(
        "integrations.upserve.is_report_processed",
        return_value=False,
    ), patch(
        "integrations.slack.send_staff_message",
        return_value=slack_response,
    ) as mock_send, patch(
        "integrations.upserve.mark_report_processed"
    ) as mock_mark:

        result = process_latest_upserve_report()

    assert result["status"] == "processed"
    assert result["message_id"] == "test-new-upserve-report"
    assert result["reporting_period"] == "09-07-2026 to 09-13-2026"
    assert result["slack_timestamp"] == "1234567890.123456"

    mock_send.assert_called_once()
    mock_mark.assert_called_once_with(
        "test-new-upserve-report",
        "09-07-2026 to 09-13-2026",
    )


def test_upserve_processing_does_not_mark_failed_slack_send():
    source = {
        "message_id": "test-failed-upserve-report",
        "email_subject": "Vanish Weekly Product Mix",
        "email_date": "Mon, 14 Sep 2026",
        "filename": "report.csv",
        "file_path": "data/upserve/report.csv",
        "report": {
            "reporting_period": "09-07-2026 to 09-13-2026",
            "products": [],
        },
    }

    with patch(
        "integrations.upserve.get_latest_upserve_sales_report_with_source",
        return_value=source,
    ), patch(
        "integrations.upserve.is_report_processed",
        return_value=False,
    ), patch(
        "integrations.slack.send_staff_message",
        side_effect=RuntimeError("Slack failed"),
    ), patch(
        "integrations.upserve.mark_report_processed"
    ) as mock_mark:

        try:
            process_latest_upserve_report()
        except RuntimeError as exc:
            assert str(exc) == "Slack failed"
        else:
            raise AssertionError("Expected Slack failure")

    mock_mark.assert_not_called()