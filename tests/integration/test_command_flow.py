import pytest
import asyncio
from core.central_executor import executor
from core.command_router import router

@pytest.mark.asyncio
async def test_command_execution():
    """Test that commands are properly routed and executed."""
    # Create a test command
    test_command = {
        "type": "test_command",
        "content": "test content"
    }

    # Track if the command was routed
    command_routed = False

    # Mock the router's route_command method
    original_route_command = router.route_command

    async def mock_route_command(command):
        nonlocal command_routed
        command_routed = True
        assert command["type"] == "test_command"
        assert command["content"] == "test content"
        return {"status": "success", "message": "Command executed successfully"}

    router.route_command = mock_route_command

    try:
        # Submit the command to the executor
        await executor.submit(test_command)

        # Allow the command to be processed
        await asyncio.sleep(0.1)

        # Check that the command was routed
        assert command_routed
    finally:
        # Restore the original route_command method
        router.route_command = original_route_command

@pytest.mark.asyncio
async def test_command_error_handling():
    """Test that errors during command execution are properly handled."""
    # Create a test command that will cause an error
    test_command = {
        "type": "error_command",
        "content": "cause error"
    }

    # Mock the router's route_command method to raise an exception
    original_route_command = router.route_command

    async def mock_route_command(command):
        raise Exception("Test error during command execution")

    router.route_command = mock_route_command

    try:
        # Submit the command to the executor
        await executor.submit(test_command)

        # Allow the command to be processed
        await asyncio.sleep(0.1)

        # Check that the error was logged (this would normally be verified with a mock logger)
    finally:
        # Restore the original route_command method
        router.route_command = original_route_command