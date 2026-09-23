import re

from intelligence.brew_planning import get_active_recipe


RECIPE_INTENTS = (
    ("grain_bill", "the grain bill for"),
    ("hop_bill", "the hop bill for"),
    ("recipe", "the recipe for"),
)

RECIPE_PREFIXES = (
    "what is ",
    "what's ",
)


def _parse_recipe_question(question):
    """
    Parse an explicit Beer30 recipe question.

    Returns:
        {"intent": ..., "beer_name": ...}
    or None when the question is not an explicit recipe request.
    """
    q = question.strip().rstrip("?.!")

    for prefix in RECIPE_PREFIXES:
        if q.lower().startswith(prefix):
            q = q[len(prefix):].strip()
            break

    for intent, phrase in RECIPE_INTENTS:
        match = re.match(
            rf"^{re.escape(phrase)}\s+(.+)$",
            q,
            flags=re.IGNORECASE,
        )

        if match:
            beer_name = match.group(1).strip()

            if beer_name:
                return {
                    "intent": intent,
                    "beer_name": beer_name,
                }

    return None


def is_recipe_question(question):
    """Return True when the question contains explicit recipe intent."""
    return _parse_recipe_question(question) is not None


def _format_quantity(quantity):
    """Format recipe quantities consistently."""
    try:
        value = float(quantity)
    except (TypeError, ValueError):
        return str(quantity)

    if value.is_integer():
        return f"{value:.2f}"

    return f"{value:.3f}".rstrip("0").rstrip(".")


def _format_process(process):
    """Convert normalized recipe process names to display text."""
    labels = {
        "boil": "Boil",
        "first_wort": "First Wort",
        "whirlpool": "Whirlpool",
        "active_fermentation": "Active Fermentation",
        "dry_hop": "Dry Hop",
    }

    return labels.get(
        str(process or "").strip().lower(),
        str(process or "").strip(),
    )


def _format_ingredients(ingredients, category):
    """Format ingredients belonging to one recipe category."""
    lines = []

    for ingredient in ingredients:
        if ingredient.get("category") != category:
            continue

        name = str(ingredient.get("name") or "").strip()

        if not name:
            continue

        quantity = _format_quantity(ingredient.get("quantity"))
        unit = str(ingredient.get("unit") or "").strip()

        line = f"- {name}: {quantity}"

        if unit:
            line += f" {unit}"

        process = ingredient.get("process")

        if process:
            line += f" ({_format_process(process)})"

        lines.append(line)

    return lines


def format_recipe(recipe, intent="recipe"):
    """Format a normalized Beer30 recipe for a user."""
    if not recipe:
        return None

    ingredients = recipe.get("ingredients") or []

    if intent == "grain_bill":
        lines = _format_ingredients(ingredients, "grain")

        if not lines:
            return "No grains were listed in the Beer30 recipe."

        return "Grain bill:\n" + "\n".join(lines)

    if intent == "hop_bill":
        lines = _format_ingredients(ingredients, "hop")

        if not lines:
            return "No hops were listed in the Beer30 recipe."

        return "Hop bill:\n" + "\n".join(lines)

    recipe_name = str(
        recipe.get("recipe_name")
        or recipe.get("base_name")
        or "Beer30 recipe"
    ).strip()

    lines = [recipe_name]

    version = recipe.get("version")
    if version is not None:
        lines.append(f"Recipe version: {version}")

    batch_size = recipe.get("batch_size")
    if batch_size is not None:
        lines.append(f"Batch size: {_format_quantity(batch_size)}")

    grains = _format_ingredients(ingredients, "grain")
    hops = _format_ingredients(ingredients, "hop")
    adjuncts = _format_ingredients(ingredients, "adjunct")

    if grains:
        lines.extend(["", "Grains:", *grains])

    if hops:
        lines.extend(["", "Hops:", *hops])

    if adjuncts:
        lines.extend(["", "Adjuncts:", *adjuncts])

    return "\n".join(lines)


def answer_recipe_question(question):
    """
    Answer an explicit Beer30 recipe question.

    Returns None when the question is not an explicit recipe request
    or when no active Beer30 recipe can be found.
    """
    parsed = _parse_recipe_question(question)

    if parsed is None:
        return None

    recipe = get_active_recipe(parsed["beer_name"])

    if recipe is None:
        return (
            f"I couldn't find an active Beer30 recipe for "
            f"{parsed['beer_name']}."
        )

    return format_recipe(
        recipe,
        intent=parsed["intent"],
    )
