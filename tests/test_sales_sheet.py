from unittest.mock import MagicMock

import pytest

from integrations.sales_sheet import preflight_sales_sheet


def make_spreadsheet():
    spreadsheet = MagicMock()
    sales = MagicMock()
    cans = MagicMock()

    spreadsheet.worksheet.side_effect = {
        "2026": sales,
        "Cans": cans,
    }.__getitem__

    sales.get.side_effect = [
        [[""] for _ in range(36)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    sales.acell.return_value.value = "=SUM(R6:R41)"

    cans.get.side_effect = [
        [[""] for _ in range(14)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    return spreadsheet, sales, cans


def test_preflight_accepts_expected_sheet_structure():
    spreadsheet, sales, cans = make_spreadsheet()

    state = preflight_sales_sheet(spreadsheet)

    assert len(state["pint_values"]) == 36
    assert len(state["can_values"]) == 14
    assert state["total_formula"] == "=SUM(R6:R41)"
    sales.get.assert_any_call("R6:R41")
    cans.get.assert_any_call("AR6:AR19")


def test_preflight_rejects_changed_total_formula():
    spreadsheet, sales, cans = make_spreadsheet()
    sales.acell.return_value.value = "=SUM(R6:R40)"

    with pytest.raises(
        RuntimeError,
        match="Unexpected 2026!R42 formula",
    ):
        preflight_sales_sheet(spreadsheet)


def test_preflight_rejects_changed_percentage_formula():
    spreadsheet, sales, cans = make_spreadsheet()
    sales.get.side_effect = [
        [[""] for _ in range(36)],
        [["=R6/$R$42"]] + [["=WRONG"] for _ in range(35)],
    ]

    with pytest.raises(
        RuntimeError,
        match="Unexpected formula in 2026!S7",
    ):
        preflight_sales_sheet(spreadsheet)


def test_preflight_rejects_changed_ros_formula():
    spreadsheet, sales, cans = make_spreadsheet()
    cans.get.side_effect = [
        [[""] for _ in range(14)],
        [["=(AR6/4)"]] + [["=WRONG"] for _ in range(13)],
    ]

    with pytest.raises(
        RuntimeError,
        match="Unexpected formula in Cans!AS7",
    ):
        preflight_sales_sheet(spreadsheet)

from integrations.sales_sheet import validate_sales_destinations


def test_validate_sales_destinations_accepts_blank_cells():
    spreadsheet, sales, cans = make_spreadsheet()
    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
        "can_updates": [(6, "Beach Boys", 22)],
    }

    validate_sales_destinations(state, updates)


def test_validate_sales_destinations_accepts_matching_existing_values():
    spreadsheet, sales, cans = make_spreadsheet()
    sales.get.side_effect = [
        [["282"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    cans.get.side_effect = [
        [["22"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
        "can_updates": [(6, "Beach Boys", 22)],
    }

    validate_sales_destinations(state, updates)


def test_validate_sales_destinations_rejects_conflicting_pint_value():
    spreadsheet, sales, cans = make_spreadsheet()
    sales.get.side_effect = [
        [["999"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]

    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
    }

    with pytest.raises(
        RuntimeError,
        match="2026!R6.*999",
    ):
        validate_sales_destinations(state, updates)


def test_validate_sales_destinations_rejects_conflicting_can_value():
    spreadsheet, sales, cans = make_spreadsheet()
    cans.get.side_effect = [
        [["999"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "can_updates": [(6, "Beach Boys", 22)],
    }

    with pytest.raises(
        RuntimeError,
        match="Cans!AR6.*999",
    ):
        validate_sales_destinations(state, updates)


def test_validate_sales_destinations_rejects_protected_fire_row():
    spreadsheet, sales, cans = make_spreadsheet()
    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [(9, "Fire", 100)],
    }

    with pytest.raises(
        RuntimeError,
        match="Protected destination",
    ):
        validate_sales_destinations(state, updates)

from integrations.sales_sheet import build_sales_sheet_writes, apply_sales_sheet_writes, verify_sales_sheet_writes


def test_build_sales_sheet_writes_returns_blank_destinations():
    spreadsheet, sales, cans = make_spreadsheet()
    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [
            (6, "Beach Boys", 282),
            (7, "Electroplasm", 292),
        ],
        "can_updates": [
            (6, "Beach Boys", 22),
            (7, "Electroplasm", 55),
        ],
    }

    writes = build_sales_sheet_writes(state, updates)

    assert writes == [
        {
            "sheet": "2026",
            "cell": "R6",
            "label": "Beach Boys",
            "quantity": 282,
        },
        {
            "sheet": "2026",
            "cell": "R7",
            "label": "Electroplasm",
            "quantity": 292,
        },
        {
            "sheet": "Cans",
            "cell": "AR6",
            "label": "Beach Boys",
            "quantity": 22,
        },
        {
            "sheet": "Cans",
            "cell": "AR7",
            "label": "Electroplasm",
            "quantity": 55,
        },
    ]


def test_build_sales_sheet_writes_skips_matching_existing_values():
    spreadsheet, sales, cans = make_spreadsheet()

    sales.get.side_effect = [
        [["282"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    cans.get.side_effect = [
        [["22"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [
            (6, "Beach Boys", 282),
            (7, "Electroplasm", 292),
        ],
        "can_updates": [
            (6, "Beach Boys", 22),
            (7, "Electroplasm", 55),
        ],
    }

    writes = build_sales_sheet_writes(state, updates)

    assert writes == [
        {
            "sheet": "2026",
            "cell": "R7",
            "label": "Electroplasm",
            "quantity": 292,
        },
        {
            "sheet": "Cans",
            "cell": "AR7",
            "label": "Electroplasm",
            "quantity": 55,
        },
    ]


def test_build_sales_sheet_writes_returns_empty_when_everything_matches():
    spreadsheet, sales, cans = make_spreadsheet()

    sales.get.side_effect = [
        [["282"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    cans.get.side_effect = [
        [["22"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    state = preflight_sales_sheet(spreadsheet)

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
        "can_updates": [(6, "Beach Boys", 22)],
    }

    writes = build_sales_sheet_writes(state, updates)

    assert writes == []

def test_apply_sales_sheet_writes_separates_worksheets():
    spreadsheet, sales, cans = make_spreadsheet()

    writes = [
        {
            "sheet": "2026",
            "cell": "R6",
            "label": "Beach Boys",
            "quantity": 282,
        },
        {
            "sheet": "2026",
            "cell": "R7",
            "label": "Electroplasm",
            "quantity": 292,
        },
        {
            "sheet": "Cans",
            "cell": "AR6",
            "label": "Beach Boys",
            "quantity": 22,
        },
    ]

    result = apply_sales_sheet_writes(spreadsheet, writes)

    assert result == writes

    sales.batch_update.assert_called_once_with(
        [
            {
                "range": "R6",
                "values": [[282]],
            },
            {
                "range": "R7",
                "values": [[292]],
            },
        ],
        value_input_option="USER_ENTERED",
    )

    cans.batch_update.assert_called_once_with(
        [
            {
                "range": "AR6",
                "values": [[22]],
            },
        ],
        value_input_option="USER_ENTERED",
    )


def test_apply_sales_sheet_writes_does_not_write_when_plan_is_empty():
    spreadsheet, sales, cans = make_spreadsheet()

    result = apply_sales_sheet_writes(spreadsheet, [])

    assert result == []
    sales.batch_update.assert_not_called()
    cans.batch_update.assert_not_called()

def test_verify_sales_sheet_writes_accepts_expected_values():
    spreadsheet, sales, cans = make_spreadsheet()

    sales.get.side_effect = [
        [["282"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    cans.get.side_effect = [
        [["22"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
        "can_updates": [(6, "Beach Boys", 22)],
    }

    assert verify_sales_sheet_writes(spreadsheet, updates) is True


def test_verify_sales_sheet_writes_rejects_wrong_pint_value():
    spreadsheet, sales, cans = make_spreadsheet()

    sales.get.side_effect = [
        [["999"] if row == 6 else [""] for row in range(6, 42)],
        [[f"=R{row}/$R$42"] for row in range(6, 42)],
    ]
    cans.get.side_effect = [
        [["22"] if row == 6 else [""] for row in range(6, 20)],
        [[f"=(AR{row}/4)"] for row in range(6, 20)],
    ]

    updates = {
        "pint_updates": [(6, "Beach Boys", 282)],
        "can_updates": [(6, "Beach Boys", 22)],
    }

    with pytest.raises(
        RuntimeError,
        match="2026!R6.*expected 282.*got '999'",
    ):
        verify_sales_sheet_writes(spreadsheet, updates)

def test_apply_sales_sheet_writes_updates_sales_and_cans():
    spreadsheet, sales, cans = make_spreadsheet()

    writes = [
        {
            "sheet": "2026",
            "cell": "R6",
            "label": "Beach Boys",
            "quantity": 282,
        },
        {
            "sheet": "Cans",
            "cell": "AR6",
            "label": "Beach Boys",
            "quantity": 22,
        },
    ]

    result = apply_sales_sheet_writes(spreadsheet, writes)

    assert result == writes

    sales.batch_update.assert_called_once_with(
        [{"range": "R6", "values": [[282]]}],
        value_input_option="USER_ENTERED",
    )

    cans.batch_update.assert_called_once_with(
        [{"range": "AR6", "values": [[22]]}],
        value_input_option="USER_ENTERED",
    )


def test_apply_sales_sheet_writes_skips_empty_sheet_groups():
    spreadsheet, sales, cans = make_spreadsheet()

    writes = [
        {
            "sheet": "2026",
            "cell": "R6",
            "label": "Beach Boys",
            "quantity": 282,
        },
    ]

    apply_sales_sheet_writes(spreadsheet, writes)

    sales.batch_update.assert_called_once()
    cans.batch_update.assert_not_called()
