import os
from openai import OpenAI
import random
import mysql.connector
import requests
import threading
from gevent.pywsgi import WSGIServer
from pathlib import Path
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
from flask import Flask, request, Response
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
import time


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

openai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ['OPENAI_API_KEY']
)

xai_client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ['GROK_API_KEY'],
    base_url="https://api.x.ai/v1"
)

signing_secret = os.environ['SLACK_SIGNING_SECRET']

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize Slack Bolt app
slack_app = App(
    token=os.getenv("SLACK_API_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

handler = SlackRequestHandler(slack_app)


# Get the user's real name from their user id
def getNameFromMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find("|")+1]
        user_id = mention[2:-1]
        user = slack_app.client.users_info(user=user_id)
        name = user['user']['real_name']
        return name
    else:
        return text

def getNameFromUserId(user_id):
    print("userID" + user_id)
    user = client.users_info(user=user_id)
    name = user['user']['real_name']
    return name


#replace tag of any user with user's real name
def replaceMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find("|")+1]
        removal = text[text.find("<@"):text.find(">")+1]
        name = getNameFromMention(text)
        text = text.replace(removal, name)
        return text
    else:
        return text

def get_prompt_from_command(text):
    #remove tag of praise bot

    #add spacing if there's multiple users
    text = text.replace("><@", "> and <@")
    text = text.replace("> <@", "> and <@")

    #replace tags with user's real name
    while("<@" in text):
        text = replaceMention(text)
    return text

def get_users_from_command(text):
    users = []
    while("<@" in text):
        startIndex = text.find("<@")
        endIndex = text.find("|")
        mention = text[startIndex+2:endIndex]
        users.append(mention)
        text = text.replace(text[startIndex:endIndex+1], "")
    return users

def getUserFromText(text):
    mention = text[text.find("<@"):text.find("|")+1]
    return mention

def postMessage(channel_id, response, points):
    response = slack_app.client.chat_postMessage(
        channel=channel_id,
        text="Someone sent a Praise!",
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response
                }
            },
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": points
                }]
            }
        ]
        
    )

# Naming convention: command_text -> prompt_text & user_text

@slack_app.command('/praise')
def praise(ack, body, respond, client):
    ack()

    print("Praise Request Received")
    print(body)

    command_text = body['text']
    channel_id = body['channel_id']

    prompt = get_prompt_from_command(command_text) #might need to remove Praise Bot text
    usersArray = get_users_from_command(command_text)

    print ("prompt: " + prompt)
    print ("users: " + str(usersArray))

    x = threading.Thread(
        target=some_processing,
        args=(usersArray, prompt, channel_id,)
    )
    x.start()

    return {"response_type": "in_channel"}


def some_processing(usersArray, prompt, channel_id):
    cnx = mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        database=os.environ['DB_DATABASE']
    )


    cursor = cnx.cursor()

    pointNotificationText = ""

    for userId in usersArray:
        query = "SELECT points FROM users WHERE id = %s;"
        values = (userId,)
        cursor.execute(query, values)

        cursorFetch = cursor.fetchone()
        points = 1
        if cursorFetch == None: #user is not in database
            addQuery = "INSERT INTO users (id, name, points) VALUES (%s, %s, %s);"
            values = (userId, getNameFromUserId(userId), 0)
            cursor.execute(addQuery, values)
            cnx.commit()
            print("user added to database")
        else:
            points = cursorFetch[0] + 1

        updateQuery = "UPDATE users SET points = %s WHERE id = %s;"
        updateValues = (points, userId)
        cursor.execute(updateQuery, updateValues)
        cnx.commit()


        if points < 10:
            pointNotificationText += "<@"+userId + ">, now with " + str(points) + " points\n"
        elif points < 15:
            pointNotificationText += "<@"+userId + ">, with a lot of points\n"
        elif points < 25:
            pointNotificationText += "<@"+userId + ">, with too many points\n"
        else:
            pointNotificationText += "<@"+userId + ">, with far too many points\n"

    response = generate_praise(prompt)

    print("response: " + response)

    cursor.close()
    cnx.close()

    try:
        postMessage(channel_id, response, pointNotificationText)

    except SlackApiError as e:
        # An error occurred
        print(f'Error: {e}')
        return e, 500

    message = {        
        "text": "testing",
        "response_type": "in_channel"
        
    }
    return message

def generate_praise(prompt):
        
    ## options
    response_options = ["poem", "haiku (with a title that includes it’s a haiku)", "formal statement", "informal funny statement", "rap song", "limrick"]

    prompt_choice = random.choice(response_options)

    prompt = f" Write a {prompt_choice} to praise {prompt}. Make it funny and include space puns if relevant."


    print("prompt: " + prompt)

    if random.random() < 0.5:
        completion = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a “praise bot” who writes praises for people to thank them for things they did. This is in the context of the Stanford Student Space Initiative (which you can refer to as SSI), a student engineering group at Stanford. The person you’re praising has the description of {bio}."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-3.5-turbo",
        )
    else:
        completion = xai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a “praise bot” who writes praises for people to thank them for things they did. This is in the context of the Stanford Student Space Initiative (which you can refer to as SSI), a student engineering group at Stanford. The person you’re praising has the description of {bio}."},
                {"role": "user", "content": prompt}
            ],
            model="grok-2-latest",

        )

    print("completion: " + completion.choices[0].message.content)

    return completion.choices[0].message.content


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    print("Starting Praise Bot")
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

    flask_app.run(port=3000)

