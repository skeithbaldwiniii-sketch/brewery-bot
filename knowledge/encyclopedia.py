from knowledge.database import get_connection


def add_style(
    name,
    bjcp_number=None,
    category=None,
    country_of_origin=None,
    historical_period=None,
    history=None,
    description=None,
    aroma=None,
    appearance=None,
    flavor=None,
    mouthfeel=None,
    ingredients=None,
    brewing_notes=None,
    typical_abv_min=None,
    typical_abv_max=None,
    typical_ibu_min=None,
    typical_ibu_max=None,
    typical_og_min=None,
    typical_og_max=None,
    typical_fg_min=None,
    typical_fg_max=None,
    typical_srm_min=None,
    typical_srm_max=None,
    source=None,
):
    """Add or update a beer style in the encyclopedia."""

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO beer_styles (
            bjcp_number,
            name,
            category,
            country_of_origin,
            historical_period,
            history,
            description,
            aroma,
            appearance,
            flavor,
            mouthfeel,
            ingredients,
            brewing_notes,
            typical_abv_min,
            typical_abv_max,
            typical_ibu_min,
            typical_ibu_max,
            typical_og_min,
            typical_og_max,
            typical_fg_min,
            typical_fg_max,
            typical_srm_min,
            typical_srm_max,
            source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            bjcp_number = excluded.bjcp_number,
            category = excluded.category,
            country_of_origin = excluded.country_of_origin,
            historical_period = excluded.historical_period,
            history = excluded.history,
            description = excluded.description,
            aroma = excluded.aroma,
            appearance = excluded.appearance,
            flavor = excluded.flavor,
            mouthfeel = excluded.mouthfeel,
            ingredients = excluded.ingredients,
            brewing_notes = excluded.brewing_notes,
            typical_abv_min = excluded.typical_abv_min,
            typical_abv_max = excluded.typical_abv_max,
            typical_ibu_min = excluded.typical_ibu_min,
            typical_ibu_max = excluded.typical_ibu_max,
            typical_og_min = excluded.typical_og_min,
            typical_og_max = excluded.typical_og_max,
            typical_fg_min = excluded.typical_fg_min,
            typical_fg_max = excluded.typical_fg_max,
            typical_srm_min = excluded.typical_srm_min,
            typical_srm_max = excluded.typical_srm_max,
            source = excluded.source,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            bjcp_number,
            name,
            category,
            country_of_origin,
            historical_period,
            history,
            description,
            aroma,
            appearance,
            flavor,
            mouthfeel,
            ingredients,
            brewing_notes,
            typical_abv_min,
            typical_abv_max,
            typical_ibu_min,
            typical_ibu_max,
            typical_og_min,
            typical_og_max,
            typical_fg_min,
            typical_fg_max,
            typical_srm_min,
            typical_srm_max,
            source,
        ),
    )

    connection.commit()
    connection.close()

def search_styles(search_term):
    """Search beer styles."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM beer_styles
        WHERE name LIKE ?
           OR category LIKE ?
           OR description LIKE ?
           OR history LIKE ?
           OR ingredients LIKE ?
        ORDER BY name
        """,
        (
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
        ),
    ).fetchall()

    connection.close()

    return rows

def search_entries(search_term):
    """Search general encyclopedia entries."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM encyclopedia_entries
        WHERE title LIKE ?
           OR category LIKE ?
           OR content LIKE ?
        ORDER BY title
        """,
        (
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%",
        ),
    ).fetchall()

    connection.close()

    return rows

def get_style(name):
    """Get a specific beer style."""

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM beer_styles
        WHERE name = ?
        """,
        (name,),
    ).fetchone()

    connection.close()

    return row


if __name__ == "__main__":
    print("Beer encyclopedia ready.")