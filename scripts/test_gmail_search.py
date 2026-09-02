import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.gmail import search_emails

def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — GMAIL SEARCH TEST")
    print("=" * 70)

    query = input("Gmail search query: ").strip()

    if not query:
        print("No search query provided.")
        return

    results = search_emails(query, max_results=10)

    print()
    print(f"Found {len(results)} message(s)")
    print()

    for index, email in enumerate(results, start=1):
        print("-" * 70)
        print(f"{index}. {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Date: {email['date']}")
        print(f"Snippet: {email['snippet']}")

    print("-" * 70)


if __name__ == "__main__":
    main()