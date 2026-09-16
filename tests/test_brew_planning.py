import pytest

from intelligence.brew_planning import (
    check_brew_feasibility,
    combine_recipe_requirements,
    compare_inventory,
    get_active_recipe,
    normalize_inventory,
    normalize_recipe,
    normalize_recipe_export,
    select_active_recipe,
    parse_brew_request,
    format_brew_plan_response
)


def test_recipe_base_name_is_used_for_matching():
    recipes = [
        {
            "recipe_name": "Fire IPA (10.00)",
            "base_name": "Fire IPA",
            "normalized_name": "fire ipa",
            "version": 3,
            "live_status": "Active",
            "batch_size": 10.0,
            "ingredients": [],
        },
    ]

    result = select_active_recipe(
        recipes,
        "Fire IPA",
    )

    assert result is not None
    assert result["recipe_name"] == "Fire IPA (10.00)"


def test_archived_recipe_is_not_selected():
    recipes = [
        {
            "recipe_name": "Fire IPA (10.00)",
            "normalized_name": "fire ipa",
            "version": 4,
            "live_status": "Archived",
            "batch_size": 10.0,
            "ingredients": [],
        },
        {
            "recipe_name": "Fire IPA (10.00)",
            "normalized_name": "fire ipa",
            "version": 3,
            "live_status": "Active",
            "batch_size": 10.0,
            "ingredients": [],
        },
    ]

    result = select_active_recipe(
        recipes,
        "Fire IPA",
    )

    assert result["version"] == 3


def test_highest_active_version_is_selected():
    recipes = [
        {
            "recipe_name": "Test Beer (10.00)",
            "normalized_name": "test beer",
            "version": 1,
            "live_status": "Active",
            "batch_size": 10.0,
            "ingredients": [],
        },
        {
            "recipe_name": "Test Beer (10.00)",
            "normalized_name": "test beer",
            "version": 2,
            "live_status": "Active",
            "batch_size": 10.0,
            "ingredients": [],
        },
    ]

    result = select_active_recipe(
        recipes,
        "Test Beer",
    )

    assert result["version"] == 2


def test_draft_recipe_is_not_selected():
    recipes = [
        {
            "recipe_name": "Test Beer (10.00)",
            "normalized_name": "test beer",
            "version": 2,
            "live_status": "Draft",
            "batch_size": 10.0,
            "ingredients": [],
        },
    ]

    result = select_active_recipe(
        recipes,
        "Test Beer",
    )

    assert result is None


def test_normalize_recipe_extracts_grains():
    row = {
        "brandName": "Test Beer (10.00)",
        "uniqueNumber": "123",
        "Version": "2",
        "LiveStatus": "Active",
        "batchSize": "10.00",
        "grain1Name": "Pilsner Malt",
        "grain1Quantity": "400.00",
        "grain2Name": "Munich Malt",
        "grain2Quantity": "50.00",
    }

    recipe = normalize_recipe(row)

    assert recipe["recipe_name"] == "Test Beer (10.00)"
    assert recipe["version"] == 2
    assert recipe["batch_size"] == 10.0

    assert recipe["ingredients"] == [
        {
            "name": "Pilsner Malt",
            "category": "grain",
            "quantity": 400.0,
            "unit": "lb",
        },
        {
            "name": "Munich Malt",
            "category": "grain",
            "quantity": 50.0,
            "unit": "lb",
        },
    ]


def test_normalize_recipe_extracts_all_hop_processes():
    row = {
        "brandName": "Hop Test (10.00)",
        "Version": "1",
        "LiveStatus": "Active",
        "hops1Name": "Citra",
        "hops1Quantity": "2.0",
        "BoilHopsSelectUnits": "lb",
        "FirstWortHops1Name": "Mosaic",
        "FirstWortHops1Quantity": "1.0",
        "FirstWortHopsSelectUnits": "lb",
        "whirlpoolHops1Name": "Simcoe",
        "whirlpoolHops1Quantity": "3.0",
        "WhirlpoolHopsSelectUnits": "lb",
        "activeFermHops1Name": "Amarillo",
        "activeFermHops1Quantity": "1.5",
        "ActiveFermentationHopsSelectUnits": "lb",
        "dryHops1Name": "Citra",
        "dryHops1Quantity": "4.0",
        "DryHopsSelectUnits": "lb",
    }

    recipe = normalize_recipe(row)

    hops = [
        ingredient
        for ingredient in recipe["ingredients"]
        if ingredient["category"] == "hop"
    ]

    assert len(hops) == 5

    processes = {hop["process"] for hop in hops}

    assert processes == {
        "boil",
        "first_wort",
        "whirlpool",
        "active_fermentation",
        "dry_hop",
    }


