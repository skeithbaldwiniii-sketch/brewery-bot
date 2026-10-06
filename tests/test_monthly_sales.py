from pathlib import Path
from unittest.mock import MagicMock, patch

from monthly_sales import run_monthly_sales


REPORT = Path(
    r"data\upserve\pmix-report--2026-09-01-to-2026-09-30--vanish-brewery.csv"
)


def test_run_monthly_sales_dry_run():
    result = run_monthly_sales(REPORT)

    assert result["reporting_period"] == "09-01-2026 to 09-30-2026"
    assert result["pint_updates"] == 23
    assert result["can_updates"] == 14
    assert len(result["writes"]) == 37
    assert result["applied"] is False


def test_run_monthly_sales_apply_uses_guarded_write_and_verify():
    spreadsheet = MagicMock()

    state = {
        "pint_values": [[""] for _ in range(36)],
        "can_values": [[""] for _ in range(14)],
        "total_formula": "=SUM(R6:R41)",
        "percentage_formulas": [
            [f"=R{row}/$R$42"] for row in range(6, 42)
        ],
        "ros_formulas": [
            [f"=(AR{row}/4)"] for row in range(6, 20)
        ],
    }

    with (
        patch("monthly_sales.connect_to_sales_spreadsheet", return_value=spreadsheet) as connect,
        patch("monthly_sales.preflight_sales_sheet", return_value=state) as preflight,
        patch("monthly_sales.apply_sales_sheet_writes") as apply_writes,
        patch("monthly_sales.verify_sales_sheet_writes") as verify,
    ):
        result = run_monthly_sales(REPORT, apply=True)

    connect.assert_called_once()
    preflight.assert_called_once_with(spreadsheet)
    apply_writes.assert_called_once()
    verify.assert_called_once()

    assert result["reporting_period"] == "09-01-2026 to 09-30-2026"
    assert result["pint_updates"] == 23
    assert result["can_updates"] == 14
    assert len(result["writes"]) == 37
    assert result["applied"] is True
    apply_writes.assert_called_once()
    verify.assert_called_once()



def test_main_download_uses_gmail_report(tmp_path):
    downloaded = tmp_path / "pmix-report--2026-09-01-to-2026-09-30--vanish-brewery.csv"
    downloaded.write_text(REPORT.read_text())

    source = {"file_path": downloaded}

    with (
        patch(
            "monthly_sales.download_latest_upserve_monthly_report_with_source",
            return_value=source,
        ) as download,
        patch(
            "monthly_sales.run_monthly_sales",
            return_value={
                "reporting_period": "09-01-2026 to 09-30-2026",
                "pint_updates": 23,
                "can_updates": 14,
                "writes": [],
                "applied": False,
            },
        ) as run,
        patch(
            "sys.argv",
            ["monthly_sales.py", "--download"],
        ),
    ):
        from monthly_sales import main

        main()

    download.assert_called_once()
    run.assert_called_once_with(downloaded, apply=False)

def test_dry_run_scheduler_wrapper_uses_monthly_runner(tmp_path):
    import subprocess
    from unittest.mock import patch

    from scripts import run_monthly_sales_dry_run

    fake_python = tmp_path / "python.exe"
    fake_runner = tmp_path / "monthly_sales.py"

    with (
        patch.object(run_monthly_sales_dry_run, "PYTHON", fake_python),
        patch.object(run_monthly_sales_dry_run, "RUNNER", fake_runner),
        patch.object(
            run_monthly_sales_dry_run.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=[],
                returncode=0,
            ),
        ) as run,
    ):
        result = run_monthly_sales_dry_run.main()

    assert result == 0
    run.assert_called_once_with(
        [str(fake_python), str(fake_runner), "--download"],
        cwd=run_monthly_sales_dry_run.PROJECT_DIR,
        check=False,
    )

