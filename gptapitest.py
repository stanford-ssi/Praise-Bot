import os
import openai
import random

openai.api_key = "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"
openai.Model.list()


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

print(generateText("helping me with my homework", "Mr. Smith"))