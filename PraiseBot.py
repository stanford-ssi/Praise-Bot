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

def getPronounsFromUserId(user_id):
    user = client.users_profile_get(user=user_id)
    print(user)
    pronouns = ""
    try:
        pronouns = user['profile']['fields']['Xf7BUD4MEV']['value'] #Xf7BUD4MEV is the custom field id for pronouns
    except:
        pronouns = ""
    print("pronouns: " + pronouns)
    return pronouns

def getNameFromUserId(user_id):
    print("userID" + user_id)
    user_id = user_id.replace(">", "").replace("<", "").replace("@", "")
    user = client.users_info(user=user_id)
    name = user['user']['real_name']
    return name


#replace tag of any user with user's real name
def replaceMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find(">")+1]
        name = getNameFromMention(text)
        pronounStatement = ""
        if getPronounsFromUserId(mention[2:-1]) != "":
            pronounStatement = " (who uses " + getPronounsFromUserId(mention[2:-1]) + " pronouns)"
        text = text.replace(mention, name + pronounStatement)
        return text
    else:
        return text

def convertPromptToText(text):
    #remove tag of praise bot
    text = removePraiseBotText(text)

    #add spacing if there's multiple users
    text = text.replace("><@", "> and <@")
    text = text.replace("> <@", "> and <@")

    #replace tags with user's real name
    while("<@" in text):
        text = replaceMention(text)
    return text

def getUsersFromText(text):
    users = []
    while("<@" in text):
        mention = text[text.find("<@"):text.find(">")+1]
        if mention == "<@U04FP0Z01QV>":
            text = text.replace(mention, "")
            continue
        users.append(mention)
        text = text.replace(mention, "")
    return users
    
def removePraiseBotText(text):
    while "Praise Bot" in text:
        text = text.replace("Praise Bot", "")
    return text

def postMessage(channel_id, response, points):
    response = client.chat_postMessage(
        channel=channel_id,
        text="Someone sent a Praise!",#response + "\n\nNice! " + name + ", now at " + str(result[0]) + " points",#generateText(text, name),  # Include the command text in the response
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

@slack_event_adapter.on('app_mention')
def mention(payload):
    Response(), 200
    print("tag received")
    event = payload.get('event', {})
    #print(event)
    channel_id = event.get('channel')
    text = event.get('text')

    prompt = convertPromptToText(text)
    prompt = removePraiseBotText(prompt)
    usersArray = getUsersFromText(text)
    
    print(prompt)
    print(usersArray)

    cnx = mysql.connector.connect(
        host="iu51mf0q32fkhfpl.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="e0ajs9c6m0vqvgq3",
        password="hprwbgjs2xsf9f2s",
        database="azdlxzpzmqhqjfyh"
    )


    cursor = cnx.cursor()

    pointNotificationText = ""

    for user in usersArray:
        userId = user[2:-1]

        query = "SELECT points FROM users WHERE id = %s;"
        values = (userId,)
        cursor.execute(query, values)

        print("id" + userId)

        cursorFetch = cursor.fetchone()
        points = 1
        if cursorFetch == None: #user is not in database
            addQuery = "INSERT INTO users (id, name, points) VALUES (%s, %s, %s);"
            values = (userId, getNameFromUserId(user), 0)
            cursor.execute(addQuery, values)
            cnx.commit()
            print("user added to database")
        else:
            points = cursorFetch[0] + 1

        updateQuery = "UPDATE users SET points = %s WHERE id = %s;"
        updateValues = (points, userId)
        cursor.execute(updateQuery, updateValues)
        cnx.commit()



        pointNotificationText += user + ", now at " + str(points) + " points\n"

    response = generateText(prompt)

    cursor.close()
    cnx.close()

    try:
        postMessage(channel_id, response, pointNotificationText)

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


if __name__ == "__main__":
    app.run(debug=False, port=3000)