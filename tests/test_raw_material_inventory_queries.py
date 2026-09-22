from unittest.mock import patch

from intelligence.beer30_queries import _get_current_grain_inventory


def test_get_current_grain_inventory_excludes_archived_items():
    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            },
            {
                "GrainName": "Old Wheat",
                "QuantityInStock": "100.0000",
                "WeightUnits": "lb",
                "Archived": "1",
            },
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        inventory = _get_current_grain_inventory()

    assert len(inventory) == 1
    assert inventory[0]["GrainName"] == "wheat - Rahr"
    assert inventory[0]["QuantityInStock"] == "935.0000"

def test_find_grain_inventory_matches_words_in_any_order():
    from intelligence.beer30_queries import _find_grain_inventory

    items = [
        {
            "GrainName": "wheat - Rahr",
            "QuantityInStock": "935.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
        {
            "GrainName": "Rahr - 2row",
            "QuantityInStock": "550.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
        {
            "GrainName": "Malted Oats - Rahr",
            "QuantityInStock": "330.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
        {
            "GrainName": "Flaked Oats",
            "QuantityInStock": "750.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
    ]

    matches = _find_grain_inventory(items, "Rahr wheat")

    assert len(matches) == 1
    assert matches[0]["GrainName"] == "wheat - Rahr"


def test_extract_grain_search_term_from_inventory_question():
    from intelligence.beer30_queries import _extract_grain_search_term

    assert (
        _extract_grain_search_term(
            "How much Rahr wheat do we have in stock?"
        )
        == "rahr wheat"
    )

    assert (
        _extract_grain_search_term(
            "How many bags of Rahr wheat do we have?"
        )
        == "rahr wheat"
    )


def test_extract_grain_search_term_handles_flaked_grain():
    from intelligence.beer30_queries import _extract_grain_search_term

    assert (
        _extract_grain_search_term(
            "How much flaked oats do we have?"
        )
        == "flaked oats"
    )

def test_format_grain_inventory():
    from intelligence.beer30_queries import _format_grain_inventory

    items = [
        {
            "GrainName": "wheat - Rahr",
            "QuantityInStock": "935.0000",
            "WeightUnits": "lb",
        }
    ]

    result = _format_grain_inventory(items)

    assert result == (
        "Current grain inventory:\n"
        "- wheat - Rahr: 935.00 lb"
    )

def test_answer_inventory_question_returns_grain_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        result = answer_inventory_question(
            "How much Rahr wheat do we have in stock?"
        )

    assert result == (
        "Current grain inventory:\n"
        "- wheat - Rahr: 935.00 lb"
    )

def test_grain_bag_size_uses_55_pounds_for_standard_grain():
    from intelligence.beer30_queries import _grain_bag_size

    assert _grain_bag_size("wheat - Rahr") == 55
    assert _grain_bag_size("Rahr - 2row") == 55


def test_grain_bag_size_uses_50_pounds_for_flaked_grain():
    from intelligence.beer30_queries import _grain_bag_size

    assert _grain_bag_size("Flaked Oats") == 50
    assert _grain_bag_size("Flaked Wheat") == 50

def test_grain_bag_count_for_standard_grain():
    from intelligence.beer30_queries import _grain_bag_count

    item = {
        "GrainName": "wheat - Rahr",
        "QuantityInStock": "935.0000",
        "WeightUnits": "lb",
    }

    assert _grain_bag_count(item) == 17.0


def test_grain_bag_count_for_flaked_grain():
    from intelligence.beer30_queries import _grain_bag_count

    item = {
        "GrainName": "Flaked Oats",
        "QuantityInStock": "750.0000",
        "WeightUnits": "lb",
    }

    assert _grain_bag_count(item) == 15.0

def test_format_grain_bag_inventory():
    from intelligence.beer30_queries import _format_grain_bag_inventory

    items = [
        {
            "GrainName": "wheat - Rahr",
            "QuantityInStock": "935.0000",
            "WeightUnits": "lb",
        }
    ]

    result = _format_grain_bag_inventory(items)

    assert result == (
        "Current grain inventory by bag equivalent:\n"
        "- wheat - Rahr: 935.00 lb "
        "(17.00 bags at 55 lb/bag)"
    )

def test_format_flaked_grain_bag_inventory():
    from intelligence.beer30_queries import _format_grain_bag_inventory

    items = [
        {
            "GrainName": "Flaked Oats",
            "QuantityInStock": "750.0000",
            "WeightUnits": "lb",
        }
    ]

    result = _format_grain_bag_inventory(items)

    assert result == (
        "Current grain inventory by bag equivalent:\n"
        "- Flaked Oats: 750.00 lb "
        "(15.00 bags at 50 lb/bag)"
    )

def test_answer_inventory_question_returns_grain_bag_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=[
            {
                "item_type": "grains",
                "item_name": "wheat - Rahr",
            }
        ],
    ), patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        result = answer_inventory_question(
            "How many bags of Rahr wheat do we have?"
        )

    assert result == (
        "Current grain inventory by bag equivalent:\n"
        "- wheat - Rahr: 935.00 lb "
        "(17.00 bags at 55 lb/bag)"
    )


def test_answer_inventory_question_still_returns_pounds_without_bags():
    from intelligence.beer30_queries import answer_inventory_question

    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        result = answer_inventory_question(
            "How much Rahr wheat do we have?"
        )

    assert result == (
        "Current grain inventory:\n"
        "- wheat - Rahr: 935.00 lb"
    )

def test_get_current_hop_inventory_excludes_archived_items():
    from intelligence.beer30_queries import _get_current_hop_inventory

    response = {
        "inventory": [
            {
                "HopsName": "Citra",
                "QuantityInStock": "42.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            },
            {
                "HopsName": "Old Citra",
                "QuantityInStock": "10.0000",
                "WeightUnits": "lb",
                "Archived": "1",
            },
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        inventory = _get_current_hop_inventory()

    assert len(inventory) == 1
    assert inventory[0]["HopsName"] == "Citra"


def test_find_hop_inventory_prefers_exact_name_match():
    from intelligence.beer30_queries import _find_hop_inventory

    items = [
        {
            "HopsName": "Citra",
            "QuantityInStock": "42.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
        {
            "HopsName": "Citra Lupulin",
            "QuantityInStock": "12.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
        {
            "HopsName": "Amarillo",
            "QuantityInStock": "39.5000",
            "WeightUnits": "lb",
            "Archived": "0",
        },
    ]

    matches = _find_hop_inventory(items, "Citra")

    assert len(matches) == 1
    assert matches[0]["HopsName"] == "Citra"

def test_find_hop_inventory_falls_back_to_word_matching():
    from intelligence.beer30_queries import _find_hop_inventory

    items = [
        {
            "HopsName": "Citra Lupulin",
            "QuantityInStock": "12.0000",
            "WeightUnits": "lb",
            "Archived": "0",
        }
    ]

    matches = _find_hop_inventory(items, "Citra Lupulin")

    assert len(matches) == 1
    assert matches[0]["HopsName"] == "Citra Lupulin"

def test_format_hop_inventory():
    from intelligence.beer30_queries import _format_hop_inventory

    items = [
        {
            "HopsName": "Citra",
            "QuantityInStock": "42.0000",
            "WeightUnits": "lb",
        }
    ]

    result = _format_hop_inventory(items)

    assert result == (
        "Current hop inventory:\n"
        "- Citra: 42.00 lb"
    )

def test_extract_hop_search_term():
    from intelligence.beer30_queries import _extract_hop_search_term

    items = [
        {"HopsName": "Citra"},
        {"HopsName": "Citra Lupulin"},
        {"HopsName": "Amarillo"},
    ]

    assert (
        _extract_hop_search_term(
            "How much Citra do we have?",
            items,
        )
        == "Citra"
    )

    assert (
        _extract_hop_search_term(
            "How much Citra Lupulin do we have?",
            items,
        )
        == "Citra Lupulin"
    )

def test_answer_inventory_question_asks_for_specific_citra_product():
    from intelligence.beer30_queries import answer_inventory_question

    with patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra do we have?"
        )

    assert "multiple matching inventory items" in result
    assert "Citra Incognito" in result
    assert "Citra Spectrum" in result
    assert "Citra Lupomax" in result
    assert "Citra Lupulin Pellet" in result
    assert "Citra T-90" in result
    assert "Which specific item do you mean?" in result
    mock_get_inventory.assert_not_called()

def test_get_current_adjunct_catalog():
    from intelligence.beer30_queries import _get_current_adjunct_catalog

    response = {
        "inventory": [
            {
                "AdjunctsName": "Lactose",
                "MeasurementUnits": "lb",
                "historyUnique": "12345",
            },
            {
                "AdjunctsName": "Cocoa Nibs",
                "MeasurementUnits": "lb",
                "historyUnique": "67890",
            },
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        catalog = _get_current_adjunct_catalog()

    assert len(catalog) == 2
    assert catalog[0]["AdjunctsName"] == "Lactose"
    assert catalog[0]["historyUnique"] == "12345"

def test_find_adjunct_inventory_exact_match():
    from intelligence.beer30_queries import _find_adjunct_inventory

    items = [
        {
            "AdjunctsName": "Lactose",
            "MeasurementUnits": "lb",
            "historyUnique": "12345",
        },
        {
            "AdjunctsName": "Cocoa Nibs",
            "MeasurementUnits": "lb",
            "historyUnique": "67890",
        },
    ]

    matches = _find_adjunct_inventory(items, "Lactose")

    assert len(matches) == 1
    assert matches[0]["AdjunctsName"] == "Lactose"


def test_find_adjunct_inventory_matches_multiple_words():
    from intelligence.beer30_queries import _find_adjunct_inventory

    items = [
        {
            "AdjunctsName": "Apricot Juice Concentrate, Frozen",
            "MeasurementUnits": "gal",
            "historyUnique": "12345",
        }
    ]

    matches = _find_adjunct_inventory(
        items,
        "Apricot Juice Concentrate",
    )

    assert len(matches) == 1
    assert (
        matches[0]["AdjunctsName"]
        == "Apricot Juice Concentrate, Frozen"
    )

def test_get_adjunct_available_quantity():
    from intelligence.beer30_queries import _get_adjunct_available_quantity

    item = {
        "AdjunctsName": "Lactose",
        "MeasurementUnits": "lb",
        "historyUnique": "12345",
    }

    lots_response = {
        "inventory": [
            {
                "AddAmount": "100.0",
                "TotalDepleted": "25.0",
                "Archived": "0",
            },
            {
                "AddAmount": "50.0",
                "TotalDepleted": "10.0",
                "Archived": "0",
            },
            {
                "AddAmount": "200.0",
                "TotalDepleted": "200.0",
                "Archived": "1",
            },
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory_lots",
        return_value=lots_response,
    ):
        quantity = _get_adjunct_available_quantity(item)

    assert quantity == 115.0

def test_format_adjunct_inventory():
    from intelligence.beer30_queries import _format_adjunct_inventory

    items = [
        {
            "AdjunctsName": "Lactose",
            "MeasurementUnits": "lb",
            "historyUnique": "12345",
        }
    ]

    lots_response = {
        "inventory": [
            {
                "AddAmount": "100.0",
                "TotalDepleted": "25.0",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory_lots",
        return_value=lots_response,
    ):
        result = _format_adjunct_inventory(items)

    assert result == (
        "Current adjunct inventory:\n"
        "- Lactose: 75.00 lb"
    )

def test_extract_adjunct_search_term():
    from intelligence.beer30_queries import _extract_adjunct_search_term

    items = [
        {"AdjunctsName": "Lactose"},
        {"AdjunctsName": "Cocoa Nibs"},
        {"AdjunctsName": "Apricot Juice Concentrate, Frozen"},
    ]

    assert (
        _extract_adjunct_search_term(
            "How much lactose do we have?",
            items,
        )
        == "Lactose"
    )

    assert (
        _extract_adjunct_search_term(
            "How much cocoa nibs do we have?",
            items,
        )
        == "Cocoa Nibs"
    )

def test_answer_inventory_question_returns_adjunct_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    catalog_response = {
        "inventory": [
            {
                "AdjunctsName": "Lactose",
                "MeasurementUnits": "lb",
                "historyUnique": "12345",
            },
            {
                "AdjunctsName": "Cocoa Nibs",
                "MeasurementUnits": "lb",
                "historyUnique": "67890",
            },
        ]
    }

    lots_response = {
        "inventory": [
            {
                "AddAmount": "100.0",
                "TotalDepleted": "25.0",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=catalog_response,
    ), patch(
        "intelligence.beer30_queries.get_inventory_lots",
        return_value=lots_response,
    ):
        result = answer_inventory_question(
            "How much lactose do we have?"
        )

    assert result == (
        "Current adjunct inventory:\n"
        "- Lactose: 75.00 lb"
    )

def test_grain_question_uses_grain_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        result = answer_inventory_question(
            "How much Rahr wheat do we have?"
        )

    assert "wheat - Rahr: 935.00 lb" in result


def test_grain_bag_question_uses_bag_conversion():
    from intelligence.beer30_queries import answer_inventory_question

    response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=[
            {
                "item_type": "grains",
                "item_name": "wheat - Rahr",
            }
        ],
    ), patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=response,
    ):
        result = answer_inventory_question(
            "How many bags of Rahr wheat do we have?"
        )

    assert "17.00 bags at 55 lb/bag" in result


def test_hop_question_asks_for_specific_citra_product():
    from intelligence.beer30_queries import answer_inventory_question

    with patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra do we have?"
        )

    assert "multiple matching inventory items" in result
    assert "Citra Incognito" in result
    assert "Citra Spectrum" in result
    assert "Citra Lupomax" in result
    assert "Citra Lupulin Pellet" in result
    assert "Citra T-90" in result
    assert "Which specific item do you mean?" in result
    mock_get_inventory.assert_not_called()


def test_adjunct_question_uses_adjunct_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    catalog_response = {
        "inventory": [
            {
                "AdjunctsName": "Lactose",
                "MeasurementUnits": "lb",
                "historyUnique": "12345",
            }
        ]
    }

    lots_response = {
        "inventory": [
            {
                "AddAmount": "100.0",
                "TotalDepleted": "25.0",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=catalog_response,
    ), patch(
        "intelligence.beer30_queries.get_inventory_lots",
        return_value=lots_response,
    ):
        result = answer_inventory_question(
            "How much lactose do we have?"
        )

    assert "Lactose: 75.00 lb" in result

def test_inventory_category_hint_identifies_grains():
    from intelligence.beer30_queries import _inventory_category_hint

    assert _inventory_category_hint(
        "How much grain do we have?"
    ) == "grain"

    assert _inventory_category_hint(
        "How much malt do we have?"
    ) == "grain"


def test_inventory_category_hint_identifies_hops():
    from intelligence.beer30_queries import _inventory_category_hint

    assert _inventory_category_hint(
        "How much hops do we have?"
    ) == "hop"


def test_inventory_category_hint_identifies_adjuncts():
    from intelligence.beer30_queries import _inventory_category_hint

    assert _inventory_category_hint(
        "How much adjunct do we have?"
    ) == "adjunct"


def test_inventory_category_hint_returns_none_without_category():
    from intelligence.beer30_queries import _inventory_category_hint

    assert _inventory_category_hint(
        "How much Citra do we have?"
    ) is None

def test_explicit_hop_question_does_not_query_grains():
    from intelligence.beer30_queries import answer_inventory_question

    hop_response = {
        "inventory": [
            {
                "HopsName": "Citra",
                "QuantityInStock": "42.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory"
    ) as mock_inventory:
        mock_inventory.return_value = hop_response

        result = answer_inventory_question(
            "How much Citra hops do we have?"
        )

    assert "Citra: 42.00 lb" in result
    mock_inventory.assert_called_once_with("hops")


def test_explicit_grain_question_does_not_query_hops():
    from intelligence.beer30_queries import answer_inventory_question

    grain_response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_inventory"
    ) as mock_inventory:
        mock_inventory.return_value = grain_response

        result = answer_inventory_question(
            "How much Rahr wheat grain do we have?"
        )

    assert "wheat - Rahr: 935.00 lb" in result
    mock_inventory.assert_called_once_with("grains")


def test_explicit_adjunct_question_does_not_query_grains_or_hops():
    from intelligence.beer30_queries import answer_inventory_question

    lots_response = {
        "inventory": [
            {
                "AddAmount": "100.0",
                "TotalDepleted": "25.0",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=[
            {
                "item_type": "adjuncts",
                "item_name": "Lactose",
                "measurement_unit": "lb",
                "beer30_item_id": "12345",
            }
        ],
    ), patch(
        "intelligence.beer30_queries.get_inventory"
    ) as mock_inventory, patch(
        "intelligence.beer30_queries.get_inventory_lots",
        return_value=lots_response,
    ):
        result = answer_inventory_question(
            "How much lactose adjunct do we have?"
        )

    assert "Lactose: 75.00 lb" in result
    mock_inventory.assert_not_called()

def test_unqualified_hop_question_asks_for_specific_citra_product():
    from intelligence.beer30_queries import answer_inventory_question

    with patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra do we have?"
        )

    assert "multiple matching inventory items" in result
    assert "Citra Incognito" in result
    assert "Citra Spectrum" in result
    assert "Citra Lupomax" in result
    assert "Citra Lupulin Pellet" in result
    assert "Citra T-90" in result
    assert "Which specific item do you mean?" in result
    mock_get_inventory.assert_not_called()

def test_local_inventory_category_identifies_hop_without_live_category_scan():
    from intelligence.beer30_queries import (
        _find_local_inventory_category,
    )

    local_items = [
        {
            "item_type": "grains",
            "item_name": "Rahr - 2row",
        },
        {
            "item_type": "hops",
            "item_name": "Citra",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Coriander",
            "measurement_unit": "kg",
            "beer30_item_id": "12345",
        }
    ]

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ):
        result = _find_local_inventory_category(
            "How much Citra do we have?"
        )

    assert result == "hop"


def test_local_inventory_category_identifies_grain():
    from intelligence.beer30_queries import (
        _find_local_inventory_category,
    )

    local_items = [
        {
            "item_type": "grains",
            "item_name": "wheat - Rahr",
        },
        {
            "item_type": "hops",
            "item_name": "Citra",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Coriander",
            "measurement_unit": "kg",
            "beer30_item_id": "12345",
        }
    ]

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ):
        result = _find_local_inventory_category(
            "How much Rahr wheat do we have?"
        )

    assert result == "grain"


def test_local_inventory_category_identifies_adjunct():
    from intelligence.beer30_queries import (
        _find_local_inventory_category,
    )

    local_items = [
        {
            "item_type": "grains",
            "item_name": "wheat - Rahr",
        },
        {
            "item_type": "hops",
            "item_name": "Citra",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Coriander",
            "measurement_unit": "kg",
            "beer30_item_id": "12345",
        }
    ]

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ):
        result = _find_local_inventory_category(
            "How much coriander do we have?"
        )

    assert result == "adjunct"

def test_specific_hop_question_uses_local_category_before_live_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    local_items = [
        {
            "item_type": "grains",
            "item_name": "Rahr - 2row",
        },
        {
            "item_type": "hops",
            "item_name": "Citra T-90",
        },
        {
            "item_type": "hops",
            "item_name": "Citra Lupulin Pellet",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Citra Incognito",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Citra Spectrum",
        },
    ]

    hop_response = {
        "inventory": [
            {
                "HopsName": "Citra T-90",
                "QuantityInStock": "68.5000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ), patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=hop_response,
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra T-90 do we have?"
        )

    assert result == (
        "Current hop inventory:\n"
        "- Citra T-90: 68.50 lb"
    )

    mock_get_inventory.assert_called_once_with("hops")


def test_ambiguous_citra_question_does_not_call_live_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    local_items = [
        {
            "item_type": "hops",
            "item_name": "Citra T-90",
        },
        {
            "item_type": "hops",
            "item_name": "Citra Lupulin Pellet",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Citra Incognito",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Citra Spectrum",
        },
    ]

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ), patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra do we have?"
        )

    assert "Citra T-90" in result
    assert "Citra Lupulin Pellet" in result
    assert "Citra Incognito" in result
    assert "Citra Spectrum" in result
    assert "which" in result.lower() or "specific" in result.lower()

    mock_get_inventory.assert_not_called()
def test_unqualified_grain_question_uses_local_category_before_live_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    local_items = [
        {
            "item_type": "grains",
            "item_name": "wheat - Rahr",
        },
        {
            "item_type": "hops",
            "item_name": "Citra",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Coriander",
            "measurement_unit": "kg",
            "beer30_item_id": "12345",
        },
    ]

    grain_response = {
        "inventory": [
            {
                "GrainName": "wheat - Rahr",
                "QuantityInStock": "935.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ), patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=grain_response,
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Rahr wheat do we have?"
        )

    assert result == (
        "Current grain inventory:\n"
        "- wheat - Rahr: 935.00 lb"
    )

    mock_get_inventory.assert_called_once_with("grains")

def test_unqualified_adjunct_question_uses_local_category_before_live_inventory():
    from intelligence.beer30_queries import answer_inventory_question

    local_items = [
        {
            "item_type": "grains",
            "item_name": "wheat - Rahr",
        },
        {
            "item_type": "hops",
            "item_name": "Citra",
        },
        {
            "item_type": "adjuncts",
            "item_name": "Coriander",
            "measurement_unit": "kg",
            "beer30_item_id": "12345",
        },
    ]

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ), patch(
        "intelligence.beer30_queries._get_adjunct_available_quantity",
        return_value=12.5,
    ), patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much coriander do we have?"
        )

    assert result == (
        "Current adjunct inventory:\n"
        "- Coriander: 12.50 kg"
    )

    mock_get_inventory.assert_not_called()

def test_hop_question_asks_for_specific_citra_product():
    from intelligence.beer30_queries import answer_inventory_question

    with patch(
        "intelligence.beer30_queries.get_inventory",
    ) as mock_get_inventory:
        result = answer_inventory_question(
            "How much Citra do we have?"
        )

    assert "multiple matching inventory items" in result
    assert "Citra Incognito" in result
    assert "Citra Spectrum" in result
    assert "Citra Lupomax" in result
    assert "Citra Lupulin Pellet" in result
    assert "Citra T-90" in result
    assert "Which specific item do you mean?" in result
    mock_get_inventory.assert_not_called()


def test_bare_inventory_item_question_uses_local_snapshot():
    from intelligence.beer30_queries import answer_inventory_question

    local_items = [
        {
            "item_type": "hops",
            "item_name": "Citra T-90",
        },
    ]

    hop_response = {
        "inventory": [
            {
                "HopsName": "Citra T-90",
                "QuantityInStock": "68.5000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    with patch(
        "intelligence.beer30_queries.get_latest_inventory",
        return_value=local_items,
    ), patch(
        "intelligence.beer30_queries.get_inventory",
        return_value=hop_response,
    ) as mock_get_inventory:
        result = answer_inventory_question("Citra T-90")

    assert result == (
        "Current hop inventory:\n"
        "- Citra T-90: 68.50 lb"
    )
    mock_get_inventory.assert_called_once_with("hops")