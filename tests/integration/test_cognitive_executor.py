import pytest
import asyncio
from core.cognitive_core import cognitive_core
from core.central_executor import executor

@pytest.mark.asyncio
async def test_cognitive_core_command_submission():
    """Test that the cognitive core submits commands to the executor."""
    # Create a test event
    test_event = {
        "type": "command",
        "command": {
            "type": "test_command",
            "content": "test content"
        }
    }

    # Track if the command was submitted
    command_submitted = False

    # Mock the executor's submit method
    original_submit = executor.submit

    async def mock_submit(command):
        nonlocal command_submitted
        command_submitted = True
        assert command["type"] == "test_command"
        assert command["content"] == "test content"

    executor.submit = mock_submit

    try:
        # Process the event through the cognitive core
        await cognitive_core.process_event(test_event)

        # Allow the event to be processed
        await asyncio.sleep(0.1)

        # Check that the command was submitted
        assert command_submitted
    finally:
        # Restore the original submit method
        executor.submit = original_submit

@pytest.mark.asyncio
async def test_cognitive_core_error_handling():
    """Test that the cognitive core handles errors properly."""
    # Create a test error event
    test_event = {
        "type": "error",
        "error": "Test error occurred"
    }

    # Track if the error handling command was submitted
    error_handled = False

    # Mock the executor's submit method
    original_submit = executor.submit

    async def mock_submit(command):
        nonlocal error_handled
        error_handled = True
        assert command["type"] == "system"
        assert command["command"] == "handle_error"
        assert command["error"] == "Test error occurred"

    executor.submit = mock_submit

    try:
        # Process the error event through the cognitive core
        await cognitive_core.process_event(test_event)

        # Allow the event to be processed
        await asyncio.sleep(0.1)

        # Check that the error handling command was submitted
        assert error_handled
    finally:
        # Restore the original submit method
        executor.submit = original_submit