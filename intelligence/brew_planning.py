"""
Brew feasibility and recipe planning intelligence.

This module converts Beer30's wide recipe export into a normalized
representation suitable for brew-planning calculations.
"""

import re
from collections import defaultdict
from typing import Any

from integrations.beer30 import (
    _export_data,
    get_inventory,
    get_inventory_lots,
)
RECIPE_EXPORT_NAME = "TableExportWithCustomFields"

# Beer30 recipe slots.
GRAIN_SLOTS = range(1, 17)
BOIL_HOP_SLOTS = range(1, 13)
FIRST_WORT_HOP_SLOTS = range(1, 4)
WHIRLPOOL_HOP_SLOTS = range(1, 11)
ACTIVE_FERM_HOP_SLOTS = range(1, 4)
DRY_HOP_SLOTS = range(1, 11)
ADJUNCT_SLOTS = range(1, 11)


def _to_float(value: Any) -> float:
    """Safely convert a Beer30 numeric value to float."""
    if value is None or value == "":
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def _canonical_unit(
    unit: Any,
    *,
    category: str,
) -> str:
    """
    Return the canonical comparison unit for a recipe/inventory item.

    Beer30 recipe grain units may be blank, while live grain inventory
    reports pounds. Hop recipes may report ounces while live inventory
    reports pounds.
    """
    clean_unit = str(unit or "").strip().lower()

    if category == "grain":
        return "lb" if not clean_unit else clean_unit

    if category == "hop":
        if clean_unit in {"oz", "ounce", "ounces"}:
            return "lb"
        return clean_unit

    return clean_unit

def normalize_inventory(
    inventory_response: dict[str, Any],
    category: str,
) -> list[dict[str, Any]]:
    """
    Normalize a Beer30 live inventory response.

    Beer30 returns inventory records under the ``inventory`` key.
    Grains and hops expose QuantityInStock directly. Adjuncts may
    expose the item catalog without a current quantity, so those
    records are represented with ``quantity=None``.
    """
    records = inventory_response.get("inventory", [])
    normalized: list[dict[str, Any]] = []

    name_fields = {
        "grain": "GrainName",
        "hop": "HopsName",
        "adjunct": "AdjunctsName",
    }

    name_field = name_fields.get(category)
    if not name_field:
        raise ValueError(f"Unsupported inventory category: {category}")

    for record in records:
        name = str(record.get(name_field) or "").strip()

        if not name:
            continue

        quantity_value = record.get("QuantityInStock")

        raw_unit = str(
            record.get("WeightUnits")
            or record.get("MeasurementUnits")
            or ""
        ).strip()

        quantity = (
            _to_float(quantity_value)
            if quantity_value is not None
            else None
        )

        unit = _canonical_unit(raw_unit, category=category)

        if (
            category == "hop"
            and quantity is not None
            and raw_unit.lower() in {"oz", "ounce", "ounces"}
        ):
            quantity /= 16

        normalized.append(
            {
                "name": name,
                "normalized_name": _normalize_name(name),
                "category": category,
                "quantity": quantity,
                "unit": unit,
                "archived": str(
                    record.get("Archived") or "0"
                ).strip() == "1",
                "inventory_known": quantity_value is not None,
                "history_unique": record.get("historyUnique"),
            }
        )

    return normalized

