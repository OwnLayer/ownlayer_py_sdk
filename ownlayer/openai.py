import types

from wrapt import wrap_function_wrapper
from .ownlayer_api import post_inference, Inference
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
    return int(datetime.now(timezone.utc).timestamp() * 1000)

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

# TODO support openai V0
def _is_streaming_response(response):
    return (
        isinstance(response, types.GeneratorType)
        or isinstance(response, types.AsyncGeneratorType)
        or isinstance(response, openai.Stream)
        or isinstance(response, openai.AsyncStream)
    )

class ResponseGenerator:
    def __init__(
        self,
        *,
        request,
        response,
        start_time,
    ):
        self.items = []
        self.start_time = start_time
        self.request = request
        self.response = response

    def __iter__(self):
        try:
            for i in self.response:
                self.items.append(i)

                yield i
        finally:
            self._finalize()

    def __enter__(self):
        return self.__iter__()

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _finalize(self):
        output = ""
        prompt_tokens = 0
        total_tokens = 0
        for chunk in self.items:
            if chunk.usage is not None:
                prompt_tokens += chunk.usage.prompt_tokens
                total_tokens += chunk.usage.total_tokens

            output += (chunk.choices[0].delta.content or "")

        _generate_trace(self.request, output, prompt_tokens, total_tokens, self.start_time)

class ResponseGeneratorAsync:
    def __init__(
        self,
        *,
        request,
        response,
        start_time,
    ):
        self.items = []
        self.start_time = start_time
        self.request = request
        self.response = response

    async def __aiter__(self):
        try:
            async for i in self.response:
                self.items.append(i)

                yield i
        finally:
            await self._finalize()

    async def __aenter__(self):
        return self.__aiter__()

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    async def _finalize(self):
        output = ""
        prompt_tokens = 0
        total_tokens = 0
        for chunk in self.items:
            if chunk.usage is not None:
                prompt_tokens += chunk.usage.prompt_tokens
                total_tokens += chunk.usage.total_tokens

            if len(chunk.choices) > 0:
                output += (chunk.choices[0].delta.content or "")

        _generate_trace(self.request, output, prompt_tokens, total_tokens, self.start_time)

def _ownlayer_wrapper(func):
    def _with_ownlayer(open_ai_definitions, initialize):
        def wrapper(wrapped, instance, args, kwargs):
            return func(open_ai_definitions, initialize, wrapped, args, kwargs)

        return wrapper

    return _with_ownlayer

def _generate_trace(request, output, prompt_tokens, total_tokens, start_time):
    try:
        messages = request.get("messages", [])
        system_messages = list(filter(lambda x: x["role"] == "system", messages))
        settings = {
            "provider": "OpenAI",
            "model": request.get("model", None),
            "max_tokens": request.get("max_tokens", None),
            "temperature": request.get("temperature", None),
            "system_message": system_messages[-1]["content"] if len(system_messages) > 0 else ""
        }
        additional_metadata = { "_source": "ownlayer_py_sdk", "_sdk_version": "0.1.1" }

        inference = Inference(
            input_messages=messages,
            output=output,
            start_time=start_time,
            end_time=now(),
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
            completion_tokens= total_tokens - prompt_tokens,
            additional_metadata=additional_metadata,
            settings=settings
        )
        post_inference(inference)
    except Exception as ex:
        print(f"Exception during ownlayer trace: {ex}")

def _ownlayer_trace(request: dict, openai_response, start_time):
    output = openai_response.choices[0].message.content
    prompt_tokens = openai_response.usage.prompt_tokens
    total_tokens = openai_response.usage.total_tokens
    _generate_trace(request, output, prompt_tokens, total_tokens, start_time)
    return openai_response
    
@_ownlayer_wrapper
def _wrap(open_ai_resource: OpenAiDefinition, initialize, wrapped, args, kwargs):
    start_time = now()
    openai_response = wrapped(**kwargs)

    if _is_streaming_response(openai_response):
        return ResponseGenerator(request=kwargs, response=openai_response, start_time=start_time)
    
    return _ownlayer_trace(kwargs, openai_response, start_time)

@_ownlayer_wrapper
async def _wrap_async(
    open_ai_resource: OpenAiDefinition, initialize, wrapped, args, kwargs
):
    start_time = now()
    openai_response = await wrapped(**kwargs)

    if _is_streaming_response(openai_response):
        return ResponseGeneratorAsync(request=kwargs, response=openai_response, start_time=start_time)
    
    return _ownlayer_trace(kwargs, openai_response, start_time)


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
