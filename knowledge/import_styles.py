import json
from pathlib import Path

from knowledge.encyclopedia import add_style


DATA_FILE = Path(__file__).parent.parent / "styles.json"


def convert_style(style):
    """Convert the source JSON format into our database format."""

    def number(key):
        value = style.get(key)

        if value in (None, "", "N/A"):
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    return {
        "bjcp_number": style.get("number"),
        "name": style.get("name"),
        "category": style.get("category"),
        "country_of_origin": None,
        "historical_period": None,
        "history": style.get("history"),
        "description": style.get("overallimpression"),
        "aroma": style.get("aroma"),
        "appearance": style.get("appearance"),
        "flavor": style.get("flavor"),
        "mouthfeel": style.get("mouthfeel"),
        "ingredients": style.get("characteristicingredients"),
        "brewing_notes": style.get("comments"),
        "typical_abv_min": number("abvmin"),
        "typical_abv_max": number("abvmax"),
        "typical_ibu_min": number("ibumin"),
        "typical_ibu_max": number("ibumax"),
        "typical_og_min": number("ogmin"),
        "typical_og_max": number("ogmax"),
        "typical_fg_min": number("fgmin"),
        "typical_fg_max": number("fgmax"),
        "typical_srm_min": number("srmmin"),
        "typical_srm_max": number("srmmax"),
        "source": "BJCP 2021 Beer Style Guidelines",
    }

def import_styles():
    """Import all beer styles from styles.json."""

    if not DATA_FILE.exists():
        print(f"ERROR: Could not find {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        styles = json.load(file)

    if not isinstance(styles, list):
        raise ValueError("styles.json must contain a JSON list.")

    imported = 0

    for style in styles:
        converted = convert_style(style)

        if not converted["name"]:
            continue

        add_style(**converted)
        imported += 1

    print(f"Successfully imported {imported} beer styles.")


if __name__ == "__main__":
    import_styles()