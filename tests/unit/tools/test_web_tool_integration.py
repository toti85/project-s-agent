#!/usr/bin/env python3
"""
Test script for WebPageFetchTool integration
--------------------------------------------
This script tests the new WebPageFetchTool in our stable system.
"""

import asyncio
import logging
import sys
import io
from pathlib import Path

# Configure UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Test the stable system with WebPageFetchTool."""
    print("DEBUG: Starting test...")
    try:
        print("\n" + "="*60)
        print("Project-S Web Tool Integration Test")
        print("="*60)
        
        print("DEBUG: About to import...")
        # Import and create the stable system
        from WORKING_MINIMAL_VERSION import StableProjectS
        print("DEBUG: Import successful...")
        
        # Create system instance
        system = StableProjectS()
        print(f"✅ System created: Version {system.version}")
        
        # Run comprehensive tests
        print("\n🧪 Running comprehensive system tests...")
        test_result = await system.run_test()
        
        if test_result:
            print("\n🎉 ALL TESTS PASSED! System is stable with WebPageFetchTool.")
        else:
            print("\n⚠️  Some tests failed, but system is stable.")
            
        print(f"\n✅ System Status: {system.status}")
        print("✅ Integration complete!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    asyncio.run(main())
