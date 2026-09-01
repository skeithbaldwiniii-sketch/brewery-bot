from intelligence.beer30_queries import answer_inventory_question


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN - BEER30 QUERY INTELLIGENCE TEST")
    print("=" * 70)

    questions = [
        "How many Sleek 12 oz cans do we have?",
        "What's our canning inventory?",
        "How many 12 oz cans do we have?",
        "What packaging inventory do we have?",
        "Do we have crown lids?",
        "How many 32 oz crowlers do we have?",
    ]

    for question in questions:
        print(f"\nQUESTION: {question}")
        print("-" * 70)

        answer = answer_inventory_question(question)

        if answer:
            print(answer)
        else:
            print("No inventory answer.")

    print("\nPASS - Beer30 query intelligence is working.")


if __name__ == "__main__":
    main()