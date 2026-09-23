import json
from pathlib import Path

from knowledge.beer_queries import find_ba_style, search_beers
from knowledge.encyclopedia import get_style
from knowledge.style_crosswalk import find_equivalents


FOH_RELATIONSHIPS_FILE = (
    Path(__file__).parent.parent / "data" / "foh_style_relationships.json"
)

def sg_to_plato(sg):
    """Convert specific gravity to degrees Plato."""
    return (
        135.997 * sg**3
        - 630.272 * sg**2
        + 1111.14 * sg
        - 616.868
    )

def get_style_sources(style_name):
    """
    Retrieve the BJCP and Brewers Association records for a matched style.

    Returns:
        dict or None containing the BJCP and BA records.
    """

    style_name = style_name.strip()

    relationships = find_equivalents(style_name)

    if relationships:
        relationship = relationships[0]

        bjcp_name = relationship["bjcp_name"]
        ba_name = relationship["ba_name"]

        bjcp_style = get_style(bjcp_name)
        ba_style = find_ba_style(ba_name)

        if bjcp_style is not None and ba_style is not None:
            return {
                "relationship": relationship,
                "bjcp": bjcp_style,
                "ba": ba_style,
            }

    # Some BJCP styles do not have a Brewers Association crosswalk.
    # Use the direct BJCP record when one exists.
    bjcp_style = get_style(style_name)

    if bjcp_style is None:
        return None

    return {
        "relationship": None,
        "bjcp": bjcp_style,
        "ba": None,
    }

def load_foh_style_relationships():
    """Load explicit FOH beer-to-style relationships."""
    with open(FOH_RELATIONSHIPS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_foh_style_examples(style_name):
    """
    Find Vanish FOH beers associated with a style.

    Direct style matches use the brewery's stored style exactly.
    Explicit relationships allow a beer to be associated with a
    style without changing its stored FOH style terminology.
    """

    normalized_style = style_name.strip().casefold()

    beers = search_beers("")
    beers_by_name = {
        beer["name"].strip().casefold(): beer
        for beer in beers
    }

    examples = []

    # First, include beers whose stored FOH style exactly matches
    # the requested style.
    for beer in beers:
        beer_style = (beer.get("style") or "").strip()

        if beer_style.casefold() == normalized_style:
            examples.append(
                {
                    "beer": beer["name"],
                    "abv": beer["abv"],
                    "foh_style": beer_style,
                    "relationship": "direct_match",
                    "note": beer.get("recommend_if"),
                }
            )

    # Then include explicitly defined relationships.
    for relationship in load_foh_style_relationships():
        if relationship["style_name"].strip().casefold() != normalized_style:
            continue

        beer = beers_by_name.get(
            relationship["beer_name"].strip().casefold()
        )

        if beer is None:
            continue

        # Avoid adding the same beer twice.
        if any(example["beer"] == beer["name"] for example in examples):
            continue

        examples.append(
            {
                "beer": beer["name"],
                "abv": beer["abv"],
                "foh_style": beer.get("style"),
                "relationship": relationship["relationship"],
                "note": beer.get("recommend_if"),
            }
        )

    return examples


def format_foh_style_examples(style_name):
    """Format concise Vanish FOH examples for the style synthesis response."""

    examples = get_foh_style_examples(style_name)

    if not examples:
        return []

    beer_names = ", ".join(
        example["beer"]
        for example in examples
    )

    return [
        "",
        f"*Vanish Examples:* {beer_names}",
    ]

def format_style_synthesis(style_name):
    """
    Create a combined BJCP/BA summary for a beer style.

    Source-specific guideline ranges remain separate so conflicting
    specifications are not incorrectly combined.
    """

    sources = get_style_sources(style_name)

    if sources is None:
        return None

    bjcp = sources["bjcp"]
    ba = sources["ba"]

    bjcp_og_min = float(bjcp["typical_og_min"])
    bjcp_og_max = float(bjcp["typical_og_max"])
    bjcp_fg_min = float(bjcp["typical_fg_min"])
    bjcp_fg_max = float(bjcp["typical_fg_max"])

    bjcp_og_plato = (
        sg_to_plato(bjcp_og_min),
        sg_to_plato(bjcp_og_max),
    )
    bjcp_fg_plato = (
        sg_to_plato(bjcp_fg_min),
        sg_to_plato(bjcp_fg_max),
    )

    lines = [
        f"*{bjcp['name']}*",
        "",
        "*Style Summary*",
        bjcp["description"],
        "",
        "*Guideline Comparison*",
        "",
        f"*BJCP — {bjcp['source']}*",
        f"OG: {bjcp_og_min:.3f}-{bjcp_og_max:.3f} ({bjcp_og_plato[0]:.1f}-{bjcp_og_plato[1]:.1f} °Plato)",
        f"FG: {bjcp_fg_min:.3f}-{bjcp_fg_max:.3f} ({bjcp_fg_plato[0]:.1f}-{bjcp_fg_plato[1]:.1f} °Plato)",
        f"ABV: {bjcp['typical_abv_min']}-{bjcp['typical_abv_max']}%",
        f"IBU: {bjcp['typical_ibu_min']}-{bjcp['typical_ibu_max']}",
        f"SRM: {bjcp['typical_srm_min']}-{bjcp['typical_srm_max']}",
    ]

    if ba is not None:
        lines.extend(
            [
                "",
                f"*Brewers Association — {ba['guideline_year']}*",
                f"OG: {ba['original_gravity']}",
                f"FG: {ba['final_gravity']}",
                f"Alcohol: {ba['alcohol']}",
                f"IBU: {ba['ibu']}",
                f"SRM: {ba['srm']}",
            ]
        )

    lines.extend(format_foh_style_examples(style_name))

    lines.extend(
        [
            "",
            "_BJCP and Brewers Association guidelines are shown separately because their specifications may differ._",
        ]
    )

    return "\n".join(lines)
