import os
import openai
import random
import slack
import os
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
        print(mention)
        user_id = mention[2:-1]
        print(user_id)
        user = client.users_info(user=user_id)
        print(user)
        name = user['user']['real_name']
        print(name)
        return name
    else:
        return text


#replace tag of any user with user's real name
def replaceMention(text):
    if "<@" in text:
        mention = text[text.find("<@"):text.find(">")+1]
        print(mention)
        name = getNameFromMention(text)
        print(name)
        text = text.replace(mention, name)
        print(text)
        return text
    else:
        return text
    

@app.route("/praise", methods=["POST"])
def praise():
  # Get the request data
  data = request.form

  # Get the channel ID and command text from the request data
  channel_id = data.get('channel_id')
  command_text = data.get('text')

  try:
    # Use the WebClient to send a message to the channel
    response = client.chat_postMessage(
      channel=channel_id,
      text=f'{command_text} testing',  # Include the command text in the response
      response_type='in_channel'  # Make the response visible in the channel
    )
  except SlackApiError as e:
    # An error occurred
    print(f'Error: {e}')
    return e, 500

  # Create a response object with a 200 status code and a JSON body
  resp = Response(response=response, status=200, mimetype='application/json')

  # Return the response object
  return resp

@ slack_event_adapter.on('app_mention')
def mention(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')

    #search for each instance of a tag
    #if tag is bot's, remove it
    #if tag is person, replace it with the name, and add it to praise array

    text = event.get('text')

    print(text)
    
    text = text.replace("<@U04FP0Z01QV>", "")

    name = getNameFromMention(text)
    #remove bot name from text
    text = replaceMention(text)

    print("text: " + text)

    try:
    # Use the WebClient to send a message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text="placeholder",#generateText(text, name),  # Include the command text in the response
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": generateText(text, name)
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "@person, now at XX points"
                    }
                }
            ]
            
        )
    except SlackApiError as e:
        # An error occurred
        print(f'Error: {e}')
        return e, 500


def generateText(message, name):
        
    ## options
    response_options = ["a short humorous thank you", "a short serious thank you", "a poem", "a haiku", "a rap", "a space themed thank you", "a thank you with a space pun"]

    prompt_choice = random.choice(response_options)
    print(prompt_choice)

    prompt = "write" + prompt_choice + " to " + name + " for " + message

    completion = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.7,
    )

    return completion.choices[0].text

#print(generateText("helping me with my homework", "Mr. Smith"))

# if __name__ == "__main__":
#     app.run(debug=True, port=3000)