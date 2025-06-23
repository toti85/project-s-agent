#!/usr/bin/env python3
"""
Direct test of the enhanced system analysis command parser
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_parser():
    """Test the enhanced system analysis command parsing."""
    
    print("🔥 TESTING ENHANCED SYSTEM ANALYSIS COMMAND PARSER")
    print("=" * 60)
    
    try:
        # Import the legacy parser directly to bypass the advanced engine
        from main import _legacy_intelligent_command_parser
        
        print("✅ Successfully imported legacy parser")
        
        # Test the exact command that was failing
        test_command = "analyze system performance and output paste to report file"
        
        print(f"\n🔍 Testing exact command: '{test_command}'")
        result = await _legacy_intelligent_command_parser(test_command)
        
        print(f"   Type: {result['type']}")
        print(f"   Operation: {result.get('operation', 'N/A')}")
        print(f"   Report File: {result.get('report_file', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0):.0%} ({result.get('confidence_level', 'Unknown')})")
        
        if result['type'] == 'SYSTEM_ANALYSIS':
            print("   ✅ CORRECTLY identified as SYSTEM_ANALYSIS")
            
            # Now test the system analysis function
            print(f"\n📋 Testing system analysis report generation...")
            from main import generate_system_analysis_report
            
            report_result = await generate_system_analysis_report(result.get('report_file', 'test_report.txt'))
            
            if report_result["status"] == "success":
                print("✅ System analysis report generated successfully!")
                print(f"   📄 Report path: {report_result['report_path']}")
                print(f"   📊 Report size: {report_result['size']} bytes")
                print(f"   📋 Summary: {report_result['summary']}")
                
                # Show first few lines of the report
                with open(report_result['report_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')[:15]  # First 15 lines
                    print(f"\n📝 Report preview:")
                    print("-" * 50)
                    for line in lines:
                        print(line)
                    print("-" * 50)
                
                return True
            else:
                print(f"❌ System analysis failed: {report_result['message']}")
                return False
        else:
            print(f"   ❌ INCORRECTLY identified as {result['type']}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting enhanced parser test...")
    result = asyncio.run(test_enhanced_parser())
    if result:
        print("\n🎉 ENHANCED PARSER TEST PASSED!")
        print("The system analysis functionality is now working correctly.")
        print("Try running: python main.py")
        print("Then type: analyze system performance and output paste to report file")
    else:
        print("\n❌ ENHANCED PARSER TEST FAILED!")
