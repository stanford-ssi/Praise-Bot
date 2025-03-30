from PraiseBotServer import create_app
from PraiseBotServer.slack_command import setup_slack_commands
from PraiseBotServer.health_check import setup_health_check
from PraiseBotServer.slack_command import praise
import PraiseBotServer.apps as apps
from slack_sdk import WebClient
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

apps.flask_app, apps.slack_app, apps.handler = create_app()

setup_slack_commands(apps.flask_app, apps.slack_app, apps.handler)
setup_health_check(apps.flask_app, apps.handler)

if __name__ == "__main__":
    test_body = {
        "text": "<@U02GG2K5XLH|lskaling> for cleaning the workspace",
        "channel_id": "C7F3VVB1S"
    }

    test_client = WebClient(token=os.environ["SLACK_API_TOKEN"])

    # call the handler directly
    praise(
        ack=lambda: print("ACK"),
        body=test_body,
        respond=print,
        client=test_client
    )

    apps.flask_app.run(port=3000)