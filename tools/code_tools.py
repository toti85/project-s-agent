"""
Project-S Code Tools
-----------------
Ez a modul a kód végrehajtáshoz kapcsolódó eszközöket tartalmazza:
- Python kód futtatás biztonságos környezetben
- Kód szerkesztés és validálás
"""

import os
import asyncio
import logging
import ast
import sys
import io
import traceback
from typing import Dict, Any, List, Optional, Union, Set
from pathlib import Path
import uuid
import shutil
import tempfile
import contextlib
import importlib
import time
import signal
import subprocess
import json

from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry

logger = logging.getLogger(__name__)

# Biztonságos kód végrehajtáshoz használt segédfüggvények és osztályok

class CodeSandbox:
    """
    Biztonságos környezet a kód futtatásához.
    
    A CodeSandbox osztály gondoskodik arról, hogy a futtatott kód ne férjen hozzá
    a rendszerhez vagy ne tudjon káros műveleteket végrehajtani.
    """
    
    # Tiltott modulok
    FORBIDDEN_MODULES = {
        'os', 'subprocess', 'sys', 'builtins', 
        'importlib', 'importlib.util', 'multiprocessing',
        'ctypes', 'socket', 'shutil'
    }
    
    # Korlátozott modulok (csak bizonyos függvényekhez férhet hozzá)
    LIMITED_MODULES = {
        'pathlib': {'Path.read_text', 'Path.exists', 'Path.is_file', 'Path.is_dir'},
        'io': {'StringIO', 'BytesIO', 'TextIOWrapper'}
    }
    
    def __init__(self, 
                max_execution_time: int = 5, 
                max_memory_mb: int = 100,
                allowed_modules: Optional[Set[str]] = None):
        """
        Inicializálja a homokozót.
        
        Args:
            max_execution_time: Maximális végrehajtási idő másodpercben
            max_memory_mb: Maximális memóriahasználat megabájtban
            allowed_modules: Engedélyezett modulok halmaza
        """
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.allowed_modules = allowed_modules or set()
        
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Ellenőrzi a kódot biztonsági szempontból.
        
        Args:
            code: A vizsgálandó kód szövege
            
        Returns:
            Dict[str, Any]: Az ellenőrzés eredménye
        """
        try:
            parsed = ast.parse(code)
            return self._analyze_ast(parsed)
        except SyntaxError as e:
            return {
                "valid": False,
                "reason": f"Szintaktikai hiba: {str(e)}",
                "line": e.lineno,
                "column": e.offset
            }
            
    def _analyze_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Elemzi az AST-t biztonsági szempontból.
        
        Args:
            tree: Az elemzendő AST
            
        Returns:
            Dict[str, Any]: Az elemzés eredménye
        """
        # Veszélyes import ellenőrző
        import_checker = ImportChecker(self.FORBIDDEN_MODULES)
        import_checker.visit(tree)
        
        if import_checker.violations:
            return {
                "valid": False,
                "reason": f"Tiltott modul importálása: {', '.join(import_checker.violations)}",
                "line": import_checker.violation_lines[0] if import_checker.violation_lines else 0
            }
            
        # Veszélyes függvényhívás ellenőrző
        call_checker = CallChecker()
        call_checker.visit(tree)
        
        if call_checker.violations:
            return {
                "valid": False,
                "reason": f"Tiltott függvényhívás: {', '.join(call_checker.violations)}",
                "line": call_checker.violation_lines[0] if call_checker.violation_lines else 0
            }
        
        return {
            "valid": True,
            "reason": "A kód megfelel a biztonsági előírásoknak"
        }
        
    async def execute_code(self, code: str, globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Végrehajtja a kódot biztonságos környezetben.
        
        Args:
            code: A végrehajtandó kód
            globals_dict: Globális változók szótára
            
        Returns:
            Dict[str, Any]: A végrehajtás eredménye
        """
        # Először validáljuk a kódot
        validation = self.validate_code(code)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["reason"],
                "output": "",
                "execution_time": 0
            }
            
        # Előkészítjük a futtatási környezetet
        if globals_dict is None:
            globals_dict = {}
            
        # Átirányítjuk a standard kimenetet és hibakimenetet
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Időmérés
        start_time = time.time()
        
        # Eredmény változók
        success = True
        error = ""
        result_value = None
        
        try:
            # Végrehajtás időkorláttal és kimenet elfogással
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Időkorlát beállítása
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.max_execution_time)
                
                try:
                    # Előkészítjük a kódot a végrehajtásra, hogy az utolsó kifejezést visszaadja
                    try:
                        tree = ast.parse(code)
                        last_expr = None
                        
                        # Ellenőrizzük, hogy az utolsó utasítás kifejezés-e
                        if tree.body and isinstance(tree.body[-1], ast.Expr):
                            last_expr = tree.body[-1]
                            tree.body = tree.body[:-1]
                            
                            # Összeállítjuk a végrehajtandó kódot
                            exec_code = compile(tree, "<string>", "exec")
                            
                            # Végrehajtjuk a kódot
                            exec(exec_code, globals_dict)
                            
                            # Ha volt utolsó kifejezés, kiértékeljük
                            if last_expr:
                                last_expr_code = compile(ast.Module(body=[last_expr], type_ignores=[]), "<string>", "eval")
                                result_value = eval(last_expr_code, globals_dict)
                        else:
                            # Ha nincs utolsó kifejezés, egyszerűen végrehajtjuk a kódot
                            exec(code, globals_dict)
                            
                    except Exception as e:
                        success = False
                        error = str(e)
                        traceback.print_exc(file=stderr_capture)
                
                finally:
                    # Időkorlát visszavonása
                    signal.alarm(0)
        
        except TimeoutError:
            success = False
            error = f"Időtúllépés: a végrehajtás tovább tartott, mint {self.max_execution_time} másodperc"
            
        # Végrehajtás ideje
        execution_time = time.time() - start_time
        
        # Eredmény összeállítása
        return {
            "success": success,
            "error": error,
            "output": stdout_capture.getvalue(),
            "error_output": stderr_capture.getvalue(),
            "result": result_value,
            "execution_time": execution_time,
            "globals": {k: v for k, v in globals_dict.items() 
                        if not k.startswith("__") and not callable(v) and not isinstance(v, type)}
        }
        
    @staticmethod
    def _timeout_handler(signum, frame):
        """Időtúllépés kezelő."""
        raise TimeoutError("A kód végrehajtása túllépte az időkorlátot")


class ImportChecker(ast.NodeVisitor):
    """AST látogató az importok ellenőrzéséhez."""
    
    def __init__(self, forbidden_modules: Set[str]):
        self.forbidden_modules = forbidden_modules
        self.violations = set()
        self.violation_lines = []
        
    def visit_Import(self, node: ast.Import) -> None:
        """Import utasítások ellenőrzése."""
        for name in node.names:
            module = name.name.split('.')[0]
            if module in self.forbidden_modules:
                self.violations.add(module)
                self.violation_lines.append(node.lineno)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """From import utasítások ellenőrzése."""
        if node.module:
            module = node.module.split('.')[0]
            if module in self.forbidden_modules:
                self.violations.add(module)
                self.violation_lines.append(node.lineno)
        self.generic_visit(node)


class CallChecker(ast.NodeVisitor):
    """AST látogató a függvényhívások ellenőrzéséhez."""
    
    DANGEROUS_CALLS = {
        "eval", "exec", "compile", "globals", "locals", "getattr", "setattr",
        "delattr", "__import__", "open", "input"
    }
    
    def __init__(self):
        self.violations = set()
        self.violation_lines = []
        
    def visit_Call(self, node: ast.Call) -> None:
        """Függvényhívások ellenőrzése."""
        if isinstance(node.func, ast.Name) and node.func.id in self.DANGEROUS_CALLS:
            self.violations.add(node.func.id)
            self.violation_lines.append(node.lineno)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in self.DANGEROUS_CALLS:
            self.violations.add(node.func.attr)
            self.violation_lines.append(node.lineno)
        self.generic_visit(node)


class CodeExecutionTool(BaseTool):
    """
    Biztonságos Python kód végrehajtása.
    
    Category: code
    Version: 1.0.0
    Requires permissions: Yes
    Safe: Yes
    """
    
    def __init__(self):
        """Inicializálja az eszközt."""
        super().__init__()
        
        # Létrehozunk egy homokozó példányt
        self.sandbox = CodeSandbox(
            max_execution_time=5,
            max_memory_mb=100,
            allowed_modules={"math", "random", "datetime", "json", "re", "collections", "itertools"}
        )
        
    async def execute(self, 
                    code: str,
                    globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Végrehajt egy Python kód részletet biztonságos környezetben.
        
        Args:
            code: A végrehajtandó Python kód
            globals_dict: Opcionális globális változók
            
        Returns:
            Dict: A végrehajtás eredménye
        """
        try:
            # Biztonsági ellenőrzés
            security_check = tool_registry.check_security("code_execution", {"code_length": len(code)})
            if not security_check["allowed"]:
                return {
                    "success": False,
                    "error": security_check["reason"],
                    "output": ""
                }
                
            # Kód validálása
            validation = self.sandbox.validate_code(code)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"A kód nem biztonságos: {validation['reason']}",
                    "output": ""
                }
                
            # Alapvető modulok hozzáadása a globálisokhoz
            if globals_dict is None:
                globals_dict = {}
                
            # Futtatás a homokozóban
            result = await self.sandbox.execute_code(code, globals_dict)
            
            # Eredmény formázása
            return {
                "success": result["success"],
                "output": result["output"],
                "error": result.get("error", ""),
                "error_output": result.get("error_output", ""),
                "result": result.get("result"),
                "execution_time": result["execution_time"],
                "globals": result.get("globals", {})
            }
                
        except Exception as e:
            logger.error(f"Hiba történt a kód végrehajtása közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba a kód végrehajtása során: {str(e)}",
                "output": ""
            }


