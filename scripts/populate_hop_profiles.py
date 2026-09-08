from knowledge.database import get_connection


PROFILES = [
    {
        "name": "Amarillo",
        "origin_country": "United States",
        "origin_region": "Washington",
        "developer": "Virgil Gamache Farms",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": 6.5,
        "alpha_acid_max": 11.0,
        "beta_acid_min": 5.5,
        "beta_acid_max": 8.0,
        "cohumulone_min": 20.0,
        "cohumulone_max": 24.0,
        "oil_total_min": 0.8,
        "oil_total_max": 2.5,
        "aroma_description": (
            "Citrus-forward with grapefruit, orange, lemon, "
            "melon, stone fruit and subtle herbal and woody notes."
        ),
        "flavor_description": (
            "Grapefruit, orange, lemon, melon and stone fruit "
            "with herbal and spicy character."
        ),
        "common_descriptors": (
            "grapefruit, orange, lemon, melon, citrus, "
            "stone fruit, herbal, spicy, woody"
        ),
        "common_uses": (
            "American Ale, Pale Ale, IPA, late-kettle additions, "
            "whirlpool, dry hop"
        ),
        "brewing_notes": (
            "A versatile American aroma hop with relatively high "
            "myrcene. Particularly useful when citrus and grapefruit "
            "character are desired."
        ),
        "source": "Yakima Chief Hops",
    },

    {
        "name": "BRU-1",
        "origin_country": "United States",
        "origin_region": "Washington",
        "developer": "Brulotte Farms / John I. Haas",
        "released_year": 2016,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 13.0,
        "alpha_acid_max": 15.0,
        "beta_acid_min": 8.0,
        "beta_acid_max": 10.0,
        "cohumulone_min": 35.0,
        "cohumulone_max": 37.0,
        "oil_total_min": 1.5,
        "oil_total_max": 2.0,
        "aroma_description": (
            "Sweet tropical fruit dominated by pineapple, "
            "with pear, apple and fresh-cut grass."
        ),
        "flavor_description": (
            "Pineapple and green fruit with pear, apple "
            "and fresh-cut grass character."
        ),
        "common_descriptors": (
            "pineapple, pear, apple, tropical fruit, "
            "green fruit, fresh-cut grass"
        ),
        "common_uses": (
            "Pale Ale, IPA, Hazy IPA, NEIPA, IPL, "
            "Wheat Ale, Golden Ale"
        ),
        "brewing_notes": (
            "Especially effective in whirlpool and dry-hop "
            "applications. Its pineapple-forward character "
            "can add depth when paired with other American aroma hops."
        ),
        "source": "John I. Haas / BarthHaas",
    },

    {
        "name": "Callista",
        "origin_country": "Germany",
        "origin_region": "Hallertau",
        "developer": "Hop Research Center Hüll",
        "released_year": 2016,
        "hop_type": "Aroma",
        "alpha_acid_min": 3.4,
        "alpha_acid_max": 3.4,
        "beta_acid_min": 6.8,
        "beta_acid_max": 6.8,
        "cohumulone_min": 19.0,
        "cohumulone_max": 19.0,
        "oil_total_min": 1.0,
        "oil_total_max": 1.0,
        "aroma_description": (
            "Broad fruity aroma with passion fruit, peach "
            "and sweet-fruit berry character."
        ),
        "flavor_description": (
            "Passion fruit, peach and sweet-fruity berry notes, "
            "with an intensely hoppy character."
        ),
        "common_descriptors": (
            "passion fruit, peach, berry, sweet fruit, "
            "floral, fruity"
        ),
        "common_uses": (
            "Aroma additions, late hopping, whirlpool, "
            "cold hopping, modern German ales and lagers"
        ),
        "brewing_notes": (
            "Low cohumulone contributes to a mild, balanced "
            "bitterness. Cold hopping can emphasize passion fruit, "
            "peach and berry character."
        ),
        "source": "Hop Research Center Hüll",
    },

    {
        "name": "Cashmere",
        "origin_country": "United States",
        "origin_region": "Washington",
        "developer": "Washington State University",
        "released_year": 2013,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 7.0,
        "alpha_acid_max": 10.0,
        "beta_acid_min": 5.0,
        "beta_acid_max": 7.0,
        "cohumulone_min": 20.0,
        "cohumulone_max": 24.0,
        "oil_total_min": 0.5,
        "oil_total_max": 1.5,
        "aroma_description": (
            "Mild citrus, berry, grapefruit, herbal and "
            "stone-fruit character."
        ),
        "flavor_description": (
            "Berry, grapefruit, herbal and stone-fruit flavors "
            "with a smooth citrus character."
        ),
        "common_descriptors": (
            "berry, grapefruit, citrus, herbal, stone fruit"
        ),
        "common_uses": (
            "Pale Ale, IPA, lager, wheat beer, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A daughter of Cascade with Northern Brewer germplasm. "
            "Its higher alpha content and relatively high humulene "
            "contribute to smooth bitterness and mild citrus character."
        ),
        "source": "Yakima Chief Hops / Washington State University",
    },

    {
        "name": "Cascade",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "USDA-ARS",
        "released_year": 1972,
        "hop_type": "Aroma",
        "alpha_acid_min": 4.0,
        "alpha_acid_max": 9.0,
        "beta_acid_min": 5.5,
        "beta_acid_max": 9.0,
        "cohumulone_min": 29.0,
        "cohumulone_max": 35.0,
        "oil_total_min": 0.5,
        "oil_total_max": 2.0,
        "aroma_description": (
            "Classic American hop character with grapefruit, "
            "floral, pine, herbal and grassy notes."
        ),
        "flavor_description": (
            "Grapefruit and citrus supported by floral, pine, "
            "herbal and grassy character."
        ),
        "common_descriptors": (
            "grapefruit, citrus, floral, pine, herbal, grassy"
        ),
        "common_uses": (
            "Pale Ale, IPA, Amber Ale, American Wheat, "
            "lager, late-kettle and dry hop"
        ),
        "brewing_notes": (
            "A foundational American aroma variety. It can provide "
            "both recognizable grapefruit character and moderate "
            "bitterness."
        ),
        "source": "Yakima Chief Hops / USDA-ARS",
    },

        {
        "name": "Cascade Cryo",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Yakima Chief Hops",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": None,
        "alpha_acid_max": None,
        "beta_acid_min": None,
        "beta_acid_max": None,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": None,
        "oil_total_max": None,
        "aroma_description": (
            "Concentrated Cascade character with grapefruit, "
            "citrus, floral and resinous notes."
        ),
        "flavor_description": (
            "Intensified grapefruit and citrus character with "
            "floral and resinous notes."
        ),
        "common_descriptors": (
            "grapefruit, citrus, floral, resin, concentrated Cascade"
        ),
        "common_uses": (
            "IPA, Pale Ale, hop-forward lager, whirlpool, "
            "dry hop"
        ),
        "brewing_notes": (
            "Cryo processing concentrates lupulin and removes much "
            "of the vegetative material found in conventional pellets. "
            "Use as a concentrated form of Cascade rather than treating "
            "it as an unrelated variety."
        ),
        "source": "Yakima Chief Hops",
    },

    {
        "name": "Centennial",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "USDA-ARS",
        "released_year": 1974,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 8.0,
        "alpha_acid_max": 11.5,
        "beta_acid_min": 3.5,
        "beta_acid_max": 5.5,
        "cohumulone_min": 28.0,
        "cohumulone_max": 30.0,
        "oil_total_min": 1.5,
        "oil_total_max": 2.3,
        "aroma_description": (
            "Strong citrus and floral American hop aroma."
        ),
        "flavor_description": (
            "Grapefruit, lemon, citrus and floral character."
        ),
        "common_descriptors": (
            "grapefruit, lemon, citrus, floral"
        ),
        "common_uses": (
            "IPA, Pale Ale, American Amber, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "Classic American hop with strong citrus character. "
            "Can provide both bitterness and substantial late-hop "
            "aroma."
        ),
        "source": "Yakima Chief Hops / USDA-ARS",
    },

    {
        "name": "Centennial Cryo",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Yakima Chief Hops",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": None,
        "alpha_acid_max": None,
        "beta_acid_min": None,
        "beta_acid_max": None,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": None,
        "oil_total_max": None,
        "aroma_description": (
            "Concentrated Centennial character with grapefruit, "
            "lemon, citrus and floral notes."
        ),
        "flavor_description": (
            "Intense grapefruit, lemon and citrus character with "
            "Centennial's characteristic floral component."
        ),
        "common_descriptors": (
            "grapefruit, lemon, citrus, floral, concentrated Centennial"
        ),
        "common_uses": (
            "IPA, Pale Ale, Double IPA, whirlpool, dry hop"
        ),
        "brewing_notes": (
            "Cryo form of Centennial with concentrated lupulin and "
            "reduced vegetative matter. Treat as a concentrated "
            "Centennial product rather than a separate variety."
        ),
        "source": "Yakima Chief Hops",
    },

    {
        "name": "Chinook",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "USDA-ARS",
        "released_year": 1985,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 12.0,
        "alpha_acid_max": 15.0,
        "beta_acid_min": 3.0,
        "beta_acid_max": 4.0,
        "cohumulone_min": 25.0,
        "cohumulone_max": 29.0,
        "oil_total_min": 1.5,
        "oil_total_max": 2.5,
        "aroma_description": (
            "Distinctive spicy, piney and resinous American hop aroma."
        ),
        "flavor_description": (
            "Pine, resin, spice and grapefruit."
        ),
        "common_descriptors": (
            "pine, resin, spicy, grapefruit, herbal"
        ),
        "common_uses": (
            "IPA, Pale Ale, Porter, Stout, Red Ale, "
            "bittering and late-hop additions"
        ),
        "brewing_notes": (
            "High-alpha variety with a distinctive pine and spice "
            "character. Can be used for bittering or to add substantial "
            "resinous character in later additions."
        ),
        "source": "Yakima Chief Hops / USDA-ARS",
    },

    {
        "name": "Citra",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Hop Breeding Company",
        "released_year": 2007,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 10.0,
        "alpha_acid_max": 16.0,
        "beta_acid_min": 3.0,
        "beta_acid_max": 5.0,
        "cohumulone_min": 22.0,
        "cohumulone_max": 24.0,
        "oil_total_min": 2.0,
        "oil_total_max": 3.0,
        "aroma_description": (
            "Intense citrus and tropical fruit aroma."
        ),
        "flavor_description": (
            "Lime, grapefruit, mango, passionfruit and tropical fruit."
        ),
        "common_descriptors": (
            "lime, grapefruit, mango, passionfruit, tropical fruit"
        ),
        "common_uses": (
            "IPA, Hazy IPA, Pale Ale, Double IPA, "
            "whirlpool and dry hop"
        ),
        "brewing_notes": (
            "Highly expressive modern American hop. Particularly "
            "effective in whirlpool and dry-hop applications where "
            "its citrus and tropical character can be emphasized."
        ),
        "source": "Hop Breeding Company / Yakima Chief Hops",
    },

        {
        "name": "Contessa",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Hopsteiner breeding program",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": 3.0,
        "alpha_acid_max": 5.0,
        "beta_acid_min": 5.0,
        "beta_acid_max": 7.4,
        "cohumulone_min": 29.0,
        "cohumulone_max": 32.0,
        "oil_total_min": 0.8,
        "oil_total_max": 1.9,
        "aroma_description": (
            "Green tea, floral and light pear character."
        ),
        "flavor_description": (
            "Delicate herbal and floral character with "
            "green tea and light pear notes."
        ),
        "common_descriptors": (
            "green tea, floral, pear, herbal"
        ),
        "common_uses": (
            "Lager, Kölsch, wheat beer, pale ale, "
            "late-kettle and dry hop"
        ),
        "brewing_notes": (
            "A relatively low-alpha aroma variety with a delicate "
            "herbal and floral profile. Hopsteiner lists Hersbrucker "
            "Spät and Willamette as brewhouse substitutes."
        ),
        "source": "Hopsteiner",
    },

    {
        "name": "Cryo Citra",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Yakima Chief Hops",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": 24.0,
        "alpha_acid_max": 26.0,
        "beta_acid_min": 5.0,
        "beta_acid_max": 6.5,
        "cohumulone_min": 22.0,
        "cohumulone_max": 24.0,
        "oil_total_min": 3.5,
        "oil_total_max": 5.5,
        "aroma_description": (
            "Highly concentrated Citra character with intense "
            "citrus, tropical fruit and stone-fruit expression."
        ),
        "flavor_description": (
            "Intense citrus and tropical fruit with mango, "
            "passionfruit and related Citra character."
        ),
        "common_descriptors": (
            "citrus, tropical fruit, mango, passionfruit, "
            "stone fruit, concentrated Citra"
        ),
        "common_uses": (
            "IPA, Hazy IPA, Double IPA, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "Cryogenic processing concentrates lupulin and reduces "
            "vegetative material compared with conventional T-90 "
            "pellets. Treat as a concentrated Citra product, not "
            "as a separate hop variety."
        ),
        "source": "Yakima Chief Hops / Citra Cryo product specification",
    },

    {
        "name": "Galaxy",
        "origin_country": "Australia",
        "origin_region": "Tasmania",
        "developer": "Hop Products Australia",
        "released_year": 2009,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 15.7,
        "alpha_acid_max": 19.8,
        "beta_acid_min": 7.8,
        "beta_acid_max": 9.9,
        "cohumulone_min": 32.0,
        "cohumulone_max": 43.0,
        "oil_total_min": 2.6,
        "oil_total_max": 3.3,
        "aroma_description": (
            "Punchy passionfruit, juicy peach and tangy citrus."
        ),
        "flavor_description": (
            "Strong passionfruit and peach with bright citrus "
            "and tropical fruit character."
        ),
        "common_descriptors": (
            "passionfruit, peach, citrus, tropical fruit"
        ),
        "common_uses": (
            "XPA, Pacific Ale, Hazy Pale Ale, IPA, NEIPA, "
            "whirlpool and dry hop"
        ),
        "brewing_notes": (
            "High-alpha Australian variety with exceptionally strong "
            "fruit expression. HPA notes that excessive hop intensity "
            "can produce harsher characters in lean malt beers."
        ),
        "source": "Hop Products Australia",
    },

    {
        "name": "Hallertau Blanc",
        "origin_country": "Germany",
        "origin_region": "Hallertau",
        "developer": "Hop Research Center Hüll",
        "released_year": 2012,
        "hop_type": "Aroma",
        "alpha_acid_min": 8.0,
        "alpha_acid_max": 12.9,
        "beta_acid_min": 4.6,
        "beta_acid_max": 7.0,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": 0.8,
        "oil_total_max": 1.9,
        "aroma_description": (
            "White muscatel grape and green fruit character with "
            "citrusy grapefruit, elderflower, lemongrass and cucumber."
        ),
        "flavor_description": (
            "White grape, green fruit and citrus with floral, "
            "herbal and fresh green notes."
        ),
        "common_descriptors": (
            "white grape, muscatel, grapefruit, elderflower, "
            "lemongrass, cucumber, green fruit"
        ),
        "common_uses": (
            "Pale Ale, IPA, wheat beer, modern lager, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A daughter of Cascade bred at Hüll for the craft beer "
            "market. Its white-wine-like character makes it especially "
            "useful when a grape or wine-like hop expression is desired."
        ),
        "source": "BarthHaas",
    },

    {
        "name": "Lemondrop",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Hopsteiner",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": None,
        "alpha_acid_max": None,
        "beta_acid_min": None,
        "beta_acid_max": None,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": None,
        "oil_total_max": None,
        "aroma_description": (
            "Bright lemon and citrus character with herbal, "
            "mint and tea-like notes."
        ),
        "flavor_description": (
            "Lemon-forward citrus with herbal and subtle "
            "tea-like character."
        ),
        "common_descriptors": (
            "lemon, citrus, herbal, mint, tea"
        ),
        "common_uses": (
            "Pale Ale, IPA, wheat beer, saison, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A specialty aroma hop selected for pronounced lemon "
            "character. Particularly useful when a bright lemon "
            "expression is desired without relying on fruit additions."
        ),
        "source": "Hopsteiner",
    },

        {
        "name": "Magnum",
        "origin_country": "Germany",
        "origin_region": "Hallertau",
        "developer": "Hop Research Center Hüll",
        "released_year": 1993,
        "hop_type": "Bittering",
        "alpha_acid_min": 11.0,
        "alpha_acid_max": 16.0,
        "beta_acid_min": 5.0,
        "beta_acid_max": 7.0,
        "cohumulone_min": 21.0,
        "cohumulone_max": 29.0,
        "oil_total_min": 1.9,
        "oil_total_max": 2.8,
        "aroma_description": (
            "Relatively clean bitterness with subtle pepper, "
            "fruity and apple-like character."
        ),
        "flavor_description": (
            "Clean, smooth bitterness with subtle spicy and "
            "fruity character."
        ),
        "common_descriptors": (
            "pepper, spice, fruit, apple, clean bitterness"
        ),
        "common_uses": (
            "Lager, Pilsner, IPA, Pale Ale, Porter, Stout, "
            "early-kettle bittering"
        ),
        "brewing_notes": (
            "A high-alpha German variety primarily valued for "
            "clean, efficient bittering. Its relatively restrained "
            "aroma makes it useful when hop aroma should remain subtle."
        ),
        "source": "Hopsteiner",
    },

    {
        "name": "Mandarina Bavaria",
        "origin_country": "Germany",
        "origin_region": "Hallertau",
        "developer": "Hop Research Center Hüll",
        "released_year": 2012,
        "hop_type": "Aroma",
        "alpha_acid_min": 7.6,
        "alpha_acid_max": 10.2,
        "beta_acid_min": 6.1,
        "beta_acid_max": 7.3,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": 1.5,
        "oil_total_max": 1.8,
        "aroma_description": (
            "Distinctive tangerine and orange character with "
            "black and red currant, rosemary and gooseberry."
        ),
        "flavor_description": (
            "Tangerine and orange with berry, gooseberry, "
            "herbal and lightly tropical character."
        ),
        "common_descriptors": (
            "tangerine, orange, currant, gooseberry, rosemary, "
            "citrus, tropical"
        ),
        "common_uses": (
            "Pale Ale, IPA, Saison, wheat beer, Pilsner, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A modern German aroma variety bred at Hüll. Its "
            "distinctive tangerine character makes it useful when "
            "a bright citrus expression is desired in German or "
            "American-influenced beer styles."
        ),
        "source": "BarthHaas / Hop Research Center Hüll",
    },

    {
        "name": "Mittelfruh",
        "origin_country": "Germany",
        "origin_region": "Hallertau",
        "developer": "Traditional Hallertau landrace",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": 2.3,
        "alpha_acid_max": 6.6,
        "beta_acid_min": 3.3,
        "beta_acid_max": 6.5,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": 0.0,
        "oil_total_max": 1.5,
        "aroma_description": (
            "Noble spicy and woody character with myrrh, "
            "carnation, lilac, red currant and lemon."
        ),
        "flavor_description": (
            "Delicate noble spice, woody, floral and citrus "
            "character with red currant and lemon."
        ),
        "common_descriptors": (
            "noble, spicy, woody, myrrh, carnation, lilac, "
            "red currant, lemon"
        ),
        "common_uses": (
            "Pilsner, Helles, German lager, Kölsch, wheat beer, "
            "late-kettle and traditional noble hopping"
        ),
        "brewing_notes": (
            "The classic Hallertau land variety and a benchmark "
            "for noble German hop character. Analytical values can "
            "vary substantially by crop year."
        ),
        "source": "BarthHaas / Hallertauer Mittelfrüh",
    },

    {
        "name": "Mosaic",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Hop Breeding Company",
        "released_year": 2012,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 10.0,
        "alpha_acid_max": 15.0,
        "beta_acid_min": 3.0,
        "beta_acid_max": 4.5,
        "cohumulone_min": 20.0,
        "cohumulone_max": 25.0,
        "oil_total_min": 0.5,
        "oil_total_max": 3.0,
        "aroma_description": (
            "Complex fruit-forward character including blueberry, "
            "tangerine, papaya, rose, blossom and bubble gum."
        ),
        "flavor_description": (
            "Layered berry, citrus and tropical fruit with floral "
            "and sweet-fruit character."
        ),
        "common_descriptors": (
            "blueberry, tangerine, papaya, berry, citrus, "
            "tropical, floral, bubble gum"
        ),
        "common_uses": (
            "Pale Ale, IPA, Double IPA, Stout, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A daughter of Simcoe with a complex and highly "
            "expressive aroma profile. Particularly useful when "
            "multiple fruit and citrus dimensions are desired."
        ),
        "source": "Yakima Chief Hops / Hop Breeding Company",
    },

    {
        "name": "Mosaic Cryo",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Yakima Chief Hops",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": None,
        "alpha_acid_max": None,
        "beta_acid_min": None,
        "beta_acid_max": None,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": None,
        "oil_total_max": None,
        "aroma_description": (
            "Highly concentrated Mosaic character with intense "
            "berry, citrus, tropical fruit and floral expression."
        ),
        "flavor_description": (
            "Concentrated blueberry, tangerine, tropical fruit, "
            "papaya and floral Mosaic character."
        ),
        "common_descriptors": (
            "blueberry, tangerine, papaya, berry, citrus, "
            "tropical, floral, concentrated Mosaic"
        ),
        "common_uses": (
            "IPA, Hazy IPA, Double IPA, Stout, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "Cryo form of Mosaic with concentrated lupulin and "
            "reduced vegetative matter. Treat as a concentrated "
            "Mosaic product rather than a separate hop variety."
        ),
        "source": "Yakima Chief Hops",
    },

        {
        "name": "Motueka",
        "origin_country": "New Zealand",
        "origin_region": "Nelson",
        "developer": "NZ Hops",
        "released_year": None,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 6.0,
        "alpha_acid_max": 9.5,
        "beta_acid_min": 5.0,
        "beta_acid_max": 6.0,
        "cohumulone_min": 28.0,
        "cohumulone_max": 32.0,
        "oil_total_min": 0.6,
        "oil_total_max": 1.0,
        "aroma_description": (
            "Fresh crushed lime and lemon with mojito-like citrus, "
            "tropical fruit and light herbal character."
        ),
        "flavor_description": (
            "Bright lime and lemon citrus with tropical fruit "
            "and refreshing herbal character."
        ),
        "common_descriptors": (
            "lime, lemon, mojito, citrus, tropical fruit, "
            "herbal, stone fruit"
        ),
        "common_uses": (
            "Pale Ale, IPA, Lager, Pilsner, Saison, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A distinctive New Zealand dual-purpose hop. Its "
            "fresh lime character makes it particularly useful "
            "when a bright, refreshing citrus profile is desired."
        ),
        "source": "NZ Hops / Clayton Hops",
    },

    {
        "name": "Nelson",
        "origin_country": "New Zealand",
        "origin_region": "Nelson",
        "developer": "NZ Hops",
        "released_year": 2000,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 9.0,
        "alpha_acid_max": 13.0,
        "beta_acid_min": 5.0,
        "beta_acid_max": 8.0,
        "cohumulone_min": 20.0,
        "cohumulone_max": 30.0,
        "oil_total_min": 0.8,
        "oil_total_max": 2.0,
        "aroma_description": (
            "Distinctive gooseberry, white wine and fresh "
            "New World fruit character with tropical, citrus "
            "and stone-fruit notes."
        ),
        "flavor_description": (
            "Gooseberry and white-wine character with fruity, "
            "tropical and citrus notes."
        ),
        "common_descriptors": (
            "gooseberry, white wine, Sauvignon Blanc, "
            "grape, tropical, citrus, stone fruit"
        ),
        "common_uses": (
            "Pale Ale, IPA, Double IPA, Saison, Lager, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A highly distinctive New Zealand variety. Its "
            "white-wine and gooseberry character can become "
            "very expressive in late and dry-hop applications."
        ),
        "source": "NZ Hops / HPA",
    },

    {
        "name": "Simcoe",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Select Botanicals Group",
        "released_year": 2000,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 10.0,
        "alpha_acid_max": 16.0,
        "beta_acid_min": 3.5,
        "beta_acid_max": 5.5,
        "cohumulone_min": 17.0,
        "cohumulone_max": 21.0,
        "oil_total_min": 0.5,
        "oil_total_max": 3.0,
        "aroma_description": (
            "Complex citrus, grapefruit, stone fruit and "
            "tropical character with woody and resinous notes."
        ),
        "flavor_description": (
            "Grapefruit and citrus layered with pine, resin, "
            "stone fruit and tropical character."
        ),
        "common_descriptors": (
            "grapefruit, citrus, pine, resin, stone fruit, "
            "tropical, woody"
        ),
        "common_uses": (
            "IPA, Double IPA, Pale Ale, American Amber, "
            "Stout, late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A versatile American dual-purpose variety capable "
            "of providing both substantial bitterness and a "
            "complex citrus, pine and fruit character."
        ),
        "source": "Yakima Chief Hops",
    },

    {
        "name": "Summit",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "American Dwarf Hop Association",
        "released_year": 2003,
        "hop_type": "Dual Purpose",
        "alpha_acid_min": 13.0,
        "alpha_acid_max": 18.0,
        "beta_acid_min": 3.5,
        "beta_acid_max": 5.5,
        "cohumulone_min": 28.0,
        "cohumulone_max": 35.0,
        "oil_total_min": 1.5,
        "oil_total_max": 2.5,
        "aroma_description": (
            "Citrusy, herbal and spicy character with a "
            "distinctive savory and resinous edge."
        ),
        "flavor_description": (
            "Strong citrus, herbal and spicy character with "
            "resinous and savory notes."
        ),
        "common_descriptors": (
            "citrus, herbal, spicy, garlic, resinous, savory"
        ),
        "common_uses": (
            "IPA, American Pale Ale, Amber Ale, Stout, "
            "bittering and late-kettle additions"
        ),
        "brewing_notes": (
            "A high-alpha American variety with a distinctive "
            "spicy and herbal profile. Its assertive character "
            "makes it particularly useful when a strong hop "
            "presence is desired."
        ),
        "source": "Hopsteiner",
    },

    {
        "name": "Trident Lupulin",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "Hopsteiner",
        "released_year": None,
        "hop_type": "Aroma",
        "alpha_acid_min": None,
        "alpha_acid_max": None,
        "beta_acid_min": None,
        "beta_acid_max": None,
        "cohumulone_min": None,
        "cohumulone_max": None,
        "oil_total_min": None,
        "oil_total_max": None,
        "aroma_description": (
            "Concentrated Trident character combining fruity, "
            "citrus, tropical and passion-fruit notes."
        ),
        "flavor_description": (
            "Intense tropical fruit, citrus and passion-fruit "
            "character with a broad modern hop profile."
        ),
        "common_descriptors": (
            "tropical, citrus, passion fruit, fruity, "
            "concentrated, lupulin"
        ),
        "common_uses": (
            "Hazy IPA, IPA, American Pale Ale, Lager, "
            "whirlpool and dry hop"
        ),
        "brewing_notes": (
            "Concentrated lupulin form of Hopsteiner's Trident "
            "blend. Treat as a processed Trident product rather "
            "than as an independent hop variety."
        ),
        "source": "Hopsteiner",
        "base_variety": "Trident",
        "product_form": "Lupulin",
    },

        {
        "name": "Vera",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "USDA Agricultural Research Service / Hop Research Council",
        "released_year": 2025,
        "hop_type": "Aroma",
        "alpha_acid_min": 4.0,
        "alpha_acid_max": 7.0,
        "beta_acid_min": 3.0,
        "beta_acid_max": 5.0,
        "cohumulone_min": 42.0,
        "cohumulone_max": 46.0,
        "oil_total_min": 1.0,
        "oil_total_max": 1.4,
        "aroma_description": (
            "Fruit-forward character with ripe white peach, "
            "stone fruit, crisp white grape, citrus and tropical "
            "fruit, with a distinctive candy-like character."
        ),
        "flavor_description": (
            "White peach, stone fruit, white grape and tropical "
            "fruit with bright citrus and candy-like notes."
        ),
        "common_descriptors": (
            "white peach, stone fruit, white grape, citrus, "
            "tropical fruit, pineapple, candy"
        ),
        "common_uses": (
            "Hazy Pale Ale, IPA, Pale Ale, fruity Lager, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A very new public USDA variety and daughter of "
            "Brewers Gold. Its fruit-forward profile is especially "
            "well suited to dry hopping and modern hop-forward ales."
        ),
        "source": "USDA-ARS / Hop Research Council / Charles Faram",
    },

    {
        "name": "Vista",
        "origin_country": "United States",
        "origin_region": "Pacific Northwest",
        "developer": "USDA Agricultural Research Service",
        "released_year": 2021,
        "hop_type": "Aroma",
        "alpha_acid_min": 9.0,
        "alpha_acid_max": 12.0,
        "beta_acid_min": 3.5,
        "beta_acid_max": 5.5,
        "cohumulone_min": 29.0,
        "cohumulone_max": 34.0,
        "oil_total_min": 1.2,
        "oil_total_max": 1.8,
        "aroma_description": (
            "Fruit-forward profile featuring tropical fruit, "
            "honeydew melon, pear and citrus with floral, "
            "herbal and green-tea character."
        ),
        "flavor_description": (
            "Tropical fruit and melon with pear, citrus and "
            "subtle herbal and green-tea character."
        ),
        "common_descriptors": (
            "tropical fruit, honeydew, melon, pear, citrus, "
            "floral, herbal, green tea"
        ),
        "common_uses": (
            "Lager, Pale Ale, IPA, Hazy IPA, Saison, "
            "late-kettle, whirlpool and dry hop"
        ),
        "brewing_notes": (
            "A versatile modern American aroma variety developed "
            "through the USDA public breeding program. Its softer "
            "fruit and citrus character can work alone or blend "
            "well with more dominant varieties."
        ),
        "source": "USDA-ARS / Yakima Chief Hops",
    },

    {
        "name": "Willamette",
        "origin_country": "United States",
        "origin_region": "Oregon / Pacific Northwest",
        "developer": "USDA Agricultural Research Service",
        "released_year": 1976,
        "hop_type": "Aroma",
        "alpha_acid_min": 4.5,
        "alpha_acid_max": 6.5,
        "beta_acid_min": 3.0,
        "beta_acid_max": 4.5,
        "cohumulone_min": 28.0,
        "cohumulone_max": 32.0,
        "oil_total_min": 0.5,
        "oil_total_max": 1.6,
        "aroma_description": (
            "Classic American aroma profile with floral, "
            "incense-like, elderberry, citrus, hay, tea and "
            "woody character."
        ),
        "flavor_description": (
            "Floral and woody character with earthy, herbal, "
            "tea-like and elderberry notes."
        ),
        "common_descriptors": (
            "floral, incense, elderberry, citrus, hay, tea, woody"
        ),
        "common_uses": (
            "Brown Ale, Lager, Pale Ale, Stout, Porter, ESB, "
            "late-kettle and traditional American aroma hopping"
        ),
        "brewing_notes": (
            "A classic American aroma variety released in 1976 "
            "from the USDA breeding program and derived from "
            "English Fuggle. It provides a distinctly traditional "
            "American interpretation of Fuggle-like character."
        ),
        "source": "Yakima Chief Hops / USDA-ARS",
    },
]


def populate_profiles():
    connection = get_connection()

    updated = 0
    skipped = 0

    try:
        for profile in PROFILES:
            existing = connection.execute(
                """
                SELECT id
                FROM hop_varieties
                WHERE LOWER(name) = LOWER(?)
                """,
                (profile["name"],),
            ).fetchone()

            if not existing:
                print(f"SKIPPED: {profile['name']} - not found")
                skipped += 1
                continue

            assignments = ", ".join(
                f"{column} = ?"
                for column in profile
                if column != "name"
            )

            values = [
                value
                for column, value in profile.items()
                if column != "name"
            ]

            values.append(profile["name"])

            connection.execute(
                f"""
                UPDATE hop_varieties
                SET {assignments},
                    updated_at = CURRENT_TIMESTAMP
                WHERE LOWER(name) = LOWER(?)
                """,
                values,
            )

            updated += 1

        connection.commit()

        print(f"Updated: {updated}")
        print(f"Skipped: {skipped}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    populate_profiles()