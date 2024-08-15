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
          {"role": "user", "content": "Tell me a joke"}
        ],
        stream=True,
        stream_options={"include_usage": True}
    )

    async for chunk in chat_completion:
        if len(chunk.choices) > 0:
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is not None:
                print(chunk_content, end="")

asyncio.run(main())