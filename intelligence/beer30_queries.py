import re
from integrations.beer30 import (
    get_inventory,
    get_inventory_item,
    get_inventory_items,
    get_inventory_lots,
    get_latest_inventory,
    get_inventory_history,
    get_latest_sync,
    get_sync_history,
    get_wholesale_inventory,
)


INVENTORY_KEYWORDS = [
    "inventory",
    "in stock",
    "stock",
    "wholesale",
    "coldbox",
    "how many",
    "how much",
    "do we have",
    "left",
    "remaining",
    "cans",
    "can inventory",
    "packaging",
    "sync",
    "synced",
]

def _inventory_category_hint(question):
    """
    Detect an explicit raw-material category in an inventory question.
    """

    q = question.lower()

    if any(
        phrase in q
        for phrase in [
            "grain",
            "grains",
            "malt",
            "malts",
        ]
    ):
        return "grain"

    if any(
        phrase in q
        for phrase in [
            "hop",
            "hops",
        ]
    ):
        return "hop"

    if "adjunct" in q or "adjuncts" in q:
        return "adjunct"

    return None

def _find_local_inventory_category(question):
    """
    Identify the inventory category from the local Beer30 snapshot.

    Returns "grain", "hop", or "adjunct" when the question matches
    exactly one local inventory item category.
    """
    local_items = get_latest_inventory()

    if not local_items:
        return None

    q_words = set(
        re.findall(
            r"[a-z0-9]+",
            question.lower(),
        )
    )

    if not q_words:
        return None

    categories = {
        "grains": "grain",
        "hops": "hop",
        "adjuncts": "adjunct",
    }

    matches = []

    for item in local_items:
        item_type = item.get("item_type")
        category = categories.get(item_type)

        if category is None:
            continue

        item_name = str(item.get("item_name") or "").strip()

        if not item_name:
            continue

        item_words = set(
            re.findall(
                r"[a-z0-9]+",
                item_name.lower(),
            )
        )

        if item_words.issubset(q_words):
            matches.append((len(item_words), category))

    if not matches:
        return None

    return max(matches, key=lambda match: match[0])[1]

def _find_local_inventory_matches(question):
    """
    Find raw-material inventory items matching the requested item words.

    Uses the local Beer30 inventory snapshot so category and product
    matching can be resolved without making a Beer30 API request.
    """
    local_items = get_latest_inventory()

    if not local_items:
        return []

    stop_words = {
        "how",
        "much",
        "many",
        "do",
        "we",
        "have",
        "has",
        "is",
        "are",
        "there",
        "in",
        "our",
        "the",
        "a",
        "an",
        "of",
        "for",
        "on",
        "hand",
        "left",
        "remaining",
        "remain",
        "stock",
        "inventory",
        "raw",
        "material",
        "grain",
        "grains",
        "malt",
        "malts",
        "hop",
        "hops",
        "adjunct",
        "adjuncts",
        "bag",
        "bags",
        "pound",
        "pounds",
        "lbs",
        "lb",
        "kg",
        "kilogram",
        "kilograms",
    }

    search_words = {
        word
        for word in re.findall(
            r"[a-z0-9]+",
            question.lower(),
        )
        if word not in stop_words
    }

    if not search_words:
        return []

    matches = []

    for item in local_items:
        if item.get("item_type") not in {
            "grains",
            "hops",
            "adjuncts",
        }:
            continue

        item_name = str(item.get("item_name") or "").strip()

        if not item_name:
            continue

        item_words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                item_name.lower(),
            )
        }

        if search_words.issubset(item_words):
            matches.append(item)

    return matches

def _find_local_adjunct_inventory(items, search_term):
    """
    Find adjuncts in the local Beer30 inventory snapshot.
    """

    if not search_term or not search_term.strip():
        return []

    search_words = {
        word
        for word in re.findall(
            r"[a-z0-9]+",
            search_term.lower(),
        )
    }

    if not search_words:
        return []

    matches = []

    for item in items:
        if item.get("item_type") != "adjuncts":
            continue

        item_name = str(
            item.get("item_name") or ""
        ).strip()

        item_words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                item_name.lower(),
            )
        }

        if search_words.issubset(item_words):
            matches.append(item)

    return matches

