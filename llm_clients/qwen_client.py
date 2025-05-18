"""
Qwen3 client for the Project-S agent.
Provides integration with the Qwen3 language model.
"""

import logging
import json
import asyncio
import os
import subprocess
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import tempfile
from utils.performance_monitor import monitor_performance
from llm_clients.base_client import BaseLLMClient
from llm_clients.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class QwenOllamaClient(OllamaClient):
    """
    Qwen3 Ollama integráció Project-S-hez.
    Alapértelmezett modell: qwen3:8b (vagy a helyi Ollama Qwen3 modell neve)
    """
    def __init__(self, model: str = "qwen3:8b", host: str = "http://localhost:11434"):
        super().__init__(model=model, host=host)
        logger.info(f"QwenOllamaClient initialized with model: {model} at {host}")

    async def ask(self, query: str, **kwargs) -> str:
        """
        Ask a question using the Qwen Ollama model and return the response text.
        
        Args:
            query: The question or prompt to send to the model.
            **kwargs: Additional arguments for generation (optional).
            
        Returns:
            The response text from the model.
        """
        result = await self.generate(query, **kwargs)
        if isinstance(result, dict):
            return result.get("text") or str(result)
        return str(result)

class QwenClient(BaseLLMClient):
    """
    DEPRECATED: Használj QwenOllamaClient-et! Ez a helyi bináris Qwen kliens csak visszafelé kompatibilitás miatt van itt.
    """
    
    def __init__(self, 
                model: str = "qwen",
                executable_path: Optional[str] = None,
                context_length: int = 8192,
                temperature: float = 0.7):
        """
        Initialize the Qwen client.
        
        Args:
            model: The model identifier
            executable_path: Path to the Qwen executable (if None, will try to find it in PATH)
            context_length: Maximum context length
            temperature: Default temperature for generation
        """
        self.model = model
        self.executable_path = executable_path or self._find_executable()
        self.context_length = context_length
        self.default_temperature = temperature
        
        logger.info(f"Qwen client initialized with model: {self.model}")
        
    def _find_executable(self) -> str:
        """
        Find the Qwen executable in the PATH.
        
        Returns:
            Path to the Qwen executable
        """
        # Try to find qwen executable in PATH
        try:
            result = subprocess.run(["which", "qwen"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
        # If not found, check for environment variable
        if "QWEN_PATH" in os.environ:
            return os.environ["QWEN_PATH"]
            
        # Default path for development
        default_path = os.path.expanduser("~/qwen/qwen")
        if os.path.exists(default_path):
            return default_path
            
        # If still not found, use just the name and hope it's in PATH
        return "qwen"
        
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
        temperature = kwargs.get("temperature", self.default_temperature)
        system = kwargs.get("system", "You are a helpful assistant.")
        
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            prompt_data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            json.dump(prompt_data, temp_file)
            temp_file_path = temp_file.name
            
        try:
            # Run Qwen in a subprocess
            cmd = [
                self.executable_path,
                "--input", temp_file_path,
                "--output", "-",  # Output to stdout
                "--no-stream"     # Don't stream output
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Qwen process failed with code {process.returncode}: {stderr.decode()}")
                return {"error": f"Qwen process failed: {stderr.decode()}"}
                
            # Parse the output
            output = stdout.decode().strip()
            try:
                result = json.loads(output)
                
                # Extract the response text
                content = result.get("message", {}).get("content", "")
                
                return {
                    "text": content,
                    "model": self.model,
                    "usage": result.get("usage", {})
                }
            except json.JSONDecodeError:
                logger.error(f"Could not parse Qwen output as JSON: {output}")
                return {"error": "Could not parse Qwen output", "raw_output": output}
        except Exception as e:
            logger.error(f"Error running Qwen process: {str(e)}")
            return {"error": f"Error running Qwen process: {str(e)}"}
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
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
        temperature = kwargs.get("temperature", self.default_temperature)
        system = kwargs.get("system", "You are a helpful assistant.")
        
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            prompt_data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            json.dump(prompt_data, temp_file)
            temp_file_path = temp_file.name
            
        try:
            # Run Qwen in a subprocess with streaming enabled
            cmd = [
                self.executable_path,
                "--input", temp_file_path,
                "--output", "-",  # Output to stdout
                "--stream"        # Enable streaming
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Process the streamed output
            async for line in process.stdout:
                line = line.decode().strip()
                if not line:
                    continue
                    
                try:
                    chunk = json.loads(line)
                    
                    # Extract the chunk text
                    content = chunk.get("content", "")
                    
                    yield {
                        "text": content,
                        "model": self.model,
                        "chunk": True
                    }
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse streaming chunk as JSON: {line}")
                    
            # Wait for the process to finish
            await process.wait()
            
            if process.returncode != 0:
                stderr = await process.stderr.read()
                logger.error(f"Qwen process failed with code {process.returncode}: {stderr.decode()}")
                yield {"error": f"Qwen process failed: {stderr.decode()}"}
        except Exception as e:
            logger.error(f"Error streaming from Qwen process: {str(e)}")
            yield {"error": f"Error streaming from Qwen process: {str(e)}"}
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    async def run_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Run code using Qwen and return the result.
        
        Args:
            code: The code to run
            language: The programming language
            
        Returns:
            The execution result
        """
        prompt = f"Please execute the following {language} code and return only the output:\n\n```{language}\n{code}\n```"
        
        result = await self.generate(prompt, system="You are a code execution assistant. Execute the code provided and return only the output.")
        
        return result
    
    async def ask(self, query: str, **kwargs) -> str:
        """
        Ask a question using the Qwen model and return the response text.
        DEPRECATED: Használj QwenOllamaClient-et!
        Args:
            query: The question or prompt to send to the model.
            **kwargs: Additional arguments for generation (optional).
        Returns:
            The response text from the model.
        """
        # Ha nincs max_tokens, adjunk alapértelmezettet
        if "max_tokens" not in kwargs:
            kwargs["max_tokens"] = 256
        try:
            result = await self.generate(query, **kwargs)
            if isinstance(result, dict):
                text = result.get("text")
                if text:
                    return text
                # Ha error kulcs van, azt is logoljuk
                if "error" in result:
                    logger.error(f"QwenClient.ask error: {result['error']}")
                    return f"[Qwen error] {result['error']}"
                # Ha raw_output van, azt is visszaadjuk
                if "raw_output" in result:
                    logger.warning(f"QwenClient.ask raw output: {result['raw_output']}")
                    return str(result["raw_output"])
                return str(result)
            return str(result)
        except Exception as e:
            logger.error(f"Exception in QwenClient.ask: {str(e)}")
            return f"[Qwen exception] {str(e)}"