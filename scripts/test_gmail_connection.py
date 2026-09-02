import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = "gmail_credentials.json"
TOKEN_FILE = "gmail_token.json"


def main():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build(
            "gmail",
            "v1",
            credentials=creds,
        )

        profile = service.users().getProfile(
            userId="me"
        ).execute()

        print()
        print("=" * 60)
        print("GMAIL CONNECTION SUCCESSFUL")
        print("=" * 60)
        print(f"Email address: {profile.get('emailAddress')}")
        print(f"Messages total: {profile.get('messagesTotal')}")
        print(f"Threads total:  {profile.get('threadsTotal')}")
        print("=" * 60)

    except HttpError as error:
        print(f"Gmail API error: {error}")


if __name__ == "__main__":
    main()