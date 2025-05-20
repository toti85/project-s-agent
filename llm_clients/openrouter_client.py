"""
OpenRouterClient for Project-S
Uses the OpenRouter API for LLM calls.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
from llm_clients.base_client import BaseLLMClient

# Load API key from docs/openrouter_api_key.py
try:
    from docs.openrouter_api_key import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = None

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
        payload = self.default_params.copy()
        payload["prompt"] = prompt
        payload.update(kwargs)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.api_url}/chat/completions", json=payload, headers=headers, timeout=120)
                print("HTTP status:", response.status_code)
                print("HTTP text:", response.text)
                response.raise_for_status()
                data = response.json()
                # Qwen3 válasz formázás - robusztusabb ellenőrzés
                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    # OpenRouter néha 'message', néha 'text' kulcsot ad
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    elif "text" in choice:
                        return choice["text"]
                    else:
                        return choice
                # Ha nincs 'choices', adjuk vissza a teljes választ
                return data
            except httpx.HTTPStatusError as e:
                print("HTTP error:", e.response.status_code, e.response.text)
                return {"error": f"HTTP error: {e.response.status_code} {e.response.text}"}
            except Exception as e:
                print("Exception during OpenRouter call:", str(e))
                return {"error": str(e)}

    async def stream_generate(self, prompt: str, **kwargs):
        # Not implemented for OpenRouter (would require SSE or similar)
        raise NotImplementedError()
