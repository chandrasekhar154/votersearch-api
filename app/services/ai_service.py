from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generateSQL(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a SQL generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()
    return sql