from integrations.google_sheets import get_column_a
from reports.daily_tasks import get_tasks_for_day
from reports.daily_report import build_daily_report
from integrations.slack import send_message


def main():
    # Get today's tasks from Google Sheets.
    column_a = get_column_a()
    tasks = get_tasks_for_day(column_a)

    # Build the daily report.
    report = build_daily_report(tasks)

    # Display the report locally.
    print()
    print(report)
    print()

    # Send the report to Slack.
    send_message(report)

    print("Daily report sent to Slack!")


if __name__ == "__main__":
    main()