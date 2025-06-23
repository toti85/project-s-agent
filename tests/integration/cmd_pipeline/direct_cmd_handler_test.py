#!/usr/bin/env python3
"""
KÖZVETLEN CMD HANDLER TESZT
==========================
Közvetlenül teszteljük a CMD handler funkcionalitást
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def direct_cmd_handler_test():
    """Közvetlen CMD handler teszt"""
    
    print("🚀 KÖZVETLEN CMD HANDLER TESZT")
    print("=" * 50)
    
    try:
        # Import CMD handler
        from core.ai_command_handler import AICommandHandler
        ai_handler = AICommandHandler()
        print("✅ AICommandHandler betöltve")
        
        # Windows CMD parancsok tesztelése
        test_commands = [
            {"cmd": "dir"},                    # List directory
            {"cmd": "echo Hello World"},       # Echo test  
            {"cmd": "time /t"},               # Current time
            {"cmd": "cd"},                    # Current directory
        ]
        
        print("\n📋 CMD PARANCSOK TESZTELÉSE:")
        print("-" * 40)
        
        for i, cmd_dict in enumerate(test_commands, 1):
            cmd = cmd_dict['cmd']
            print(f"\n🔧 TESZT {i}: {cmd}")
            print("-" * 30)
            
            try:
                # Közvetlen CMD handler hívás
                result = await ai_handler.handle_cmd_command(cmd_dict)
                
                print(f"📊 Status: {result.get('status', 'NINCS')}")
                print(f"🔄 Return Code: {result.get('return_code', 'NINCS')}")
                
                if result.get('stdout'):
                    stdout = result['stdout'].strip()
                    print(f"📄 STDOUT: {stdout[:200]}...")
                    
                if result.get('stderr'):
                    stderr = result['stderr'].strip()
                    print(f"⚠️ STDERR: {stderr[:200]}...")
                    
                if result.get('error'):
                    print(f"❌ ERROR: {result['error']}")
                    
                if result.get('status') == 'success':
                    print("✅ SIKERES")
                else:
                    print("⚠️ PROBLÉMÁS")
                    
            except Exception as e:
                print(f"❌ HIBA: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎯 CMD HANDLER TESZT BEFEJEZVE")
        print("=" * 50)
        
        # Security Validation teszt
        print("\n🔒 BIZTONSÁGI VALIDÁCIÓ TESZT:")
        print("-" * 40)
        
        try:
            from tools.system_tools import CommandValidator
            
            test_security_commands = [
                "dir",
                "echo hello",
                "del important.txt",  # Should be blocked
                "format c:",         # Should be blocked
                "ls -la"             # Unix command 
            ]
            
            for cmd in test_security_commands:
                is_valid = CommandValidator.is_command_allowed(cmd)
                validation = CommandValidator.validate_command(cmd)
                
                status = "✅ ENGEDÉLYEZETT" if is_valid else "❌ TILTOTT"
                print(f"  📝 '{cmd}' -> {status}")
                if not validation['valid']:
                    print(f"      Indok: {validation['reason']}")
                    
        except Exception as e:
            print(f"❌ Biztonsági validáció hiba: {e}")
        
        print("\n🎯 TELJES TESZT BEFEJEZVE!")
        
    except Exception as e:
        print(f"❌ Kritikus hiba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(direct_cmd_handler_test())
