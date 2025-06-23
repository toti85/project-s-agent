import sys
import os
import asyncio

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from core.ai_command_handler import AICommandHandler
    print("✓ CMD handler imported successfully")
    
    handler = AICommandHandler()
    print("✓ CMD handler instance created")
    
    async def test_cmd_handler():
        # Test with simple echo command
        test_command = {"cmd": "echo Test CMD Handler"}
        result = await handler.handle_cmd_command(test_command)
        
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Return code: {result.get('return_code', 'unknown')}")
        print(f"Output: {result.get('stdout', 'no output')}")
        
        if result.get('stderr'):
            print(f"Error: {result.get('stderr')}")
            
        return result
    
    # Run the test
    result = asyncio.run(test_cmd_handler())
    print("✅ CMD handler test completed successfully!")
    
    # Test with dir command
    print("\nTesting with 'dir' command:")
    dir_result = asyncio.run(handler.handle_cmd_command({"cmd": "dir /b"}))
    print(f"Dir status: {dir_result.get('status')}")
    print(f"Dir return code: {dir_result.get('return_code')}")
    print(f"Dir output length: {len(dir_result.get('stdout', ''))}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
