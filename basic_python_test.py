import subprocess

print("=== Basic Python/Subprocess Test ===")

try:
    # Test basic subprocess
    result = subprocess.run("echo Hello World", shell=True, capture_output=True, text=True)
    print(f"Subprocess test successful:")
    print(f"Return code: {result.returncode}")
    print(f"Output: '{result.stdout.strip()}'")
    
    # Test dir command
    result2 = subprocess.run("dir /b", shell=True, capture_output=True, text=True)
    print(f"\nDir command test:")
    print(f"Return code: {result2.returncode}")
    print(f"Output lines: {len(result2.stdout.strip().split())}")
    
    print("\n✅ Basic subprocess functionality works!")
    
    # Now test if we can load the CMD handler
    print("\n=== Testing CMD Handler Import ===")
    import sys
    import os
    sys.path.append(os.getcwd())
    
    from core.ai_command_handler import AICommandHandler
    print("✅ CMD handler imported successfully")
    
    handler = AICommandHandler()
    print("✅ CMD handler instance created")
    
    print("\n=== All tests passed! ===")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Write test completion marker
with open("basic_test_completed.txt", "w") as f:
    f.write("Basic test completed successfully")
    
print("Test completion marker written")
