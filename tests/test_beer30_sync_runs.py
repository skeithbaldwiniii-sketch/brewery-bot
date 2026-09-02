from knowledge.database import get_connection


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 SYNC HISTORY")
    print("=" * 70)

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            data_type,
            started_at,
            completed_at,
            records_saved,
            status,
            error_message
        FROM beer30_sync_runs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    if not rows:
        print("\nNo Beer30 sync runs found.")
        connection.close()
        return

    print()

    for row in rows:
        print(
            f"Sync #{row['id']}"
        )
        print(
            f"  Data: {row['data_type']}"
        )
        print(
            f"  Started: {row['started_at']}"
        )
        print(
            f"  Completed: {row['completed_at']}"
        )
        print(
            f"  Records: {row['records_saved']}"
        )
        print(
            f"  Status: {row['status']}"
        )

        if row["error_message"]:
            print(
                f"  Error: {row['error_message']}"
            )

        print()

    connection.close()

    print("PASS - Beer30 sync tracking is working.")


if __name__ == "__main__":
    main()