def test_normalize_recipe_extracts_adjuncts():
    row = {
        "brandName": "Adjunct Test (10.00)",
        "Version": "1",
        "LiveStatus": "Active",
        "adjuncts1Name": "Cocoa Nibs",
        "adjuncts1Amount": "25",
        "adjuncts1Units": "lb",
        "adjuncts2Name": "Chili",
        "adjuncts2Amount": "5",
        "adjuncts2Units": "lb",
    }

    recipe = normalize_recipe(row)

    adjuncts = [
        ingredient
        for ingredient in recipe["ingredients"]
        if ingredient["category"] == "adjunct"
    ]

    assert adjuncts == [
        {
            "name": "Cocoa Nibs",
            "category": "adjunct",
            "quantity": 25.0,
            "unit": "lb",
        },
        {
            "name": "Chili",
            "category": "adjunct",
            "quantity": 5.0,
            "unit": "lb",
        },
    ]


def test_zero_and_blank_ingredients_are_ignored():
    row = {
        "brandName": "Test Beer (10.00)",
        "Version": "1",
        "LiveStatus": "Active",
        "grain1Name": "Pilsner",
        "grain1Quantity": "400",
        "grain2Name": "Unused",
        "grain2Quantity": "0",
        "grain3Name": "Blank",
        "grain3Quantity": "",
    }

    recipe = normalize_recipe(row)

    assert len(recipe["ingredients"]) == 1
    assert recipe["ingredients"][0]["name"] == "Pilsner"


def test_combined_requirements_sum_same_ingredient():
    recipes = [
        {
            "recipe_name": "Beer A (10.00)",
            "ingredients": [
                {
                    "name": "Pilsner Malt",
                    "category": "grain",
                    "quantity": 400.0,
                    "unit": "lb",
                },
            ],
        },
        {
            "recipe_name": "Beer B (10.00)",
            "ingredients": [
                {
                    "name": "Pilsner Malt",
                    "category": "grain",
                    "quantity": 300.0,
                    "unit": "lb",
                },
            ],
        },
    ]

    requirements = combine_recipe_requirements(recipes)

    assert requirements == [
        {
            "name": "Pilsner Malt",
            "category": "grain",
            "quantity": 700.0,
            "unit": "lb",
        },
    ]


def test_combined_requirements_do_not_mix_units():
    recipes = [
        {
            "recipe_name": "Beer A",
            "ingredients": [
                {
                    "name": "Citra",
                    "category": "hop",
                    "quantity": 2.0,
                    "unit": "lb",
                },
                {
                    "name": "Citra",
                    "category": "hop",
                    "quantity": 32.0,
                    "unit": "oz",
                },
            ],
        },
    ]

    requirements = combine_recipe_requirements(recipes)

    assert len(requirements) == 2


def test_no_active_recipe_returns_none():
    recipes = [
        {
            "recipe_name": "Fest Bier (10.00)",
            "normalized_name": "fest bier",
            "version": 1,
            "live_status": "Active",
            "batch_size": 10.0,
            "ingredients": [],
        },
    ]

    assert select_active_recipe(
        recipes,
        "Festbier",
    ) is None

