Read about the praisebot use [here](https://lawtonskaling.sites.stanford.edu/news/praise-bot)

## Overview

A Slack Bot that praises members for doing good work on Slack. It utilizes the Slack and OpenAI GPT3 API to generate custom praise messages based on an input on why a user is being praised. Involved on Slack with `/praise @member [reason]` 

## How it works

The bot is deployed to a Heroku server and is called when the /praise command is entered in channels. It must be a public channel because of Slack’s limitations on bot users (they can only post in channels they’re members of, and it’s impractical make the bot a member of every private channel). Based on the praised user’s name, a random prompt, the praise reason, and if they enter pronouns in slack, a request is made to the OpenAI API to generate some form of a thank you message (either poetic, funny, or serious) to that user.