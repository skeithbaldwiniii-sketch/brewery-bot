from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge.database import get_connection


PARSED_PATH = Path("knowledge/data/BA_2024_parsed_styles.json")


def main():
    with open(PARSED_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    styles = data["styles"]

    connection = get_connection()

    updated = 0
    missing = []

    for style in styles:
        name = style["name"]

        cursor = connection.execute(
            """
            UPDATE ba_styles
            SET
                color = ?,
                clarity = ?,
                malt_aroma_flavor = ?,
                hop_aroma_flavor = ?,
                perceived_bitterness = ?,
                fermentation_characteristics = ?,
                body = ?,
                additional_notes = ?,
                original_gravity = ?,
                final_gravity = ?,
                alcohol = ?,
                ibu = ?,
                srm = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
            """,
            (
                style.get("Color"),
                style.get("Clarity"),
                style.get("Perceived Malt Aroma & Flavor"),
                style.get("Perceived Hop Aroma & Flavor"),
                style.get("Perceived bitterness"),
                style.get("Fermentation Characteristics"),
                style.get("Body"),
                style.get("Additional notes"),
                style.get("original_gravity"),
                style.get("final_gravity"),
                style.get("alcohol"),
                style.get("ibu"),
                style.get("srm"),
                name,
            ),
        )

        if cursor.rowcount == 1:
            updated += 1
        else:
            missing.append(name)

    connection.commit()
    connection.close()

    print("=" * 80)
    print("BA PARSED DATA IMPORT")
    print("=" * 80)
    print(f"Parsed styles:   {len(styles)}")
    print(f"Updated styles:   {updated}")
    print(f"Missing styles:   {len(missing)}")

    if missing:
        print("\nMISSING FROM DATABASE:")
        for name in missing:
            print(f"- {name}")


if __name__ == "__main__":
    main()