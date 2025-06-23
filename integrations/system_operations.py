"""
System Operations Module for Project-S
--------------------------------------
Ez a modul a rendszerszintű műveletek végrehajtásáért felelős komponenseket tartalmazza.
Biztonságos fájlrendszer-kezelést, folyamatkezelést és konfigurációkezelést biztosít
a LangGraph munkafolyamatokhoz integrálva.

Funkciók:
- Fájlrendszerműveletek: olvasás, írás, listázás, törlés
- Folyamatkezelés: indítás, leállítás, monitorozás
- Konfigurációkezelés: beállítások olvasása és írása
- Biztonsági korlátozások és jogosultságkezelés
"""
import logging
import os
import sys
import platform
import subprocess
import json
import yaml
import time
import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypedDict, Tuple
import psutil
from functools import wraps

from core.event_bus import event_bus
from core.error_handler import error_handler
from integrations.tool_manager import tool_manager

logger = logging.getLogger(__name__)

# Alapértelmezett beállítások
DEFAULT_ENCODING = "utf-8"
DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
DEFAULT_TIMEOUT = 30  # másodpercek

# Biztonsági konstansok
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB maximum fájlméret
ALLOWED_CONFIG_EXTENSIONS = [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"]
RESTRICTED_PATHS = [
    "/etc", "/var/log", "/var/run", "/proc", "/sys",  # Linux
    "C:\\Windows", "C:\\Program Files", "C:\\Users\\Default",  # Windows
    "/Library/", "/System/", "/private/"  # macOS
]

class SystemOperationState(TypedDict, total=False):
    """
    TypedDict a rendszerszintű műveletek állapotának tárolására
    LangGraph munkafolyamatokban való használatra tervezve
    """
    # Fájlrendszer műveletek állapota
    last_read_file: str
    last_write_file: str
    file_content: Optional[str]
    file_listing: List[Dict[str, Any]]
    
    # Folyamat kezelés állapota
    running_processes: List[Dict[str, Any]]
    last_started_process: Dict[str, Any]
    process_output: Optional[str]
    
    # Konfiguráció kezelés
    loaded_config: Dict[str, Any]
    config_path: str
    
    # Hibakezelés
    error_state: bool
    error_message: Optional[str]
    error_traceback: Optional[str]
    
    # Biztonsági adatok
    permissions: Dict[str, bool]
    allowed_paths: List[str]
    
    # Metaadatok
    os_info: Dict[str, str]
    timestamp: float


def security_check(func):
    """
    Dekorátor a biztonsági ellenőrzésekhez.
    Ellenőrzi, hogy a műveletek biztonságosak-e.
    
    Args:
        func: Az ellenőrizendő függvény
        
    Returns:
        A dekorált függvény
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Fájlútvonal ellenőrzése
        file_path = kwargs.get('file_path')
        if file_path and not is_path_allowed(file_path):
            error_msg = f"Biztonsági hiba: A megadott útvonal nem engedélyezett: {file_path}"
            logger.error(error_msg)
            event_bus.emit("system.security_violation", {
                "operation": func.__name__,
                "path": file_path,
                "error": error_msg
            })
            return {
                "success": False,
                "error": error_msg,
                "error_type": "SecurityViolation"
            }
        
        # További biztonsági ellenőrzések a speciális műveletekhez
        if func.__name__ == "execute_process":
            command = kwargs.get('command', [])
            if not is_command_allowed(command):
                error_msg = f"Biztonsági hiba: A megadott parancs nem engedélyezett: {command}"
                logger.error(error_msg)
                event_bus.emit("system.security_violation", {
                    "operation": func.__name__,
                    "command": command,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "SecurityViolation"
                }
        
        # Ha minden ellenőrzés átment, folytatjuk a végrehajtást
        return await func(*args, **kwargs)
    return wrapper


def is_path_allowed(path: str) -> bool:
    """
    Ellenőrzi, hogy az adott útvonal engedélyezett-e.
    
    Args:
        path: Az ellenőrizendő fájl vagy mappa útvonal
        
    Returns:
        True, ha az útvonal engedélyezett, egyébként False
    """
    # Normalizáljuk az útvonalat
    norm_path = os.path.abspath(os.path.normpath(path))
    
    # Ellenőrizzük a tiltott útvonalakat
    for restricted in RESTRICTED_PATHS:
        if platform.system() == "Windows":
            # Windows esetén case-insensitive ellenőrzés
            if norm_path.lower().startswith(restricted.lower()):
                return False
        else:
            # Unix-szerű rendszereken case-sensitive ellenőrzés
            if norm_path.startswith(restricted):
                return False
    
    # Ellenőrizzük, hogy a fájl mérete nem nagyobb-e, mint a megengedett
    if os.path.isfile(norm_path) and os.path.getsize(norm_path) > MAX_FILE_SIZE:
        return False
    
    return True


def is_command_allowed(command: Union[str, List[str]]) -> bool:
    """
    Ellenőrzi, hogy a parancs biztonságos-e futtatásra.
    
    Args:
        command: A futtatandó parancs stringként vagy lista formában
        
    Returns:
        True, ha a parancs biztonságos, egyébként False
    """
    # Konvertáljuk a parancsot lista formátumra ha string
    if isinstance(command, str):
        cmd_parts = command.split()
    else:
        cmd_parts = command
    
    # Tiltott parancsok listája
    dangerous_commands = [
        "rm", "rmdir", "del", "format", "mkfs",  # Törlés és formázás
        "chmod", "chown", "icacls", "attrib",    # Jogosultságkezelés
        "sudo", "su", "runas",                   # Jogosultságnövelés
        "wget", "curl", "powershell.exe -e",     # Távoli kódletöltés/futtatás
        ">", ">>", "2>", "&"                     # Átirányítás és láncolás
    ]
    
    # Ellenőrizzük a parancs első részét
    if cmd_parts and cmd_parts[0]:
        base_cmd = cmd_parts[0].lower()
        for dangerous in dangerous_commands:
            if base_cmd.endswith(dangerous) or dangerous in " ".join(cmd_parts).lower():
                return False
    
    return True
