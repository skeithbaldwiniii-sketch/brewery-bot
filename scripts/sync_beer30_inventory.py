from integrations.beer30 import (
    Beer30Error,
    save_inventory_snapshot,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 INVENTORY SYNC")
    print("=" * 70)

    inventory_types = (
        "grains",
        "hops",
        "adjuncts",
        "canning",
    )

    try:
        total_saved = 0

        for inventory_type in inventory_types:
            print(f"\nSyncing {inventory_type}...")

            saved = save_inventory_snapshot(inventory_type)
            total_saved += saved

            print(
                f"Saved {saved} {inventory_type} inventory records."
            )

        print(
            f"\nBeer30 inventory sync complete."
        )
        print(
            f"Saved {total_saved} inventory records total."
        )

    except Beer30Error as exc:
        print(f"\nBeer30 sync failed:\n{exc}")

    except Exception as exc:
        print(
            f"\nUnexpected error during Beer30 sync:\n{exc}"
        )


if __name__ == "__main__":
    main()