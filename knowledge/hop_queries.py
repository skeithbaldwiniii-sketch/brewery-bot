from knowledge.database import get_connection


def search_exact_hop(name):
    """
    Find a hop variety by exact name.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM hop_varieties
            WHERE LOWER(name) = LOWER(?)
            """,
            (name.strip(),)
        ).fetchall()

        return rows

    finally:
        connection.close()


def search_hops(term):
    """
    Search hop varieties by name, origin, descriptors,
    flavor, aroma, or common uses.
    """

    term = term.strip().lower()
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM hop_varieties
            WHERE LOWER(name) LIKE ?
               OR LOWER(origin_country) LIKE ?
               OR LOWER(origin_region) LIKE ?
               OR LOWER(aroma_description) LIKE ?
               OR LOWER(flavor_description) LIKE ?
               OR LOWER(common_descriptors) LIKE ?
               OR LOWER(common_uses) LIKE ?
            ORDER BY name
            """,
            (
                f"%{term}%",
                f"%{term}%",
                f"%{term}%",
                f"%{term}%",
                f"%{term}%",
                f"%{term}%",
                f"%{term}%",
            )
        ).fetchall()

        return rows

    finally:
        connection.close()


def get_all_hops():
    """
    Return all hop varieties alphabetically.
    """

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM hop_varieties
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()