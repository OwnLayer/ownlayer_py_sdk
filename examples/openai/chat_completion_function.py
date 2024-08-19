# import openai
from ownlayer.openai import openai # Ownlayer integration

def main():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_delivery_date",
                "description": "Get the delivery date for a customer's order. Call this whenever you need to know the delivery date, for example when a customer asks 'Where is my package'",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The customer's order ID.",
                        }
                    },
                    "required": ["order_id"],
                    "additionalProperties": False,
                },
            },
        }
    ]
    return (
        openai.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=100,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user.",
                },
                {"role": "user", "content": "I want the delivery date for my order. I think the order is 123, I guess"},
            ],
            tools=tools,
        )
        .choices[0]
        .message.tool_calls
    )


print(main())
