from knowledge.beer_queries import find_ba_style, format_ba_style


def test_format_ba_style():
    row = find_ba_style("West Coast-Style India Pale Ale")

    result = format_ba_style(row)

    assert "*Color:* Straw to gold" in result
    assert "*Perceived Malt Aroma & Flavor:*" in result
    assert "*Perceived Hop Aroma & Flavor:*" in result
    assert "*Perceived Bitterness:*" in result
    assert "*Fermentation Characteristics:*" in result
    assert "*Body:* Low to medium" in result
    assert "Original Gravity: 1.055-1.070" in result
    assert "Final Gravity: 1.005-1.012" in result
    assert "Alcohol: 5.0%-6.0%" in result
    assert "IBU: 50-75" in result
    assert "SRM: 2-6" in result

def test_format_ba_style_missing():
    result = format_ba_style(None)

    assert result is None