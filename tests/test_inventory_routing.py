from knowledge.ask import answer_question


def test_wholesale_inventory_question_precedes_beer_knowledge(capsys):
    answer_question(
        "How many kegs of Oktoberfest are in the Coldbox?"
    )

    result = capsys.readouterr().out

    assert "Current wholesale inventory:" in result
    assert "Oktoberfest: 6.00 5.16-gal Keg" in result
    assert "Oktoberfest: 5.00 15.5-gal Keg" in result
    assert "6.0% ABV" not in result
