"""
OpenRouterClient for Project-S
Uses the OpenRouter API for LLM calls.
"""
import os
import logging
import aiohttp
from typing import Dict, Any, Optional
from llm_clients.base_client import BaseLLMClient

# Load API key from docs/openrouter_api_key.py
try:
    from docs.openrouter_api_key import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

logger = logging.getLogger(__name__)

class OpenRouterClient(BaseLLMClient):
    def __init__(self, model: str = "mistralai/mixtral-8x7b-instruct", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or OPENROUTER_API_KEY
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        if not self.api_key:
            logger.warning("No OpenRouter API key provided!")

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 256),
            "temperature": kwargs.get("temperature", 0.7)
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"OpenRouter API error: {resp.status} - {text}")
                    return {"error": f"API error: {resp.status}", "details": text}
                result = await resp.json()
                # Extract the response text
                try:
                    content = result["choices"][0]["message"]["content"]
                except Exception:
                    content = str(result)
                return {"text": content, "model": self.model, "raw": result}

    async def stream_generate(self, prompt: str, **kwargs):
        # Not implemented for OpenRouter (would require SSE or similar)
        raise NotImplementedError()
