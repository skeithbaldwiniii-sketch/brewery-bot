from intelligence.beer30_queries import answer_inventory_question


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 INVENTORY HISTORY TEST")
    print("=" * 70)

    questions = [
        "What is the inventory history for Sleek 12 oz cans?",
        "How much did Sleek 12 oz cans change?",
        "When was Sleek 12 oz cans last synced?",
    ]

    for question in questions:
        print()
        print(f"QUESTION: {question}")
        print("-" * 70)

        answer = answer_inventory_question(question)

        if answer:
            print(answer)
        else:
            print("No answer returned.")

    print()
    print("=" * 70)
    print("PASS - History queries completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()