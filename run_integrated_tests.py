#!/usr/bin/env python
# filepath: c:\project_s_agent\run_integrated_tests.py
"""
Integrated Test Runner for Project-S + LangGraph Hybrid System
------------------------------------------------------------
This script combines both the standard test framework and the custom test scripts
to provide comprehensive coverage of all system aspects.
"""
import os
import sys
import argparse
import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("integrated_test_results.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("integrated_tester")

# Add test directory to path
PROJECT_ROOT = Path(__file__).parent.resolve()
TEST_DIR = PROJECT_ROOT / "tests"
sys.path.insert(0, str(TEST_DIR))

# Import test configuration
try:
    from tests.test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
except ImportError:
    logger.warning("Could not import test configuration from test_config.py")
    TEST_CONFIG = {}
    TEST_DATA_DIR = PROJECT_ROOT / "tests" / "test_data"
    TEST_OUTPUT_DIR = PROJECT_ROOT / "tests" / "test_output"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Integrated Test Runner for Project-S")
    
    parser.add_argument(
        "--test-type",
        choices=["all", "unit", "integration", "e2e", "performance", "api-ui", "custom"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Increase verbosity"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML reports"
    )
    
    parser.add_argument(
        "--report-dir",
        default=str(TEST_OUTPUT_DIR),
        help="Directory for test reports"
    )
    
    parser.add_argument(
        "--custom-tests",
        nargs="+",
        default=[],
        help="List of custom test scripts to run"
    )
    
    return parser.parse_args()


def run_pytest_tests(test_pattern, verbose=False):
    """Run tests using pytest"""
    import pytest
    
    args = [test_pattern]
    if verbose:
        args.append("-v")
    
    exit_code = pytest.main(args)
    
    return exit_code == 0


def run_custom_test_script(script_path, verbose=False):
    """Run a custom test script"""
    import importlib.util
    
    logger.info(f"Running custom test script: {script_path}")
    
    try:
        # Import the script as a module
        script_path = Path(script_path)
        if not script_path.is_absolute():
            script_path = PROJECT_ROOT / script_path
            
        module_name = script_path.stem
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # If the module has a main function, call it
        if hasattr(module, "main"):
            result = module.main()
            return result
        
        # If the module has run_tests function, call it
        elif hasattr(module, "run_tests"):
            result = module.run_tests()
            return result
            
        # If the module has an async main or run_tests, run it in the event loop
        elif hasattr(module, "async_main"):
            result = asyncio.run(module.async_main())
            return result
        elif hasattr(module, "run_async_tests"):
            result = asyncio.run(module.run_async_tests())
            return result
        
        logger.warning(f"No test runner function found in {script_path}")
        return False
        
    except Exception as e:
        logger.error(f"Error running custom test script {script_path}: {e}")
        logger.exception(e)
        return False


def generate_test_report(report_dir, test_results):
    """Generate HTML report of test results"""
    try:
        from jinja2 import Environment, FileSystemLoader
        import matplotlib.pyplot as plt
        
        # Create report directory if it doesn't exist
        report_dir = Path(report_dir)
        report_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up Jinja environment
        env = Environment(loader=FileSystemLoader(TEST_DIR / "templates", followlinks=True))
        template = env.get_template("test_report_template.html")
        
        # Generate test report
        report_path = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_path, "w") as f:
            f.write(template.render(
                test_results=test_results,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
        logger.info(f"Test report generated: {report_path}")
        
        # Generate performance chart
        if any(result.get("performance_data") for result in test_results.values()):
            performance_data = {}
            for test_type, result in test_results.items():
                if "performance_data" in result:
                    performance_data[test_type] = result["performance_data"]
            
            if performance_data:
                chart_path = report_dir / "performance_chart.png"
                generate_performance_chart(performance_data, chart_path)
                logger.info(f"Performance chart generated: {chart_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error generating test report: {e}")
        logger.exception(e)
        return False


def generate_performance_chart(performance_data, chart_path):
    """Generate performance chart from test data"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Extract data
        test_types = list(performance_data.keys())
        metrics = set()
        for test_data in performance_data.values():
            metrics.update(test_data.keys())
        metrics = list(metrics)
        
        # Create subplots for each metric
        fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 4*len(metrics)))
        if len(metrics) == 1:
            axes = [axes]
            
        for i, metric in enumerate(metrics):
            ax = axes[i]
            values = [performance_data[test_type].get(metric, 0) for test_type in test_types]
            
            ax.bar(test_types, values)
            ax.set_title(f"{metric} by Test Type")
            ax.set_ylabel(metric)
            
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        
    except Exception as e:
        logger.error(f"Error generating performance chart: {e}")
        logger.exception(e)


def main():
    """Main function for the test runner"""
    args = parse_arguments()
    
    logger.info("Starting integrated test runner")
    logger.info(f"Test type: {args.test_type}")
    
    test_results = {}
    start_time_overall = time.time()
    
    # Ensure report directory exists
    if args.report:
        report_dir = Path(args.report_dir)
        report_dir.mkdir(exist_ok=True, parents=True)
    
    # Run standard pytest tests
    if args.test_type in ["all", "unit"]:
        logger.info("Running unit tests")
        start_time = time.time()
        success = run_pytest_tests("tests/test_*unit.py", args.verbose)
        duration = time.time() - start_time
        test_results["unit"] = {
            "success": success,
            "duration": duration,
            "performance_data": {"execution_time": duration}
        }
        logger.info(f"Unit tests {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    if args.test_type in ["all", "integration"]:
        logger.info("Running integration tests")
        start_time = time.time()
        success = run_pytest_tests("tests/test_*integration.py", args.verbose)
        duration = time.time() - start_time
        test_results["integration"] = {
            "success": success,
            "duration": duration,
            "performance_data": {"execution_time": duration}
        }
        logger.info(f"Integration tests {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    if args.test_type in ["all", "e2e"]:
        logger.info("Running end-to-end tests")
        start_time = time.time()
        success = run_pytest_tests("tests/test_*e2e.py", args.verbose)
        duration = time.time() - start_time
        test_results["e2e"] = {
            "success": success,
            "duration": duration,
            "performance_data": {"execution_time": duration}
        }
        logger.info(f"End-to-end tests {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    if args.test_type in ["all", "performance"]:
        logger.info("Running performance tests")
        start_time = time.time()
        success = run_pytest_tests("tests/test_*performance.py", args.verbose)
        duration = time.time() - start_time
        test_results["performance"] = {
            "success": success,
            "duration": duration,
            "performance_data": {"execution_time": duration}
        }
        logger.info(f"Performance tests {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    # Run custom test scripts
    custom_test_scripts = []
    
    if args.test_type in ["all", "custom"] or args.custom_tests:
        if args.custom_tests:
            custom_test_scripts = args.custom_tests
        else:
            # Default custom test scripts
            custom_test_scripts = [
                "comprehensive_test_suite.py",
                "basic_test.py",
                "langgraph_integration_test.py",
                "api_ui_test.py"
            ]
        
        for script in custom_test_scripts:
            logger.info(f"Running custom test script: {script}")
            start_time = time.time()
            success = run_custom_test_script(script, args.verbose)
            duration = time.time() - start_time
            test_results[f"custom_{Path(script).stem}"] = {
                "success": success,
                "duration": duration,
                "performance_data": {"execution_time": duration}
            }
            logger.info(f"Custom test {script} {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    # Run API/UI tests separately if requested
    if args.test_type in ["all", "api-ui"]:
        logger.info("Running API and UI tests")
        start_time = time.time()
        success = run_custom_test_script("api_ui_test.py", args.verbose)
        duration = time.time() - start_time
        test_results["api-ui"] = {
            "success": success,
            "duration": duration,
            "performance_data": {"execution_time": duration}
        }
        logger.info(f"API/UI tests {'passed' if success else 'failed'} in {duration:.2f} seconds")
    
    # Calculate overall results
    overall_success = all(result["success"] for result in test_results.values())
    overall_duration = time.time() - start_time_overall
    
    logger.info(f"All tests {'passed' if overall_success else 'failed'} in {overall_duration:.2f} seconds")
    
    # Generate report if requested
    if args.report:
        test_results["overall"] = {
            "success": overall_success,
            "duration": overall_duration,
            "performance_data": {"execution_time": overall_duration}
        }
        
        generate_test_report(args.report_dir, test_results)
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
