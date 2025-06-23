import os
from docs.openrouter_api_key import OPENROUTER_API_KEY

print("Environment OPENROUTER_API_KEY:", os.environ.get("OPENROUTER_API_KEY", "NOT SET"))
print("File OPENROUTER_API_KEY:", OPENROUTER_API_KEY)

# Test the client initialization
from llm_clients.openrouter_client import OpenRouterClient

try:
    client = OpenRouterClient(model="qwen/qwen-72b")
    print("Client API key:", client.api_key[:20] + "..." if client.api_key else "NONE")
    print("Client model:", client.model)
    print("Client URL:", client.api_url)
except Exception as e:
    print("Error creating client:", e)
