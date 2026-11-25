import requests
import json
from environment import ProductionEnvironment

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"

env = ProductionEnvironment(scenario="database")


# Helper function to communicate with the LLM
def call_llm(prompt):

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
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

    return response.json()["message"]["content"]


# Step 1: Retrieve checkout service logs
print("\n--- AI Workflow Started ---")

print("\n[Step 1] Retrieving checkout logs")

logs = env.get_logs()

print(json.dumps(logs, indent=4))

evidence = {
    "checkout_logs": logs
}


# Step 2: Follow predefined conditional branches
print("\n[Step 2] Identifying failure category")

log_text = " ".join(logs).lower()

if "db connection" in log_text or "database" in log_text:

    print("Database investigation branch selected")

    print("\n[Step 3] Retrieving database metrics")

    evidence["database_metrics"] = env.get_db_metrics()

    print(json.dumps(
        evidence["database_metrics"], indent=4
    ))

    print("\n[Step 4] Inspecting active queries")

    evidence["active_queries"] = env.get_active_queries()

    print(json.dumps(
        evidence["active_queries"], indent=4
    ))

    print("\n[Step 5] Checking deployment history")

    evidence["deployment_history"] = (
        env.get_deployment_history()
    )

    print(json.dumps(
        evidence["deployment_history"], indent=4
    ))

elif "payment service" in log_text:

    print("Payment investigation branch selected")

    print("\n[Step 3] Checking payment service health")

    evidence["payment_health"] = env.get_payment_health()

    print(json.dumps(
        evidence["payment_health"], indent=4
    ))

else:

    print("Unknown failure category")


# Step 6: Send collected evidence to the LLM
print("\n[Final Step] Analyzing collected evidence")

prompt = f"""
Our e-commerce application is experiencing
a high failure rate in the checkout service.

The automated investigation workflow has
collected the following evidence:

{json.dumps(evidence, indent=4)}

Based only on the collected evidence:

1. Identify the root cause.
2. Explain why checkout requests are failing.
3. Recommend a corrective action.
4. Suggest how to verify system recovery.

If the evidence is insufficient, state that clearly.
"""

final_response = call_llm(prompt)

print("\n--- AI Workflow Response ---\n")

print(final_response)

print("\n--- AI Workflow Completed ---")