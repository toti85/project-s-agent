"""
llama.cpp client for the Project-S agent.
Provides integration with locally running models via llama.cpp.
"""

import logging
import asyncio
import os
import subprocess
import json
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import aiohttp
from utils.performance_monitor import monitor_performance
from llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class LlamaCppClient(BaseLLMClient):
    """
    Client for interacting with locally running llama.cpp models.
    Implements the BaseLLMClient interface.
    """
    
    def __init__(self, 
                 model_path: str = "/path/to/your/model.gguf", 
                 server_port: int = 8080,
                 n_ctx: int = 2048,
                 n_threads: int = 4):
        """
        Initialize the llama.cpp client.
        
        Args:
            model_path: Path to the model file
            server_port: Port to run the server on
            n_ctx: Context window size
            n_threads: Number of threads to use
        """
        self.model_path = model_path
        self.server_port = server_port
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.api_url = f"http://localhost:{server_port}/completion"
        self.server_process = None
        self.headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"llama.cpp client initialized with model: {self.model_path}")
        
    async def start_server(self):
        """Start the llama.cpp server."""
        if self.server_process is None or self.server_process.poll() is not None:
            cmd = [
                "llama-server",
                "-m", self.model_path,
                "-c", str(self.n_ctx),
                "-t", str(self.n_threads),
                "--port", str(self.server_port)
            ]
            
            logger.info(f"Starting llama.cpp server with command: {' '.join(cmd)}")
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server some time to start
            await asyncio.sleep(2)
            
            # Check if the server started successfully
            if self.server_process.poll() is not None:
                stderr = self.server_process.stderr.read()
                logger.error(f"Failed to start llama.cpp server: {stderr}")
                raise RuntimeError(f"Failed to start llama.cpp server: {stderr}")
                
            logger.info("llama.cpp server started successfully")
    
    def stop_server(self):
        """Stop the llama.cpp server."""
        if self.server_process is not None and self.server_process.poll() is None:
            logger.info("Stopping llama.cpp server")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Server did not terminate, killing it")
                self.server_process.kill()
            self.server_process = None
            
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
        # Make sure the server is running
        await self.start_server()
        
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        request_data = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stop": kwargs.get("stop", ["\n\n"]),
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=request_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"llama.cpp API error: {response.status} - {error_text}")
                        return {"error": f"API error: {response.status}", "details": error_text}
                    
                    result = await response.json()
                    
                    return {
                        "text": result.get("content", ""),
                        "model": os.path.basename(self.model_path),
                        "usage": {
                            "prompt_tokens": result.get("prompt_tokens", 0),
                            "completion_tokens": result.get("completion_tokens", 0),
                        }
                    }
        except Exception as e:
            logger.error(f"Error calling llama.cpp API: {str(e)}")
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
        # Make sure the server is running
        await self.start_server()
        
        max_tokens = kwargs.get("max_tokens", 1000)
        temperature = kwargs.get("temperature", 0.7)
        
        request_data = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stop": kwargs.get("stop", ["\n\n"]),
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=request_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"llama.cpp API error: {response.status} - {error_text}")
                        yield {"error": f"API error: {response.status}", "details": error_text}
                        return
                    
                    # Process the streamed response
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "content" in data:
                                    yield {
                                        "text": data["content"],
                                        "model": os.path.basename(self.model_path),
                                        "chunk": True
                                    }
                                    
                                # Check if this is the last message
                                if data.get("stop", False):
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Could not decode JSON: {line}")
        except Exception as e:
            logger.error(f"Error streaming from llama.cpp API: {str(e)}")
            yield {"error": f"API streaming failed: {str(e)}"}
    
    def __del__(self):
        """Clean up when the object is deleted."""
        self.stop_server()