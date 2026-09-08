from knowledge.database import get_connection


HOPS = [
    {
        "name": "Amarillo",
        "base_variety": "Amarillo",
        "product_form": "Pellet",
    },
    {
        "name": "BRU-1",
        "base_variety": "BRU-1",
        "product_form": "Pellet",
    },
    {
        "name": "Callista",
        "base_variety": "Callista",
        "product_form": "Pellet",
    },
    {
        "name": "Cashmere",
        "base_variety": "Cashmere",
        "product_form": "Pellet",
    },
    {
        "name": "Cascade",
        "base_variety": "Cascade",
        "product_form": "Pellet",
    },
    {
        "name": "Cascade Cryo",
        "base_variety": "Cascade",
        "product_form": "Cryo",
    },
    {
        "name": "Centennial",
        "base_variety": "Centennial",
        "product_form": "Pellet",
    },
    {
        "name": "Centennial Cryo",
        "base_variety": "Centennial",
        "product_form": "Cryo",
    },
    {
        "name": "Chinook",
        "base_variety": "Chinook",
        "product_form": "Pellet",
    },
    {
        "name": "Contessa",
        "base_variety": "Contessa",
        "product_form": "Pellet",
    },
    {
        "name": "Citra",
        "base_variety": "Citra",
        "product_form": "Pellet",
    },
    {
        "name": "Cryo Citra",
        "base_variety": "Citra",
        "product_form": "Cryo",
    },
    {
        "name": "Galaxy",
        "base_variety": "Galaxy",
        "product_form": "Pellet",
    },
    {
        "name": "Hallertau Blanc",
        "base_variety": "Hallertau Blanc",
        "product_form": "Pellet",
    },
    {
        "name": "Lemondrop",
        "base_variety": "Lemondrop",
        "product_form": "Pellet",
    },
    {
        "name": "Magnum",
        "base_variety": "Magnum",
        "product_form": "Pellet",
    },
    {
        "name": "Mandarina Bavaria",
        "base_variety": "Mandarina Bavaria",
        "product_form": "Pellet",
    },
    {
        "name": "Mittelfruh",
        "base_variety": "Hallertau Mittelfrüh",
        "product_form": "Pellet",
    },
    {
        "name": "Mosaic",
        "base_variety": "Mosaic",
        "product_form": "Pellet",
    },
    {
        "name": "Mosaic Cryo",
        "base_variety": "Mosaic",
        "product_form": "Cryo",
    },
    {
        "name": "Motueka",
        "base_variety": "Motueka",
        "product_form": "Pellet",
    },
    {
        "name": "Nelson",
        "base_variety": "Nelson Sauvin",
        "product_form": "Pellet",
    },
    {
        "name": "Simcoe",
        "base_variety": "Simcoe",
        "product_form": "Pellet",
    },
    {
        "name": "Summit",
        "base_variety": "Summit",
        "product_form": "Pellet",
    },
    {
        "name": "Trident Lupulin",
        "base_variety": "Trident",
        "product_form": "Lupulin",
    },
    {
        "name": "Vera",
        "base_variety": "Vera",
        "product_form": "Pellet",
    },
    {
        "name": "Vista",
        "base_variety": "Vista",
        "product_form": "Pellet",
    },
    {
        "name": "Willamette",
        "base_variety": "Willamette",
        "product_form": "Pellet",
    },
]


def seed_hops():
    connection = get_connection()

    inserted = 0
    skipped = 0

    try:
        for hop in HOPS:
            existing = connection.execute(
                """
                SELECT id
                FROM hop_varieties
                WHERE LOWER(name) = LOWER(?)
                """,
                (hop["name"],),
            ).fetchone()

            if existing:
                skipped += 1
                continue

            connection.execute(
                """
                INSERT INTO hop_varieties (
                    name,
                    base_variety,
                    product_form
                )
                VALUES (?, ?, ?)
                """,
                (
                    hop["name"],
                    hop["base_variety"],
                    hop["product_form"],
                ),
            )

            inserted += 1

        connection.commit()

        print(f"Inserted: {inserted}")
        print(f"Skipped:  {skipped}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_hops()