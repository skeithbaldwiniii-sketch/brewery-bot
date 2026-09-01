from integrations.beer30 import (
    get_inventory_item,
    get_inventory_items,
    get_latest_inventory,
    get_inventory_history,
    get_latest_sync,
    get_sync_history,
)


INVENTORY_KEYWORDS = [
    "inventory",
    "in stock",
    "stock",
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


def answer_inventory_question(question):
    """
    Answer natural-language questions about Beer30 inventory.
    """

    q = question.lower().strip()

    if not any(keyword in q for keyword in INVENTORY_KEYWORDS):
        return None

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