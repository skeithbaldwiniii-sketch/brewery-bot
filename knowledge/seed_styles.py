from knowledge.database import get_connection
from knowledge.encyclopedia import add_style


def seed_test_styles():
    """Add a small set of test beer styles."""

    styles = [
        {
            "name": "Pilsner",
            "category": "Pale Lager",
            "bjcp_number": "5D",
            "country_of_origin": "Bohemia",
            "historical_period": "19th century",
            "history": (
                "Pilsner originated in Plzeň, Bohemia, during the "
                "19th century and became one of the most influential "
                "lager styles in the world."
            ),
            "description": (
                "A pale, clean lager with a noticeable hop character "
                "and crisp, refreshing finish."
            ),
            "aroma": "Clean malt character with noticeable hop aroma.",
            "appearance": "Pale gold to deep gold with good clarity.",
            "flavor": (
                "Clean malt character balanced by moderate to "
                "moderately high hop bitterness."
            ),
            "mouthfeel": "Light to medium body with moderate carbonation.",
            "ingredients": (
                "Pale base malt and noble-type lager hops."
            ),
            "brewing_notes": (
                "Traditionally fermented with lager yeast at cool "
                "temperatures followed by extended conditioning."
            ),
            "typical_abv_min": 4.4,
            "typical_abv_max": 5.4,
            "typical_ibu_min": 22,
            "typical_ibu_max": 40,
            "source": "Test data",
        },
        {
            "name": "Vienna Lager",
            "bjcp_number": "7A",
            "category": "Amber Lager",
            "country_of_origin": "Austria",
            "historical_period": "19th century",
            "history": (
                "Vienna Lager developed in Austria during the 19th "
                "century and is associated with the development of "
                "modern lager brewing."
            ),
            "description": (
                "A clean, smooth amber lager with a rich malt character "
                "and restrained hop bitterness."
            ),
            "aroma": "Toasty, bready malt with restrained hop character.",
            "appearance": "Amber to copper with good clarity.",
            "flavor": (
                "Rich but clean malt flavor with toasted and bready "
                "character balanced by moderate bitterness."
            ),
            "mouthfeel": "Medium body with moderate carbonation.",
            "ingredients": (
                "Vienna malt with complementary base and specialty "
                "malts and lager yeast."
            ),
            "brewing_notes": (
                "Cool fermentation followed by lagering produces the "
                "clean profile associated with the style."
            ),
            "typical_abv_min": 4.7,
            "typical_abv_max": 5.5,
            "typical_ibu_min": 18,
            "typical_ibu_max": 30,
            "source": "Test data",
        },
    ]

    for style in styles:
        add_style(**style)


def display_styles():
    """Display all beer styles currently in the database."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT name, category, country_of_origin
        FROM beer_styles
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    print("\nBeer styles in encyclopedia:")
    print("-" * 50)

    for row in rows:
        print(
            f"{row['name']} | "
            f"{row['category']} | "
            f"{row['country_of_origin']}"
        )


if __name__ == "__main__":
    seed_test_styles()
    display_styles()