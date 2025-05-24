"""
Project-S Tools Package
---------------------
Ez a csomag tartalmazza az összes eszközt (tool) a rendszer számára.
Az eszközök különböző funkciókat biztosítanak, mint fájlműveletek,
webes hozzáférés, kód végrehajtás, és rendszerparancsok.
"""

from tools.tool_interface import BaseTool
from tools.tool_registry import tool_registry

# Importáljuk az eszközök osztályait, hogy elérhetők legyenek
# a 'tools' névtérben anélkül, hogy minden eszközt külön kellene importálni
from tools.file_tools import FileReadTool, FileWriteTool, FileSearchTool, FileInfoTool, FileContentSearchTool
from tools.web_tools import WebPageFetchTool, WebApiCallTool, WebSearchTool
from tools.code_tools import CodeExecutionTool, PythonModuleInfoTool
from tools.system_tools import SystemCommandTool, SystemInfoTool, EnvironmentVariableTool

# Inicializálás
__all__ = [
    # Alap osztályok
    'BaseTool', 'tool_registry',
    
    # Fájl eszközök
    'FileReadTool', 'FileWriteTool', 'FileSearchTool', 
    'FileInfoTool', 'FileContentSearchTool',
    
    # Web eszközök
    'WebPageFetchTool', 'WebApiCallTool', 'WebSearchTool',
    
    # Kód eszközök
    'CodeExecutionTool', 'PythonModuleInfoTool',
    
    # Rendszer eszközök
    'SystemCommandTool', 'SystemInfoTool', 'EnvironmentVariableTool'
]

# Automatikus eszköz regisztráció a ToolRegistry-ben
async def register_all_tools():
    """
    Regisztrálja az összes eszközt a tool_registry-ben.
    """
    # Eszköz osztályok betöltése
    await tool_registry.load_tools()
    
    # Minden betöltött tool osztályból példányt hozunk létre és regisztráljuk
    for name, cls in tool_registry.tool_classes.items():
        try:
            instance = cls()
            tool_registry.register_tool(instance)
        except Exception as e:
            print(f"[register_all_tools] Nem sikerült példányosítani/regisztrálni: {name} - {e}")
    
    # Biztonsági konfiguráció betöltése
    tool_registry.load_security_config()
    # DEBUG: Kiírjuk a regisztrált toolok nevét
    print(f"[register_all_tools] Regisztrált toolok: {list(tool_registry.tools.keys())}")