def answer_inventory_question(question):
    """
    Answer natural-language questions about Beer30 inventory.
    """

    q = question.lower().strip()

    has_inventory_keyword = any(
        keyword in q
        for keyword in INVENTORY_KEYWORDS
    )

    if not has_inventory_keyword:
        if not _find_local_inventory_matches(q):
            return None

    if "wholesale" in q or "coldbox" in q:
        items = get_wholesale_inventory()

        product_name = _extract_wholesale_product_name(q, items)
        package_type = _extract_wholesale_package_type(q)

        if product_name:
            matches = _find_wholesale_product(items, product_name)

            if package_type:
                matches = _find_wholesale_package(matches, package_type)

            if matches:
                return _format_wholesale_inventory(matches)

            if package_type:
                return (
                    f"No wholesale inventory found for "
                    f"{product_name} {package_type}s."
                )

            return f"No wholesale inventory found for {product_name}."

        return _format_wholesale_inventory(items)

    # ---------------------------------------------------------
    # RAW MATERIAL INVENTORY
    # ---------------------------------------------------------

    category_hint = _inventory_category_hint(q)
    local_matches = []

    if category_hint is None:
        local_matches = _find_local_inventory_matches(q)

        if len(local_matches) == 1:
            item_type = local_matches[0].get("item_type")

            category_hint = {
                "grains": "grain",
                "hops": "hop",
                "adjuncts": "adjunct",
            }.get(item_type)

        elif len(local_matches) > 1:
            match_names = [
                str(item.get("item_name") or "Unknown item")
                for item in local_matches
            ]

            return (
                "I found multiple matching inventory items:\n"
                + "\n".join(
                    f"- {name}"
                    for name in match_names
                )
                + "\nWhich specific item do you mean?"
            )
    # ---------------------------------------------------------
    # GRAIN
    # ---------------------------------------------------------

    if category_hint == "grain":
        grain_search = _extract_grain_search_term(q)

        if grain_search:
            grain_items = _get_current_grain_inventory()
            grain_matches = _find_grain_inventory(
                grain_items,
                grain_search,
            )

            if grain_matches:
                if "bag" in q:
                    return _format_grain_bag_inventory(
                        grain_matches
                    )

                return _format_grain_inventory(
                    grain_matches
                )

    # ---------------------------------------------------------
    # HOP
    # ---------------------------------------------------------

    if category_hint == "hop":
        hop_items = _get_current_hop_inventory()
        hop_search = _extract_hop_search_term(
            q,
            hop_items,
        )

        if hop_search:
            hop_matches = _find_hop_inventory(
                hop_items,
                hop_search,
            )

            if hop_matches:
                return _format_hop_inventory(
                    hop_matches
                )

    # ---------------------------------------------------------
    # ADJUNCT
    # ---------------------------------------------------------

    if category_hint == "adjunct":
        adjunct_items = get_latest_inventory()

        adjunct_search = _extract_adjunct_search_term(
            q,
            [
                {
                    "AdjunctsName": item.get("item_name"),
                }
                for item in adjunct_items
                if item.get("item_type") == "adjuncts"
            ],
        )

        if adjunct_search:
            adjunct_matches = _find_local_adjunct_inventory(
                adjunct_items,
                adjunct_search,
            )

            if adjunct_matches:
                return _format_adjunct_inventory(
                    [
                        {
                            "AdjunctsName": item.get("item_name"),
                            "MeasurementUnits": item.get(
                                "measurement_unit"
                            ),
                            "historyUnique": item.get(
                                "beer30_item_id"
                            ),
                        }
                        for item in adjunct_matches
                    ]
                )

    if category_hint is None:
        return (
            "I couldn't find that raw material in the latest "
            "Beer30 inventory snapshot."
        )
    # ---------------------------------------------------------
    # SYNC STATUS REQUESTS
    # ---------------------------------------------------------

    if any(word in q for word in [
        "sync",
        "synced",
        "synchronization",
        "synchronised",
        "synchronized",
    ]):
        sync = get_latest_sync("inventory:canning")

        if not sync:
            return "No Beer30 inventory syncs have been recorded."

        return _format_sync_status(sync)

    # ---------------------------------------------------------
    # HISTORY / CHANGE REQUESTS
    # ---------------------------------------------------------

    if any(word in q for word in [
        "history",
        "historical",
        "over time",
        "previous",
        "last time",
        "change",
        "changed",
    ]):
        item_name = _extract_item_name(q)

        if item_name:
            history = get_inventory_history(item_name, "canning")

            if not history:
                return f"No inventory history found for {item_name}."

            if "change" in q or "changed" in q:
                return _format_inventory_change(history)

            return _format_inventory_history(history)

    # ---------------------------------------------------------
    # LATEST SYNC REQUEST
    # ---------------------------------------------------------

    if any(word in q for word in [
        "last synced",
        "last sync",
        "when was",
        "when did",
    ]):
        item_name = _extract_item_name(q)

        if item_name:
            item = get_inventory_item(item_name, "canning")

            if not item:
                return f"No inventory found for {item_name}."

            return (
                f"{item['item_name']}: "
                f"last retrieved {item['retrieved_at']}"
            )

    # ---------------------------------------------------------
    # SPECIFIC INVENTORY REQUEST
    # ---------------------------------------------------------

    item_name = _extract_item_name(q)

    if item_name:
        matches = get_inventory_items(item_name, "canning")

        if matches:
            if len(matches) == 1:
                return _format_inventory_item(matches[0])

            return _format_matching_inventory(matches)

    # ---------------------------------------------------------
    # GENERAL CANNING INVENTORY
    # ---------------------------------------------------------

    if "inventory" in q or "packaging" in q:
        items = get_latest_inventory("canning")

        return _format_inventory_list(items)


    return None

