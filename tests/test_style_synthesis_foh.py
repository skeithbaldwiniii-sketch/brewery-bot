from knowledge import style_synthesis
from knowledge.encyclopedia import get_style
from knowledge.style_synthesis import format_style_synthesis


def test_direct_foh_style_match(monkeypatch):
    beers = [
        {
            "name": "Darkness",
            "style": "Oatmeal Stout",
            "abv": 5.5,
            "recommend_if": "Someone asks for a stout.",
        }
    ]

    monkeypatch.setattr(
        style_synthesis,
        "search_beers",
        lambda _: beers,
    )

    monkeypatch.setattr(
        style_synthesis,
        "load_foh_style_relationships",
        lambda: [],
    )

    examples = style_synthesis.get_foh_style_examples("Oatmeal Stout")

    assert len(examples) == 1
    assert examples[0]["beer"] == "Darkness"
    assert examples[0]["foh_style"] == "Oatmeal Stout"
    assert examples[0]["relationship"] == "direct_match"


def test_explicit_foh_relationship(monkeypatch):
    beers = [
        {
            "name": "Fields of Gold",
            "style": "Harvest Lager",
            "abv": 5.0,
            "recommend_if": "Lighter alternative to Oktoberfest.",
        }
    ]

    monkeypatch.setattr(
        style_synthesis,
        "search_beers",
        lambda _: beers,
    )

    monkeypatch.setattr(
        style_synthesis,
        "load_foh_style_relationships",
        lambda: [
            {
                "beer_name": "Fields of Gold",
                "style_name": "Festbier",
                "relationship": "recommended_for",
            }
        ],
    )

    examples = style_synthesis.get_foh_style_examples("Festbier")

    assert len(examples) == 1
    assert examples[0]["beer"] == "Fields of Gold"
    assert examples[0]["foh_style"] == "Harvest Lager"
    assert examples[0]["relationship"] == "recommended_for"


def test_explicit_relationship_preserves_foh_style(monkeypatch):
    beers = [
        {
            "name": "The Gr8 Chase",
            "style": "India Pale Ale",
            "abv": 4.9,
            "recommend_if": "Low ABV hoppy beer.",
        }
    ]

    monkeypatch.setattr(
        style_synthesis,
        "search_beers",
        lambda _: beers,
    )

    monkeypatch.setattr(
        style_synthesis,
        "load_foh_style_relationships",
        lambda: [
            {
                "beer_name": "The Gr8 Chase",
                "style_name": "Session IPA",
                "relationship": "falls_into",
            }
        ],
    )

    examples = style_synthesis.get_foh_style_examples("Session IPA")

    assert len(examples) == 1
    assert examples[0]["beer"] == "The Gr8 Chase"
    assert examples[0]["foh_style"] == "India Pale Ale"
    assert examples[0]["relationship"] == "falls_into"


def test_no_foh_examples_returns_empty_list(monkeypatch):
    monkeypatch.setattr(
        style_synthesis,
        "search_beers",
        lambda _: [],
    )

    monkeypatch.setattr(
        style_synthesis,
        "load_foh_style_relationships",
        lambda: [],
    )

    assert style_synthesis.get_foh_style_examples("Nonexistent Style") == []

def test_hazy_ipa_uses_bjcp_guideline_without_ba_crosswalk():
    """BJCP-only styles should still produce guideline synthesis."""

    result = format_style_synthesis("Hazy IPA")

    assert result is not None
    assert "*Hazy IPA*" in result
    assert "*Style Summary*" in result
    assert "intense fruit flavors and aromas" in result
    assert "*BJCP — BJCP 2021 Beer Style Guidelines*" in result
    assert "*Vanish Examples:* Into The Haze, Super Juice, Fire IPA, Ghost Fleet" in result


def test_hazy_ipa_lookup_is_case_insensitive():
    """Normalized style names should find canonical database records."""

    style = get_style("hazy ipa")

    assert style is not None
    assert style["name"] == "Hazy IPA"
    assert style["bjcp_number"] == "21C"
