import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "style_crosswalk.json"


def load_crosswalk():
    """Load the BJCP/BA style relationship crosswalk."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_relationships(style_name):
    """Return all crosswalk relationships involving a style name."""

    style_name = style_name.strip().lower()

    relationships = load_crosswalk()

    return [
        relationship
        for relationship in relationships
        if (
            relationship["bjcp_name"].lower() == style_name
            or relationship["ba_name"].lower() == style_name
        )
    ]


def find_equivalents(style_name):
    """Return styles that are explicitly equivalent to the supplied style."""

    return [
        relationship
        for relationship in find_relationships(style_name)
        if relationship["relationship"] == "equivalent_to"
    ]


def find_related_styles(style_name):
    """Return non-equivalent style relationships."""

    return [
        relationship
        for relationship in find_relationships(style_name)
        if relationship["relationship"] != "equivalent_to"
    ]

def find_all_equivalents():
    """Return all explicit equivalent style relationships."""

    return [
        relationship
        for relationship in load_crosswalk()
        if relationship["relationship"] == "equivalent_to"
    ]