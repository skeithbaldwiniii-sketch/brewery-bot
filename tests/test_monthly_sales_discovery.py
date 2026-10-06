from pathlib import Path

from monthly_sales import find_latest_monthly_report


REAL_REPORT = Path(
    r"data\upserve\pmix-report--2026-09-01-to-2026-09-30--vanish-brewery.csv"
)


def test_find_latest_monthly_report_ignores_weekly_reports(tmp_path):
    monthly = tmp_path / "pmix-report--2026-09-01-to-2026-09-30--vanish-brewery.csv"
    weekly = tmp_path / "pmix-report--2026-09-28-to-2026-10-04--vanish-brewery.csv"

    source = REAL_REPORT.read_text()

    monthly.write_text(source)
    weekly.write_text(
        source.replace(
            "09-01-2026 to 09-30-2026",
            "09-28-2026 to 10-04-2026",
            1,
        )
    )

    selected = find_latest_monthly_report(tmp_path)

    assert selected == monthly
