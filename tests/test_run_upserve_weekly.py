from unittest.mock import patch

from scripts.run_upserve_weekly import main


def test_run_upserve_weekly_initializes_database_and_processes_report():
    result = {
        "status": "already_processed",
        "reporting_period": "09-07-2026 to 09-13-2026",
    }

    with patch(
        "scripts.run_upserve_weekly.initialize_database"
    ) as mock_initialize, patch(
        "scripts.run_upserve_weekly.process_latest_upserve_report",
        return_value=result,
    ) as mock_process:

        main()

    mock_initialize.assert_called_once()
    mock_process.assert_called_once()

def test_upserve_weekly_logs_processing_failure(caplog):
    with patch(
        "scripts.run_upserve_weekly.process_latest_upserve_report",
        side_effect=RuntimeError("Test processing failure"),
    ):
        try:
            main()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected processing failure")

    assert "Upserve weekly report processing failed." in caplog.text
    assert "Test processing failure" in caplog.text

def test_upserve_weekly_main_returns_processing_result():
    result = {
        "status": "processed",
        "reporting_period": "09-07-2026 to 09-13-2026",
        "slack_timestamp": "1234567890.123456",
    }

    with patch(
        "scripts.run_upserve_weekly.process_latest_upserve_report",
        return_value=result,
    ):
        returned = main()

    assert returned == result
