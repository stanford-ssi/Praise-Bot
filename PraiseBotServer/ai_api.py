import random
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

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

def generate_praise(prompt):
        
    ## options
    response_options = ["poem", "haiku (with a title that includes it’s a haiku)", "formal statement", "informal funny statement", "rap song", "limrick"]

    prompt_choice = random.choice(response_options)

    prompt = f" Write a {prompt_choice} to praise {prompt}. Make it funny and include space puns if relevant."


    print("prompt: " + prompt)

    try:
        print("Using OpenAI")
        completion = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a “praise bot” who writes praises for people to thank them for things they did. This is in the context of the Stanford Student Space Initiative (which you can refer to as SSI), a student engineering group at Stanford."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4-turbo",
        )
    except Exception as e:
        try:
            print("Using XAI")
            completion = xai_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a “praise bot” who writes praises for people to thank them for things they did. This is in the context of the Stanford Student Space Initiative (which you can refer to as SSI), a student engineering group at Stanford."},
                    {"role": "user", "content": prompt}
                ],
                model="grok-2-latest",

            )
        except Exception as e:
            return "Error: " + str(e)

    print("completion: " + completion.choices[0].message.content)

    return completion.choices[0].message.content