from integrations.slack import app, SLACK_APP_TOKEN
from slack_bolt.adapter.socket_mode import SocketModeHandler


def main():
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


if __name__ == "__main__":
    main()
