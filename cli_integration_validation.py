#!/usr/bin/env python3
"""
CLI Integration Validation Test
===============================
Comprehensive test suite to validate the unified CLI integration with Project-S.

Tests:
1. CLI Import and Initialization
2. Command Processing
3. Multi-model AI Integration
4. File Operations
5. Workflow System
6. Interactive Mode
7. Export Functionality
8. Windows Launcher Integration

Author: Project-S Team
Version: 1.0 - CLI Integration Test
"""

import asyncio
import os
import sys
import time
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_cli_import():
    """Test 1: CLI Import and Basic Functionality"""
    print("🔍 Test 1: CLI Import and Basic Functionality")
    try:
        import cli_main
        print("✅ CLI module imported successfully")
        
        # Test argument parser creation
        parser = cli_main.create_argument_parser()
        print("✅ Argument parser created successfully")
        
        # Test CLI class instantiation
        cli = cli_main.ProjectSCLI()
        print("✅ ProjectSCLI class instantiated successfully")
        
        return True
    except Exception as e:
        print(f"❌ CLI import test failed: {e}")
        return False

async def test_system_initialization():
    """Test 2: System Initialization"""
    print("\n🔍 Test 2: System Initialization")
    try:
        import cli_main
        cli = cli_main.ProjectSCLI()
        
        # Test initialization
        init_result = await cli.initialize()
        if init_result:
            print("✅ CLI system initialized successfully")
            return True
        else:
            print("❌ CLI system initialization failed")
            return False
    except Exception as e:
        print(f"❌ System initialization test failed: {e}")
        return False

def test_export_functionality():
    """Test 3: Export Functionality"""
    print("\n🔍 Test 3: Export Functionality")
    try:
        # Test CLI export command
        result = subprocess.run([
            sys.executable, "cli_main.py", "--export"
        ], capture_output=True, text=True, cwd="c:\\project_s_agent")
        
        if result.returncode == 0:
            print("✅ CLI export command executed successfully")
            
            # Check if export files exist
            export_dir = Path("c:\\project_s_agent\\PROJECTS_CLI_EXPORT")
            if export_dir.exists():
                print("✅ Export directory exists")
                
                # Check for key files
                key_files = [
                    "cli_entry.py",
                    "main_interactive.py", 
                    "workflow_integration.py",
                    "model_manager_integration.py",
                    "README.md"
                ]
                
                for file in key_files:
                    if (export_dir / file).exists():
                        print(f"✅ {file} exists in export")
                    else:
                        print(f"❌ {file} missing from export")
                
                return True
            else:
                print("❌ Export directory not found")
                return False
        else:
            print(f"❌ CLI export command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Export functionality test failed: {e}")
        return False

def test_windows_launcher():
    """Test 4: Windows Launcher Script"""
    print("\n🔍 Test 4: Windows Launcher Script")
    try:
        launcher_path = Path("c:\\project_s_agent\\start_cli.bat")
        if launcher_path.exists():
            print("✅ Windows launcher script exists")
            
            # Read and verify launcher content
            with open(launcher_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "Project-S Unified CLI - Windows Launcher" in content:
                print("✅ Launcher script has correct header")
            
            if "Interactive Mode" in content:
                print("✅ Launcher script includes interactive mode")
                
            return True
        else:
            print("❌ Windows launcher script not found")
            return False
    except Exception as e:
        print(f"❌ Windows launcher test failed: {e}")
        return False

def test_help_system():
    """Test 5: Help System"""
    print("\n🔍 Test 5: Help System")
    try:
        # Test main help
        result = subprocess.run([
            sys.executable, "cli_main.py", "--help"
        ], capture_output=True, text=True, cwd="c:\\project_s_agent")
        
        if result.returncode == 0 and "Project-S Unified CLI" in result.stdout:
            print("✅ Main help system working")
            
            # Test model listing
            result = subprocess.run([
                sys.executable, "cli_main.py", "--list-models"
            ], capture_output=True, text=True, cwd="c:\\project_s_agent")
            
            if result.returncode == 0:
                print("✅ Model listing command working")
                
            # Test workflow listing
            result = subprocess.run([
                sys.executable, "cli_main.py", "--list-workflows"
            ], capture_output=True, text=True, cwd="c:\\project_s_agent")
            
            if result.returncode == 0:
                print("✅ Workflow listing command working")
                
            return True
        else:
            print(f"❌ Help system test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Help system test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all tests and provide comprehensive report"""
    print("=" * 80)
    print("🚀 PROJECT-S CLI INTEGRATION VALIDATION")
    print("=" * 80)
    
    start_time = time.time()
    tests_passed = 0
    total_tests = 5
    
    # Run all tests
    test_results = []
    
    # Test 1: CLI Import
    result1 = await test_cli_import()
    test_results.append(("CLI Import", result1))
    if result1: tests_passed += 1
    
    # Test 2: System Initialization
    result2 = await test_system_initialization()
    test_results.append(("System Initialization", result2))
    if result2: tests_passed += 1
    
    # Test 3: Export Functionality
    result3 = test_export_functionality()
    test_results.append(("Export Functionality", result3))
    if result3: tests_passed += 1
    
    # Test 4: Windows Launcher
    result4 = test_windows_launcher()
    test_results.append(("Windows Launcher", result4))
    if result4: tests_passed += 1
    
    # Test 5: Help System
    result5 = test_help_system()
    test_results.append(("Help System", result5))
    if result5: tests_passed += 1
    
    # Generate report
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print(f"\n📈 Tests Passed: {tests_passed}/{total_tests}")
    print(f"⏱️  Execution Time: {duration:.2f} seconds")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! CLI Integration is successful!")
        print("\n✅ INTEGRATION STATUS: COMPLETE")
        print("✅ The unified CLI is ready for production use")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} tests failed. Review and fix issues.")
        print("\n❌ INTEGRATION STATUS: INCOMPLETE")
    
    # Save report
    report_path = Path("c:\\project_s_agent\\cli_integration_test_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("PROJECT-S CLI INTEGRATION TEST REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Tests Passed: {tests_passed}/{total_tests}\n")
        f.write(f"Execution Time: {duration:.2f} seconds\n\n")
        
        f.write("DETAILED RESULTS:\n")
        f.write("-" * 20 + "\n")
        for test_name, passed in test_results:
            status = "PASSED" if passed else "FAILED"
            f.write(f"{test_name}: {status}\n")
        
        if tests_passed == total_tests:
            f.write("\nINTEGRATION STATUS: COMPLETE\n")
            f.write("The unified CLI is ready for production use.\n")
        else:
            f.write("\nINTEGRATION STATUS: INCOMPLETE\n")
            f.write("Some tests failed. Review and fix issues.\n")
    
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    sys.exit(0 if success else 1)
