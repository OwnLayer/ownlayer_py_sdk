from typing import Optional

class CostDetail:
    input: float
    output: float

    def __init__(self, input: float, output: float):
        self.input = input
        self.output = output

    def __str__(self):
         return f"CostDetail({self.input},{self.output})"

openai_models_cost: dict[str, CostDetail] = {
    'gpt-4o': CostDetail(5, 15),
    'gpt-4o-2024-08-06': CostDetail(2.5, 10),
    'gpt-4o-2024-05-13': CostDetail(5, 15),
    'gpt-4o-mini': CostDetail(0.15, 0.6),
    'gpt-4o-mini-2024-07-18': CostDetail(0.15, 0.6),
    'gpt-4-turbo': CostDetail(10, 30),
    'gpt-4-turbo-2024-04-09': CostDetail(10, 30),
    'gpt-4': CostDetail(30, 60),
    'gpt-4-32k': CostDetail(60, 120),
    'gpt-4-0125-preview': CostDetail(10, 30),
    'gpt-4-1106-preview': CostDetail(10, 30),
    'gpt-4-vision-preview': CostDetail(10, 30),
    'gpt-3.5-turbo': CostDetail(0.5, 1.5), # Currently points to gpt-3.5-turbo-0125
    'gpt-3.5-turbo-0125': CostDetail(0.5, 1.5),
    'gpt-3.5-turbo-instruct': CostDetail(1.5, 2),
    'gpt-3.5-turbo-1106': CostDetail(1, 2),
    'gpt-3.5-turbo-0613': CostDetail(1.5, 2),
    'gpt-3.5-turbo-16k-0613': CostDetail(3, 4),
    'gpt-3.5-turbo-0301': CostDetail(1.5, 2),
    'davinci-002': CostDetail(2, 2),
    'babbage-002': CostDetail(0.4, 0.4),
}

def _calculate(input_cost_per_m: float, output_cost_per_m: float, input_token_count: int, output_token_count: int):
    input_cost = input_token_count * input_cost_per_m / 1000000
    output_cost = output_token_count * output_cost_per_m / 1000000
    return input_cost + output_cost

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    if model is None:
        return None
    
    normalized = model.lower()
    # anthorpic models concat a date: "claude-3-5-sonnet-20240620"
    # se we check for start of string
    if normalized.startswith('claude-3-5-sonnet'):
        return _calculate(3, 15, input_tokens, output_tokens)
    
    if normalized.startswith('claude-3-5-opus'):
        return _calculate(15, 75, input_tokens, output_tokens)
    
    if normalized.startswith('claude-3-5-haiku'):
        return _calculate(0.25, 1.25, input_tokens, output_tokens)
    
    # for openai we have exact model name matches
    if normalized in openai_models_cost:
        return _calculate(openai_models_cost[model].input, openai_models_cost[model].output, input_tokens, output_tokens)
    
    # unkwon model
    return None