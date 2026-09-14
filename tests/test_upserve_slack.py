import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.upserve import get_latest_upserve_sales_report
from reports.upserve_report import format_upserve_sales_report
from integrations.slack import send_staff_message


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — UPSERVE SLACK TEST")
    print("=" * 70)

    report = get_latest_upserve_sales_report()

    message = format_upserve_sales_report(report)

    print()
    print(message)
    print()
    print("Sending report to staff channel...")

    response = send_staff_message(message)

    print()
    print("Slack response:")
    print(f"OK: {response.get('ok')}")
    print(f"Channel: {response.get('channel')}")
    print(f"Timestamp: {response.get('ts')}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()