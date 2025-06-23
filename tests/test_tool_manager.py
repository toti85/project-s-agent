"""
Tests for the Tool Management System
-----------------------------------
This module contains tests for the unified tool registration and management system.
"""
import pytest
import asyncio
from typing import Dict, Any
import os
import tempfile

from integrations.tool_manager import tool_manager, ToolResult
from integrations.example_tools import read_file, write_file, list_directory, web_search, execute_python


@pytest.fixture
def temp_file():
    """Create a temporary file for testing file operations."""
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
        f.write("Test content for tool manager tests.")
    try:
        yield f.name
    finally:
        if os.path.exists(f.name):
            os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a few test files inside
        with open(os.path.join(temp_dir, "test1.txt"), 'w') as f:
            f.write("Test file 1")
        with open(os.path.join(temp_dir, "test2.txt"), 'w') as f:
            f.write("Test file 2")
        with open(os.path.join(temp_dir, "data.json"), 'w') as f:
            f.write('{"key": "value"}')
        yield temp_dir


class TestToolRegistration:
    """Test tool registration."""
    
    def test_tool_listing(self):
        """Test listing registered tools."""
        # Get all tools
        all_tools = tool_manager.list_tools()
        assert len(all_tools) > 0
        
        # Check if our example tools are registered
        assert "read_file" in all_tools
        assert "web_search" in all_tools
        assert "execute_python" in all_tools
    
    def test_tool_categories(self):
        """Test tool categorization."""
        # Check file category
        file_tools = tool_manager.list_tools(category="file")
        assert "read_file" in file_tools
        assert "write_file" in file_tools
        assert "list_directory" in file_tools
        
        # Check web category
        web_tools = tool_manager.list_tools(category="web")
        assert "web_search" in web_tools
        assert "fetch_webpage" in web_tools
        
        # Tools should only appear in their own category
        assert "read_file" not in web_tools
        assert "web_search" not in file_tools
    
    def test_tool_metadata(self):
        """Test tool metadata extraction."""
        # Check metadata for read_file tool
        metadata = tool_manager.get_tool_metadata("read_file")
        assert metadata.name == "read_file"
        assert "Read the contents of a file" in metadata.description
        assert metadata.category == "file"
        assert "file" in metadata.tags
        assert metadata.is_dangerous is False
    
    def test_tool_schema(self):
        """Test tool schema generation."""
        # Check schema for web_search tool
        schema = tool_manager.get_tool_schema("web_search")
        assert schema["name"] == "web_search"
        assert "parameters" in schema
        
        # Check that the schema includes expected parameters
        parameters = schema["parameters"]["properties"]
        assert "query" in parameters
        assert "num_results" in parameters


class TestToolExecution:
    """Test tool execution."""
    
    @pytest.mark.asyncio
    async def test_read_file_tool(self, temp_file):
        """Test the read_file tool."""
        # Execute directly
        result = await read_file(temp_file)
        assert result["success"] is True
        assert "Test content" in result["content"]
        
        # Execute via tool manager
        result = await tool_manager.execute_tool("read_file", file_path=temp_file)
        assert result.success is True
        assert "Test content" in result.result["content"]
    
    @pytest.mark.asyncio
    async def test_write_file_tool(self, temp_file):
        """Test the write_file tool."""
        # Execute via tool manager
        test_content = "New content written by test"
        result = await tool_manager.execute_tool("write_file", file_path=temp_file, content=test_content)
        assert result.success is True
        
        # Verify the content was written
        with open(temp_file, 'r') as f:
            content = f.read()
        assert content == test_content
    
    @pytest.mark.asyncio
    async def test_list_directory_tool(self, temp_dir):
        """Test the list_directory tool."""
        # Execute via tool manager
        result = await tool_manager.execute_tool("list_directory", directory_path=temp_dir)
        assert result.success is True
        
        # Check that all test files are listed
        files = [f["name"] for f in result.result["files"]]
        assert "test1.txt" in files
        assert "test2.txt" in files
        assert "data.json" in files
    
    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        """Test the web_search tool (mock implementation)."""
        # Execute via tool manager
        result = await tool_manager.execute_tool("web_search", query="test query")
        assert result.success is True
        assert "results" in result.result
        assert len(result.result["results"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_python_tool(self):
        """Test the execute_python tool."""
        # Execute via tool manager with simple code
        code = "a = 5\nb = 7\nresult = a + b"
        result = await tool_manager.execute_tool("execute_python", code=code)
        assert result.success is True
        assert result.result["locals"]["result"] == 12
        
        # Test with code that prints
        code = "print('Hello from test')"
        result = await tool_manager.execute_tool("execute_python", code=code)
        assert result.success is True
        assert "Hello from test" in result.result["stdout"]
        
        # Test with code that raises an exception
        code = "1/0"
        result = await tool_manager.execute_tool("execute_python", code=code)
        assert result.success is False
        assert "division by zero" in result.error


class TestToolErrors:
    """Test tool error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_parameters(self):
        """Test tool execution with invalid parameters."""
        # Missing required parameter
        result = await tool_manager.execute_tool("read_file")
        assert result.success is False
        assert "Invalid parameters" in result.error
        
        # Invalid parameter type
        result = await tool_manager.execute_tool("web_search", query=123)  # Should be string
        assert result.success is False
        assert "Invalid parameters" in result.error
    
    @pytest.mark.asyncio
    async def test_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        result = await tool_manager.execute_tool("nonexistent_tool")
        assert result.success is False
        assert "Tool not found" in result.error


class TestLangGraphIntegration:
    """Test LangGraph integration."""
    
    def test_create_tool_node(self):
        """Test creating a ToolNode from a tool."""
        # Create a tool node
        tool_node = tool_manager.create_tool_node("read_file")
        assert tool_node is not None
    
    def test_create_all_tool_nodes(self):
        """Test creating ToolNodes for all tools in a category."""
        # Create tool nodes for file category
        tool_nodes = tool_manager.create_all_tool_nodes(category="file")
        assert len(tool_nodes) == 3  # read_file, write_file, list_directory
        assert "read_file" in tool_nodes
        assert "write_file" in tool_nodes
        assert "list_directory" in tool_nodes
        
        # Create tool nodes for all tools
        all_tool_nodes = tool_manager.create_all_tool_nodes()
        assert len(all_tool_nodes) > 3


class TestToolStatistics:
    """Test tool statistics tracking."""
    
    @pytest.mark.asyncio
    async def test_tool_stats_tracking(self):
        """Test tool usage statistics tracking."""
        # Get initial stats for a tool
        tool_name = "web_search"
        initial_stats = tool_manager.get_tool_stats(tool_name).copy()
        
        # Execute the tool
        await tool_manager.execute_tool(tool_name, query="test stats")
        
        # Get updated stats
        updated_stats = tool_manager.get_tool_stats(tool_name)
        
        # Check that calls increased by 1
        assert updated_stats["calls"] == initial_stats["calls"] + 1
        assert updated_stats["successes"] == initial_stats["successes"] + 1
        
        # Test stats reset
        tool_manager.reset_stats(tool_name)
        reset_stats = tool_manager.get_tool_stats(tool_name)
        assert reset_stats["calls"] == 0
        assert reset_stats["successes"] == 0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])