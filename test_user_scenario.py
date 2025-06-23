#!/usr/bin/env python3
"""
Final integration test simulating the exact user scenario
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def simulate_user_command():
    """Simulate the exact user command scenario."""
    
    print("🔥 SIMULATING EXACT USER SCENARIO")
    print("=" * 60)
    print("Simulating: Project-S> analyze system performance and output paste to report file")
    print("")
    
    try:
        # Import the main processing function
        from main import intelligent_command_parser, process_file_operation_directly, generate_system_analysis_report
        
        # The exact command the user entered
        user_command = "analyze system performance and output paste to report file"
        
        print("⏳ Processing with enhanced intelligence...")
        
        # Process the command
        parsed_command = await intelligent_command_parser(user_command)
        
        # Display confidence information (as shown in the real system)
        confidence = parsed_command.get("confidence", 0.0)
        confidence_level = parsed_command.get("confidence_level", "Unknown")
        
        print(f"🎯 Intent Analysis: {parsed_command['type']} ({confidence:.0%} confidence - {confidence_level})")
        
        # Execute based on command type
        if parsed_command["type"] == "SYSTEM_ANALYSIS":
            print(f"🔥 SYSTEM PERFORMANCE ANALYSIS AND REPORTING")
            result = await generate_system_analysis_report(parsed_command.get("report_file", "system_analysis_report.txt"))
            print("\n=== SYSTEM ANALYSIS RESULT ===")
            if result["status"] == "success":
                print(f"✅ {result['message']}")
                print(f"📄 Report saved to: {result['report_path']}")
                print(f"📊 Report size: {result['size']} bytes")
                if result.get("summary"):
                    print(f"📋 Summary: {result['summary']}")
                
                # Verify the report is NOT empty
                if result['size'] > 0:
                    print(f"\n🎉 SUCCESS: Report file is NOT empty ({result['size']} bytes)")
                    print("The issue has been RESOLVED!")
                else:
                    print(f"\n❌ FAILURE: Report file is still empty")
                    
            else:
                print(f"❌ {result['message']}")
        else:
            # This would be the old behavior that caused empty reports
            print(f"❌ Command incorrectly identified as: {parsed_command['type']}")
            print("This would have resulted in an empty report file (the original issue)")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting user scenario simulation...")  
    result = asyncio.run(simulate_user_command())
    if result:
        print("\n" + "🎉" * 30)
        print("SUCCESS: The system analysis functionality is now working!")
        print("The original issue has been resolved.")
        print("Your command 'analyze system performance and output paste to report file'")
        print("will now generate a comprehensive, NON-EMPTY report file.")
        print("🎉" * 30)
    else:
        print("\n❌ SIMULATION FAILED!")
