from intelligence.beer30_queries import (
    is_wip_question,
    answer_wip_question,
)


def test(question):
    print()
    print(f"Q: {question}")
    print(f"WIP question: {is_wip_question(question)}")
    print("A:")
    print(answer_wip_question(question))


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 WIP ANSWER TEST")
    print("=" * 70)

    test("What's the total WIP volume?")
    test("What's fermenting?")
    test("What's in the cellar?")
    test("Which tanks are empty?")
    test("What's in UNI-V-01?")
    test("What is currently in the tanks?")


if __name__ == "__main__":
    main()