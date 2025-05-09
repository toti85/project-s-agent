from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any


class BaseLLMClient(ABC):
    """
    Abstract base class for Language Model clients in Project-S.
    
    All LLM implementations (e.g., QwenClient, LlamaClient) must inherit from this class
    and implement the required methods to ensure consistent interfaces across the system.
    """
    
    @property
    def provider_id(self) -> str:
        """Return the unique identifier for this LLM provider"""
        raise NotImplementedError("Provider ID must be defined in subclass")
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a complete response from the language model in one call.
        
        Args:
            prompt (str): The input prompt or instruction
            **kwargs: Additional model-specific parameters (e.g., temperature, max_tokens)
        
        Returns:
            str: The complete generated text
        """
        pass
    
    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the language model.
        
        Args:
            prompt (str): The input prompt or instruction
            **kwargs: Additional model-specific parameters (e.g., temperature, max_tokens)
            
        Returns:
            AsyncGenerator[str, None]: An async generator that yields text chunks as they're generated
        """
        pass
    
    async def process(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a command from the command router.
        
        This default implementation extracts common parameters and routes to the appropriate
        generation method. Subclasses can override for custom behavior.
        
        Args:
            command (Dict[str, Any]): Command dictionary from the router
            
        Returns:
            Dict[str, Any]: Response with generation results
        """
        operation = command.get("operation", "generate")
        prompt = command.get("prompt", "")
        stream = command.get("stream", False)
        params = command.get("params", {})
        
        if not prompt:
            return {"status": "error", "message": "No prompt provided"}
            
        try:
            if operation == "generate":
                if stream:
                    # This is just a placeholder - actual implementation would 
                    # collect chunks from the generator and return them
                    return {"status": "success", "message": "Stream generation not fully implemented in base class"}
                else:
                    result = await self.generate(prompt, **params)
                    return {
                        "status": "success",
                        "result": result
                    }
            else:
                return {"status": "error", "message": f"Unsupported operation: {operation}"}
        except Exception as e:
            return {"status": "error", "message": f"Generation failed: {str(e)}"}