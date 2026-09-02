import re

from integrations.gmail import search_email_content, get_email_body


EMAIL_KEYWORDS = [
    "email",
    "emails",
    "mail",
    "inbox",
    "message",
    "messages",
]

RECENT_KEYWORDS = [
    "recent",
    "today",
    "today's",
    "latest",
    "new",
    "newest",
]


def is_email_question(question):
    """Determine whether a question is asking about email."""

    question_lower = question.lower()

    return any(
        keyword in question_lower
        for keyword in EMAIL_KEYWORDS
    )


def extract_search_term(question):
    """
    Extract a useful search term from a natural-language
    email question.
    """

    question_lower = question.lower()

    # Common phrases that indicate the user wants to find
    # messages from a particular person/company.
    patterns = [
        r"from\s+([a-z0-9._%+\-]+(?:\.[a-z]{2,})?)",
        r"from\s+([a-z0-9& .'\-]+)",
        r"about\s+([a-z0-9& .'\-]+)",
        r"regarding\s+([a-z0-9& .'\-]+)",
        r"related to\s+([a-z0-9& .'\-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, question_lower)

        if match:
            term = match.group(1).strip()

            # Remove common trailing words.
            term = re.sub(
                r"\b(email|emails|message|messages|today|recently)\b",
                "",
                term,
            ).strip()

            if term:
                return term

    return None


def build_gmail_query(question):
    """Translate a natural-language email question into Gmail syntax."""

    question_lower = question.lower()

    search_term = extract_search_term(question)

    if search_term:
        return search_term

    if any(
        keyword in question_lower
        for keyword in RECENT_KEYWORDS
    ):
        return "in:inbox newer_than:1d"

    return "in:inbox"


def answer_email_question(question):
    """
    Search Gmail and return a concise answer.
    """

    query = build_gmail_query(question)

    results = search_email_content(
        query,
        max_results=10,
    )

    if not results:
        return (
            f"I couldn't find any emails matching "
            f"`{query}`."
        )

    lines = [
        f"I found {len(results)} email(s) matching `{query}`:"
    ]

    for index, email in enumerate(results, start=1):
        subject = email.get("subject") or "(No subject)"
        sender = email.get("from") or "(Unknown sender)"
        date = email.get("date") or ""
        snippet = email.get("snippet") or ""

        lines.append("")
        lines.append(f"{index}. **{subject}**")
        lines.append(f"From: {sender}")
        lines.append(f"Date: {date}")
        lines.append(f"{snippet}")

    return "\n".join(lines)