import requests
import json
from environment import ProductionEnvironment

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"

env = ProductionEnvironment()

# Step 1: Define the tool available to the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_logs",
            "description": "Retrieve checkout service logs",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Step 2: Human provides the investigation instruction
messages = [
    {
        "role": "user",
        "content": """
        Our e-commerce application is experiencing
        a high failure rate in the checkout service.

        Retrieve the checkout service logs using
        the available tool and explain what they indicate.
        Do not claim an unverified root cause.
        """
    }
]

# Helper function to communicate with Ollama
def call_llm(messages, tools=None):

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096
        }
    }

    if tools is not None:
        payload["tools"] = tools

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()["message"]


# Step 3: Send prompt and tool definitions to the LLM
print("\n--- Sending request to LLM ---")

message = call_llm(messages, tools)

messages.append(message)

# Step 4: Execute the requested tool
tool_calls = message.get("tool_calls") or []

if tool_calls:

    for tool_call in tool_calls:

        tool_name = tool_call["function"]["name"]

        print(f"\n[LLM requested tool]: {tool_name}")

        if tool_name == "get_logs":
            result = env.get_logs()
        else:
            result = {"error": "Unknown tool"}

        print("\n[Tool output]")
        print(json.dumps(result, indent=4))

        # Step 5: Return tool output to the LLM
        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(result)
        })

    # Step 6: Generate the final response
    final_response = call_llm(messages)

    print("\n--- Tool-Augmented LLM Response ---\n")
    print(final_response["content"])

else:
    print("\nNo tool call was requested.")
    print(message["content"])