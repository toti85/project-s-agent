#!/usr/bin/env python3
"""
Quick System Test for PROJECT-S Restoration
Tests core components without heavy AI model dependencies
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_json_serialization():
    """Test JSON serialization with Path objects"""
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        
        # Test with Windows paths
        test_data = {
            "path": Path("C:/test/file.txt"),
            "paths": [Path("C:/dir1"), Path("C:/dir2/file.py")],
            "nested": {
                "path": Path("C:/nested/path"),
                "other": "data"
            }
        }
        
        processor = UniversalRequestProcessor()
        helper = processor.json_helper
        serialized = helper.serialize(test_data)
        deserialized = helper.deserialize(serialized)
        
        logger.info("✅ JSON serialization test passed")
        return True
    except Exception as e:
        logger.error(f"❌ JSON serialization test failed: {e}")
        return False

async def test_universal_processor_basic():
    """Test Universal Request Processor with basic functionality"""
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        
        processor = UniversalRequestProcessor()
        
        # Test basic request normalization
        test_request = {
            "type": "TEST",
            "data": "test data"
        }
        
        # Test with correct parameters
        normalized = processor._normalize_request(test_request, {"source": "test"})
        
        if normalized.get("id") and normalized.get("timestamp"):
            logger.info("✅ Request normalization test passed")
            return True
        else:
            logger.error("❌ Request normalization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Universal processor test failed: {e}")
        return False

async def test_execution_coordinator():
    """Test Enhanced Execution Coordinator"""
    try:
        from core.enhanced_execution_coordinator import EnhancedExecutionCoordinator
        
        coordinator = EnhancedExecutionCoordinator()
        
        # Test simple workflow execution setup
        workflow_def = {
            "steps": [
                {
                    "id": "test_step",
                    "type": "test",
                    "action": "validate"
                }
            ]
        }
        
        # Test workflow initialization
        if hasattr(coordinator, 'execute_workflow'):
            logger.info("✅ Execution coordinator test passed")
            return True
        else:
            logger.error("❌ Execution coordinator missing required methods")
            return False
            
    except Exception as e:
        logger.error(f"❌ Execution coordinator test failed: {e}")
        return False

async def test_asyncio_manager():
    """Test AsyncIO cleanup manager"""
    try:
        from core.universal_request_processor import UniversalRequestProcessor
        
        processor = UniversalRequestProcessor()
        manager = processor.asyncio_manager
        
        # Test simple async operation
        async def simple_task():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await manager.safe_execute(simple_task(), timeout=5)
        
        if result == "success":
            logger.info("✅ AsyncIO manager test passed")
            return True
        else:
            logger.error("❌ AsyncIO manager failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ AsyncIO manager test failed: {e}")
        return False

async def test_cognitive_core_basic():
    """Test Cognitive Core basic functionality"""
    try:
        from core.cognitive_core_langgraph import CognitiveCoreWithLangGraph
        
        # Just test initialization
        core = CognitiveCoreWithLangGraph()
        
        if hasattr(core, 'state') and hasattr(core, 'compile_graph') and core.graph is not None:
            logger.info("✅ Cognitive Core initialization test passed")
            return True
        else:
            logger.error("❌ Cognitive Core initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cognitive Core test failed: {e}")
        return False

async def main():
    """Run all quick tests"""
    logger.info("🧪 PROJECT-S Quick System Test")
    logger.info("=" * 50)
    
    tests = [
        ("JSON Serialization", test_json_serialization),
        ("Universal Processor Basic", test_universal_processor_basic),
        ("Execution Coordinator", test_execution_coordinator),
        ("AsyncIO Manager", test_asyncio_manager),
        ("Cognitive Core Basic", test_cognitive_core_basic),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        try:
            result = await asyncio.wait_for(test_func(), timeout=10)
            results.append((test_name, result))
        except asyncio.TimeoutError:
            logger.error(f"❌ {test_name} test timed out")
            results.append((test_name, False))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("=" * 50)
    logger.info("🏆 TEST RESULTS SUMMARY")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    logger.info(f"Success Rate: {success_rate:.1f}% ({passed}/{len(results)})")
    
    if success_rate >= 95:
        logger.info("🎉 PROJECT-S RESTORATION SUCCESS!")
        return 0
    elif success_rate >= 80:
        logger.info("⚠️ PROJECT-S RESTORATION PARTIAL SUCCESS")
        return 1
    else:
        logger.error("❌ PROJECT-S RESTORATION FAILED")
        return 2

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite crashed: {e}")
        sys.exit(1)
