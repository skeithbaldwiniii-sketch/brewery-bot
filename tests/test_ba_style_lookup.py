from knowledge.beer_queries import find_ba_style


def test_find_ba_style():
    row = find_ba_style("West Coast-Style India Pale Ale")

    assert row is not None
    assert row["name"] == "West Coast-Style India Pale Ale"
    assert row["guideline_year"] == 2024
    assert row["section"] == "Ale Styles"
    assert row["subsection"] == "North American Origin Ale Styles"
    assert row["page"] == 11


def test_find_ba_style_case_insensitive():
    row = find_ba_style("west coast-style india pale ale")

    assert row is not None
    assert row["name"] == "West Coast-Style India Pale Ale"


def test_find_ba_style_missing():
    row = find_ba_style("Definitely Not A Real Beer Style")

    assert row is None