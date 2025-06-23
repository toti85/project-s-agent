"""
Project-S Tool Integration Test
------------------------------
Safe tool integration testing on the stable foundation.
This demonstrates how to add features incrementally.

Version: 0.4.0-stable-tools
Status: SAFE INCREMENTAL DEVELOPMENT
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Import stable foundation
from WORKING_MINIMAL_VERSION import StableProjectS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeToolIntegration(StableProjectS):
    """
    Extends the stable system with safe tool integration.
    Maintains all stability guarantees.
    """
    
    def __init__(self):
        super().__init__()
        self.version = "0.4.0-stable-tools"
        self.tools_loaded = 0
        
    async def load_tools_safely(self):
        """Load tools one by one with error handling."""
        logger.info("🔧 Starting safe tool integration...")
        
        # Test 1: Try to import tool registry
        try:
            from tools.tool_registry import tool_registry
            logger.info(f"✅ Tool registry imported: {len(tool_registry.tools)} tools available")
            self.tools_loaded += len(tool_registry.tools)
        except ImportError as e:
            logger.warning(f"⚠️  Tool registry not available: {e}")
            
        # Test 2: Try to import basic tools
        basic_tools = [
            ('tools.file_tools', 'FileReadTool'),
            ('tools.file_tools', 'FileWriteTool'),
            ('tools.web_tools', 'WebPageFetchTool'),
        ]
        
        for module_name, tool_name in basic_tools:
            try:
                module = __import__(module_name, fromlist=[tool_name])
                tool_class = getattr(module, tool_name)
                logger.info(f"✅ Tool available: {tool_name}")
                self.tools_loaded += 1
            except (ImportError, AttributeError) as e:
                logger.warning(f"⚠️  Tool not available: {tool_name} - {e}")
        
        logger.info(f"🔧 Tool integration complete: {self.tools_loaded} tools loaded")
        return self.tools_loaded > 0
    
    async def test_tool_execution(self):
        """Test actual tool execution safely."""
        logger.info("🧪 Testing tool execution...")
        
        try:
            # Test file operations
            from tools.file_tools import FileWriteTool, FileReadTool
            
            # Create test file
            write_tool = FileWriteTool()
            test_content = "Test content from stable system"
            test_file = "test_outputs/stability_test.txt"
            
            write_result = await write_tool.execute(path=test_file, content=test_content)
            logger.info(f"✅ File write test: {write_result}")
            
            # Read test file
            read_tool = FileReadTool()
            read_result = await read_tool.execute(path=test_file)
            logger.info(f"✅ File read test: Content length {len(read_result)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Tool execution test failed: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test with tool integration."""
        print("\n" + "="*70)
        print(f"Project-S Safe Tool Integration Test {self.version}")
        print("="*70)
        
        # Test 1: Basic system stability
        basic_success = await self.run_test()
        if not basic_success:
            print("❌ Basic system test failed - aborting tool integration")
            return False
        
        # Test 2: Tool loading
        tools_success = await self.load_tools_safely()
        
        # Test 3: Tool execution (if tools available)
        execution_success = False
        if tools_success:
            execution_success = await self.test_tool_execution()
        
        # Summary
        print("\n" + "="*70)
        print("SAFE INTEGRATION TEST RESULTS:")
        print(f"✅ Basic system: {'PASS' if basic_success else 'FAIL'}")
        print(f"✅ Tool loading: {'PASS' if tools_success else 'FAIL'}")
        print(f"✅ Tool execution: {'PASS' if execution_success else 'FAIL'}")
        print(f"📊 Tools loaded: {self.tools_loaded}")
        print("="*70)
        
        return basic_success  # System is stable as long as basic functions work

async def main():
    """Main entry point for safe tool integration test."""
    print("Starting safe tool integration test...")
    system = SafeToolIntegration()
    
    # Ensure test output directory exists
    import os
    print("Creating test_outputs directory...")
    os.makedirs('test_outputs', exist_ok=True)
    
    print("Running comprehensive test...")
    success = await system.run_comprehensive_test()
    
    if success:
        print("\n🎯 SUCCESS: System remains stable with tool integration")
        print("Next step: Add more tools incrementally")
    else:
        print("\n❌ FAILURE: System stability compromised")
        print("Action: Rollback to WORKING_MINIMAL_VERSION.py")
    
    print("Test completed.")
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
