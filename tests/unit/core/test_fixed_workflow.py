# Quick test of the fixed intelligent workflow system
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    print("Testing imports...")
    from intelligent_workflow_system_FIXED import WebContentAnalyzer
    print("✅ WebContentAnalyzer imported successfully")
    
    async def test_basic():
        print("Testing basic initialization...")
        analyzer = WebContentAnalyzer()
        result = await analyzer.initialize()
        print(f"✅ Initialization result: {result}")
        return result
    
    print("Running async test...")
    result = asyncio.run(test_basic())
    print(f"✅ Test completed: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
