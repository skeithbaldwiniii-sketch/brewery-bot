from pathlib import Path

from integrations.upserve import parse_upserve_sales_report


REPORT = Path(
    r"C:\Users\skb3i\OneDrive\Desktop\brewery_bot"
    r"\pmix-report--2026-09-07-to-2026-09-13--vanish-brewery.csv"
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