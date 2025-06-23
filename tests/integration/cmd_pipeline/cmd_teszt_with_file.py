#!/usr/bin/env python3
"""
CMD TESZT FÁJLBA ÍRÁSSAL
=======================
Írjuk ki a CMD teszt eredményeket fájlba
"""

import asyncio
import sys
import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def cmd_teszt_with_file_output():
    """CMD teszt fájl kimenettel"""
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"CMD_TESZT_EREDMENY_{timestamp}.txt"
    
    def log_print(msg):
        """Print both to console and file"""
        print(msg)
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    
    log_print("🚀 PROJECT-S CMD TESZT FÁJL KIMENETTEL")
    log_print("=" * 50)
    log_print(f"Időpont: {datetime.datetime.now()}")
    log_print(f"Output fájl: {output_file}")
    
    try:
        # ModelManager betöltés
        log_print("\n📦 ModelManager betöltés...")
        from integrations.model_manager import ModelManager
        mm = ModelManager()
        log_print("✅ ModelManager betöltve")
        
        # Command detection teszt
        log_print("\n🔍 Command Detection teszt...")
        from core.command_detector import detect_command_type
        
        test_commands = [
            "list files in current directory",
            "show current directory", 
            "what's the current time",
            "create a new file"
        ]
        
        for cmd in test_commands:
            cmd_type = detect_command_type(cmd)
            log_print(f"  📝 '{cmd}' -> {cmd_type}")
        
        # Egyszerű CMD teszt
        log_print("\n🚀 Egyszerű CMD teszt végrehajtás...")
        
        test_cmd = "show current directory"
        log_print(f"Teszt parancs: {test_cmd}")
        
        # Filename extraction
        filename = mm._extract_filename_from_query(test_cmd)
        log_print(f"📁 Filename extraction: {filename}")
        
        # Végrehajtás
        log_print("⚡ Végrehajtás...")
        result = await mm.execute_task_with_core_system(test_cmd)
        
        log_print("📊 EREDMÉNY:")
        log_print(f"  Status: {result.get('status', 'NINCS')}")
        log_print(f"  Command Type: {result.get('command_type', 'NINCS')}")
        log_print(f"  Command Action: {result.get('command_action', 'NINCS')}")
        
        if 'execution_result' in result:
            exec_result = result['execution_result']
            log_print(f"  Execution Status: {exec_result.get('status', 'NINCS')}")
            log_print(f"  Command: {exec_result.get('command', 'NINCS')}")
            if 'output' in exec_result:
                log_print(f"  Output: {str(exec_result['output'])[:500]}...")
        
        log_print("\n🎯 CMD TESZT BEFEJEZVE")
        log_print(f"📄 Teljes log: {output_file}")
        
    except Exception as e:
        log_print(f"❌ HIBA: {e}")
        import traceback
        log_print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(cmd_teszt_with_file_output())
