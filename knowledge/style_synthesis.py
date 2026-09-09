from knowledge.beer_queries import find_ba_style
from knowledge.encyclopedia import get_style
from knowledge.style_crosswalk import find_equivalents


def get_style_sources(style_name):
    """
    Retrieve the BJCP and Brewers Association records for a matched style.

    Returns:
        dict or None containing the BJCP and BA records.
    """

    style_name = style_name.strip()

    relationships = find_equivalents(style_name)

    if not relationships:
        return None

    relationship = relationships[0]

    bjcp_name = relationship["bjcp_name"]
    ba_name = relationship["ba_name"]

    bjcp_style = get_style(bjcp_name)
    ba_style = find_ba_style(ba_name)

    if bjcp_style is None or ba_style is None:
        return None

    return {
        "relationship": relationship,
        "bjcp": bjcp_style,
        "ba": ba_style,
    }


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

    lines = [
        f"*{bjcp['name']}*",
        "",
        "*Style Summary*",
        bjcp["description"],
        "",
        "*Guideline Comparison*",
        "",
        f"*BJCP — {bjcp['source']}*",
        f"OG: {bjcp['typical_og_min']}-{bjcp['typical_og_max']}",
        f"FG: {bjcp['typical_fg_min']}-{bjcp['typical_fg_max']}",
        f"ABV: {bjcp['typical_abv_min']}-{bjcp['typical_abv_max']}%",
        f"IBU: {bjcp['typical_ibu_min']}-{bjcp['typical_ibu_max']}",
        f"SRM: {bjcp['typical_srm_min']}-{bjcp['typical_srm_max']}",
        "",
        f"*Brewers Association — {ba['guideline_year']}*",
        f"OG: {ba['original_gravity']}",
        f"FG: {ba['final_gravity']}",
        f"Alcohol: {ba['alcohol']}",
        f"IBU: {ba['ibu']}",
        f"SRM: {ba['srm']}",
        "",
        "_BJCP and Brewers Association guidelines are shown separately because their specifications may differ._",
    ]

    return "\n".join(lines)