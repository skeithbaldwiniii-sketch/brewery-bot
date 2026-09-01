from integrations.beer30 import (
    Beer30Error,
    save_inventory_snapshot,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 INVENTORY SYNC")
    print("=" * 70)

    try:
        saved = save_inventory_snapshot("canning")

        print(
            f"\nBeer30 inventory sync complete."
        )
        print(
            f"Saved {saved} inventory records."
        )

    except Beer30Error as exc:
        print(f"\nBeer30 sync failed:\n{exc}")

    except Exception as exc:
        print(
            f"\nUnexpected error during Beer30 sync:\n{exc}"
        )


if __name__ == "__main__":
    main()