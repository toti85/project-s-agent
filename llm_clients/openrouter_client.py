"""
OpenRouterClient for Project-S
Uses the OpenRouter API for LLM calls.
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional, AsyncGenerator
from llm_clients.base_client import BaseLLMClient

# Load API key from docs/openrouter_api_key.py or environment
try:
    from docs.openrouter_api_key import OPENROUTER_API_KEY
except ImportError:
    OPENROUTER_API_KEY = None

# Try environment variable first, then fallback to file
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
QWEN3_MODEL_ID = "qwen/qwen3-235b-a22b:free"
FAST_MODEL_ID = "qwen/qwen3-4b:free"

logger = logging.getLogger(__name__)

class OpenRouterClient(BaseLLMClient):
    def __init__(self, model: str = QWEN3_MODEL_ID, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided!")
        self.api_url = OPENROUTER_API_URL
        
        # Extract parameters from kwargs
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 1024)
        top_p = kwargs.get('top_p', 0.8)
        
        self.default_params = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        logger.info(f"OpenRouter client initialized with model: {self.model}")
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenRouter API with proper error handling."""
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
                response = await client.post(
                    f"{self.api_url}/chat/completions", 
                    json=payload, 
                    headers=headers, 
                    timeout=120
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenRouter API error: {response.status_code} - {error_text}")
                    return {"error": f"HTTP error: {response.status_code}", "details": error_text}
                
                # Parse JSON response with robust error handling
                try:
                    data = response.json()
                except Exception as json_err:
                    logger.error(f"JSON parsing error: {json_err}")
                    return {"error": f"Invalid JSON response: {json_err}"}
                
                # Check if data is valid and contains expected structure
                if not data:
                    logger.error("Empty response data received")
                    return {"error": "Empty response data from OpenRouter API"}
                
                if not isinstance(data, dict):
                    logger.error(f"Unexpected data type: {type(data)}")
                    return {"error": f"Unexpected response type: {type(data)}"}
                
                # Extract response content with robust error handling
                if "choices" in data and data["choices"] and isinstance(data["choices"], list):
                    if len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if isinstance(choice, dict):
                            if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                                content = choice["message"]["content"]
                                return {
                                    "text": content,
                                    "model": self.model,
                                    "usage": data.get("usage", {}),
                                    "choices": data.get("choices", [])
                                }
                            elif "text" in choice:
                                return {
                                    "text": choice["text"],
                                    "model": self.model,
                                    "usage": data.get("usage", {})
                                }
                
                # Handle API errors
                if "error" in data:
                    error_msg = data["error"]
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get("message", str(error_msg))
                    logger.error(f"API returned error: {error_msg}")
                    return {"error": f"OpenRouter API error: {error_msg}"}
                
                logger.error(f"Unexpected response format: {data}")
                return {"error": f"Unexpected response format from OpenRouter API"}
                
            except httpx.HTTPStatusError as e:
                error_text = e.response.text if hasattr(e.response, 'text') else str(e)
                logger.error(f"HTTP error: {e.response.status_code} {error_text}")
                return {"error": f"HTTP error: {e.response.status_code}", "details": error_text}
            except Exception as e:
                logger.error(f"Exception during OpenRouter call: {str(e)}")
                return {"error": str(e)}

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream generation - not fully implemented for OpenRouter yet."""
        # For now, fallback to regular generation
        result = await self.generate(prompt, **kwargs)
        if "error" not in result:
            yield {
                "text": result.get("text", ""),
                "model": self.model,
                "chunk": False
            }
        else:
            yield {"error": result["error"]}