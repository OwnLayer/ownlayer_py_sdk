from ownlayer_py_sdk.ownlayer_api import post_inference

# import openai
from ownlayer_py_sdk.openai import openai # OpenAI integration
 
def main():
    openai_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens=100,
        messages=[
          {"role": "user", "content": "Tell me a joke"}
        ],
        stream=True
    )
    
    for chunk in openai_response:
        print(chunk.choices[0].delta.content or "", end="")
 
main()