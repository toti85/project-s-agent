#!/usr/bin/env python3
"""
Direct test of main.py with the system analysis command
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_main_system():
    """Test the main system with the system analysis command."""
    
    print("🔥 TESTING MAIN.PY SYSTEM WITH SYSTEM ANALYSIS COMMAND")
    print("=" * 60)
    
    try:
        from main import ProjectSUnified
        
        # Create the unified agent
        agent = ProjectSUnified()
        
        # Initialize the system
        print("🚀 Initializing Project-S Unified System...")
        initialized = await agent.initialize()
        
        if not initialized:
            print("❌ Failed to initialize Project-S system")
            return False
            
        print("✅ Project-S system initialized successfully")
        
        # Test the exact command
        user_input = "analyze system performance and output paste to report file"
        print(f"\n🔍 Processing command: '{user_input}'")
        
        # Process the command
        should_continue = await agent.process_user_input(user_input)
        
        print(f"✅ Command processed successfully")
        
        # Check if report file was created
        from pathlib import Path
        report_files = list(Path(".").glob("*report*.txt"))
        if report_files:
            print(f"\n📄 Report files found:")
            for file in report_files[-3:]:  # Show last 3 files
                size = file.stat().st_size
                print(f"   {file.name}: {size} bytes")
                if size > 0:
                    print(f"   ✅ File is NOT empty")
                else:
                    print(f"   ❌ File is empty")
        
        # Cleanup
        await agent.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting main.py system test...")
    result = asyncio.run(test_main_system())
    if result:
        print("\n🎉 MAIN SYSTEM TEST COMPLETED!")
        print("Check the report files to see if they contain content.")
    else:
        print("\n❌ MAIN SYSTEM TEST FAILED!")
