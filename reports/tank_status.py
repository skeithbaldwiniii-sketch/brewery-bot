"""Formatting helpers for brewery tank status reports."""

TANK_DISPLAY_MAP = {
    "UNI-CID1": "CID1",
    "UNI-CID2": "CID2",
    "UNI-CID3": "CID3",
    "UNI-V-01": "FV1",
    "UNI-V-02": "FV2",
    "UNI-V-03": "FV3",
    "UNI-V-04": "FV4",
    "UNI-V-05": "FV5",
    "UNI-V-06": "FV6",
    "UNI-V-07": "FV7",
    "UNI-V-08": "FV8",
    "UNI-V-09": "FV9",
    "UNI-V-10": "FV10",
    "BBT-V-01": "BT1",
    "BBT-V-02": "BT2",
    "BBT-V-03": "BT3",
}

TANK_ORDER = [
    "CID1",
    "CID2",
    "CID3",
    "FV1",
    "FV2",
    "FV3",
    "FV4",
    "FV5",
    "FV6",
    "FV7",
    "FV8",
    "FV9",
    "FV10",
    "BT1",
    "BT2",
    "BT3",
]


def _format_volume(value):
    """Format a Beer30 volume without unnecessary trailing zeroes."""
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def _clean_brand_name(brand_name):
    """Remove Beer30's package/batch-size suffix from a brand name."""
    if not brand_name or brand_name == "-":
        return ""

    return brand_name.rsplit(" (", 1)[0].strip()

def match_fermentation_record(wip_record, fermentation_records):
    """
    Find the fermentation summary record matching an active WIP record.

    A match requires both the Beer30 tank name and batch number.
    """
    tank = wip_record.get("tankTypeAndNumber")
    batch = wip_record.get("batchNumber")

    if not tank or not batch or batch == "-":
        return None

    for record in fermentation_records:
        if (
            record.get("FVTank") == tank
            and record.get("BatchNumber") == batch
        ):
            return record

    return None

from datetime import datetime


def format_fermentation_metrics(record, today=None):
    """
    Format fermentation metrics from a Beer30 fermentation summary record.

    Beer30's *Gravity fields are treated as degrees Plato for this report.
    Fermentation age is calculated from StartDate.
    """
    if not record:
        return None

    def format_value(value):
        if value is None or value == "":
            return "—"

        try:
            return f"{float(value):g}"
        except (TypeError, ValueError):
            return str(value)

    start_date = record.get("StartDate")
    fermentation_days = None

    if start_date:
        try:
            start_datetime = datetime.strptime(
                start_date,
                "%Y-%m-%d %H:%M:%S",
            )

            if today is None:
                today = datetime.now().date()

            fermentation_days = (today - start_datetime.date()).days

        except (TypeError, ValueError):
            fermentation_days = None

    plato = format_value(record.get("LowestGravity"))
    abv = format_value(record.get("ABV"))
    attenuation = format_value(record.get("Attenuation"))

    if fermentation_days is None:
        days = "—"
    else:
        days = f"{fermentation_days} day" if fermentation_days == 1 else f"{fermentation_days} days"

    return (
        f"Plato: {plato}° • "
        f"ABV: {abv}% • "
        f"Attn: {attenuation}% • "
        f"{days}"
    )

def format_tank_status(records, fermentation_records=None):
    """
    Format active target tanks for the daily brewery report.

    Empty tanks and non-target tanks are omitted.
    Beer30 tank names are translated to brewery-facing names.
    """
    active_tanks = []

    for record in records:
        beer30_name = record.get("tankTypeAndNumber")

        if beer30_name not in TANK_DISPLAY_MAP:
            continue

        try:
            volume = float(record.get("currentVolume", 0))
        except (TypeError, ValueError):
            volume = 0

        if volume <= 0:
            continue

        display_name = TANK_DISPLAY_MAP[beer30_name]
        beer_name = _clean_brand_name(record.get("brandName"))

        fermentation = None

        if fermentation_records:
            fermentation = match_fermentation_record(
                record,
                fermentation_records,
            )

        active_tanks.append(
            {
                "tank": display_name,
                "beer": beer_name,
                "volume": volume,
                "action": (record.get("action") or "").upper(),
                "fermentation": fermentation,
            }
        )

    active_tanks.sort(
        key=lambda tank: TANK_ORDER.index(tank["tank"])
    )

    lines = ["TANK STATUS", "───────────"]

    for tank in active_tanks:
        lines.append(
            f'{tank["tank"]} — {tank["beer"]} — '
            f'{_format_volume(tank["volume"])} BBL'
        )

        if tank["fermentation"]:
            metrics = format_fermentation_metrics(
                tank["fermentation"]
            )
            lines.append(f"     {metrics}")

    return "\n".join(lines)