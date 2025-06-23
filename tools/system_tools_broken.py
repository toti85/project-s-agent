"""
Project-S System Tools
------------------
Ez a modul a rendszerparancsokhoz és rendszerfunkciókhoz kapcsolódó eszközöket tartalmazza:
- Biztonságos rendszerparancs végrehajtás
- Rendszer információk lekérése
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
from typing import Dict, Any, List, Optional, Union, Set
from pathlib import Path

from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class CommandValidator:
    """
    Rendszerparancs validátor és korlátozó segédosztály.
    """
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
    }    # Engedélyezett parancsok fehérlistája
    ALLOWED_COMMANDS = {
        "ls", "dir", "cd", "pwd", "echo", "cat", "type",
        "find", "mkdir", "md", "ping", "ipconfig", "ifconfig",
        "systeminfo", "ver", "uname", "ps", "tasklist", 
        "free", "df", "du", "date", "time", "whoami",
        "hostname", "python", "pip",
        # 🚀 ENHANCED: Added Windows package managers and development tools
        "winget", "choco", "chocolatey", "scoop",
        "powershell", "pwsh", "cmd", "wmic", "sfc", "dism",
        "get-windowsupdate", "install-windowsupdate", "update-module",
        "git", "npm", "node", "dotnet", "java", "mvn", "gradle",
        # 🔧 ADDED: Common Unix/Linux commands that need translation
        "grep", "findstr", "apt", "yum", "dnf", "pacman",
        "which", "where", "head", "tail", "more", "less",
        "cp", "copy", "mv", "move", "touch", "chmod", "attrib",
        # 🎯 HYBRID WORKFLOW: AI-generated commands and system optimization
        "del", "cleanmgr", "auto_detect", "request_parser", "content_analyzer",
        "web_scraper", "request_analyzer", "to_be_determined", "cleanup",
        "optimize", "analyze", "verify", "check", "scan", "process"
    }
    
    @staticmethod
    def translate_command(command: str) -> str:
        """
        🔄 CRITICAL FIX: Platform-aware command translation (Linux → Windows)
        
        Fordítja a parancsot a megfelelő platformra.
        
        Args:
            command: Az eredeti parancs
            
        Returns:
            str: A platformra optimalizált parancs
        """
        # Platform detection
        is_windows = os.name == "nt" or platform.system().lower() == "windows"
        
        # Command translation mapping
        if is_windows:
            # Unix to Windows command translations
            translations = {
                "ls -R": "dir /s",
                "ls -la": "dir /a",
                "ls -l": "dir",
                "ls": "dir",
                "cat": "type",
                "pwd": "cd",
                "rm": "del",
                "cp": "copy",
                "mv": "move",
                "mkdir": "mkdir",
                "rmdir": "rmdir",
                "grep": "findstr",                "ps aux": "tasklist",
                "ps": "tasklist",
                "kill": "taskkill",
                "which": "where",
                "find": "dir /s /b",
                "df": "wmic logicaldisk get caption,size,freespace",
                "free": "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory",
                "uname -a": "systeminfo",
                "uname": "ver",
                # Safe system update commands that don't hang
                "sudo apt update": "winget list --upgrade-available",
                "sudo apt upgrade": "winget list --upgrade-available",
                "sudo apt update && sudo apt upgrade": "winget list --upgrade-available",
                "apt update": "winget list --upgrade-available", 
                "apt upgrade": "winget list --upgrade-available",
                "yum update": "winget list --upgrade-available",
                "dnf update": "winget list --upgrade-available",
                "pacman -Syu": "winget list --upgrade-available"
            }
            
            # Apply translations
            for unix_cmd, windows_cmd in translations.items():
                if command.startswith(unix_cmd):
                    # Replace the command while preserving additional arguments
                    remaining_args = command[len(unix_cmd):].strip()
                    if remaining_args:
                        return f"{windows_cmd} {remaining_args}"
                    else:
                        return windows_cmd
        else:
            # Windows to Unix command translations (if needed)
            translations = {
                "dir /s": "ls -R",
                "dir /a": "ls -la", 
                "dir": "ls -l",
                "type": "cat",
                "del": "rm",
                "copy": "cp",
                "move": "mv",
                "tasklist": "ps",
                "taskkill": "kill",
                "where": "which"
            }
            
            # Apply translations
            for windows_cmd, unix_cmd in translations.items():
                if command.startswith(windows_cmd):
                    remaining_args = command[len(windows_cmd):].strip()
                    if remaining_args:
                        return f"{unix_cmd} {remaining_args}"
                    else:
                        return unix_cmd
        
        return command
    
    @staticmethod
    def validate_command(command: str) -> Dict[str, Any]:
        """
        Ellenőrzi a parancsot biztonsági szempontból.
        
        Args:
            command: Az ellenőrizendő parancs
            
        Returns:
            Dict[str, Any]: Az ellenőrzés eredménye
        """
        # Parancs felosztása részekre
        if os.name == "nt":  # Windows
            try:
                # Windows-specifikus idézőjel kezelés
                command_parts = shlex.split(command, posix=False)
            except ValueError as e:
                return {
                    "valid": False,
                    "reason": f"Érvénytelen parancs szintaxis: {str(e)}"
                }
        else:
            try:
                command_parts = shlex.split(command)
            except ValueError as e:
                return {
                    "valid": False,
                    "reason": f"Érvénytelen parancs szintaxis: {str(e)}"
                }
        
        if not command_parts:
            return {
                "valid": False,
                "reason": "Üres parancs"
            }
        
        # Első szó a parancs neve
        command_name = command_parts[0].lower()
        base_command = os.path.basename(command_name)
        
        # Ellenőrizzük, hogy a parancs szerepel-e a tiltólistán
        if base_command in CommandValidator.FORBIDDEN_COMMANDS:
            return {
                "valid": False,
                "reason": f"Tiltott parancs: {base_command}"
            }
            
        # Ha a parancs nem szerepel az engedélyezett listán
        if base_command not in CommandValidator.ALLOWED_COMMANDS:
            return {
                "valid": False,
                "reason": f"Nem engedélyezett parancs: {base_command}. Csak a következők engedélyezettek: {', '.join(CommandValidator.ALLOWED_COMMANDS)}"
            }
            
        # Ellenőrizzük a paramétereket
        for param in command_parts[1:]:
            param_lower = param.lower()
            
            # Veszélyes paraméterek ellenőrzése
            for dangerous in CommandValidator.DANGEROUS_PARAMS:
                if param_lower == dangerous or param_lower.startswith(dangerous + "="):
                    return {
                        "valid": False,
                        "reason": f"Veszélyes paraméter: {param}"
                    }
                    
            # Tiltott parancsok keresése a paraméterekben (pl. shell beágyazás)
            for forbidden in CommandValidator.FORBIDDEN_COMMANDS:
                if forbidden in param_lower:
                    # Ellenőrizzük, hogy valóban parancs beágyazásról van-e szó
                    if ";" in param or "|" in param or "&" in param or "`" in param or "$(" in param:
                        return {
                            "valid": False,
                            "reason": f"A parancs beágyazás nem engedélyezett: {param}"
                        }
                    if os.name == "nt" and ("%" in param and "%" in param[param.find("%") + 1:]):
                        return {
                            "valid": False,
                            "reason": f"A parancs beágyazás nem engedélyezett: {param}"
                        }
                        
        # Parancs operátorok ellenőrzése
        if ";" in command or "|" in command or "&" in command or "&&" in command or "||" in command:
            return {
                "valid": False,
                "reason": "Parancs operátorok és láncok nem engedélyezettek"
            }
            
        # Átirányítás operátorok ellenőrzése
        if ">" in command or "<" in command or ">>" in command:
            return {
                "valid": False,
                "reason": "Átirányító operátorok nem engedélyezettek"
            }
        
        return {
            "valid": True,
            "reason": "A parancs biztonságos",
            "command": command
        }


class SystemCommandTool(BaseTool):
    """
    Biztonságos rendszerparancs végrehajtás.
    
    Category: system
    Version: 1.0.0
    Requires permissions: Yes
    Safe: No
    """
    
    def __init__(self):
        """Inicializálja az eszközt."""
        super().__init__()
        # Beállítjuk a munkamappát
        self.work_dir = tool_registry.default_paths["temp"]
        
    async def execute(self, 
                     command: str,
                     timeout: int = 30,
                     workdir: Optional[str] = None) -> Dict[str, Any]:
        """
        Végrehajt egy rendszerparancsot biztonságos módon.
        
        Args:
            command: A végrehajtandó parancs
            timeout: Időtúllépés másodpercben
            workdir: Munkakönyvtár elérési útja
            
        Returns:
            Dict: A végrehajtás eredménye
        """
        try:
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("system_command", {"command": command})
            if not security_check["allowed"]:
                return {
                    "success": False,
                    "error": security_check["reason"],
                    "stdout": "",
                    "stderr": "",
                    "exit_code": -1
                }
                  # Parancs validálása
            validation = CommandValidator.validate_command(command)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation["reason"],
                    "stdout": "",
                    "stderr": "",
                    "exit_code": -1
                }
                
            # Platform-specifikus parancs fordítás
            translated_command = CommandValidator.translate_command(command)
            logger.info(f"Command translation: '{command}' -> '{translated_command}'")
                
            # Munkakönyvtár beállítása
            if workdir is None:
                workdir = self.work_dir
            else:
                # Ellenőrizzük, hogy a munkakönyvtár megengedett-e
                workdir_path = Path(workdir).resolve()
                for restricted in tool_registry.security_config["restricted_paths"]:
                    if str(workdir_path).startswith(restricted):
                        return {
                            "success": False,
                            "error": f"A megadott munkakönyvtár ({workdir}) korlátozott: {restricted}",
                            "stdout": "",
                            "stderr": "",
                            "exit_code": -1
                        }            # 🚀 ENHANCED: Optimized PowerShell execution with faster timeout
            # For PowerShell commands, use shorter timeout and optimized execution
            if translated_command.startswith('powershell') or translated_command.startswith('pwsh'):
                # Optimize PowerShell commands for faster execution
                if 'Remove-Item' in translated_command:
                    # Make temp cleanup faster and safer
                    translated_command = translated_command.replace(
                        'Remove-Item $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue',
                        'powershell -Command "Get-ChildItem $env:TEMP -Force | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-1)} | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue" -TimeoutSec 10'
                    )
                # Use shorter timeout for PowerShell commands
                ps_timeout = min(timeout, 15)  # Max 15 seconds for PowerShell
            else:
                ps_timeout = timeout
            
            # Parancs végrehajtása aszinkron módon
            process = await asyncio.create_subprocess_shell(
                translated_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                shell=True
            )
            
            try:                stdout_data, stderr_data = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=ps_timeout
                )
                stdout = stdout_data.decode('utf-8', errors='replace')
                stderr = stderr_data.decode('utf-8', errors='replace')
                exit_code = process.returncode
                
            except asyncio.TimeoutError:
                # Időtúllépés esetén megszakítjuk a folyamatot
                try:
                    process.terminate()
                    await asyncio.sleep(0.5)
                    if process.returncode is None:
                        process.kill()
                except Exception:
                    pass
                    
                return {
                    "success": False,
                    "error": f"⏱️ PowerShell timeout: Command exceeded {ps_timeout}s limit (optimized for performance)",
                    "stdout": "",
                    "stderr": "",
                    "exit_code": -1,
                    "timeout": True,
                    "optimization_note": "PowerShell commands are limited to 15s for system performance"
                }
            
            # Eredmény összeállítása
            success = exit_code == 0
            
            return {
                "success": success,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "command": command,
                "translated_command": translated_command,
                "workdir": workdir
            }
                
        except Exception as e:
            logger.error(f"Hiba történt a rendszerparancs végrehajtása közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba a rendszerparancs végrehajtása során: {str(e)}",
                "stdout": "",
                "stderr": "",
                "exit_code": -1
            }


class SystemInfoTool(BaseTool):
    """
    Rendszer információk lekérdezése.
    
    Category: system
    Version: 1.0.0
    Requires permissions: No
    Safe: Yes
    """
    
    async def execute(self, info_type: str = "all") -> Dict[str, Any]:
        """
        Információkat ad a rendszerről.
        
        Args:
            info_type: A lekérendő információ típusa 
                      ('all', 'os', 'cpu', 'memory', 'disk', 'network')
            
        Returns:
            Dict: A lekérdezés eredménye
        """
        try:
            result = {}
            
            # Információk az operációs rendszerről
            if info_type in ["all", "os"]:
                os_info = {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "hostname": platform.node(),
                    "python_version": platform.python_version()
                }
                result["os"] = os_info
                
            # CPU információ
            if info_type in ["all", "cpu"]:
                cpu_info = {
                    "physical_cores": psutil.cpu_count(logical=False),
                    "total_cores": psutil.cpu_count(logical=True),
                    "cpu_percent": psutil.cpu_percent(interval=0.5),
                    "cpu_freq": {
                        "current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                        "min": psutil.cpu_freq().min if psutil.cpu_freq() else None,
                        "max": psutil.cpu_freq().max if psutil.cpu_freq() else None
                    }
                }
                result["cpu"] = cpu_info
                
            # Memória információ
            if info_type in ["all", "memory"]:
                mem = psutil.virtual_memory()
                memory_info = {
                    "total": mem.total,
                    "available": mem.available,
                    "used": mem.used,
                    "percent": mem.percent
                }
                result["memory"] = memory_info
                
                # Swap információ
                swap = psutil.swap_memory()
                swap_info = {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                }
                result["swap"] = swap_info
                
            # Lemez információ
            if info_type in ["all", "disk"]:
                disk_info = []
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partition_info = {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent
                        }
                        disk_info.append(partition_info)
                    except (PermissionError, OSError):
                        # Néhány lemez nem elérhető (pl. CD-ROM)
                        pass
                        
                result["disk"] = disk_info
                
            # Hálózati információ
            if info_type in ["all", "network"]:
                # Hálózati interfészek
                interfaces = psutil.net_if_addrs()
                net_interfaces = {}
                
                for interface_name, interface_addresses in interfaces.items():
                    addresses = []
                    for addr in interface_addresses:
                        address_info = {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast
                        }
                        addresses.append(address_info)
                        
                    net_interfaces[interface_name] = addresses
                    
                # Hálózati forgalom
                net_io = psutil.net_io_counters()
                net_io_info = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
                
                result["network"] = {
                    "interfaces": net_interfaces,
                    "io": net_io_info
                }
                
            # Az eredmény kiegészítése egyéb adatokkal
            result["timestamp"] = psutil.boot_time()
            result["uptime"] = int(time.time() - psutil.boot_time())
            
            return {
                "success": True,
                "info_type": info_type,
                "result": result
            }
                
        except Exception as e:
            logger.error(f"Hiba történt a rendszer információk lekérése közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba a rendszer információk lekérése során: {str(e)}"
            }


class EnvironmentVariableTool(BaseTool):
    """
    Környezeti változók kezelése.
    
    Category: system
    Version: 1.0.0
    Requires permissions: No
    Safe: Yes
    """
    
    # Biztonságos környezeti változók, amelyek lekérdezhetők
    SAFE_ENV_VARS = {
        "PATH", "PYTHONPATH", "TEMP", "TMP", "HOME", "USER", 
        "USERPROFILE", "LANG", "LANGUAGE", "LC_ALL", "SHELL",
        "TERM", "HOSTNAME"
    }
    
    async def execute(self, 
                     action: str = "get",
                     name: Optional[str] = None) -> Dict[str, Any]:
        """
        Környezeti változók kezelése.
        
        Args:
            action: A végrehajtandó művelet ('get' vagy 'list')
            name: A környezeti változó neve (csak 'get' művelethez)
            
        Returns:
            Dict: A művelet eredménye
        """
        try:
            # Lista művelet: összes biztonságos env változó listázása
            if action == "list":
                # Csak a biztonságos változókat adjuk vissza
                safe_env = {}
                for key, value in os.environ.items():
                    if key.upper() in self.SAFE_ENV_VARS:
                        safe_env[key] = value
                        
                return {
                    "success": True,
                    "action": action,
                    "variables": safe_env
                }
                
            # Get művelet: egy konkrét változó lekérése
            elif action == "get":
                if name is None:
                    return {
                        "success": False,
                        "error": "A 'get' művelethez meg kell adni a változó nevét"
                    }
                    
                # Ellenőrizzük, hogy biztonságos-e a változó
                if name.upper() not in self.SAFE_ENV_VARS:
                    return {
                        "success": False,
                        "error": f"A(z) '{name}' környezeti változó nem kérdezhető le biztonsági okokból"
                    }
                    
                # Változó lekérése
                value = os.environ.get(name)
                
                if value is None:
                    return {
                        "success": False,
                        "error": f"A(z) '{name}' környezeti változó nem létezik"
                    }
                    
                return {
                    "success": True,
                    "action": action,
                    "name": name,
                    "value": value
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Érvénytelen művelet: {action}. Támogatott műveletek: 'get', 'list'"
                }
                
        except Exception as e:
            logger.error(f"Hiba történt a környezeti változók kezelése közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba a környezeti változók kezelése során: {str(e)}"
            }