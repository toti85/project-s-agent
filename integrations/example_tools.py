"""
Example Tools for Project-S
--------------------------
This module provides example tools for Project-S that can be registered with the ToolManager.
Tools include:
- File operations: read/write/list files
- Web search: perform web searches
- Code execution: run and analyze code
- System information: get system stats
"""
import os
import sys
import json
import aiofiles
import aiohttp
import psutil
import asyncio
import subprocess
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

from integrations.tool_manager import tool_manager

logger = logging.getLogger(__name__)

# ===== FILE OPERATIONS =====
@tool_manager.register(
    metadata={
        "description": "Read the contents of a file",
        "category": "file",
        "tags": ["file", "io", "read"],
        "is_dangerous": False,
    }
)
async def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read the contents of a file.
    
    Args:
        file_path: The path to the file to read
        
    Returns:
        Dict containing file contents and metadata
        
    @category: file
    @author: Project-S
    """
    try:
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
            
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            
        file_stats = os.stat(file_path)
        
        return {
            "success": True,
            "content": content,
            "metadata": {
                "size": file_stats.st_size,
                "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "path": os.path.abspath(file_path)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool_manager.register(
    metadata={
        "description": "Write content to a file",
        "category": "file",
        "tags": ["file", "io", "write"],
        "is_dangerous": True,
    }
)
async def write_file(file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        file_path: The path to the file to write
        content: The content to write
        append: Whether to append to the file (default: False)
        
    Returns:
        Dict containing success status and metadata
        
    @category: file
    @author: Project-S
    """
    try:
        mode = 'a' if append else 'w'
        async with aiofiles.open(file_path, mode) as f:
            await f.write(content)
            
        return {
            "success": True,
            "metadata": {
                "path": os.path.abspath(file_path),
                "size": len(content),
                "operation": "append" if append else "write"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool_manager.register(
    metadata={
        "description": "List files in a directory",
        "category": "file",
        "tags": ["file", "directory", "list"],
        "is_dangerous": False,
    }
)
async def list_directory(directory_path: str, pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    List files in a directory, optionally filtering by pattern.
    
    Args:
        directory_path: The path to the directory to list
        pattern: Optional glob pattern to filter files
        
    Returns:
        Dict containing file list and metadata
        
    @category: file
    @author: Project-S
    """
    try:
        import glob
        
        if not os.path.exists(directory_path):
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
            
        if not os.path.isdir(directory_path):
            return {
                "success": False,
                "error": f"Not a directory: {directory_path}"
            }
        
        # List all files if no pattern is provided
        if pattern is None:
            files = os.listdir(directory_path)
        else:
            # Use glob to find files matching pattern
            path_with_pattern = os.path.join(directory_path, pattern)
            files = [os.path.basename(f) for f in glob.glob(path_with_pattern)]
            
        # Get additional metadata for each file
        file_list = []
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            is_dir = os.path.isdir(file_path)
            
            try:
                stats = os.stat(file_path)
                file_list.append({
                    "name": file_name,
                    "is_directory": is_dir,
                    "size": stats.st_size,
                    "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    "path": os.path.abspath(file_path)
                })
            except:
                # Handle case where file might be inaccessible
                file_list.append({
                    "name": file_name,
                    "is_directory": is_dir,
                    "path": os.path.abspath(file_path),
                    "error": "Cannot access file metadata"
                })
            
        return {
            "success": True,
            "files": file_list,
            "metadata": {
                "directory": os.path.abspath(directory_path),
                "count": len(file_list),
                "pattern": pattern
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ===== WEB SEARCH =====
@tool_manager.register(
    metadata={
        "description": "Search the web for information",
        "category": "web",
        "tags": ["web", "search", "internet"],
        "is_dangerous": False,
        "rate_limit": 10,  # Limit to 10 calls per minute
        "timeout": 30,     # Timeout after 30 seconds
    }
)
async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for information using a search API.
    
    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        
    Returns:
        Dict containing search results and metadata
        
    @category: web
    @author: Project-S
    """
    try:
        # This is a placeholder. In a real implementation, this would call 
        # an actual search API like Google Custom Search, Bing, or DuckDuckGo
        async with aiohttp.ClientSession() as session:
            # Simulating a web search with a delay
            await asyncio.sleep(1)
            
            # Mocked search results
            results = [
                {
                    "title": f"Search Result {i} for '{query}'",
                    "url": f"https://example.com/result/{i}",
                    "snippet": f"This is a snippet of text that would be returned for the search query '{query}'..."
                }
                for i in range(1, min(num_results + 1, 10))
            ]
            
            return {
                "success": True,
                "results": results,
                "metadata": {
                    "query": query,
                    "result_count": len(results),
                    "search_engine": "Mock Search Engine",
                    "timestamp": datetime.now().isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@tool_manager.register(
    metadata={
        "description": "Fetch the content of a web page",
        "category": "web",
        "tags": ["web", "fetch", "scrape"],
        "is_dangerous": False,
        "rate_limit": 5,   # Limit to 5 calls per minute
        "timeout": 60,     # Timeout after 60 seconds
    }
)
async def fetch_webpage(url: str) -> Dict[str, Any]:
    """
    Fetch the content of a web page.
    
    Args:
        url: The URL of the web page to fetch
        
    Returns:
        Dict containing page content and metadata
        
    @category: web
    @author: Project-S
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP Error: {response.status}",
                        "metadata": {
                            "url": url,
                            "status": response.status
                        }
                    }
                    
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    return {
                        "success": False,
                        "error": f"Not an HTML page. Content type: {content_type}",
                        "metadata": {
                            "url": url,
                            "content_type": content_type
                        }
                    }
                    
                html = await response.text()
                
                return {
                    "success": True,
                    "content": html,
                    "metadata": {
                        "url": url,
                        "title": extract_title(html),  # This would be a function to extract the page title
                        "content_type": content_type,
                        "headers": dict(response.headers),
                        "size": len(html),
                        "timestamp": datetime.now().isoformat()
                    }
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def extract_title(html: str) -> str:
    """
    Extract the title from HTML content.
    
    Args:
        html: HTML content
        
    Returns:
        The page title
    """
    import re
    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        return title_match.group(1).strip()
    return "Unknown Title"

# ===== CODE EXECUTION =====
@tool_manager.register(
    metadata={
        "description": "Execute Python code and return the result",
        "category": "code",
        "tags": ["code", "python", "execute"],
        "is_dangerous": True,
        "timeout": 5,  # Timeout after 5 seconds for safety
    }
)
async def execute_python(code: str, globals_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute Python code and return the result.
    
    Args:
        code: The Python code to execute
        globals_dict: Optional globals dictionary for execution context
        
    Returns:
        Dict containing execution result and metadata
        
    @category: code
    @author: Project-S
    """
    import io
    import contextlib
    from traceback import format_exc
    
    # Set up streams to capture output
    stdout = io.StringIO()
    stderr = io.StringIO()
    
    # Prepare globals dictionary
    if globals_dict is None:
        globals_dict = {}
    
    # Add safe imports
    safe_globals = {
        "__builtins__": {
            name: __builtins__[name] for name in [
                "abs", "all", "any", "bool", "chr", "dict", "dir", "divmod", 
                "enumerate", "filter", "float", "format", "frozenset", "hash", 
                "hex", "int", "isinstance", "issubclass", "len", "list", "map", 
                "max", "min", "oct", "ord", "pow", "print", "range", "repr", 
                "reversed", "round", "set", "slice", "sorted", "str", "sum", 
                "tuple", "type", "zip"
            ]
        }
    }
    
    # Update with provided globals
    execution_globals = {**safe_globals, **globals_dict}
    
    try:
        # Execute code with stdout/stderr capture
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            # Compile to catch syntax errors before execution
            compiled_code = compile(code, "<string>", "exec")
            
            # Create a local namespace for execution
            local_namespace = {}
            
            # Execute code
            exec(compiled_code, execution_globals, local_namespace)
            
        return {
            "success": True,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
            "locals": {k: v for k, v in local_namespace.items() if not k.startswith("_")},
            "metadata": {
                "code_length": len(code),
                "execution_time": "N/A"  # Would be measured in a real implementation
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": format_exc(),
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue()
        }

@tool_manager.register(
    metadata={
        "description": "Analyze code to extract structure and dependencies",
        "category": "code",
        "tags": ["code", "analysis", "ast"],
        "is_dangerous": False,
    }
)
async def analyze_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code to extract structure and dependencies.
    
    Args:
        code: The code to analyze
        language: The programming language (default: "python")
        
    Returns:
        Dict containing analysis results
        
    @category: code
    @author: Project-S
    """
    try:
        if language.lower() == "python":
            import ast
            import astunparse
            
            try:
                # Parse the code
                tree = ast.parse(code)
                
                # Extract imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append({
                                "module": name.name,
                                "alias": name.asname
                            })
                    elif isinstance(node, ast.ImportFrom):
                        for name in node.names:
                            imports.append({
                                "module": f"{node.module}.{name.name}",
                                "alias": name.asname,
                                "from_import": True,
                                "from_module": node.module
                            })
                
                # Extract functions and classes
                functions = []
                classes = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            "name": node.name,
                            "lineno": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "is_async": isinstance(node, ast.AsyncFunctionDef)
                        })
                    elif isinstance(node, ast.ClassDef):
                        classes.append({
                            "name": node.name,
                            "lineno": node.lineno,
                            "bases": [astunparse.unparse(base).strip() for base in node.bases]
                        })
                
                return {
                    "success": True,
                    "language": "python",
                    "imports": imports,
                    "functions": functions,
                    "classes": classes,
                    "metadata": {
                        "code_length": len(code),
                        "line_count": len(code.splitlines())
                    }
                }
            except SyntaxError as e:
                return {
                    "success": False,
                    "error": f"Syntax error: {str(e)}",
                    "language": "python"
                }
        else:
            return {
                "success": False,
                "error": f"Language not supported: {language}",
                "supported_languages": ["python"]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ===== SYSTEM INFORMATION =====
@tool_manager.register(
    metadata={
        "description": "Get system information",
        "category": "system",
        "tags": ["system", "info", "metrics"],
        "is_dangerous": False,
    }
)
async def get_system_info() -> Dict[str, Any]:
    """
    Get system information and metrics.
    
    Returns:
        Dict containing system information
        
    @category: system
    @author: Project-S
    """
    try:
        import platform
        
        # Get CPU information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Get memory information
        memory = psutil.virtual_memory()
        
        # Get disk information
        disk = psutil.disk_usage('/')
        
        return {
            "success": True,
            "system": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node()
            },
            "cpu": {
                "count": cpu_count,
                "usage_percent": cpu_percent,
                "per_cpu_percent": psutil.cpu_percent(interval=0.1, percpu=True)
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Register all example tools
def register_all_example_tools():
    """
    This function doesn't need to do anything since tools are registered with the
    @tool_manager.register decorator, but it can be called to ensure the module is imported
    and all tools are registered.
    """
    logger.info("Example tools registered with ToolManager")
    return {
        "file_tools": ["read_file", "write_file", "list_directory"],
        "web_tools": ["web_search", "fetch_webpage"],
        "code_tools": ["execute_python", "analyze_code"],
        "system_tools": ["get_system_info"]
    }
