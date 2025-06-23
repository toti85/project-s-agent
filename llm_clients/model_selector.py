"""
Model selector for the Project-S agent.
Intelligently selects the appropriate model for different tasks.
"""

import logging
from typing import Dict, Any, List, Optional
from llm_clients.base_client import BaseLLMClient
from llm_clients.openrouter_client import OpenRouterClient
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
            return self.models[model_name]["client"]        # If no models are available, raise an error
        raise ValueError("No models available")

    def get_model(self, provider: str, model_name: str, **parameters) -> BaseLLMClient:
        """
        Get a model by provider and model name with parameters.
        This method provides compatibility with multi_model_integration.py
        
        Args:
            provider: The provider name (e.g., "openrouter", "ollama", "llamacpp")
            model_name: The specific model name
            **parameters: Additional parameters for model configuration
            
        Returns:
            The model client instance
        """
        # Create a composite key for the model
        model_key = f"{provider}_{model_name}"
        
        # If model is already registered, return it
        if model_key in self.models:
            logger.info(f"Retrieved existing model: {model_key}")
            return self.models[model_key]["client"]
          # Try to create the model dynamically based on provider
        try:
            if provider.lower() == "openrouter":
                from llm_clients.openrouter_client import OpenRouterClient
                client = OpenRouterClient(model=model_name, **parameters)
                self.register_model(model_key, client, ["code", "reasoning", "creativity", "factual"])
                logger.info(f"Created new OpenRouter model: {model_key}")
                return client
                
            elif provider.lower() == "ollama":
                from llm_clients.qwen_client import QwenOllamaClient
                client = QwenOllamaClient(model=model_name, **parameters)
                self.register_model(model_key, client, ["reasoning", "creativity", "factual"])
                logger.info(f"Created new Ollama model: {model_key}")
                return client
                
            elif provider.lower() == "llamacpp":
                from llm_clients.llamacpp_client import LlamaCppClient
                # For llamacpp, model_name should be the path to the model file
                client = LlamaCppClient(model_path=model_name, **parameters)
                self.register_model(model_key, client, ["reasoning", "factual"])
                logger.info(f"Created new LlamaCpp model: {model_key}")
                return client
                
            else:
                # If provider is not recognized, try to find a suitable existing model
                logger.warning(f"Unknown provider: {provider}, trying to find suitable model")
                return self.select_model("reasoning")  # Fallback to reasoning task
                
        except Exception as e:
            logger.error(f"Failed to create model {provider}/{model_name}: {str(e)}")
            # Fallback to an existing model if available
            if self.models:
                fallback_model = next(iter(self.models.values()))["client"]
                logger.info(f"Using fallback model due to error")
                return fallback_model
            else:
                raise ValueError(f"No models available and failed to create {provider}/{model_name}: {str(e)}")

# Create a singleton instance
model_selector = ModelSelector()

# Register available models (this would typically be done at startup)
def initialize_models():
    """Initialize and register available models."""
    # Register Qwen3 via OpenRouter as the main 'qwen' model
    try:
        qwen3_openrouter = OpenRouterClient(model="qwen/qwen3-235b-a22b:free")
        model_selector.register_model("qwen", qwen3_openrouter, ["code", "reasoning", "creativity", "factual"])
    except Exception as e:
        logger.warning(f"Could not initialize Qwen3 OpenRouterClient: {str(e)}")

    # (Optional) Remove or comment out local QwenClient registration if you want only OpenRouter
    # try:
    #     qwen = QwenClient()
    #     model_selector.register_model("qwen_local", qwen, ["code", "reasoning", "creativity", "factual"])
    # except Exception as e:
    #     logger.warning(f"Could not initialize Qwen client: {str(e)}")

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

def get_model_client(provider: str, model_name: str, **parameters) -> BaseLLMClient:
    """
    Get a model client by provider and model name.
    This is a convenience function that uses the singleton model_selector.
    
    Args:
        provider: The provider name (e.g., "openrouter", "ollama", "llamacpp")
        model_name: The specific model name
        **parameters: Additional parameters for model configuration
        
    Returns:
        The model client instance
    """
    return model_selector.get_model(provider, model_name, **parameters)