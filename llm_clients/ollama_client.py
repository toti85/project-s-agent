"""
Ollama client for the Project-S agent.
Provides integration with locally running models via Ollama.
"""

import logging
import json
import asyncio
import os
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import aiohttp
from utils.performance_monitor import monitor_performance
from llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class OllamaClient(BaseLLMClient):
    """
    Client for interacting with locally running Ollama models.
    Implements the BaseLLMClient interface.
    """
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            model: The model to use for generation
            host: The host where Ollama is running
        """
        self.model = model
        self.host = host
        self.api_url = f"{host}/api/generate"
        self.headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"Ollama client initialized with model: {self.model} at {self.host}")
        
    @monitor_performance
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a response to a prompt.
        
        Args:
            prompt: The prompt to generate a response to
            **kwargs: Additional arguments for the generation
            
        Returns:
            The generated response
        """
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        system = kwargs.get("system", "You are a helpful assistant.")
        
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=request_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}", "details": error_text}
                    
                    # Ollama returns the response as a stream of JSON objects
                    # Each object has a 'response' field with a text chunk
                    # We need to accumulate all chunks to get the complete response
                    full_response = ""
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                full_response += data.get("response", "")
                            except json.JSONDecodeError:
                                logger.warning(f"Could not decode JSON: {line}")
                    
                    return {
                        "text": full_response,
                        "model": self.model,
                        "usage": {
                            "prompt_tokens": len(prompt) // 4,  # Rough estimate
                            "completion_tokens": len(full_response) // 4,  # Rough estimate
                        }
                    }
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return {"error": f"API call failed: {str(e)}"}
            
    @monitor_performance
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a response to a prompt, streaming the output.
        
        Args:
            prompt: The prompt to generate a response to
            **kwargs: Additional arguments for the generation
            
        Yields:
            Chunks of the generated response
        """
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        system = kwargs.get("system", "You are a helpful assistant.")
        
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            },
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=request_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        yield {"error": f"API error: {response.status}", "details": error_text}
                        return
                    
                    # Process the streamed response
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                chunk = data.get("response", "")
                                if chunk:
                                    yield {
                                        "text": chunk,
                                        "model": self.model,
                                        "chunk": True
                                    }
                                
                                # Check if this is the last message
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Could not decode JSON: {line}")
        except Exception as e:
            logger.error(f"Error streaming from Ollama API: {str(e)}")
            yield {"error": f"API streaming failed: {str(e)}"}