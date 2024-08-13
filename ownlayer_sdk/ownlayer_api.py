from dotenv import load_dotenv

load_dotenv()

import requests
import os

# TODO add proper typing
def post_inference(**kwargs):
    url = 'https://develop.ownlayer.com/api/v1/inferences/'
    api_key = os.environ.get("OWNLAYER_API_KEY")

    if api_key is None:
        raise Exception('No OWNLAYER_API_KEY found')

    # print(f"New ownlayer trace {kwargs}")
    res = requests.post(url, json = kwargs, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })

    # TODO handle exception
    if not res.ok:
        print(f"Error tracing call {res.text}")


