from knowledge.database import get_connection


def add_entry(title, category, content, source=None):
    """Add or update a general encyclopedia entry."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO encyclopedia_entries
        (
            title,
            category,
            content,
            source
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(title) DO UPDATE SET
            category = excluded.category,
            content = excluded.content,
            source = excluded.source,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            title,
            category,
            content,
            source,
        ),
    )

    connection.commit()
    connection.close()


def seed_entries():
    """Add initial test encyclopedia topics."""

    entries = [
        {
            "title": "Lager",
            "category": "Beer History",
            "content": (
                "Lager is a broad family of beers traditionally "
                "associated with cool fermentation and maturation "
                "using lager yeast. Lager brewing became particularly "
                "important in Central Europe and later spread "
                "throughout the world."
            ),
            "source": "Test encyclopedia data",
        },
        {
            "title": "Hops",
            "category": "Ingredients",
            "content": (
                "Hops are the flowers of Humulus lupulus used in "
                "brewing to contribute bitterness, aroma, flavor, "
                "and antimicrobial properties. Different hop "
                "varieties can produce substantially different "
                "aroma and flavor characteristics."
            ),
            "source": "Test encyclopedia data",
        },
    ]

    for entry in entries:
        add_entry(**entry)

    print(f"Successfully seeded {len(entries)} encyclopedia entries.")


if __name__ == "__main__":
    seed_entries()