def test_normalize_inventory_grain():
    response = {
        "inventory": [
            {
                "historyUnique": "123",
                "GrainName": "Pils - Proximity",
                "QuantityInStock": "1705.0000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    result = normalize_inventory(response, "grain")

    assert result == [
        {
            "name": "Pils - Proximity",
            "normalized_name": "pils proximity",
            "category": "grain",
            "quantity": 1705.0,
            "unit": "lb",
            "archived": False,
            "inventory_known": True,
            "history_unique": "123",
        }
    ]


def test_normalize_inventory_hop():
    response = {
        "inventory": [
            {
                "historyUnique": "456",
                "HopsName": "Amarillo",
                "QuantityInStock": "39.5000",
                "WeightUnits": "lb",
                "Archived": "0",
            }
        ]
    }

    result = normalize_inventory(response, "hop")

    assert result[0]["name"] == "Amarillo"
    assert result[0]["quantity"] == 39.5
    assert result[0]["unit"] == "lb"
    assert result[0]["inventory_known"] is True
    assert result[0]["archived"] is False


def test_normalize_inventory_adjunct_without_quantity():
    response = {
        "inventory": [
            {
                "historyUnique": "145884",
                "AdjunctsName": "Biofine",
                "MeasurementUnits": "l",
            }
        ]
    }

    result = normalize_inventory(response, "adjunct")

    assert result[0]["name"] == "Biofine"
    assert result[0]["quantity"] is None
    assert result[0]["unit"] == "l"
    assert result[0]["inventory_known"] is False
    assert result[0]["archived"] is False


def test_normalize_inventory_preserves_archived_status():
    response = {
        "inventory": [
            {
                "historyUnique": "789",
                "GrainName": "Old Malt",
                "QuantityInStock": "100.0000",
                "WeightUnits": "lb",
                "Archived": "1",
            }
        ]
    }

    result = normalize_inventory(response, "grain")

    assert result[0]["archived"] is True

def test_compare_inventory_available():
    requirements = [
        {
            "name": "Pils - Proximity",
            "category": "grain",
            "quantity": 500.0,
            "unit": "lb",
        }
    ]

    inventory = [
        {
            "name": "Pils - Proximity",
            "normalized_name": "pils proximity",
            "category": "grain",
            "quantity": 1705.0,
            "unit": "lb",
            "archived": False,
            "inventory_known": True,
            "history_unique": "123",
        }
    ]

    result = compare_inventory(requirements, inventory)

    assert result[0]["status"] == "available"
    assert result[0]["available"] == 1705.0
    assert result[0]["shortage"] == 0.0


def test_compare_inventory_shortage():
    requirements = [
        {
            "name": "Mosaic",
            "category": "hop",
            "quantity": 12.0,
            "unit": "lb",
        }
    ]

    inventory = [
        {
            "name": "Mosaic",
            "normalized_name": "mosaic",
            "category": "hop",
            "quantity": 8.0,
            "unit": "lb",
            "archived": False,
            "inventory_known": True,
            "history_unique": "123",
        }
    ]

    result = compare_inventory(requirements, inventory)

    assert result[0]["status"] == "short"
    assert result[0]["available"] == 8.0
    assert result[0]["shortage"] == 4.0


def test_compare_inventory_aggregates_duplicate_inventory():
    requirements = [
        {
            "name": "Pils - Proximity",
            "category": "grain",
            "quantity": 1800.0,
            "unit": "lb",
        }
    ]

    inventory = [
        {
            "name": "Pils - Proximity",
            "normalized_name": "pils proximity",
            "category": "grain",
            "quantity": 1705.0,
            "unit": "lb",
            "archived": False,
            "inventory_known": True,
            "history_unique": "123",
        },
        {
            "name": "Pils - Proximity",
            "normalized_name": "pils proximity",
            "category": "grain",
            "quantity": 200.0,
            "unit": "lb",
            "archived": False,
            "inventory_known": True,
            "history_unique": "456",
        },
    ]

    result = compare_inventory(requirements, inventory)

    assert result[0]["available"] == 1905.0
    assert result[0]["shortage"] == 0.0
    assert result[0]["status"] == "available"


def test_compare_inventory_unknown_quantity():
    requirements = [
        {
            "name": "Biofine",
            "category": "adjunct",
            "quantity": 5.0,
            "unit": "l",
        }
    ]

    inventory = [
        {
            "name": "Biofine",
            "normalized_name": "biofine",
            "category": "adjunct",
            "quantity": None,
            "unit": "l",
            "archived": False,
            "inventory_known": False,
            "history_unique": "145884",
        }
    ]

    result = compare_inventory(requirements, inventory)

    assert result[0]["status"] == "unknown"
    assert result[0]["available"] is None
    assert result[0]["shortage"] is None

def test_check_brew_feasibility_combines_requirements_and_inventory(
    monkeypatch,
):
    recipes = [
        {
            "brandName": "Beer A (10.00)",
            "uniqueNumber": "1",
            "Version": "1",
            "LiveStatus": "Active",
            "batchSize": "10.00",
            "grain1Name": "Pils Malt",
            "grain1Quantity": "500",
            "grain1Units": "lb",
        },
        {
            "brandName": "Beer B (10.00)",
            "uniqueNumber": "2",
            "Version": "1",
            "LiveStatus": "Active",
            "batchSize": "10.00",
            "grain1Name": "Pils Malt",
            "grain1Quantity": "700",
            "grain1Units": "lb",
        },
    ]

    def fake_recipe_export():
        return recipes

    def fake_inventory(item_type):
        if item_type == "grains":
            return {
                "inventory": [
                    {
                        "historyUnique": "1",
                        "GrainName": "Pils Malt",
                        "QuantityInStock": "1500",
                        "WeightUnits": "lb",
                        "Archived": "0",
                    }
                ]
            }

        return {"inventory": []}

    monkeypatch.setattr(
        "intelligence.brew_planning.get_recipe_export",
        fake_recipe_export,
    )

    monkeypatch.setattr(
        "intelligence.brew_planning.get_inventory",
        fake_inventory,
    )

    result = check_brew_feasibility(
        ["Beer A", "Beer B"]
    )

    assert result["feasible"] is True
    assert result["not_found"] == []
    assert result["shortages"] == []
    assert result["unknown_inventory"] == []

    comparison = result["inventory_comparison"]

    assert len(comparison) == 1
    assert comparison[0]["name"] == "Pils Malt"
    assert comparison[0]["required"] == 1200.0
    assert comparison[0]["available"] == 1500.0
    assert comparison[0]["shortage"] == 0.0
    assert comparison[0]["status"] == "available"

def test_check_brew_feasibility_detects_shortage(
    monkeypatch,
):
    recipes = [
        {
            "brandName": "Beer A (10.00)",
            "uniqueNumber": "1",
            "Version": "1",
            "LiveStatus": "Active",
            "batchSize": "10.00",
            "grain1Name": "Pils Malt",
            "grain1Quantity": "1200",
            "grain1Units": "lb",
        }
    ]

    def fake_recipe_export():
        return recipes

    def fake_inventory(item_type):
        if item_type == "grains":
            return {
                "inventory": [
                    {
                        "historyUnique": "1",
                        "GrainName": "Pils Malt",
                        "QuantityInStock": "1000",
                        "WeightUnits": "lb",
                        "Archived": "0",
                    }
                ]
            }

        return {"inventory": []}

    monkeypatch.setattr(
        "intelligence.brew_planning.get_recipe_export",
        fake_recipe_export,
    )

    monkeypatch.setattr(
        "intelligence.brew_planning.get_inventory",
        fake_inventory,
    )

    result = check_brew_feasibility(["Beer A"])

    assert result["feasible"] is False
    assert len(result["shortages"]) == 1

    shortage = result["shortages"][0]

    assert shortage["name"] == "Pils Malt"
    assert shortage["required"] == 1200.0
    assert shortage["available"] == 1000.0
    assert shortage["shortage"] == 200.0
    assert shortage["status"] == "short"


def test_check_brew_feasibility_detects_unknown_adjunct_inventory(
    monkeypatch,
):
    recipes = [
        {
            "brandName": "Beer A (10.00)",
            "uniqueNumber": "1",
            "Version": "1",
            "LiveStatus": "Active",
            "batchSize": "10.00",
            "adjuncts1Name": "Biofine",
            "adjuncts1Amount": "5",
            "adjuncts1Units": "l",
        }
    ]

    def fake_recipe_export():
        return recipes

    def fake_inventory(item_type):
        if item_type == "adjuncts":
            return {
                "inventory": [
                    {
                        "historyUnique": "145884",
                        "AdjunctsName": "Biofine",
                        "MeasurementUnits": "l",
                    }
                ]
            }

        return {"inventory": []}

    def fake_inventory_lots(item_type, item_id):
        raise RuntimeError("Beer30 lot inventory unavailable")

    monkeypatch.setattr(
        "intelligence.brew_planning.get_recipe_export",
        fake_recipe_export,
    )

    monkeypatch.setattr(
        "intelligence.brew_planning.get_inventory",
        fake_inventory,
    )

    monkeypatch.setattr(
        "intelligence.brew_planning.get_inventory_lots",
        fake_inventory_lots,
    )

    result = check_brew_feasibility(["Beer A"])

    assert result["feasible"] is False
    assert result["shortages"] == []
    assert len(result["unknown_inventory"]) == 1

    unknown = result["unknown_inventory"][0]

    assert unknown["name"] == "Biofine"
    assert unknown["required"] == 5.0
    assert unknown["available"] is None
    assert unknown["shortage"] is None
    assert unknown["status"] == "unknown"

def test_normalize_recipe_converts_hop_ounces_to_pounds():
    row = {
        "brandName": "Test Beer (10.00)",
        "FirstWortHops1Name": "Hallertau Mittelfruh T-90",
        "FirstWortHops1Quantity": "16.00",
        "FirstWortHopsSelectUnits": "oz",
        "whirlpoolHops1Name": "Hallertau Mittelfruh T-90",
        "whirlpoolHops1Quantity": "64.00",
        "WhirlpoolHopsSelectUnits": "oz",
    }

    recipe = normalize_recipe(row)

    assert recipe["ingredients"] == [
        {
            "name": "Hallertau Mittelfruh T-90",
            "category": "hop",
            "quantity": 1.0,
            "unit": "lb",
            "process": "first_wort",
        },
        {
            "name": "Hallertau Mittelfruh T-90",
            "category": "hop",
            "quantity": 4.0,
            "unit": "lb",
            "process": "whirlpool",
        },
    ]

def test_parse_brew_request_with_comma_and_and():
    question = "I'd like to brew Festbier, Hefeweizen, and Chocolate Stout."

    result = parse_brew_request(question)

    assert result == {
        "is_brew_request": True,
        "beers": [
            "Festbier",
            "Hefeweizen",
            "Chocolate Stout",
        ],
    }


def test_parse_brew_request_with_single_beer():
    question = "Can we brew Festbier?"

    result = parse_brew_request(question)

    assert result == {
        "is_brew_request": True,
        "beers": ["Festbier"],
    }


def test_parse_brew_request_with_ampersand():
    question = "I want to brew Festbier & Hefeweizen."

    result = parse_brew_request(question)

    assert result == {
        "is_brew_request": True,
        "beers": [
            "Festbier",
            "Hefeweizen",
        ],
    }


def test_parse_brew_request_strips_beer_prefix():
    question = "I'd like to brew beer Festbier, beer Hefeweizen, and beer Stout."

    result = parse_brew_request(question)

    assert result == {
        "is_brew_request": True,
        "beers": [
            "Festbier",
            "Hefeweizen",
            "Stout",
        ],
    }


def test_parse_brew_request_rejects_unrelated_question():
    question = "How much Festbier do we have?"

    result = parse_brew_request(question)

    assert result == {
        "is_brew_request": False,
        "beers": [],
    }

def test_format_brew_plan_response_when_feasible():
    result = {
        "feasible": True,
        "beers": [
            {"requested_name": "Festbier"},
            {"requested_name": "Hefeweizen"},
        ],
        "requirements": [],
        "shortages": [],
        "unknown_inventory": [],
        "not_found": [],
        "incomplete_recipes": [],
    }

    answer = format_brew_plan_response(result)

    assert "🍺 Brew Plan" in answer
    assert "Festbier" in answer
    assert "Hefeweizen" in answer
    assert "enough inventory" in answer


def test_format_brew_plan_response_with_shortage():
    result = {
        "feasible": False,
        "beers": [
            {"requested_name": "Festbier"},
        ],
        "requirements": [],
        "shortages": [
            {
                "name": "Pilsner Malt",
                "required": 1200.0,
                "available": 1000.0,
                "shortage": 200.0,
                "unit": "lb",
                "status": "short",
            },
        ],
        "unknown_inventory": [],
        "not_found": [],
        "incomplete_recipes": [],
    }

    answer = format_brew_plan_response(result)

    assert "❌" in answer
    assert "Pilsner Malt" in answer
    assert "200 lb" in answer
    assert "Order:" in answer


def test_format_brew_plan_response_with_unknown_inventory():
    result = {
        "feasible": False,
        "beers": [
            {"requested_name": "Chocolate Stout"},
        ],
        "requirements": [],
        "shortages": [],
        "unknown_inventory": [
            {
                "name": "Cocoa Nibs",
                "required": 25.0,
                "available": None,
                "shortage": None,
                "unit": "lb",
                "status": "unknown",
            },
        ],
        "not_found": [],
        "incomplete_recipes": [],
    }

    answer = format_brew_plan_response(result)

    assert "Cocoa Nibs" in answer
    assert "inventory" in answer.lower()
    assert "unknown" in answer.lower()


def test_format_brew_plan_response_with_missing_recipe():
    result = {
        "feasible": False,
        "beers": [],
        "requirements": [],
        "shortages": [],
        "unknown_inventory": [],
        "not_found": ["Definitely Not A Beer"],
        "incomplete_recipes": [],
    }

    answer = format_brew_plan_response(result)

    assert "Definitely Not A Beer" in answer
    assert "recipe" in answer.lower()

def test_get_adjunct_inventory_calculates_available_quantity(monkeypatch):
    from intelligence import brew_planning

    requirement = {
        "name": "Citra Incognito",
        "category": "adjunct",
        "quantity": 0.5,
        "unit": "kg",
    }

    monkeypatch.setattr(
        brew_planning,
        "get_inventory",
        lambda item_type: {
            "inventory": [
                {
                    "AdjunctsName": "Citra Incognito",
                    "MeasurementUnits": "kg",
                    "historyUnique": "1039472",
                }
            ]
        },
    )

    monkeypatch.setattr(
        brew_planning,
        "get_inventory_lots",
        lambda item_type, item_id: {
            "inventory": [
                {
                    "AdjunctsName": "Citra Incognito",
                    "MeasurementUnits": "kg",
                    "AddAmount": "4.0000",
                    "TotalDepleted": "3.5000",
                    "Archived": "0",
                }
            ]
        },
    )

    result = brew_planning.get_adjunct_inventory([requirement])

    assert len(result) == 1
    assert result[0]["name"] == "Citra Incognito"
    assert result[0]["quantity"] == 0.5
    assert result[0]["unit"] == "kg"
    assert result[0]["inventory_known"] is True


def test_get_adjunct_inventory_combines_multiple_lots(monkeypatch):
    from intelligence import brew_planning

    requirement = {
        "name": "Test Adjunct",
        "category": "adjunct",
        "quantity": 1.0,
        "unit": "kg",
    }

    monkeypatch.setattr(
        brew_planning,
        "get_inventory",
        lambda item_type: {
            "inventory": [
                {
                    "AdjunctsName": "Test Adjunct",
                    "MeasurementUnits": "kg",
                    "historyUnique": "12345",
                }
            ]
        },
    )

    monkeypatch.setattr(
        brew_planning,
        "get_inventory_lots",
        lambda item_type, item_id: {
            "inventory": [
                {
                    "MeasurementUnits": "kg",
                    "AddAmount": "4.0",
                    "TotalDepleted": "1.0",
                    "Archived": "0",
                },
                {
                    "MeasurementUnits": "kg",
                    "AddAmount": "10.0",
                    "TotalDepleted": "2.0",
                    "Archived": "0",
                },
            ]
        },
    )

    result = brew_planning.get_adjunct_inventory([requirement])

    assert result[0]["quantity"] == 11.0


def test_get_adjunct_inventory_ignores_archived_lots(monkeypatch):
    from intelligence import brew_planning

    requirement = {
        "name": "Test Adjunct",
        "category": "adjunct",
        "quantity": 1.0,
        "unit": "kg",
    }

    monkeypatch.setattr(
        brew_planning,
        "get_inventory",
        lambda item_type: {
            "inventory": [
                {
                    "AdjunctsName": "Test Adjunct",
                    "MeasurementUnits": "kg",
                    "historyUnique": "12345",
                }
            ]
        },
    )

    monkeypatch.setattr(
        brew_planning,
        "get_inventory_lots",
        lambda item_type, item_id: {
            "inventory": [
                {
                    "MeasurementUnits": "kg",
                    "AddAmount": "4.0",
                    "TotalDepleted": "1.0",
                    "Archived": "0",
                },
                {
                    "MeasurementUnits": "kg",
                    "AddAmount": "20.0",
                    "TotalDepleted": "0.0",
                    "Archived": "1",
                },
            ]
        },
    )

    result = brew_planning.get_adjunct_inventory([requirement])

    assert result[0]["quantity"] == 3.0