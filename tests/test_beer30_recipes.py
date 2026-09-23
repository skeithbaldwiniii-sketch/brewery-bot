from intelligence.beer30_recipes import (
    _parse_recipe_question,
    answer_recipe_question,
    is_recipe_question,
)


def test_recipe_question_parser():
    result = _parse_recipe_question(
        "What is the recipe for Ghost Fleet?"
    )

    assert result == {
        "intent": "recipe",
        "beer_name": "Ghost Fleet",
    }


def test_grain_bill_question_parser():
    result = _parse_recipe_question(
        "What is the grain bill for Ghost Fleet?"
    )

    assert result == {
        "intent": "grain_bill",
        "beer_name": "Ghost Fleet",
    }


def test_hop_bill_question_parser():
    result = _parse_recipe_question(
        "What is the hop bill for Ghost Fleet?"
    )

    assert result == {
        "intent": "hop_bill",
        "beer_name": "Ghost Fleet",
    }


def test_non_recipe_question_does_not_trigger():
    assert is_recipe_question("What is Ghost Fleet?") is False
    assert is_recipe_question("What is in Ghost Fleet?") is False
    assert is_recipe_question("Tell me about Ghost Fleet") is False


def test_full_recipe_answer_contains_recipe_sections():
    result = answer_recipe_question(
        "What is the recipe for Ghost Fleet?"
    )

    assert "Ghost Fleet (10.00)" in result
    assert "Recipe version: 8" in result
    assert "Batch size: 10.00" in result
    assert "Grains:" in result
    assert "Hops:" in result
    assert "Marris Otter - Simpsons: 275.00 lb" in result
    assert "Summit: 0.375 lb (First Wort)" in result


def test_grain_bill_answer_excludes_hops():
    result = answer_recipe_question(
        "What is the grain bill for Ghost Fleet?"
    )

    assert "Grain bill:" in result
    assert "Marris Otter - Simpsons: 275.00 lb" in result
    assert "Flaked Oats: 100.00 lb" in result
    assert "Summit" not in result
    assert "Amarillo" not in result


def test_hop_bill_answer_includes_process():
    result = answer_recipe_question(
        "What is the hop bill for Ghost Fleet?"
    )

    assert "Hop bill:" in result
    assert "Summit: 0.375 lb (First Wort)" in result
    assert "Amarillo: 3.125 lb (Whirlpool)" in result
    assert "Amarillo: 4.00 lb (Dry Hop)" in result
    assert "Marris Otter - Simpsons" not in result