def _get_current_grain_inventory():
    """
    Retrieve active grain inventory directly from Beer30.
    """

    response = get_inventory("grains")

    if not response:
        return []

    records = response.get("inventory", [])

    return [
        record
        for record in records
        if str(record.get("Archived") or "0").strip() != "1"
    ]

def _get_current_hop_inventory():
    """
    Retrieve active hop inventory directly from Beer30.
    """

    response = get_inventory("hops")

    if not response:
        return []

    records = response.get("inventory", [])

    return [
        record
        for record in records
        if str(record.get("Archived") or "0").strip() != "1"
    ]

def _get_current_adjunct_catalog():
    """
    Retrieve the Beer30 adjunct catalog.
    """

    response = get_inventory("adjuncts")

    if not response:
        return []

    return response.get("inventory", [])

def _find_adjunct_inventory(items, search_term):
    """
    Find adjunct catalog entries using word-based name matching.
    """

    if not search_term or not search_term.strip():
        return []

    search_words = {
        word
        for word in re.findall(
            r"[a-z0-9]+",
            search_term.lower(),
        )
    }

    if not search_words:
        return []

    exact_matches = [
        item
        for item in items
        if str(item.get("AdjunctsName") or "").strip().lower()
        == search_term.strip().lower()
    ]

    if exact_matches:
        return exact_matches

    matches = []

    for item in items:
        adjunct_name = str(
            item.get("AdjunctsName") or ""
        ).lower()

        name_words = {
            word
            for word in re.findall(
                r"[a-z0-9]+",
                adjunct_name,
            )
        }

        if search_words.issubset(name_words):
            matches.append(item)

    return matches

def _get_adjunct_available_quantity(item):
    """
    Calculate current available quantity for an adjunct.

    Beer30 does not expose the current quantity on the adjunct
    catalog record. Availability is calculated from active lots:

        available = AddAmount - TotalDepleted
    """

    item_id = item.get("historyUnique")

    if not item_id:
        return None

    lots_response = get_inventory_lots(
        "adjuncts",
        str(item_id),
    )

    if not lots_response:
        return 0.0

    lots = lots_response.get("inventory", [])

    available_quantity = 0.0

    for lot in lots:
        if str(lot.get("Archived") or "0").strip() == "1":
            continue

        add_amount = lot.get("AddAmount")

        if add_amount is None:
            continue

        total_depleted = lot.get("TotalDepleted")

        available_quantity += (
            float(add_amount or 0)
            - float(total_depleted or 0)
        )

    return max(available_quantity, 0.0)

def _format_adjunct_inventory(items):
    """
    Format matching adjunct inventory with current lot availability.
    """

    if not items:
        return "No matching adjunct inventory found."

    lines = ["Current adjunct inventory:"]

    for item in items:
        name = item.get("AdjunctsName") or "Unknown adjunct"
        quantity = _get_adjunct_available_quantity(item)
        unit = item.get("MeasurementUnits") or "unit"

        if quantity is None:
            lines.append(
                f"- {name}: inventory quantity unavailable"
            )
            continue

        lines.append(
            f"- {name}: {quantity:,.2f} {unit}"
        )

    return "\n".join(lines)

