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

openai.api_key = "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"
openai.Model.list()

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("351874bda052ab5615fe8cc0f8769cdd", "/slack/events", app)

client = slack.WebClient(token="xoxb-4610823292-4533033001845-NyNb1iYb10aYPqjDvG4UhcPo")

BOT_ID = client.api_call("auth.test")["user_id"]

def getUserFromMention(mention):
    mention = mention.strip("<@")[:11]
    print(mention)
    return client.users_info(user=mention).data["user"]["real_name"]

def getTextFromMention(mention):
    mention = mention.strip("<@")[:11]
    print(mention)
    return mention

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


def generateText(message, name):
        
    ## options
    response_options = ["a short humorous thank you", "a short serious thank you", "a poem", "a haiku", "a rap"]

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

if __name__ == "__main__":
    app.run(debug=True, port=3000)