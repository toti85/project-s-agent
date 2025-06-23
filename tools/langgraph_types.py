"""
Project-S LangGraph Types Module
-------------------------------
Ez a modul központi helyet biztosít a LangGraph-hoz kapcsolódó típusdefinícióknak,
ami segít elkerülni a körkörös importálási problémákat.
"""

from typing import Dict, Any, List, TypedDict, Optional, Union, Callable, Set, Tuple

# Alap állapot definíció a LangGraph állapotokhoz
class GraphState(TypedDict, total=False):
    """
    Alapvető állapot típus a LangGraph munkafolyamatokhoz.
    Ez a definíció használható azokban a modulokban, amelyeknek szükségük van
    a GraphState típusra, de nem akarnak körkörös importálásokat okozni.
    """
    messages: List[Dict[str, Any]]
    context: Dict[str, Any]
    
    # Opcionális mezők, amelyek gyakran használtak
    tool_results: Optional[Dict[str, Any]]
    errors: Optional[List[Dict[str, Any]]]
    
# Tool-specifikus állapot a LangGraph munkafolyamatokban
class ToolState(TypedDict, total=False):
    """
    Tool-specifikus állapot a LangGraph munkafolyamatokhoz.
    """
    messages: List[Dict[str, Any]]
    tools: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    tool_history: List[Dict[str, Any]]
    tool_errors: List[Dict[str, Any]]

# Dokumentáció generátor állapot
class DocGenState(TypedDict, total=False):
    """
    Dokumentáció generáló munkafolyamat állapota a LangGraph-ban.
    """
    messages: List[Dict[str, Any]]
    tools: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    tool_history: List[Dict[str, Any]]
    tool_errors: List[Dict[str, Any]]
    
    # A dokumentáció generáló speciális állapotai
    project_data: Dict[str, Any]
    file_analysis: Dict[str, Any]
    ai_results: Dict[str, Any]
    output_paths: Dict[str, str]
    current_stage: str
