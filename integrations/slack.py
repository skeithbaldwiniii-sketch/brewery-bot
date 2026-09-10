import os
import re
from datetime import datetime, timedelta
import html

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from knowledge.ask import (
    answer_question,
    STYLE_FAMILIES,
    search_style_family,
)
from knowledge.beer_queries import answer_brewery_beer_question
from intelligence.task_queries import answer_task_question
from intelligence.beer30_queries import (
    is_wip_question,
    answer_wip_question,
)
from intelligence.springsteen import (
    is_springsteen_request,
    get_springsteen_mood,
    play_springsteen,
)
from intelligence.email_queries import (
    is_email_question,
    answer_email_question,
)
from intelligence.schedule_commands import (
    handle_schedule_write_question,
    is_schedule_move_request,
    is_schedule_add_request,
    is_future_event_add_request,
    handle_future_event_request,
    has_pending_future_event,
    handle_future_event_beer_response,
)
from intelligence.access_control import (
    BEER_KNOWLEDGE,
    ENCYCLOPEDIA,
    SCHEDULE,
    SCHEDULE_WRITE,
    BEER30,
    EMAIL,
    SPRINGSTEEN,
    FUTURE_EVENTS_WRITE,
    has_capability,
    access_denied_message,
)
from reports.schedule import format_schedule


load_dotenv()


# -------------------------------------------------
# SLACK CONFIGURATION
# -------------------------------------------------

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

PRODUCTION_CHANNEL_ID = os.getenv("SLACK_PRODUCTION_CHANNEL_ID")
TEST_CHANNEL_ID = os.getenv("SLACK_TEST_CHANNEL_ID")
STAFF_CHANNEL_ID = os.getenv("BREWS_STAFF_CHANNEL_ID")

