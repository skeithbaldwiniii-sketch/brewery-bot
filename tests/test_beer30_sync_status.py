from intelligence.beer30_queries import answer_inventory_question


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEIN - BEER30 SYNC STATUS TEST")
    print("=" * 70)

    questions = [
        "When was Beer30 last synced?",
        "Did the last Beer30 sync succeed?",
        "How many records were saved in the last sync?",
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
    print("PASS - Beer30 sync status queries completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()