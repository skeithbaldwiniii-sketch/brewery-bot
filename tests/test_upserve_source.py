import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.upserve import (
    get_latest_upserve_sales_report_with_source,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN ΓÇö UPSERVE SOURCE TEST")
    print("=" * 70)

    result = get_latest_upserve_sales_report_with_source()

    print()
    print(f"Message ID: {result['message_id']}")
    print(f"Subject: {result['email_subject']}")
    print(f"Email date: {result['email_date']}")
    print(f"Filename: {result['filename']}")
    print(f"File path: {result['file_path']}")
    print(
        f"Reporting period: "
        f"{result['report']['reporting_period']}"
    )
    print(
        f"Products: "
        f"{len(result['report']['products'])}"
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
