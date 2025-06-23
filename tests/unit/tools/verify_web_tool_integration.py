#!/usr/bin/env python3
"""
WebPageFetchTool Integration Verification
-----------------------------------------
Test that the WebPageFetchTool integrates properly without network dependency.
"""

import asyncio
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

def test_imports():
    """Test that all required imports work."""
    print("🧪 Testing imports...")
    
    try:
        from WORKING_MINIMAL_VERSION import StableProjectS, WEB_TOOL_AVAILABLE
        print("✅ StableProjectS imported successfully")
        print(f"✅ WEB_TOOL_AVAILABLE: {WEB_TOOL_AVAILABLE}")
        
        if WEB_TOOL_AVAILABLE:
            from tools.web_tools import WebPageFetchTool
            print("✅ WebPageFetchTool imported successfully")
            
            # Create instance
            tool = WebPageFetchTool()
            print("✅ WebPageFetchTool instance created")
            
            return True
        else:
            print("⚠️  WebPageFetchTool not available")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def test_tool_method_availability():
    """Test that the tool has the expected methods."""
    print("\n🧪 Testing tool method availability...")
    
    try:
        from tools.web_tools import WebPageFetchTool
        tool = WebPageFetchTool()
        
        # Check if execute method exists
        if hasattr(tool, 'execute'):
            print("✅ execute method available")
        else:
            print("❌ execute method missing")
            return False
            
        # Check if it's async
        import asyncio
        if asyncio.iscoroutinefunction(tool.execute):
            print("✅ execute method is async")
        else:
            print("❌ execute method is not async")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Method test failed: {e}")
        return False

async def test_stable_system_integration():
    """Test that the stable system recognizes the tool."""
    print("\n🧪 Testing stable system integration...")
    
    try:
        from WORKING_MINIMAL_VERSION import StableProjectS
        system = StableProjectS()
        
        print(f"✅ System version: {system.version}")
        print(f"✅ System status: {system.status}")
        
        # Check if the test method exists
        if hasattr(system, 'test_web_page_fetch_tool'):
            print("✅ test_web_page_fetch_tool method available")
            return True
        else:
            print("❌ test_web_page_fetch_tool method missing")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run all integration tests."""
    print("="*60)
    print("WebPageFetchTool Integration Verification")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports()),
        ("Method Test", await test_tool_method_availability()),
        ("Integration Test", await test_stable_system_integration())
    ]
    
    all_passed = True
    for test_name, result in tests:
        if result:
            print(f"\n✅ {test_name}: PASSED")
        else:
            print(f"\n❌ {test_name}: FAILED")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ WebPageFetchTool is properly integrated into the stable system.")
    else:
        print("⚠️  Some integration tests failed.")
    
    print(f"✅ Phase 3B: WebPageFetchTool integration {'COMPLETE' if all_passed else 'INCOMPLETE'}")
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(main())
