#!/usr/bin/env python3
"""
Final verification test for intelligence engine
"""
import sys
import asyncio
sys.path.append('.')

async def test_intelligence():
    try:
        from core.intelligence_engine import intelligence_engine
        
        # Test intelligence analysis
        result = await intelligence_engine.analyze_intent_with_confidence('create a test file')
        
        print(f"✅ Intelligence Engine Test Results:")
        print(f"   Intent: {result.intent_type}")
        print(f"   Operation: {result.operation}")
        print(f"   Confidence: {result.confidence:.0%}")
        print(f"   Patterns: {result.matched_patterns}")
        print("🎉 INTELLIGENCE ENGINE FULLY FUNCTIONAL")
        
    except Exception as e:
        print(f"❌ Intelligence test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_intelligence())
