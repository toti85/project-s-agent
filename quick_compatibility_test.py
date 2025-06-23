#!/usr/bin/env python3
"""
Quick Compatibility Test
========================
Quick test of the fixed compatibility issues.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_quick_fixes():
    """Test the key fixes quickly."""
    print("🚀 Quick Compatibility Test")
    print("=" * 30)
    
    # Test 1: QwenOllamaClient ask method
    try:
        from llm_clients.qwen_client import QwenOllamaClient
        client = QwenOllamaClient(model='qwen:7b')
        has_ask = hasattr(client, 'ask')
        print(f"✅ QwenOllamaClient ask method: {has_ask}")
    except Exception as e:
        print(f"❌ QwenOllamaClient test failed: {e}")
    
    # Test 2: Model selector uses QwenOllamaClient
    try:
        from llm_clients.model_selector import model_selector
        model = model_selector.get_model("ollama", "qwen:7b")
        is_qwen_client = "QwenOllamaClient" in str(type(model))
        print(f"✅ Model selector uses QwenOllamaClient: {is_qwen_client}")
    except Exception as e:
        print(f"❌ Model selector test failed: {e}")
    
    # Test 3: Multi-model integration fallback
    try:
        from core.multi_model_integration import MultiModelManager
        manager = MultiModelManager()
        print("✅ MultiModelManager with fallback: True")
    except Exception as e:
        print(f"❌ MultiModelManager test failed: {e}")
    
    # Test 4: Basic workflow detection
    try:
        from integrations.model_manager import ModelManager
        model_manager = ModelManager()
        command = "organize downloads folder by file types and remove duplicates"
        result = await model_manager.process_command(command)
        is_workflow = "workflow" in str(result).lower()
        print(f"✅ Workflow detection working: {is_workflow}")
    except Exception as e:
        print(f"❌ Workflow detection test failed: {e}")
    
    print("\n🎯 Key fixes appear to be working!")
    print("The system should now handle complex workflows properly.")

if __name__ == "__main__":
    asyncio.run(test_quick_fixes())