def get_adjunct_inventory(
    requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Retrieve current Beer30 inventory for adjuncts required by a brew plan.

    Beer30's adjunct inventory endpoint provides the item catalog but does
    not provide current quantities. Current quantities are calculated from
    the item's active lots:

        available = AddAmount - TotalDepleted

    Only adjuncts actually required by the brew plan are queried to avoid
    unnecessary Beer30 API requests.
    """
    required_adjuncts = {
        _normalize_name(requirement["name"])
        for requirement in requirements
        if requirement["category"] == "adjunct"
    }

    if not required_adjuncts:
        return []

    master_response = get_inventory("adjuncts")
    master_inventory = normalize_inventory(
        master_response,
        "adjunct",
    )

    normalized: list[dict[str, Any]] = []

    for item in master_inventory:
        if item["normalized_name"] not in required_adjuncts:
            continue

        item_id = item.get("history_unique")

        if not item_id:
            normalized.append(
                {
                    **item,
                    "quantity": None,
                    "inventory_known": False,
                }
            )
            continue

        try:
            lots_response = get_inventory_lots(
                "adjuncts",
                str(item_id),
            )
        except Exception:
            normalized.append(
                {
                    **item,
                    "quantity": None,
                    "inventory_known": False,
                }
            )
            continue

        lots = lots_response.get("inventory", [])

        available_quantity = 0.0
        unit = item["unit"]

        for lot in lots:
            if str(lot.get("Archived") or "0").strip() == "1":
                continue

            add_amount = lot.get("AddAmount")
            total_depleted = lot.get("TotalDepleted")

            if add_amount is None:
                continue

            available_quantity += (
                _to_float(add_amount)
                - _to_float(total_depleted)
            )

            lot_unit = str(
                lot.get("MeasurementUnits") or ""
            ).strip()

            if lot_unit:
                unit = _canonical_unit(
                    lot_unit,
                    category="adjunct",
                )

        normalized.append(
            {
                "name": item["name"],
                "normalized_name": item["normalized_name"],
                "category": "adjunct",
                "quantity": max(available_quantity, 0.0),
                "unit": unit,
                "archived": False,
                "inventory_known": True,
                "history_unique": item_id,
            }
        )

    return normalized

def _normalize_name(value: str | None) -> str:
    """
    Normalize a beer or ingredient name for comparison.

    This intentionally does not perform fuzzy matching. It only
    handles capitalization, whitespace, and punctuation that should
    not materially affect an inventory/recipe lookup.
    """
    if not value:
        return ""

    normalized = value.lower().strip()
    normalized = normalized.replace("’", "'")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()

def parse_brew_request(question: str) -> dict[str, Any]:
    """
    Parse a natural-language request to brew one or more beers.

    This parser extracts the beer names from common brew-planning
    phrasing. It intentionally does not validate the names against
    Beer30; recipe validation happens later in the feasibility engine.
    """
    if not question or not question.strip():
        return {
            "is_brew_request": False,
            "beers": [],
        }

    text = question.strip()

    brew_match = re.search(
        r"\b(?:brew|brewing|make)\b",
        text,
        flags=re.IGNORECASE,
    )

    if not brew_match:
        return {
            "is_brew_request": False,
            "beers": [],
        }

    beer_text = text[brew_match.end():].strip()

    # Remove common conversational lead-ins that can occur after
    # the brew verb.
    beer_text = re.sub(
        r"^(?:a|an|some|beer)\s+",
        "",
        beer_text,
        flags=re.IGNORECASE,
    )

    # Remove common trailing question/punctuation characters.
    beer_text = re.sub(
        r"[?.!]+$",
        "",
        beer_text,
    ).strip()

    if not beer_text:
        return {
            "is_brew_request": True,
            "beers": [],
        }

    # Treat commas, ampersands, and conjunctions as beer separators.
    parts = re.split(
        r"\s*(?:,|&|\band\b)\s*",
        beer_text,
        flags=re.IGNORECASE,
    )

    beers: list[str] = []

    for part in parts:
        beer = part.strip(" \t\r\n.,!?")

        beer = re.sub(
            r"^beer\s+",
            "",
            beer,
            flags=re.IGNORECASE,
        ).strip()

        if beer:
            beers.append(beer)

    return {
        "is_brew_request": True,
        "beers": beers,
    }


def _recipe_base_name(brand_name: str | None) -> str:
    """
    Remove Beer30's batch-size suffix from a recipe name.

    Examples:
        'Fire IPA (10.00)' -> 'Fire IPA'
        'Fire IPA (30.00)' -> 'Fire IPA'
        'Holy Mole (5.00)' -> 'Holy Mole'
    """
    if not brand_name:
        return ""

    return re.sub(
        r"\s*\(\s*\d+(?:\.\d+)?\s*\)\s*$",
        "",
        brand_name,
    ).strip()


def _version_number(row: dict[str, Any]) -> int:
    """Return a recipe version as an integer for sorting."""
    try:
        return int(row.get("Version") or 0)
    except (TypeError, ValueError):
        return 0


def _is_active_recipe(row: dict[str, Any]) -> bool:
    """Return whether Beer30 considers a recipe active."""
    return str(row.get("LiveStatus") or "").strip().lower() == "active"


def _add_ingredient(
    ingredients: list[dict[str, Any]],
    *,
    name: Any,
    quantity: Any,
    unit: Any,
    category: str,
    process: str | None = None,
) -> None:
    """Append a normalized ingredient when it has a usable quantity."""
    clean_name = str(name or "").strip()
    clean_quantity = _to_float(quantity)
    clean_unit = _canonical_unit(unit, category=category)

    if category == "hop" and str(unit or "").strip().lower() in {
        "oz",
        "ounce",
        "ounces",
    }:
        clean_quantity /= 16

    if not clean_name or clean_quantity <= 0:
        return

    ingredient = {
        "name": clean_name,
        "category": category,
        "quantity": clean_quantity,
        "unit": clean_unit,
    }

    if process:
        ingredient["process"] = process

    ingredients.append(ingredient)


def normalize_recipe(row: dict[str, Any]) -> dict[str, Any]:
    """
    Convert one Beer30 recipe export row into a normalized recipe.
    """
    ingredients: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # GRAINS
    # ---------------------------------------------------------

    for slot in GRAIN_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"grain{slot}Name"),
            quantity=row.get(f"grain{slot}Quantity"),
            unit=row.get(f"grain{slot}Units")
            or row.get("GrainSelectUnits"),
            category="grain",
        )

    # ---------------------------------------------------------
    # BOIL HOPS
    # ---------------------------------------------------------

    for slot in BOIL_HOP_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"hops{slot}Name"),
            quantity=row.get(f"hops{slot}Quantity"),
            unit=row.get("BoilHopsSelectUnits"),
            category="hop",
            process="boil",
        )

    # ---------------------------------------------------------
    # FIRST WORT HOPS
    # ---------------------------------------------------------

    for slot in FIRST_WORT_HOP_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"FirstWortHops{slot}Name"),
            quantity=row.get(f"FirstWortHops{slot}Quantity"),
            unit=row.get("FirstWortHopsSelectUnits"),
            category="hop",
            process="first_wort",
        )

    # ---------------------------------------------------------
    # WHIRLPOOL HOPS
    # ---------------------------------------------------------

    for slot in WHIRLPOOL_HOP_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"whirlpoolHops{slot}Name"),
            quantity=row.get(f"whirlpoolHops{slot}Quantity"),
            unit=row.get("WhirlpoolHopsSelectUnits"),
            category="hop",
            process="whirlpool",
        )

    # ---------------------------------------------------------
    # ACTIVE FERMENTATION HOPS
    # ---------------------------------------------------------

    for slot in ACTIVE_FERM_HOP_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"activeFermHops{slot}Name"),
            quantity=row.get(f"activeFermHops{slot}Quantity"),
            unit=row.get("ActiveFermentationHopsSelectUnits"),
            category="hop",
            process="active_fermentation",
        )

    # ---------------------------------------------------------
    # DRY HOPS
    # ---------------------------------------------------------

    for slot in DRY_HOP_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"dryHops{slot}Name"),
            quantity=row.get(f"dryHops{slot}Quantity"),
            unit=row.get("DryHopsSelectUnits"),
            category="hop",
            process="dry_hop",
        )

    # ---------------------------------------------------------
    # ADJUNCTS
    # ---------------------------------------------------------

    for slot in ADJUNCT_SLOTS:
        _add_ingredient(
            ingredients,
            name=row.get(f"adjuncts{slot}Name"),
            quantity=row.get(f"adjuncts{slot}Amount"),
            unit=row.get(f"adjuncts{slot}Units"),
            category="adjunct",
        )

    return {
        "recipe_name": str(row.get("brandName") or "").strip(),
        "base_name": _recipe_base_name(row.get("brandName")),
        "normalized_name": _normalize_name(
            _recipe_base_name(row.get("brandName"))
        ),
        "unique_number": row.get("uniqueNumber"),
        "version": _version_number(row),
        "live_status": str(row.get("LiveStatus") or "").strip(),
        "batch_size": _to_float(row.get("batchSize")),
        "created_at": row.get("RecipeCreationDateTime"),
        "ingredients": ingredients,
    }

def compare_inventory(
    requirements: list[dict[str, Any]],
    inventory: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Compare combined recipe requirements against normalized inventory.

    Archived inventory is ignored. Inventory with an unknown quantity
    is reported as ``unknown`` rather than being treated as zero.
    """
    available: dict[tuple[str, str, str], float] = {}
    unknown: set[tuple[str, str, str]] = set()

    for item in inventory:
        if item["archived"]:
            continue

        key = (
            item["normalized_name"],
            item["category"],
            item["unit"].lower(),
        )

        if not item["inventory_known"]:
            unknown.add(key)
            continue

        available[key] = available.get(key, 0.0) + item["quantity"]

    results: list[dict[str, Any]] = []

    for requirement in requirements:
        key = (
            _normalize_name(requirement["name"]),
            requirement["category"],
            requirement["unit"].lower(),
        )

        required = requirement["quantity"]

        if key in unknown:
            status = "unknown"
            available_quantity = None
            shortage = None
        else:
            available_quantity = available.get(key, 0.0)
            shortage = max(required - available_quantity, 0.0)
            status = "short" if shortage > 0 else "available"

        results.append(
            {
                "name": requirement["name"],
                "category": requirement["category"],
                "required": required,
                "available": available_quantity,
                "unit": requirement["unit"],
                "shortage": shortage,
                "status": status,
            }
        )

    return sorted(
        results,
        key=lambda item: (
            item["status"] != "short",
            item["category"],
            item["name"].lower(),
        ),
    )

def get_recipe_export() -> list[dict[str, Any]]:
    """Retrieve the current Beer30 recipe export."""
    return _export_data(
        RECIPE_EXPORT_NAME,
        type_="recipe",
    )


def select_active_recipe(
    recipes: list[dict[str, Any]],
    beer_name: str,
) -> dict[str, Any] | None:
    """
    Select the active Beer30 recipe for a requested beer.

    Matching is performed against the recipe name with Beer30's
    batch-size suffix removed.

    If multiple active recipes exist for the same beer, the highest
    version is selected.
    """
    target = _normalize_name(beer_name)

    matches = [
        recipe
        for recipe in recipes
        if recipe["normalized_name"] == target
        and recipe["live_status"].lower() == "active"
    ]

    if not matches:
        return None

    return max(
        matches,
        key=lambda recipe: (
            recipe["version"],
            recipe["batch_size"],
        ),
    )


def normalize_recipe_export(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Normalize all rows from a Beer30 recipe export.
    """
    return [
        normalize_recipe(row)
        for row in rows
        if str(row.get("brandName") or "").strip()
    ]


def get_active_recipe(beer_name: str) -> dict[str, Any] | None:
    """
    Retrieve and select the active recipe for one beer.
    """
    recipes = normalize_recipe_export(get_recipe_export())

    return select_active_recipe(
        recipes,
        beer_name,
    )


def combine_recipe_requirements(
    recipes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Combine ingredient requirements across multiple recipes.

    Ingredients are combined by normalized name, category, and unit.
    """
    combined: dict[
        tuple[str, str, str],
        dict[str, Any],
    ] = {}

    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            key = (
                _normalize_name(ingredient["name"]),
                ingredient["category"],
                ingredient["unit"].lower(),
            )

            if key not in combined:
                combined[key] = {
                    "name": ingredient["name"],
                    "category": ingredient["category"],
                    "quantity": 0.0,
                    "unit": ingredient["unit"],
                }

            combined[key]["quantity"] += ingredient["quantity"]

    return sorted(
        combined.values(),
        key=lambda item: (
            item["category"],
            item["name"].lower(),
        ),
    )


def check_brew_feasibility(
    beer_names: list[str],
) -> dict[str, Any]:
    """
    Retrieve active recipes, calculate combined requirements, and
    compare them against current Beer30 inventory.
    """
    if not beer_names:
        raise ValueError("At least one beer must be requested.")

    normalized_recipes = normalize_recipe_export(
        get_recipe_export()
    )

    beers: list[dict[str, Any]] = []
    found_recipes: list[dict[str, Any]] = []
    not_found: list[str] = []

    for beer_name in beer_names:
        requested_name = beer_name.strip()

        recipe = select_active_recipe(
            normalized_recipes,
            requested_name,
        )

        if recipe is None:
            not_found.append(requested_name)
            continue

        beers.append(
            {
                "requested_name": requested_name,
                "recipe_name": recipe["recipe_name"],
                "version": recipe["version"],
                "batch_size": recipe["batch_size"],
                "ingredient_count": len(recipe["ingredients"]),
            }
        )

        found_recipes.append(recipe)

    requirements = combine_recipe_requirements(
        found_recipes
    )

    incomplete = [
        beer
        for beer in found_recipes
        if not beer["ingredients"]
    ]

    inventory: list[dict[str, Any]] = []

    inventory_categories = {
        "grain": "grains",
        "hop": "hops",
        "adjunct": "adjuncts",
    }

    for category, beer30_category in inventory_categories.items():
        if category == "adjunct":
            inventory.extend(
                get_adjunct_inventory(requirements)
            )
            continue

        response = get_inventory(beer30_category)
        inventory.extend(
            normalize_inventory(response, category)
        )

    comparison = compare_inventory(
        requirements,
        inventory,
    )

    shortages = [
        item
        for item in comparison
        if item["status"] == "short"
    ]

    unknown_inventory = [
        item
        for item in comparison
        if item["status"] == "unknown"
    ]

    feasible = (
        not not_found
        and not incomplete
        and not shortages
        and not unknown_inventory
    )

    return {
        "feasible": feasible,
        "beers": beers,
        "requirements": requirements,
        "inventory_comparison": comparison,
        "shortages": shortages,
        "unknown_inventory": unknown_inventory,
        "not_found": not_found,
        "incomplete_recipes": [
            {
                "recipe_name": recipe["recipe_name"],
                "version": recipe["version"],
            }
            for recipe in incomplete
        ],
    }

def format_brew_plan_response(result: dict[str, Any]) -> str:
    """
    Format a brew-feasibility result for Slack.
    """
    beers = result.get("beers", [])
    beer_names = [
        str(beer.get("requested_name") or beer.get("recipe_name") or "").strip()
        for beer in beers
    ]
    beer_names = [name for name in beer_names if name]

    lines = [
        "🍺 Brew Plan",
        "",
        "I checked the Beer30 recipes and current inventory for:",
    ]

    for beer_name in beer_names:
        lines.append(f"• {beer_name}")

    lines.append("")

    not_found = result.get("not_found", [])
    incomplete = result.get("incomplete_recipes", [])
    shortages = result.get("shortages", [])
    unknown_inventory = result.get("unknown_inventory", [])

    if not_found:
        lines.append("❌ I couldn't find recipes for:")
        for beer_name in not_found:
            lines.append(f"• {beer_name}")
        lines.append("")

    if incomplete:
        lines.append("⚠️ These recipes do not contain usable ingredient data:")
        for recipe in incomplete:
            lines.append(
                f"• {recipe.get('recipe_name', 'Unknown recipe')}"
            )
        lines.append("")

    if shortages:
        lines.append(
            "❌ We do not have enough inventory to brew all requested beers."
        )
        lines.append("")
        lines.append("Order:")

        for item in shortages:
            shortage = item.get("shortage", 0)
            unit = item.get("unit", "")
            lines.append(
                f"• {item['name']}: {_format_quantity(shortage)} {unit}"
            )

        lines.append("")

    if unknown_inventory:
        lines.append(
            "⚠️ Inventory status is unknown for:"
        )

        for item in unknown_inventory:
            required = item.get("required")
            unit = item.get("unit", "")
            lines.append(
                f"• {item['name']}: {_format_quantity(required)} {unit} required"
            )

        lines.append("")

    if (
        not not_found
        and not incomplete
        and not shortages
        and not unknown_inventory
        and result.get("feasible")
    ):
        lines.append(
            "✅ We have enough inventory to brew all requested beers."
        )
    elif not_found or incomplete or shortages or unknown_inventory:
        lines.append(
            "The brew plan cannot currently be confirmed."
        )

    return "\n".join(lines)


def _format_quantity(value: Any) -> str:
    """Format a quantity without unnecessary trailing zeroes."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if number.is_integer():
        return str(int(number))

    return f"{number:.2f}".rstrip("0").rstrip(".")
