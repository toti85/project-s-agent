"""
Enhanced Performance Testing Framework for Project-S
------------------------------------------------
This module provides advanced performance testing and benchmarking
for the Project-S hybrid system components.
"""
import os
import sys
import asyncio
import time
import json
import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, TypeVar
from datetime import datetime
import tempfile
import gc
import psutil
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


class PerformanceMetrics:
    """Class for collecting and analyzing performance metrics"""
    
    def __init__(self):
        """Initialize metrics collection"""
        self.execution_times = []
        self.memory_usages = []
        self.cpu_usages = []
        self.timestamps = []
        self.labels = []
        self.start_time = None
        self.process = psutil.Process()
    
    def start_measurement(self):
        """Start performance measurement"""
        self.start_time = time.time()
        self.timestamps.append(self.start_time)
        
        # Collect initial memory and CPU usage
        memory_info = self.process.memory_info()
        self.memory_usages.append(memory_info.rss / 1024 / 1024)  # MB
        self.cpu_usages.append(self.process.cpu_percent())
    
    def record_metric(self, label: str):
        """Record a performance metric with a label"""
        current_time = time.time()
        execution_time = current_time - self.start_time
        
        self.execution_times.append(execution_time)
        self.timestamps.append(current_time)
        self.labels.append(label)
        
        # Collect memory and CPU usage
        memory_info = self.process.memory_info()
        self.memory_usages.append(memory_info.rss / 1024 / 1024)  # MB
        self.cpu_usages.append(self.process.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the performance metrics"""
        if not self.execution_times:
            return {
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": 0,
                "avg_memory": 0,
                "avg_cpu": 0
            }
        
        return {
            "total_time": sum(self.execution_times),
            "avg_time": sum(self.execution_times) / len(self.execution_times),
            "max_time": max(self.execution_times),
            "min_time": min(self.execution_times),
            "avg_memory": sum(self.memory_usages) / len(self.memory_usages),
            "avg_cpu": sum(self.cpu_usages) / len(self.cpu_usages)
        }
    
    def get_details(self) -> Dict[str, List]:
        """Get detailed performance metrics"""
        return {
            "execution_times": self.execution_times,
            "memory_usages": self.memory_usages,
            "cpu_usages": self.cpu_usages,
            "timestamps": self.timestamps,
            "labels": self.labels
        }
    
    def generate_charts(self, output_dir: str, prefix: str = "perf"):
        """Generate performance charts"""
        if not self.execution_times or not self.labels:
            test_logger.warning("No performance data to generate charts")
            return []
        
        chart_files = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Execution Time Chart
        plt.figure(figsize=(12, 6))
        plt.bar(self.labels, self.execution_times, color='skyblue')
        plt.title('Execution Time by Operation')
        plt.xlabel('Operation')
        plt.ylabel('Execution Time (s)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        time_chart_path = os.path.join(output_dir, f"{prefix}_execution_time.png")
        plt.savefig(time_chart_path)
        plt.close()
        chart_files.append(time_chart_path)
        
        # 2. Memory Usage Chart
        if len(self.memory_usages) > 1:
            plt.figure(figsize=(12, 6))
            plt.plot(self.memory_usages, marker='o', color='green')
            plt.title('Memory Usage Over Time')
            plt.xlabel('Measurement Point')
            plt.ylabel('Memory Usage (MB)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            memory_chart_path = os.path.join(output_dir, f"{prefix}_memory_usage.png")
            plt.savefig(memory_chart_path)
            plt.close()
            chart_files.append(memory_chart_path)
        
        # 3. CPU Usage Chart
        if len(self.cpu_usages) > 1:
            plt.figure(figsize=(12, 6))
            plt.plot(self.cpu_usages, marker='o', color='red')
            plt.title('CPU Usage Over Time')
            plt.xlabel('Measurement Point')
            plt.ylabel('CPU Usage (%)')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            cpu_chart_path = os.path.join(output_dir, f"{prefix}_cpu_usage.png")
            plt.savefig(cpu_chart_path)
            plt.close()
            chart_files.append(cpu_chart_path)
        
        return chart_files
    
    def generate_html_report(self, output_dir: str, title: str = "Performance Report", prefix: str = "perf") -> str:
        """Generate an HTML performance report"""
        # Generate charts first
        chart_files = self.generate_charts(output_dir, prefix)
        chart_paths = [os.path.basename(path) for path in chart_files]
        
        # Get summary metrics
        summary = self.get_summary()
        
        # Create HTML report
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".summary { background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "tr:nth-child(even) { background-color: #f9f9f9; }",
            ".chart { margin-top: 20px; text-align: center; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            "<div class='summary'>",
            "<h2>Summary</h2>",
            f"<p>Total Execution Time: {summary['total_time']:.2f}s</p>",
            f"<p>Average Execution Time: {summary['avg_time']:.2f}s</p>",
            f"<p>Maximum Execution Time: {summary['max_time']:.2f}s</p>",
            f"<p>Minimum Execution Time: {summary['min_time']:.2f}s</p>",
            f"<p>Average Memory Usage: {summary['avg_memory']:.2f} MB</p>",
            f"<p>Average CPU Usage: {summary['avg_cpu']:.2f}%</p>",
            "</div>"
        ]
        
        # Add charts
        for chart_path in chart_paths:
            html.append(f"<div class='chart'><img src='{chart_path}' alt='Performance Chart'></div>")
        
        # Add detailed metrics table
        html.extend([
            "<h2>Detailed Metrics</h2>",
            "<table>",
            "<tr><th>Operation</th><th>Execution Time (s)</th><th>Memory Usage (MB)</th><th>CPU Usage (%)</th></tr>"
        ])
        
        for i, label in enumerate(self.labels):
            html.append("<tr>")
            html.append(f"<td>{label}</td>")
            html.append(f"<td>{self.execution_times[i]:.4f}</td>")
            
            # Memory and CPU might have one more or one less entry
            memory_idx = min(i + 1, len(self.memory_usages) - 1)
            cpu_idx = min(i + 1, len(self.cpu_usages) - 1)
            
            html.append(f"<td>{self.memory_usages[memory_idx]:.2f}</td>")
            html.append(f"<td>{self.cpu_usages[cpu_idx]:.2f}</td>")
            html.append("</tr>")
        
        html.extend([
            "</table>",
            "</body>",
            "</html>"
        ])
        
        # Write HTML report
        report_path = os.path.join(output_dir, f"{prefix}_report.html")
        with open(report_path, "w") as f:
            f.write("\n".join(html))
        
        return report_path


# Performance testing decorator with detailed metrics
def measure_detailed_performance(func):
    """Decorator to measure detailed performance of a function"""
    async def wrapper(*args, **kwargs):
        # Set up metrics collection
        metrics = PerformanceMetrics()
        metrics.start_measurement()
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            exception = str(e)
            test_logger.error(f"Error in {func.__name__}: {exception}")
        
        # Record final metric
        metrics.record_metric(func.__name__)
        
        # Return result with metrics
        return {
            "result": result,
            "success": success,
            "metrics": metrics
        }
    
    return wrapper


class FileOperationsPerformanceTest(TestCase):
    """Performance test for file operations"""
    
    def __init__(self, file_size_kb: int = 100, num_operations: int = 10):
        """Initialize the test case"""
        super().__init__(
            name=f"File Operations Performance (Size: {file_size_kb}KB, Ops: {num_operations})",
            description=f"Performance test for file operations with {file_size_kb}KB files and {num_operations} operations"
        )
        self.file_size_kb = file_size_kb
        self.num_operations = num_operations
        self.test_dir = None
        self.metrics = PerformanceMetrics()
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create test directory
        self.test_dir = os.path.join(TEST_OUTPUT_DIR, f"file_perf_{self.file_size_kb}kb_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Generate test content
        self.content = "X" * (self.file_size_kb * 1024)
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        self.metrics.start_measurement()
        operation_results = {}
        
        # Test write operations
        write_files = []
        self.metrics.record_metric("setup")
        
        for i in range(self.num_operations):
            start_time = time.time()
            
            file_path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            write_result = await file_system_operations.write_file(file_path, self.content)
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            write_files.append(file_path)
            operation_results[f"write_{i}"] = {
                "success": write_result["success"],
                "time": operation_time
            }
        
        self.metrics.record_metric("write_operations")
        
        # Test read operations
        read_contents = []
        for i, file_path in enumerate(write_files):
            start_time = time.time()
            
            read_result = await file_system_operations.read_file(file_path)
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            if read_result["success"]:
                read_contents.append(read_result["content"])
            
            operation_results[f"read_{i}"] = {
                "success": read_result["success"],
                "time": operation_time
            }
        
        self.metrics.record_metric("read_operations")
        
        # Test list operations
        list_result = await file_system_operations.list_directory(self.test_dir)
        self.metrics.record_metric("list_operation")
        
        # Generate performance charts
        charts = self.metrics.generate_charts(
            output_dir=TEST_OUTPUT_DIR,
            prefix=f"file_ops_{self.file_size_kb}kb"
        )
        
        # Generate HTML report
        report_path = self.metrics.generate_html_report(
            output_dir=TEST_OUTPUT_DIR,
            title=f"File Operations Performance ({self.file_size_kb}KB files)",
            prefix=f"file_ops_{self.file_size_kb}kb"
        )
        
        return {
            "operation_results": operation_results,
            "metrics_summary": self.metrics.get_summary(),
            "charts": charts,
            "report": report_path
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


class LangGraphWorkflowPerformanceTest(TestCase):
    """Performance test for LangGraph workflows"""
    
    def __init__(self, workflow_complexity: str = "simple", num_iterations: int = 5):
        """Initialize the test case"""
        super().__init__(
            name=f"LangGraph Workflow Performance (Complexity: {workflow_complexity}, Iterations: {num_iterations})",
            description=f"Performance test for LangGraph workflow with {workflow_complexity} complexity and {num_iterations} iterations"
        )
        self.workflow_complexity = workflow_complexity
        self.num_iterations = num_iterations
        self.test_dir = None
        self.metrics = PerformanceMetrics()
    
    async def setup(self):
        """Set up the test environment"""
        await super().setup()
        
        # Create test directory
        self.test_dir = os.path.join(TEST_OUTPUT_DIR, f"workflow_perf_{self.workflow_complexity}_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Set up mocks
        self.mock_env = setup_mock_langgraph_environment()
        self.mock_model = MockLLMClient()
    
    @mock.patch("integrations.system_operations_manager.StateGraph")
    @mock.patch("core.model_selector.get_model_by_task")
    async def execute(self, mock_get_model, mock_state_graph) -> Dict[str, Any]:
        """Execute the test case"""
        # Set up mocks
        mock_get_model.return_value = self.mock_model
        mock_state_graph.return_value = self.mock_env["graph"]
        
        self.metrics.start_measurement()
        operation_results = {}
        
        # Create workflow
        start_time = time.time()
        workflow = system_operations_manager.create_file_operations_workflow(f"perf_workflow_{uuid.uuid4().hex[:8]}")
        end_time = time.time()
        workflow_creation_time = end_time - start_time
        
        operation_results["workflow_creation"] = {
            "success": workflow is not None,
            "time": workflow_creation_time
        }
        
        self.metrics.record_metric("workflow_creation")
        
        # Create test files for workflow operations
        test_files = []
        for i in range(self.num_iterations):
            file_path = os.path.join(self.test_dir, f"workflow_input_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Test content for workflow iteration {i}\n")
                f.write("Multiple lines of text\n" * 10)
            test_files.append(file_path)
        
        self.metrics.record_metric("files_creation")
        
        # Execute workflow iterations
        for i in range(self.num_iterations):
            start_time = time.time()
            
            # Create a simple state
            state = {
                "file_path": test_files[i],
                "operation": "read_and_process"
            }
            
            # For a more complex workflow, add more state and operations
            if self.workflow_complexity == "complex":
                state["additional_paths"] = test_files
                state["processing_level"] = "deep"
                state["model_parameters"] = {"temperature": 0.7, "max_tokens": 100}
                state["output_formats"] = ["text", "json"]
            
            # Execute workflow with state
            try:
                # Since we're using mocks, we need to simulate workflow execution
                # In a real test, we would call workflow.invoke(state)
                simulated_result = await self._simulate_workflow_execution(state)
                
                end_time = time.time()
                operation_time = end_time - start_time
                
                operation_results[f"workflow_execution_{i}"] = {
                    "success": True,
                    "time": operation_time,
                    "state_size": len(str(state))
                }
                
            except Exception as e:
                test_logger.error(f"Error executing workflow iteration {i}: {e}")
                operation_results[f"workflow_execution_{i}"] = {
                    "success": False,
                    "error": str(e)
                }
            
            self.metrics.record_metric(f"workflow_iteration_{i}")
        
        # Generate performance charts
        charts = self.metrics.generate_charts(
            output_dir=TEST_OUTPUT_DIR,
            prefix=f"workflow_{self.workflow_complexity}"
        )
        
        # Generate HTML report
        report_path = self.metrics.generate_html_report(
            output_dir=TEST_OUTPUT_DIR,
            title=f"LangGraph Workflow Performance ({self.workflow_complexity} complexity)",
            prefix=f"workflow_{self.workflow_complexity}"
        )
        
        return {
            "operation_results": operation_results,
            "metrics_summary": self.metrics.get_summary(),
            "charts": charts,
            "report": report_path
        }
    
    async def _simulate_workflow_execution(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate workflow execution with the given state"""
        # This simulates what a real workflow would do
        result_state = state.copy()
        
        # Read file content
        if "file_path" in state:
            try:
                read_result = await file_system_operations.read_file(state["file_path"])
                result_state["content"] = read_result["content"]
            except Exception as e:
                result_state["error"] = f"File read error: {str(e)}"
        
        # Process content
        if "content" in result_state:
            result_state["processed"] = f"Processed: {result_state['content'][:50]}..."
            
            # For complex workflows, do more processing
            if self.workflow_complexity == "complex" and "additional_paths" in state:
                additional_contents = []
                for path in state["additional_paths"][:3]:  # Limit to 3 for performance
                    try:
                        read_result = await file_system_operations.read_file(path)
                        additional_contents.append(read_result["content"])
                    except Exception:
                        pass
                
                result_state["additional_contents"] = additional_contents
                result_state["combined_length"] = sum(len(c) for c in additional_contents)
        
        # Write output
        output_path = os.path.join(self.test_dir, f"workflow_output_{uuid.uuid4().hex[:8]}.txt")
        try:
            write_result = await file_system_operations.write_file(
                file_path=output_path,
                content=result_state.get("processed", "No content processed")
            )
            result_state["output_path"] = output_path
            result_state["write_success"] = write_result["success"]
        except Exception as e:
            result_state["error"] = f"File write error: {str(e)}"
        
        return result_state
    
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


@measure_detailed_performance
async def benchmark_tool_registration():
    """Benchmark tool registration and execution"""
    results = []
    
    # Register tools
    start_time = time.time()
    
    # Define test tools
    async def test_tool_1(args):
        return {"result": f"Tool 1 executed with {args}", "status": "success"}
    
    async def test_tool_2(args):
        return {"result": f"Tool 2 executed with {args}", "status": "success"}
    
    async def test_tool_3(args):
        return {"result": f"Tool 3 executed with {args}", "status": "success"}
    
    # Register tools
    tool_ids = []
    tool_ids.append(tool_manager.register_tool("test_tool_1", test_tool_1))
    tool_ids.append(tool_manager.register_tool("test_tool_2", test_tool_2))
    tool_ids.append(tool_manager.register_tool("test_tool_3", test_tool_3))
    
    end_time = time.time()
    registration_time = end_time - start_time
    results.append({"operation": "tool_registration", "time": registration_time})
    
    # Execute tools
    start_time = time.time()
    
    tool_results = []
    tool_results.append(await tool_manager.execute_tool("test_tool_1", {"test": "value1"}))
    tool_results.append(await tool_manager.execute_tool("test_tool_2", {"test": "value2"}))
    tool_results.append(await tool_manager.execute_tool("test_tool_3", {"test": "value3"}))
    
    end_time = time.time()
    execution_time = end_time - start_time
    results.append({"operation": "tool_execution", "time": execution_time})
    
    # Unregister tools
    start_time = time.time()
    
    for tool_id in tool_ids:
        tool_manager.unregister_tool(tool_id)
    
    end_time = time.time()
    unregistration_time = end_time - start_time
    results.append({"operation": "tool_unregistration", "time": unregistration_time})
    
    return {
        "registration_time": registration_time,
        "execution_time": execution_time,
        "unregistration_time": unregistration_time,
        "tool_results": tool_results,
        "overall_time": registration_time + execution_time + unregistration_time
    }


@measure_detailed_performance
async def benchmark_event_bus():
    """Benchmark event bus performance"""
    results = []
    events_received = []
    
    # Define event handler
    def event_handler(event_data):
        events_received.append(event_data)
    
    # Subscribe to events
    event_types = ["test.event.1", "test.event.2", "test.event.3"]
    
    start_time = time.time()
    for event_type in event_types:
        event_bus.subscribe(event_type, event_handler)
    end_time = time.time()
    subscription_time = end_time - start_time
    results.append({"operation": "event_subscription", "time": subscription_time})
    
    # Publish events
    start_time = time.time()
    for i in range(100):
        event_type = event_types[i % len(event_types)]
        event_data = {"id": i, "type": event_type, "timestamp": time.time()}
        event_bus.publish(event_type, event_data)
    end_time = time.time()
    publish_time = end_time - start_time
    results.append({"operation": "event_publishing", "time": publish_time})
    
    # Unsubscribe from events
    start_time = time.time()
    for event_type in event_types:
        event_bus.unsubscribe(event_type, event_handler)
    end_time = time.time()
    unsubscription_time = end_time - start_time
    results.append({"operation": "event_unsubscription", "time": unsubscription_time})
    
    return {
        "subscription_time": subscription_time,
        "publish_time": publish_time,
        "unsubscription_time": unsubscription_time,
        "events_published": 100,
        "events_received": len(events_received),
        "overall_time": subscription_time + publish_time + unsubscription_time
    }


# Run all performance tests
async def run_performance_tests():
    """Run all performance tests"""
    # Create test suite
    suite = TestSuite(
        name="Project-S Performance Tests",
        description="Performance tests for Project-S hybrid system components"
    )
    
    # Add test cases
    suite.add_test_case(FileOperationsPerformanceTest(file_size_kb=10, num_operations=5))
    suite.add_test_case(FileOperationsPerformanceTest(file_size_kb=100, num_operations=5))
    suite.add_test_case(LangGraphWorkflowPerformanceTest(workflow_complexity="simple", num_iterations=3))
    suite.add_test_case(LangGraphWorkflowPerformanceTest(workflow_complexity="complex", num_iterations=2))
    
    # Run tests
    results = await suite.run_all()
    
    # Generate report
    report_path = suite.generate_report("html")
    test_logger.info(f"Test report generated: {report_path}")
    
    # Run benchmark tests
    test_logger.info("Running benchmark tests...")
    tool_benchmark = await benchmark_tool_registration()
    event_bus_benchmark = await benchmark_event_bus()
    
    # Generate benchmark reports
    metrics = tool_benchmark["metrics"]
    tool_report_path = metrics.generate_html_report(
        output_dir=TEST_OUTPUT_DIR,
        title="Tool Registration Benchmark",
        prefix="tool_benchmark"
    )
    
    metrics = event_bus_benchmark["metrics"]
    event_bus_report_path = metrics.generate_html_report(
        output_dir=TEST_OUTPUT_DIR,
        title="Event Bus Benchmark",
        prefix="event_bus_benchmark"
    )
    
    test_logger.info(f"Tool benchmark report generated: {tool_report_path}")
    test_logger.info(f"Event bus benchmark report generated: {event_bus_report_path}")
    
    return {
        "test_results": results,
        "benchmark_results": {
            "tool": tool_benchmark["result"],
            "event_bus": event_bus_benchmark["result"]
        }
    }


if __name__ == "__main__":
    asyncio.run(run_performance_tests())
