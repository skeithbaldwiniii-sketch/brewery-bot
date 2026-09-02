from intelligence.beer30_queries import (
    get_latest_wip,
    get_wip_by_tank,
    get_wip_by_action,
    get_active_wip,
    get_empty_tanks,
    get_total_wip_volume,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 WIP QUERY TEST")
    print("=" * 70)

    print("\n1. Latest WIP snapshot")
    wip = get_latest_wip()

    print(f"Records: {len(wip)}")

    for record in wip[:5]:
        print(
            f"  {record['tank_name']} | "
            f"{record['brand_name']} | "
            f"{record['current_volume']} | "
            f"{record['action']}"
        )

    print("\n2. Tank lookup")
    tank = get_wip_by_tank("UNI-V-01")

    for record in tank:
        print(
            f"  {record['tank_name']} | "
            f"{record['brand_name']} | "
            f"Batch {record['batch_number']} | "
            f"{record['current_volume']} bbl"
        )

    print("\n3. Fermenting WIP")
    fermenting = get_wip_by_action("ferment")

    print(f"Records: {len(fermenting)}")

    for record in fermenting:
        print(
            f"  {record['tank_name']} | "
            f"{record['brand_name']} | "
            f"{record['current_volume']} bbl"
        )

    print("\n4. Active WIP")
    active = get_active_wip()
    print(f"Active tanks: {len(active)}")

    print("\n5. Empty tanks")
    empty = get_empty_tanks()
    print(f"Empty tanks: {len(empty)}")

    print("\n6. Total WIP volume")
    total_volume = get_total_wip_volume()
    print(f"Total WIP volume: {total_volume:.2f} bbl")

    print("\n" + "=" * 70)
    print("PASS - WIP query layer executed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()