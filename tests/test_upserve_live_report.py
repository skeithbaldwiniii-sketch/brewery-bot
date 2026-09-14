import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.upserve import get_latest_upserve_sales_report
from reports.upserve_report import format_upserve_sales_report


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — LIVE UPSERVE REPORT TEST")
    print("=" * 70)

    report = get_latest_upserve_sales_report()

    print()
    print(f"Reporting period: {report['reporting_period']}")
    print(f"Products found: {len(report['products'])}")
    print()

    formatted = format_upserve_sales_report(report)

    print(formatted)

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()