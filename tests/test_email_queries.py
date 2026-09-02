import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intelligence.email_queries import (
    is_email_question,
    build_gmail_query,
    answer_email_question,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — EMAIL INTELLIGENCE TEST")
    print("=" * 70)

    question = input("Ask Brews Springsteen: ").strip()

    print()
    print(f"Email question: {is_email_question(question)}")

    query = build_gmail_query(question)

    print(f"Gmail query: {query}")
    print()
    print("RESULT")
    print("-" * 70)

    answer = answer_email_question(question)

    print(answer)

    print("-" * 70)


if __name__ == "__main__":
    main()