def _extract_adjunct_search_term(question, items):
    """
    Extract an adjunct name from a natural-language inventory question.
    """

    q = question.lower()

    adjunct_names = {
        str(item.get("AdjunctsName") or "").strip()
        for item in items
        if item.get("AdjunctsName")
    }

    exact_matches = [
        name
        for name in adjunct_names
        if name.lower() in q
    ]

    if exact_matches:
        return max(exact_matches, key=len)

    return None

def _find_grain_inventory(items, search_term):
    """
    Find active grain inventory records using word-based name matching.
    """

    if not search_term or not search_term.strip():
        return []

    search_words = {
        word
        for word in re.findall(r"[a-z0-9]+", search_term.lower())
    }

    if not search_words:
        return []

    matches = []

    for item in items:
        grain_name = str(item.get("GrainName") or "").lower()

        name_words = {
            word
            for word in re.findall(r"[a-z0-9]+", grain_name)
        }

        if search_words.issubset(name_words):
            matches.append(item)

    return matches

def _find_hop_inventory(items, search_term):
    """
    Find active hop inventory using exact-name matching first,
    then fall back to word-based matching.
    """

    if not search_term or not search_term.strip():
        return []

    target = search_term.strip().lower()

    exact_matches = [
        item
        for item in items
        if str(item.get("HopsName") or "").strip().lower() == target
    ]

    if exact_matches:
        return exact_matches

    search_words = {
        word
        for word in re.findall(r"[a-z0-9]+", target)
    }

    if not search_words:
        return []

    matches = []

    for item in items:
        hop_name = str(item.get("HopsName") or "").lower()

        name_words = {
            word
            for word in re.findall(r"[a-z0-9]+", hop_name)
        }

        if search_words.issubset(name_words):
            matches.append(item)

    return matches

def _format_hop_inventory(items):
    """
    Format matching hop inventory.
    """

    if not items:
        return "No matching hop inventory found."

    lines = ["Current hop inventory:"]

    for item in items:
        name = item.get("HopsName") or "Unknown hop"
        quantity = float(item.get("QuantityInStock") or 0)
        unit = item.get("WeightUnits") or "lb"

        lines.append(
            f"- {name}: {quantity:,.2f} {unit}"
        )

    return "\n".join(lines)

def _extract_hop_search_term(question, items):
    """
    Extract a hop name from a natural-language inventory question.
    """

    q = question.lower()

    hop_names = {
        str(item.get("HopsName") or "").strip()
        for item in items
        if item.get("HopsName")
    }

    exact_matches = [
        name
        for name in hop_names
        if name.lower() in q
    ]

    if exact_matches:
        return max(exact_matches, key=len)

    return None

def _extract_grain_search_term(question):
    """
    Extract the likely grain name from a natural-language inventory question.
    """

    q = question.lower()

    stop_words = {
        "how",
        "much",
        "many",
        "do",
        "we",
        "have",
        "has",
        "is",
        "are",
        "there",
        "in",
        "our",
        "the",
        "a",
        "an",
        "of",
        "for",
        "on",
        "hand",
        "left",
        "remaining",
        "remain",
        "stock",
        "inventory",
        "grain",
        "grains",
        "bag",
        "bags",
        "pound",
        "pounds",
        "lbs",
        "lb",
    }

    words = re.findall(r"[a-z0-9]+", q)

    search_words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(search_words)

def _format_grain_inventory(items):
    """
    Format matching grain inventory records.
    """

    if not items:
        return "No matching grain inventory found."

    lines = ["Current grain inventory:"]

    for item in items:
        name = item.get("GrainName") or "Unknown grain"
        quantity = item.get("QuantityInStock", 0)
        unit = item.get("WeightUnits") or "lb"

        lines.append(
            f"- {name}: {float(quantity):,.2f} {unit}"
        )

    return "\n".join(lines)

def _grain_bag_size(grain_name):
    """
    Return the expected bag size for a grain.

    Flaked grains are treated as 50 lb bags.
    Other grains are treated as 55 lb bags.
    """

    name = str(grain_name or "").lower()

    if "flaked" in name:
        return 50

    return 55

