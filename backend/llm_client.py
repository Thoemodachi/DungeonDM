import openai
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

def generate_response(prompt, model="gpt-4", temperature=0.7, max_tokens=1000):
    """
    Send a prompt to OpenAI GPT and return the response.
    """
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": 
            "You are the Dungeon Master. Narrate the story from a third-person perspective. \
            Describe the world, NPCs, and outcomes of player actions. \
            Answer player questions if asked. \
            Always end your response by asking the player what they want to do next. \
            Do not give meta commentary or advice about the game mechanics."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content