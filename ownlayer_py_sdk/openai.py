import types

from wrapt import wrap_function_wrapper
from .ownlayer_api import post_inference
from datetime import datetime, timezone

try:
    import openai
except ImportError:
    raise ModuleNotFoundError(
        "Please install OpenAI to use ownlayer: 'pip install openai'"
    )

try:
    from openai import AsyncOpenAI, OpenAI
except ImportError:
    AsyncOpenAI = None
    OpenAI = None

def now():
    return int(datetime.now(timezone.utc).timestamp())

class OpenAiDefinition:
    module: str
    object: str
    method: str
    type: str
    sync: bool

    def __init__(self, module: str, object: str, method: str, type: str, sync: bool):
        self.module = module
        self.object = object
        self.method = method
        self.type = type
        self.sync = sync

    def __str__(self): 
        return f"({self.module}.{self.object}.{self.method}.{self.type}{"(async)" if not self.sync else ""})"

OPENAI_METHODS_V1 = [
    OpenAiDefinition(
        module="openai.resources.chat.completions",
        object="Completions",
        method="create",
        type="chat",
        sync=True,
    ),
    OpenAiDefinition(
        module="openai.resources.completions",
        object="Completions",
        method="create",
        type="completion",
        sync=True,
    ),
    OpenAiDefinition(
        module="openai.resources.chat.completions",
        object="AsyncCompletions",
        method="create",
        type="chat",
        sync=False,
    ),
    OpenAiDefinition(
        module="openai.resources.completions",
        object="AsyncCompletions",
        method="create",
        type="completion",
        sync=False,
    ),
]

def _ownlayer_wrapper(func):
    def _with_ownlayer(open_ai_definitions, initialize):
        def wrapper(wrapped, instance, args, kwargs):
            return func(open_ai_definitions, initialize, wrapped, args, kwargs)

        return wrapper

    return _with_ownlayer

def _ownlayer_trace(request: dict, openai_response, start_time):
    try:
        messages = request.get("messages", [])
        input = list(filter(lambda x: x["role"] == "user", messages))[-1]["content"]
        output = openai_response.choices[0].message.content
        prompt_tokens = openai_response.usage.prompt_tokens
        total_tokens = openai_response.usage.total_tokens
        settings = {
            "provider": "OpenAI",
            "model": request.get("model", None),
            "max_tokens": request.get("max_tokens", None),
            "temperature": request.get("temperature", None),
            "system_message": list(filter(lambda x: x["role"] == "system", messages))[-1]["content"]
        }
        additional_metadata = { "_source": "ownlayer_py_sdk", "_sdk_version": "0.1" }
        post_inference(input=input,
                       output=output,
                       start_time=start_time,
                       end_time=now(),
                       prompt_tokens=prompt_tokens,
                       total_tokens=total_tokens,
                       completion_tokens= total_tokens - prompt_tokens,
                       additional_metadata=additional_metadata,
                       settings=settings
                       )

        return openai_response
    except Exception as ex:
        print(f"Exception during ownlayer trace: {ex}")
        raise ex
    
@_ownlayer_wrapper
def _wrap(open_ai_resource: OpenAiDefinition, initialize, wrapped, args, kwargs):
    start_time = now()
    openai_response = wrapped(**kwargs)
    _ownlayer_trace(kwargs, openai_response, start_time)
    return openai_response

@_ownlayer_wrapper
async def _wrap_async(
    open_ai_resource: OpenAiDefinition, initialize, wrapped, args, kwargs
):
    start_time = now()
    openai_response = await wrapped(**kwargs)
    _ownlayer_trace(kwargs, openai_response, start_time)
    return openai_response


class OpenAIOwnlayer:
    def initialize(self):
        pass
    
    def register_tracing(self):
        for resource in OPENAI_METHODS_V1:
            wrap_function_wrapper(
                resource.module,
                f"{resource.object}.{resource.method}",
                _wrap(resource, self.initialize)
                if resource.sync
                else _wrap_async(resource, self.initialize)
            )

modifier = OpenAIOwnlayer()
modifier.register_tracing()