def _grain_bag_count(item):
    """
    Calculate the equivalent number of bags for a grain inventory item.
    """

    quantity = float(item.get("QuantityInStock") or 0)
    bag_size = _grain_bag_size(item.get("GrainName"))

    return quantity / bag_size

def _format_grain_bag_inventory(items):
    """
    Format matching grain inventory as equivalent bag counts.
    """

    if not items:
        return "No matching grain inventory found."

    lines = ["Current grain inventory by bag equivalent:"]

    for item in items:
        name = item.get("GrainName") or "Unknown grain"
        quantity = float(item.get("QuantityInStock") or 0)
        bag_size = _grain_bag_size(name)
        bag_count = _grain_bag_count(item)

        lines.append(
            f"- {name}: "
            f"{quantity:,.2f} lb "
            f"({bag_count:,.2f} bags at {bag_size} lb/bag)"
        )

    return "\n".join(lines)

def _extract_item_name(question):
    """
    Translate natural-language descriptions into
    Beer30 inventory item searches.
    """

    q = question.lower()

    # Most specific names first.
    if "sleek" in q and "12" in q:
        return "Sleek 12 Oz Cans (Brite)"

    if "16 oz" in q or "16oz" in q:
        return "16 Oz Cans"

    if "12 oz" in q or "12oz" in q:
        return "12 Oz Cans"

    if "32 oz" in q or "32oz" in q:
        return "32 Oz Crowlers"

    if "crown lid" in q:
        return "202 Crown Lids"

    if "crowler lid" in q:
        return "Crowler 303 Lids"

    return None

def _format_inventory_item(item):
    """
    Format a single inventory item.
    """

    quantity = item["quantity_in_stock"]
    unit = item.get("measurement_unit") or "each"

    return (
        f"{item['item_name']}: "
        f"{quantity:,.2f} {unit}"
    )


def _format_matching_inventory(items):
    """
    Format multiple matching inventory items.
    """

    lines = [
        f"Matching inventory items ({len(items)}):"
    ]

    total = 0

    for item in items:
        quantity = item["quantity_in_stock"]
        unit = item.get("measurement_unit") or "each"

        total += quantity

        lines.append(
            f"- {item['item_name']}: "
            f"{quantity:,.2f} {unit}"
        )

    lines.append(
        f"Total: {total:,.2f} "
        f"{items[0].get('measurement_unit') or 'each'}"
    )

    return "\n".join(lines)


def _format_inventory_history(history):
    """
    Format historical inventory records.
    """

    lines = [
        f"Inventory history: {history[0]['item_name']}"
    ]

    for record in history:
        lines.append(
            f"- {record['retrieved_at']}: "
            f"{record['quantity_in_stock']:,.2f} "
            f"{record.get('measurement_unit') or 'each'}"
        )

    return "\n".join(lines)


def _format_inventory_change(history):
    """
    Compare the two most recent inventory snapshots.
    """

    if len(history) < 2:
        return (
            f"{history[0]['item_name']}: "
            "not enough history to calculate a change."
        )

    previous = history[-2]
    current = history[-1]

    previous_qty = previous["quantity_in_stock"]
    current_qty = current["quantity_in_stock"]

    change = current_qty - previous_qty

    if change > 0:
        direction = "increase"
    elif change < 0:
        direction = "decrease"
    else:
        direction = "no change"

    return (
        f"{current['item_name']}: {direction} of "
        f"{abs(change):,.2f} "
        f"({previous_qty:,.2f} -> {current_qty:,.2f})"
    )


def _format_inventory_list(items):
    """
    Format all current canning inventory.
    """

    if not items:
        return "No canning inventory found."

    lines = ["Current canning inventory:"]

    for item in items:
        quantity = item["quantity_in_stock"]
        unit = item.get("measurement_unit") or "each"

        lines.append(
            f"- {item['item_name']}: "
            f"{quantity:,.2f} {unit}"
        )

    return "\n".join(lines)

def _find_wholesale_product(items, beer_name):
    """
    Find wholesale inventory records matching a beer brand name.

    Matching is case-insensitive substring matching.
    """

    if not beer_name or not beer_name.strip():
        return []

    target = beer_name.strip().lower()

    return [
        item
        for item in items
        if target in str(item.get("brand") or "").lower()
    ]

