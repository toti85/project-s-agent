"""
Testing Framework for Project-S Hybrid System
-------------------------------------------
This module provides a unified framework for testing the Project-S hybrid system,
including support for unit tests, integration tests, end-to-end tests,
mock objects, and performance tests.
"""
import os
import sys
import asyncio
import logging
import json
import time
import pytest
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, Generic
from unittest import mock
import matplotlib.pyplot as plt

# Import test configuration
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
from mock_objects import setup_mock_environment, MockLLMClient, MockWebAccess

# Type variables for test results
T = TypeVar('T')

class TestResult(Generic[T]):
    """Base class for test results"""
    def __init__(
        self, 
        name: str, 
        success: bool, 
        result: Optional[T] = None, 
        error: Optional[Exception] = None,
        execution_time: float = 0.0
    ):
        self.name = name
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary"""
        return {
            "name": self.name,
            "success": self.success,
            "result": self.result,
            "error": str(self.error) if self.error else None,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }

class TestCase:
    """Base class for test cases"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.setup_complete = False
    
    async def setup(self) -> None:
        """Setup method called before execution"""
        self.setup_complete = True
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the test case"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    async def teardown(self) -> None:
        """Teardown method called after execution"""
        pass
    
    async def run(self) -> TestResult:
        """Run the complete test case with setup and teardown"""
        start_time = time.time()
        
        try:
            await self.setup()
            result = await self.execute()
            success = True
        except Exception as e:
            result = None
            success = False
            error = e
        finally:
            await self.teardown()
        
        execution_time = time.time() - start_time
        
        if success:
            return TestResult(self.name, True, result, None, execution_time)
        else:
            return TestResult(self.name, False, None, error, execution_time)

class TestSuite:
    """A collection of test cases"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
    
    def add_test_case(self, test_case: TestCase) -> None:
        """Add a test case to the suite"""
        self.test_cases.append(test_case)
    
    async def run_all(self) -> List[TestResult]:
        """Run all test cases in the suite"""
        self.results = []
        
        for test_case in self.test_cases:
            test_logger.info(f"Running test case: {test_case.name}")
            result = await test_case.run()
            self.results.append(result)
            
            status = "PASS" if result.success else "FAIL"
            test_logger.info(f"Test case {test_case.name}: {status} ({result.execution_time:.2f}s)")
        
        return self.results
    
    def generate_report(self, output_format: str = "text") -> str:
        """Generate a test report"""
        if output_format == "text":
            return self._generate_text_report()
        elif output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_text_report(self) -> str:
        """Generate a text test report"""
        report = [
            f"Test Suite: {self.name}",
            f"Description: {self.description}",
            f"Total Tests: {len(self.test_cases)}",
            f"Passed: {sum(1 for r in self.results if r.success)}",
            f"Failed: {sum(1 for r in self.results if not r.success)}",
            "\nResults:",
        ]
        
        for result in self.results:
            status = "PASS" if result.success else "FAIL"
            report.append(f"  {result.name}: {status} ({result.execution_time:.2f}s)")
            if not result.success and result.error:
                report.append(f"    Error: {result.error}")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON test report"""
        report_data = {
            "name": self.name,
            "description": self.description,
            "total_tests": len(self.test_cases),
            "passed": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "results": [r.to_dict() for r in self.results]
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self) -> str:
        """Generate an HTML test report"""
        passed = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        
        # Create basic charts using matplotlib
        plt.figure(figsize=(8, 4))
        plt.pie([passed, failed], labels=['Passed', 'Failed'], colors=['#4CAF50', '#F44336'], autopct='%1.1f%%')
        plt.title('Test Results')
        
        chart_path = os.path.join(TEST_OUTPUT_DIR, f"{self.name}_chart.png")
        plt.savefig(chart_path)
        
        # Create HTML report
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Test Report: {self.name}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".summary { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }",
            ".pass { color: #4CAF50; }",
            ".fail { color: #F44336; }",
            "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "tr:nth-child(even) { background-color: #f9f9f9; }",
            ".chart { margin-top: 20px; text-align: center; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Test Report: {self.name}</h1>",
            f"<p>{self.description}</p>",
            "<div class='summary'>",
            f"<p>Total Tests: {len(self.test_cases)}</p>",
            f"<p>Passed: <span class='pass'>{passed}</span></p>",
            f"<p>Failed: <span class='fail'>{failed}</span></p>",
            "</div>",
            "<div class='chart'>",
            f"<img src='{os.path.basename(chart_path)}' alt='Test Results Chart'>",
            "</div>",
            "<h2>Results:</h2>",
            "<table>",
            "<tr><th>Test Case</th><th>Status</th><th>Execution Time</th><th>Details</th></tr>"
        ]
        
        for result in self.results:
            status = "PASS" if result.success else "FAIL"
            status_class = "pass" if result.success else "fail"
            details = f"Error: {result.error}" if not result.success and result.error else ""
            
            html.append(f"<tr>")
            html.append(f"<td>{result.name}</td>")
            html.append(f"<td class='{status_class}'>{status}</td>")
            html.append(f"<td>{result.execution_time:.2f}s</td>")
            html.append(f"<td>{details}</td>")
            html.append(f"</tr>")
        
        html.extend([
            "</table>",
            "</body>",
            "</html>"
        ])
        
        html_content = "\n".join(html)
        
        # Save the HTML report
        report_path = os.path.join(TEST_OUTPUT_DIR, f"{self.name}_report.html")
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return report_path

# Decorator for performance measurement
def performance_test(iterations: int = 1):
    """Decorator for performance testing"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            times = []
            results = []
            
            for i in range(iterations):
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                times.append(execution_time)
                results.append(result)
                
                test_logger.debug(f"Performance test iteration {i+1}/{iterations}: {execution_time:.4f}s")
            
            avg_time = sum(times) / len(times)
            test_logger.info(f"Average execution time ({iterations} iterations): {avg_time:.4f}s")
            
            return {
                "results": results,
                "times": times,
                "average_time": avg_time,
                "min_time": min(times),
                "max_time": max(times)
            }
        
        return wrapper
    
    return decorator

# Main test runner
async def run_test_suites(suites: List[TestSuite], output_format: str = "text") -> Dict[str, Any]:
    """Run multiple test suites and generate a combined report"""
    all_results = {}
    
    for suite in suites:
        test_logger.info(f"Running test suite: {suite.name}")
        results = await suite.run_all()
        report = suite.generate_report(output_format)
        
        all_results[suite.name] = {
            "results": [r.to_dict() for r in results],
            "report": report
        }
        
        test_logger.info(f"Completed test suite: {suite.name}")
        test_logger.info(f"Passed: {sum(1 for r in results if r.success)}/{len(results)}")
    
    return all_results
