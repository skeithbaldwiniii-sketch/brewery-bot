import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.gmail import search_emails, get_email_body
def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — GMAIL BODY TEST")
    print("=" * 70)

    results = search_emails(
        "newer_than:1d",
        max_results=1,
    )

    if not results:
        print("No emails found.")
        return

    email = results[0]

    print()
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']}")
    print(f"Date: {email['date']}")
    print()

    full_email = get_email_body(email["id"])

    print("EMAIL BODY")
    print("-" * 70)
    print(full_email["body"][:5000])
    print("-" * 70)


if __name__ == "__main__":
    main()