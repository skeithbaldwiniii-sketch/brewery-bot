import os
import re
from datetime import datetime, timedelta

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from knowledge.ask import answer_question
from intelligence.task_queries import answer_task_question
from reports.schedule import format_schedule


load_dotenv()


# -------------------------------------------------
# SLACK CONFIGURATION
# -------------------------------------------------

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

PRODUCTION_CHANNEL_ID = "C02TD8XFXLK"
TEST_CHANNEL_ID = "C0BTJKD1PPZ"

# Production remains the destination for automated
# reports sent through send_message().
SLACK_CHANNEL_ID = PRODUCTION_CHANNEL_ID


# -------------------------------------------------
# SLACK MESSAGE SENDING
# -------------------------------------------------

def send_message(message):
    """Send a message to the production brewery channel."""

    if not SLACK_BOT_TOKEN:
        raise RuntimeError(
            "SLACK_BOT_TOKEN was not found in the .env file."
        )

    client = WebClient(token=SLACK_BOT_TOKEN)

    response = client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=message,
    )

    return response


# -------------------------------------------------
# BEER ENCYCLOPEDIA
# -------------------------------------------------

def build_answer(question):
    """
    Get an answer from the beer encyclopedia.

    answer_question() currently prints its answer directly,
    so capture that output and return it as a string.
    """

    import io
    from contextlib import redirect_stdout

    output = io.StringIO()

    with redirect_stdout(output):
        answer_question(question)

    return output.getvalue().strip()


# -------------------------------------------------
# TOMORROW HANDLING
# -------------------------------------------------

def get_tomorrow_name():
    """Return tomorrow's weekday name."""

    tomorrow = datetime.now() + timedelta(days=1)

    return tomorrow.strftime("%A").lower()


def is_tomorrow_schedule_question(question):
    """
    Determine whether the user is asking for tomorrow's
    schedule.

    Examples:

        What's the schedule for tomorrow?
        What is on the schedule tomorrow?
        What are we doing tomorrow?
        What's scheduled tomorrow?
    """

    normalized = question.lower().strip()

    tomorrow_terms = [
        "tomorrow",
    ]

    schedule_terms = [
        "schedule",
        "scheduled",
        "what are we doing",
        "what do we have",
        "what is planned",
        "what's planned",
        "what is on",
        "what's on",
    ]

    has_tomorrow = any(
        term in normalized
        for term in tomorrow_terms
    )

    has_schedule_language = any(
        term in normalized
        for term in schedule_terms
    )

    return has_tomorrow and has_schedule_language


def handle_tomorrow_question(question):
    """
    Answer a schedule question referring to tomorrow.
    """

    if not is_tomorrow_schedule_question(question):
        return None

    tomorrow = get_tomorrow_name()

    return format_schedule(tomorrow)


# -------------------------------------------------
# SCHEDULE QUESTION ROUTER
# -------------------------------------------------

def handle_schedule_question(question):
    """
    Route schedule questions through the advanced
    task intelligence.

    The intelligence layer is now the primary schedule
    system. Slack only handles the special natural-language
    case of "tomorrow" before passing everything else
    to the intelligence layer.
    """

    # ---------------------------------------------
    # TOMORROW
    # ---------------------------------------------

    tomorrow_answer = handle_tomorrow_question(question)

    if tomorrow_answer:
        return tomorrow_answer

    # ---------------------------------------------
    # ADVANCED TASK INTELLIGENCE
    # ---------------------------------------------

    answer = answer_task_question(question)

    if answer:
        return answer

    return None


# -------------------------------------------------
# SLACK APP
# -------------------------------------------------

app = App(token=SLACK_BOT_TOKEN)


@app.event("app_mention")
def handle_mention(event, say):
    """Respond when someone mentions Brews Springsteen."""

    text = event.get("text", "")

    # Remove the bot mention.
    question = re.sub(
        r"<@[^>]+>",
        "",
        text,
    ).strip()

    if not question:
        say(
            "I'm listening. Ask me something about beer "
            "or the brewery schedule!"
        )
        return

    # ---------------------------------------------
    # SCHEDULE / TASK INTELLIGENCE
    # ---------------------------------------------

    schedule_answer = handle_schedule_question(question)

    if schedule_answer:
        say(schedule_answer)
        return

    # ---------------------------------------------
    # BEER ENCYCLOPEDIA
    # ---------------------------------------------

    answer = build_answer(question)

    if answer:
        say(answer)
    else:
        say(
            "I couldn't find anything in the encyclopedia "
            "matching that question."
        )


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":

    if not SLACK_BOT_TOKEN:
        raise RuntimeError(
            "SLACK_BOT_TOKEN was not found in the .env file."
        )

    if not SLACK_APP_TOKEN:
        raise RuntimeError(
            "SLACK_APP_TOKEN was not found in the .env file."
        )

    print("Brews Springsteen is starting...")
    print("Socket Mode enabled.")
    print("Listening for Slack mentions...")
    print("Bolt app is running!")

    handler = SocketModeHandler(
        app,
        SLACK_APP_TOKEN,
    )

    handler.start()