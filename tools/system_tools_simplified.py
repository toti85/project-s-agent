#!/usr/bin/env python3
"""
Project-S System Tools (Simplified)
-----------------------------------
Egyszerűsített rendszerparancs végrehajtás timeout problémák javításával.
"""

import os
import asyncio
import logging
import subprocess
import shlex
import platform
import psutil
import tempfile
import json
import re
import pathlib
import time
from typing import Dict, Any, List, Optional, Union, Set
from pathlib import Path

from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class CommandValidator:
    """Rendszerparancs validátor és korlátozó segédosztály."""
    
    # Tiltott parancsok és parancsrészek
    FORBIDDEN_COMMANDS = {
        "rm", "format", "mkfs", "fdisk", "wget", "curl", 
        "chmod", "chown", "sudo", "su", "passwd", "dd", 
        "rundll32", "regedit", "reg", "shutdown", 
        "restart", "halt", "rmdir", "rd", "deltree", "taskkill"
    }
    
    # Veszélyes paraméterek és kapcsolók
    DANGEROUS_PARAMS = {
        "-rf", "/s", "/q", "/f", "--force", "--recursive", 
        "--delete", "--purge", "--no-preserve-root", "/c", "/k"
    }
    
    # Engedélyezett parancsok fehérlistája
    ALLOWED_COMMANDS = {
        "ls", "dir", "cd", "pwd", "echo", "cat", "type",
        "find", "mkdir", "md", "ping", "ipconfig", "ifconfig",
        "systeminfo", "ver", "uname", "ps", "tasklist", 
        "free", "df", "du", "date", "time", "whoami",
        "hostname", "python", "pip", "winget", "choco", "chocolatey", 
        "scoop", "powershell", "pwsh", "cmd", "wmic", "sfc", "dism",
        "get-windowsupdate", "install-windowsupdate", "update-module",
        "git", "npm", "node", "dotnet", "java", "mvn", "gradle",
        "grep", "findstr", "apt", "yum", "dnf", "pacman",
        "which", "where", "head", "tail", "more", "less",
        "cp", "copy", "mv", "move", "touch", "chmod", "attrib",
        "del", "cleanmgr", "auto_detect", "request_parser", "content_analyzer",
        "web_scraper", "request_analyzer", "to_be_determined", "cleanup",
        "optimize", "analyze", "verify", "check", "scan", "process"
    }
    
    @staticmethod
    def translate_command(command: str) -> str:
        """Platform-aware command translation (Linux → Windows)"""
        is_windows = os.name == "nt" or platform.system().lower() == "windows"
        
        if is_windows:
            # Unix to Windows command translations
            translations = {
                "ls -R": "dir /s", "ls -la": "dir /a", "ls -l": "dir", "ls": "dir",
                "cat": "type", "pwd": "cd", "rm": "del", "cp": "copy", "mv": "move",
                "mkdir": "mkdir", "rmdir": "rmdir", "grep": "findstr",
                "ps aux": "tasklist", "ps": "tasklist", "kill": "taskkill",
                "which": "where", "find": "dir /s /b",
                "df": "wmic logicaldisk get caption,size,freespace",
                "free": "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory",
                "uname -a": "systeminfo", "uname": "ver"
            }
            
            for unix_cmd, windows_cmd in translations.items():
                if command.startswith(unix_cmd):
                    remaining_args = command[len(unix_cmd):].strip()
                    return f"{windows_cmd} {remaining_args}" if remaining_args else windows_cmd
        
        return command
    
    @staticmethod
    def validate_command(command: str) -> Dict[str, Any]:
        """Ellenőrzi a parancsot biztonsági szempontból."""
        try:
            if os.name == "nt":
                command_parts = shlex.split(command, posix=False)
            else:
                command_parts = shlex.split(command)
        except ValueError as e:
            return {"valid": False, "reason": f"Érvénytelen parancs szintaxis: {str(e)}"}
        
        if not command_parts:
            return {"valid": False, "reason": "Üres parancs"}
        
        command_name = command_parts[0].lower()
        base_command = os.path.basename(command_name)
        
        # Tiltott parancsok ellenőrzése
        if base_command in CommandValidator.FORBIDDEN_COMMANDS:
            return {"valid": False, "reason": f"Tiltott parancs: {base_command}"}
        
        # Engedélyezett parancsok ellenőrzése
        if base_command not in CommandValidator.ALLOWED_COMMANDS:
            return {
                "valid": False, 
                "reason": f"Nem engedélyezett parancs: {base_command}"
            }
        
        # Veszélyes paraméterek ellenőrzése
        for param in command_parts[1:]:
            param_lower = param.lower()
            for dangerous in CommandValidator.DANGEROUS_PARAMS:
                if param_lower == dangerous or param_lower.startswith(dangerous + "="):
                    return {"valid": False, "reason": f"Veszélyes paraméter: {param}"}
        
        # Parancs operátorok ellenőrzése
        if any(op in command for op in [";", "|", "&", "&&", "||", ">", "<", ">>"]):
            return {"valid": False, "reason": "Parancs operátorok nem engedélyezettek"}
        
        return {"valid": True, "reason": "A parancs biztonságos", "command": command}


