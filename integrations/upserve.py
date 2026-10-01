"""
Upserve POS report parsing.

Handles CSV reports exported by Upserve POS Reporting and extracts
weekly product sales for B - Full and C - Full categories.
"""

import csv
import re
from pathlib import Path

from integrations.gmail import (
    search_emails,
    get_email_attachments,
    download_email_attachment,
)

from knowledge.upserve import (
    is_report_processed,
    mark_report_processed,
)


TARGET_CATEGORIES = {"B - Full", "C - Full"}

MONTHLY_PINT_CATEGORIES = {"B - Full", "C - Full"}
MONTHLY_FOUR_PACK_CATEGORY = "B - 4 Pack"
MONTHLY_750ML_CATEGORY = "B - 750ml Bottle"
MONTHLY_THC_CATEGORY = "W - Wine Cocktails"


def normalize_category(value: str) -> str:
    """Normalize an Upserve category value for comparison."""
    return " ".join(value.strip().split())


def normalize_product_name(value: str) -> str:
    """Normalize whitespace around an Upserve product name."""
    return " ".join(value.strip().split())


def parse_sold(value: str) -> int:
    """Convert Upserve's Sold field to an integer."""
    value = value.strip()

    if not value:
        return 0

    return int(float(value))


def extract_reporting_period(file_path: str | Path) -> str | None:
    """
    Extract the reporting period from an Upserve report.

    Upserve reports contain the period in the second line of the CSV.

    Example:
        09-07-2026 to 09-13-2026
    """
    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8-sig") as csv_file:
        csv_file.readline()
        period = csv_file.readline().strip()

    if period:
        return period

    return None

def extract_monthly_reporting_period(file_path: str | Path) -> str | None:
    """Extract the reporting period from a monthly Upserve filename."""
    file_path = Path(file_path)

    match = re.search(
        r"(\d{4}-\d{2}-\d{2})-to-(\d{4}-\d{2}-\d{2})",
        file_path.name,
    )

    if not match:
        return None

    start_date, end_date = match.groups()

    start_date = (
        f"{start_date[5:7]}-{start_date[8:10]}-{start_date[0:4]}"
    )
    end_date = (
        f"{end_date[5:7]}-{end_date[8:10]}-{end_date[0:4]}"
    )

    return f"{start_date} to {end_date}"


def parse_upserve_sales_report(file_path: str | Path) -> dict:
    """
    Parse an Upserve Product Mix CSV report.

    Returns:
        {
            "reporting_period": str | None,
            "products": [
                {
                    "rank": int,
                    "product": str,
                    "sold": int,
                    "category": str,
                }
            ]
        }
    """

    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        # Upserve places two report metadata rows before the CSV header.
        csv_file.readline()
        csv_file.readline()

        reader = csv.DictReader(csv_file)

        required_columns = {
            "Type",
            "Name",
            "Sold",
            "Category Name",
        }

        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"Upserve report is missing required columns: "
                f"{sorted(missing)}"
            )

        products = []

        for row in reader:
            if row["Type"].strip() != "Item":
                continue

            category = normalize_category(row["Category Name"])

            if category not in TARGET_CATEGORIES:
                continue

            product = normalize_product_name(row["Name"])

            if not product:
                continue

            sold = parse_sold(row["Sold"])

            products.append(
                {
                    "product": product,
                    "sold": sold,
                    "category": category,
                }
            )

    products.sort(
        key=lambda item: item["sold"],
        reverse=True,
    )

    for rank, product in enumerate(products, start=1):
        product["rank"] = rank

    return {
        "reporting_period": extract_reporting_period(file_path),
        "products": products,
    }

def _rank_monthly_products(products: list[dict]) -> list[dict]:
    """Sort monthly sales descending and assign ranks."""
    products.sort(
        key=lambda item: item["sold"],
        reverse=True,
    )

    for rank, product in enumerate(products, start=1):
        product["rank"] = rank

    return products


