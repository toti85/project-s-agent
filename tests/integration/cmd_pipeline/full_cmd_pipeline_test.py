import sys
import os
import asyncio

print("=== TELJES CMD PIPELINE TESZT ===")

# Add project root to path
sys.path.insert(0, '.')

async def test_cmd_pipeline():
    try:
        from core.ai_command_handler import AICommandHandler
        print("✅ CMD handler import sikeres")
        
        ai_handler = AICommandHandler()
        print("✅ CMD handler példány létrehozva")
        
        # Teszt parancsok
        test_commands = [
            "dir",
            "echo Hello CMD Pipeline!",
            "ver",
            "time /t",
            "cd"        ]
        
        for i, cmd in enumerate(test_commands, 1):
            print(f"\n🧪 TESZT {i}: '{cmd}'")
            try:
                # A handle_cmd_command metódust hívjuk (helyes formátumban - dictionary)
                command_dict = {"cmd": cmd}
                result = await ai_handler.handle_cmd_command(command_dict)
                
                print(f"📊 Eredmény típus: {type(result)}")
                print(f"📋 Eredmény: {result}")
                
                # Ha dict, akkor részletezzük
                if isinstance(result, dict):
                    status = result.get('status', 'unknown')
                    return_code = result.get('return_code', 'unknown')
                    stdout = result.get('stdout', '')
                    stderr = result.get('stderr', '')
                    
                    print(f"   📈 Status: {status}")
                    print(f"   🔢 Return Code: {return_code}")
                    if stdout:
                        print(f"   📄 Output (first 100 chars): {stdout[:100]}...")
                    if stderr:
                        print(f"   ⚠️  Error: {stderr}")
                
                print("   ✅ TESZT SIKERES")
                
            except Exception as e:
                print(f"   ❌ TESZT HIBA: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎉 TELJES CMD PIPELINE TESZT BEFEJEZVE!")
        
    except Exception as e:
        print(f"❌ PIPELINE HIBA: {e}")
        import traceback
        traceback.print_exc()

# Async futtatás
if __name__ == "__main__":
    asyncio.run(test_cmd_pipeline())

print("=== TESZT VÉGE ===")
