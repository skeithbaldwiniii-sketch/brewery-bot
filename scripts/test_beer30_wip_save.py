from integrations.beer30 import save_wip_snapshot


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 WIP SNAPSHOT TEST")
    print("=" * 70)

    report_date = "2026-08-31"

    print()
    print(f"Report date: {report_date}")
    print()

    saved = save_wip_snapshot(report_date)

    print(f"Saved {saved} WIP records.")

    if saved > 0:
        print()
        print("PASS - Beer30 WIP snapshot saved successfully.")
    else:
        print()
        print("FAIL - No WIP records were saved.")


if __name__ == "__main__":
    main()