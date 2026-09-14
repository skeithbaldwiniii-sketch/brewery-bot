import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integrations.gmail import (
    search_emails,
    get_email_attachments,
    download_email_attachment,
)


def main():
    print("=" * 70)
    print("BREWS SPRINGSTEEN — UPSERVE ATTACHMENT TEST")
    print("=" * 70)

    results = search_emails(
        'has:attachment "Vanish Weekly Product Mix"',
        max_results=5,
    )

    if not results:
        print("No Upserve emails found.")
        return

    email = results[0]

    print()
    print(f"Subject: {email['subject']}")
    print(f"From: {email['from']}")
    print(f"Date: {email['date']}")
    print(f"Message ID: {email['id']}")
    print()

    attachments = get_email_attachments(email["id"])

    csv_attachments = [
        attachment
        for attachment in attachments
        if attachment["filename"].lower().endswith(".csv")
    ]

    if not csv_attachments:
        print("No CSV attachment found.")
        return

    attachment = csv_attachments[0]

    print(f"Downloading: {attachment['filename']}")

    data = download_email_attachment(
        email["id"],
        attachment["attachment_id"],
    )

    print(f"Downloaded bytes: {len(data)}")

    output_path = Path("tests") / attachment["filename"]
    output_path.write_bytes(data)

    print(f"Saved to: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()