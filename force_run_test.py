#!/usr/bin/env python3
"""
Force run the fixed system and check file outputs.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

async def force_run():
    """Force run the system and capture results in files."""
    try:
        print("Attempting to import and run WORKING_MINIMAL_VERSION_FIXED...")
        
        # Import the fixed system
        from WORKING_MINIMAL_VERSION_FIXED import StableProjectS
        
        # Create system instance
        system = StableProjectS()
        
        print("System created, running tests...")
        
        # Run the test
        result = await system.run_test()
        
        print(f"Test completed: {result}")
        print("Check test_outputs/test_results.json for detailed results")
        print("Check logs/system_logs.txt for system logs")
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Force running the stable system...")
    result = asyncio.run(force_run())
    print(f"Final result: {result}")
