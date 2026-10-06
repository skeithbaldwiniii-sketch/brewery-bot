"""Map parsed Upserve monthly sales reports to spreadsheet cell updates."""


from __future__ import annotations

import calendar
from datetime import datetime

def validate_monthly_reporting_period(
    reporting_period: str | None,
    expected_year: int | None = None,
    expected_month: int | None = None,
) -> None:
    """Reject missing, invalid, partial-month, or unexpected reporting periods."""
    if not reporting_period:
        raise ValueError("The report is missing its reporting period.")

    try:
        start_text, end_text = reporting_period.split(" to ")
        start_date = datetime.strptime(start_text, "%m-%d-%Y").date()
        end_date = datetime.strptime(end_text, "%m-%d-%Y").date()
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Invalid reporting period format: {reporting_period!r}. "
            "Expected MM-DD-YYYY to MM-DD-YYYY."
        ) from exc

    if start_date > end_date:
        raise ValueError("The reporting period starts after it ends.")

    if start_date.day != 1:
        raise ValueError("The reporting period must start on the first day of a month.")

    last_day = calendar.monthrange(end_date.year, end_date.month)[1]
    if (
        start_date.year != end_date.year
        or start_date.month != end_date.month
        or end_date.day != last_day
    ):
        raise ValueError(
            "The reporting period must cover one complete calendar month."
        )

    if expected_year is not None and start_date.year != expected_year:
        raise ValueError(
            f"Expected year {expected_year}, got {start_date.year}."
        )

    if expected_month is not None and start_date.month != expected_month:
        raise ValueError(
            f"Expected month {expected_month}, got {start_date.month}."
        )

def normalize_product_name(value: str | None) -> str:
    """Normalize product names for case-insensitive, whitespace-tolerant matching."""
    return " ".join((value or "").casefold().split())


def sales_by_names(products: list[dict], names: list[str]) -> int:
    """Sum sales for products whose names match any supplied alias."""
    wanted = {normalize_product_name(name) for name in names}
    return sum(
        int(product["sold"])
        for product in products
        if normalize_product_name(product.get("product")) in wanted
    )


# Each entry is (spreadsheet row, display label, Upserve product aliases).
PINT_MAPPING = [
    (6, "Beach Boys", ["Beach Boys"]),
    (7, "Electroplasm", ["Electroplasm"]),
    (8, "Fat Boys", ["Fat Boys"]),
    (10, "Ghost Fleet", ["Ghost Fleet"]),
    (11, "Hacienda", ["Hacienda"]),
    (12, "Into The Haze", ["Into the Haze"]),
    (13, "Lucketts Light", ["Lucketts Light"]),
    (14, "River Run", ["River Run"]),
    (15, "Snowbird", ["Snowbird"]),
    (16, "Strawberry Blonde", ["Strawberry Blonde"]),
    (17, "Wraith", ["Wraith"]),
    (18, "Wrexham Red", ["Wrexham Red"]),
    (19, "Super Juice", ["Super Juice"]),
    (20, "Bloom", ["Bloom"]),
    (21, "Midnight City", ["Midnight City Cider"]),
    (22, "Anti Hero", ["Anti Hero"]),
    (23, "Irish Coffee Stout", ["Irish Coffee Stout"]),
    (24, "Wajito", ["Wajito"]),
    (25, "Bingo Bango", ["Bingo Bango Mango Cider"]),
    (26, "Drift", ["Drift"]),
    (27, "Wander", ["Wander"]),
    (28, "ofest", ["O'Fest", "Oktober"]),
    (29, "pumpkin chai", ["Pumpkin Chai"]),
    (30, "tickled pink", ["Tickled Pink"]),
    (32, "darkness", ["Darkness"]),
    (33, "Very Berry Seltzer", ["Very Berry Seltzer"]),
    (34, "peach mimosa", ["Peach Mimosa THC"]),
    (35, "summer breeze", ["Summer Breeze"]),
    (36, "Nitro Cold brew", ["Nitro Cold Brew"]),
    (37, "sunchaser", ["Sun Chaser"]),
    (38, "Fields Of Gold", ["Fields Of Gold"]),
]

