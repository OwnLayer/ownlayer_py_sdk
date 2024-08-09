from ownlayer_py_sdk.ownlayer_api import post_inference

# import openai
from ownlayer_py_sdk.openai import openai # OpenAI integration
 
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