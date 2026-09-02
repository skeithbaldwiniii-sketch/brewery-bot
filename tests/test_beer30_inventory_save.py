from integrations.beer30 import (
    Beer30Error,
    save_inventory_snapshot,
)
from knowledge.database import get_connection


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 INVENTORY DATABASE TEST")
    print("=" * 70)

    try:
        saved = save_inventory_snapshot("canning")

        print(f"\nSaved {saved} inventory records to SQLite.")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                beer30_item_id,
                item_name,
                quantity_in_stock,
                measurement_unit,
                retrieved_at
            FROM beer30_inventory
            ORDER BY id DESC
            LIMIT 13
        """)

        rows = cursor.fetchall()

        print("\nLatest inventory snapshot:")
        print("-" * 70)

        for row in rows:
            print(
                f"- {row['item_name']}: "
                f"{row['quantity_in_stock']} "
                f"{row['measurement_unit']}"
            )

        connection.close()

        print("\nPASS - Beer30 inventory saved to SQLite.")

    except Beer30Error as exc:
        print(f"\nFAIL - Beer30 error:\n{exc}")

    except Exception as exc:
        print(f"\nFAIL - Unexpected error:\n{exc}")


if __name__ == "__main__":
    main()