import unicodedata

from knowledge.database import get_connection
from knowledge.beer_queries import (
    answer_beer_question,
    answer_ba_style_question,
)
from knowledge.hop_intelligence import (
    extract_hop_name,
    format_hop_profile,
)

from knowledge.style_aliases import STYLE_ALIASES
from knowledge.style_crosswalk import find_all_equivalents

from knowledge.hop_comparison import (
    extract_two_hop_names,
    format_hop_comparison,
)

from knowledge.hop_recommendations import (
    recommend_hops,
    format_hop_recommendations,
)
from knowledge.hop_substitutions import (
    format_hop_substitutions,
)

from intelligence.beer30_queries import (
    is_wip_question,
    answer_wip_question,
)

STYLE_FAMILIES = {
    "ipa": "IPA",
    "lager": "Lager",
    "ale": "Ale",
    "stout": "Stout",
    "porter": "Porter",
    "sour": "Sour",
}

STYLE_FAMILIES = {
    "ipa": "IPA",
    "lager": "Lager",
    "ale": "Ale",
    "stout": "Stout",
    "porter": "Porter",
    "sour": "Sour",
}

last_style_list = {}



def normalize_style_name(name):
    """Normalize a beer style name for matching."""

    name = unicodedata.normalize("NFKD", name)
    name = "".join(
        character
        for character in name
        if not unicodedata.combining(character)
    )

    name = name.lower().strip()

    if name.startswith("historical beer:"):
        name = name[len("historical beer:"):].strip()

    if name in STYLE_ALIASES:
        return STYLE_ALIASES[name]

    for relationship in find_all_equivalents():
        bjcp_name = relationship["bjcp_name"].lower()
        ba_name = relationship["ba_name"].lower()

        if name == bjcp_name:
            return bjcp_name

        if name == ba_name:
            return bjcp_name

    return name


