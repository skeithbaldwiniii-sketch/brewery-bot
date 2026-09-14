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


TARGET_CATEGORIES = {"B - Full", "C - Full"}


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

def get_latest_upserve_sales_report():
    """Download and parse the latest Upserve sales report."""

    file_path = download_latest_upserve_report()

    return parse_upserve_sales_report(file_path)