def _find_wholesale_package(items, package_type):
    """
    Find wholesale inventory records matching a package type.

    Matching is case-insensitive substring matching against
    the Beer30 package description.
    """

    if not package_type or not package_type.strip():
        return []

    target = package_type.strip().lower()

    return [
        item
        for item in items
        if target in str(item.get("package") or "").lower()
    ]

def _extract_wholesale_package_type(question):
    """
    Extract a package type from a wholesale inventory question.

    Returns "can", "keg", or None.
    """

    q = question.lower()

    if "can" in q:
        return "can"

    if "keg" in q:
        return "keg"

    return None

def _extract_wholesale_product_name(question, items):
    """
    Find a finished-goods brand name mentioned in a wholesale question.

    Matching is case-insensitive and based on the brands present
    in the current Beer30 wholesale inventory.
    """

    q = question.lower()

    brands = {
        str(item.get("brand")).strip()
        for item in items
        if item.get("brand")
    }

    matches = [
        brand
        for brand in brands
        if brand.lower() in q
    ]

    if not matches:
        return None

    return max(matches, key=len)

def _format_wholesale_inventory(items):
    """
    Format current Beer30 finished-goods inventory
    from the Coldbox.
    """

    if not items:
        return "No wholesale inventory found."

    lines = ["Current wholesale inventory:"]

    for item in items:
        quantity = item.get("available", 0)
        brand = item.get("brand") or "Unknown product"
        package = item.get("package") or "Unknown package"

        lines.append(
            f"- {brand}: "
            f"{quantity:,.2f} {package}"
        )

    return "\n".join(lines)

def _format_sync_status(sync):
    """
    Format the most recent Beer30 sync.
    """

    status = sync["status"]
    records = sync["records_saved"]
    started = sync["started_at"]
    completed = sync["completed_at"]

    if status == "success":
        return (
            "Beer30 inventory sync: SUCCESS\n"
            f"Started: {started}\n"
            f"Completed: {completed}\n"
            f"Records saved: {records}"
        )

    if status == "failed":
        error = sync.get("error_message") or "Unknown error"

        return (
            "Beer30 inventory sync: FAILED\n"
            f"Started: {started}\n"
            f"Records saved: {records}\n"
            f"Error: {error}"
        )

    return (
        f"Beer30 inventory sync: {status.upper()}\n"
        f"Started: {started}\n"
        f"Completed: {completed or 'Still running'}\n"
        f"Records saved: {records}"
    )

from knowledge.database import get_connection


def get_latest_wip(report_date: str | None = None) -> list[dict]:
    """
    Return the latest stored WIP snapshot.

    If report_date is provided, return the WIP snapshot for that date.
    Otherwise, use the most recently stored report date.
    """
    connection = get_connection()
    connection.row_factory = lambda cursor, row: {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }

    cursor = connection.cursor()

    try:
        if report_date:
            cursor.execute(
                """
                SELECT *
                FROM beer30_wip
                WHERE report_date = ?
                ORDER BY tank_name
                """,
                (report_date,),
            )
        else:
            cursor.execute(
                """
                SELECT *
                FROM beer30_wip
                WHERE report_date = (
                    SELECT MAX(report_date)
                    FROM beer30_wip
                )
                ORDER BY tank_name
                """
            )

        return cursor.fetchall()

    finally:
        connection.close()


