import subprocess
import asyncio

print("=== STANDALONE CMD TEST ===")

def test_subprocess_direct():
    """Test subprocess directly"""
    print("Testing subprocess.run directly...")
    try:
        result = subprocess.run("echo Hello Direct Test", shell=True, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        print(f"Output: '{result.stdout.strip()}'")
        print(f"Error: '{result.stderr.strip()}'")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_cmd_implementation():
    """Test the same implementation as in the CMD handler"""
    print("\nTesting CMD handler implementation...")
    try:
        cmd = "dir /b"
        print(f"Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        response = {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
        print(f"Status: {response['status']}")
        print(f"Return code: {response['return_code']}")
        print(f"Output length: {len(response['stdout'])} chars")
        print(f"Error length: {len(response['stderr'])} chars")
        
        if response['stdout']:
            lines = response['stdout'].strip().split('\n')
            print(f"First few files: {lines[:5]}")
            
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("Starting CMD tests...")
    
    # Test 1: Direct subprocess
    if test_subprocess_direct():
        print("✓ Direct subprocess test passed")
    else:
        print("✗ Direct subprocess test failed")
        return
    
    # Test 2: CMD handler implementation
    result = test_cmd_implementation()
    if result and result['return_code'] == 0:
        print("✓ CMD handler implementation test passed")
    else:
        print("✗ CMD handler implementation test failed")
        
    print("\n=== CMD TESTS COMPLETED ===")

if __name__ == "__main__":
    main()
