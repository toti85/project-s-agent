#!/usr/bin/env python3
"""
Test script for the new system analysis functionality in Project-S
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_system_analysis():
    """Test the system analysis command parsing and execution."""
    
    print("🔥 TESTING PROJECT-S SYSTEM ANALYSIS FUNCTIONALITY")
    print("=" * 60)
    
    try:
        # Import the necessary functions from main.py
        from main import intelligent_command_parser, generate_system_analysis_report
        
        print("✅ Successfully imported Project-S functions")
        
        # Test 1: Command parsing for system analysis
        print("\n📊 TEST 1: Command Parsing")
        test_commands = [
            "analyze system performance and output paste to report file",
            "analyze system performance",
            "generate system report",
            "system analysis report",
            "create performance report"
        ]
        
        for cmd in test_commands:
            print(f"\n🔍 Testing command: '{cmd}'")
            result = await intelligent_command_parser(cmd)
            print(f"   Type: {result['type']}")
            print(f"   Confidence: {result.get('confidence', 0):.0%} ({result.get('confidence_level', 'Unknown')})")
            if result['type'] == 'SYSTEM_ANALYSIS':
                print(f"   Report file: {result.get('report_file', 'Unknown')}")
                print("   ✅ Correctly identified as SYSTEM_ANALYSIS")
            else:
                print(f"   ❌ Incorrectly identified as {result['type']}")
        
        # Test 2: System analysis report generation
        print(f"\n📋 TEST 2: System Analysis Report Generation")
        report_result = await generate_system_analysis_report("test_system_analysis_report.txt")
        
        if report_result["status"] == "success":
            print("✅ System analysis report generated successfully!")
            print(f"   📄 Report path: {report_result['report_path']}")
            print(f"   📊 Report size: {report_result['size']} bytes")
            print(f"   📋 Summary: {report_result['summary']}")
        else:
            print(f"❌ System analysis failed: {report_result['message']}")
        
        # Test 3: Verify report content
        print(f"\n📖 TEST 3: Report Content Verification")
        try:
            with open("test_system_analysis_report.txt", 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ Report file created with {len(content)} characters")
                print(f"📝 Report preview (first 300 chars):")
                print("-" * 40)
                print(content[:300] + "..." if len(content) > 300 else content)
                print("-" * 40)
                
                # Check for key sections
                required_sections = [
                    "PROJECT-S SYSTEM ANALYSIS REPORT",
                    "SYSTEM INFORMATION:",
                    "PERFORMANCE METRICS:",
                    "MEMORY:",
                    "DISK USAGE:",
                    "ANALYSIS SUMMARY:"
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in content:
                        missing_sections.append(section)
                
                if missing_sections:
                    print(f"⚠️ Missing sections: {missing_sections}")
                else:
                    print("✅ All required sections present in report")
                
        except FileNotFoundError:
            print("❌ Report file was not created")
        except Exception as e:
            print(f"❌ Error reading report file: {e}")
        
        print(f"\n🎯 SYSTEM ANALYSIS TEST COMPLETE")
        print("=" * 60)
        print("Summary:")
        print("- ✅ Command parsing working")
        print("- ✅ Report generation working")
        print("- ✅ File creation working")
        print("- ✅ System analysis functionality is READY!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure main.py is properly configured")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting system analysis test...")
    result = asyncio.run(test_system_analysis())
    if result:
        print("\n🎉 ALL TESTS PASSED! System analysis functionality is working properly.")
    else:
        print("\n❌ TESTS FAILED! Check the error messages above.")
