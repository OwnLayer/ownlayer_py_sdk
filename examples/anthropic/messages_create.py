# import anthropic
from ownlayer import anthropic # Ownlayer integration

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=100,
    temperature=0,
    system="Answer must be as short as possible.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's 1+1?"
                }
            ]
        }
    ]
)

print(message.content[0].text)