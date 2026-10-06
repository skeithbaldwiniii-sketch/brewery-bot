"""Google Sheets integration for the Vanish Taproom Sales spreadsheet."""

from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1BHSQS36Wz3WYDKRdTB2-zY2iTJSbVdhf4NaKXSlZYiQ"
SALES_WORKSHEET = "2026"
CANS_WORKSHEET = "Cans"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def connect_to_sales_spreadsheet():
    """Connect to the Vanish Taproom Sales spreadsheet."""
    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES,
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(SPREADSHEET_ID)
def read_sales_sheet_state(spreadsheet):
    """Read sales destinations and protected formulas without writing."""
    sales = spreadsheet.worksheet(SALES_WORKSHEET)
    cans = spreadsheet.worksheet(CANS_WORKSHEET)

    return {
        "pint_values": sales.get("R6:R41"),
        "can_values": cans.get("AR6:AR19"),
        "total_formula": sales.acell(
            "R42",
            value_render_option="FORMULA",
        ).value,
        "percentage_formulas": sales.get(
            "S6:S41",
            value_render_option="FORMULA",
        ),
        "ros_formulas": cans.get(
            "AS6:AS19",
            value_render_option="FORMULA",
        ),
    }


def preflight_sales_sheet(spreadsheet):
    """Connect to the expected worksheet structure and read its state."""
    state = read_sales_sheet_state(spreadsheet)

    if state["total_formula"] != "=SUM(R6:R41)":
        raise RuntimeError(
            "Unexpected 2026!R42 formula: "
            f"{state['total_formula']!r}"
        )

    for row, values in enumerate(
        state["percentage_formulas"],
        start=6,
    ):
        if values and values[0] not in ("", None, f"=R{row}/$R$42"):
            raise RuntimeError(
                f"Unexpected formula in 2026!S{row}: {values[0]!r}"
            )

    for row, values in enumerate(
        state["ros_formulas"],
        start=6,
    ):
        if not values or values[0] != f"=(AR{row}/4)":
            raise RuntimeError(
                f"Unexpected formula in Cans!AS{row}: {values!r}"
            )

    return state

def validate_sales_destinations(state, updates):
    """Validate proposed sales updates against the current sheet state."""
    errors = []
    pint_values = state["pint_values"]
    can_values = state["can_values"]

    for row, label, quantity in updates.get("pint_updates", []):
        if row == 9:
            errors.append(
                f"Protected destination: 2026!R{row} ({label})."
            )
            continue

        actual_values = pint_values[row - 6]
        actual = actual_values[0] if actual_values else ""

        if actual not in ("", None) and str(actual) != str(quantity):
            errors.append(
                f"2026!R{row} ({label}) contains {actual!r}; "
                f"expected blank or {quantity}."
            )

    for row, label, quantity in updates.get("can_updates", []):
        actual_values = can_values[row - 6]
        actual = actual_values[0] if actual_values else ""

        if actual not in ("", None) and str(actual) != str(quantity):
            errors.append(
                f"Cans!AR{row} ({label}) contains {actual!r}; "
                f"expected blank or {quantity}."
            )

    if errors:
        raise RuntimeError(
            "Sales-sheet preflight failed:\n" + "\n".join(errors)
        )



def build_sales_sheet_writes(state, updates):
    """Build only the spreadsheet writes that are actually needed."""
    validate_sales_destinations(state, updates)

    writes = []

    for row, label, quantity in updates.get("pint_updates", []):
        actual_values = state["pint_values"][row - 6]
        actual = actual_values[0] if actual_values else ""

        if actual in ("", None):
            writes.append(
                {
                    "sheet": SALES_WORKSHEET,
                    "cell": f"R{row}",
                    "label": label,
                    "quantity": quantity,
                }
            )

    for row, label, quantity in updates.get("can_updates", []):
        actual_values = state["can_values"][row - 6]
        actual = actual_values[0] if actual_values else ""

        if actual in ("", None):
            writes.append(
                {
                    "sheet": CANS_WORKSHEET,
                    "cell": f"AR{row}",
                    "label": label,
                    "quantity": quantity,
                }
            )

    return writes

def apply_sales_sheet_writes(spreadsheet, writes, state=None):
    """Apply a validated write plan to the sales spreadsheet."""
    if state is None:
        state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [
            (int(write["cell"][1:]), write["label"], write["quantity"])
            for write in writes
            if write["sheet"] == SALES_WORKSHEET
        ],
        "can_updates": [
            (int(write["cell"][2:]), write["label"], write["quantity"])
            for write in writes
            if write["sheet"] == CANS_WORKSHEET
        ],
    }

    validate_sales_destinations(state, updates)

    sales = spreadsheet.worksheet(SALES_WORKSHEET)
    cans = spreadsheet.worksheet(CANS_WORKSHEET)

    sales_writes = [
        write for write in writes
        if write["sheet"] == SALES_WORKSHEET
    ]
    cans_writes = [
        write for write in writes
        if write["sheet"] == CANS_WORKSHEET
    ]

    if sales_writes:
        sales.batch_update(
            [
                {
                    "range": write["cell"],
                    "values": [[write["quantity"]]],
                }
                for write in sales_writes
            ],
            value_input_option="USER_ENTERED",
        )

    if cans_writes:
        cans.batch_update(
            [
                {
                    "range": write["cell"],
                    "values": [[write["quantity"]]],
                }
                for write in cans_writes
            ],
            value_input_option="USER_ENTERED",
        )

    return writes

def verify_sales_sheet_writes(spreadsheet, updates):
    """Verify sales values and protected formulas after a write."""
    state = read_sales_sheet_state(spreadsheet)
    validate_sales_destinations(
        {
            "pint_values": state["pint_values"],
            "can_values": state["can_values"],
        },
        {
            "pint_updates": [],
            "can_updates": [],
        },
    )

    errors = []

    for row, label, quantity in updates.get("pint_updates", []):
        values = state["pint_values"][row - 6]
        actual = values[0] if values else ""
        if str(actual) != str(quantity):
            errors.append(
                f"2026!R{row} ({label}): expected {quantity}, got {actual!r}"
            )

    for row, label, quantity in updates.get("can_updates", []):
        values = state["can_values"][row - 6]
        actual = values[0] if values else ""
        if str(actual) != str(quantity):
            errors.append(
                f"Cans!AR{row} ({label}): expected {quantity}, got {actual!r}"
            )

    if state["total_formula"] != "=SUM(R6:R41)":
        errors.append(
            f"2026!R42 formula: expected '=SUM(R6:R41)', "
            f"got {state['total_formula']!r}"
        )

    if errors:
        raise RuntimeError(
            "Sales-sheet verification failed:\n" + "\n".join(errors)
        )

    return True
