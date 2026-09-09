from knowledge.style_synthesis import (
    get_style_sources,
    format_style_synthesis,    
)

from knowledge.ask import answer_question


def test_general_festbier_question_uses_synthesis():
    result = answer_question("What is Festbier?")

    assert result is not None
    assert "*Festbier*" in result
    assert "*Style Summary*" in result
    assert "*BJCP — BJCP 2021 Beer Style Guidelines*" in result
    assert "*Brewers Association — 2024*" in result

def test_festbier_returns_bjcp_and_ba_sources():
    result = get_style_sources("Festbier")

    assert result is not None

    assert result["relationship"]["relationship"] == "equivalent_to"
    assert result["relationship"]["confidence"] == "high"

    assert result["bjcp"] is not None
    assert result["bjcp"]["name"] == "Festbier"
    assert result["bjcp"]["bjcp_number"] == "4B"

    assert result["ba"] is not None
    assert result["ba"]["name"] == "German-Style Oktoberfest/Festbier"
    assert result["ba"]["guideline_year"] == 2024


def test_unknown_style_returns_none():
    result = get_style_sources("Definitely Not A Beer Style")

    assert result is None

def test_festbier_synthesis_format():
    result = format_style_synthesis("Festbier")

    assert result is not None

    assert "*Festbier*" in result
    assert "*Style Summary*" in result
    assert "A smooth, clean, pale German lager" in result

    assert "*BJCP — BJCP 2021 Beer Style Guidelines*" in result
    assert "OG: 1.054-1.057" in result
    assert "ABV: 5.8-6.3%" in result
    assert "IBU: 18.0-25.0" in result

    assert "*Brewers Association — 2024*" in result
    assert "OG: 1.048-1.056 (11.9-13.8 °Plato)" in result
    assert "Alcohol: 4.0%-4.8% (5.1%-6.1%)" in result
    assert "IBU: 23-29" in result

    assert "guidelines are shown separately" in result
    assert "specifications may differ" in result

def test_bjcp_specific_festbier_question_uses_bjcp_only(capsys):
    answer_question("What does BJCP say about Festbier?")

    captured = capsys.readouterr()
    result = captured.out

    assert "Style: Festbier" in result
    assert "Source: BJCP 2021 Beer Style Guidelines" in result
    assert "Brewers Association" not in result