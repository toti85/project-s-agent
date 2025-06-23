"""
Comprehensive End-to-End Tests for Project-S Hybrid System
------------------------------------------------------
This module provides end-to-end tests for the complete Project-S hybrid system,
including LangGraph workflows, system operations, and external integrations.
"""
import os
import sys
import pytest
import asyncio
import json
import uuid
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
from unittest import mock

# Import test configuration and framework
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
from test_framework import TestCase, TestSuite, TestResult
from langgraph_mock_objects import setup_mock_langgraph_environment
from mock_objects import setup_mock_environment, MockLLMClient, MockWebAccess

# Import Project-S components
from integrations.system_operations_manager import system_operations_manager
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from integrations.langgraph_integration import LangGraphIntegrator
from core.event_bus import event_bus
from core.model_selector import model_selector
from core.web_access import web_access
from core.central_executor import central_executor
from core.cognitive_core import cognitive_core


class CompleteSystemE2ETestCase(TestCase):
    """Complete system end-to-end test case"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="Complete System E2E",
            description="Tests the complete Project-S system including all components"
        )
        self.test_dir = None
        self.events_captured = []
    
    def _capture_event(self, event_data):
        """Event bus callback to capture events"""
        self.events_captured.append(event_data)
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create test directory
        self.test_dir = os.path.join(TEST_OUTPUT_DIR, f"e2e_test_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Subscribe to events
        event_bus.subscribe("file.read", self._capture_event)
        event_bus.subscribe("file.write", self._capture_event)
        event_bus.subscribe("process.execute", self._capture_event)
        event_bus.subscribe("config.load", self._capture_event)
        
        # Set up mocks
        self.mock_model = MockLLMClient()
        self.mock_web = MockWebAccess()
        
        # Create test files
        self.test_file = os.path.join(self.test_dir, "test_input.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test file for end-to-end testing.\n")
            f.write("It contains multiple lines to process.\n")
            f.write("The system should be able to handle this content.\n")
        
        self.test_config = os.path.join(self.test_dir, "test_config.json")
        with open(self.test_config, "w") as f:
            json.dump({
                "name": "e2e_test_config",
                "settings": {
                    "test_mode": True,
                    "model": "test-model",
                    "max_tokens": 100
                }
            }, f, indent=2)
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        results = {}
        
        # 1. Test file operations
        test_logger.info("Testing file operations...")
        
        # Read test file
        read_result = await file_system_operations.read_file(self.test_file)
        results["file_read"] = read_result["success"]
        
        # Write processed file
        processed_content = read_result["content"].upper()  # Simple transformation
        write_result = await file_system_operations.write_file(
            file_path=os.path.join(self.test_dir, "processed_output.txt"),
            content=processed_content
        )
        results["file_write"] = write_result["success"]
        
        # List directory
        list_result = await file_system_operations.list_directory(self.test_dir)
        results["file_list"] = list_result["success"]
        
        # 2. Test configuration operations
        test_logger.info("Testing configuration operations...")
        
        # Load config
        config_result = await config_operations.load_config(self.test_config)
        results["config_load"] = config_result["success"]
        
        # Update config
        config_data = config_result["config"]
        config_data["settings"]["updated"] = True
        update_result = await config_operations.update_config(self.test_config, config_data)
        results["config_update"] = update_result["success"]
        
        # 3. Test process operations (with safe command)
        test_logger.info("Testing process operations...")
        
        # Execute a safe process
        if os.name == "nt":  # Windows
            command = "echo Process test successful"
        else:  # Linux/Mac
            command = ["echo", "Process test successful"]
            
        process_result = await process_operations.execute_process(command)
        results["process_execute"] = process_result["success"]
        
        # 4. Test LangGraph integration
        test_logger.info("Testing LangGraph integration...")
        
        # Create a workflow
        with mock.patch("integrations.system_operations_manager.StateGraph"):
            workflow = system_operations_manager.create_file_operations_workflow("e2e_test_workflow")
            results["workflow_created"] = workflow is not None
        
        # 5. Test with mock LLM
        test_logger.info("Testing LLM integration...")
        
        with mock.patch("core.model_selector.get_model_by_task") as mock_get_model:
            mock_get_model.return_value = self.mock_model
            
            # Simple model call
            model = await model_selector.get_model_by_task("general")
            response = await model.generate("Generate a test response")
            results["model_response"] = response is not None
        
        # 6. Test with mock web access
        test_logger.info("Testing web access integration...")
        
        with mock.patch("core.web_access.search") as mock_search:
            mock_search.return_value = [
                {"title": "Test Result 1", "link": "https://example.com/1", "snippet": "Example 1"},
                {"title": "Test Result 2", "link": "https://example.com/2", "snippet": "Example 2"}
            ]
            
            # Web search
            search_results = await web_access.search("test query")
            results["web_search"] = len(search_results) > 0
        
        # 7. Verify event bus integration
        results["events_captured"] = len(self.events_captured) > 0
        
        # Overall success
        all_operations_success = all([
            results.get("file_read", False),
            results.get("file_write", False),
            results.get("file_list", False),
            results.get("config_load", False),
            results.get("config_update", False),
            results.get("process_execute", False),
            results.get("workflow_created", False),
            results.get("model_response", False),
            results.get("web_search", False),
            results.get("events_captured", False)
        ])
        
        results["all_operations_success"] = all_operations_success
        
        return results
    
    async def teardown(self):
        """Clean up after test execution"""
        # Unsubscribe from events
        event_bus.unsubscribe("file.read", self._capture_event)
        event_bus.unsubscribe("file.write", self._capture_event)
        event_bus.unsubscribe("process.execute", self._capture_event)
        event_bus.unsubscribe("config.load", self._capture_event)
        
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


class TechnologyAnalysisWorkflowE2ETestCase(TestCase):
    """Technology analysis workflow end-to-end test case"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="Technology Analysis Workflow E2E",
            description="Tests the technology analysis workflow end-to-end"
        )
        self.output_dir = None
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create output directory
        self.output_dir = os.path.join(TEST_OUTPUT_DIR, f"tech_analysis_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up mocks
        self.mock_model = MockLLMClient()
        self.mock_web = MockWebAccess()
    
    @mock.patch("core.web_access.search")
    @mock.patch("core.model_selector.get_model_by_task")
    async def execute(self, mock_get_model, mock_search) -> Dict[str, Any]:
        """Execute the test case"""
        # Set up mocks
        mock_get_model.return_value = self.mock_model
        mock_search.return_value = [
            {"title": "LangGraph Overview", "link": "https://example.com/langgraph", "snippet": "LangGraph is a framework for building stateful, multi-actor applications with LLMs."},
            {"title": "LangGraph Tutorial", "link": "https://example.com/langgraph/tutorial", "snippet": "Learn how to build complex workflows with LangGraph."},
            {"title": "LangGraph vs Traditional Systems", "link": "https://example.com/langgraph/compare", "snippet": "Comparing LangGraph with traditional workflow systems."}
        ]
        
        # Import technology analysis workflow
        sys.path.append(os.path.join(Path(__file__).parent.parent, "examples"))
        
        try:
            from tech_analysis_workflow import TechAnalysisWorkflow
            
            # Create workflow instance
            workflow = TechAnalysisWorkflow(
                workflow_id=f"e2e_test_{uuid.uuid4().hex[:8]}",
                output_dir=self.output_dir
            )
            
            # Execute workflow
            technology = "LangGraph"
            result = await workflow.execute(technology=technology)
            
            # Verify workflow execution
            assert isinstance(result, dict), "Workflow result should be a dictionary"
            assert "workflow_id" in result, "Workflow result should contain workflow_id"
            assert "analysis" in result, "Workflow result should contain analysis"
            
            # Check for output files
            output_file = os.path.join(self.output_dir, f"{technology.lower()}_analysis.md")
            assert os.path.exists(output_file), f"Output file does not exist: {output_file}"
            
            # Read output file
            with open(output_file, "r") as f:
                output_content = f.read()
            
            return {
                "workflow_result": result,
                "output_file": output_file,
                "output_content": output_content,
                "success": True
            }
            
        except ImportError as e:
            test_logger.error(f"Failed to import tech_analysis_workflow: {e}")
            return {"success": False, "error": f"Import error: {str(e)}"}
        except Exception as e:
            test_logger.error(f"Error executing technology analysis workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def teardown(self):
        """Clean up after test execution"""
        # Remove test directory and files
        if self.output_dir and os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    test_logger.error(f"Error removing file {filepath}: {e}")
            
            try:
                os.rmdir(self.output_dir)
            except Exception as e:
                test_logger.error(f"Error removing directory {self.output_dir}: {e}")
        
        await super().teardown()


class CognitiveCoreLangGraphE2ETestCase(TestCase):
    """Cognitive Core with LangGraph end-to-end test case"""
    
    def __init__(self):
        """Initialize the test case"""
        super().__init__(
            name="Cognitive Core LangGraph E2E",
            description="Tests the Cognitive Core with LangGraph integration end-to-end"
        )
        self.output_dir = None
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create output directory
        self.output_dir = os.path.join(TEST_OUTPUT_DIR, f"cognitive_core_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create test file
        self.test_file = os.path.join(self.output_dir, "cognitive_input.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test input for the cognitive core.\n")
            f.write("It should process this content and generate a response.\n")
            f.write("The response should demonstrate reasoning capabilities.\n")
        
        # Set up mocks
        self.mock_model = MockLLMClient()
    
    @mock.patch("core.model_selector.get_model_by_task")
    @mock.patch("core.cognitive_core.cognitive_core_langgraph")
    async def execute(self, mock_cognitive_core, mock_get_model) -> Dict[str, Any]:
        """Execute the test case"""
        # Set up mocks
        mock_get_model.return_value = self.mock_model
        
        # Create a simple mock implementation
        class MockCognitiveCore:
            async def process_query(self, query, context=None):
                return {
                    "response": f"Processed query: {query}",
                    "reasoning": "This is mock reasoning for the test case.",
                    "confidence": 0.95
                }
            
            async def generate_workflow(self, task_description):
                return {
                    "workflow_id": f"mock_workflow_{uuid.uuid4().hex[:8]}",
                    "steps": [
                        {"name": "read_input", "type": "file_operation"},
                        {"name": "analyze", "type": "llm_operation"},
                        {"name": "generate_output", "type": "file_operation"}
                    ]
                }
        
        mock_cognitive_core.return_value = MockCognitiveCore()
        
        try:
            # Test query processing
            query = "Analyze the content of the test file and summarize it."
            query_result = await cognitive_core.process_query(query)
            
            # Test workflow generation
            workflow_result = await cognitive_core.generate_workflow(
                "Create a workflow that reads the test file, analyzes its content, and writes a summary."
            )
            
            # Write output file
            output_file = os.path.join(self.output_dir, "cognitive_output.json")
            with open(output_file, "w") as f:
                json.dump({
                    "query_result": query_result,
                    "workflow_result": workflow_result
                }, f, indent=2)
            
            return {
                "query_result": query_result,
                "workflow_result": workflow_result,
                "output_file": output_file,
                "success": True
            }
            
        except Exception as e:
            test_logger.error(f"Error executing cognitive core test: {e}")
            return {"success": False, "error": str(e)}
    
    async def teardown(self):
        """Clean up after test execution"""
        # Remove test directory and files
        if self.output_dir and os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                except Exception as e:
                    test_logger.error(f"Error removing file {filepath}: {e}")
            
            try:
                os.rmdir(self.output_dir)
            except Exception as e:
                test_logger.error(f"Error removing directory {self.output_dir}: {e}")
        
        await super().teardown()


# Run all E2E tests
async def run_e2e_tests():
    """Run all E2E tests"""
    # Create test suite
    suite = TestSuite(
        name="Project-S Hybrid System E2E Tests",
        description="End-to-end tests for the complete Project-S hybrid system"
    )
    
    # Add test cases
    suite.add_test_case(CompleteSystemE2ETestCase())
    suite.add_test_case(TechnologyAnalysisWorkflowE2ETestCase())
    suite.add_test_case(CognitiveCoreLangGraphE2ETestCase())
    
    # Run tests
    results = await suite.run_all()
    
    # Generate report
    report_path = suite.generate_report("html")
    test_logger.info(f"Test report generated: {report_path}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_e2e_tests())
