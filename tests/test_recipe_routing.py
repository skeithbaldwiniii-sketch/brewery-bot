from knowledge.ask import answer_question


def test_full_recipe_question_precedes_beer_knowledge(capsys):
    answer_question("What is the recipe for Ghost Fleet?")

    result = capsys.readouterr().out

    assert "Ghost Fleet (10.00)" in result
    assert "Marris Otter - Simpsons" in result
    assert "Rahr - 2row" in result
    assert "Summit" in result


def test_grain_bill_returns_only_grains(capsys):
    answer_question("What is the grain bill for Ghost Fleet?")

    result = capsys.readouterr().out

    assert "Marris Otter - Simpsons" in result
    assert "275.00 lb" in result
    assert "Flaked Oats" in result
    assert "100.00 lb" in result
    assert "Summit" not in result
    assert "Amarillo" not in result


def test_hop_bill_returns_only_hops(capsys):
    answer_question("What is the hop bill for Ghost Fleet?")

    result = capsys.readouterr().out

    assert "Summit" in result
    assert "0.375 lb" in result
    assert "First Wort" in result
    assert "Amarillo" in result
    assert "Dry Hop" in result
    assert "Marris Otter - Simpsons" not in result
