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