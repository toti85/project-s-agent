"""
CI/CD Integration for Project-S Tests
---------------------------------
This script provides integration with CI/CD systems for running the Project-S test suite.
It outputs test results in formats compatible with common CI/CD platforms.
"""
import os
import sys
import asyncio
import argparse
import json
import time
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Import test configuration
from tests.test_config import TEST_CONFIG, test_logger, TEST_OUTPUT_DIR

# Test results output formats
OUTPUT_FORMATS = ["json", "xml", "text"]

# Exit codes
EXIT_CODE_SUCCESS = 0
EXIT_CODE_TEST_FAILURES = 1
EXIT_CODE_SYSTEM_ERROR = 2


async def run_tests(test_type: str) -> dict:
    """Run tests using the main test runner"""
    from tests.run_all_tests import run_unit_tests, run_integration_tests, run_e2e_tests, run_performance_tests, run_all_tests
    
    if test_type == "unit":
        return await run_unit_tests()
    elif test_type == "integration":
        return await run_integration_tests()
    elif test_type == "e2e":
        return await run_e2e_tests()
    elif test_type == "performance":
        return await run_performance_tests()
    else:
        return await run_all_tests()


def generate_json_output(results: dict, output_file: str) -> None:
    """Generate JSON output for test results"""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)


def generate_xml_output(results: dict, output_file: str) -> None:
    """Generate JUnit XML output for test results"""
    test_suite = ET.Element("testsuite")
    test_suite.set("name", "Project-S Tests")
    test_suite.set("tests", str(results.get("total_tests", 0)))
    test_suite.set("failures", str(results.get("failed_tests", 0)))
    test_suite.set("errors", str(results.get("error_tests", 0)))
    test_suite.set("time", str(results.get("duration", 0)))
    test_suite.set("timestamp", datetime.now().isoformat())
    
    # Add test cases
    for test_type, type_results in results.items():
        if isinstance(type_results, dict) and "details" in type_results:
            for test_name, test_result in type_results["details"].items():
                test_case = ET.SubElement(test_suite, "testcase")
                test_case.set("classname", test_type)
                test_case.set("name", test_name)
                test_case.set("time", str(test_result.get("duration", 0)))
                
                if not test_result.get("success", True):
                    failure = ET.SubElement(test_case, "failure")
                    failure.set("message", f"Test {test_name} failed")
                    failure.set("type", "AssertionError")
                    failure.text = str(test_result.get("error", "Unknown error"))
    
    # Create XML tree and write to file
    tree = ET.ElementTree(test_suite)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def generate_text_output(results: dict, output_file: str) -> None:
    """Generate plain text output for test results"""
    lines = [
        "Project-S Test Results",
        "=" * 80,
        f"Total Tests: {results.get('total_tests', 0)}",
        f"Passed Tests: {results.get('passed_tests', 0)}",
        f"Failed Tests: {results.get('failed_tests', 0)}",
        f"Error Tests: {results.get('error_tests', 0)}",
        f"Duration: {results.get('duration', 0):.2f}s",
        "=" * 80
    ]
    
    # Add detailed results
    for test_type, type_results in results.items():
        if isinstance(type_results, dict):
            lines.append(f"\n{test_type}:")
            lines.append("-" * 80)
            
            if "details" in type_results:
                for test_name, test_result in type_results["details"].items():
                    status = "PASSED" if test_result.get("success", False) else "FAILED"
                    lines.append(f"{test_name}: {status} ({test_result.get('duration', 0):.2f}s)")
                    
                    if not test_result.get("success", True) and "error" in test_result:
                        lines.append(f"  Error: {test_result['error']}")
            
            lines.append("-" * 80)
    
    # Write to file
    with open(output_file, "w") as f:
        f.write("\n".join(lines))


def setup_environment():
    """Set up the test environment"""
    # Create test output directory if it doesn't exist
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)
    
    # Check for required dependencies
    missing_deps = []
    try:
        import pytest
    except ImportError:
        missing_deps.append("pytest")
    
    try:
        import matplotlib
    except ImportError:
        missing_deps.append("matplotlib")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        test_logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
        test_logger.error("Please run: pip install -r requirements-test.txt")
        return False
    
    return True


def determine_exit_code(results: dict) -> int:
    """Determine the exit code based on test results"""
    if "total_tests" not in results:
        return EXIT_CODE_SYSTEM_ERROR
    
    if results.get("failed_tests", 0) > 0:
        return EXIT_CODE_TEST_FAILURES
    
    return EXIT_CODE_SUCCESS


async def run_ci_tests(test_type: str, output_format: str, output_file: str) -> int:
    """Run tests and generate output in the specified format"""
    # Run tests
    try:
        results = await run_tests(test_type)
    except Exception as e:
        test_logger.error(f"Error running tests: {str(e)}")
        return EXIT_CODE_SYSTEM_ERROR
    
    # Generate output
    try:
        if output_format == "json":
            generate_json_output(results, output_file)
        elif output_format == "xml":
            generate_xml_output(results, output_file)
        elif output_format == "text":
            generate_text_output(results, output_file)
    except Exception as e:
        test_logger.error(f"Error generating output: {str(e)}")
        return EXIT_CODE_SYSTEM_ERROR
    
    # Determine exit code
    return determine_exit_code(results)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CI/CD integration for Project-S tests")
    parser.add_argument("--test-type", choices=["unit", "integration", "e2e", "performance", "all"],
                        default="all", help="Type of tests to run")
    parser.add_argument("--output-format", choices=OUTPUT_FORMATS,
                        default="json", help="Output format for test results")
    parser.add_argument("--output-file", type=str,
                        help="Output file path (defaults to test_results.<format>)")
    parser.add_argument("--ci-system", choices=["github", "jenkins", "gitlab", "azure", "generic"],
                        default="generic", help="CI system to integrate with")
    args = parser.parse_args()
    
    # Set default output file if not specified
    if not args.output_file:
        args.output_file = os.path.join(TEST_OUTPUT_DIR, f"test_results.{args.output_format}")
    
    # Set up environment
    if not setup_environment():
        return EXIT_CODE_SYSTEM_ERROR
    
    # Run tests
    exit_code = asyncio.run(run_ci_tests(args.test_type, args.output_format, args.output_file))
    
    # Output for CI system
    if args.ci_system == "github":
        # GitHub Actions output
        with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
            f.write(f"test_result_file={args.output_file}\n")
            f.write(f"test_exit_code={exit_code}\n")
    elif args.ci_system == "jenkins":
        # Jenkins typically uses the exit code and JUnit XML format
        pass
    elif args.ci_system == "gitlab":
        # GitLab CI typically uses the exit code and JUnit XML format
        pass
    elif args.ci_system == "azure":
        # Azure DevOps typically uses the exit code and JUnit XML format
        pass
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
