"""
Master Test Runner for Project-S
-----------------------------
This module provides a unified interface for running all types of tests
for the Project-S hybrid system.
"""
import os
import sys
import asyncio
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import test configuration and framework
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR

# Import test modules
import test_system_operations_unit
import test_system_langgraph_integration
import test_system_e2e
import test_langgraph_unit
import test_enhanced_integration
import test_comprehensive_e2e
import test_enhanced_performance


class TestReporter:
    """Class for generating unified test reports"""
    
    @staticmethod
    def generate_summary_report(test_results: Dict[str, Any], output_dir: str = TEST_OUTPUT_DIR) -> str:
        """Generate a summary report for all test runs"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare report data
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": test_results,
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 0
            }
        }
        
        # Compute summary statistics
        for test_type, results in test_results.items():
            if isinstance(results, dict) and "total_tests" in results:
                report_data["summary"]["total_tests"] += results["total_tests"]
                report_data["summary"]["passed_tests"] += results["passed_tests"]
                report_data["summary"]["failed_tests"] += results["failed_tests"]
                report_data["summary"]["error_tests"] += results.get("error_tests", 0)
        
        # Save JSON report
        json_path = os.path.join(output_dir, "master_test_report.json")
        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=2)
          # Generate HTML report
        html_path = os.path.join(output_dir, "master_test_report.html")
        html_content = TestReporter._generate_html_report(report_data)
        with open(html_path, "w") as f:
            f.write(html_content)
        
        return html_path
    
    @staticmethod
    def _generate_html_report(report_data: Dict[str, Any]) -> str:
        """Generate HTML content for the report"""
        # Calculate totals and success rate
        summary = report_data["summary"]
        total_tests = summary["total_tests"]
        passed_tests = summary["passed_tests"]
        failed_tests = summary["failed_tests"]
        error_tests = summary["error_tests"]
        
        success_rate = 0
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
        
        # Create HTML content
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Project-S Master Test Report</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            ".summary { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }",
            ".test-section { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }",
            ".test-section h2 { margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 10px; }",
            ".success { color: green; }",
            ".failure { color: red; }",
            ".warning { color: orange; }",
            ".progress-bar-container { width: 100%; background-color: #f3f3f3; border-radius: 5px; }",
            ".progress-bar { height: 24px; border-radius: 5px; line-height: 24px; color: white; text-align: center; }",
            ".progress-bar-success { background-color: #4CAF50; }",
            ".progress-bar-failure { background-color: #F44336; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "tr:nth-child(even) { background-color: #f9f9f9; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Project-S Hybrid System Test Report</h1>",
            f"<p>Generated on: {report_data['timestamp']}</p>",
            "<div class='summary'>",
            "<h2>Summary</h2>"
        ])
        
        # Add summary statistics
        html.extend([
            f"<p>Total Tests: <strong>{total_tests}</strong></p>",
            f"<p>Passed Tests: <strong class='success'>{passed_tests}</strong></p>",
            f"<p>Failed Tests: <strong class='failure'>{failed_tests}</strong></p>",
            f"<p>Error Tests: <strong class='warning'>{error_tests}</strong></p>",
            f"<p>Success Rate: <strong>{success_rate:.1f}%</strong></p>"
        ])
        
        # Add progress bar
        html.extend([
            "<div class='progress-bar-container'>",
            f"<div class='progress-bar progress-bar-success' style='width:{success_rate}%'>",
            f"{success_rate:.1f}%",
            "</div>",
            "</div>"
        ])
        
        html.append("</div>")  # Close summary div
        
        # Add individual test sections
        for test_type, results in report_data["results"].items():
            if isinstance(results, dict):
                html.extend([
                    f"<div class='test-section'>",
                    f"<h2>{test_type}</h2>"
                ])
                
                # Add test type specific information
                if "total_tests" in results:
                    success_rate = 0
                    if results["total_tests"] > 0:
                        success_rate = (results["passed_tests"] / results["total_tests"]) * 100
                    
                    html.extend([
                        f"<p>Total: {results['total_tests']}, ",
                        f"Passed: <span class='success'>{results['passed_tests']}</span>, ",
                        f"Failed: <span class='failure'>{results['failed_tests']}</span></p>",
                        "<div class='progress-bar-container'>",
                        f"<div class='progress-bar progress-bar-success' style='width:{success_rate}%'>",
                        f"{success_rate:.1f}%",
                        "</div>",
                        "</div>"
                    ])
                
                # Add details if available
                if "details" in results:
                    html.append("<h3>Details</h3>")
                    html.append("<table>")
                    html.append("<tr><th>Test</th><th>Result</th><th>Duration</th></tr>")
                    
                    for test_name, test_result in results["details"].items():
                        status = "PASS" if test_result.get("success", False) else "FAIL"
                        status_class = "success" if status == "PASS" else "failure"
                        duration = test_result.get("duration", "N/A")
                        
                        html.append("<tr>")
                        html.append(f"<td>{test_name}</td>")
                        html.append(f"<td class='{status_class}'>{status}</td>")
                        html.append(f"<td>{duration}s</td>")
                        html.append("</tr>")
                    
                    html.append("</table>")
                
                # Add reports if available
                if "reports" in results and results["reports"]:
                    html.append("<h3>Reports</h3>")
                    html.append("<ul>")
                    
                    for report_name, report_path in results["reports"].items():
                        if report_path:
                            report_basename = os.path.basename(report_path)
                            html.append(f"<li><a href='{report_basename}'>{report_name}</a></li>")
                    
                    html.append("</ul>")
                
                html.append("</div>")  # Close test-section div
        
        # Close HTML document
        html.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html)


async def run_unit_tests() -> Dict[str, Any]:
    """Run all unit tests"""
    test_logger.info("Running unit tests...")
    
    start_time = time.time()
    
    # Run system operations unit tests
    import pytest
    unit_test_results = pytest.main(["-xvs", "test_system_operations_unit.py"])
    langgraph_unit_results = pytest.main(["-xvs", "test_langgraph_unit.py"])
    
    end_time = time.time()
    
    # Interpret pytest return codes
    return {
        "total_tests": 2,  # 2 test modules
        "passed_tests": int(unit_test_results == 0) + int(langgraph_unit_results == 0),
        "failed_tests": int(unit_test_results != 0) + int(langgraph_unit_results != 0),
        "duration": end_time - start_time,
        "details": {
            "system_operations": {
                "success": unit_test_results == 0,
                "return_code": unit_test_results,
                "duration": end_time - start_time  # Approximation
            },
            "langgraph_components": {
                "success": langgraph_unit_results == 0,
                "return_code": langgraph_unit_results,
                "duration": end_time - start_time  # Approximation
            }
        }
    }


async def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests"""
    test_logger.info("Running integration tests...")
    
    start_time = time.time()
    
    # Run integration tests
    langgraph_integration_results = await test_system_langgraph_integration.run_integration_tests()
    enhanced_integration_results = await test_enhanced_integration.run_integration_tests()
    
    end_time = time.time()
    
    # Count test cases
    total_tests = len(langgraph_integration_results) + len(enhanced_integration_results)
    passed_tests = sum(1 for r in langgraph_integration_results if r.success)
    passed_tests += sum(1 for r in enhanced_integration_results if r.success)
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "duration": end_time - start_time,
        "details": {
            "langgraph_integration": {
                "success": all(r.success for r in langgraph_integration_results),
                "test_count": len(langgraph_integration_results),
                "passed": sum(1 for r in langgraph_integration_results if r.success)
            },
            "enhanced_integration": {
                "success": all(r.success for r in enhanced_integration_results),
                "test_count": len(enhanced_integration_results),
                "passed": sum(1 for r in enhanced_integration_results if r.success)
            }
        },
        "reports": {
            "langgraph_integration": os.path.join(TEST_OUTPUT_DIR, "Project-S LangGraph Integration Tests_report.html"),
            "enhanced_integration": os.path.join(TEST_OUTPUT_DIR, "Project-S LangGraph Integration Tests_report.html")
        }
    }


