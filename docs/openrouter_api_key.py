# OpenRouter API Key for Project-S
# This file contains the API key for OpenRouter integration

# Current API Key (replace with your actual key)
OPENROUTER_API_KEY = "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"

# API Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "qwen/qwen-2.5-coder-32b-instruct"  # High-quality, cost-effective model

# Headers required by OpenRouter
OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://project-s-agent.local",
    "X-Title": "Project-S Multi-AI Agent System"
}
