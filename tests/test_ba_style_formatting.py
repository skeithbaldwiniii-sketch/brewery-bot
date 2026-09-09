from knowledge.beer_queries import find_ba_style, format_ba_style


def test_format_ba_style():
    row = find_ba_style("West Coast-Style India Pale Ale")

    result = format_ba_style(row)

    assert "*West Coast-Style India Pale Ale*" in result
    assert "Brewers Association Beer Style Guidelines (2024)" in result
    assert "Section: Ale Styles" in result
    assert "Subsection: North American Origin Ale Styles" in result
    assert "Page: 11" in result


def test_format_ba_style_missing():
    result = format_ba_style(None)

    assert result is None