import pytest
import asyncio
from typing import Dict, Any
from core.event_bus import event_bus
from core.central_executor import executor
from core.cognitive_core import cognitive_core

@pytest.fixture
async def setup_system():
    """Set up the event system for testing."""
    # Clear any existing subscriptions
    event_bus.subscribers = {}
    
    # Subscribe to test channels
    test_results = {}
    
    async def test_handler(event):
        channel = event.get("test_channel", "unknown")
        test_results[channel] = event
    
    event_bus.subscribe("test_channel", test_handler)
    
    yield test_results
    
    # Cleanup
    event_bus.subscribers = {}

@pytest.mark.asyncio
async def test_event_publishing(setup_system):
    """Test that events are properly published and received."""
    test_results = setup_system
    
    # Publish a test event
    test_event = {"test_channel": "channel1", "data": "test_data"}
    await event_bus.publish("test_channel", test_event)
    
    # Allow the event to be processed
    await asyncio.sleep(0.1)
    
    # Check that the event was received
    assert "channel1" in test_results
    assert test_results["channel1"]["data"] == "test_data"

@pytest.mark.asyncio
async def test_multiple_subscribers(setup_system):
    """Test that multiple subscribers can receive the same event."""
    test_results = setup_system
    
    # Create a second test result dict
    test_results2 = {}
    
    async def second_handler(event):
        channel = event.get("test_channel", "unknown")
        test_results2[channel] = event
    
    # Subscribe a second handler
    event_bus.subscribe("test_channel", second_handler)
    
    # Publish a test event
    test_event = {"test_channel": "channel2", "data": "multi_test"}
    await event_bus.publish("test_channel", test_event)
    
    # Allow the event to be processed
    await asyncio.sleep(0.1)
    
    # Check that both handlers received the event
    assert "channel2" in test_results
    assert test_results["channel2"]["data"] == "multi_test"
    assert "channel2" in test_results2
    assert test_results2["channel2"]["data"] == "multi_test"

@pytest.mark.asyncio
async def test_cognitive_core_event_processing():
    """Test that the cognitive core properly processes events."""
    # Create a test event
    test_event = {
        "type": "command",
        "command": {
            "type": "test",
            "content": "test content"
        }
    }
    
    # Track if the command was submitted
    command_submitted = False
    
    # Override the executor's submit method
    original_submit = executor.submit
    
    async def mock_submit(command):
        nonlocal command_submitted
        command_submitted = True
        assert command["type"] == "test"
        assert command["content"] == "test content"
    
    executor.submit = mock_submit
    
    try:
        # Publish the event
        await event_bus.publish("event_channel", test_event)
        
        # Allow the event to be processed
        await asyncio.sleep(0.1)
        
        # Check that the command was submitted
        assert command_submitted
    finally:
        # Restore the original submit method
        executor.submit = original_submit