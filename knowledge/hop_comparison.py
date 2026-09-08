from knowledge.hop_intelligence import (
    extract_hop_name,
    get_hop_profile,
)


def compare_hops(name1, name2):
    """
    Compare two hop profiles.

    Returns a dictionary containing both hop profiles,
    or None if either hop does not exist.
    """

    hop1 = get_hop_profile(name1)
    hop2 = get_hop_profile(name2)

    if not hop1 or not hop2:
        return None

    return {
        "hop1": hop1,
        "hop2": hop2,
    }

def format_hop_comparison(name1, name2):
    """
    Format two hop profiles into a human-readable comparison.

    Returns None if either hop does not exist.
    """

    comparison = compare_hops(name1, name2)

    if not comparison:
        return None

    hop1 = comparison["hop1"]
    hop2 = comparison["hop2"]

    lines = [
        f"{hop1['name']} vs {hop2['name']}",
        "",
    ]

    if hop1["origin_country"] or hop2["origin_country"]:
        lines.append("Origin:")

        origin1 = hop1["origin_country"] or "Unknown"
        origin2 = hop2["origin_country"] or "Unknown"

        if hop1["origin_region"]:
            origin1 += f" — {hop1['origin_region']}"

        if hop2["origin_region"]:
            origin2 += f" — {hop2['origin_region']}"

        lines.append(f"  {hop1['name']}: {origin1}")
        lines.append(f"  {hop2['name']}: {origin2}")
        lines.append("")

    if hop1["hop_type"] or hop2["hop_type"]:
        lines.append("Type:")
        lines.append(
            f"  {hop1['name']}: {hop1['hop_type'] or 'Unknown'}"
        )
        lines.append(
            f"  {hop2['name']}: {hop2['hop_type'] or 'Unknown'}"
        )
        lines.append("")

    if hop1["alpha_acid_min"] is not None or hop2["alpha_acid_min"] is not None:
        lines.append("Alpha acid:")

        if hop1["alpha_acid_min"] is not None:
            lines.append(
                f"  {hop1['name']}: "
                f"{hop1['alpha_acid_min']:.1f}–"
                f"{hop1['alpha_acid_max']:.1f}%"
            )

        if hop2["alpha_acid_min"] is not None:
            lines.append(
                f"  {hop2['name']}: "
                f"{hop2['alpha_acid_min']:.1f}–"
                f"{hop2['alpha_acid_max']:.1f}%"
            )

        lines.append("")

    if hop1["beta_acid_min"] is not None or hop2["beta_acid_min"] is not None:
        lines.append("Beta acid:")

        if hop1["beta_acid_min"] is not None:
            lines.append(
                f"  {hop1['name']}: "
                f"{hop1['beta_acid_min']:.1f}–"
                f"{hop1['beta_acid_max']:.1f}%"
            )

        if hop2["beta_acid_min"] is not None:
            lines.append(
                f"  {hop2['name']}: "
                f"{hop2['beta_acid_min']:.1f}–"
                f"{hop2['beta_acid_max']:.1f}%"
            )

        lines.append("")

    if hop1["cohumulone_min"] is not None or hop2["cohumulone_min"] is not None:
        lines.append("Cohumulone:")

        if hop1["cohumulone_min"] is not None:
            lines.append(
                f"  {hop1['name']}: "
                f"{hop1['cohumulone_min']:.1f}–"
                f"{hop1['cohumulone_max']:.1f}%"
            )

        if hop2["cohumulone_min"] is not None:
            lines.append(
                f"  {hop2['name']}: "
                f"{hop2['cohumulone_min']:.1f}–"
                f"{hop2['cohumulone_max']:.1f}%"
            )

        lines.append("")

    if hop1["aroma_description"] or hop2["aroma_description"]:
        lines.append("Aroma:")

        if hop1["aroma_description"]:
            lines.append(
                f"  {hop1['name']}: {hop1['aroma_description']}"
            )

        if hop2["aroma_description"]:
            lines.append(
                f"  {hop2['name']}: {hop2['aroma_description']}"
            )

        lines.append("")

    if hop1["common_uses"] or hop2["common_uses"]:
        lines.append("Common uses:")

        if hop1["common_uses"]:
            lines.append(
                f"  {hop1['name']}: {hop1['common_uses']}"
            )

        if hop2["common_uses"]:
            lines.append(
                f"  {hop2['name']}: {hop2['common_uses']}"
            )

    return "\n".join(lines)

def extract_two_hop_names(question):
    """
    Extract two recognized hop names from a natural-language question.

    Returns a tuple containing the two database hop names
    in the order they appear in the question.

    Returns None if two hops cannot be identified.
    """

    question = question.strip()

    if not question:
        return None

    question_lower = question.lower()

    from knowledge.hop_queries import get_all_hops

    hops = get_all_hops()

    # Explicit aliases.
    aliases = {
        "nelson sauvin": "Nelson",
        "hallertau mittelfrüh": "Mittelfruh",
        "hallertau mittelfruh": "Mittelfruh",
        "trident": "Trident Lupulin",
    }

    candidates = []

    # Add aliases as candidates.
    for alias, hop_name in aliases.items():
        start = question_lower.find(alias)

        if start != -1:
            candidates.append(
                (start, len(alias), hop_name)
            )

    # Add database names as candidates.
    for hop in hops:
        hop_name = hop["name"]

        start = question_lower.find(hop_name.lower())

        if start != -1:
            candidates.append(
                (start, len(hop_name), hop_name)
            )

    # Sort by where the name appears in the question.
    # For identical starting positions, prefer the longer name.
    candidates.sort(
        key=lambda item: (item[0], -item[1])
    )

    matches = []

    for _, _, hop_name in candidates:
        if hop_name not in matches:
            matches.append(hop_name)

    if len(matches) < 2:
        return None

    return matches[0], matches[1]