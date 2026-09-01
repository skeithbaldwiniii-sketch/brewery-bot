import os
from datetime import date, datetime
from typing import Any
from knowledge.database import get_connection

import requests
from dotenv import load_dotenv


load_dotenv()

BEER30_BASE_URL = os.getenv(
    "BEER30_BASE_URL",
    "http://api.integration-demo.b30.app",
).rstrip("/")

BEER30_API_KEY = os.getenv("BEER30_API_KEY")


class Beer30Error(Exception):
    """Raised when a Beer30 API request fails."""


def _request(
    endpoint: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any] | None:
    """
    Make an authenticated request to the Beer30 REST API.
    """

    if not BEER30_API_KEY:
        raise Beer30Error(
            "BEER30_API_KEY is not configured in the environment."
        )

    url = f"{BEER30_BASE_URL}/{endpoint.lstrip('/')}"

    request_params = {
        "key": BEER30_API_KEY,
    }

    if params:
        request_params.update(params)

    try:
        response = requests.get(
            url,
            params=request_params,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise Beer30Error(
            f"Unable to connect to Beer30: {exc}"
        ) from exc

    if response.status_code == 429:
        raise Beer30Error(
            "Beer30 API rate limit exceeded."
        )

    if not response.ok:
        raise Beer30Error(
            f"Beer30 API returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    if response.status_code == 204:
        return None

    try:
        return response.json()
    except ValueError as exc:
        raise Beer30Error(
            "Beer30 returned a response that was not valid JSON."
        ) from exc


def get_inventory(item_type: str) -> dict[str, Any] | list[Any] | None:
    """
    Retrieve Beer30 inventory.

    Valid Beer30 item types include:
        grains
        hops
        adjuncts
        canning
        bottling
        kegging
    """

    valid_types = {
        "grains",
        "hops",
        "adjuncts",
        "canning",
        "bottling",
        "kegging",
    }

    item_type = item_type.lower().strip()

    if item_type not in valid_types:
        raise ValueError(
            f"Invalid Beer30 inventory type '{item_type}'. "
            f"Valid types: {', '.join(sorted(valid_types))}"
        )

    return _request(
        "inventory/items",
        params={
            "type": item_type,
        },
    )


def get_production_volume_brewed(
    start_date: str | date,
    end_date: str | date,
) -> dict[str, Any] | list[Any] | None:
    """
    Retrieve Beer30 production volume brewed
    for a specified date range.
    """

    return _request(
        "reports/production-volume-brewed",
        params={
            "start-date": _format_date(start_date),
            "end-date": _format_date(end_date),
        },
    )


def get_production_volume_packaged(
    start_date: str | date,
    end_date: str | date,
) -> dict[str, Any] | list[Any] | None:
    """
    Retrieve Beer30 production volume packaged
    for a specified date range.
    """

    return _request(
        "reports/production-volume-packaged",
        params={
            "start-date": _format_date(start_date),
            "end-date": _format_date(end_date),
        },
    )


def get_transfer_history(
    start_date: str | date,
    end_date: str | date,
) -> dict[str, Any] | list[Any] | None:
    """
    Retrieve Beer30 transfer history
    for a specified date range.
    """

    return _request(
        "reports/transfer-history",
        params={
            "start-date": _format_date(start_date),
            "end-date": _format_date(end_date),
        },
    )


def _format_date(value: str | date) -> str:
    """Convert a date or date string to YYYY-MM-DD."""

    if isinstance(value, date):
        return value.isoformat()

    return str(value)

def save_inventory_snapshot(item_type: str) -> int:
    """
    Retrieve inventory from Beer30 and save a snapshot
    to the local SQLite database.

    A sync-run record is created so the database knows
    which records were created by each synchronization.

    Returns the number of records saved.
    """

    connection = get_connection()
    cursor = connection.cursor()

    sync_id = None

    try:
        # -----------------------------------------------------
        # START SYNC RUN
        # -----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO beer30_sync_runs (
                data_type,
                status
            )
            VALUES (?, ?)
            """,
            (f"inventory:{item_type}", "running"),
        )

        sync_id = cursor.lastrowid

        connection.commit()

        # -----------------------------------------------------
        # GET BEER30 DATA
        # -----------------------------------------------------

        result = get_inventory(item_type)

        if not result:
            cursor.execute(
                """
                UPDATE beer30_sync_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    records_saved = 0,
                    status = ?
                WHERE id = ?
                """,
                ("success", sync_id),
            )

            connection.commit()
            return 0

        inventory = result.get("inventory", [])

        if not inventory:
            cursor.execute(
                """
                UPDATE beer30_sync_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    records_saved = 0,
                    status = ?
                WHERE id = ?
                """,
                ("success", sync_id),
            )

            connection.commit()
            return 0

        # -----------------------------------------------------
        # SAVE INVENTORY
        # -----------------------------------------------------

        saved = 0

        for item in inventory:
            if item_type == "canning":
                item_id = item.get(
                    "Canning_Supply_HistoryUnique"
                )
                item_name = item.get(
                    "Canning_Item_Name"
                )
            else:
                item_id = (
                    item.get("SupplyItem_HistoryUnique")
                    or item.get(
                        "InventoryItem_HistoryUnique"
                    )
                )

                item_name = (
                    item.get("Supply_Item_Name")
                    or item.get("Inventory_Item_Name")
                )

            cursor.execute(
                """
                INSERT INTO beer30_inventory (
                    beer30_item_id,
                    item_type,
                    item_name,
                    brewery_id,
                    measurement_unit,
                    quantity_per_unit,
                    quantity_in_stock,
                    archived,
                    beer30_timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    item_type,
                    item_name,
                    item.get("breweryID"),
                    item.get("Measurement_Unit"),
                    _to_float(
                        item.get("Quantity_Per_Unit")
                    ),
                    _to_float(
                        item.get(
                            "Total_Quantity_In_Stock_In_Each"
                        )
                    ),
                    _to_int(
                        item.get("Archived")
                    ),
                    item.get("TimeStamp"),
                ),
            )

            saved += 1

        # -----------------------------------------------------
        # COMPLETE SYNC RUN
        # -----------------------------------------------------

        cursor.execute(
            """
            UPDATE beer30_sync_runs
            SET
                completed_at = CURRENT_TIMESTAMP,
                records_saved = ?,
                status = ?
            WHERE id = ?
            """,
            (saved, "success", sync_id),
        )

        connection.commit()

        return saved

    except Exception as exc:

        if sync_id is not None:
            cursor.execute(
                """
                UPDATE beer30_sync_runs
                SET
                    completed_at = CURRENT_TIMESTAMP,
                    status = ?,
                    error_message = ?
                WHERE id = ?
                """,
                (
                    "failed",
                    str(exc),
                    sync_id,
                ),
            )

            connection.commit()

        raise

    finally:
        connection.close()

