def postMessage(channel_id, response, points, client):
    response = client.chat_postMessage(
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
