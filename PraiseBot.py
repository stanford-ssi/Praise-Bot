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

def convertPromptToText(text):
    text = text.replace("><@", "> and <@")
    text = text.replace("> <@", "> and <@")
    while("<@" in text):
        text = replaceMention(text)
    return text

def getUsersFromText(text):
    users = []
    while("<@" in text):
        mention = text[text.find("<@"):text.find(">")+1]
        users.append(mention)
        text = text.replace(mention, "")
    return users
    
def removePraiseBotText(text):
    return text.replace("Praise Bot", "")

@slack_event_adapter.on('app_mention')
def mention(payload):
    Response(), 200
    print("tag received")
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    prompt = convertPromptToText(text)
    prompt = removePraiseBotText(prompt)
    users = getUsersFromText(text)
    
    print(prompt)
    print(users)

    cnx = mysql.connector.connect(
        host="iu51mf0q32fkhfpl.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="e0ajs9c6m0vqvgq3",
        password="hprwbgjs2xsf9f2s",
        database="azdlxzpzmqhqjfyh"
    )


    cursor = cnx.cursor()

    print("users: " + str(users[0]))

    user = users[0].replace("<@", "").replace(">", "")

    query = "SELECT points FROM users WHERE id = 'U02GG2K5XLH';"
    values = ()
    cursor.execute(query, values)
    points = cursor.fetchone()[0] + 1

    updateQuery = "UPDATE users SET points = " + str(points) + " WHERE id = 'U02GG2K5XLH';"
    cursor.execute(updateQuery)
    cnx.commit()

    cursor.close()
    cnx.close()

    response = generateText(prompt)

    try:
    # Use the WebClient to send a message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text="praise",#response + "\n\nNice! " + name + ", now at " + str(result[0]) + " points",#generateText(text, name),  # Include the command text in the response
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": users[0] + ", now at " + str(points) + " points"
                    }
                }
            ]
            
        )
    except SlackApiError as e:
        # An error occurred
        print(f'Error: {e}')
        return e, 500
    return Response(), 200


def generateText(message):
        
    ## options
    response_options = ["a short humorous thank you", "a short serious thank you", "a poem", "a haiku", "a rap", "a space themed thank you", "a thank you with a space pun"]

    prompt_choice = random.choice(response_options)

    prompt = "write " + prompt_choice + " to " + message

    print("prompt: " + prompt)

    completion = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.7,
    )

    return completion.choices[0].text

#print(generateText("helping me with my homework", "Mr. Smith"))

if __name__ == "__main__":
    app.run(debug=False, port=3000)