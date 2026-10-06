"""Reusable monthly Upserve sales runner.

Default behavior is a dry run. Use --apply only when a live
Google Sheets update has been explicitly authorized.
"""

from __future__ import annotations

import argparse
import calendar
from datetime import datetime
from pathlib import Path

from integrations.sales_sheet import (
    apply_sales_sheet_writes,
    build_sales_sheet_writes,
    connect_to_sales_spreadsheet,
    preflight_sales_sheet,
    verify_sales_sheet_writes,
)
from integrations.upserve import (
    download_latest_upserve_monthly_report_with_source,
    parse_upserve_monthly_sales_report,
)
from reports.sales_sheet_mapping import (
    build_sales_sheet_updates,
    validate_sales_sheet_updates,
)


DEFAULT_REPORT_DIR = Path("data/upserve")


def find_latest_monthly_report(report_dir: Path) -> Path:
    """Find the newest complete-calendar-month Upserve PMIX report."""
    candidates = sorted(
        report_dir.glob("pmix-report--*.csv"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )

    monthly_reports = []

    for candidate in candidates:
        try:
            report = parse_upserve_monthly_sales_report(candidate)
        except (ValueError, KeyError):
            continue

        period = report["reporting_period"]

        try:
            start_text, end_text = period.split(" to ")
            start = datetime.strptime(start_text, "%m-%d-%Y").date()
            end = datetime.strptime(end_text, "%m-%d-%Y").date()
        except ValueError:
            continue

        if (
            start.day == 1
            and start.year == end.year
            and start.month == end.month
            and end.day == calendar.monthrange(end.year, end.month)[1]
        ):
            monthly_reports.append(candidate)

    if not monthly_reports:
        raise FileNotFoundError(
            f"No complete monthly Upserve PMIX reports found in {report_dir}."
        )

    return monthly_reports[0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process a monthly Upserve sales report."
    )
    parser.add_argument(
        "report",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the Upserve monthly PMIX CSV. "
        "If omitted, the newest complete monthly report is selected.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the validated write plan to Google Sheets.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the latest monthly Upserve report from Gmail first.",
    )
    return parser


def run_monthly_sales(report_path: Path, apply: bool = False) -> dict:
    """Process a monthly report, optionally applying validated sheet updates."""
    report = parse_upserve_monthly_sales_report(report_path)
    updates = build_sales_sheet_updates(report)
    validate_sales_sheet_updates(updates)

    result = {
        "reporting_period": report["reporting_period"],
        "pint_updates": len(updates["pint_updates"]),
        "can_updates": len(updates["can_updates"]),
        "writes": [],
        "applied": False,
    }

    if not apply:
        state = {
            "pint_values": [[""] for _ in range(36)],
            "can_values": [[""] for _ in range(14)],
        }
        result["writes"] = build_sales_sheet_writes(state, updates)
        return result

    spreadsheet = connect_to_sales_spreadsheet()
    state = preflight_sales_sheet(spreadsheet)
    writes = build_sales_sheet_writes(state, updates)
    result["writes"] = writes

    if not writes:
        return result

    apply_sales_sheet_writes(spreadsheet, writes, state=state)
    verify_sales_sheet_writes(spreadsheet, updates)

    result["applied"] = True
    return result


def main() -> None:
    args = build_parser().parse_args()

    if args.download:
        source = download_latest_upserve_monthly_report_with_source()
        report_path = Path(source["file_path"])
    else:
        report_path = (
            args.report
            if args.report is not None
            else find_latest_monthly_report(DEFAULT_REPORT_DIR)
        )

    result = run_monthly_sales(report_path, apply=args.apply)

    print(f"Report: {result['reporting_period']}")
    print(f"Pint/THC updates: {result['pint_updates']}")
    print(f"Can updates: {result['can_updates']}")

    if args.apply and not result["writes"]:
        print("No spreadsheet changes required.")
        print("Live preflight passed; all target cells already matched.")
        return

    if args.apply:
        print(f"Applied and verified: {len(result['writes'])} cells.")
        return

    print()
    print("DRY RUN ? proposed spreadsheet writes")
    print("=" * 60)

    for write in result["writes"]:
        print(
            f"{write['sheet']:>6} | "
            f"{write['cell']:<5} | "
            f"{write['label']:<25} | "
            f"{write['quantity']:>4}"
        )

    print("=" * 60)
    print(f"Total proposed writes: {len(result['writes'])}")
    print("NO SPREADSHEET CHANGES MADE.")

if __name__ == "__main__":
    main()




