from flask import request
import os
from PraiseBotServer.text_formatting import getNameFromUserId, get_prompt_from_command, get_users_from_command
import threading
import mysql.connector
from PraiseBotServer.slack_api import postMessage
from PraiseBotServer.ai_api import generate_praise
from PraiseBotServer.database import fetch_and_update_database

def setup_slack_commands(flask_app, slack_app, handler):

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return handler.handle(request)

    @slack_app.command('/praise')
    def praise_wrapper(ack, body, respond):
        return praise(ack, body, respond, slack_app.client)

def praise(ack, body, respond, client):
    command_text = body['text']
    channel_id = body['channel_id']

    ack({
        "response_type": "in_channel",
    })

    print("Praise Request Received")
    print(body)

    prompt = get_prompt_from_command(command_text, client) 
    usersArray = get_users_from_command(command_text)

    print ("prompt: " + prompt)
    print ("users: " + str(usersArray))

    x = threading.Thread(
        target=some_processing,
        args=(usersArray, prompt, channel_id, client)
    )
    x.start()
    

    return {
        "response_type": "in_channel",
        "text": f"*You said:* `{command_text}`\nGenerating praise... hang tight! 🚀"
    }

def some_processing(usersArray, prompt, channel_id, client):
    
    user_points = fetch_and_update_database(usersArray, client)

    pointNotificationText = ""

    for userId in usersArray:
        
        points = user_points[userId]

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

    try:
        postMessage(channel_id, response, pointNotificationText, client)

    except SlackApiError as e:
        # An error occurred
        print(f'Error: {e}')
        return e, 500

    message = {        
        "text": "testing",
        "response_type": "in_channel"
        
    }
    return message
