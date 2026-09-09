from knowledge.ask import answer_question


def test_ba_style_question_routes_to_ba_database():
    result = answer_question(
        "What is the Brewers Association description of "
        "West Coast-Style India Pale Ale?"
    )

    assert result is not None
    assert "West Coast-Style India Pale Ale" in result
    assert "Brewers Association Beer Style Guidelines (2024)" in result
    assert "*Color:* Straw to gold" in result
    assert "IBU: 50-75" in result

def test_ba_style_question_resolves_bjcp_style_name():
    result = answer_question(
        "What does the Brewers Association say about Festbier?"
    )

    assert result is not None
    assert "German-Style Oktoberfest/Festbier" in result
    assert "Brewers Association Beer Style Guidelines (2024)" in result
    assert "IBU: 23-29" in result