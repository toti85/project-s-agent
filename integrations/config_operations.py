"""
Configuration Operations for Project-S
------------------------------------
Ez a modul a konfigurációs műveletek végrehajtásáért felelős komponenseket tartalmazza.
Biztonságos konfigurációs fájl kezelést biztosít a LangGraph munkafolyamatokhoz.
"""
import os
import logging
import json
import yaml
import copy
from typing import Dict, List, Any, Optional, Union
import asyncio

from langgraph.prebuilt import ToolNode
from integrations.tool_manager import tool_manager
from integrations.system_operations import (
    security_check, is_path_allowed, SystemOperationState,
    DEFAULT_ENCODING, ALLOWED_CONFIG_EXTENSIONS
)
from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)

# Gyorsítótár a betöltött konfigurációkhoz
config_cache = {}

class ConfigOperations:
    """
    Konfigurációs műveletek osztálya, amely biztonságos konfigurációs
    fájl kezelést biztosít a Project-S rendszer számára.
    """
    
    def __init__(self):
        """Inicializálja a ConfigOperations osztályt"""
        # Az alapértelmezett konfigurációs könyvtár beállítása
        self.config_dir = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "config"
        ))
        
        # Feliratkozás az eseményekre
        event_bus.subscribe("config.changed", self._on_config_changed)
        
    def _on_config_changed(self, event_data):
        """
        Eseménykezelő, amely a konfiguráció változásakor fut le.
        
        Args:
            event_data: Az esemény adatai
        """
        config_path = event_data.get("path")
        if config_path and config_path in config_cache:
            # Töröljük a gyorsítótárból, hogy a következő betöltés friss legyen
            del config_cache[config_path]
            logger.info(f"A konfigurációs gyorsítótár törölve: {config_path}")
    
    @tool_manager.register(
        metadata={
            "name": "load_config",
            "description": "Konfigurációs fájl biztonságos betöltése",
            "category": "config",
            "tags": ["config", "load", "settings"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def load_config(self, config_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Biztonságosan betölt egy konfigurációs fájlt.
        
        Args:
            config_path: A konfigurációs fájl útvonala
            use_cache: Ha True, akkor a gyorsítótárból tölt be, ha rendelkezésre áll
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a konfigurációs adatokat
        """
        try:
            # Útvonal normalizálása
            config_path = os.path.abspath(config_path)
            
            # Ellenőrizzük, hogy a fájl létezik-e
            if not os.path.isfile(config_path):
                error_msg = f"A konfigurációs fájl nem létezik: {config_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Ellenőrizzük a fájl kiterjesztését
            _, ext = os.path.splitext(config_path)
            if ext.lower() not in ALLOWED_CONFIG_EXTENSIONS:
                error_msg = f"Nem támogatott konfigurációs fájl típus: {ext}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Ha a gyorsítótárazás engedélyezett, és a fájl már a gyorsítótárban van
            if use_cache and config_path in config_cache:
                logger.info(f"Konfiguráció betöltése a gyorsítótárból: {config_path}")
                return {
                    "success": True,
                    "config": copy.deepcopy(config_cache[config_path]),
                    "path": config_path,
                    "from_cache": True
                }
                
            # Fájl beolvasása
            with open(config_path, 'r', encoding=DEFAULT_ENCODING) as file:
                content = file.read()
                
                # JSON fájl esetén
                if ext.lower() == '.json':
                    config_data = json.loads(content)
                # YAML fájl esetén
                elif ext.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(content)
                # TOML fájl esetén (ha van toml modul)
                elif ext.lower() == '.toml':
                    try:
                        import toml
                        config_data = toml.loads(content)
                    except ImportError:
                        error_msg = "A TOML fájlok betöltéséhez telepítse a toml csomagot"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}
                # Egyéb konfigurációs fájlok
                else:
                    # Egyszerű kulcs=érték párok betöltése
                    config_data = {}
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                config_data[key.strip()] = value.strip()
            
            # Gyorsítótárazás
            if use_cache:
                config_cache[config_path] = copy.deepcopy(config_data)
            
            # Esemény kibocsátása
            event_bus.emit("config.loaded", {
                "path": config_path,
                "success": True
            })
            
            return {
                "success": True,
                "config": config_data,
                "path": config_path,
                "from_cache": False
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Hibás JSON formátum: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            return {"success": False, "error": error_msg, "error_type": "JSONDecodeError"}
            
        except yaml.YAMLError as e:
            error_msg = f"Hibás YAML formátum: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            return {"success": False, "error": error_msg, "error_type": "YAMLError"}
            
        except Exception as e:
            error_msg = f"Hiba a konfiguráció betöltése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("config.error", {
                "operation": "load",
                "path": config_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "save_config",
            "description": "Konfigurációs adatok biztonságos mentése",
            "category": "config",
            "tags": ["config", "save", "settings"],
            "is_dangerous": True,  # Írás veszélyes művelet
        }
    )
    @security_check
    async def save_config(self, config_path: str, config_data: Dict[str, Any], 
                        format_type: Optional[str] = None,
                        create_backup: bool = True) -> Dict[str, Any]:
        """
        Biztonságosan menti a konfigurációs adatokat egy fájlba.
        
        Args:
            config_path: A konfigurációs fájl útvonala
            config_data: A mentendő konfigurációs adatok
            format_type: A fájl formátuma ('json', 'yaml', vagy None a kiterjesztés alapján)
            create_backup: Ha True, akkor készül egy biztonsági másolat a felülírás előtt
            
        Returns:
            Dict: A művelet eredménye
        """
        try:
            # Útvonal normalizálása
            config_path = os.path.abspath(config_path)
            
            # Könyvtár létrehozása, ha nem létezik
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Formátum meghatározása
            if not format_type:
                _, ext = os.path.splitext(config_path)
                if ext.lower() == '.json':
                    format_type = 'json'
                elif ext.lower() in ['.yaml', '.yml']:
                    format_type = 'yaml'
                elif ext.lower() == '.toml':
                    format_type = 'toml'
                else:
                    format_type = 'text'
            
            # Biztonsági mentés készítése
            if create_backup and os.path.isfile(config_path):
                backup_path = f"{config_path}.bak"
                import shutil
                shutil.copy2(config_path, backup_path)
                logger.info(f"Biztonsági mentés készült: {backup_path}")
            
            # Adatok formázása és mentése
            with open(config_path, 'w', encoding=DEFAULT_ENCODING) as file:
                if format_type == 'json':
                    json.dump(config_data, file, indent=2, ensure_ascii=False)
                elif format_type == 'yaml':
                    yaml.dump(config_data, file, default_flow_style=False, allow_unicode=True)
                elif format_type == 'toml':
                    try:
                        import toml
                        file.write(toml.dumps(config_data))
                    except ImportError:
                        error_msg = "A TOML fájlok mentéséhez telepítse a toml csomagot"
                        logger.error(error_msg)
                        return {"success": False, "error": error_msg}
                else:
                    # Egyszerű kulcs=érték párok mentése
                    for key, value in config_data.items():
                        file.write(f"{key}={value}\n")
            
            # Frissítsük a gyorsítótárat
            config_cache[config_path] = copy.deepcopy(config_data)
            
            # Esemény kibocsátása
            event_bus.emit("config.saved", {
                "path": config_path,
                "format": format_type,
                "success": True
            })
            
            return {
                "success": True,
                "path": config_path,
                "format": format_type,
                "backup_created": create_backup and os.path.isfile(f"{config_path}.bak")
            }
            
        except Exception as e:
            error_msg = f"Hiba a konfiguráció mentése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("config.error", {
                "operation": "save",
                "path": config_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "update_config",
            "description": "Meglévő konfigurációs fájl részleges frissítése",
            "category": "config",
            "tags": ["config", "update", "settings"],
            "is_dangerous": True,  # Írás veszélyes művelet
        }
    )
    @security_check
    async def update_config(self, config_path: str, 
                          updates: Dict[str, Any],
                          create_if_not_exists: bool = True) -> Dict[str, Any]:
        """
        Frissíti egy meglévő konfigurációs fájl részleteit.
        
        Args:
            config_path: A konfigurációs fájl útvonala
            updates: A frissítendő konfigurációs adatok (kulcs-érték párok)
            create_if_not_exists: Ha True, akkor létrehozza a fájlt, ha nem létezik
            
        Returns:
            Dict: A művelet eredménye
        """
        try:
            # Először betöltjük a meglévő konfigurációt
            load_result = await self.load_config(config_path, use_cache=False)
            
            if not load_result["success"]:
                # Ha nem sikerült betölteni és nem akarjuk létrehozni
                if not create_if_not_exists:
                    return load_result
                
                # Létrehozunk egy új konfigurációs fájlt
                logger.info(f"Új konfigurációs fájl létrehozása: {config_path}")
                existing_config = {}
            else:
                # Meglévő konfiguráció
                existing_config = load_result["config"]
            
            # Rekurzív frissítés függvény
            def update_dict(target, source):
                for key, value in source.items():
                    if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                        update_dict(target[key], value)
                    else:
                        target[key] = value
                return target
            
            # Konfiguráció frissítése
            updated_config = update_dict(existing_config, updates)
            
            # Konfiguráció mentése
            _, ext = os.path.splitext(config_path)
            format_type = None
            if ext.lower() == '.json':
                format_type = 'json'
            elif ext.lower() in ['.yaml', '.yml']:
                format_type = 'yaml'
            elif ext.lower() == '.toml':
                format_type = 'toml'
            
            save_result = await self.save_config(config_path, updated_config, format_type)
            
            if save_result["success"]:
                # Esemény kibocsátása
                event_bus.emit("config.changed", {
                    "path": config_path,
                    "updates": list(updates.keys()),
                    "success": True
                })
            
            return {
                "success": save_result["success"],
                "path": config_path,
                "updated_keys": list(updates.keys()),
                "created": not load_result["success"] and create_if_not_exists
            }
            
        except Exception as e:
            error_msg = f"Hiba a konfiguráció frissítése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("config.error", {
                "operation": "update",
                "path": config_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "get_config_value",
            "description": "Egy specifikus érték kinyerése a konfigurációból",
            "category": "config",
            "tags": ["config", "read", "settings"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def get_config_value(self, config_path: str, key_path: str, 
                            default_value: Any = None) -> Dict[str, Any]:
        """
        Kinyeri egy adott kulcs értékét a konfigurációból.
        
        Args:
            config_path: A konfigurációs fájl útvonala
            key_path: A kulcs elérési útja (pl. "app.settings.theme")
            default_value: Az alapértelmezett érték, ha a kulcs nem található
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a kinyert értéket
        """
        try:
            # Először betöltjük a teljes konfigurációt
            load_result = await self.load_config(config_path)
            
            if not load_result["success"]:
                return load_result
            
            # Konfiguráció elérése
            config = load_result["config"]
            
            # Kulcs útvonal feldolgozása
            keys = key_path.split('.')
            current = config
            
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    # Ha nem találjuk a kulcsot, visszaadjuk az alapértelmezett értéket
                    return {
                        "success": True,
                        "value": default_value,
                        "found": False,
                        "key_path": key_path,
                        "config_path": config_path
                    }
            
            return {
                "success": True,
                "value": current,
                "found": True,
                "key_path": key_path,
                "config_path": config_path
            }
            
        except Exception as e:
            error_msg = f"Hiba a konfigurációs érték lekérdezése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    @tool_manager.register(
        metadata={
            "name": "list_config_files",
            "description": "Konfigurációs fájlok listázása egy könyvtárban",
            "category": "config",
            "tags": ["config", "list", "settings"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def list_config_files(self, directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Listázza a konfigurációs fájlokat egy könyvtárban.
        
        Args:
            directory_path: A könyvtár útvonala (alapértelmezett: a config könyvtár)
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a konfigurációs fájlok listáját
        """
        try:
            # Ha nincs megadva könyvtár, használjuk az alapértelmezettet
            if not directory_path:
                directory_path = self.config_dir
                
            directory_path = os.path.abspath(directory_path)
            
            # Ellenőrizzük, hogy a könyvtár létezik-e
            if not os.path.isdir(directory_path):
                error_msg = f"A könyvtár nem létezik: {directory_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Konfigurációs fájlok keresése
            config_files = []
            
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path)
                    
                    if ext.lower() in ALLOWED_CONFIG_EXTENSIONS:
                        # Relatív útvonal számítása
                        rel_path = os.path.relpath(file_path, directory_path)
                        
                        # Fájl meta adatok
                        stats = os.stat(file_path)
                        
                        config_files.append({
                            "name": file,
                            "path": file_path,
                            "relative_path": rel_path,
                            "type": ext.lower()[1:],  # A kezdő . nélkül
                            "size": stats.st_size,
                            "modified": stats.st_mtime
                        })
            
            return {
                "success": True,
                "directory": directory_path,
                "config_files": config_files,
                "count": len(config_files)
            }
            
        except Exception as e:
            error_msg = f"Hiba a konfigurációs fájlok listázása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
            
    def convert_to_tool_node(self, tool_name: str) -> ToolNode:
        """
        Konvertálja a metódust LangGraph ToolNode-dá.
        
        Args:
            tool_name: Az eszköz neve (metódus név)
            
        Returns:
            ToolNode: A létrehozott LangGraph ToolNode
        """
        # Ellenőrizzük, hogy a metódus létezik és regisztrálva van
        if not hasattr(self, tool_name) or not callable(getattr(self, tool_name)):
            raise ValueError(f"A(z) {tool_name} eszköz nem létezik")
        
        # Létrehozzuk a ToolNode-ot
        return tool_manager.create_tool_node(tool_name)
        
    def register_langgraph_tools(self) -> Dict[str, ToolNode]:
        """
        Létrehozza és regisztrálja az összes konfigurációs műveletet LangGraph eszközként.
        
        Returns:
            Dict[str, ToolNode]: Az eszköznevek és ToolNode-ok szótára
        """
        tool_nodes = {}
        
        # Az osztály nyilvános metódusait regisztráljuk
        for method_name in dir(self):
            if not method_name.startswith('_'):
                method = getattr(self, method_name)
                if callable(method) and hasattr(method, '__wrapped__'):
                    try:
                        tool_nodes[method_name] = self.convert_to_tool_node(method_name)
                    except ValueError:
                        # Ha nem sikerül konvertálni, akkor kihagyjuk
                        pass
        
        return tool_nodes


# Singleton példány létrehozása
config_operations = ConfigOperations()
