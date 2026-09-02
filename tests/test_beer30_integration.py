from integrations.beer30 import (
    Beer30Error,
    get_inventory,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 INTEGRATION TEST")
    print("=" * 70)

    try:
        result = get_inventory("canning")

        if result is None:
            print("\nBeer30 returned no content.")
            return

        inventory = result.get("inventory", [])

        print(f"\nBeer30 returned {len(inventory)} inventory items.\n")

        for item in inventory:
            name = item.get("Canning_Item_Name", "Unknown")
            quantity = item.get(
                "Total_Quantity_In_Stock_In_Each",
                "Unknown",
            )
            unit = item.get(
                "Measurement_Unit",
                "Unknown",
            )

            print(
                f"- {name}: {quantity} {unit}"
            )

        print("\nPASS - Beer30 integration is working.")

    except Beer30Error as exc:
        print(f"\nFAIL - Beer30 error:\n{exc}")

    except Exception as exc:
        print(f"\nFAIL - Unexpected error:\n{exc}")


if __name__ == "__main__":
    main()