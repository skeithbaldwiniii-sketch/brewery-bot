from knowledge.hop_queries import search_exact_hop, get_all_hops


def get_hop_profile(name):
    """
    Return a single hop profile as a dictionary.

    Returns None if the hop does not exist.
    """

    rows = search_exact_hop(name)

    if not rows:
        return None

    return dict(rows[0])


def extract_hop_name(question):
    """
    Extract a recognized hop name from a natural-language question.

    Returns the exact database hop name if one is found.
    Returns None if no hop is recognized.
    """

    question = question.strip()

    if not question:
        return None

    question_lower = question.lower()

    # Explicit aliases for database/product names.
    aliases = {
        "nelson sauvin": "Nelson",
        "hallertau mittelfrüh": "Mittelfruh",
        "hallertau mittelfruh": "Mittelfruh",
        "trident": "Trident Lupulin",
    }

    # Check explicit aliases first.
    for alias, hop_name in aliases.items():
        if alias in question_lower:
            return hop_name

    # Otherwise check database names.
    hops = get_all_hops()

    # Check longer names first so:
    # "Cryo Citra" matches before "Citra".
    hops = sorted(
        hops,
        key=lambda row: len(row["name"]),
        reverse=True,
    )

    for hop in hops:
        hop_name = hop["name"]

        if hop_name.lower() in question_lower:
            return hop_name

    return None


def format_hop_profile(name):
    """
    Format a hop profile into a human-readable brewery answer.

    Returns None if the hop does not exist.
    """

    hop = get_hop_profile(name)

    if not hop:
        return None

    lines = [
        f"{hop['name']}",
        f"Base variety: {hop['base_variety']}",
        f"Product form: {hop['product_form']}",
    ]

    if hop["origin_country"]:
        origin = hop["origin_country"]

        if hop["origin_region"]:
            origin += f" — {hop['origin_region']}"

        lines.append(f"Origin: {origin}")

    if hop["developer"]:
        lines.append(f"Developer: {hop['developer']}")

    if hop["released_year"]:
        lines.append(f"Released: {hop['released_year']}")

    if hop["hop_type"]:
        lines.append(f"Type: {hop['hop_type']}")

    if hop["alpha_acid_min"] is not None:
        lines.append(
            f"Alpha acid: {hop['alpha_acid_min']:.1f}–"
            f"{hop['alpha_acid_max']:.1f}%"
        )

    if hop["beta_acid_min"] is not None:
        lines.append(
            f"Beta acid: {hop['beta_acid_min']:.1f}–"
            f"{hop['beta_acid_max']:.1f}%"
        )

    if hop["cohumulone_min"] is not None:
        lines.append(
            f"Cohumulone: {hop['cohumulone_min']:.1f}–"
            f"{hop['cohumulone_max']:.1f}%"
        )

    if hop["oil_total_min"] is not None:
        lines.append(
            f"Total oil: {hop['oil_total_min']:.1f}–"
            f"{hop['oil_total_max']:.1f} mL/100g"
        )

    if hop["aroma_description"]:
        lines.append(f"Aroma: {hop['aroma_description']}")

    if hop["flavor_description"]:
        lines.append(f"Flavor: {hop['flavor_description']}")

    if hop["common_descriptors"]:
        lines.append(f"Descriptors: {hop['common_descriptors']}")

    if hop["common_uses"]:
        lines.append(f"Common uses: {hop['common_uses']}")

    if hop["brewing_notes"]:
        lines.append(f"Brewing notes: {hop['brewing_notes']}")

    return "\n".join(lines)