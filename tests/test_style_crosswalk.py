from knowledge.style_crosswalk import find_relationships, find_equivalents


def test_festbier_crosswalk():
    relationships = find_relationships("Festbier")

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship["bjcp_name"] == "Festbier"
    assert relationship["ba_name"] == "German-Style Oktoberfest/Festbier"
    assert relationship["relationship"] == "equivalent_to"
    assert relationship["confidence"] == "high"


def test_festbier_equivalent():
    equivalents = find_equivalents("Festbier")

    assert len(equivalents) == 1
    assert equivalents[0]["ba_name"] == "German-Style Oktoberfest/Festbier"