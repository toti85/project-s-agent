#!/usr/bin/env python3
"""
Real AI test through unified interface
"""

import asyncio
import os
import sys

# Set API key
os.environ["OPENROUTER_API_KEY"] = "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"

from main import ProjectSUnified

async def test_unified_ai():
    """Test AI through the unified interface."""
    print("🧪 TESTING AI THROUGH UNIFIED INTERFACE")
    print("=" * 60)
    
    project_s = ProjectSUnified()
    
    # Initialize
    if not await project_s.initialize():
        print("❌ Failed to initialize")
        return
    
    # Test AI chat
    print("📋 Testing AI Chat Intent")
    test_data = {
        'raw': 'What is artificial intelligence? Explain briefly.',
        'confidence': 'high'
    }
    
    print(f"   Query: '{test_data['raw']}'")
    print("   🔄 Processing through unified interface...")
    
    await project_s.handle_chat_intent(test_data)
    
    await project_s.cleanup()

if __name__ == "__main__":
    asyncio.run(test_unified_ai())