def parse_upserve_monthly_sales_report(file_path: str | Path) -> dict:
    """
    Parse an Upserve monthly Product Mix CSV report.

    Returns independently ranked sales lists for:
      - pints
      - 4-packs
      - 750ml bottles
      - THC drinks
    """
    file_path = Path(file_path)

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        # Upserve places two report metadata rows before the CSV header.
        csv_file.readline()
        csv_file.readline()

        reader = csv.DictReader(csv_file)

        required_columns = {
            "Type",
            "Name",
            "Sold",
            "Category Name",
        }

        missing = required_columns - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"Upserve report is missing required columns: "
                f"{sorted(missing)}"
            )

        pint_sales = []
        four_pack_sales = []
        bottle_750ml_sales = []
        thc_sales = []

        for row in reader:
            if row["Type"].strip() != "Item":
                continue

            category = normalize_category(row["Category Name"])
            product = normalize_product_name(row["Name"])

            if not product:
                continue

            sold = parse_sold(row["Sold"])

            item = {
                "product": product,
                "sold": sold,
                "category": category,
            }

            if category in MONTHLY_PINT_CATEGORIES:
                pint_sales.append(item)

            elif category == MONTHLY_FOUR_PACK_CATEGORY:
                four_pack_sales.append(item)

            elif category == MONTHLY_750ML_CATEGORY:
                bottle_750ml_sales.append(item)

            elif (
                category == MONTHLY_THC_CATEGORY
                and "thc" in product.casefold()
            ):
                thc_sales.append(item)

        return {
            "reporting_period": extract_monthly_reporting_period(file_path),
            "pint_sales": _rank_monthly_products(pint_sales),
            "four_pack_sales": _rank_monthly_products(four_pack_sales),
            "bottle_750ml_sales": _rank_monthly_products(
                bottle_750ml_sales
            ),
            "thc_sales": _rank_monthly_products(thc_sales),
        }

def download_latest_upserve_report(output_dir="data/upserve"):
    """Find the latest Upserve CSV email and download its report."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    emails = search_emails(
        'has:attachment "Vanish Weekly Product Mix"',
        max_results=10,
    )

    if not emails:
        raise FileNotFoundError(
            "No Upserve Product Mix email was found."
        )

    for email in emails:
        attachments = get_email_attachments(email["id"])

        csv_attachments = [
            attachment
            for attachment in attachments
            if attachment["filename"].lower().endswith(".csv")
        ]

        if not csv_attachments:
            continue

        attachment = csv_attachments[0]

        data = download_email_attachment(
            email["id"],
            attachment["attachment_id"],
        )

        if not data:
            raise ValueError(
                f"Downloaded attachment is empty: "
                f"{attachment['filename']}"
            )

        file_path = output_path / attachment["filename"]
        file_path.write_bytes(data)

        return file_path

    raise FileNotFoundError(
        "No CSV attachment was found in the Upserve email."
    )

def download_latest_upserve_report_with_source(
    output_dir="data/upserve",
):
    """Download the latest Upserve report and return its source metadata."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    emails = search_emails(
        'has:attachment "Vanish Weekly Product Mix"',
        max_results=10,
    )

    if not emails:
        raise FileNotFoundError(
            "No Upserve Product Mix email was found."
        )

    for email in emails:
        attachments = get_email_attachments(email["id"])

        csv_attachments = [
            attachment
            for attachment in attachments
            if attachment["filename"].lower().endswith(".csv")
        ]

        if not csv_attachments:
            continue

        attachment = csv_attachments[0]

        data = download_email_attachment(
            email["id"],
            attachment["attachment_id"],
        )

        if not data:
            raise ValueError(
                f"Downloaded attachment is empty: "
                f"{attachment['filename']}"
            )

        file_path = output_path / attachment["filename"]
        file_path.write_bytes(data)

        return {
            "message_id": email["id"],
            "email_subject": email["subject"],
            "email_date": email["date"],
            "filename": attachment["filename"],
            "file_path": file_path,
        }

    raise FileNotFoundError(
        "No CSV attachment was found in the Upserve email."
    )

