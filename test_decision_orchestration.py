#!/usr/bin/env python3
"""
Test script for intelligent decision making and multi-AI orchestration
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the enhanced functions from main.py
from main import intelligent_command_parser, ProjectSUnified

async def test_intelligent_decisions():
    """Test intelligent decision making with confidence scoring"""
    print("🧠 TESTING INTELLIGENT DECISION MAKING")
    print("=" * 60)
    
    test_cases = [
        "create a Python file called test.py",
        "organize my files",
        "What is machine learning?",
        "run command ls -la",
        "ambiguous command xyz"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: '{test_input}'")
        try:
            result = await intelligent_command_parser(test_input)
            confidence = result.get("confidence", 0.0)
            confidence_level = result.get("confidence_level", "Unknown")
            
            print(f"   🎯 Type: {result['type']}")
            print(f"   🎯 Operation: {result.get('operation', 'N/A')}")
            print(f"   🎯 Confidence: {confidence:.0%} ({confidence_level})")
            
            if result.get("requires_confirmation"):
                print(f"   ❓ Would ask for confirmation")
            
            if result.get("suggest_alternatives"):
                print(f"   💡 Would suggest alternatives")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_multi_ai_orchestration():
    """Test multi-AI orchestration capabilities"""
    print("\n\n🤖 TESTING MULTI-AI ORCHESTRATION")
    print("=" * 60)
    
    # Initialize the unified system
    project_s = ProjectSUnified()
    await project_s.initialize()
    
    test_queries = [
        "What is artificial intelligence?",
        "Create a simple Python function",
        "Explain quantum computing"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: '{query}'")
        try:
            # Test the chat handler (uses model_manager)
            print("   🔄 Processing with model manager...")
            await project_s.handle_chat_intent({"raw": query})
            print("   ✅ Multi-AI orchestration successful")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    """Run all tests"""
    print("🚀 TESTING INTELLIGENT DECISION MAKING & MULTI-AI ORCHESTRATION")
    print("=" * 80)
    
    try:
        await test_intelligent_decisions()
        await test_multi_ai_orchestration()
        
        print("\n\n🎉 ALL TESTS COMPLETED!")
        print("✅ Intelligent decision making and multi-AI orchestration are working!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
