import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(token="xoxb-4610823292-4533033001845-NyNb1iYb10aYPqjDvG4UhcPo")

@app.command("/testing")
def testing(ack, body):
    user_id = body["user_id"]
    ack(f"Hi, <@{user_id}>!")

if __name__ == "__main__":
    SocketModeHandler(app, "xapp-1-A04G4HQDEMP-4539703661236-cc01f9e1c6679ccf777195d7ac8a7fdee187b1dfa0e9aba3c6647f34c640ae9c").start()