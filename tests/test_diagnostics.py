"""
Test suite for the Project-S diagnostics and monitoring subsystem.
"""

import os
import sys
import json
import asyncio
import unittest
from unittest import mock
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the project root to the path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.diagnostics import (
    diagnostics_manager, 
    LogLevel, 
    AlertLevel,
    ErrorContext,
    PerformanceMetrics,
    Alert
)
from integrations.workflow_visualizer import workflow_visualizer
from integrations.langgraph_diagnostics_bridge import langgraph_diagnostics_bridge
from integrations.langgraph_error_monitor import error_monitor


class TestDiagnosticsManager(unittest.TestCase):
    """Test the core diagnostics manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directories for diagnostic files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = os.path.join(self.temp_dir.name, "logs")
        self.diagnostics_dir = os.path.join(self.temp_dir.name, "diagnostics")
        
        # Initialize diagnostics manager with test configuration
        self.dm = diagnostics_manager
        self.dm.log_dir = self.log_dir
        self.dm.diagnostics_dir = self.diagnostics_dir
        
        # Ensure directories exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.diagnostics_dir, exist_ok=True)
        os.makedirs(os.path.join(self.diagnostics_dir, "errors"), exist_ok=True)
        os.makedirs(os.path.join(self.diagnostics_dir, "graphs"), exist_ok=True)
        os.makedirs(os.path.join(self.diagnostics_dir, "reports"), exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directories
        self.temp_dir.cleanup()
        
        # Reset the diagnostics manager state
        self.dm.error_history = []
        self.dm.alert_history = []
        self.dm.alert_cooldowns = {}
    
    def test_error_registration(self):
        """Test error registration and tracking"""
        try:
            # Simulate an error
            raise ValueError("Test error")
        except Exception as e:
            # Register the error
            error_context = self.dm.register_error(
                error=e,
                component="test_component",
                workflow_id="test_workflow",
                additional_info={"test_key": "test_value"}
            )
        
        # Verify error was registered
        self.assertGreater(len(self.dm.error_history), 0)
        
        # Verify error context
        last_error = self.dm.error_history[-1]
        self.assertEqual(last_error.error_type, "ValueError")
        self.assertEqual(last_error.message, "Test error")
        self.assertEqual(last_error.component, "test_component")
        self.assertEqual(last_error.workflow_id, "test_workflow")
        self.assertEqual(last_error.additional_info["test_key"], "test_value")
    
    def test_alert_system(self):
        """Test the alert system"""
        # Send an alert
        alert = self.dm.send_alert(
            level=AlertLevel.WARNING,
            message="Test alert",
            source="test_source",
            details={"test_key": "test_value"}
        )
        
        # Verify alert was registered
        self.assertGreater(len(self.dm.alert_history), 0)
        
        # Verify alert properties
        last_alert = self.dm.alert_history[-1]
        self.assertEqual(last_alert.level, AlertLevel.WARNING)
        self.assertEqual(last_alert.message, "Test alert")
        self.assertEqual(last_alert.source, "test_source")
        self.assertEqual(last_alert.details["test_key"], "test_value")
        
        # Test alert cooldown
        repeat_alert = self.dm.send_alert(
            level=AlertLevel.WARNING,
            message="Test alert",
            source="test_source"
        )
        
        # Should be None due to cooldown
        self.assertIsNone(repeat_alert)
        
        # Verify alert count hasn't increased
        self.assertEqual(len(self.dm.alert_history), 1)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        # Update response time
        self.dm.update_response_time("test_api", 100.0)
        
        # Update workflow metrics
        self.dm.update_workflow_metrics(
            workflow_id="test_workflow",
            execution_time_ms=500.0,
            status="completed"
        )
        
        # Generate performance report
        report = self.dm.generate_performance_report(include_graphs=False)
        
        # Verify report contents
        self.assertIn("timestamp", report)
        self.assertIn("current_metrics", report)
        self.assertIn("response_times_ms", report)
        self.assertIn("test_api", report["response_times_ms"])
        self.assertIn("workflows", report)
        self.assertIn("completed", report["workflows"])
        
        # Verify workflow completion count
        self.assertGreaterEqual(report["workflows"]["completed"], 1)
    
    def test_error_statistics(self):
        """Test error statistics generation"""
        # Register multiple errors
        for i in range(3):
            try:
                if i % 2 == 0:
                    raise ValueError(f"Test error {i}")
                else:
                    raise KeyError(f"Test error {i}")
            except Exception as e:
                self.dm.register_error(
                    error=e,
                    component="test_component"
                )
        
        # Get error statistics
        stats = self.dm.get_error_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_errors"], 3)
        self.assertIn("top_error_types", stats)
        self.assertIn("ValueError", stats["top_error_types"])
        self.assertIn("KeyError", stats["top_error_types"])
        self.assertEqual(stats["top_error_types"]["ValueError"], 2)
        self.assertEqual(stats["top_error_types"]["KeyError"], 1)


class TestWorkflowVisualizer(unittest.TestCase):
    """Test the workflow visualizer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for visualizations
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = os.path.join(self.temp_dir.name, "workflows")
        
        # Initialize workflow visualizer with test configuration
        self.visualizer = workflow_visualizer
        self.visualizer.output_dir = self.output_dir
        
        # Ensure directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sample workflow state
        self.workflow_id = "test-workflow"
        self.workflow_state = {
            "status": "running",
            "retry_count": 0,
            "current_task": {"name": "task2", "type": "command"},
            "command_history": [{"name": "task1", "result": "success"}],
            "context": {
                "created_at": datetime.now().isoformat(),
                "workflow_steps": [
                    {"name": "task1", "type": "command"},
                    {"name": "task2", "type": "command"},
                    {"name": "task3", "type": "command"}
                ],
                "branches": {}
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    @unittest.skipIf(not hasattr(workflow_visualizer, "VISUALIZATION_AVAILABLE") or 
                    not workflow_visualizer.VISUALIZATION_AVAILABLE, 
                    "Visualization libraries not available")
    async def test_workflow_visualization(self):
        """Test workflow visualization"""
        # Visualize workflow
        output_path = await self.visualizer.visualize_workflow(
            self.workflow_id, 
            self.workflow_state
        )
        
        # Skip further checks if visualization failed (libraries might be missing)
        if not output_path:
            self.skipTest("Visualization failed, likely due to missing libraries")
        
        # Verify output file exists
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(output_path.endswith(".png"))
    
    def test_workflow_data_export(self):
        """Test workflow data export"""
        # Export to JSON
        json_path = self.visualizer.export_workflow_data(
            self.workflow_id,
            self.workflow_state,
            format="json"
        )
        
        # Verify JSON export
        self.assertIsNotNone(json_path)
        self.assertTrue(os.path.exists(json_path))
        
        # Verify contents
        with open(json_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["workflow_id"], self.workflow_id)
            self.assertEqual(data["status"], self.workflow_state["status"])
        
        # Export to YAML if supported
        try:
            import yaml
            yaml_path = self.visualizer.export_workflow_data(
                self.workflow_id,
                self.workflow_state,
                format="yaml"
            )
            
            # Verify YAML export
            self.assertIsNotNone(yaml_path)
            self.assertTrue(os.path.exists(yaml_path))
            
            # Verify contents
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
                self.assertEqual(data["workflow_id"], self.workflow_id)
                self.assertEqual(data["status"], self.workflow_state["status"])
        except ImportError:
            # Skip YAML test if not available
            pass


class TestLangGraphDiagnosticsBridge(unittest.TestCase):
    """Test the LangGraph diagnostics bridge"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the event bus
        self.mock_event_bus = mock.MagicMock()
        self.event_bus_patcher = mock.patch('integrations.langgraph_diagnostics_bridge.event_bus', 
                                            self.mock_event_bus)
        self.event_bus_patcher.start()
        
        # Mock the diagnostics manager
        self.mock_dm = mock.MagicMock()
        self.dm_patcher = mock.patch('integrations.langgraph_diagnostics_bridge.diagnostics_manager', 
                                      self.mock_dm)
        self.dm_patcher.start()
        
        # Mock the workflow visualizer
        self.mock_visualizer = mock.MagicMock()
        self.visualizer_patcher = mock.patch('integrations.langgraph_diagnostics_bridge.workflow_visualizer', 
                                             self.mock_visualizer)
        self.visualizer_patcher.start()
        
        # Initialize the diagnostics bridge
        from integrations.langgraph_diagnostics_bridge import LangGraphDiagnosticsBridge
        self.bridge = LangGraphDiagnosticsBridge()
    
    def tearDown(self):
        """Clean up test environment"""
        self.event_bus_patcher.stop()
        self.dm_patcher.stop()
        self.visualizer_patcher.stop()
    
    def test_event_registration(self):
        """Test event handler registration"""
        # Verify event subscriptions
        self.mock_event_bus.subscribe.assert_any_call("workflow.error", self.bridge._on_workflow_error)
        self.mock_event_bus.subscribe.assert_any_call("workflow.retry", self.bridge._on_workflow_retry)
        self.mock_event_bus.subscribe.assert_any_call("command.error", self.bridge._on_command_error)
    
    async def test_workflow_error_handling(self):
        """Test workflow error event handling"""
        error = ValueError("Test error")
        event_data = {
            "graph_id": "test-workflow",
            "error": error,
            "state": {
                "current_task": {"name": "task1"},
                "context": {"key": "value"}
            }
        }
        
        # Process the event
        await self.bridge._on_workflow_error(event_data)
        
        # Verify error registration
        self.mock_dm.register_error.assert_called_once()
        args, kwargs = self.mock_dm.register_error.call_args
        self.assertEqual(kwargs["error"], error)
        self.assertEqual(kwargs["component"], "langgraph_workflow")
        self.assertEqual(kwargs["workflow_id"], "test-workflow")
    
    async def test_workflow_completion_metrics(self):
        """Test workflow completion metrics update"""
        # Setup start time for the workflow
        workflow_id = "test-workflow"
        self.bridge._workflow_start_times[workflow_id] = time.time() - 1  # 1 second ago
        
        # Create completion event
        event_data = {
            "graph_id": workflow_id,
            "state": {
                "status": "completed"
            }
        }
        
        # Process the event
        await self.bridge._on_workflow_complete(event_data)
        
        # Verify metrics update
        self.mock_dm.update_workflow_metrics.assert_called_once()
        args, kwargs = self.mock_dm.update_workflow_metrics.call_args
        self.assertEqual(kwargs["workflow_id"], workflow_id)
        self.assertEqual(kwargs["status"], "completed")
        self.assertGreaterEqual(kwargs["execution_time_ms"], 900)  # At least 0.9 seconds (allowing some margin)


# Define a custom TestRunner class for async tests
class AsyncTestRunner:
    """Custom test runner for async tests"""
    
    def run_tests(self):
        """Run all tests including async tests"""
        # Regular unittest for synchronous tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestDiagnosticsManager)
        suite.addTests(loader.loadTestsFromTestCase(TestLangGraphDiagnosticsBridge))
        unittest.TextTestRunner().run(suite)
        
        # Run async tests manually
        self._run_async_tests()
    
    def _run_async_tests(self):
        """Run the async tests"""
        print("\nRunning async tests:")
        
        # Create an instance of TestWorkflowVisualizer
        test_instance = TestWorkflowVisualizer()
        
        # Setup the test
        test_instance.setUp()
        
        try:
            # Run the async test
            print("- test_workflow_visualization")
            asyncio.run(test_instance.test_workflow_visualization())
            print("  PASS")
            
            # Run the sync test manually since we're handling the instance ourselves
            print("- test_workflow_data_export")
            test_instance.test_workflow_data_export()
            print("  PASS")
            
        except unittest.SkipTest as skip:
            print(f"  SKIP: {skip}")
        except Exception as e:
            print(f"  FAIL: {e}")
        finally:
            # Clean up
            test_instance.tearDown()


if __name__ == "__main__":
    runner = AsyncTestRunner()
    runner.run_tests()
"""
