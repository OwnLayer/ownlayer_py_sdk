# Ownlayer Python SDK
Python SDK to integrate Ownlayer

## Usage

Install SDK

```shell
pip install ownlayer
```

Change openai import to use Ownlayer wrapper
```diff
- import openai
+ from ownlayer.openai import openai


def some_AI_func:
    # use AI as you did before
    return openai.chat.completions.create(
        ...
    )
```

Be sure to have add `OWNLAYER_API_KEY` to your `.env` file:

```dotenv
OWNLAYER_API_KEY=ey...xxx
```

## Running examples

The "examples" folder holds demos of how to use this SDK. In order to run one from root folder run:

```bash
python -m examples.<path-to-example>
```

E.g. to run `openai/chat_completion.py` example, run:

```bash
python -m examples.openai.chat_completion
```