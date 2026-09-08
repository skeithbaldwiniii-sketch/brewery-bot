import re

from knowledge.hop_intelligence import get_hop_profile
from knowledge.hop_queries import get_all_hops


def _text(value):
    return (value or "").lower()

def _descriptor_matches(text, keywords):
    """
    Return True when a keyword appears as a complete descriptor
    rather than merely as part of another word.
    """
    text = _text(text)

    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

        if re.search(pattern, text):
            return True

    return False


def _score_hops(source_hop, candidates):
    """
    Score hop candidates based on overlapping characteristics.

    This is intentionally deterministic and explainable.
    """

    source = get_hop_profile(source_hop)

    if not source:
        return []

    source_uses = _text(source["common_uses"])

    source_text = _text(source["common_descriptors"])

    results = []

    for candidate in candidates:
        candidate_name = candidate["name"]

        if candidate_name.lower() == source_hop.lower():
            continue

        score = 0
        reasons = []

        candidate_text = _text(candidate["common_descriptors"])

        # ---------------------------------------------------------
        # Aroma / flavor overlap
        # ---------------------------------------------------------

        descriptor_groups = {
            "white wine / grape": {
                "weight": 4,
                "keywords": [
                    "white wine",
                    "white-wine",
                    "grape",
                    "muscat",
                    "muscatel",
                    "wine-like",
                ],
            },
            "tropical": {
                "weight": 3,
                "keywords": [
                    "tropical",
                    "passionfruit",
                    "pineapple",
                    "mango",
                    "papaya",
                ],
            },
            "stone fruit": {
                "weight": 3,
                "keywords": [
                    "stone fruit",
                    "peach",
                    "apricot",
                    "nectarine",
                ],
            },
            "berry": {
                "weight": 3,
                "keywords": [
                    "berry",
                    "blueberry",
                    "strawberry",
                    "raspberry",
                ],
            },
            "citrus": {
                "weight": 2,
                "keywords": [
                    "citrus",
                    "grapefruit",
                    "orange",
                    "lemon",
                    "lime",
                ],
            },
            "resinous": {
                "weight": 2,
                "keywords": [
                    "resin",
                    "pine",
                ],
            },
            "floral": {
                "weight": 1,
                "keywords": [
                    "floral",
                    "blossom",
                    "rose",
                ],
            },
            "herbal": {
                "weight": 1,
                "keywords": [
                    "herbal",
                    "tea",
                    "grass",
                ],
            },
            "spicy": {
                "weight": 1,
                "keywords": [
                    "spicy",
                    "spice",
                ],
            },
        }

        for group, data in descriptor_groups.items():
            weight = data["weight"]
            keywords = data["keywords"]
            source_has_group = _descriptor_matches(
                source_text,
                keywords,
            )

            candidate_has_group = _descriptor_matches(
                candidate_text,
                keywords,
            )

            if source_has_group and candidate_has_group:
                score += weight
                reasons.append(
                    f"shared {group} character"
                )


        # ---------------------------------------------------------
        # Common use overlap
        # ---------------------------------------------------------

        common_use_keywords = [
            "ipa",
            "pale ale",
            "double ipa",
            "hazy ipa",
            "dry hop",
            "whirlpool",
        ]

        for keyword in common_use_keywords:
            if (
                keyword in source_uses
                and keyword in _text(candidate["common_uses"])
            ):
                score += 1
                reasons.append(
                    f"both commonly used for {keyword}"
                )
                break

        # ---------------------------------------------------------
        # Alpha acid similarity
        # ---------------------------------------------------------

        source_alpha_min = source["alpha_acid_min"]
        source_alpha_max = source["alpha_acid_max"]

        candidate_alpha_min = candidate["alpha_acid_min"]
        candidate_alpha_max = candidate["alpha_acid_max"]

        if all(
            value is not None
            for value in [
                source_alpha_min,
                source_alpha_max,
                candidate_alpha_min,
                candidate_alpha_max,
            ]
        ):
            source_midpoint = (
                source_alpha_min + source_alpha_max
            ) / 2

            candidate_midpoint = (
                candidate_alpha_min
                + candidate_alpha_max
            ) / 2

            alpha_difference = abs(
                source_midpoint - candidate_midpoint
            )

            if alpha_difference <= 2:
                score += 2
                reasons.append(
                    "similar alpha-acid range"
                )

            elif alpha_difference <= 4:
                score += 1
                reasons.append(
                    "moderately similar alpha-acid range"
                )

        if score > 0:
            results.append(
                {
                    "name": candidate_name,
                    "score": score,
                    "reasons": reasons,
                }
            )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["name"],
        )
    )

    return results


def recommend_hops(name, limit=5):
    """
    Return the strongest deterministic hop recommendations.
    """

    candidates = get_all_hops()

    results = _score_hops(name, candidates)

    return results[:limit]


def format_hop_recommendations(name, limit=5):
    """
    Format hop recommendations for Brews Springsteen.
    """

    source = get_hop_profile(name)

    if not source:
        return None

    recommendations = recommend_hops(name, limit)

    if not recommendations:
        return None

    lines = [
        f"Hop recommendations for {source['name']}",
        "",
    ]

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        lines.append(
            f"{index}. {recommendation['name']}"
        )

        if recommendation["reasons"]:
            for reason in recommendation["reasons"][:3]:
                lines.append(
                    f"   - {reason.capitalize()}."
                )

        lines.append("")

    return "\n".join(lines).rstrip()