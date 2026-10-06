from reports.sales_sheet_mapping import (
    build_sales_sheet_updates,
    normalize_product_name,
    sales_by_names,
)


def test_normalize_product_name_ignores_case_and_extra_whitespace():
    assert normalize_product_name("  River   Run Manhattan ") == "river run manhattan"


def test_sales_by_names_sums_matching_aliases():
    products = [
        {"product": "O'Fest", "sold": 653},
        {"product": "Oktober", "sold": 64},
        {"product": "Other Beer", "sold": 10},
    ]

    assert sales_by_names(products, ["O'Fest", "Oktober"]) == 717


def test_build_sales_sheet_updates_routes_peach_mimosa_to_pint_tab():
    report = {
        "reporting_period": "09-01-2026 to 09-30-2026",
        "pint_sales": [{"product": "Ghost Fleet", "sold": 527}],
        "four_pack_sales": [],
        "bottle_750ml_sales": [],
        "thc_sales": [{"product": "Peach Mimosa THC", "sold": 86}],
    }

    result = build_sales_sheet_updates(report)

    assert (10, "Ghost Fleet", 527) in result["pint_updates"]
    assert (34, "peach mimosa", 86) in result["pint_updates"]
    assert result["can_updates"] == []


def test_build_sales_sheet_combines_river_run_bottle_variants():
    report = {
        "pint_sales": [],
        "four_pack_sales": [],
        "bottle_750ml_sales": [
            {"product": "River Run Bottle", "sold": 17},
            {"product": "River Run Dubai", "sold": 11},
            {"product": "River Run Manhattan", "sold": 12},
            {"product": "Celebration Cider", "sold": 3},
        ],
        "thc_sales": [],
    }

    result = build_sales_sheet_updates(report)

    assert (12, "River Run (750 ml bottles)", 40) in result["can_updates"]
    assert [p["product"] for p in result["unmapped_bottles"]] == [
        "Celebration Cider"
    ]


def test_build_sales_sheet_reports_excluded_products():
    report = {
        "pint_sales": [
            {"product": "N/A Beer Golden", "sold": 62},
            {"product": "Pride Brew", "sold": 25},
            {"product": "Ghost Fleet", "sold": 527},
        ],
        "four_pack_sales": [
            {"product": "Mixed 4-Pack", "sold": 13},
            {"product": "Vanish Cross", "sold": 8},
        ],
        "bottle_750ml_sales": [],
        "thc_sales": [
            {"product": "Peach Mimosa THC", "sold": 86},
            {"product": "Buzzin Breeze THC", "sold": 33},
        ],
    }

    result = build_sales_sheet_updates(report)

    assert {p["product"] for p in result["excluded_pints"]} == {
        "N/A Beer Golden",
        "Pride Brew",
    }
    assert {p["product"] for p in result["excluded_packaged"]} == {
        "Mixed 4-Pack",
        "Vanish Cross",
    }
    assert [p["product"] for p in result["excluded_thc"]] == [
        "Buzzin Breeze THC"
    ]
