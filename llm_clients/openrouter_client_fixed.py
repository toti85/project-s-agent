"""
OpenRouterClient for Project-S
Uses the OpenRouter API for LLM calls.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
from llm_clients.base_client import BaseLLMClient

# Load API key from docs/openrouter_api_key.py or environment
try:
    from docs.openrouter_api_key import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = None

# Try environment variable first, then fallback to file
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
# QWEN3_MODEL_ID = "qwen/qwen3-235b-a22b:free"
FAST_MODEL_ID = "qwen/qwen3-4b:free"

logger = logging.getLogger(__name__)

class OpenRouterClient(BaseLLMClient):
    def __init__(self, model: str = FAST_MODEL_ID, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API kulcs nincs megadva!")
        self.api_url = OPENROUTER_API_URL
        self.default_params = {
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.8,
        }
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Use proper OpenRouter message format
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "top_p": kwargs.get("top_p", 0.8),
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://project-s-agent.local",  # Required by OpenRouter
            "X-Title": "Project-S Multi-Model AI System"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.api_url}/chat/completions", json=payload, headers=headers, timeout=120)
                print("HTTP status:", response.status_code)
                if response.status_code != 200:
                    print("HTTP text:", response.text)
                response.raise_for_status()
                
                # Parse JSON response with error handling
                try:
                    data = response.json()
                except Exception as json_err:
                    print(f"JSON parsing error: {json_err}")
                    return {"error": f"Invalid JSON response: {json_err}"}
                
                # Check if data is valid and contains expected structure
                if not data:
                    print("Empty response data received")
                    return {"error": "Empty response data from OpenRouter API"}
                
                if not isinstance(data, dict):
                    print(f"Unexpected data type: {type(data)}")
                    return {"error": f"Unexpected response type: {type(data)}"}
                
                # Extract response content with robust error handling
                if "choices" in data and data["choices"] and isinstance(data["choices"], list):
                    choice = data["choices"][0]
                    if isinstance(choice, dict):
                        if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                            return choice["message"]["content"]
                        elif "text" in choice:
                            return choice["text"]
                        else:
                            return str(choice)
                    else:
                        return str(choice)
                elif "error" in data:
                    print(f"API returned error: {data['error']}")
                    return {"error": f"OpenRouter API error: {data['error']}"}
                else:
                    print(f"Unexpected response format: {data}")
                    return {"error": f"Unexpected response format from OpenRouter API"}
                
            except httpx.HTTPStatusError as e:
                print("HTTP error:", e.response.status_code, e.response.text)
                return {"error": f"HTTP error: {e.response.status_code} {e.response.text}"}
            except Exception as e:
                print("Exception during OpenRouter call:", str(e))
                return {"error": str(e)}

    async def stream_generate(self, prompt: str, **kwargs):
        # Not implemented for OpenRouter (would require SSE or similar)
        raise NotImplementedError()