def search_exact_style(question):
    """Look for an exact beer style name using normalized names."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM beer_styles
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    normalized_question = normalize_style_name(question)

    matches = []

    for row in rows:
        normalized_name = normalize_style_name(row["name"])

        if normalized_name == normalized_question:
            matches.append(row)

    return matches


def search_style_family(family):
    """Find beer styles belonging to a style family."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM beer_styles
        WHERE LOWER(category) LIKE ?
           OR LOWER(name) LIKE ?
        ORDER BY name
        """,
        (
            f"%{family.lower()}%",
            f"%{family.lower()}%",
        ),
    ).fetchall()

    connection.close()

    return rows


def search_encyclopedia(term):
    """Search general encyclopedia entries."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM encyclopedia_entries
        WHERE LOWER(title) LIKE ?
           OR LOWER(category) LIKE ?
        ORDER BY title
        """,
        (
            f"%{term.lower()}%",
            f"%{term.lower()}%",
        ),
    ).fetchall()

    connection.close()

    return rows


def clean_question(question):
    """Remove common conversational wording."""

    question = question.lower().strip()

    prefixes = [
        "what is ",
        "what's ",
        "tell me about ",
        "tell me the history of ",
        "what is the history of ",
        "what's the history of ",
        "history of ",
        "give me the full description of ",
        "give me the full details of ",
        "give me the complete description of ",
        "give me the complete details of ",
    ]

    for prefix in prefixes:
        if question.startswith(prefix):
            question = question[len(prefix):]
            break

    question = question.rstrip("?.!")

    # Remove common articles left at the beginning
    articles = [
        "a ",
        "an ",
        "the ",
    ]

    for article in articles:
        if question.startswith(article):
            question = question[len(article):]
            break

    return question.strip()

def display_style(style, question=None):
    question_lower = (question or "").lower()

    full_detail_phrases = [
        "full description",
        "full details",
        "full detail",
        "complete description",
        "complete details",
        "complete detail",
        "detailed description",
        "detailed details",
        "all the details",
        "everything about",
        "full bjcp",
        "bjcp description",
    ]

    full_detail = any(
        phrase in question_lower
        for phrase in full_detail_phrases
    )
    """Display a beer style record."""

    print("Brews Springsteen:")
    print("-" * 50)

    print(f"Style: {style['name']}")
    print(f"Category: {style['category']}")
    origin = style["country_of_origin"] or "Not specified"
    print(f"Origin: {origin}")

    if full_detail:
        if style["history"]:
            print(f"\nHistory: {style['history']}")

        if style["description"]:
            print(f"\nDescription: {style['description']}")

        if style["aroma"]:
            print(f"Aroma: {style['aroma']}")

        if style["appearance"]:
            print(f"Appearance: {style['appearance']}")

        if style["flavor"]:
            print(f"Flavor: {style['flavor']}")

        if style["mouthfeel"]:
            print(f"Mouthfeel: {style['mouthfeel']}")

        if style["ingredients"]:
            print(f"\nIngredients: {style['ingredients']}")

    if style["typical_abv_min"] is not None:
        print(
            f"\nTypical ABV: "
            f"{style['typical_abv_min']:.1f}%–"
            f"{style['typical_abv_max']:.1f}%"
        )

    if style["typical_ibu_min"] is not None:
        print(
            f"Typical IBU: "
            f"{style['typical_ibu_min']:.0f}–"
            f"{style['typical_ibu_max']:.0f}"
        )

    if style["typical_og_min"] is not None:
        print(
            f"Typical OG: "
            f"{style['typical_og_min']:.3f}–"
            f"{style['typical_og_max']:.3f}"
        )

    if style["typical_fg_min"] is not None:
        print(
            f"Typical FG: "
            f"{style['typical_fg_min']:.3f}–"
            f"{style['typical_fg_max']:.3f}"
        )

    if style["typical_srm_min"] is not None:
        print(
            f"Typical SRM: "
            f"{style['typical_srm_min']:.0f}–"
            f"{style['typical_srm_max']:.0f}"
        )

    if not full_detail and style["description"]:
        print(f"\n{style['description']}")
    print(f"\nSource: {style['source']}")
    print("-" * 50)


def display_entry(entry):
    """Display a general encyclopedia entry."""

    print("Brews Springsteen:")
    print("-" * 50)

    print(f"Topic: {entry['title']}")
    print(f"Category: {entry['category']}")

    print(f"\n{entry['content']}")

    print(f"\nSource: {entry['source']}")
    print("-" * 50)

def search_styles_by_names(names):
    """Find exact styles by a list of names."""

    connection = get_connection()

    results = []

    for name in names:
        row = connection.execute(
            """
            SELECT *
            FROM beer_styles
            WHERE LOWER(name) = LOWER(?)
            """,
            (name.strip(),),
        ).fetchone()

        if row:
            results.append(row)

    connection.close()

    return results

def display_history(style):
    """Display the historical information for a beer style."""

    print("Brews Springsteen:")
    print("-" * 50)

    print(f"Style: {style['name']}")

    if style["bjcp_number"]:
        print(f"BJCP: {style['bjcp_number']}")

    if style["history"]:
        print(f"\nHistory:\n{style['history']}")
    else:
        print("\nNo historical information is currently available.")

    print(f"\nSource: {style['source']}")
    print("-" * 50)

def display_comparison(styles):
    """Compare two beer styles."""

    print("Brews Springsteen:")
    print("-" * 50)

    print(f"COMPARING {styles[0]['name']} vs. {styles[1]['name']}")
    print()

    fields = [
        ("Category", "category"),
        ("Description", "description"),
        ("Aroma", "aroma"),
        ("Appearance", "appearance"),
        ("Flavor", "flavor"),
        ("Mouthfeel", "mouthfeel"),
        ("Ingredients", "ingredients"),
    ]

    for label, field in fields:
        print(f"{label}:")
        print(f"  {styles[0]['name']}:")
        print(f"    {styles[0][field] or 'N/A'}")
        print(f"  {styles[1]['name']}:")
        print(f"    {styles[1][field] or 'N/A'}")
        print()

    print("Brewing Metrics:")

    metric_labels = [
        ("ABV", "typical_abv_min", "typical_abv_max", "%"),
        ("IBU", "typical_ibu_min", "typical_ibu_max", ""),
        ("OG", "typical_og_min", "typical_og_max", ""),
        ("FG", "typical_fg_min", "typical_fg_max", ""),
        ("SRM", "typical_srm_min", "typical_srm_max", ""),
    ]

    for label, min_field, max_field, suffix in metric_labels:
        print(f"\n{label}:")

        for style in styles:
            minimum = style[min_field]
            maximum = style[max_field]

            if minimum is None or maximum is None:
                value = "N/A"
            elif label == "ABV":
                value = f"{minimum:.1f}–{maximum:.1f}%"
            elif label in ("OG", "FG"):
                value = f"{minimum:.3f}–{maximum:.3f}"
            else:
                value = f"{minimum:.0f}–{maximum:.0f}"

            print(f"  {style['name']}: {value}")

    print("\nSources:")
    for style in styles:
        print(f"  {style['name']}: {style['source']}")

    print("-" * 50)

def answer_question(question):
    """Determine what the user is asking and return an answer."""
    global last_style_list

    cleaned = clean_question(question)

    # ---------------------------------------------------------
    # STYLE NUMBER SELECTION
    # ---------------------------------------------------------

    if cleaned.isdigit() or cleaned.startswith("#") or cleaned.startswith("number "):
        selection = cleaned.replace("#", "").replace("number ", "").strip()

        if selection.isdigit():
            number = int(selection)

            if number in last_style_list:
                style_name = last_style_list[number]
                styles = search_exact_style(style_name)

                if styles:
                    display_style(styles[0], question)
                    return

    # ---------------------------------------------------------
    # TASK / SCHEDULE QUESTIONS
    # ---------------------------------------------------------
    #
    # Let the task-intelligence system handle brewery
    # schedule questions before checking the beer encyclopedia.
    #
    # Examples:
    #   "When are we releasing Festbier?"
    #   "What day are we doing Festbier?"
    #   "What is on the schedule for Wednesday?"
    #   "What is left today?"
    #
    # Import here instead of at the top of the file so the
    # encyclopedia system remains independent from the task
    # intelligence system.
    #
    from intelligence.task_queries import answer_task_question

    task_answer = answer_task_question(question)

    if task_answer:
        print(task_answer)
        return

    # ---------------------------------------------------------
    # BEER30 WIP QUESTIONS
    # ---------------------------------------------------------

    if is_wip_question(question):
        print(answer_wip_question(question))
        return

    cleaned = clean_question(question)

        # ---------------------------------------------------------
    # HISTORY QUESTIONS
    # ---------------------------------------------------------

    history_question = (
        "history" in question.lower()
        or "historical" in question.lower()
    )

    if history_question:

        history_name = cleaned

        for phrase in [
            "history",
            "historical",
            "of",
        ]:
            history_name = history_name.replace(phrase, " ")

        history_name = " ".join(history_name.split()).strip()

        styles = search_exact_style(history_name)

        if styles:
            display_history(styles[0])
            return

        # ---------------------------------------------------------
    # COMPARISON QUESTIONS
    # ---------------------------------------------------------

    comparison_words = [
        "compare",
        "comparison",
        "difference",
        "differ",
        "versus",
        " vs ",
    ]

    is_comparison = any(
        word in question.lower()
        for word in comparison_words
    )

    if is_comparison:

        comparison_text = question.lower()

        for phrase in [
            "what's the difference between",
            "what is the difference between",
            "what's the difference between",
            "compare",
            "comparison of",
            "difference between",
            "difference of",
            "versus",
        ]:
            comparison_text = comparison_text.replace(
                phrase,
                " "
            )

        comparison_text = comparison_text.replace(" vs ", "|")
        comparison_text = comparison_text.replace(" and ", "|")
        comparison_text = comparison_text.replace(" to ", "|")

        comparison_text = comparison_text.rstrip("?.!")

        names = [
            name.strip()
            for name in comparison_text.split("|")
            if name.strip()
        ]

        if len(names) == 2:

            styles = search_styles_by_names(names)

            if len(styles) == 2:
                display_comparison(styles)
                return

    

    # ---------------------------------------------------------
    # 1. METRIC QUESTIONS
    # ---------------------------------------------------------

    metric_words = {
        "abv": "typical_abv",
        "ibu": "typical_ibu",
        "og": "typical_og",
        "fg": "typical_fg",
        "srm": "typical_srm",
    }

    requested_metric = None

    for word, field in metric_words.items():
        if word in cleaned:
            requested_metric = field
            break

    if requested_metric:
        # Remove common metric wording so we can identify the style.
        style_name = cleaned

        phrases_to_remove = [
            "abv",
            "ibu",
            "og",
            "fg",
            "srm",
            "of",
            "range",
            "typical",
            "what is",
            "whats",
            "the",
        ]

        for phrase in phrases_to_remove:
            style_name = style_name.replace(phrase, " ")

        style_name = " ".join(style_name.split()).strip()

        styles = search_exact_style(style_name)

        if styles:
            style = styles[0]

            min_value = style[f"{requested_metric}_min"]
            max_value = style[f"{requested_metric}_max"]

            if min_value is not None and max_value is not None:

                labels = {
                    "typical_abv": "ABV",
                    "typical_ibu": "IBU",
                    "typical_og": "OG",
                    "typical_fg": "FG",
                    "typical_srm": "SRM",
                }

                label = labels[requested_metric]

                if label == "ABV":
                    value = f"{min_value:.1f}%–{max_value:.1f}%"

                elif label == "IBU":
                    value = f"{min_value:.0f}–{max_value:.0f}"

                elif label in ("OG", "FG"):
                    value = f"{min_value:.3f}–{max_value:.3f}"

                else:
                    value = f"{min_value:.0f}–{max_value:.0f}"

                print("Brews Springsteen:")
                print("-" * 50)
                print(f"{style['name']}")
                print(f"Typical {label}: {value}")
                print(f"\nSource: {style['source']}")
                print("-" * 50)

                return

    # ---------------------------------------------------------
    # 2. HOP COMPARISON
    # ---------------------------------------------------------

    hop_names = extract_two_hop_names(question)

    if hop_names:
        hop_comparison = format_hop_comparison(
            hop_names[0],
            hop_names[1],
        )

        if hop_comparison:
            print("Brews Springsteen:")
            print("-" * 50)
            print(hop_comparison)
            print("-" * 50)
            return

        # ---------------------------------------------------------
    # 3. HOP SUBSTITUTIONS
    # ---------------------------------------------------------

    hop_name = extract_hop_name(question)

    if hop_name and any(
        phrase in question.lower()
        for phrase in [
            "substitute for",
            "substitution for",
            "substitutions for",
            "use instead of",
            "instead of",
            "replace",
            "replacement for",
        ]
    ):
        formatted_substitutions = format_hop_substitutions(
            hop_name,
        )

        if formatted_substitutions:
            print("Brews Springsteen:")
            print("-" * 50)
            print(formatted_substitutions)
            print("-" * 50)
            return

    # 3. HOP RECOMMENDATIONS
    hop_name = extract_hop_name(question)

    if hop_name and any(
        phrase in question.lower()
        for phrase in [
            "similar hops",
            "similar to",
            "hops like",
            "recommend hops",
            "recommend a hop",
            "what hops",
            "alternative to",
            "alternatives to",
        ]
    ):
        formatted_recommendations = format_hop_recommendations(
            hop_name,
        )

        if formatted_recommendations:
            print("Brews Springsteen:")
            print("-" * 50)
            print(formatted_recommendations)
            print("-" * 50)
            return
    hop_name = extract_hop_name(question)

    if hop_name:
        hop_profile = format_hop_profile(hop_name)

        if hop_profile:
            print("Brews Springsteen:")
            print("-" * 50)
            print(hop_profile)
            print("-" * 50)
            return

    # ---------------------------------------------------------
    # 3. EXACT STYLE
    # ---------------------------------------------------------
    # Brewers Association style
    ba_style_answer = answer_ba_style_question(cleaned)
    if ba_style_answer:
        return ba_style_answer
    
    styles = search_exact_style(cleaned)

    if styles:
        display_style(styles[0], question)
        return

    # ---------------------------------------------------------
    # 3. STYLE FAMILY
    # ---------------------------------------------------------

    if cleaned in STYLE_FAMILIES:
        family = STYLE_FAMILIES[cleaned]
        styles = search_style_family(family)

        if styles:

            last_style_list = {}

            print("Brews Springsteen:")
            print("-" * 50)
            print(f"{family} styles currently in the encyclopedia:\n")

            for number, style in enumerate(styles, start=1):
                last_style_list[number] = style["name"]

                print(
                    f"{number}. {style['name']}"
                    f" ({style['category']})"
                )

            print("\nReply with a number to see the description.")
            print("-" * 50)
            return

    # ---------------------------------------------------------
    # 4. GENERAL ENCYCLOPEDIA
    # ---------------------------------------------------------

    entries = search_encyclopedia(cleaned)

    if entries:
        display_entry(entries[0])
        return

    # ---------------------------------------------------------
    # 5. NOTHING FOUND
    # ---------------------------------------------------------

    print(
        "Brews Springsteen: "
        "I couldn't find anything in the encyclopedia "
        "matching that question."
    )


if __name__ == "__main__":

    print()
    print("🍺 BREWS SPRINGSTEEN — BEER ENCYCLOPEDIA")
    print("=" * 50)
    print("Ask a question about beer.")
    print("Type 'quit' to exit.")
    print()

    while True:

        question = input("You: ").strip()

        if question.lower() == "quit":
            break

        if not question:
            continue

        print()

        answer_question(question)

        print()