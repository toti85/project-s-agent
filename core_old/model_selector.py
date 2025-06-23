"""
Model selector for the Project-S agent.
Intelligently selects the appropriate model for different tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from llm_clients.base_client import BaseLLMClient
from llm_clients.qwen_client import QwenOllamaClient
from llm_clients.ollama_client import OllamaClient
from llm_clients.llamacpp_client import LlamaCppClient

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    Intelligently selects the appropriate model for different tasks.
    """
    
    def __init__(self):
        """Initialize the model selector with available models."""
        self.models = {}
        self.task_affinities = {
            "code": ["qwen", "llama3"],  # Models good at code generation
            "reasoning": ["qwen", "llama3"],  # Models good at reasoning
            "creativity": ["qwen", "llama3"],  # Models good at creative tasks
            "factual": ["qwen", "llama3"]  # Models good at factual recall
        }
        
        logger.info("Model selector initialized")
        
    def register_model(self, name: str, client: BaseLLMClient, tags: List[str] = None):
        """
        Register a model with the selector.
        
        Args:
            name: The name of the model
            client: The client for the model
            tags: Tags describing the model's capabilities
        """
        self.models[name] = {
            "client": client,
            "tags": tags or []
        }
        logger.info(f"Registered model: {name} with tags: {tags}")
        
    def select_model(self, task_type: str, preference: Optional[str] = None) -> BaseLLMClient:
        """
        Select the most appropriate model for a task.
        
        Args:
            task_type: The type of task
            preference: An optional preferred model
            
        Returns:
            The selected model client
        """
        # If a preferred model is specified and available, use it
        if preference and preference in self.models:
            logger.info(f"Using preferred model: {preference} for task: {task_type}")
            return self.models[preference]["client"]
        
        # Get models that are good at this task
        task_models = self.task_affinities.get(task_type, [])
        
        # Find the first available model good at this task
        for model_name in task_models:
            if model_name in self.models:
                logger.info(f"Selected model: {model_name} for task: {task_type}")
                return self.models[model_name]["client"]
        
        # If no suitable model is found, use the first available model
        if self.models:
            model_name = next(iter(self.models))
            logger.warning(f"No ideal model for task: {task_type}, using: {model_name}")
            return self.models[model_name]["client"]
        
        # If no models are available, raise an error
        raise ValueError("No models available")

# Create a singleton instance
model_selector = ModelSelector()

# Register available models (this would typically be done at startup)
def initialize_models():
    """Initialize and register available models."""
    # Register Qwen3 via OpenRouter (cloud, not local)
    from llm_clients.openrouter_client import OpenRouterClient
    try:
        qwen3_openrouter = OpenRouterClient(model="qwen/qwen3-235b-a22b:free")
        model_selector.register_model("qwen3_openrouter", qwen3_openrouter, ["code", "reasoning", "creativity", "factual"])
    except Exception as e:
        logger.warning(f"Could not initialize Qwen3 OpenRouterClient: {str(e)}")

    # (Optional) Remove or comment out local Qwen3/Ollama registration if you want only OpenRouter
    # try:
    #     qwen3_ollama = QwenOllamaClient()
    #     model_selector.register_model("qwen", qwen3_ollama, ["code", "reasoning", "creativity", "factual"])
    # except Exception as e:
    #     logger.warning(f"Could not initialize QwenOllamaClient: {str(e)}")

    # Register Ollama models
    try:
        llama3 = OllamaClient(model="llama3")
        model_selector.register_model("llama3", llama3, ["reasoning", "creativity", "factual"])
    except Exception as e:
        logger.warning(f"Could not initialize Ollama client: {str(e)}")

    # Register llama.cpp models
    try:
        llamacpp = LlamaCppClient(model_path="/path/to/your/model.gguf")
        model_selector.register_model("llamacpp", llamacpp, ["reasoning", "factual"])
    except Exception as e:
        logger.warning(f"Could not initialize llama.cpp client: {str(e)}")

    logger.info(f"Initialized models: {list(model_selector.models.keys())}")