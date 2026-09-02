import random
import re


SPRINGSTEEN_SNIPPETS = [
    # -------------------------------------------------
    # BORN TO RUN
    # -------------------------------------------------
    {
        "song": "Born to Run",
        "snippet": "Tramps like us, baby, we were born to run.",
        "moods": ["pumped", "happy", "hopeful"],
    },
    {
        "song": "Born to Run",
        "snippet": "Beyond the Palace, hemi-powered drones scream down the boulevard.",
        "moods": ["pumped"],
    },

    # -------------------------------------------------
    # THUNDER ROAD
    # -------------------------------------------------
    {
        "song": "Thunder Road",
        "snippet": "It's a town full of losers.",
        "moods": ["sad", "angry", "nostalgic"],
    },
    {
        "song": "Thunder Road",
        "snippet": "It's a town full of losers, I'm pulling out.",
        "moods": ["pumped", "hopeful"],
    },

    # -------------------------------------------------
    # DANCING IN THE DARK
    # -------------------------------------------------
    {
        "song": "Dancing in the Dark",
        "snippet": "You can't start a fire without a spark.",
        "moods": ["pumped", "hopeful", "happy"],
    },
    {
        "song": "Dancing in the Dark",
        "snippet": "You sit around getting older.",
        "moods": ["sad", "angry", "nostalgic"],
    },

    # -------------------------------------------------
    # HUNGRY HEART
    # -------------------------------------------------
    {
        "song": "Hungry Heart",
        "snippet": "Everybody's got a hungry heart.",
        "moods": ["happy", "romantic", "hopeful"],
    },
    {
        "song": "Hungry Heart",
        "snippet": "Like a river that don't know where it's flowing.",
        "moods": ["sad", "nostalgic"],
    },

    # -------------------------------------------------
    # GLORY DAYS
    # -------------------------------------------------
    {
        "song": "Glory Days",
        "snippet": "Glory days, well, they'll pass you by.",
        "moods": ["nostalgic", "sad"],
    },
    {
        "song": "Glory Days",
        "snippet": "Glory days, in the wink of a young girl's eye.",
        "moods": ["nostalgic", "happy"],
    },

    # -------------------------------------------------
    # BADLANDS
    # -------------------------------------------------
    {
        "song": "Badlands",
        "snippet": "It ain't no sin to be glad you're alive.",
        "moods": ["pumped", "happy", "hopeful"],
    },
    {
        "song": "Badlands",
        "snippet": "Poor man wanna be a rich man.",
        "moods": ["angry", "hopeful"],
    },

    # -------------------------------------------------
    # ATLANTIC CITY
    # -------------------------------------------------
    {
        "song": "Atlantic City",
        "snippet": "Everything dies, baby, that's a fact.",
        "moods": ["sad", "angry"],
    },

    # -------------------------------------------------
    # THE RIVER
    # -------------------------------------------------
    {
        "song": "The River",
        "snippet": "Is a dream a lie if it don't come true?",
        "moods": ["sad", "nostalgic"],
    },
    {
        "song": "The River",
        "snippet": "Then I got Mary pregnant.",
        "moods": ["sad"],
    },

    # -------------------------------------------------
    # ROSALITA
    # -------------------------------------------------
    {
        "song": "Rosalita",
        "snippet": "Radio's jammed up with Gospel stations.",
        "moods": ["happy"],
    },
    {
        "song": "Rosalita",
        "snippet": "The record company, Rosie, just gave me a big advance.",
        "moods": ["happy", "pumped"],
    },

    # -------------------------------------------------
    # TENTH AVENUE FREEZE-OUT
    # -------------------------------------------------
    {
        "song": "Tenth Avenue Freeze-Out",
        "snippet": "When the change was made uptown.",
        "moods": ["pumped", "hopeful"],
    },
    {
        "song": "Tenth Avenue Freeze-Out",
        "snippet": "The big man joined the band.",
        "moods": ["happy", "pumped"],
    },

    # -------------------------------------------------
    # I'M ON FIRE
    # -------------------------------------------------
    {
        "song": "I'm on Fire",
        "snippet": "Hey little girl, is your daddy home?",
        "moods": ["romantic"],
    },
    {
        "song": "I'm on Fire",
        "snippet": "Sometimes it's like someone took a knife.",
        "moods": ["sad", "romantic"],
    },

    # -------------------------------------------------
    # NO SURRENDER
    # -------------------------------------------------
    {
        "song": "No Surrender",
        "snippet": "We made a promise we swore we'd always remember.",
        "moods": ["nostalgic", "hopeful"],
    },
    {
        "song": "No Surrender",
        "snippet": "We learned more from a three-minute record.",
        "moods": ["nostalgic", "happy"],
    },

    # -------------------------------------------------
    # MY HOMETOWN
    # -------------------------------------------------
    {
        "song": "My Hometown",
        "snippet": "This is my hometown.",
        "moods": ["nostalgic"],
    },
    {
        "song": "My Hometown",
        "snippet": "Now Main Street's whitewashed windows.",
        "moods": ["nostalgic", "sad"],
    },

    # -------------------------------------------------
    # COVER ME
    # -------------------------------------------------
    {
        "song": "Cover Me",
        "snippet": "The times are tough now, just getting tougher.",
        "moods": ["sad", "angry"],
    },

    # -------------------------------------------------
    # TUNNEL OF LOVE
    # -------------------------------------------------
    {
        "song": "Tunnel of Love",
        "snippet": "It ought to be easy, it ought to be simple.",
        "moods": ["romantic", "sad"],
    },

    # -------------------------------------------------
    # STREETS OF PHILADELPHIA
    # -------------------------------------------------
    {
        "song": "Streets of Philadelphia",
        "snippet": "I was bruised and battered.",
        "moods": ["sad"],
    },
    {
        "song": "Streets of Philadelphia",
        "snippet": "I walked the avenue till my legs felt like stone.",
        "moods": ["sad"],
    },

    # -------------------------------------------------
    # RADIO NOWHERE
    # -------------------------------------------------
    {
        "song": "Radio Nowhere",
        "snippet": "I was driving through the misty night.",
        "moods": ["nostalgic", "sad"],
    },
    {
        "song": "Radio Nowhere",
        "snippet": "Is there anybody alive out there?",
        "moods": ["angry", "hopeful"],
    },

    # -------------------------------------------------
    # WORKING ON THE HIGHWAY
    # -------------------------------------------------
    {
        "song": "Working on the Highway",
        "snippet": "I work five days a week.",
        "moods": ["angry", "nostalgic"],
    },
    {
        "song": "Working on the Highway",
        "snippet": "I'm working on the highway.",
        "moods": ["pumped", "angry"],
    },

    # -------------------------------------------------
    # OUT IN THE STREET
    # -------------------------------------------------
    {
        "song": "Out in the Street",
        "snippet": "I don't wanna go home.",
        "moods": ["happy", "pumped"],
    },
    {
        "song": "Out in the Street",
        "snippet": "I'm out in the street.",
        "moods": ["happy", "pumped"],
    },

    # -------------------------------------------------
    # THE PROMISED LAND
    # -------------------------------------------------
    {
        "song": "The Promised Land",
        "snippet": "I've done my best to live right.",
        "moods": ["hopeful"],
    },

    # -------------------------------------------------
    # THE RISING
    # -------------------------------------------------
    {
        "song": "The Rising",
        "snippet": "Come on up for the rising.",
        "moods": ["hopeful", "pumped"],
    },

    # -------------------------------------------------
    # WAITIN' ON A SUNNY DAY
    # -------------------------------------------------
    {
        "song": "Waitin' on a Sunny Day",
        "snippet": "It's rainin' but there ain't a cloud in the sky.",
        "moods": ["happy", "hopeful"],
    },

    # -------------------------------------------------
    # LONESOME DAY
    # -------------------------------------------------
    {
        "song": "Lonesome Day",
        "snippet": "It's a lonesome day.",
        "moods": ["sad", "nostalgic"],
    },

    # -------------------------------------------------
    # LETTER TO YOU
    # -------------------------------------------------
    {
        "song": "Letter to You",
        "snippet": "I took all the sunshine and I walked it away.",
        "moods": ["sad", "nostalgic"],
    },
]


