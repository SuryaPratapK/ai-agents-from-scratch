import requests
import json
from environment import ProductionEnvironment

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"
MAX_ITERATIONS = 10

env = ProductionEnvironment(scenario="database")

# Step 1: Register available tools
tool_registry = {
    "get_logs": env.get_logs,
    "get_db_metrics": env.get_db_metrics,
    "get_active_queries": env.get_active_queries,
    "get_deployment_history": env.get_deployment_history,
    "get_payment_health": env.get_payment_health
}

tool_descriptions = {
    "get_logs": "Retrieve checkout service error logs",
    "get_db_metrics": "Retrieve database connection and performance metrics",
    "get_active_queries": "Inspect currently active database queries",
    "get_deployment_history": "Retrieve recent service deployments",
    "get_payment_health": "Check payment service health"
}

# Define tools for the LLM
tools = []

for name, description in tool_descriptions.items():
    tools.append({
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    })

# Step 2: Define the objective
messages = [
    {
        "role": "system",
        "content": """
        You are a production incident investigation agent.

        Use the available tools to investigate the incident.
        Decide which tool to call based on the evidence
        collected so far.

        Continue investigating until you have sufficient
        evidence to identify the root cause.

        Avoid unnecessary or repeated tool calls.
        Do not invent information or assume a root cause
        without sufficient evidence.

        When the investigation is complete, provide:
        1. Root cause
        2. Supporting evidence
        3. Recommended corrective action
        4. Steps to verify system recovery

        Do not execute corrective actions.
        If evidence is insufficient, state that clearly.
        """
    },
    {
        "role": "user",
        "content": """
        Our e-commerce application is experiencing
        a high failure rate in the checkout service.

        Investigate the incident and identify
        the root cause.
        """
    }
]

# Step 3: Function to communicate with the LLM
def call_llm(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()["message"]


# Step 4: Agent execution loop
print("\n--- AI Agent Started ---")

for iteration in range(1, MAX_ITERATIONS + 1):

    print(f"\n--- Iteration {iteration} ---")
    print("Consulting LLM...")

    message = call_llm(messages)
    messages.append(message)

    tool_calls = message.get("tool_calls") or []

    # If no tool call is requested, finish
    if not tool_calls:
        print("\n--- AI Agent Final Response ---\n")
        print(message.get("content", ""))
        print("\n--- AI Agent Completed ---")
        break

    # Execute the tools selected by the LLM
    for tool_call in tool_calls:

        tool_name = tool_call["function"]["name"]

        print(f"\n[Agent selected tool]: {tool_name}")

        if tool_name in tool_registry:
            try:
                result = tool_registry[tool_name]()
            except Exception as error:
                result = {"error": str(error)}
        else:
            result = {"error": "Unknown tool"}

        print("\n[Tool output]")
        print(json.dumps(result, indent=4))

        # Return observations to the LLM
        messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": json.dumps(result)
        })

else:
    print("\nMaximum iterations reached.")
    print("Investigation stopped without a final response.")