def get_wip_by_tank(tank_name: str) -> list[dict]:
    """
    Return the most recent WIP record for a specific tank.
    """
    connection = get_connection()
    connection.row_factory = lambda cursor, row: {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM beer30_wip
            WHERE LOWER(tank_name) = LOWER(?)
              AND report_date = (
                  SELECT MAX(report_date)
                  FROM beer30_wip
                  WHERE LOWER(tank_name) = LOWER(?)
              )
            ORDER BY id DESC
            LIMIT 1
            """,
            (tank_name, tank_name),
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_wip_by_action(action: str) -> list[dict]:
    """
    Return the latest WIP records matching an action.
    """
    connection = get_connection()
    connection.row_factory = lambda cursor, row: {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM beer30_wip
            WHERE LOWER(action) LIKE LOWER(?)
              AND report_date = (
                  SELECT MAX(report_date)
                  FROM beer30_wip
              )
            ORDER BY tank_name
            """,
            (f"%{action}%",),
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_active_wip() -> list[dict]:
    """
    Return all tanks from the latest WIP snapshot that contain product.
    """
    connection = get_connection()
    connection.row_factory = lambda cursor, row: {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM beer30_wip
            WHERE report_date = (
                SELECT MAX(report_date)
                FROM beer30_wip
            )
            AND COALESCE(current_volume, 0) > 0
            ORDER BY tank_name
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_empty_tanks() -> list[dict]:
    """
    Return empty tanks from the latest WIP snapshot.
    """
    connection = get_connection()
    connection.row_factory = lambda cursor, row: {
        column[0]: row[index]
        for index, column in enumerate(cursor.description)
    }

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT *
            FROM beer30_wip
            WHERE report_date = (
                SELECT MAX(report_date)
                FROM beer30_wip
            )
            AND COALESCE(current_volume, 0) = 0
            ORDER BY tank_name
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_total_wip_volume() -> float:
    """
    Calculate total current WIP volume from the latest snapshot.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(current_volume), 0)
            FROM beer30_wip
            WHERE report_date = (
                SELECT MAX(report_date)
                FROM beer30_wip
            )
            """
        )

        result = cursor.fetchone()
        return float(result[0] or 0)

    finally:
        connection.close()

WIP_KEYWORDS = [
    "wip",
    "work in progress",
    "cellar",
    "cellaring",
    "fermenting",
    "ferment",
    "tanks",
    "tank",
    "brewing",
    "beer in tank",
    "what's in",
    "whats in",
    "what is in",
    "empty tanks",
    "active tanks",
]


def is_wip_question(question: str) -> bool:
    """Determine whether a question is related to Beer30 WIP."""
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in WIP_KEYWORDS)

def _format_batch(batch_number) -> str:
    """Format a Beer30 batch number for conversational output."""
    if not batch_number:
        return "Unknown"

    return f"Batch {batch_number}"

