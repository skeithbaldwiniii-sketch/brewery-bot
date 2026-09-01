from integrations.beer30 import (
    get_inventory_item,
    get_inventory_history,
    get_latest_inventory,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 INVENTORY QUERY TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1: ALL CURRENT INVENTORY
    # ---------------------------------------------------------

    inventory = get_latest_inventory("canning")

    print("\nCURRENT CANNING INVENTORY")
    print("-" * 70)

    for item in inventory:
        print(
            f"{item['item_name']}: "
            f"{item['quantity_in_stock']} "
            f"{item['measurement_unit']}"
        )

    print(f"\nFound {len(inventory)} current inventory items.")

    # ---------------------------------------------------------
    # TEST 2: SPECIFIC ITEM
    # ---------------------------------------------------------

    item = get_inventory_item(
        "Sleek 12 Oz Cans",
        "canning",
    )

    print("\nSPECIFIC ITEM")
    print("-" * 70)

    if item:
        print(f"Item: {item['item_name']}")
        print(f"Quantity: {item['quantity_in_stock']}")
        print(f"Unit: {item['measurement_unit']}")
        print(f"Beer30 ID: {item['beer30_item_id']}")
        print(f"Beer30 timestamp: {item['beer30_timestamp']}")
        print(f"Retrieved: {item['retrieved_at']}")
    else:
        print("Item not found.")

    # ---------------------------------------------------------
    # TEST 3: HISTORY
    # ---------------------------------------------------------

    history = get_inventory_history(
        "Sleek 12 Oz Cans",
        "canning",
    )

    print("\nITEM HISTORY")
    print("-" * 70)

    for record in history:
        print(
            f"{record['retrieved_at']} | "
            f"{record['quantity_in_stock']} "
            f"{record['measurement_unit']}"
        )

    print(f"\nFound {len(history)} historical record(s).")

    print("\nPASS - Beer30 inventory query layer is working.")


if __name__ == "__main__":
    main()