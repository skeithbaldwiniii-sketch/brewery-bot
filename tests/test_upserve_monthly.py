from pathlib import Path

from integrations.upserve import parse_upserve_monthly_sales_report


REPORT = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "upserve"
    / "pmix-report--2026-09-01-to-2026-09-30--vanish-brewery.csv"
)


def test_monthly_report_parses_reporting_period():
    report = parse_upserve_monthly_sales_report(REPORT)

    assert report["reporting_period"] == "09-01-2026 to 09-30-2026"


def test_monthly_pint_sales_are_ranked():
    report = parse_upserve_monthly_sales_report(REPORT)

    products = report["pint_sales"]

    assert len(products) == 28

    assert products[0]["rank"] == 1
    assert products[0]["product"] == "O'Fest"
    assert products[0]["sold"] == 653

    assert products[1]["rank"] == 2
    assert products[1]["product"] == "Ghost Fleet"
    assert products[1]["sold"] == 527

    assert products[2]["rank"] == 3
    assert products[2]["product"] == "Lucketts Light"
    assert products[2]["sold"] == 525

    assert all(
        products[index]["sold"] >= products[index + 1]["sold"]
        for index in range(len(products) - 1)
    )


def test_monthly_four_pack_sales_are_ranked():
    report = parse_upserve_monthly_sales_report(REPORT)

    products = report["four_pack_sales"]

    assert len(products) == 15

    assert products[0]["product"] == "Electroplasm 4 pack"
    assert products[0]["sold"] == 55

    assert products[1]["product"] == "Oktoberfest 6 pack"
    assert products[1]["sold"] == 53

    assert all(
        products[index]["sold"] >= products[index + 1]["sold"]
        for index in range(len(products) - 1)
    )


def test_monthly_750ml_sales_are_ranked():
    report = parse_upserve_monthly_sales_report(REPORT)

    products = report["bottle_750ml_sales"]

    assert len(products) == 6

    assert products[0]["product"] == "River Run Bottle"
    assert products[0]["sold"] == 17

    assert products[1]["product"] == "River Run Dubai"
    assert products[1]["sold"] == 12

    assert products[2]["product"] == "River Run Manhattan"
    assert products[2]["sold"] == 11

    assert all(
        products[index]["sold"] >= products[index + 1]["sold"]
        for index in range(len(products) - 1)
    )


def test_monthly_thc_sales_only_include_thc_products():
    report = parse_upserve_monthly_sales_report(REPORT)

    products = report["thc_sales"]

    assert len(products) == 4

    assert products[0]["product"] == "Peach Mimosa THC"
    assert products[0]["sold"] == 86

    assert products[1]["product"] == "Buzzin Breeze THC"
    assert products[1]["sold"] == 33

    assert products[2]["product"] == "Cheat Code Paloma THC"
    assert products[2]["sold"] == 23

    assert products[3]["product"] == "High Fashioned THC"
    assert products[3]["sold"] == 12

    assert all(
        "thc" in product["product"].casefold()
        for product in products
    )

    assert all(
        product["category"] == "W - Wine Cocktails"
        for product in products
    )


def test_monthly_rankings_are_independent():
    report = parse_upserve_monthly_sales_report(REPORT)

    assert report["pint_sales"][0]["rank"] == 1
    assert report["four_pack_sales"][0]["rank"] == 1
    assert report["bottle_750ml_sales"][0]["rank"] == 1
    assert report["thc_sales"][0]["rank"] == 1