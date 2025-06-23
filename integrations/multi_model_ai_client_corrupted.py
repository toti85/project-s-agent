"""
Project-S Többmodelles AI Kliens
-------------------------------
Ez a modul biztosítja a többmodelles AI integrációt a Project-S rendszer számára.
Képes különböző AI szolgáltatókkal kommunikálni és intelligensen kiválasztani
a megfelelő modellt a feladat típusa alapján.
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
    """Kivétel, amikor a kért modell nem érhető el."""
    pass

class AIClient:
    """
    class AIClient:
    """
    Többmodelles AI kliens, amely képes különböző szolgáltatókkal kommunikálni.
    Támogatott szolgáltatók: OpenAI, Anthropic, Ollama, OpenRouter
    """
    
    def __init__(self):
        """AI kliens inicializálása és modellek konfigurálása."""
        # API kulcsok betöltése környezeti változókból VAGY fájlokból
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        
        # OpenRouter API kulcs betöltése (environment vagy fájl)
        openrouter_env = os.environ.get("OPENROUTER_API_KEY", "")
        if openrouter_env:
            self.openrouter_api_key = openrouter_env
        else:
            # Próbáljuk betölteni a fájlból
            try:
                from docs.openrouter_api_key import OPENROUTER_API_KEY
                self.openrouter_api_key = OPENROUTER_API_KEY or ""
            except ImportError:
                self.openrouter_api_key = ""
        
        # Modell konfigurációk betöltése
        self.config_path = Path(__file__).parent.parent / "config" / "models_config.yaml"
        self.config = self._load_config()
        
        # Modell hozzáférhetőség ellenőrzése
        self._check_available_models()
        
        # Timeout beállítása (másodpercben)
        self.timeout = 60
        
        logger.info("Többmodelles AI kliens inicializálva")
        
    def _load_config(self) -> Dict[str, Any]:
        """Betölti a modell konfigurációkat a YAML fájlból."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Modell konfigurációk sikeresen betöltve: {len(config)} szolgáltató")
            return config
        except Exception as e:
            logger.error(f"Hiba a modell konfiguráció betöltése közben: {e}")
            return {}
            
    def _check_available_models(self) -> None:
        """Ellenőrzi a szolgáltatók hozzáférhetőségét API kulcsok alapján."""
        # OpenAI elérhetőség
        if not self.openai_api_key:
            if self.config.get("openai", {}).get("enabled", False):
                logger.warning("OpenAI szolgáltatás engedélyezve, de nincs API kulcs")
                self.config["openai"]["enabled"] = False
        
        # Anthropic elérhetőség
        if not self.anthropic_api_key:
            if self.config.get("anthropic", {}).get("enabled", False):
                logger.warning("Anthropic szolgáltatás engedélyezve, de nincs API kulcs")
                self.config["anthropic"]["enabled"] = False
                
        # OpenRouter elérhetőség
        if not self.openrouter_api_key:
            if self.config.get("openrouter", {}).get("enabled", False):
                logger.warning("OpenRouter szolgáltatás engedélyezve, de nincs API kulcs")
                self.config["openrouter"]["enabled"] = False
        
        # Lokális Ollama elérhetőség ellenőrzése majd lesz
        
    def list_available_models(self) -> List[Dict[str, Any]]:
        """Listázza az összes elérhető modellt szolgáltató szerinti csoportosításban."""
        available_models = []
        
        # Végigmegy az összes szolgáltatón és modelljein
        for provider, provider_config in self.config.items():
            if provider in ["openai", "anthropic", "ollama", "openrouter"] and provider_config.get("enabled", False):
                for model_id, model_config in provider_config.get("models", {}).items():
                    available_models.append({
                        "provider": provider,
                        "model_id": model_id,
                        "name": model_config.get("name", model_id),
                        "description": model_config.get("description", ""),
                        "strengths": model_config.get("strengths", []),
                        "cost_tier": model_config.get("cost_tier", "unknown")
                    })
        
        return available_models
    
    def suggest_model_for_task(self, task_type: str) -> str:
        """
        Javasol egy modellt a megadott feladat típus alapján.
        
        Args:
            task_type: A feladat típusa (pl. "kódolás", "tervezés", stb.)
            
        Returns:
            str: A javasolt modell azonosítója
        """
        # Ellenőrizzük, hogy létezik-e a feladat típushoz modell javaslat
        task_models = self.config.get("task_model_mapping", {}).get(task_type, [])
        
        if not task_models:
            logger.info(f"Nincs specifikus modell javaslat a '{task_type}' feladathoz, alapértelmezett használata")
            return self.config.get("default_model", "gpt-3.5-turbo")
            
        # Végigmegyünk a javasolt modelleken és ellenőrizzük az elérhetőségüket
        for model_id in task_models:
            # Meghatározzuk a modell szolgáltatóját
            provider = self._get_provider_for_model(model_id)
            
            # Ellenőrizzük, hogy a szolgáltató engedélyezve van-e
            if provider and self.config.get(provider, {}).get("enabled", False):
                logger.info(f"A '{task_type}' feladathoz a '{model_id}' modell javasolt")
                return model_id
                
        # Ha egyik javasolt modell sem elérhető, használjuk az alapértelmezettet
        logger.info(f"Egyik javasolt modell sem elérhető a '{task_type}' feladathoz, alapértelmezett használata")
        return self.config.get("default_model", "gpt-3.5-turbo")
    
    def _get_provider_for_model(self, model_id: str) -> Optional[str]:
        """Meghatározza egy modell azonosító alapján a szolgáltatót."""
        for provider in ["openai", "anthropic", "ollama", "openrouter"]:
            if model_id in self.config.get(provider, {}).get("models", {}):
                return provider
        return None
    
    async def generate_response(self, 
                               prompt: str, 
                               system_message: Optional[str] = None,
                               model: Optional[str] = None,
                               task_type: Optional[str] = None,
                               temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Válasz generálása az AI modell segítségével.
        
        Args:
            prompt: A felhasználói üzenet
            system_message: Opcionális rendszerüzenet
            model: Opcionális modell azonosító. Ha nincs megadva, akkor kiválasztásra kerül
            task_type: Opcionális feladat típus, ami alapján kiválasztható a modell
            temperature: Opcionális hőmérséklet beállítás a válasz változatosságához
            
        Returns:
            Dict: A válasz és metaadatok szótára
        """
        # Modell kiválasztása
        selected_model = model
        selected_provider = None
        
        if not selected_model and task_type:
            # Ha nincs megadva modell, de van feladat típus, akkor ajánlunk egyet
            selected_model = self.suggest_model_for_task(task_type)
        elif not selected_model:
            # Ha nincs megadva se modell, se feladat típus, akkor az alapértelmezettet használjuk
            selected_model = self.config.get("default_model", "gpt-3.5-turbo")
        
        # Meghatározzuk a kiválasztott modell szolgáltatóját
        selected_provider = self._get_provider_for_model(selected_model)
        
        if not selected_provider:
            raise ModelNotAvailableError(f"A(z) '{selected_model}' modell nem ismert vagy nem elérhető")
        
        if not self.config.get(selected_provider, {}).get("enabled", False):
            raise ModelNotAvailableError(f"A(z) '{selected_provider}' szolgáltató nincs engedélyezve")
        
        # Hőmérséklet beállítása
        if temperature is None:
            temperature = self.config.get(selected_provider, {}).get("models", {}).get(selected_model, {}).get("default_temperature", 0.7)
        
        # Megfelelő szolgáltató API hívás
        if selected_provider == "openai":
            result = await self._generate_with_openai(prompt, system_message, selected_model, temperature)
        elif selected_provider == "anthropic":
            result = await self._generate_with_anthropic(prompt, system_message, selected_model, temperature)
        elif selected_provider == "ollama":
            result = await self._generate_with_ollama(prompt, system_message, selected_model, temperature)
        elif selected_provider == "openrouter":
            result = await self._generate_with_openrouter(prompt, system_message, selected_model, temperature)
        else:
            raise ValueError(f"Ismeretlen szolgáltató: {selected_provider}")
        
        # Metaadatok hozzáadása a válaszhoz
        return {
            "content": result,
            "model": selected_model,
            "provider": selected_provider,
            "task_type": task_type
        }
    
    async def _generate_with_openai(self, 
                                   prompt: str, 
                                   system_message: Optional[str] = None, 
                                   model: str = "gpt-3.5-turbo", 
                                   temperature: float = 0.7) -> str:
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
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000
            }
            
            # Fejlécek
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            logger.info(f"OpenAI API hívás: {model}")
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
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

    async def _generate_with_anthropic(self, 
                                      prompt: str, 
                                      system_message: Optional[str] = None, 
                                      model: str = "claude-3-sonnet", 
                                      temperature: float = 0.5) -> str:
        """Anthropic API használata a válasz generáláshoz."""
        try:
            # API kérés adatok
            data = {
                "model": model,
                "max_tokens": 2000,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Ha van rendszerüzenet, hozzáadjuk
            if system_message:
                data["system"] = system_message
            
            # Fejlécek
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01"
            }
            
            logger.info(f"Anthropic API hívás: {model}")
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "content" in response_data:
                        # Végigmegyünk a tartalom részeken
                        text_parts = []
                        for content in response_data["content"]:
                            if content["type"] == "text":
                                text_parts.append(content["text"])
                        
                        return "".join(text_parts).strip()
                    else:
                        return "Hiba: Nincs válasz az API-tól."
                else:
                    logger.error(f"Anthropic API hiba: {response.status_code} - {response.text}")
                    return f"API hiba történt: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Hiba a válasz generálása közben (Anthropic): {e}")
            return f"Hiba történt: {str(e)}"

    async def _generate_with_ollama(self, 
                                   prompt: str, 
                                   system_message: Optional[str] = None, 
                                   model: str = "llama3", 
                                   temperature: float = 0.7) -> str:
        """Ollama használata a válasz generáláshoz."""
        try:
            # Ellenőrizzük a végpont elérhetőségét
            endpoint = self.config.get("ollama", {}).get("endpoint", "http://localhost:11434/api")
            
            # API kérés adatok
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 1024  # Mennyit jósoljon előre
                }
            }
            
            # Ha van rendszerüzenet, hozzáadjuk
            if system_message:
                data["system"] = system_message
            
            logger.info(f"Ollama API hívás: {model}")
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{endpoint}/generate",
                    json=data
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    if "response" in response_data:
                        return response_data["response"].strip()
                    else:
                        return "Hiba: Nincs válasz az Ollama API-tól."
                else:
                    logger.error(f"Ollama API hiba: {response.status_code} - {response.text}")
                    return f"Ollama API hiba történt: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Hiba a válasz generálása közben (Ollama): {e}")
            return f"Hiba történt: {str(e)}"

    async def _generate_with_openrouter(self, 
                                       prompt: str, 
                                       system_message: Optional[str] = None, 
                                       model: str = "qwen", 
                                       temperature: float = 0.7) -> str:
        """OpenRouter API használata a válasz generáláshoz."""
        try:
            messages = []
            
            # Rendszerüzenet hozzáadása, ha van
            if system_message:
                messages.append({"role": "system", "content": system_message})
                
            # Felhasználói üzenet hozzáadása
            messages.append({"role": "user", "content": prompt})
            
            # API kérés adatok - megfelelő modell azonosító
            model_id = model
            if model == "qwen":
                model_id = "qwen/qwen3-72b-instruct"
            elif model == "yi":
                model_id = "01-ai/yi-34b"
                
            data = {
                "model": model_id,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000
            }
            
            # Fejlécek
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "HTTP-Referer": "https://project-s-agent.example.com",  # Referer
                "X-Title": "Project-S Agent"
            }
            
            logger.info(f"OpenRouter API hívás: {model_id}")
            
            # API kérés küldése
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
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
    
    async def test_model_connection(self, model_id: str) -> Dict[str, Any]:
        """
        Teszteli a modell kapcsolatot egy egyszerű üzenettel.
        
        Args:
            model_id: A tesztelendő modell azonosítója
            
        Returns:
            Dict: A teszt eredménye sikerességgel és üzenettel
        """
        try:
            provider = self._get_provider_for_model(model_id)
            if not provider:
                return {
                    "success": False,
                    "message": f"A(z) '{model_id}' modell nem ismert vagy nem elérhető"
                }
                
            # Egyszerű teszt üzenet
            test_result = await self.generate_response(
                prompt="Kérlek válaszolj egyszerűen: 'A modell kapcsolat működik!'",
                model=model_id
            )
            
            return {
                "success": True,
                "message": "Kapcsolat sikeresen tesztelve",
                "response": test_result
            }
            
        except Exception as e:
            logger.error(f"Hiba a modell kapcsolat tesztelése közben ({model_id}): {e}")
            return {
                "success": False,
                "message": f"Hiba történt: {str(e)}"
            }

# Singleton példány létrehozása
multi_model_ai_client = AIClient()