async def run_e2e_tests() -> Dict[str, Any]:
    """Run all end-to-end tests"""
    test_logger.info("Running end-to-end tests...")
    
    start_time = time.time()
    
    # Run E2E tests
    system_e2e_results = await test_system_e2e.run_e2e_tests()
    comprehensive_e2e_results = await test_comprehensive_e2e.run_e2e_tests()
    
    end_time = time.time()
    
    # Count test cases
    total_tests = len(system_e2e_results) + len(comprehensive_e2e_results)
    passed_tests = sum(1 for r in system_e2e_results if r.success)
    passed_tests += sum(1 for r in comprehensive_e2e_results if r.success)
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "duration": end_time - start_time,
        "details": {
            "system_e2e": {
                "success": all(r.success for r in system_e2e_results),
                "test_count": len(system_e2e_results),
                "passed": sum(1 for r in system_e2e_results if r.success)
            },
            "comprehensive_e2e": {
                "success": all(r.success for r in comprehensive_e2e_results),
                "test_count": len(comprehensive_e2e_results),
                "passed": sum(1 for r in comprehensive_e2e_results if r.success)
            }
        },
        "reports": {
            "system_e2e": os.path.join(TEST_OUTPUT_DIR, "Project-S System E2E Tests_report.html"),
            "comprehensive_e2e": os.path.join(TEST_OUTPUT_DIR, "Project-S Hybrid System E2E Tests_report.html")
        }
    }


