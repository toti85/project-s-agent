#!/usr/bin/env python
# filepath: c:\project_s_agent\ci_cd_test_runner.py
"""
CI/CD Test Runner for Project-S + LangGraph Hybrid System
-------------------------------------------------------
This script is designed to run tests in a CI/CD environment
and generate appropriate XML test reports.
"""
import os
import sys
import time
import argparse
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("ci_cd_test_results.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ci_cd_test_runner")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="CI/CD Test Runner for Project-S")
    
    parser.add_argument(
        "--test-type",
        choices=["all", "unit", "integration", "e2e", "performance", "api-ui"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--xml-output",
        action="store_true",
        help="Generate JUnit XML reports"
    )
    
    parser.add_argument(
        "--output-dir",
        default="test_results",
        help="Directory for test results"
    )
    
    return parser.parse_args()


def run_pytest_tests(test_pattern, xml_output=False, output_dir="test_results"):
    """Run pytest tests with optional XML output"""
    try:
        # Ensure output directory exists
        Path(output_dir).mkdir(exist_ok=True, parents=True)
        
        # Build command
        cmd = ["pytest", test_pattern, "-v"]
        if xml_output:
            xml_file = Path(output_dir) / f"test_results_{Path(test_pattern).stem}.xml"
            cmd.extend(["--junitxml", str(xml_file)])
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run pytest
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        # Log results
        logger.info(f"Test execution completed in {duration:.2f} seconds")
        logger.info(f"Return code: {result.returncode}")
        
        # Log stdout and stderr
        for line in result.stdout.splitlines():
            logger.info(f"[STDOUT] {line}")
        
        for line in result.stderr.splitlines():
            logger.warning(f"[STDERR] {line}")
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error running pytest: {e}", exc_info=True)
        return False


def run_custom_script(script_path, xml_output=False, output_dir="test_results"):
    """Run a custom test script"""
    try:
        # Ensure output directory exists
        Path(output_dir).mkdir(exist_ok=True, parents=True)
        
        # Build command
        cmd = [sys.executable, script_path]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run script
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        # Log results
        logger.info(f"Test execution completed in {duration:.2f} seconds")
        logger.info(f"Return code: {result.returncode}")
        
        # Log stdout and stderr
        for line in result.stdout.splitlines():
            logger.info(f"[STDOUT] {line}")
        
        for line in result.stderr.splitlines():
            logger.warning(f"[STDERR] {line}")
        
        # Generate XML report if requested
        if xml_output:
            from junit_xml import TestSuite, TestCase
            
            # Create test case
            test_case = TestCase(
                name=f"run_{Path(script_path).stem}",
                classname=Path(script_path).stem,
                elapsed_sec=duration
            )
            
            # Set status based on return code
            if result.returncode != 0:
                test_case.add_failure_info(
                    message="Test script failed",
                    output=result.stdout + "\n" + result.stderr
                )
            
            # Create test suite and write to file
            test_suite = TestSuite(Path(script_path).stem, [test_case])
            xml_file = Path(output_dir) / f"test_results_{Path(script_path).stem}.xml"
            
            with open(xml_file, 'w') as f:
                from junit_xml import to_xml_report_string
                f.write(to_xml_report_string([test_suite]))
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error running custom script: {e}", exc_info=True)
        return False


def main():
    """Main function for the CI/CD test runner"""
    args = parse_arguments()
    
    logger.info("Starting CI/CD test runner")
    logger.info(f"Test type: {args.test_type}")
    logger.info(f"XML output: {args.xml_output}")
    logger.info(f"Output directory: {args.output_dir}")
    
    test_results = {}
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(exist_ok=True, parents=True)
    
    # Run pytest tests
    if args.test_type in ["all", "unit"]:
        logger.info("Running unit tests")
        success = run_pytest_tests("tests/test_*unit.py", args.xml_output, args.output_dir)
        test_results["unit"] = success
    
    if args.test_type in ["all", "integration"]:
        logger.info("Running integration tests")
        success = run_pytest_tests("tests/test_*integration.py", args.xml_output, args.output_dir)
        test_results["integration"] = success
    
    if args.test_type in ["all", "e2e"]:
        logger.info("Running end-to-end tests")
        success = run_pytest_tests("tests/test_*e2e.py", args.xml_output, args.output_dir)
        test_results["e2e"] = success
    
    if args.test_type in ["all", "performance"]:
        logger.info("Running performance tests")
        success = run_pytest_tests("tests/test_*performance.py", args.xml_output, args.output_dir)
        test_results["performance"] = success
    
    # Run custom test scripts
    if args.test_type in ["all", "custom"]:
        logger.info("Running custom test suite")
        success = run_custom_script("comprehensive_test_suite.py", args.xml_output, args.output_dir)
        test_results["comprehensive"] = success
    
    if args.test_type in ["all", "api-ui"]:
        logger.info("Running API and UI tests")
        success = run_custom_script("api_ui_test.py", args.xml_output, args.output_dir)
        test_results["api-ui"] = success
    
    # Calculate overall results
    overall_success = all(test_results.values())
    
    # Write summary report
    summary = {
        "timestamp": datetime.now().isoformat(),
        "overall_success": overall_success,
        "test_results": test_results
    }
    
    summary_file = Path(args.output_dir) / "test_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Test summary written to {summary_file}")
    logger.info(f"Overall test status: {'PASSED' if overall_success else 'FAILED'}")
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