CAN_MAPPING = [
    (6, "Beach Boys", ["Beach Boys 4-Pack"]),
    (7, "Electroplasm", ["Electroplasm 4 pack"]),
    (8, "Ghost Fleet", ["Ghost Fleet 4 pack"]),
    (9, "Hacienda", ["Hacienda 6 Pack"]),
    (10, "Into The Haze", ["Into the Haze 4 pack"]),
    (11, "Lucketts Light", ["Lucketts Store Light 6 Pack"]),
    (13, "Strawberry Blonde", ["Strawberry Blond 4 pack"]),
    (14, "Wrexham Red", ["Wrexham Red 4-Pack"]),
    (15, "Super Juice", ["Super Juice 4 pack"]),
    (16, "Midnight City", ["Midnight City 4 Pack"]),
    (17, "Bingo Bango", ["Bingo Bango Mango 4-pack"]),
    (18, "Drift", ["Drift 4 Pack"]),
    (19, "ofest", ["Oktoberfest 6 pack"]),
]

RIVER_RUN_BOTTLE_ALIASES = [
    "River Run Bottle",
    "River Run Dubai",
    "River Run Manhattan",
]

EXCLUDED_PINT_NAMES = {
    normalize_product_name("Pride Brew"),
    normalize_product_name("La Hacienda"),
}
EXCLUDED_PACKAGED_NAMES = {
    normalize_product_name("Mixed 4-Pack"),
    normalize_product_name("Vanish Cross"),
}


def build_sales_sheet_updates(report: dict) -> dict:
    """Build proposed spreadsheet updates without connecting to any services.

    Returns row/label/quantity tuples for the 2026 pint-sales column and
    the Cans packaged-sales column. Peach Mimosa THC is mapped to the 2026
    tab because it competes with pint sales. River Run bottle variants are
    combined into the Cans tab's River Run row.
    """
    pints = report.get("pint_sales", [])
    packs = report.get("four_pack_sales", [])
    bottles = report.get("bottle_750ml_sales", [])
    thc = report.get("thc_sales", [])

    pint_updates = []
    for row, label, aliases in PINT_MAPPING:
        products = thc if row == 34 else pints
        sold = sales_by_names(products, aliases)
        if sold:
            pint_updates.append((row, label, sold))

    can_updates = []
    for row, label, aliases in CAN_MAPPING:
        sold = sales_by_names(packs, aliases)
        if sold:
            can_updates.append((row, label, sold))

    river_run_bottles = sales_by_names(bottles, RIVER_RUN_BOTTLE_ALIASES)
    if river_run_bottles:
        can_updates.append((12, "River Run (750 ml bottles)", river_run_bottles))

    return {
        "reporting_period": report.get("reporting_period"),
        "pint_updates": pint_updates,
        "can_updates": can_updates,
        "excluded_pints": [
            product for product in pints
            if normalize_product_name(product.get("product")).startswith("n/a beer")
            or normalize_product_name(product.get("product")) in EXCLUDED_PINT_NAMES
        ],
        "excluded_packaged": [
            product for product in packs
            if normalize_product_name(product.get("product")) in EXCLUDED_PACKAGED_NAMES
        ],
        "unmapped_bottles": [
            product for product in bottles
            if normalize_product_name(product.get("product"))
            not in {normalize_product_name(name) for name in RIVER_RUN_BOTTLE_ALIASES}
        ],
        "excluded_thc": [
            product for product in thc
            if normalize_product_name(product.get("product"))
            != normalize_product_name("Peach Mimosa THC")
        ],
    }

def validate_sales_sheet_updates(updates: dict) -> None:
    """Validate proposed updates before any spreadsheet write is attempted."""
    destinations = set()

    protected_destinations = {
        ("2026", 9),  # Fire: discontinued; leave September blank.
    }

    update_groups = [
        ("2026", updates.get("pint_updates", [])),
        ("Cans", updates.get("can_updates", [])),
    ]

    for sheet_name, entries in update_groups:
        for row, label, sold in entries:
            destination = (sheet_name, row)

            if destination in destinations:
                raise ValueError(
                    f"Duplicate destination: {sheet_name}!row {row}."
                )
            destinations.add(destination)

            if destination in protected_destinations:
                raise ValueError(
                    f"Protected destination cannot be updated: "
                    f"{sheet_name}!row {row} ({label})."
                )

            if isinstance(sold, bool) or not isinstance(sold, int) or sold < 0:
                raise ValueError(
                    f"Invalid sales quantity for {sheet_name}!row {row} "
                    f"({label}): {sold!r}. Expected a nonnegative integer."
                )