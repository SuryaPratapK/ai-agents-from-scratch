import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"

prompt = """
Our e-commerce application is experiencing
a high failure rate in the checkout service.

Investigate the issue, identify the root cause,
and recommend a solution.
"""

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

result = response.json()

print("\n--- Standalone LLM Response ---\n")
print(result["message"]["content"])