class PythonModuleInfoTool(BaseTool):
    """
    Python modullal kapcsolatos információk lekérdezése.
    
    Category: code
    Version: 1.0.0
    Requires permissions: No
    Safe: Yes
    """
    
    # Biztonságos modulok listája
    SAFE_MODULES = {
        "math", "random", "datetime", "json", "re", "collections", 
        "itertools", "functools", "string", "typing", "enum", "copy",
        "dataclasses", "uuid", "time", "calendar"
    }
    
    async def execute(self,
                     module_name: str,
                     attribute: Optional[str] = None) -> Dict[str, Any]:
        """
        Információt ad egy Python modulról vagy annak tulajdonságairól.
        
        Args:
            module_name: A modul neve
            attribute: Opcionális attribútum név a modulon belül
            
        Returns:
            Dict: A lekérdezés eredménye
        """
        try:
            # Biztonsági ellenőrzés
            if module_name not in self.SAFE_MODULES:
                return {
                    "success": False,
                    "error": f"A modul nem szerepel a biztonságos modulok listáján: {module_name}"
                }
                
            # Modul importálása
            try:
                module = importlib.import_module(module_name)
            except (ImportError, ModuleNotFoundError) as e:
                return {
                    "success": False,
                    "error": f"A modul nem található: {module_name} - {str(e)}"
                }
                
            # Ha csak a modulról kérünk információt
            if attribute is None:
                # Összegyűjtjük a modul publikus attribútumait
                attrs = []
                for name in dir(module):
                    if not name.startswith("_"):
                        attrs.append(name)
                
                return {
                    "success": True,
                    "module": module_name,
                    "attributes": attrs,
                    "doc": module.__doc__
                }
                
            # Ha egy konkrét attribútumról kérünk információt
            if not hasattr(module, attribute):
                return {
                    "success": False,
                    "error": f"Az attribútum nem található a modulban: {attribute}"
                }
                
            attr = getattr(module, attribute)
            
            # Különböző típusú attribútumok kezelése
            if callable(attr):
                # Függvény vagy osztály
                doc = attr.__doc__ or "Nincs dokumentáció"
                
                # Ellenőrizzük, hogy osztály-e
                if isinstance(attr, type):
                    return {
                        "success": True,
                        "type": "class",
                        "name": attribute,
                        "doc": doc
                    }
                else:
                    # Függvény
                    import inspect
                    signature = str(inspect.signature(attr))
                    
                    return {
                        "success": True,
                        "type": "function",
                        "name": attribute,
                        "signature": signature,
                        "doc": doc
                    }
            else:
                # Egyéb attribútum
                return {
                    "success": True,
                    "type": "attribute",
                    "name": attribute,
                    "value": str(attr),
                    "python_type": type(attr).__name__
                }
                
        except Exception as e:
            logger.error(f"Hiba történt a modul információ lekérése közben: {str(e)}")
            return {
                "success": False,
                "error": f"Hiba a modul információ lekérése során: {str(e)}"
            }