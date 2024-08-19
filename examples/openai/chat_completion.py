# import openai
from ownlayer.openai import openai # Ownlayer integration
 
def main():
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        messages=[
          {"role": "system", "content": "Answer must be as short as possible."},
          {"role": "user", "content": "What's 1+1?"}
        ],
    ).choices[0].message.content
 
print(main())