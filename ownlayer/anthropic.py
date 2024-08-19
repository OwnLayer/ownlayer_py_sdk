from wrapt import wrap_function_wrapper
from .ownlayer_api import post_inference, Inference
from .utils import now, get_metadata

try:
    from anthropic import *

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


modifier = AnthropicOwnlayer()
modifier.register_tracing()
