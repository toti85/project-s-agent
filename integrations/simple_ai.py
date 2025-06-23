"""
Project-S Egyszerű AI Integráció
-------------------------------
Ez a fájl egy minimális AI integrációt biztosít a Project-S rendszerhez.
Az API kulcsot környezeti változóban kell megadni.
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class SimpleAIClient:
    """
    Egyszerű AI integrációs kliens, ami API hívásokkal kommunikál
    a modelszolgáltatással. OpenAI és OpenRouter is támogatott.
    """
    
    def __init__(self):
        """AI kliens inicializálása."""
        # Alap konfiguráció
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
        
        # OpenAI alapértelmezett beállítások
        self.openai_model = "gpt-3.5-turbo"
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        
        # OpenRouter alapértelmezett beállítások
        self.openrouter_model = "gpt-3.5-turbo"  # Vagy "qwen/qwen3-72b-instruct"
        self.openrouter_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        
        # Timeout másodpercben
        self.timeout = 30
        
        # Ellenőrizzük, hogy van-e API kulcs
        if not self.openai_api_key and not self.openrouter_api_key:
            logger.warning("Nincs beállítva sem OpenAI, sem OpenRouter API kulcs!")
            logger.warning("Állítsd be az OPENAI_API_KEY vagy OPENROUTER_API_KEY környezeti változót.")
        else:
            logger.info("AI kliens inicializálva.")
            if self.openai_api_key:
                logger.info("OpenAI API kulcs konfigurálva.")
            if self.openrouter_api_key:
                logger.info("OpenRouter API kulcs konfigurálva.")
    
    async def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        AI válasz generálása a megadott prompt alapján.
        
        Args:
            prompt: A felhasználói üzenet
            system_message: Opcionális rendszerüzenet
            
        Returns:
            str: A generált válasz szövege
        """
        # Ha van OpenRouter API kulcs, azt használjuk előnyben
        if self.openrouter_api_key:
            return await self._generate_with_openrouter(prompt, system_message)
        # Különben, ha van OpenAI API kulcs, azt használjuk
        elif self.openai_api_key:
            return await self._generate_with_openai(prompt, system_message)
        else:
            return "Nincs konfigurálva API kulcs. Állítsd be az OPENAI_API_KEY vagy OPENROUTER_API_KEY környezeti változót."
    
    async def _generate_with_openai(self, prompt: str, system_message: Optional[str] = None) -> str:
        """OpenAI API használata a válasz generáláshoz."""
        try:
            messages = []
            
            # Rendszerüzenet hozzáadása, ha van
            if system_message:
                messages.append({"role": "system", "content": system_message})
                
            # Felhasználói üzenet hozzáadása
            messages.append({"role": "user", "content": prompt})
            
            # API kérés adatok
            data = {
                "model": self.openai_model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Fejlécek
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.openai_endpoint,
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        return response_data["choices"][0]["message"]["content"].strip()
                    else:
                        return "Hiba: Nincs válasz az API-tól."
                else:
                    logger.error(f"OpenAI API hiba: {response.status_code} - {response.text}")
                    return f"API hiba történt: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Hiba a válasz generálása közben (OpenAI): {e}")
            return f"Hiba történt: {str(e)}"
    
    async def _generate_with_openrouter(self, prompt: str, system_message: Optional[str] = None) -> str:
        """OpenRouter API használata a válasz generáláshoz."""
        try:
            messages = []
            
            # Rendszerüzenet hozzáadása, ha van
            if system_message:
                messages.append({"role": "system", "content": system_message})
                
            # Felhasználói üzenet hozzáadása
            messages.append({"role": "user", "content": prompt})
            
            # API kérés adatok
            data = {
                "model": self.openrouter_model,  # pl. "qwen/qwen3-72b-instruct"
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            # Fejlécek
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "HTTP-Referer": "https://project-s-agent.example.com",  # Dummy referer
                "X-Title": "Project-S Agent"
            }
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.openrouter_endpoint,
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        return response_data["choices"][0]["message"]["content"].strip()
                    else:
                        return "Hiba: Nincs válasz az API-tól."
                else:
                    logger.error(f"OpenRouter API hiba: {response.status_code} - {response.text}")
                    return f"API hiba történt: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Hiba a válasz generálása közben (OpenRouter): {e}")
            return f"Hiba történt: {str(e)}"

# Singleton példány létrehozása
ai_client = SimpleAIClient()
