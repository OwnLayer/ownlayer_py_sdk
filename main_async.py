import os
import asyncio

# from openai import AsyncOpenAI
from ownlayer.openai import AsyncOpenAI # OpenAI integration

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

async def main() -> None:
    chat_completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        messages=[
          {"role": "system", "content": "Answer must be as short as possible."},
          {"role": "user", "content": "What's 1+1?"}
        ]
    )
    print(chat_completion.choices[0].message.content)


asyncio.run(main())