class SystemCommandTool(BaseTool):
    """Biztonságos rendszerparancs végrehajtás."""
    
    def __init__(self):
        super().__init__()
        self.work_dir = tool_registry.default_paths["temp"]
        
    async def execute(self, command: str, timeout: int = 30, workdir: Optional[str] = None) -> Dict[str, Any]:
        """Végrehajt egy rendszerparancsot biztonságos módon."""
        try:
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("system_command", {"command": command})
            if not security_check["allowed"]:
                return {
                    "success": False, "error": security_check["reason"],
                    "stdout": "", "stderr": "", "exit_code": -1
                }
            
            # Parancs validálása
            validation = CommandValidator.validate_command(command)
            if not validation["valid"]:
                return {
                    "success": False, "error": validation["reason"],
                    "stdout": "", "stderr": "", "exit_code": -1
                }
            
            # Platform-specifikus parancs fordítás
            translated_command = CommandValidator.translate_command(command)
            logger.info(f"Command translation: '{command}' -> '{translated_command}'")
            
            # Munkakönyvtár beállítása
            if workdir is None:
                workdir = self.work_dir
            
            # ⚡ OPTIMIZED: Shorter timeout for PowerShell commands
            if translated_command.startswith(('powershell', 'pwsh')):
                timeout = min(timeout, 15)  # Max 15 seconds for PowerShell
            
            # Parancs végrehajtása
            process = await asyncio.create_subprocess_shell(
                translated_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                shell=True
            )
            
            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                stdout = stdout_data.decode('utf-8', errors='replace')
                stderr = stderr_data.decode('utf-8', errors='replace')
                exit_code = process.returncode
                
            except asyncio.TimeoutError:
                # Timeout handling
                try:
                    process.terminate()
                    await asyncio.sleep(0.5)
                    if process.returncode is None:
                        process.kill()
                except Exception:
                    pass
                
                return {
                    "success": False,
                    "error": f"Timeout: Command exceeded {timeout}s limit",
                    "stdout": "", "stderr": "", "exit_code": -1, "timeout": True
                }
            
            return {
                "success": exit_code == 0,
                "stdout": stdout, "stderr": stderr, "exit_code": exit_code,
                "command": command, "translated_command": translated_command,
                "workdir": workdir
            }
            
        except Exception as e:
            logger.error(f"System command error: {str(e)}")
            return {
                "success": False, "error": f"Command execution error: {str(e)}",
                "stdout": "", "stderr": "", "exit_code": -1
            }


class SystemInfoTool(BaseTool):
    """Rendszer információk lekérdezése."""
    
    async def execute(self, info_type: str = "all") -> Dict[str, Any]:
        """Információkat ad a rendszerről."""
        try:
            result = {}
            
            if info_type in ["all", "os"]:
                result["os"] = {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "hostname": platform.node(),
                    "python_version": platform.python_version()
                }
                
            if info_type in ["all", "cpu"]:
                result["cpu"] = {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "cpu_percent": psutil.cpu_percent(interval=0.5)
                }
                
            if info_type in ["all", "memory"]:
                mem = psutil.virtual_memory()
                result["memory"] = {
                    "total": mem.total, "available": mem.available,
                    "used": mem.used, "percent": mem.percent
                }
            
            result["timestamp"] = psutil.boot_time()
            result["uptime"] = int(time.time() - psutil.boot_time())
            
            return {"success": True, "info_type": info_type, "result": result}
            
        except Exception as e:
            logger.error(f"System info error: {str(e)}")
            return {"success": False, "error": f"System info error: {str(e)}"}


class EnvironmentVariableTool(BaseTool):
    """Környezeti változók kezelése."""
    
    SAFE_ENV_VARS = {
        "PATH", "PYTHONPATH", "TEMP", "TMP", "HOME", "USER", 
        "USERPROFILE", "LANG", "LANGUAGE", "LC_ALL", "SHELL",
        "TERM", "HOSTNAME"
    }
    
    async def execute(self, action: str = "get", name: Optional[str] = None) -> Dict[str, Any]:
        """Környezeti változók kezelése."""
        try:
            if action == "list":
                safe_env = {k: v for k, v in os.environ.items() if k.upper() in self.SAFE_ENV_VARS}
                return {"success": True, "action": action, "variables": safe_env}
                
            elif action == "get":
                if name is None:
                    return {"success": False, "error": "A 'get' művelethez meg kell adni a változó nevét"}
                
                if name.upper() not in self.SAFE_ENV_VARS:
                    return {"success": False, "error": f"A(z) '{name}' változó nem kérdezhető le"}
                
                value = os.environ.get(name)
                if value is None:
                    return {"success": False, "error": f"A(z) '{name}' változó nem létezik"}
                
                return {"success": True, "action": action, "name": name, "value": value}
            
            else:
                return {"success": False, "error": f"Érvénytelen művelet: {action}"}
                
        except Exception as e:
            logger.error(f"Environment variable error: {str(e)}")
            return {"success": False, "error": f"Environment variable error: {str(e)}"}
