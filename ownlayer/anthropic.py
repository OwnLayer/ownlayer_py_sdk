from wrapt import wrap_function_wrapper
from .ownlayer_api import post_inference, Inference
from .utils import now, get_metadata
from .calculate_cost import calculate_cost

try:
    from anthropic import *
    from anthropic import MessageStreamManager

except ImportError:
    raise ModuleNotFoundError(
        "Please install anthropic SDK to use ownlayer: 'pip install anthropic'"
    )

def wrap_anthropic_call(wrapped, instance, args, kwargs):
    start_time = now()
    anthropic_response = wrapped(*args, **kwargs)

    settings = {
        "provider": "Anthropic",
        "model": kwargs.get("model", None),
        "max_tokens": kwargs.get("max_tokens", None),
        "temperature": kwargs.get("temperature", None),
        "system_message": kwargs.get("system", None)
    }

    inference = Inference(
        input_messages=kwargs.get('messages'),
        output=anthropic_response.content[0].text,
        start_time=start_time,
        end_time=now(),
        prompt_tokens=anthropic_response.usage.input_tokens,
        total_tokens=anthropic_response.usage.input_tokens + anthropic_response.usage.output_tokens,
        completion_tokens=anthropic_response.usage.output_tokens,
        additional_metadata=get_metadata(),
        settings=settings,
        cost=calculate_cost(kwargs.get("model", None), anthropic_response.usage.input_tokens, anthropic_response.usage.output_tokens)
    )
    post_inference(inference)
    
    return anthropic_response

def wrap_stream_anthropic_enter_call(wrapped, instance: MessageStreamManager, args, kwargs):
    instance.start_time = now()
    return wrapped(*args, **kwargs)

def wrap_stream_anthropic_exit_call(wrapped, instance: MessageStreamManager, args, kwargs):
    start_time= instance.start_time or 0
    request_data = instance._MessageStreamManager__api_request.keywords['body']

    settings = {
        "provider": "Anthropic",
        "model": request_data["model"] if bool(request_data["model"]) else None,
        "max_tokens": request_data["max_tokens"] if bool(request_data["max_tokens"]) else None,
        "temperature": request_data["temperature"] if bool(request_data["temperature"]) else None,
        "system_message": request_data["system"] if bool(request_data["system"]) else None
    }

    message = instance._MessageStreamManager__stream._MessageStream__final_message_snapshot
    output = message.content[0].text

    inference = Inference(
        input_messages=request_data.get('messages'),
        output=output,
        start_time=start_time,
        end_time=now(),
        prompt_tokens=message.usage.input_tokens,
        total_tokens=message.usage.input_tokens + message.usage.output_tokens,
        completion_tokens=message.usage.output_tokens,
        additional_metadata=get_metadata(),
        settings=settings
    )
    post_inference(inference)

    return wrapped(*args, **kwargs)

class AnthropicOwnlayer:
    def initialize(self):
        pass
    
    def register_tracing(self):
        wrap_function_wrapper(
            'anthropic.resources.messages',
            'Messages.create',
            wrap_anthropic_call
        )

        # wrapping stream entry and exit
        # exit, to trace only when stream has ended
        # entry, to set start time
        wrap_function_wrapper(
            'anthropic.lib.streaming._messages',
            'MessageStreamManager.__enter__',
            wrap_stream_anthropic_enter_call
        )
        wrap_function_wrapper(
            'anthropic.lib.streaming._messages',
            'MessageStreamManager.__exit__',
            wrap_stream_anthropic_exit_call
        )


modifier = AnthropicOwnlayer()
modifier.register_tracing()
