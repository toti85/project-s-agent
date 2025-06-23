"""
Multi-layered LLM Integration for Project-S
------------------------------------------
This module enables using different LLM models for specific cognitive tasks,
providing a more specialized and efficient approach to AI processing.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Tuple, Union
import os
import json

from core.error_handler import error_handler
from llm_clients.model_selector import ModelSelector
from llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class MultiModelManager:
    """
    Manages multiple LLM models for different types of cognitive tasks.
    
    This class allows Project-S to use specialized models for different
    cognitive functions, such as:
    - Planning models for breaking down complex tasks
    - Reasoning models for analytical tasks
    - Creative models for content generation
    - Code-specific models for programming tasks
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the multi-model manager with optional configuration.
        
        Args:
            config_path (str, optional): Path to a JSON configuration file
                defining which models to use for which tasks
        """
        self.model_selector = ModelSelector()
        self.models: Dict[str, BaseLLMClient] = {}
        self.task_model_mapping: Dict[str, str] = {}
        self.default_model = "qwen"  # Default model identifier
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        else:
            # Set up default mappings
            self._setup_default_mappings()
            
        logger.info(f"MultiModelManager initialized with {len(self.models)} models")
    
    def _load_config(self, config_path: str) -> None:
        """
        Load model configuration from a JSON file.
        
        Args:
            config_path (str): Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load models section
            models_config = config.get("models", {})
            for model_id, model_config in models_config.items():
                provider = model_config.get("provider", "openrouter")
                model_name = model_config.get("model_name")
                parameters = model_config.get("parameters", {})
                
                try:
                    model = self.model_selector.get_model(
                        provider=provider,
                        model_name=model_name,
                        **parameters
                    )
                    self.models[model_id] = model
                    logger.info(f"Loaded model '{model_id}' ({provider}/{model_name})")
                except Exception as e:
                    logger.error(f"Failed to load model '{model_id}': {str(e)}")
            
            # Load task mappings section
            task_mappings = config.get("task_mappings", {})
            for task_type, model_id in task_mappings.items():
                if model_id in self.models:
                    self.task_model_mapping[task_type] = model_id
                else:
                    logger.warning(f"Task '{task_type}' mapped to unknown model '{model_id}'")
            
            # Set default model
            if "default" in self.task_model_mapping and self.task_model_mapping["default"] in self.models:
                self.default_model = self.task_model_mapping["default"]
                
        except Exception as e:
            logger.error(f"Error loading model configuration: {str(e)}")
            error_context = {"component": "multi_model_manager", "operation": "load_config"}
            asyncio.create_task(error_handler.handle_error(e, error_context))
            
            # Fall back to default mappings
            self._setup_default_mappings()
    
    def _setup_default_mappings(self) -> None:
        """Set up default model mappings when no configuration is provided."""
        try:
            # Initialize default model
            default_model = self.model_selector.get_model(
                provider="ollama",  # Use local Ollama for default
                model_name="qwen:7b"  # Default to Qwen 7B model
            )
            self.models["default"] = default_model
            self.default_model = "default"
            
            # Map all task types to the default model
            task_types = [
                "planning", "reasoning", "creative", "coding", "summarization", 
                "qa", "classification", "extraction"
            ]
            for task_type in task_types:
                self.task_model_mapping[task_type] = "default"
                
            logger.info("Set up default model mappings")
            
        except Exception as e:
            logger.error(f"Error setting up default models: {str(e)}")
            error_context = {"component": "multi_model_manager", "operation": "setup_default"}
            asyncio.create_task(error_handler.handle_error(e, error_context))
    
    def get_model_for_task(self, task_type: str) -> BaseLLMClient:
        """
        Get the appropriate LLM model for a specific task type.
        
        Args:
            task_type (str): The type of task (planning, reasoning, coding, etc.)
            
        Returns:
            BaseLLMClient: The LLM client to use for this task
        """
        # Get the model ID mapped to this task type, or default if not found
        model_id = self.task_model_mapping.get(task_type, self.default_model)
        
        # Get the model instance, or default if not found
        return self.models.get(model_id, self.models.get(self.default_model))
    
    async def execute_task(self, task_type: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the appropriate model.
        
        Args:
            task_type (str): The type of task
            prompt (str): The prompt to send to the model
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            Dict[str, Any]: The model's response
        """
        model = self.get_model_for_task(task_type)
        
        try:
            response = await model.ask(prompt, **kwargs)
            return {
                "status": "success",
                "model_used": model.model_name,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error executing task with model: {str(e)}")
            error_context = {
                "component": "multi_model_manager", 
                "operation": "execute_task", 
                "task_type": task_type
            }
            await error_handler.handle_error(e, error_context)
            
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def add_model(self, model_id: str, provider: str, model_name: str, **params) -> bool:
        """
        Add a new model to the manager.
        
        Args:
            model_id (str): Unique identifier for this model
            provider (str): Provider name (openrouter, ollama, etc.)
            model_name (str): Name of the model
            **params: Additional parameters for the model
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model = self.model_selector.get_model(
                provider=provider,
                model_name=model_name,
                **params
            )
            self.models[model_id] = model
            logger.info(f"Added model '{model_id}' ({provider}/{model_name})")
            return True
        except Exception as e:
            logger.error(f"Failed to add model '{model_id}': {str(e)}")
            return False
    
    def map_task_to_model(self, task_type: str, model_id: str) -> bool:
        """
        Map a task type to a specific model.
        
        Args:
            task_type (str): Type of task
            model_id (str): ID of the model to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        if model_id in self.models:
            self.task_model_mapping[task_type] = model_id
            logger.info(f"Mapped task '{task_type}' to model '{model_id}'")
            return True
        else:
            logger.warning(f"Cannot map task '{task_type}' to unknown model '{model_id}'")
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get information about all available models.
        
        Returns:
            List[Dict[str, Any]]: List of model information
        """
        models_info = []
        for model_id, model in self.models.items():
            models_info.append({
                "id": model_id,
                "provider": model.provider,
                "model_name": model.model_name,
                "capabilities": getattr(model, "capabilities", ["general"]),
                "is_default": model_id == self.default_model
            })
        return models_info
    
    def get_task_mappings(self) -> Dict[str, str]:
        """
        Get all task to model mappings.
        
        Returns:
            Dict[str, str]: Dictionary mapping task types to model IDs
        """
        return self.task_model_mapping.copy()

# Create a singleton instance
multi_model_manager = MultiModelManager()
