import random


SPRINGSTEEN_SNIPPETS = [
    {
        "song": "Born to Run",
        "snippet": "Tramps like us, baby, we were born to run."
    },
    {
        "song": "Born to Run",
        "snippet": "Beyond the Palace, hemi-powered drones scream down the boulevard."
    },
    {
        "song": "Thunder Road",
        "snippet": "It's a town full of losers."
    },
    {
        "song": "Thunder Road",
        "snippet": "It's a town full of losers, I'm pulling out."
    },
    {
        "song": "Dancing in the Dark",
        "snippet": "You can't start a fire without a spark."
    },
    {
        "song": "Dancing in the Dark",
        "snippet": "You sit around getting older."
    },
    {
        "song": "Hungry Heart",
        "snippet": "Everybody's got a hungry heart."
    },
    {
        "song": "Hungry Heart",
        "snippet": "Like a river that don't know where it's flowing."
    },
    {
        "song": "Glory Days",
        "snippet": "Glory days, well, they'll pass you by."
    },
    {
        "song": "Glory Days",
        "snippet": "Glory days, in the wink of a young girl's eye."
    },
    {
        "song": "Badlands",
        "snippet": "It ain't no sin to be glad you're alive."
    },
    {
        "song": "Badlands",
        "snippet": "Poor man wanna be a rich man."
    },
    {
        "song": "Atlantic City",
        "snippet": "Everything dies, baby, that's a fact."
    },
    {
        "song": "Atlantic City",
        "snippet": "Everything dies, baby, that's a fact."
    },
    {
        "song": "The River",
        "snippet": "Is a dream a lie if it don't come true?"
    },
    {
        "song": "The River",
        "snippet": "Then I got Mary pregnant."
    },
    {
        "song": "Rosalita",
        "snippet": "Radio's jammed up with Gospel stations."
    },
    {
        "song": "Rosalita",
        "snippet": "The record company, Rosie, just gave me a big advance."
    },
    {
        "song": "Tenth Avenue Freeze-Out",
        "snippet": "When the change was made uptown."
    },
    {
        "song": "Tenth Avenue Freeze-Out",
        "snippet": "The big man joined the band."
    },
    {
        "song": "I'm on Fire",
        "snippet": "Hey little girl, is your daddy home?"
    },
    {
        "song": "I'm on Fire",
        "snippet": "Sometimes it's like someone took a knife."
    },
    {
        "song": "No Surrender",
        "snippet": "We made a promise we swore we'd always remember."
    },
    {
        "song": "No Surrender",
        "snippet": "We learned more from a three-minute record."
    },
    {
        "song": "My Hometown",
        "snippet": "This is my hometown."
    },
    {
        "song": "My Hometown",
        "snippet": "Now Main Street's whitewashed windows."
    },
    {
        "song": "Cover Me",
        "snippet": "The times are tough now, just getting tougher."
    },
    {
        "song": "Tunnel of Love",
        "snippet": "It ought to be easy, it ought to be simple."
    },
    {
        "song": "Streets of Philadelphia",
        "snippet": "I was bruised and battered."
    },
    {
        "song": "Streets of Philadelphia",
        "snippet": "I walked the avenue till my legs felt like stone."
    },
    {
        "song": "Radio Nowhere",
        "snippet": "I was driving through the misty night."
    },
    {
        "song": "Radio Nowhere",
        "snippet": "Is there anybody alive out there?"
    },
    {
        "song": "Working on the Highway",
        "snippet": "I work five days a week."
    },
    {
        "song": "Working on the Highway",
        "snippet": "I'm working on the highway."
    },
    {
        "song": "Out in the Street",
        "snippet": "I don't wanna go home."
    },
    {
        "song": "Out in the Street",
        "snippet": "I'm out in the street."
    },
    {
        "song": "Prove It All Night",
        "snippet": "Everybody's got a hungry heart."
    },
    {
        "song": "The Promised Land",
        "snippet": "I've done my best to live right."
    },
    {
        "song": "The Rising",
        "snippet": "Come on up for the rising."
    },
    {
        "song": "The Rising",
        "snippet": "Come on up for the rising."
    },
    {
        "song": "Waitin' on a Sunny Day",
        "snippet": "It's rainin' but there ain't a cloud in the sky."
    },
    {
        "song": "Lonesome Day",
        "snippet": "It's a lonesome day."
    },
    {
        "song": "Letter to You",
        "snippet": "I took all the sunshine and I walked it away."
    },
]


def is_springsteen_request(question):
    """
    Determine whether the user is asking Brews Springsteen
    to play or give them something from Bruce Springsteen.
    """

    normalized = question.lower().strip()

    play_terms = [
        "play me",
        "play something",
        "sing me",
        "sing something",
        "give me a song",
        "give me a tune",
        "springsteen song",
        "bruce song",
    ]

    return any(term in normalized for term in play_terms)


_last_springsteen_snippet = None


def play_springsteen():
    """
    Return a random short Bruce Springsteen lyric snippet.
    Avoid repeating the previous selection.
    """

    global _last_springsteen_snippet

    choices = [
        snippet
        for snippet in SPRINGSTEEN_SNIPPETS
        if snippet != _last_springsteen_snippet
    ]

    selection = random.choice(choices)

    _last_springsteen_snippet = selection

    return (
        f"🎸 **{selection['song']}**\n"
        f"_{selection['snippet']}_"
    )