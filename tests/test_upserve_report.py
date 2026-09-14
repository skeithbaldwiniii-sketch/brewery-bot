from pathlib import Path

from integrations.upserve import parse_upserve_sales_report
from reports.upserve_report import (
    format_upserve_sales_report,
    generate_upserve_sales_report,
)

REPORT = (
    Path(__file__).resolve().parent
    / "pmix-report--2026-09-07-to-2026-09-13--vanish-brewery.csv"
)


def test_upserve_report_format():
    report = {
        "reporting_period": "09-07-2026 to 09-13-2026",
        "products": [
            {
                "rank": 1,
                "product": "O'Fest",
                "sold": 168,
                "category": "B - Full",
            },
            {
                "rank": 2,
                "product": "Ghost Fleet",
                "sold": 167,
                "category": "B - Full",
            },
            {
                "rank": 3,
                "product": "Bingo Bango Mango Cider",
                "sold": 82,
                "category": "C - Full",
            },
        ],
    }

    result = format_upserve_sales_report(report)

    assert "*Upserve Weekly Sales*" in result
    assert "09-07-2026 to 09-13-2026" in result
    assert "*B - Full / C - Full Sales*" in result

    assert "1. O'Fest — 168" in result
    assert "2. Ghost Fleet — 167" in result
    assert "3. Bingo Bango Mango Cider — 82" in result


def test_upserve_report_handles_variable_number_of_products():
    report = {
        "reporting_period": "09-14-2026 to 09-20-2026",
        "products": [
            {
                "rank": 1,
                "product": "Example Beer",
                "sold": 100,
                "category": "B - Full",
            },
            {
                "rank": 2,
                "product": "Example Cider",
                "sold": 50,
                "category": "C - Full",
            },
        ],
    }

    result = format_upserve_sales_report(report)

    assert "1. Example Beer — 100" in result
    assert "2. Example Cider — 50" in result
    assert "3." not in result


def test_upserve_report_handles_no_products():
    report = {
        "reporting_period": "09-21-2026 to 09-27-2026",
        "products": [],
    }

    result = format_upserve_sales_report(report)

    assert "*Upserve Weekly Sales*" in result
    assert "09-21-2026 to 09-27-2026" in result
    assert "No B - Full or C - Full products" in result


def test_real_upserve_report_formats_correctly():
    report = parse_upserve_sales_report(REPORT)
    result = format_upserve_sales_report(report)

    assert "O'Fest" in result
    assert "168" in result

    assert "Ghost Fleet" in result
    assert "167" in result

    assert "Wrexham Red" in result
    assert "6" in result

    assert "25. Wrexham Red — 6" in result

    assert result.index("O'Fest") < result.index("Ghost Fleet")
    assert result.index("Ghost Fleet") < result.index("Wrexham Red")


def test_generate_upserve_sales_report():
    result = generate_upserve_sales_report(REPORT)

    assert "*Upserve Weekly Sales*" in result
    assert "09-07-2026 to 09-13-2026" in result

    assert "1. O'Fest — 168" in result
    assert "2. Ghost Fleet — 167" in result
    assert "25. Wrexham Red — 6" in result