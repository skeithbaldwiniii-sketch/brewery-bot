from knowledge.database import get_connection


BLACK_IPA = {
    "bjcp_number": None,
    "name": "Black IPA",
    "category": "Ipa",
    "country_of_origin": "United States",
    "historical_period": "Modern craft beer",
    "history": (
        "Black IPA is a modern American craft beer variant combining "
        "the hop-forward character of an IPA with the dark color and "
        "restrained roast character of darker beers. It is also commonly "
        "known as Cascadian Dark Ale."
    ),
    "description": (
        "A dark, hoppy, and bitter American ale with the hop character "
        "of an IPA and a restrained dark malt character. Roast and "
        "chocolate notes may be present, but should support rather than "
        "dominate the hop character."
    ),
    "aroma": (
        "Moderate to high hop aroma with citrus, pine, resin, tropical, "
        "stone fruit, or other American and New World hop characteristics. "
        "Low to moderate dark malt aromas may include light roast, toast, "
        "coffee, or chocolate. Dark malt should not overwhelm the hops."
    ),
    "appearance": (
        "Dark brown to black in color. A tan to light brown head is common. "
        "Clarity may range from clear to somewhat hazy depending on the "
        "hopping and brewing process."
    ),
    "flavor": (
        "Moderate to high hop flavor with American or New World hop "
        "characteristics such as citrus, pine, resin, tropical fruit, "
        "stone fruit, or spice. Moderate to high bitterness. Dark malt "
        "flavors such as roast, coffee, chocolate, or dark toast are "
        "present but should remain supportive. The finish should be "
        "reasonably dry rather than sweet or heavy."
    ),
    "mouthfeel": (
        "Medium-light to medium body with moderate to moderately high "
        "carbonation. Smooth texture. Some light roast-derived dryness "
        "or astringency may be present, but harshness should be avoided. "
        "Alcohol warmth may be noticeable in stronger examples."
    ),
    "ingredients": (
        "Pale base malt supplemented with darker specialty malts such as "
        "dehusked roasted malt, chocolate malt, or other dark malts. "
        "American or New World hops are typical. A clean American ale "
        "yeast or another neutral yeast is commonly used. Dark malt "
        "additions should provide color and restrained roast character "
        "without creating excessive astringency."
    ),
    "brewing_notes": (
        "The goal is to balance substantial hop character with restrained "
        "dark malt character. Dehusked or low-intensity roasted malts can "
        "help achieve a dark color without excessive roast harshness. "
        "Late hopping and dry hopping can emphasize citrus, pine, resin, "
        "or tropical character. The beer should remain recognizable as "
        "an IPA rather than becoming a stout or porter."
    ),
    "typical_abv_min": 5.5,
    "typical_abv_max": 9.0,
    "typical_ibu_min": 40.0,
    "typical_ibu_max": 70.0,
    "typical_og_min": 1.056,
    "typical_og_max": 1.075,
    "typical_fg_min": 1.008,
    "typical_fg_max": 1.016,
    "typical_srm_min": 25.0,
    "typical_srm_max": 40.0,
    "source": (
        "BJCP 2021 Beer Style Guidelines / "
        "21B Specialty IPA"
    ),
}


def add_black_ipa():
    connection = get_connection()

    existing = connection.execute(
        """
        SELECT id, name, bjcp_number
        FROM beer_styles
        WHERE LOWER(name) = LOWER(?)
        """,
        (BLACK_IPA["name"],),
    ).fetchone()

    if existing:
        print(
            f"Black IPA already exists "
            f"(id={existing['id']}, "
            f"bjcp_number={existing['bjcp_number']})."
        )
        connection.close()
        return

    columns = ", ".join(BLACK_IPA.keys())
    placeholders = ", ".join(
        ["?"] * len(BLACK_IPA)
    )

    connection.execute(
        f"""
        INSERT INTO beer_styles ({columns})
        VALUES ({placeholders})
        """,
        tuple(BLACK_IPA.values()),
    )

    connection.commit()
    connection.close()

    print("Black IPA added successfully.")
    print("BJCP number: None")
    print("Parent category: 21B Specialty IPA")


if __name__ == "__main__":
    add_black_ipa()