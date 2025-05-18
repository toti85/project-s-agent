"""
system_test.py
Quick script to verify core system functionality.
"""
import asyncio
from run import initialize_system
from core.central_executor import executor
from integrations.vscode_interface import vscode_interface

async def test_system():
    # Initialize the system
    await initialize_system()

    # Test command execution via central executor
    print("Submitting test command...")
    # Send a simple shell command through the cmd handler
    result = await executor.submit({
        "type": "cmd",
        "content": "echo 'Test command executed successfully'"
    })
    print("Command submitted, result placeholder:", result)

    # Test VSCode interface code generation
    print("Requesting code generation via VSCode interface...")
    code_result = await vscode_interface.generate_code(
        "Create a simple Python hello world function"
    )
    print("Code generation result:", code_result)

    return True

if __name__ == '__main__':
    asyncio.run(test_system())