# Pending beer-style selections by Slack user.
pending_style_selections = {}


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

    Supports both answer_question() return values and
    legacy output printed directly to stdout.
    """
    import io
    from contextlib import redirect_stdout

    output = io.StringIO()

    with redirect_stdout(output):
        result = answer_question(question)

    if result:
        return result

    return output.getvalue().strip()

def handle_style_selection(user_id, question):
    """Handle a numbered beer-style selection from a Slack user."""

    cleaned = question.lower().strip()

    selection = cleaned.replace("#", "").replace("number ", "").strip()

    if not selection.isdigit():
        return None

    number = int(selection)

    user_styles = pending_style_selections.get(user_id)

    if not user_styles:
        return None

    style_name = user_styles.get(number)

    if not style_name:
        return (
            f"I don't have a style listed as number {number}. "
            "Please choose one of the numbers from the list."
        )

    # The selection has been used.
    pending_style_selections.pop(user_id, None)

    return build_answer(style_name)

def is_brewery_beer_question(question):
    """
    Determine whether a question should be answered
    from the Vanish brewery beer database.
    """

    question_lower = question.lower().strip()

    # Explicit recommendation requests belong to the brewery database.
    recommendation_phrases = [
        "what do you recommend",
        "what would you recommend",
        "recommend a beer",
        "recommend me a beer",
        "what beer should",
        "which beer should",
        "suggest a beer",
        "suggest me a beer",
    ]

    if any(
        phrase in question_lower
        for phrase in recommendation_phrases
    ):
        return True

    # If a specific Vanish beer is mentioned, use the brewery database.
    from knowledge.beer_queries import find_beer_name_in_question

    if find_beer_name_in_question(question):
        return True

    return False

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



def is_schedule_question(question):
    """
    Detect whether a Slack question is asking about
    the brewery schedule or tasks.
    """

    question = question.lower().strip()

    schedule_phrases = [
        "what is on the schedule",
        "what's on the schedule",
        "what is scheduled",
        "what's scheduled",
        "what do we have scheduled",
        "what are we doing",
        "what do we have",
        "what is planned",
        "what's planned",
        "what tasks",
        "what are my tasks",
        "what do i need to do",
        "what do i have to do",
        "remaining tasks",
        "remaining work",
        "today's schedule",
        "todays schedule",
        "today's tasks",
        "todays tasks",
        "tomorrow's schedule",
        "tomorrows schedule",
        "tomorrow's tasks",
        "tomorrows tasks",
    ]

    return any(phrase in question for phrase in schedule_phrases)

def is_schedule_write_request(question):
    """
    Detect whether a question is requesting a schedule modification.
    """

    return (
        is_schedule_move_request(question)
        or is_schedule_add_request(question)
    )

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

def require_capability(channel_id, capability):
    """Return True if this channel may use the requested capability."""
    if has_capability(channel_id, capability):
        return True

    return False

# -------------------------------------------------
# SLACK APP
# -------------------------------------------------

app = App(token=SLACK_BOT_TOKEN)

@app.event("message")
def debug_message_event(body, say, logger):
    logger.info("===== SLACK MESSAGE EVENT RECEIVED =====")
    logger.info(body)

    event = body.get("event", {})

    # Ignore messages generated by the bot itself.
    if event.get("bot_id"):
        return

    # Ignore Slack message subtypes such as edits/deletions.
    if event.get("subtype"):
        return

    user_id = event.get("user")

    if not user_id:
        return

    # Only handle normal messages when this user
    # has a pending future event waiting for beers.
    if not has_pending_future_event(user_id):
        return

    text = html.unescape(event.get("text", "")).strip()

    if not text:
        return

    answer = handle_future_event_beer_response(
        user_id,
        text,
    )

    if answer:
        say(answer)
@app.event("app_mention")
def handle_mention(event, say):
    """Respond when someone mentions Brews Springsteen."""

    user_id = event.get("user")
    text = html.unescape(event.get("text", ""))
    channel_id = event.get("channel")

    # Remove the bot mention.
    question = re.sub(
        r"<@[^>]+>",
        "",
        text,
    ).strip()

    # ---------------------------------------------
    # PENDING FUTURE EVENT BEER RESPONSE
    # ---------------------------------------------

    if has_pending_future_event(user_id):

        answer = handle_future_event_beer_response(
            user_id,
            question,
        )

        if answer:
            say(answer)

        return

    print("===== SLACK MENTION RECEIVED =====")
    print(f"Question: {question}")
    print(f"Channel: {channel_id}")
    print(f"User: {user_id}")

        # ---------------------------------------------
    # PENDING BEER STYLE SELECTION
    # ---------------------------------------------

    if user_id in pending_style_selections:

        answer = handle_style_selection(
            user_id,
            question,
        )

        if answer:
            say(answer)
            return

    if not question:
        say(
            "I'm listening. Ask me something about beer, "
            "the brewery, or the schedule."
        )
        return

        # ---------------------------------------------
    # FUTURE EVENT REQUESTS
    # ---------------------------------------------

    if is_future_event_add_request(question):

        if not require_capability(
            channel_id,
            FUTURE_EVENTS_WRITE,
        ):
            say(access_denied_message(FUTURE_EVENTS_WRITE))
            return

        answer = handle_future_event_request(
            user_id,
            question,
        )

        if answer:
            say(answer)

        return
    # ---------------------------------------------
    # SCHEDULE QUESTIONS
    # ---------------------------------------------

    if is_schedule_question(question):

        if not require_capability(channel_id, SCHEDULE):
            say(access_denied_message(SCHEDULE))
            return

        answer = handle_schedule_question(question)

        if answer:
            say(answer)
        else:
            say("I couldn't find a schedule answer for that question.")

        return

    # ---------------------------------------------
    # BEER30 / PRODUCTION QUESTIONS
    # ---------------------------------------------

    if is_wip_question(question):

        if not require_capability(channel_id, BEER30):
            say(access_denied_message(BEER30))
            return

        answer = answer_wip_question(question)

        if answer:
            say(answer)
        else:
            say("I couldn't find an answer to that Beer30 question.")

        return

    # ---------------------------------------------
    # EMAIL QUESTIONS
    # ---------------------------------------------

    if is_email_question(question):

        if not require_capability(channel_id, EMAIL):
            say(access_denied_message(EMAIL))
            return

        answer = answer_email_question(question)

        if answer:
            say(answer)
        else:
            say("I couldn't find an answer to that email question.")

        return

    # ---------------------------------------------
    # SPRINGSTEEN
    # ---------------------------------------------

    if is_springsteen_request(question):

        if not require_capability(channel_id, SPRINGSTEEN):
            say(access_denied_message(SPRINGSTEEN))
            return

        mood = get_springsteen_mood(question)

        response = play_springsteen(mood)

        if response:
            say(response)

        return

    # ---------------------------------------------
    # SCHEDULE WRITE REQUESTS
    # ---------------------------------------------

    if is_schedule_write_request(question):

        if not require_capability(channel_id, SCHEDULE_WRITE):
            say(access_denied_message(SCHEDULE_WRITE))
            return

        handle_schedule_write_question(
            question,
            user_id,
            channel_id,
            say,
        )

        return

     # ---------------------------------------------
    # BREWERY BEER KNOWLEDGE
    # ---------------------------------------------

    if (
        has_capability(channel_id, BEER_KNOWLEDGE)
        and is_brewery_beer_question(question)
    ):

        answer = answer_brewery_beer_question(question)

        if answer:
            say(answer)
            return

        # ---------------------------------------------------------
    # BEER STYLE FAMILY SELECTION
    # ---------------------------------------------------------

    cleaned_question = question.lower().strip()

    if cleaned_question in STYLE_FAMILIES:
        family = STYLE_FAMILIES[cleaned_question]
        styles = search_style_family(family)

        if styles:
            pending_style_selections[user_id] = {
                number: style["name"]
                for number, style in enumerate(styles, start=1)
            }

            response = (
                f"{family} styles currently in the encyclopedia:\n\n"
            )

            for number, style in enumerate(styles, start=1):
                response += (
                    f"{number}. {style['name']}"
                    f" ({style['category']})\n"
                )

            response += "\nReply with a number to see the description."

            say(response)
            return

    # ---------------------------------------------
    # BEER ENCYCLOPEDIA
    # ---------------------------------------------

    if has_capability(channel_id, ENCYCLOPEDIA):

        answer = build_answer(question)

        if answer:
            say(answer)
            return

    # ---------------------------------------------
    # UNKNOWN / UNAUTHORIZED
    # ---------------------------------------------

    say(
        "I don't have access to brewery information in this channel."
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