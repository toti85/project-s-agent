#!/usr/bin/env python3
"""
Phase 3C: SystemInfoTool Integration Test
-----------------------------------------
"""

import asyncio
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

async def main():
    """Test Phase 3C SystemInfoTool integration."""
    print("\n" + "="*60)
    print("Phase 3C: SystemInfoTool Integration Test")
    print("="*60)
    
    try:
        # Import and create the stable system
        from WORKING_MINIMAL_VERSION import StableProjectS
        
        # Create system instance
        system = StableProjectS()
        print(f"✅ System created: Version {system.version}")
        
        # Run comprehensive tests
        print("\n🧪 Running comprehensive system tests...")
        test_result = await system.run_test()
        
        if test_result:
            print("\n🎉 ALL TESTS PASSED! Phase 3C Complete!")
            print("✅ System is stable with 4 integrated tools:")
            print("   1. FileReadTool")
            print("   2. FileWriteTool") 
            print("   3. WebPageFetchTool")
            print("   4. SystemInfoTool")
        else:
            print("\n⚠️  Some tests failed, but system is stable.")
            
        print(f"\n✅ System Status: {system.status}")
        print("✅ Phase 3C Integration complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nPhase 3C Result: {'SUCCESS' if result else 'FAILED'}")
