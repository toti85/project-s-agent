"""
Enhanced Integration Tests for Project-S
------------------------------------
This module tests the integration between LangGraph workflows and system operations.
"""
import os
import sys
import pytest
import asyncio
import json
import uuid
import tempfile
from typing import Dict, Any, List
from pathlib import Path
from unittest import mock

# Import test configuration and framework
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
from test_framework import TestCase, TestSuite, TestResult, performance_test
from langgraph_mock_objects import setup_mock_langgraph_environment
from mock_objects import setup_mock_environment, MockLLMClient

# Import Project-S components
from integrations.system_operations_manager import system_operations_manager
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from integrations.langgraph_integration import LangGraphIntegrator
from integrations.tool_manager import tool_manager
from core.event_bus import event_bus
from core.model_selector import model_selector
from core.web_access import web_access


class FileOperationsWorkflowTest(TestCase):
    """Test case for file operations workflow integration"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="File Operations Workflow Integration",
            description="Tests the integration between LangGraph workflow and file operations"
        )
        self.test_file = None
        self.test_dir = None
        self.workflow = None
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create test directory and files
        self.test_dir = os.path.join(TEST_OUTPUT_DIR, f"file_ops_test_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test file for the file operations workflow.\n")
            f.write("It contains multiple lines of text.\n")
            f.write("Line 3: Additional content.\n")
            f.write("Line 4: Final line of the test file.\n")
        
        # Create workflow
        self.workflow = system_operations_manager.create_file_operations_workflow(
            workflow_id=f"test_workflow_{uuid.uuid4().hex[:8]}"
        )
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        # Prepare initial state
        initial_state = {
            "file_path": self.test_file,
            "directory_path": self.test_dir,
            "operation": "read_and_transform"
        }
        
        # Mock the LangGraph execution
        with mock.patch("integrations.langgraph_integration.StateGraph") as mock_graph:
            # Set up graph mock to work with our test
            graph_instance = mock_graph.return_value
            
            # Track operations
            operations = []
            
            # Define the read operation
            async def file_read(state):
                operations.append("read")
                result = await file_system_operations.read_file(state["file_path"])
                return {**state, "file_content": result["content"]}
            
            # Define the transform operation
            async def transform(state):
                operations.append("transform")
                content = state.get("file_content", "")
                transformed = content.upper()  # Simple transformation
                return {**state, "transformed_content": transformed}
            
            # Define the write operation
            async def file_write(state):
                operations.append("write")
                output_path = os.path.join(self.test_dir, "output.txt")
                result = await file_system_operations.write_file(
                    file_path=output_path,
                    content=state.get("transformed_content", "")
                )
                return {**state, "output_path": output_path, "write_result": result["success"]}
            
            # Simulate the workflow execution
            graph_nodes = {
                "read": file_read,
                "transform": transform,
                "write": file_write
            }
            
            # Execute operations in sequence
            state = initial_state
            for op in ["read", "transform", "write"]:
                state = await graph_nodes[op](state)
            
            # Verify the output file exists and has the expected content
            output_path = state.get("output_path")
            assert os.path.exists(output_path), f"Output file does not exist: {output_path}"
            
            with open(output_path, "r") as f:
                content = f.read()
            
            assert content == state.get("transformed_content"), "Output file content doesn't match transformed content"
            
            # Return test results
            return {
                "operations": operations,
                "initial_state": initial_state,
                "final_state": state,
                "output_content": content
            }
    
    async def teardown(self):
        """Clean up after test execution"""
        # Remove test directory and files
        if self.test_dir and os.path.exists(self.test_dir):
            for filename in os.listdir(self.test_dir):
                filepath = os.path.join(self.test_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    test_logger.error(f"Error removing file {filepath}: {e}")
            
            try:
                os.rmdir(self.test_dir)
            except Exception as e:
                test_logger.error(f"Error removing directory {self.test_dir}: {e}")
        
        await super().teardown()


class ConfigSystemWorkflowTest(TestCase):
    """Test case for configuration system workflow integration"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="Configuration System Workflow Integration",
            description="Tests the integration between LangGraph workflow and configuration operations"
        )
        self.test_config_dir = None
        self.test_config_file = None
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create test directory and config file
        self.test_config_dir = os.path.join(TEST_OUTPUT_DIR, f"config_test_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # Create test config file
        self.test_config_file = os.path.join(self.test_config_dir, "test_config.json")
        test_config = {
            "name": "test_config",
            "description": "Test configuration for integration tests",
            "settings": {
                "setting1": "value1",
                "setting2": 42,
                "nested": {
                    "subsetting1": True,
                    "subsetting2": [1, 2, 3]
                }
            },
            "enabled_features": ["feature1", "feature2"]
        }
        
        with open(self.test_config_file, "w") as f:
            json.dump(test_config, f, indent=2)
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        # Define workflow steps
        operations = []
        
        # Step 1: Load configuration
        operations.append("load_config")
        load_result = await config_operations.load_config(self.test_config_file)
        assert load_result["success"], f"Failed to load config: {load_result.get('error')}"
        config_data = load_result["config"]
        
        # Step 2: Update configuration
        operations.append("update_config")
        config_data["settings"]["setting3"] = "new_value"
        config_data["enabled_features"].append("feature3")
        update_result = await config_operations.update_config(self.test_config_file, config_data)
        assert update_result["success"], f"Failed to update config: {update_result.get('error')}"
        
        # Step 3: Reload configuration to verify changes
        operations.append("verify_config")
        verify_result = await config_operations.load_config(self.test_config_file)
        assert verify_result["success"], f"Failed to reload config: {verify_result.get('error')}"
        updated_config = verify_result["config"]
        
        # Verify changes
        assert updated_config["settings"]["setting3"] == "new_value", "Config update failed"
        assert "feature3" in updated_config["enabled_features"], "Config update failed"
        
        # Return test results
        return {
            "operations": operations,
            "original_config": load_result["config"],
            "updated_config": updated_config
        }
    
    async def teardown(self):
        """Clean up after test execution"""
        # Remove test directory and files
        if self.test_config_dir and os.path.exists(self.test_config_dir):
            for filename in os.listdir(self.test_config_dir):
                filepath = os.path.join(self.test_config_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    test_logger.error(f"Error removing file {filepath}: {e}")
            
            try:
                os.rmdir(self.test_config_dir)
            except Exception as e:
                test_logger.error(f"Error removing directory {self.test_config_dir}: {e}")
        
        await super().teardown()


class ToolIntegrationWorkflowTest(TestCase):
    """Test case for tool integration with LangGraph workflows"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="Tool Integration Workflow",
            description="Tests the integration between LangGraph workflows and Project-S tools"
        )
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Set up mock environment
        self.mock_env = setup_mock_langgraph_environment()
        
        # Register mock tools
        self.tools = []
        
        # File operation tool
        async def file_tool(args):
            content = f"File tool executed with args: {args}"
            return {"result": content, "success": True}
        
        # Process operation tool
        async def process_tool(args):
            output = f"Process tool executed with args: {args}"
            return {"output": output, "exit_code": 0, "success": True}
        
        # Web operation tool
        async def web_tool(args):
            data = f"Web tool executed with args: {args}"
            return {"data": data, "status": 200, "success": True}
        
        # Register tools with the tool manager
        self.tool_ids = []
        self.tool_ids.append(tool_manager.register_tool("file_tool", file_tool))
        self.tool_ids.append(tool_manager.register_tool("process_tool", process_tool))
        self.tool_ids.append(tool_manager.register_tool("web_tool", web_tool))
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        # Create a simple workflow with tools
        tool_results = []
        
        # Execute file tool
        file_tool_args = {"path": "/test/path", "operation": "read"}
        file_tool_result = await tool_manager.execute_tool("file_tool", file_tool_args)
        tool_results.append(("file_tool", file_tool_result))
        
        # Execute process tool
        process_tool_args = {"command": "test_command", "args": ["--arg1", "--arg2"]}
        process_tool_result = await tool_manager.execute_tool("process_tool", process_tool_args)
        tool_results.append(("process_tool", process_tool_result))
        
        # Execute web tool
        web_tool_args = {"url": "https://example.com", "method": "GET"}
        web_tool_result = await tool_manager.execute_tool("web_tool", web_tool_args)
        tool_results.append(("web_tool", web_tool_result))
        
        # Verify all tools were executed successfully
        all_success = all(result.get("success", False) for _, result in tool_results)
        
        # Return test results
        return {
            "tool_results": tool_results,
            "all_success": all_success,
            "tool_ids": self.tool_ids
        }
    
    async def teardown(self):
        """Clean up after test execution"""
        # Unregister tools
        for tool_id in self.tool_ids:
            tool_manager.unregister_tool(tool_id)
        
        await super().teardown()


@performance_test(iterations=3)
async def test_langgraph_workflow_performance():
    """Performance test for LangGraph workflow execution"""
    # Set up test
    test_case = FileOperationsWorkflowTest()
    await test_case.setup()
    
    # Execute test
    result = await test_case.execute()
    
    # Clean up
    await test_case.teardown()
    
    return result


# Run all integration tests
async def run_integration_tests():
    """Run all integration tests"""
    # Create test suite
    suite = TestSuite(
        name="Project-S LangGraph Integration Tests",
        description="Tests the integration between LangGraph and Project-S components"
    )
    
    # Add test cases
    suite.add_test_case(FileOperationsWorkflowTest())
    suite.add_test_case(ConfigSystemWorkflowTest())
    suite.add_test_case(ToolIntegrationWorkflowTest())
    
    # Run tests
    results = await suite.run_all()
    
    # Generate report
    report_path = suite.generate_report("html")
    test_logger.info(f"Test report generated: {report_path}")
    
    # Also run performance test
    test_logger.info("Running performance tests...")
    perf_results = await test_langgraph_workflow_performance()
    test_logger.info(f"Performance test results: Average execution time: {perf_results['average_time']:.4f}s")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_integration_tests())
