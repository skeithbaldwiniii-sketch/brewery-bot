from reports.tank_status import format_tank_status


def test_format_tank_status_filters_empty_tanks_and_translates_names():
    records = [
        {
            "tankTypeAndNumber": "BBT-V-01",
            "brandName": "Into The Haze (10.00)",
            "batchNumber": "26-54",
            "currentVolume": "7.50",
            "action": "Cellaring",
        },
        {
            "tankTypeAndNumber": "BBT-V-02",
            "brandName": "-",
            "batchNumber": "-",
            "currentVolume": "0.00",
            "action": "EMPTY",
        },
        {
            "tankTypeAndNumber": "BBT-V-03",
            "brandName": "Oktoberfest (10.00)",
            "batchNumber": "26-46",
            "currentVolume": "7.46",
            "action": "Cellaring",
        },
        {
            "tankTypeAndNumber": "UNI-CID3",
            "brandName": "Cider- Midnight City (10.00)",
            "batchNumber": "CB2607",
            "currentVolume": "5.00",
            "action": "CELLARING",
        },
        {
            "tankTypeAndNumber": "UNI-V-03",
            "brandName": "SuperJuice (10.00)",
            "batchNumber": "26-55",
            "currentVolume": "10.50",
            "action": "Ferment",
        },
        {
            "tankTypeAndNumber": "UNI-V-07",
            "brandName": "Hacienda (10.00)",
            "batchNumber": "26-56",
            "currentVolume": "12.00",
            "action": "Ferment",
        },
    ]

    result = format_tank_status(records)

    expected = """TANK STATUS
───────────
CID3 — Cider- Midnight City — 5 BBL
FV3 — SuperJuice — 10.5 BBL
FV7 — Hacienda — 12 BBL
BT1 — Into The Haze — 7.5 BBL
BT3 — Oktoberfest — 7.46 BBL"""

    assert result == expected


def test_format_tank_status_ignores_non_target_tanks():
    records = [
        {
            "tankTypeAndNumber": "BBT-A-01",
            "brandName": "Some Beer",
            "currentVolume": "10.0",
        },
        {
            "tankTypeAndNumber": "UNI-V-03",
            "brandName": "SuperJuice (10.00)",
            "currentVolume": "10.50",
        },
    ]

    result = format_tank_status(records)

    assert "BBT-A-01" not in result
    assert "Some Beer" not in result
    assert "FV3 — SuperJuice — 10.5 BBL" in result

from reports.tank_status import match_fermentation_record


def test_match_fermentation_record_by_tank_and_batch():
    wip_record = {
        "tankTypeAndNumber": "UNI-V-03",
        "batchNumber": "26-55",
    }

    fermentation_records = [
        {
            "BrandName": "Old Beer (10.00)",
            "BatchNumber": "25-36",
            "FVTank": "UNI-V-03",
        },
        {
            "BrandName": "Super Juice (10.00)",
            "BatchNumber": "26-55",
            "FVTank": "UNI-V-03",
            "LowestGravity": "3.3000",
            "ABV": "6.87",
        },
    ]

    result = match_fermentation_record(
        wip_record,
        fermentation_records,
    )

    assert result["BatchNumber"] == "26-55"
    assert result["BrandName"] == "Super Juice (10.00)"


def test_match_fermentation_record_returns_none_for_wrong_batch():
    wip_record = {
        "tankTypeAndNumber": "UNI-V-03",
        "batchNumber": "26-99",
    }

    fermentation_records = [
        {
            "BrandName": "Super Juice (10.00)",
            "BatchNumber": "26-55",
            "FVTank": "UNI-V-03",
        },
    ]

    result = match_fermentation_record(
        wip_record,
        fermentation_records,
    )

    assert result is None


def test_match_fermentation_record_returns_none_for_non_fermentation_tank():
    wip_record = {
        "tankTypeAndNumber": "BBT-V-01",
        "batchNumber": "26-54",
    }

    fermentation_records = [
        {
            "BrandName": "Into The Haze (10.00)",
            "BatchNumber": "26-54",
            "FVTank": "UNI-V-03",
        },
    ]

    result = match_fermentation_record(
        wip_record,
        fermentation_records,
    )

    assert result is None

def test_format_tank_status_attaches_fermentation_data():
    wip_records = [
        {
            "tankTypeAndNumber": "UNI-V-03",
            "brandName": "Super Juice (10.00)",
            "batchNumber": "26-55",
            "currentVolume": "10.50",
            "action": "Ferment",
        }
    ]

    fermentation_records = [
        {
            "BrandName": "Super Juice (10.00)",
            "BatchNumber": "26-55",
            "FVTank": "UNI-V-03",
            "StartGravity": "15.5000",
            "LowestGravity": "3.3000",
            "ABV": "6.87",
            "Attenuation": "79.60",
        }
    ]

    # This test will verify the matching logic without
    # changing the displayed report yet.
    result = match_fermentation_record(
        wip_records[0],
        fermentation_records,
    )

    assert result["StartGravity"] == "15.5000"
    assert result["LowestGravity"] == "3.3000"
    assert result["ABV"] == "6.87"
    assert result["Attenuation"] == "79.60"

from datetime import date

from reports.tank_status import format_fermentation_metrics

def test_format_fermentation_metrics():
    record = {
        "StartDate": "2026-08-26 13:55:00",
        "LowestGravity": "3.3000",
        "ABV": "6.87",
        "Attenuation": "79.60",
    }

    result = format_fermentation_metrics(
        record,
        today=date(2026, 9, 10),
    )

    assert result == (
        "Plato: 3.3° • "
        "ABV: 6.87% • "
        "Attn: 79.6% • "
        "15 days"
    )

def test_format_fermentation_metrics_handles_missing_values():
    record = {
        "StartDate": "2026-09-09 13:28:00",
        "LowestGravity": "11.0000",
        "ABV": None,
        "Attenuation": None,
    }

    result = format_fermentation_metrics(
        record,
        today=date(2026, 9, 10),
    )

    assert result == (
        "Plato: 11° • "
        "ABV: —% • "
        "Attn: —% • "
        "1 day"
    )

def test_format_tank_status_displays_fermentation_metrics():
    wip_records = [
        {
            "tankTypeAndNumber": "UNI-V-03",
            "brandName": "Super Juice (10.00)",
            "batchNumber": "26-55",
            "currentVolume": "10.50",
            "action": "Ferment",
        }
    ]

    fermentation_records = [
        {
            "BrandName": "Super Juice (10.00)",
            "BatchNumber": "26-55",
            "FVTank": "UNI-V-03",
            "StartDate": "2026-08-26 13:55:00",
            "LowestGravity": "3.3000",
            "ABV": "6.87",
            "Attenuation": "79.60",
        }
    ]

    result = format_tank_status(
        wip_records,
        fermentation_records,
    )

    assert "FV3 — Super Juice — 10.5 BBL" in result
    assert (
        "Plato: 3.3° • ABV: 6.87% • Attn: 79.6%"
        in result
    )