MOOD_KEYWORDS = {
    "sad": [
        "sad",
        "melancholy",
        "depressing",
        "depressed",
        "blue",
        "down",
        "heartbroken",
        "miserable",
        "somber",
    ],
    "pumped": [
        "pumped",
        "pump me up",
        "hype",
        "hyped",
        "fired up",
        "energetic",
        "energy",
        "motivated",
        "motivation",
        "get me going",
        "get me fired up",
    ],
    "happy": [
        "happy",
        "cheerful",
        "upbeat",
        "fun",
        "joyful",
        "good mood",
    ],
    "romantic": [
        "romantic",
        "romance",
        "love",
        "lovey",
        "sexy",
        "date night",
    ],
    "angry": [
        "angry",
        "mad",
        "pissed",
        "pissed off",
        "frustrated",
        "rage",
        "furious",
        "defiant",
    ],
    "nostalgic": [
        "nostalgic",
        "nostalgia",
        "memories",
        "remember",
        "reflective",
        "looking back",
    ],
    "hopeful": [
        "hopeful",
        "hope",
        "optimistic",
        "inspiring",
        "inspirational",
        "encouraging",
    ],
}


PLAY_TERMS = [
    "play me",
    "play something",
    "sing me",
    "sing something",
    "give me a song",
    "give me a tune",
    "springsteen song",
    "bruce song",
]


def is_springsteen_request(question):
    """
    Determine whether the user is asking Brews Springsteen
    to play or give them something from Bruce Springsteen.
    """

    normalized = question.lower().strip()

    return any(term in normalized for term in PLAY_TERMS)


def get_springsteen_mood(question):
    """
    Determine the requested Springsteen mood.

    Returns:
        str | None
    """

    normalized = question.lower().strip()

    # Check longer phrases first.
    all_matches = []

    for mood, keywords in MOOD_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                all_matches.append((len(keyword), mood))

    if not all_matches:
        return None

    # Prefer the most specific phrase.
    all_matches.sort(reverse=True)

    return all_matches[0][1]


_last_springsteen_snippet = None


def play_springsteen(mood=None):
    """
    Return a short Bruce Springsteen lyric snippet.

    If a mood is supplied, restrict the selection to that mood.
    Avoid repeating the previous selection.
    """

    global _last_springsteen_snippet

    if mood:
        mood_choices = [
            snippet
            for snippet in SPRINGSTEEN_SNIPPETS
            if mood in snippet["moods"]
        ]
    else:
        mood_choices = SPRINGSTEEN_SNIPPETS

    # Fall back to the full catalog if a mood has no matches.
    if not mood_choices:
        mood_choices = SPRINGSTEEN_SNIPPETS

    # Avoid immediate repetition.
    choices = [
        snippet
        for snippet in mood_choices
        if snippet != _last_springsteen_snippet
    ]

    # If the mood only has one available entry, allow it.
    if not choices:
        choices = mood_choices

    selection = random.choice(choices)

    _last_springsteen_snippet = selection

    return (
        f"🎸 **{selection['song']}**\n"
        f"_{selection['snippet']}_"
    )