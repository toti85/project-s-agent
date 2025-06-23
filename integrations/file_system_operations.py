"""
File System Operations for Project-S
-----------------------------------
Ez a modul a fájlrendszer műveletek végrehajtásáért felelős komponenseket tartalmazza.
A Project-S rendszer számára biztonságos fájl olvasási, írási és listázási műveleteket biztosít.
"""
import os
import logging
import asyncio
import json
import aiofiles
import aiofiles.os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import platform
import stat
import shutil

from langgraph.prebuilt import ToolNode
from integrations.tool_manager import tool_manager
from integrations.system_operations import (
    security_check, is_path_allowed, SystemOperationState,
    DEFAULT_ENCODING, MAX_FILE_SIZE
)
from core.event_bus import event_bus
from core.error_handler import error_handler

logger = logging.getLogger(__name__)


class FileSystemOperations:
    """
    Fájlrendszer műveletek osztálya, amely biztonságos hozzáférést biztosít
    a fájlrendszerhez a Project-S rendszer számára.
    """
    
    def __init__(self):
        """Inicializálja a FileSystemOperations osztályt"""
        self.allowed_operations = {
            "read": True,
            "write": True,
            "list": True,
            "delete": False,  # Alapértelmezetten a törlés tiltott
        }
        
        # Az aktuális munkamappa beállítása
        self.workspace_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        
    @tool_manager.register(
        metadata={
            "name": "read_file",
            "description": "Fájl tartalmának biztonságos olvasása",
            "category": "filesystem",
            "tags": ["file", "read", "io"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def read_file(self, file_path: str, encoding: str = DEFAULT_ENCODING) -> Dict[str, Any]:
        """
        Biztonságosan beolvassa egy fájl tartalmát.
        
        Args:
            file_path: A beolvasandó fájl útvonala
            encoding: A fájl karakterkódolása (alapértelmezett: utf-8)
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a fájl tartalmát vagy a hibaüzenetet
        """
        try:
            file_path = os.path.abspath(file_path)
            
            # Ellenőrizzük, hogy a fájl létezik-e
            if not os.path.isfile(file_path):
                error_msg = f"A fájl nem létezik: {file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Ellenőrizzük a fájl méretét
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                error_msg = f"A fájl mérete túl nagy ({file_size} byte): {file_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Aszinkron beolvasás
            async with aiofiles.open(file_path, 'r', encoding=encoding) as file:
                content = await file.read()
            
            # Metaadatok gyűjtése
            stats = os.stat(file_path)
            metadata = {
                "size": stats.st_size,
                "modified": stats.st_mtime,
                "created": stats.st_ctime,
                "path": file_path,
                "encoding": encoding
            }
            
            # Esemény kibocsátása
            event_bus.emit("file.read", {
                "path": file_path,
                "size": stats.st_size,
                "success": True
            })
            
            return {
                "success": True,
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = f"Hiba a fájl olvasása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("file.error", {
                "operation": "read",
                "path": file_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg
            }
            
    @tool_manager.register(
        metadata={
            "name": "write_file",
            "description": "Tartalom biztonságos írása fájlba",
            "category": "filesystem",
            "tags": ["file", "write", "io"],
            "is_dangerous": True,  # Írás veszélyes művelet lehet
        }
    )
    @security_check
    async def write_file(self, file_path: str, content: str, 
                       encoding: str = DEFAULT_ENCODING, 
                       append: bool = False) -> Dict[str, Any]:
        """
        Biztonságosan ír tartalmat egy fájlba.
        
        Args:
            file_path: A fájl útvonala, ahova írni szeretnénk
            content: A fájlba írandó tartalom
            encoding: A fájl karakterkódolása (alapértelmezett: utf-8)
            append: Ha True, akkor hozzáfűzés módban nyitja meg a fájlt
            
        Returns:
            Dict: A művelet eredménye, sikeres volt-e az írás
        """
        try:
            file_path = os.path.abspath(file_path)
            
            # Ellenőrizzük, hogy a tartalom nem túl nagy-e
            content_size = len(content.encode(encoding))
            if content_size > MAX_FILE_SIZE:
                error_msg = f"A tartalom mérete túl nagy ({content_size} byte)"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Ellenőrizzük a könyvtár jogosultságait
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Fájl írása
            mode = 'a' if append else 'w'
            async with aiofiles.open(file_path, mode, encoding=encoding) as file:
                await file.write(content)
            
            # Metaadatok gyűjtése
            stats = os.stat(file_path)
            metadata = {
                "size": stats.st_size,
                "modified": stats.st_mtime,
                "created": stats.st_ctime,
                "path": file_path
            }
            
            # Esemény kibocsátása
            event_bus.emit("file.write", {
                "path": file_path,
                "size": stats.st_size,
                "append": append,
                "success": True
            })
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = f"Hiba a fájl írása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("file.error", {
                "operation": "write",
                "path": file_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg
            }
    
    @tool_manager.register(
        metadata={
            "name": "list_directory",
            "description": "Könyvtár tartalmának biztonságos listázása",
            "category": "filesystem",
            "tags": ["file", "directory", "list"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def list_directory(self, directory_path: str, 
                          recursive: bool = False, 
                          include_hidden: bool = False) -> Dict[str, Any]:
        """
        Biztonságosan listázza egy könyvtár tartalmát.
        
        Args:
            directory_path: A listázandó könyvtár útvonala
            recursive: Ha True, akkor rekurzívan listázza az alkönyvtárakat is
            include_hidden: Ha True, akkor a rejtett fájlokat is listázza
            
        Returns:
            Dict: A művelet eredménye, tartalmazza a fájlok és könyvtárak listáját
        """
        try:
            directory_path = os.path.abspath(directory_path)
            
            # Ellenőrizzük, hogy a könyvtár létezik-e
            if not os.path.isdir(directory_path):
                error_msg = f"A könyvtár nem létezik: {directory_path}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Fájlok és könyvtárak gyűjtése
            files = []
            directories = []
            
            # Rekurzív vagy nem rekurzív listázás
            if recursive:
                for root, dirs, filenames in os.walk(directory_path):
                    # Rejtett elemek szűrése
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        filenames = [f for f in filenames if not f.startswith('.')]
                    
                    # Relatív útvonalak számítása a kezdő könyvtárhoz képest
                    rel_path = os.path.relpath(root, directory_path)
                    if rel_path == '.':
                        rel_path = ''
                    
                    # Könyvtárak feldolgozása
                    for dir_name in dirs:
                        full_path = os.path.join(root, dir_name)
                        rel_dir_path = os.path.join(rel_path, dir_name)
                        
                        try:
                            stats = os.stat(full_path)
                            directories.append({
                                "name": dir_name,
                                "path": rel_dir_path,
                                "full_path": full_path,
                                "modified": stats.st_mtime,
                                "created": stats.st_ctime,
                                "type": "directory"
                            })
                        except OSError:
                            # Ha nem tudjuk elérni a statisztikákat, akkor kihagyjuk
                            pass
                    
                    # Fájlok feldolgozása
                    for file_name in filenames:
                        full_path = os.path.join(root, file_name)
                        rel_file_path = os.path.join(rel_path, file_name)
                        
                        try:
                            stats = os.stat(full_path)
                            files.append({
                                "name": file_name,
                                "path": rel_file_path,
                                "full_path": full_path,
                                "size": stats.st_size,
                                "modified": stats.st_mtime,
                                "created": stats.st_ctime,
                                "type": "file",
                                "extension": os.path.splitext(file_name)[1]
                            })
                        except OSError:
                            # Ha nem tudjuk elérni a statisztikákat, akkor kihagyjuk
                            pass
            else:
                # Nem rekurzív listázás - csak a megadott könyvtárat nézzük
                with os.scandir(directory_path) as entries:
                    for entry in entries:
                        # Rejtett elemek szűrése
                        if not include_hidden and entry.name.startswith('.'):
                            continue
                            
                        try:
                            stats = entry.stat()
                            item = {
                                "name": entry.name,
                                "path": entry.name,
                                "full_path": entry.path,
                                "modified": stats.st_mtime,
                                "created": stats.st_ctime
                            }
                            
                            if entry.is_file():
                                item.update({
                                    "size": stats.st_size,
                                    "type": "file",
                                    "extension": os.path.splitext(entry.name)[1]
                                })
                                files.append(item)
                            elif entry.is_dir():
                                item.update({
                                    "type": "directory"
                                })
                                directories.append(item)
                        except OSError:
                            # Ha nem tudjuk elérni a statisztikákat, akkor kihagyjuk
                            pass
            
            # Összesített eredmény
            result = {
                "success": True,
                "directory": directory_path,
                "files": files,
                "directories": directories,
                "total_files": len(files),
                "total_directories": len(directories)
            }
            
            # Esemény kibocsátása
            event_bus.emit("file.list", {
                "path": directory_path,
                "recursive": recursive,
                "file_count": len(files),
                "dir_count": len(directories)
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Hiba a könyvtár listázása közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            # Hibaesemény kibocsátása
            event_bus.emit("file.error", {
                "operation": "list",
                "path": directory_path,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": error_msg
            }
            
    @tool_manager.register(
        metadata={
            "name": "file_exists",
            "description": "Ellenőrzi, hogy egy fájl létezik-e",
            "category": "filesystem",
            "tags": ["file", "check", "exists"],
            "is_dangerous": False,
        }
    )
    @security_check
    async def file_exists(self, file_path: str) -> Dict[str, Any]:
        """
        Ellenőrzi, hogy egy fájl létezik-e.
        
        Args:
            file_path: Az ellenőrizendő fájl útvonala
            
        Returns:
            Dict: A művelet eredménye, tartalmazza, hogy a fájl létezik-e
        """
        try:
            file_path = os.path.abspath(file_path)
            exists = os.path.exists(file_path)
            is_file = os.path.isfile(file_path)
            
            result = {
                "success": True,
                "exists": exists,
                "is_file": is_file,
                "is_directory": os.path.isdir(file_path) if exists else False,
                "path": file_path
            }
            
            # Ha a fájl létezik, adjunk hozzá metaadatokat
            if exists and is_file:
                stats = os.stat(file_path)
                result.update({
                    "size": stats.st_size,
                    "modified": stats.st_mtime,
                    "created": stats.st_ctime,
                    "extension": os.path.splitext(file_path)[1]
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Hiba a fájl létezésének ellenőrzése közben: {str(e)}"
            logger.error(error_msg)
            error_handler.log_exception(e)
            
            return {
                "success": False,
                "error": error_msg
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
        Létrehozza és regisztrálja az összes fájlrendszer műveletet LangGraph eszközként.
        
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
file_system_operations = FileSystemOperations()