async def run_performance_tests() -> Dict[str, Any]:
    """Run all performance tests"""
    test_logger.info("Running performance tests...")
    
    start_time = time.time()
    
    # Run performance tests
    system_performance_results = await test_system_performance.run_performance_suite()
    enhanced_performance_results = await test_enhanced_performance.run_performance_tests()
    
    end_time = time.time()
    
    # Performance tests have a different structure, so we adapt our reporting
    test_cases = []
    if isinstance(system_performance_results, dict):
        test_cases.extend(system_performance_results.get("test_cases", []))
    
    if isinstance(enhanced_performance_results, dict):
        if "test_results" in enhanced_performance_results:
            for result in enhanced_performance_results["test_results"]:
                test_cases.append(result)
    
    return {
        "total_tests": len(test_cases),
        "passed_tests": len(test_cases),  # Performance tests don't pass/fail in the same way
        "failed_tests": 0,
        "duration": end_time - start_time,
        "details": {
            "system_performance": {
                "success": True,
                "test_count": len(test_cases),
                "average_times": system_performance_results.get("average_times", {})
            }
        },
        "reports": {
            "system_performance": os.path.join(TEST_OUTPUT_DIR, "Project-S Performance Tests_report.html"),
            "enhanced_performance": os.path.join(TEST_OUTPUT_DIR, "Project-S Performance Tests_report.html")
        }
    }


async def run_all_tests() -> Dict[str, Any]:
    """Run all types of tests"""
    test_logger.info("Running all tests for Project-S hybrid system...")
    
    # Create test results directory
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    
    # Run each test type
    unit_results = await run_unit_tests()
    integration_results = await run_integration_tests()
    e2e_results = await run_e2e_tests()
    performance_results = await run_performance_tests()
    
    # Compile all results
    all_results = {
        "unit_tests": unit_results,
        "integration_tests": integration_results,
        "e2e_tests": e2e_results,
        "performance_tests": performance_results
    }
    
    # Generate summary report
    report_path = TestReporter.generate_summary_report(all_results)
    test_logger.info(f"Summary report generated: {report_path}")
    
    return all_results


async def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="Project-S Test Runner")
    parser.add_argument("--test-type", choices=["unit", "integration", "e2e", "performance", "all"],
                      default="all", help="Type of tests to run")
    args = parser.parse_args()
    
    if args.test_type == "unit":
        results = await run_unit_tests()
    elif args.test_type == "integration":
        results = await run_integration_tests()
    elif args.test_type == "e2e":
        results = await run_e2e_tests()
    elif args.test_type == "performance":
        results = await run_performance_tests()
    else:
        results = await run_all_tests()
    
    # Print summary
    if "total_tests" in results:
        test_logger.info(f"Tests completed: {results['passed_tests']}/{results['total_tests']} passed")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
