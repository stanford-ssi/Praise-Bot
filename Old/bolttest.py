import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# @app.event("app_mention")
# def event_test(body, say, logger):
#     logger.info(body)
#     say(f"Hi there, <@{body['event']['user']}>!")

@app.message("test")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(f"Hey there <@{message['user']}>!")

# if __name__ == "__main__":
#     SocketModeHandler(app, "xapp-1-A04G4HQDEMP-4539703661236-cc01f9e1c6679ccf777195d7ac8a7fdee187b1dfa0e9aba3c6647f34c640ae9c").start()
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))