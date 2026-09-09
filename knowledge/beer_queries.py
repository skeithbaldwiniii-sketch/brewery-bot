import re

from knowledge.database import get_connection


def find_ba_style(style_name):
    """Find an exact Brewers Association style by name."""

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            name,
            guideline_year,
            section,
            subsection,
            page,
            color,
            clarity,
            malt_aroma_flavor,
            hop_aroma_flavor,
            perceived_bitterness,
            fermentation_characteristics,
            body,
            additional_notes,
            original_gravity,
            final_gravity,
            alcohol,
            ibu,
            srm,
            source
        FROM ba_styles
        WHERE LOWER(name) = LOWER(?)
        """,
        (style_name.strip(),),
    ).fetchone()

    connection.close()

    return row

def format_ba_style(ba_style):
    """
    Format a Brewers Association style record for display.
    """

    if ba_style is None:
        return None

    lines = [
        f"*{ba_style['name']}*",
        f"Brewers Association Beer Style Guidelines ({ba_style['guideline_year']})",
    ]

    if ba_style["section"]:
        lines.append(f"Section: {ba_style['section']}")

    if ba_style["subsection"]:
        lines.append(f"Subsection: {ba_style['subsection']}")

    if ba_style["page"]:
        lines.append(f"Page: {ba_style['page']}")

    lines.append("")

    if ba_style["color"]:
        lines.append(f"*Color:* {ba_style['color']}")

    if ba_style["clarity"]:
        lines.append(f"*Clarity:* {ba_style['clarity']}")

    if ba_style["malt_aroma_flavor"]:
        lines.append(
            f"*Perceived Malt Aroma & Flavor:* "
            f"{ba_style['malt_aroma_flavor']}"
        )

    if ba_style["hop_aroma_flavor"]:
        lines.append(
            f"*Perceived Hop Aroma & Flavor:* "
            f"{ba_style['hop_aroma_flavor']}"
        )

    if ba_style["perceived_bitterness"]:
        lines.append(
            f"*Perceived Bitterness:* "
            f"{ba_style['perceived_bitterness']}"
        )

    if ba_style["fermentation_characteristics"]:
        lines.append(
            f"*Fermentation Characteristics:* "
            f"{ba_style['fermentation_characteristics']}"
        )

    if ba_style["body"]:
        lines.append(f"*Body:* {ba_style['body']}")

    if ba_style["additional_notes"]:
        lines.append(
            f"*Additional Notes:* "
            f"{ba_style['additional_notes']}"
        )

    lines.append("")
    lines.append("*Style Statistics:*")

    if ba_style["original_gravity"]:
        lines.append(f"Original Gravity: {ba_style['original_gravity']}")

    if ba_style["final_gravity"]:
        lines.append(f"Final Gravity: {ba_style['final_gravity']}")

    if ba_style["alcohol"]:
        lines.append(f"Alcohol: {ba_style['alcohol']}")

    if ba_style["ibu"]:
        lines.append(f"IBU: {ba_style['ibu']}")

    if ba_style["srm"]:
        lines.append(f"SRM: {ba_style['srm']}")

    return "\n".join(lines)

def find_beer(beer_name):
    """
    Find a brewery beer by exact name.

    Returns a dictionary containing the beer's stored information,
    or None if no matching beer is found.
    """
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                style,
                abv,
                malt,
                hops,
                yeast,
                adjuncts,
                tasting_notes,
                recommend_if
            FROM brewery_beers
            WHERE LOWER(name) = LOWER(?)
            """,
            (beer_name.strip(),),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def search_beers(search_term):
    """
    Search brewery beers by name or style.

    Returns a list of matching beer dictionaries.
    """
    connection = get_connection()

    try:
        pattern = f"%{search_term.strip()}%"

        rows = connection.execute(
            """
            SELECT
                id,
                name,
                style,
                abv,
                malt,
                hops,
                yeast,
                adjuncts,
                tasting_notes,
                recommend_if
            FROM brewery_beers
            WHERE LOWER(name) LIKE LOWER(?)
               OR LOWER(style) LIKE LOWER(?)
            ORDER BY name
            """,
            (pattern, pattern),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


RECOMMENDATION_STOP_WORDS = {
    "what",
    "would",
    "you",
    "recommend",
    "recommendation",
    "recommendations",
    "suggest",
    "suggestion",
    "suggestions",
    "for",
    "someone",
    "somebody",
    "person",
    "people",
    "who",
    "likes",
    "like",
    "liked",
    "wants",
    "want",
    "wanted",
    "something",
    "anything",
    "that",
    "this",
    "they",
    "their",
    "with",
    "from",
    "has",
    "have",
    "had",
    "is",
    "are",
    "was",
    "were",
    "a",
    "an",
    "the",
    "to",
    "of",
    "me",
    "my",
    "i",
    "if",
    "customer",
}


def normalize_recommendation_text(text):
    """
    Normalize text so recommendation matching is
    insensitive to punctuation and capitalization.
    """
    return re.sub(r"[^a-z0-9%]+", " ", text.lower()).strip()


def find_recommendation_matches(question):
    """
    Search brewery recommendation notes for concepts
    mentioned in a natural-language question.

    Returns matching brewery beers ordered by relevance.
    """
    normalized_question = normalize_recommendation_text(question)

    words = [
        word
        for word in normalized_question.split()
        if word not in RECOMMENDATION_STOP_WORDS
    ]

    if not words:
        return []

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                name,
                style,
                abv,
                malt,
                hops,
                yeast,
                adjuncts,
                tasting_notes,
                recommend_if
            FROM brewery_beers
            WHERE recommend_if IS NOT NULL
              AND TRIM(recommend_if) != ''
            ORDER BY name
            """
        ).fetchall()

        matches = []

        for row in rows:
            beer = dict(row)

            recommendation = normalize_recommendation_text(
                beer["recommend_if"]
            )

            score = 0
            matched_words = []

            for word in words:
                if word in recommendation:
                    score += 1
                    matched_words.append(word)

            # Give extra weight to multi-word concepts.
            for index in range(len(words) - 1):
                phrase = f"{words[index]} {words[index + 1]}"

                if phrase in recommendation:
                    score += 2

            if score > 0:
                matches.append(
                    (
                        score,
                        len(matched_words),
                        beer,
                    )
                )

        matches.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2]["name"],
            ),
            reverse=True,
        )

        return [item[2] for item in matches]

    finally:
        connection.close()


def format_recommendation_matches(matches):
    """
    Format brewery beer recommendation matches for Slack.
    """
    if not matches:
        return None

    lines = [
        "*Brewery recommendation:*",
    ]

    for beer in matches[:5]:
        lines.append(
            f"*{beer['name']}* — {beer['recommend_if']}"
        )

    return "\n".join(lines)

def find_beer_name_in_question(question):
    """
    Find a brewery beer name mentioned in a natural-language question.

    Returns the matching beer name, or None if no brewery beer
    is mentioned.
    """
    normalized_question = question.lower()

    beers = search_beers("")

    # Check longer names first so multi-word beer names
    # are matched before shorter names contained within them.
    beers.sort(
        key=lambda beer: len(beer["name"]),
        reverse=True,
    )

    for beer in beers:
        beer_name = beer["name"]

        if beer_name.lower() in normalized_question:
            return beer_name

    return None


def format_beer_summary(beer):
    """
    Create the standard concise brewery beer summary.
    """
    lines = [
        f"*{beer['name']}*",
    ]

    if beer["style"] and beer["abv"] is not None:
        lines.append(
            f"{beer['style']} • {beer['abv']}% ABV"
        )
    elif beer["style"]:
        lines.append(beer["style"])
    elif beer["abv"] is not None:
        lines.append(f"{beer['abv']}% ABV")

    if beer["malt"]:
        lines.append(f"Malt: {beer['malt']}")

    if beer["hops"]:
        lines.append(f"Hops: {beer['hops']}")

    if beer["yeast"]:
        lines.append(f"Yeast: {beer['yeast']}")

    if beer["adjuncts"]:
        lines.append(f"Adjuncts: {beer['adjuncts']}")

    if beer["tasting_notes"]:
        lines.append(f"Tasting: {beer['tasting_notes']}")

    return "\n".join(lines)


def answer_brewery_beer_question(question):
    """
    Answer a brewery-specific beer question using only the
    brewery beer database.

    This includes direct beer questions and recommendation
    questions based on the brewery's recommendation notes.

    Returns None when the question cannot be answered from
    the brewery beer database.
"""
    beer_name = find_beer_name_in_question(question)

    if beer_name is None:
        matches = find_recommendation_matches(question)

        if matches:
            return format_recommendation_matches(matches)

        return None

    beer = find_beer(beer_name)

    if beer is None:
        return None

    question_lower = question.lower()

    # ---------------------------------------------
    # Specific field questions
    # ---------------------------------------------

    if any(
        phrase in question_lower
        for phrase in [
            "what hops",
            "which hops",
            "hops in",
            "hops are in",
            "hop bill",
        ]
    ):
        return f"*{beer['name']} — Hops:* {beer['hops'] or 'Not specified'}"

    if any(
        phrase in question_lower
        for phrase in [
            "what malt",
            "which malt",
            "malt in",
            "malt bill",
            "grain bill",
            "grains in",
        ]
    ):
        return f"*{beer['name']} — Malt:* {beer['malt'] or 'Not specified'}"

    if any(
        phrase in question_lower
        for phrase in [
            "what yeast",
            "which yeast",
            "yeast in",
        ]
    ):
        return f"*{beer['name']} — Yeast:* {beer['yeast'] or 'Not specified'}"

    if any(
        phrase in question_lower
        for phrase in [
            "what abv",
            "what is the abv",
            "what's the abv",
            "alcohol content",
            "how strong",
        ]
    ):
        if beer["abv"] is None:
            return f"*{beer['name']} — ABV:* Not specified"

        return f"*{beer['name']} — ABV:* {beer['abv']}%"

    if any(
        phrase in question_lower
        for phrase in [
            "what style",
            "which style",
            "style is",
            "what kind of beer",
            "what type of beer",
        ]
    ):
        return (
            f"*{beer['name']} — Style:* "
            f"{beer['style'] or 'Not specified'}"
        )

    if any(
        phrase in question_lower
        for phrase in [
            "what adjunct",
            "which adjunct",
            "adjuncts in",
            "what's in it",
            "what is in it",
        ]
    ):
        return (
            f"*{beer['name']} — Adjuncts:* "
            f"{beer['adjuncts'] or 'None specified'}"
        )

    if any(
        phrase in question_lower
        for phrase in [
            "taste",
            "tasting notes",
            "flavor",
            "flavors",
            "describe the taste",
            "describe the flavor",
        ]
    ):
        return (
            f"*{beer['name']} — Tasting:* "
            f"{beer['tasting_notes'] or 'Not specified'}"
        )

    if any(
        phrase in question_lower
        for phrase in [
            "recommend",
            "recommendation",
            "who would like",
            "good for someone",
            "good for somebody",
            "what should i suggest",
            "what should i recommend",
        ]
    ):
        return (
            f"*{beer['name']} — Recommendation:* "
            f"{beer['recommend_if'] or 'No recommendation specified'}"
        )

    # ---------------------------------------------
    # Broad beer question
    # ---------------------------------------------

    return format_beer_summary(beer)


def answer_beer_question(beer_name):
    """
    Backward-compatible exact beer lookup.
    """
    beer = find_beer(beer_name)

    if beer is None:
        return f"I couldn't find a brewery beer named '{beer_name}'."

    return format_beer_summary(beer)

def answer_ba_style_question(style_name):
    """
    Answer a Brewers Association beer style question.

    Returns formatted BA style information, or None if the
    style is not found in the Brewers Association database.
    """
    style_name = style_name.strip()

    prefixes = [
        "brewers association description of ",
        "brewers association details of ",
        "brewers association information on ",
        "brewers association information for ",
    ]

    for prefix in prefixes:
        if style_name.lower().startswith(prefix):
            style_name = style_name[len(prefix):].strip()
            break

    ba_style = find_ba_style(style_name)

    if ba_style is None:
        return None

    return format_ba_style(ba_style)

if __name__ == "__main__":
    print("=== Brewery Beer Question Tests ===")

    questions = [
        "What hops are in Ghost Fleet?",
        "What malt is in Ghost Fleet?",
        "What yeast is in Ghost Fleet?",
        "What is the ABV of Ghost Fleet?",
        "What style is Ghost Fleet?",
        "How does Ghost Fleet taste?",
        "What should I recommend for someone who likes Hazy Little Thing?",
        "Tell me about Ghost Fleet.",
        "What's in Hacienda?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        print(f"A: {answer_brewery_beer_question(question)}")