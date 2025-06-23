"""
Project-S Multi-Model AI Client
-------------------------------
This module provides multi-model AI integration for the Project-S system.
Capable of communicating with different AI providers and intelligently selecting
the appropriate model based on task type.
"""

import os
import logging
import asyncio
import yaml
import json
from typing import Dict, Any, List, Optional, Union, Tuple
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelNotAvailableError(Exception):
    """Exception when the requested model is not available."""
    pass

class AIClient:
    """
    Multi-model AI client capable of communicating with different providers.
    Supported providers: OpenAI, Anthropic, Ollama, OpenRouter
    """
    
    def __init__(self):
        """Initialize AI client and configure models."""
        # Load API keys from environment variables OR files
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        
        # Load OpenRouter API key (environment or file)
        openrouter_env = os.environ.get("OPENROUTER_API_KEY", "")
        if openrouter_env:
            self.openrouter_api_key = openrouter_env
        else:
            # Try to load from file
            try:
                from docs.openrouter_api_key import OPENROUTER_API_KEY
                self.openrouter_api_key = OPENROUTER_API_KEY or ""
            except ImportError:
                self.openrouter_api_key = ""
        
        # Load model configurations
        self.config_path = Path(__file__).parent.parent / "config" / "models_config.yaml"
        self.config = self._load_config()
        
        # Check model availability
        self._check_available_models()
        
        # Set timeout (in seconds)
        self.timeout = 60
        
        logger.info("Multi-model AI client initialized")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load model configurations from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Model configurations loaded successfully: {len(config)} providers")
            return config
        except Exception as e:
            logger.error(f"Error loading model configuration: {e}")
            return {}
            
    def _check_available_models(self) -> None:
        """Check provider availability based on API keys."""
        # OpenAI availability
        if not self.openai_api_key:
            if self.config.get("openai", {}).get("enabled", False):
                logger.warning("OpenAI service enabled but no API key found")
                self.config["openai"]["enabled"] = False
        
        # Anthropic availability
        if not self.anthropic_api_key:
            if self.config.get("anthropic", {}).get("enabled", False):
                logger.warning("Anthropic service enabled but no API key found")
                self.config["anthropic"]["enabled"] = False
                
        # OpenRouter availability
        if not self.openrouter_api_key:
            if self.config.get("openrouter", {}).get("enabled", False):
                logger.warning("OpenRouter service enabled but no API key found")
                self.config["openrouter"]["enabled"] = False
        
        # Local Ollama availability check will be added later
        
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models grouped by provider."""
        available_models = []
          # Go through all providers and their models
        for provider, provider_config in self.config.items():
            if provider in ["openai", "anthropic", "ollama", "openrouter"] and provider_config.get("enabled", False):
                for model_id, model_config in provider_config.get("models", {}).items():
                    available_models.append({
                        "provider": provider,
                        "model_id": model_id,
                        "name": model_config.get("display_name", model_id),
                        "display_name": model_config.get("display_name", model_id),
                        "description": model_config.get("description", f"{provider} model: {model_id}"),
                        "strengths": model_config.get("strengths", model_config.get("capabilities", [])),
                        "capabilities": model_config.get("capabilities", []),
                        "max_tokens": model_config.get("max_tokens", 4096)
                    })
        
        return available_models
    
    def get_recommended_model(self, task_type: str = "general") -> Optional[str]:
        """Get recommended model for a specific task type."""
        task_models = self.config.get("task_model_mapping", {}).get(task_type, [])
        
        for model_id in task_models:
            provider = self._get_provider_for_model(model_id)
            if provider and self.config.get(provider, {}).get("enabled", False):
                return model_id
        
        # Fallback to first available model
        available_models = self.list_available_models()
        if available_models:
            return available_models[0]["model_id"]
        
        return None
    
    def _get_provider_for_model(self, model_id: str) -> Optional[str]:
        """Get the provider for a specific model."""
        for provider, provider_config in self.config.items():
            if provider in ["openai", "anthropic", "ollama", "openrouter"]:
                if model_id in provider_config.get("models", {}):
                    return provider
        return None
    
    def _get_model_api_id(self, model_id: str) -> str:
        """Get the actual API model ID to use for API calls."""
        provider = self._get_provider_for_model(model_id)
        if provider and provider in self.config:
            model_config = self.config[provider].get("models", {}).get(model_id, {})
            # Return the model_id field from config if it exists, otherwise use the key
            return model_config.get("model_id", model_id)
        return model_id
      async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        provider: Optional[str] = None,
        system_message: Optional[str] = None,
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate response using the specified or recommended model.
        
        Args:
            prompt: The user prompt
            model: Optional specific model to use
            provider: Optional specific provider to use
            system_message: Optional system message
            task_type: Optional task type for model selection
            temperature: Optional temperature setting for response variability
            max_tokens: Optional maximum tokens for response
            
        Returns:
            Dict: Response and metadata dictionary
        """
        
        # Model selection logic
        if not model:
            model = self.get_recommended_model(task_type)
            if not model:
                logger.error("No available models found")
                return None
        
        selected_model = model
        selected_provider = provider or self._get_provider_for_model(model)
        
        if not selected_provider:
            logger.error(f"Provider not found for model: {model}")
            return None
        
        # Check if provider is enabled
        if not self.config.get(selected_provider, {}).get("enabled", False):
            logger.error(f"Provider {selected_provider} is not enabled")
            return None
          try:
            # Route to appropriate provider
            if selected_provider == "openai":
                return await self._call_openai(selected_model, prompt, system_message, temperature, max_tokens)
            elif selected_provider == "anthropic":
                return await self._call_anthropic(selected_model, prompt, system_message, temperature, max_tokens)
            elif selected_provider == "openrouter":
                return await self._call_openrouter(selected_model, prompt, system_message, temperature, max_tokens)
            elif selected_provider == "ollama":
                return await self._call_ollama(selected_model, prompt, system_message, temperature, max_tokens)
            else:
                logger.error(f"Unsupported provider: {selected_provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response with {selected_provider}: {e}")
            return None
      def _call_openai(self, model: str, prompt: str, system_message: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """Call OpenAI API."""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
      def _call_openrouter(self, model: str, prompt: str, system_message: Optional[str] = None,
                        temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """Call OpenRouter API using OpenAI SDK approach."""
        try:
            import openai
            
            # Use OpenAI SDK with OpenRouter endpoint
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_api_key,
                default_headers={
                    "HTTP-Referer": "https://project-s-agent.local",
                    "X-Title": "Project-S Multi-AI System"
                }
            )
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Get the actual model ID from config
            model_id = self._get_model_api_id(model)
            
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
                timeout=self.timeout
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None
    
    def _call_anthropic(self, model: str, prompt: str, system_message: Optional[str] = None,
                       temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """Call Anthropic API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            response = client.completions.create(
                model=model,
                prompt=full_prompt,
                temperature=temperature,
                max_tokens_to_sample=max_tokens or 4096
            )
            
            return response.completion
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None
    
    def _call_ollama(self, model: str, prompt: str, system_message: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """Call Ollama API."""
        try:
            import requests
            
            url = "http://localhost:11434/api/generate"
            
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            data = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or 4096
                }
            }
            
            response = requests.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
            
            return None
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None
    
    def test_connection(self, provider: str = None) -> Dict[str, Any]:
        """
        Test connection to the specified provider or all providers.
        
        Returns:
            Dict: Test result with success status and message
        """
        results = {}
        
        providers_to_test = [provider] if provider else ["openai", "anthropic", "openrouter", "ollama"]
        
        for prov in providers_to_test:
            if not self.config.get(prov, {}).get("enabled", False):
                results[prov] = {"success": False, "message": "Provider not enabled"}
                continue
            
            # Get first available model for this provider
            provider_models = self.config.get(prov, {}).get("models", {})
            if not provider_models:
                results[prov] = {"success": False, "message": "No models configured"}
                continue
            
            test_model = list(provider_models.keys())[0]
            
            try:
                response = self.generate_response(
                    prompt="Hello, this is a test message. Please respond with 'Connection successful!'",
                    model=test_model,
                    provider=prov,
                    max_tokens=50
                )
                
                if response:
                    results[prov] = {"success": True, "message": f"Connected successfully: {response[:100]}"}
                else:
                    results[prov] = {"success": False, "message": "No response received"}
                    
            except Exception as e:
                results[prov] = {"success": False, "message": f"Connection failed: {str(e)}"}
        
        return results

# Create global instance
multi_model_ai_client = AIClient()
