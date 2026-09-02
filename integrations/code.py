import os.path
import base64
from email import message_from_bytes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CREDENTIALS_FILE = os.path.join(
    PROJECT_ROOT,
    "gmail_credentials.json",
)

TOKEN_FILE = os.path.join(
    PROJECT_ROOT,
    "gmail_token.json",
)


def get_gmail_service():
    """Authenticate with Gmail and return the Gmail API service."""

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

    return build(
        "gmail",
        "v1",
        credentials=creds,
    )


def search_emails(query, max_results=10):
    """
    Search Gmail using standard Gmail search syntax.

    Examples:
        from:upserve
        newer_than:7d
        subject:API
        from:someone@example.com
    """

    service = get_gmail_service()

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])

    results = []

    for message in messages:
        message_id = message["id"]

        email_data = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=[
                    "From",
                    "To",
                    "Subject",
                    "Date",
                ],
            )
            .execute()
        )

        headers = {
            header["name"]: header["value"]
            for header in email_data.get("payload", {}).get(
                "headers",
                [],
            )
        }

        results.append(
            {
                "id": message_id,
                "thread_id": email_data.get("threadId"),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": email_data.get("snippet", ""),
            }
        )

    return results