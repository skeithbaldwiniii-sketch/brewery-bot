from knowledge.ask import answer_question


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - WIP ROUTER TEST")
    print("=" * 70)

    questions = [
        "What's the total WIP volume?",
        "What's fermenting?",
        "What's in the cellar?",
        "What's in UNI-V-01?",
        "Which tanks are empty?",
    ]

    for question in questions:
        print()
        print(f"Q: {question}")
        print("A:")
        answer_question(question)
        print("-" * 70)


if __name__ == "__main__":
    main()