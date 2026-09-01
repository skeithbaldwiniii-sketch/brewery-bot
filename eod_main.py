from reports.eod_report import build_eod_report
from integrations.slack import send_message


def main():
    report = build_eod_report()

    print()
    print(report)
    print()

    send_message(report)

    print("End-of-day report sent to Slack!")


if __name__ == "__main__":
    main()
