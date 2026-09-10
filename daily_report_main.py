from datetime import date

from integrations.beer30 import (
    get_wip_report,
    get_fermentation_summary,
)
from integrations.google_sheets import get_column_a
from reports.daily_tasks import get_tasks_for_day
from reports.daily_report import build_daily_report
from reports.tank_status import format_tank_status
from integrations.slack import send_message



def main():
    # Get today's tasks from Google Sheets.
    column_a = get_column_a()
    tasks = get_tasks_for_day(column_a)

    # Get current Beer30 tank status.
    wip_records = get_wip_report(date.today().isoformat())
    fermentation_records = get_fermentation_summary()

    tank_status = format_tank_status(
        wip_records,
        fermentation_records,
    )

    # Build the daily report.
    report = build_daily_report(tasks, tank_status)

    # Display the report locally.
    print()
    print(report)
    print()

    # Send the report to Slack.
    send_message(report)

    print("Daily report sent to Slack!")


if __name__ == "__main__":
    main()