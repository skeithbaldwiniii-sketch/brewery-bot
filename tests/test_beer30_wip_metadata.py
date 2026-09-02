from intelligence.beer30_queries import (
    get_latest_wip_metadata,
    get_wip_snapshot_summary,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 WIP METADATA TEST")
    print("=" * 70)

    metadata = get_latest_wip_metadata()

    print("\nLatest WIP metadata:")
    print(metadata)

    print("\nSnapshot summary:")
    print(get_wip_snapshot_summary())

    if metadata:
        print("\nPASS - WIP provenance metadata retrieved successfully.")
    else:
        print("\nFAIL - No WIP metadata found.")


if __name__ == "__main__":
    main()