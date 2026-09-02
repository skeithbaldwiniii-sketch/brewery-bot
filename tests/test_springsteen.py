import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intelligence.springsteen import (
    is_springsteen_request,
    get_springsteen_mood,
    play_springsteen,
)


TEST_REQUESTS = [
    "play me something sad",
    "play me something to get pumped",
    "play me something happy",
    "play me something romantic",
    "play me something angry",
    "play me something nostalgic",
    "play me something hopeful",
    "play me something",
]


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — MOOD TEST")
    print("=" * 70)

    for request in TEST_REQUESTS:
        mood = get_springsteen_mood(request)

        print()
        print(f"Request: {request}")
        print(f"Mood:    {mood}")
        print(play_springsteen(mood))
        print("-" * 70)


if __name__ == "__main__":
    main()