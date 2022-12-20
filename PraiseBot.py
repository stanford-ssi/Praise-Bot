import os
import openai
import random
import slack
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, Response
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

openai.api_key = os.environ['OPENAI_API_KEY']
openai.Model.list()

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("351874bda052ab5615fe8cc0f8769cdd", "/slack/events", app)

client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

BOT_ID = client.api_call("auth.test")["user_id"]

# Get the user's real name from their user id
def getNameFromMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find(">")+1]
        user_id = mention[2:-1]
        user = client.users_info(user=user_id)
        name = user['user']['real_name']
        return name
    else:
        return text


#replace tag of any user with user's real name
def replaceMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find(">")+1]
        name = getNameFromMention(text)
        text = text.replace(mention, name)
        return text
    else:
        return text
    

@slack_event_adapter.on('app_mention')
def mention(payload):
    Response(), 200
    print("tag received")
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')

    text = event.get('text')
    text = text.replace("<@U04FP0Z01QV>", "")

    name = getNameFromMention(text)
    #remove bot name from text
    text = replaceMention(text)

    cnx = mysql.connector.connect(
        host="iu51mf0q32fkhfpl.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="e0ajs9c6m0vqvgq3",
        password="hprwbgjs2xsf9f2s",
        database="azdlxzpzmqhqjfyh"
    )

    cursor = cnx.cursor()

    query = "SELECT points FROM users WHERE id = 'U02GG2K5XLH';"
    values = ()
    cursor.execute(query, values)
    result = cursor.fetchone()

    cursor.close()
    cnx.close()

    response = generateText(text, name)

    try:
    # Use the WebClient to send a message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text="test"#response + "\n\nNice! " + name + ", now at " + str(result[0]) + " points",#generateText(text, name),  # Include the command text in the response
            # blocks = [
            #     {
            #         "type": "section",
            #         "text": {
            #             "type": "mrkdwn",
            #             "text": response
            #         }
            #     },
            #     {
            #         "type": "divider"
            #     },
            #     {
            #         "type": "section",
            #         "text": {
            #             "type": "mrkdwn",
            #             "text": name + ", now at " + str(result[0]) + " points"
            #         }
            #     }
            # ]
            
        )
    except SlackApiError as e:
        # An error occurred
        print(f'Error: {e}')
        return e, 500
    return Response(), 200


def generateText(message, name):
        
    ## options
    response_options = ["a short humorous thank you", "a short serious thank you", "a poem", "a haiku", "a rap", "a space themed thank you", "a thank you with a space pun"]

    prompt_choice = random.choice(response_options)

    prompt = "write" + prompt_choice + " to " + name + " for " + message

    completion = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.7,
    )

    return completion.choices[0].text

#print(generateText("helping me with my homework", "Mr. Smith"))

if __name__ == "__main__":
    app.run(debug=True, port=3000)