def get_latest_inventory(item_type: str | None = None) -> list[dict]:
    """
    Return the most recent Beer30 inventory snapshot for each item.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if item_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_type = ?
              AND id IN (
                  SELECT MAX(id)
                  FROM beer30_inventory
                  WHERE item_type = ?
                  GROUP BY beer30_item_id
              )
            ORDER BY item_name
            """,
            (item_type, item_type),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE id IN (
                SELECT MAX(id)
                FROM beer30_inventory
                GROUP BY item_type, beer30_item_id
            )
            ORDER BY item_type, item_name
            """
        )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_inventory_item(
    item_name: str,
    item_type: str | None = None,
) -> dict | None:
    """
    Find the most recent Beer30 inventory record
    matching an item name.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if item_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
              AND item_type = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (f"%{item_name}%", item_type),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (f"%{item_name}%",),
        )

    row = cursor.fetchone()
    connection.close()

    return dict(row) if row else None

def get_inventory_items(
    item_name: str,
    item_type: str | None = None,
) -> list[dict]:
    """
    Find all current Beer30 inventory records matching an item name.

    Returns the most recent snapshot for each distinct Beer30 item.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if item_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
              AND item_type = ?
              AND id IN (
                  SELECT MAX(id)
                  FROM beer30_inventory
                  WHERE item_name LIKE ?
                    AND item_type = ?
                  GROUP BY beer30_item_id
              )
            ORDER BY item_name
            """,
            (
                f"%{item_name}%",
                item_type,
                f"%{item_name}%",
                item_type,
            ),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
              AND id IN (
                  SELECT MAX(id)
                  FROM beer30_inventory
                  WHERE item_name LIKE ?
                  GROUP BY beer30_item_id
              )
            ORDER BY item_name
            """,
            (
                f"%{item_name}%",
                f"%{item_name}%",
            ),
        )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def get_inventory_history(
    item_name: str,
    item_type: str | None = None,
) -> list[dict]:
    """
    Return all stored snapshots for an inventory item.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if item_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
              AND item_type = ?
            ORDER BY retrieved_at ASC
            """,
            (f"%{item_name}%", item_type),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_inventory
            WHERE item_name LIKE ?
            ORDER BY retrieved_at ASC
            """,
            (f"%{item_name}%",),
        )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def get_latest_sync(data_type: str | None = None) -> dict | None:
    """
    Return the most recent Beer30 sync run.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if data_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_sync_runs
            WHERE data_type = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (data_type,),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_sync_runs
            ORDER BY id DESC
            LIMIT 1
            """
        )

    row = cursor.fetchone()
    connection.close()

    return dict(row) if row else None


def get_sync_history(
    data_type: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Return recent Beer30 sync runs.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if data_type:
        cursor.execute(
            """
            SELECT *
            FROM beer30_sync_runs
            WHERE data_type = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (data_type, limit),
        )
    else:
        cursor.execute(
            """
            SELECT *
            FROM beer30_sync_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]

def get_wip_report(report_date: str) -> list[dict]:
    """
    Retrieve the Beer30 WIP report for a specific date.

    Beer30 expects a single date in YYYY-MM-DD format.
    """

    response = _request(
        "reports/wip-report",
        params={
            "date": report_date,
        },
    )

    if isinstance(response, dict):
        return response.get("wip-report", [])

    return []

def save_wip_snapshot(report_date: str) -> int:
    """
    Retrieve and store a Beer30 WIP snapshot.
    """

    records = get_wip_report(report_date)

    connection = get_connection()
    cursor = connection.cursor()

    saved = 0

    try:
        for record in records:
            cursor.execute(
                """
                INSERT INTO beer30_wip (
                    report_date,
                    tank_name,
                    brand_name,
                    batch_number,
                    current_volume,
                    action,
                    wip_type,
                    total_cost,
                    item_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_date,
                    record.get("tankTypeAndNumber"),
                    record.get("brandName"),
                    record.get("batchNumber"),
                    _to_float(record.get("currentVolume")),
                    record.get("action"),
                    record.get("wipType"),
                    _to_float(record.get("Total_Cost")),
                    record.get("itemID"),
                ),
            )

            saved += 1

        connection.commit()

    finally:
        connection.close()

    return saved

def _to_float(value):
    """Safely convert a value to float."""

    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value):
    """Safely convert a value to integer."""

    if value is None or value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None