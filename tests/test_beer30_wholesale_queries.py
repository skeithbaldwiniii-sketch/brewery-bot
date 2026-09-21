from intelligence import beer30_queries


def test_find_wholesale_product_matches_brand_case_insensitively():
    items = [
        {
            "brand": "Into The Haze",
            "package": "16-oz Can [4pk x 6]",
            "available": 3,
        },
        {
            "brand": "Into The Haze",
            "package": "15.5-gal Keg",
            "available": 9,
        },
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        },
    ]

    result = beer30_queries._find_wholesale_product(
        items,
        "into the haze",
    )

    assert result == [
        items[0],
        items[1],
    ]


def test_find_wholesale_product_returns_empty_for_no_match():
    items = [
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        }
    ]

    result = beer30_queries._find_wholesale_product(
        items,
        "Into The Haze",
    )

    assert result == []


def test_find_wholesale_product_handles_empty_name():
    items = [
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        }
    ]

    result = beer30_queries._find_wholesale_product(
        items,
        "",
    )

    assert result == []

def test_answer_inventory_question_filters_by_wholesale_beer(monkeypatch):
    items = [
        {
            "brand": "Into The Haze",
            "package": "16-oz Can [4pk x 6]",
            "available": 3,
        },
        {
            "brand": "Into The Haze",
            "package": "15.5-gal Keg",
            "available": 9,
        },
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        },
    ]

    monkeypatch.setattr(
        beer30_queries,
        "get_wholesale_inventory",
        lambda: items,
    )

    result = beer30_queries.answer_inventory_question(
        "How much Into The Haze do we have wholesale?"
    )

    assert "Into The Haze" in result
    assert "3.00" in result
    assert "9.00" in result
    assert "Beach Boys" not in result


def test_answer_inventory_question_filters_by_coldbox_beer(monkeypatch):
    items = [
        {
            "brand": "Oktoberfest",
            "package": "12-oz Can [6pk x 4]",
            "available": 36,
        },
        {
            "brand": "Oktoberfest",
            "package": "15.5-gal Keg",
            "available": 5,
        },
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        },
    ]

    monkeypatch.setattr(
        beer30_queries,
        "get_wholesale_inventory",
        lambda: items,
    )

    result = beer30_queries.answer_inventory_question(
        "How many Oktoberfest do we have in the Coldbox?"
    )

    assert "Oktoberfest" in result
    assert "36.00" in result
    assert "5.00" in result
    assert "Beach Boys" not in result

def test_find_wholesale_package_matches_cans():
    items = [
        {
            "brand": "Into The Haze",
            "package": "16-oz Can [4pk x 6]",
            "available": 3,
        },
        {
            "brand": "Into The Haze",
            "package": "15.5-gal Keg",
            "available": 9,
        },
    ]

    result = beer30_queries._find_wholesale_package(
        items,
        "can",
    )

    assert result == [items[0]]


def test_find_wholesale_package_matches_kegs():
    items = [
        {
            "brand": "Oktoberfest",
            "package": "12-oz Can [6pk x 4]",
            "available": 36,
        },
        {
            "brand": "Oktoberfest",
            "package": "5.16-gal Keg",
            "available": 6,
        },
        {
            "brand": "Oktoberfest",
            "package": "15.5-gal Keg",
            "available": 5,
        },
    ]

    result = beer30_queries._find_wholesale_package(
        items,
        "keg",
    )

    assert result == [items[1], items[2]]


def test_find_wholesale_package_returns_empty_for_no_match():
    items = [
        {
            "brand": "Beach Boys",
            "package": "16-oz Can [4pk x 6]",
            "available": 1,
        },
    ]

    result = beer30_queries._find_wholesale_package(
        items,
        "keg",
    )

    assert result == []

def test_extract_wholesale_package_type_returns_can():
    result = beer30_queries._extract_wholesale_package_type(
        "How many Into The Haze cans do we have?"
    )

    assert result == "can"


def test_extract_wholesale_package_type_returns_keg():
    result = beer30_queries._extract_wholesale_package_type(
        "How many Oktoberfest kegs are in the Coldbox?"
    )

    assert result == "keg"


def test_extract_wholesale_package_type_returns_none_for_general_question():
    result = beer30_queries._extract_wholesale_package_type(
        "How much Into The Haze do we have wholesale?"
    )

    assert result is None

def test_answer_inventory_question_filters_by_beer_and_package(
    monkeypatch,
):
    items = [
        {
            "brand": "Into The Haze",
            "package": "16-oz Can [4pk x 6]",
            "available": 3,
        },
        {
            "brand": "Into The Haze",
            "package": "15.5-gal Keg",
            "available": 9,
        },
        {
            "brand": "Beach Boys",
            "package": "16-oz Can [4pk x 6]",
            "available": 1,
        },
    ]

    monkeypatch.setattr(
        beer30_queries,
        "get_wholesale_inventory",
        lambda: items,
    )

    result = beer30_queries.answer_inventory_question(
        "How many Into The Haze cans do we have wholesale?"
    )

    assert "Into The Haze" in result
    assert "3.00" in result
    assert "9.00" not in result
    assert "Beach Boys" not in result


def test_answer_inventory_question_filters_by_beer_and_keg(
    monkeypatch,
):
    items = [
        {
            "brand": "Oktoberfest",
            "package": "12-oz Can [6pk x 4]",
            "available": 36,
        },
        {
            "brand": "Oktoberfest",
            "package": "5.16-gal Keg",
            "available": 6,
        },
        {
            "brand": "Oktoberfest",
            "package": "15.5-gal Keg",
            "available": 5,
        },
        {
            "brand": "Beach Boys",
            "package": "15.5-gal Keg",
            "available": 6,
        },
    ]

    monkeypatch.setattr(
        beer30_queries,
        "get_wholesale_inventory",
        lambda: items,
    )

    result = beer30_queries.answer_inventory_question(
        "How many Oktoberfest kegs are in the Coldbox?"
    )

    assert "Oktoberfest" in result
    assert "6.00" in result
    assert "5.00" in result
    assert "36.00" not in result
    assert "Beach Boys" not in result