import subprocess
import sys
import os
import time

print("=== CLI_MAIN.PY CMD INTEGRÁCIÓS TESZT ===")
print("Tesztelés a cli_main.py interfészen keresztül...")

# Test commands via cli_main.py
test_commands = [
    'dir',
    'echo "CLI Integration Test"',
    'ver',
    'time /t'
]

for i, cmd in enumerate(test_commands, 1):
    print(f"\n🧪 CLI TESZT {i}: python cli_main.py cmd {cmd}")
    
    start_time = time.time()
    
    try:
        # Execute through cli_main.py
        full_command = f'python cli_main.py cmd {cmd}'
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"   ⏱️  Végrehajtási idő: {execution_time:.3f}s")
        print(f"   🔢 Return code: {result.returncode}")
        
        if result.stdout:
            print(f"   📄 STDOUT (first 200 chars):")
            print(f"   {result.stdout[:200]}...")
            
        if result.stderr:
            print(f"   ⚠️  STDERR:")
            print(f"   {result.stderr}")
            
        if result.returncode == 0:
            print("   ✅ CLI TESZT SIKERES")
        else:
            print("   ❌ CLI TESZT HIBA")
            
    except subprocess.TimeoutExpired:
        print("   ⏰ TIMEOUT - CLI inicializálás túl hosszú")
    except Exception as e:
        print(f"   ❌ EXCEPTION: {e}")

print("\n🎉 CLI_MAIN.PY INTEGRÁCIÓS TESZT BEFEJEZVE!")
print("=== TESZT VÉGE ===")