def answer_wip_question(question: str) -> str:
    """
    Answer natural-language questions about Beer30 WIP data.
    """
    metadata = get_latest_wip_metadata()

    if not metadata:
        return "No Beer30 WIP snapshot is currently available."

    snapshot_date = metadata["report_date"]
    retrieved_at = metadata["retrieved_at"]
    question_lower = question.lower()

    # ---------------------------------------------------------
    # Total WIP volume
    # ---------------------------------------------------------
    if (
        "total" in question_lower
        and "volume" in question_lower
    ) or "how much wip" in question_lower:
        total = get_total_wip_volume()

        metadata = get_latest_wip_metadata()

        if metadata:
            return (
                f"Beer30's latest available WIP snapshot, dated "
                f"{metadata['report_date']}, contains approximately "
                f"{total:.2f} bbl of product across the reported tanks. "
                f"The snapshot was retrieved on {metadata['retrieved_at']}."
            )

        return "No Beer30 WIP snapshot is currently available."

    # ---------------------------------------------------------
    # Empty tanks
    # ---------------------------------------------------------
    if "empty" in question_lower:
        tanks = get_empty_tanks()

        if not tanks:
            return "No empty tanks were found in the latest Beer30 WIP snapshot."

        tank_names = [tank["tank_name"] for tank in tanks]

        return (
            f"Beer30's WIP snapshot dated {snapshot_date} shows "
            f"{len(tank_names)} empty tanks:\n"
            + "\n".join(f"- {name}" for name in tank_names)
            + f"\n\nSnapshot retrieved: {retrieved_at}"
        )

    # ---------------------------------------------------------
    # Active tanks
    # ---------------------------------------------------------
    if (
        "active tanks" in question_lower
        or "tanks are active" in question_lower
        or "what tanks are active" in question_lower
    ):
        tanks = get_active_wip()

        if not tanks:
            return "No active tanks were found in the latest Beer30 WIP snapshot."

        lines = []

        for tank in tanks:
            lines.append(
                f"- {tank['tank_name']}: "
                f"{tank['brand_name']} — "
                f"{tank['current_volume']:.2f} bbl "
                f"({tank['action']})"
            )

        return (
            f"Beer30's WIP snapshot dated {snapshot_date} shows "
            f"{len(tanks)} active tanks:\n"
            + "\n".join(lines)
            + f"\n\nSnapshot retrieved: {retrieved_at}"
        )

    # ---------------------------------------------------------
    # Fermenting
    # ---------------------------------------------------------
    if "ferment" in question_lower:
        tanks = get_wip_by_action("ferment")

        if not tanks:
            return "No fermenting tanks were found in the latest Beer30 WIP snapshot."

        lines = []

        for tank in tanks:
            lines.append(
                f"- {tank['tank_name']}: "
                f"{tank['brand_name']} — "
                f"{tank['current_volume']:.2f} bbl "
                f"({_format_batch(tank['batch_number'])})"
            )

        return (
            f"Beer30's WIP snapshot dated {snapshot_date} shows "
            f"{len(tanks)} fermenting tanks:\n"
            + "\n".join(lines)
            + f"\n\nSnapshot retrieved: {retrieved_at}"
        )

    # ---------------------------------------------------------
    # Cellaring
    # ---------------------------------------------------------
    if "cellar" in question_lower:
        tanks = get_wip_by_action("cellar")

        if not tanks:
            return "No cellaring tanks were found in the latest Beer30 WIP snapshot."

        lines = []

        for tank in tanks:
            lines.append(
                f"- {tank['tank_name']}: "
                f"{tank['brand_name']} — "
                f"{tank['current_volume']:.2f} bbl "
                f"({_format_batch(tank['batch_number'])})"
            )

        return (
            f"Beer30's WIP snapshot dated {snapshot_date} shows "
            f"{len(tanks)} cellaring tanks:\n"
            + "\n".join(lines)
            + f"\n\nSnapshot retrieved: {retrieved_at}"
        )

    # ---------------------------------------------------------
    # Specific tank lookup
    # ---------------------------------------------------------
    import re

    tank_match = re.search(
        r"\b(?:tank\s+)?((?:UNI|BBT|FV|BRITE|CIP)[-_]?[A-Z]?-?\d{1,2})\b",
        question,
        re.IGNORECASE,
    )

    if tank_match:
        tank_name = tank_match.group(1).upper()
        records = get_wip_by_tank(tank_name)

        if not records:
            return f"I couldn't find {tank_name} in the latest Beer30 WIP snapshot."

        tank = records[0]

        if not tank["brand_name"] or tank["brand_name"] == "-":
            return f"{tank_name} is currently empty."

        return (
            f"Beer30's WIP snapshot dated {snapshot_date} reports "
            f"{tank_name} containing {tank['brand_name']} "
            f"with {tank['current_volume']:.2f} bbl. "
            f"{_format_batch(tank['batch_number'])}. "
            f"Status: {tank['action']}.\n"
            f"Snapshot retrieved: {retrieved_at}"
        )

    # ---------------------------------------------------------
    # General WIP summary
    # ---------------------------------------------------------
    tanks = get_active_wip()

    if not tanks:
        return "No active WIP was found in the latest Beer30 snapshot."

    lines = []

    for tank in tanks:
        lines.append(
            f"- {tank['tank_name']}: "
            f"{tank['brand_name']} — "
            f"{tank['current_volume']:.2f} bbl "
            f"({tank['action']})"
        )

    return (
        f"Beer30's WIP snapshot dated {snapshot_date} contains "
        f"{len(tanks)} active tanks with "
        f"{get_total_wip_volume():.2f} bbl total:\n"
        + "\n".join(lines)
        + f"\n\nSnapshot retrieved: {retrieved_at}"
    )

def get_latest_wip_metadata() -> dict | None:
    """
    Return metadata about the most recently stored WIP snapshot.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                report_date,
                MIN(retrieved_at) AS retrieved_at,
                COUNT(*) AS record_count
            FROM beer30_wip
            WHERE report_date = (
                SELECT MAX(report_date)
                FROM beer30_wip
            )
            GROUP BY report_date
            """
        )

        row = cursor.fetchone()

        if not row:
            return None

        return {
            "report_date": row[0],
            "retrieved_at": row[1],
            "record_count": row[2],
        }

    finally:
        connection.close()

def get_wip_snapshot_summary() -> str:
    """
    Return a human-readable description of the latest Beer30 WIP snapshot.
    """
    metadata = get_latest_wip_metadata()

    if not metadata:
        return "No Beer30 WIP snapshot is currently stored."

    return (
        f"Beer30 WIP snapshot dated {metadata['report_date']} "
        f"with {metadata['record_count']} records. "
        f"Retrieved locally on {metadata['retrieved_at']}."
    )