def download_latest_upserve_monthly_report_with_source(
    output_dir="data/upserve",
):
    """Download the latest Upserve monthly Product Mix CSV."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    emails = search_emails(
        'has:attachment',
        max_results=50,
    )

    emails = [
        email
        for email in emails
        if email["subject"].strip().startswith(
            "Vanish Monthly Product Mix CSV"
        )
    ]

    if not emails:
        raise FileNotFoundError(
            "No Upserve monthly Product Mix email was found."
        )

    emails.sort(
        key=lambda email: email.get("date", ""),
        reverse=True,
    )

    for email in emails:
        attachments = get_email_attachments(email["id"])

        csv_attachments = [
            attachment
            for attachment in attachments
            if attachment["filename"].lower().endswith(".csv")
        ]

        if not csv_attachments:
            continue

        attachment = csv_attachments[0]

        data = download_email_attachment(
            email["id"],
            attachment["attachment_id"],
        )

        if not data:
            raise ValueError(
                f"Downloaded attachment is empty: "
                f"{attachment['filename']}"
            )

        file_path = output_path / attachment["filename"]
        file_path.write_bytes(data)

        return {
            "message_id": email["id"],
            "email_subject": email["subject"],
            "email_date": email["date"],
            "filename": attachment["filename"],
            "file_path": file_path,
        }

    raise FileNotFoundError(
        "No CSV attachment was found in the Upserve monthly email."
    )

def get_latest_upserve_monthly_sales_report_with_source():
    """
    Download, parse, and return the latest Upserve monthly report
    with source metadata.
    """

    source = download_latest_upserve_monthly_report_with_source()

    report = parse_upserve_monthly_sales_report(source["file_path"])

    return {
        "message_id": source["message_id"],
        "email_subject": source["email_subject"],
        "email_date": source["email_date"],
        "filename": source["filename"],
        "file_path": source["file_path"],
        "report": report,
    }

def get_latest_upserve_sales_report():
    """Download and parse the latest Upserve sales report."""

    file_path = download_latest_upserve_report()

    return parse_upserve_sales_report(file_path)

def get_latest_upserve_sales_report_with_source():
    """Download, parse, and return the latest Upserve report with source metadata."""

    source = download_latest_upserve_report_with_source()

    report = parse_upserve_sales_report(source["file_path"])

    return {
        "message_id": source["message_id"],
        "email_subject": source["email_subject"],
        "email_date": source["email_date"],
        "filename": source["filename"],
        "file_path": source["file_path"],
        "report": report,
    }

def process_latest_upserve_report():
    """
    Process the latest Upserve report exactly once.

    Returns a status dictionary describing what happened.
    """

    source = get_latest_upserve_sales_report_with_source()

    message_id = source["message_id"]
    report = source["report"]

    if is_report_processed(message_id):
        return {
            "status": "already_processed",
            "message_id": message_id,
            "reporting_period": report["reporting_period"],
        }

    from reports.upserve_report import format_upserve_sales_report
    from integrations.slack import send_staff_message

    message = format_upserve_sales_report(report)

    response = send_staff_message(message)

    if not response.get("ok"):
        raise RuntimeError(
            "Slack failed to send the Upserve report."
        )

    mark_report_processed(
        message_id,
        report["reporting_period"],
    )

    return {
        "status": "processed",
        "message_id": message_id,
        "reporting_period": report["reporting_period"],
        "slack_timestamp": response.get("ts"),
    }

def process_latest_upserve_monthly_report():
    """
    Process the latest Upserve monthly report exactly once.

    Sends the report to both Slack and email before marking it
    as processed.
    """

    source = get_latest_upserve_monthly_sales_report_with_source()

    message_id = source["message_id"]
    report = source["report"]

    if is_report_processed(message_id):
        return {
            "status": "already_processed",
            "message_id": message_id,
            "reporting_period": report["reporting_period"],
        }

    from reports.upserve_monthly import (
        format_upserve_monthly_sales_report,
        format_upserve_monthly_sales_email,
    )
    from integrations.gmail import (
        get_gmail_address,
        send_email,
    )
    from integrations.slack import send_staff_message

    # Build both versions before sending anything.
    slack_message = format_upserve_monthly_sales_report(report)
    email_body = format_upserve_monthly_sales_email(report)

    send_email(
        to=get_gmail_address(),
        subject=(
            f"Upserve Monthly Sales — "
            f"{report['reporting_period']}"
        ),
        body=email_body,
    )

    slack_response = send_staff_message(slack_message)

    if not slack_response.get("ok"):
        raise RuntimeError(
            "Slack failed to send the Upserve monthly report."
        )

    # Only mark processed after both deliveries succeed.
    mark_report_processed(
        message_id,
        report["reporting_period"],
    )

    return {
        "status": "processed",
        "message_id": message_id,
        "reporting_period": report["reporting_period"],
        "slack_timestamp": slack_response.get("ts"),
    }