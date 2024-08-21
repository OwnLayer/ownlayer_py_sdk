# import anthropic
from ownlayer import anthropic # Ownlayer integration

client = anthropic.Anthropic()

with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-3-5-sonnet-20240620",
) as stream:
  for text in stream.text_stream:
      print(text, flush=True)