import re

from knowledge.hop_intelligence import get_hop_profile
from knowledge.hop_queries import get_all_hops


def _text(value):
    return (value or "").lower()


def _descriptor_matches(text, keywords):
    """
    Return True when a keyword appears as a complete descriptor.
    """
    text = _text(text)

    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

        if re.search(pattern, text):
            return True

    return False


def _midpoint(min_value, max_value):
    if min_value is None or max_value is None:
        return None

    return (float(min_value) + float(max_value)) / 2


def _alpha_difference(source, candidate):
    source_alpha = _midpoint(
        source["alpha_acid_min"],
        source["alpha_acid_max"],
    )

    candidate_alpha = _midpoint(
        candidate["alpha_acid_min"],
        candidate["alpha_acid_max"],
    )

    if source_alpha is None or candidate_alpha is None:
        return None

    return abs(source_alpha - candidate_alpha)


def _score_substitution(source, candidate):
    """
    Score how suitable a candidate is as a brewing substitute.

    This is intentionally conservative. It is a substitution aid,
    not a claim that two hops are interchangeable in a recipe.
    """

    score = 0
    reasons = []

    # Same underlying hop variety
    source_base = source["base_variety"]
    candidate_base = candidate["base_variety"]

    # Substitution relationship
    relationship = "different variety"

    if source_base and candidate_base:
        if source_base.lower() == candidate_base.lower():
            source_form = source["product_form"]
            candidate_form = candidate["product_form"]

            if source_form and candidate_form and source_form.lower() != candidate_form.lower():
                relationship = "same variety, different form"
            else:
                relationship = "same variety"


    if source_base and candidate_base:
        if source_base.lower() == candidate_base.lower():
            score += 8
            reasons.append("same base hop variety")

    source_type = _text(source["hop_type"])
    candidate_type = _text(candidate["hop_type"])

    source_aroma = " ".join(
        [
            _text(source["aroma_description"]),
            _text(source["flavor_description"]),
            _text(source["common_descriptors"]),
        ]
    )

    candidate_aroma = " ".join(
        [
            _text(candidate["aroma_description"]),
            _text(candidate["flavor_description"]),
            _text(candidate["common_descriptors"]),
        ]
    )

    descriptor_groups = [
        ("tropical", 4),
        ("stone fruit", 4),
        ("berry", 4),
        ("white wine", 4),
        ("grape", 4),
        ("citrus", 3),
        ("pine", 3),
        ("resinous", 3),
        ("floral", 2),
        ("herbal", 2),
        ("spicy", 2),
    ]

    for descriptor, points in descriptor_groups:
        source_has = _descriptor_matches(
            source_aroma,
            [descriptor],
        )

        candidate_has = _descriptor_matches(
            candidate_aroma,
            [descriptor],
        )

        if source_has and candidate_has:
            score += points
            reasons.append(
                f"shared {descriptor} character"
            )

    # Brewing function matters heavily for substitutions.
    #
    # Aroma-to-aroma and dual-purpose-to-dual-purpose
    # substitutions are generally more defensible than
    # crossing between functional categories.
    if source_type and candidate_type:
        if source_type == candidate_type:
            score += 3
            reasons.append("same hop type")
        else:
            score -= 2

    alpha_difference = _alpha_difference(
        source,
        candidate,
    )

    if alpha_difference is not None:
        if alpha_difference <= 2:
            score += 2
            reasons.append("similar alpha-acid range")
        elif alpha_difference <= 4:
            score += 1
            reasons.append("moderately similar alpha-acid range")

    source_uses = _text(source["common_uses"])
    candidate_uses = _text(candidate["common_uses"])

    common_use_groups = [
        ("ipa", "IPA"),
        ("pale ale", "pale ale"),
        ("lager", "lager"),
        ("stout", "stout"),
    ]

    for keyword, label in common_use_groups:
        if (
            _descriptor_matches(source_uses, [keyword])
            and _descriptor_matches(candidate_uses, [keyword])
        ):
            score += 1
            reasons.append(
                f"both commonly used for {label}"
            )

    return score, reasons, relationship


def find_substitutions(name, limit=5):
    """
    Return the best candidate substitutions for a hop.
    """

    source = get_hop_profile(name)

    if not source:
        return []

    candidates = []

    for candidate in get_all_hops():
        if candidate["name"].lower() == source["name"].lower():
            continue

        score, reasons, relationship = _score_substitution(
            source,
            candidate,
        )

        if score <= 0:
            continue

        candidates.append(
            {
                "name": candidate["name"],
                "score": score,
                "reasons": reasons,
                "relationship": relationship,
                "profile": dict(candidate),
            }
        )

    candidates.sort(
        key=lambda item: (
            item["score"],
            len(item["reasons"]),
        ),
        reverse=True,
    )

    return candidates[:limit]

def format_hop_substitutions(name, limit=5):
    """
    Format substitutions for Slack.
    """

    substitutions = find_substitutions(
        name,
        limit,
    )

    if not substitutions:
        return None

    lines = [
        f"Hop substitution options for {name}",
        "",
    ]

    for index, substitution in enumerate(
        substitutions,
        start=1,
    ):
        lines.append(
            f"{index}. {substitution['name']} "
            f"— {substitution['relationship']}"
        )

        reasons = substitution["reasons"][:3]

        if substitution["relationship"] == "same variety, different form":
            source_profile = get_hop_profile(name)
            candidate_profile = substitution["profile"]

            source_form = source_profile["product_form"]
            candidate_form = candidate_profile["product_form"]

            lines.append(
                f"   - Same base hop variety."
            )

            if source_form and candidate_form:
                lines.append(
                    f"   - Different product form: "
                    f"{source_form} → {candidate_form}."
                )

            for reason in reasons:
                if reason == "same base hop variety":
                    continue

                lines.append(
                    f"   - {reason.capitalize()}."
                )

        else:
            for reason in reasons:
                lines.append(
                    f"   - {reason.capitalize()}."
                )

        lines.append("")

    lines.append(
        "Brewing note: These are suggested "
        "substitutions, not guaranteed 1:1 replacements. "
        "For bittering additions, adjust the amount "
        "based on actual alpha acid."
    )

    return "\n".join(lines)