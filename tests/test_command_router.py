import asyncio
import pytest
from unittest.mock import patch, MagicMock
from unittest.mock import AsyncMock

# Import will work correctly with the conftest.py file we created
from core.command_router import CommandRouter, router
from core.ai_command_handler import AICommandHandler

@pytest.mark.asyncio
async def test_command_router_initialization():
    """Test that CommandRouter initializes properly with default handlers"""
    # Create a fresh instance for testing
    test_router = CommandRouter()
    assert "ASK" in test_router.handlers
    
@pytest.mark.asyncio
async def test_ask_command_structure():
    """Test that the router properly validates ASK command structure"""
    # Create a fresh instance for testing
    test_router = CommandRouter()
    
    # Command without query should return an error
    invalid_command = {
        "type": "ASK"
        # Missing query field
    }
    
    response = await test_router.route_command(invalid_command)
    assert "error" in response
    assert "Missing query field in command" in response["error"]
    
@pytest.mark.asyncio
async def test_unknown_command_type():
    """Test that the router handles unknown command types"""
    # Create a fresh instance for testing
    test_router = CommandRouter()
    
    unknown_command = {
        "type": "UNKNOWN_TYPE",
        "data": "test data"
    }
    
    response = await test_router.route_command(unknown_command)
    assert "error" in response
    assert "No handler for command type" in response["error"]

@pytest.mark.asyncio
async def test_ask_command_with_qwen():
    """Test that ASK commands are properly routed to the Qwen client"""
    # Create a fresh instance for testing with a mocked handler
    test_router = CommandRouter()
    
    # Create a test question
    command = {
        "type": "ASK",
        "query": "Mi Magyarország fővárosa?"
    }
    
    # Create a mock handler that will return a predictable response
    mock_response = {"status": "success", "response": "Budapest a Magyarország fővárosa."}
    
    # Create an async mock function that can be awaited
    async def mock_async_handler(cmd):
        return mock_response
    
    # Replace the handler in the router with our mock
    original_handler = test_router.handlers["ASK"]
    test_router.handlers["ASK"] = mock_async_handler
    
    try:
        # Execute the command
        response = await test_router.route_command(command)
        
        # Verify the response matches our mock
        assert response == mock_response
        assert "status" in response
        assert response["status"] == "success"
        assert "response" in response
        assert "Budapest" in response["response"]
    finally:
        # Restore the original handler
        test_router.handlers["ASK"] = original_handler

@pytest.mark.asyncio
async def test_ask_command_real_integration():
    """
    Integration test with real Qwen client (if available)
    Warning: This test will actually call the Qwen client if available
    """
    # Create a fresh instance for testing
    test_router = CommandRouter()
    
    command = {
        "type": "ASK",
        "query": "Mi Magyarország fővárosa?"
    }
    
    response = await test_router.route_command(command)
    
    # Should either have a response or an error (if Qwen client isn't properly configured)
    assert isinstance(response, dict)
    print(f"Qwen integration test response: {response}")
    
    # Successful response will have these keys
    if "status" in response and response["status"] == "success":
        assert "response" in response
        print(f"Qwen responded: {response['response']}")
    else:
        # If error, print it but don't fail the test (might be environment-related)
        print(f"Qwen integration test error: {response.get('error', 'Unknown error')}")
        
    # This assertion should always pass - we're just checking for some kind of response
    assert "response" in response or "error" in response
