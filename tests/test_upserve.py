from pathlib import Path

from integrations.upserve import parse_upserve_sales_report


REPORT = (
    Path(__file__).resolve().parent
    / "pmix-report--2026-09-07-to-2026-09-13--vanish-brewery.csv"
)


def test_upserve_report_parses():
    report = parse_upserve_sales_report(REPORT)

    assert report["reporting_period"] == "09-07-2026 to 09-13-2026"

    products = report["products"]

    assert len(products) == 25


def test_upserve_report_is_ranked_by_sales():
    report = parse_upserve_sales_report(REPORT)

    products = report["products"]

    assert products[0]["rank"] == 1
    assert products[0]["product"] == "O'Fest"
    assert products[0]["sold"] == 168

    assert products[1]["rank"] == 2
    assert products[1]["product"] == "Ghost Fleet"
    assert products[1]["sold"] == 167


def test_upserve_report_contains_only_target_categories():
    report = parse_upserve_sales_report(REPORT)

    products = report["products"]

    categories = {product["category"] for product in products}

    assert categories == {"B - Full", "C - Full"}


def test_upserve_category_whitespace_is_normalized():
    report = parse_upserve_sales_report(REPORT)

    products = report["products"]

    assert all(
        product["category"] in {"B - Full", "C - Full"}
        for product in products
    )


def test_upserve_product_names_are_normalized():
    report = parse_upserve_sales_report(REPORT)

    products = report["products"]

    names = {product["product"] for product in products}

    assert "Beach Boys" in names
    assert "N/A Beer Golden" in names
    assert "Wajito" in names
    assert "N/A Beer Free Wave" in names


def test_upserve_last_rank():
    report = parse_upserve_sales_report(REPORT)

    products = report["products"]

    assert products[-1]["rank"] == 25
    assert products[-1]["product"] == "Wrexham Red"
    assert products[-1]["sold"] == 6
def test_download_latest_upserve_monthly_report_with_source(tmp_path):
    from unittest.mock import patch

    from integrations.upserve import (
        download_latest_upserve_monthly_report_with_source,
    )

    emails = [
        {
            "id": "monthly-1",
            "subject": "Vanish Monthly Product Mix CSV - September 2026",
            "date": "Wed, 01 Oct 2026 09:00:00 -0400",
        }
    ]

    attachments = [
        {
            "filename": "september.csv",
            "mime_type": "text/csv",
            "attachment_id": "attachment-1",
            "size": 123,
        }
    ]

    with (
        patch(
            "integrations.upserve.search_emails",
            return_value=emails,
        ),
        patch(
            "integrations.upserve.get_email_attachments",
            return_value=attachments,
        ),
        patch(
            "integrations.upserve.download_email_attachment",
            return_value=b"test,csv\n",
        ),
    ):
        result = download_latest_upserve_monthly_report_with_source(
            output_dir=tmp_path,
        )

    assert result["message_id"] == "monthly-1"
    assert result["email_subject"] == emails[0]["subject"]
    assert result["filename"] == "september.csv"
    assert result["file_path"].read_bytes() == b"test,csv\n"

def test_download_latest_upserve_monthly_skips_email_without_csv(tmp_path):
    from unittest.mock import patch

    from integrations.upserve import (
        download_latest_upserve_monthly_report_with_source,
    )

    emails = [
        {
            "id": "monthly-newer",
            "subject": "Vanish Monthly Product Mix CSV - October 2026",
            "date": "Mon, 02 Nov 2026 09:00:00 -0400",
        },
        {
            "id": "monthly-older",
            "subject": "Vanish Monthly Product Mix CSV - September 2026",
            "date": "Thu, 01 Oct 2026 09:00:00 -0400",
        },
    ]

    attachments_by_message = {
        "monthly-newer": [],
        "monthly-older": [
            {
                "filename": "september.csv",
                "mime_type": "text/csv",
                "attachment_id": "attachment-1",
                "size": 123,
            }
        ],
    }

    def get_attachments(message_id):
        return attachments_by_message[message_id]

    with (
        patch(
            "integrations.upserve.search_emails",
            return_value=emails,
        ),
        patch(
            "integrations.upserve.get_email_attachments",
            side_effect=get_attachments,
        ),
        patch(
            "integrations.upserve.download_email_attachment",
            return_value=b"test,csv\n",
        ),
    ):
        result = download_latest_upserve_monthly_report_with_source(
            output_dir=tmp_path,
        )

    assert result["message_id"] == "monthly-older"
    assert result["filename"] == "september.csv"
    assert result["file_path"].read_bytes() == b"test,csv\n"

def test_download_latest_upserve_monthly_rejects_empty_csv(tmp_path):
    import pytest
    from unittest.mock import patch

    from integrations.upserve import (
        download_latest_upserve_monthly_report_with_source,
    )

    emails = [
        {
            "id": "monthly-1",
            "subject": "Vanish Monthly Product Mix CSV - September 2026",
            "date": "Wed, 01 Oct 2026 09:00:00 -0400",
        }
    ]

    attachments = [
        {
            "filename": "september.csv",
            "mime_type": "text/csv",
            "attachment_id": "attachment-1",
            "size": 0,
        }
    ]

    with (
        patch(
            "integrations.upserve.search_emails",
            return_value=emails,
        ),
        patch(
            "integrations.upserve.get_email_attachments",
            return_value=attachments,
        ),
        patch(
            "integrations.upserve.download_email_attachment",
            return_value=b"",
        ),
    ):
        with pytest.raises(
            ValueError,
            match="Downloaded attachment is empty",
        ):
            download_latest_upserve_monthly_report_with_source(
                output_dir=tmp_path,
            )
