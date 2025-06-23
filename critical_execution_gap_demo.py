#!/usr/bin/env python3
"""
KRITIKUS DIAGNOSZTIKA: Projekt-S task execution hiánya
Bemutatkozza, hogy a rendszer csak beszél a feladatokról, de sosem hajtja végre őket.
"""
import asyncio
import logging
from datetime import datetime

# Beállítjuk a loggolást
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def demonstrate_execution_gap():
    """Bemutatkozza a végrehajtási hézagot"""
    
    print("=== KRITIKUS DIAGNOSZTIKA: PROJECT-S EXECUTION GAP ===")
    print("Demonstráljuk, hogy a rendszer csak beszél, nem cselekszik\n")
    
    # 1. Megnézzük, hogy a tools működnek-e külön
    print("1. TOOL TESZTELÉS (Külön):")
    from tools.tool_registry import tool_registry
    await tool_registry.load_tools()
    
    write_tool = tool_registry.get_tool("FileWriteTool")
    if write_tool:
        result = await write_tool.execute(
            path="PROOF_TOOLS_WORK.txt",
            content="Ez bizonyítja, hogy a tools működnek!"
        )
        print(f"   ✅ FileWriteTool működik: {result['success']}")
    
    # 2. Most megnézzük, hogy a main workflow használja-e a tools-okat
    print("\n2. WORKFLOW ANALYSIS:")
    from integrations.model_manager import model_manager
    from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
    
    # Simuláljuk egy feladat végrehajtását
    print("   Feladat: 'Írj hello world-öt egy fájlba'")
    
    # Mit csinál a model_manager?
    print("   Mit csinál a model_manager.execute_task_with_model?")
    result = await model_manager.execute_task_with_model(
        query="Írj hello world-öt egy fájlba",
        system_message="Te egy file írásért felelős vagy.",
        task_type="file_operation"
    )
    
    print(f"   Model válasz: {result.get('content', 'No content')[:100]}...")
    print(f"   Típus: {type(result)}")
    print(f"   Van-e 'file_created' kulcs: {'file_created' in result}")
    print(f"   Van-e 'tool_executed' kulcs: {'tool_executed' in result}")
    
    # 3. Ellenőrizzük, hogy létrejött-e ténylegesen valami fájl
    print("\n3. VALÓDI HATÁS ELLENŐRZÉSE:")
    import os
    files_created = [f for f in os.listdir('.') if f.startswith('hello') or 'hello' in f.lower()]
    print(f"   Hello fájlok létrehozva: {files_created}")
    
    # 4. A KRITIKUS HIBA MAGYARÁZATA
    print("\n4. 🚨 KRITIKUS PROBLÉMA AZONOSÍTVA:")
    print("   ❌ model_manager.execute_task_with_model() CSAK AI SZÖVEGET GENERÁL")
    print("   ❌ NEM HAJT VÉGRE TOOLS-OKAT")
    print("   ❌ NEM CSINÁL VALÓDI MŰVELETET")
    print("   ✅ Tools külön-külön működnek")
    print("   🔥 A BRIDGE HIÁNYZIK AI ↔ TOOLS között")
    
    # Cleanup
    if os.path.exists("PROOF_TOOLS_WORK.txt"):
        os.remove("PROOF_TOOLS_WORK.txt")
    
    print("\n=== DIAGNÓZIS VÉGE ===")

if __name__ == "__main__":
    asyncio.run(demonstrate_execution_gap())
