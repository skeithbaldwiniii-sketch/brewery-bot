from integrations.slack import build_answer


def test_build_answer_returns_ba_style_answer():
    result = build_answer(
        "What is the Brewers Association description of "
        "West Coast-Style India Pale Ale?"
    )

    assert result is not None
    assert "West Coast-Style India Pale Ale" in result
    assert "Brewers Association Beer Style Guidelines (2024)" in result
    assert "*Color:* Straw to gold" in result
    assert "IBU: 50-75" in result

def test_build_answer_returns_bjcp_style_answer():
    result = build_answer("What does BJCP say about Festbier?")

    assert result is not None
    assert "Festbier" in result
    assert "BJCP 2021 Beer Style Guidelines" in result
    assert "Typical IBU: 18–25" in result