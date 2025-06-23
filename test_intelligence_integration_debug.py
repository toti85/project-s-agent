#!/usr/bin/env python3
"""
Debug script to test intelligence engine integration in main system
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_intelligence_integration():
    """Test the intelligence engine integration exactly as used in main_multi_model.py"""
    
    print("=== Testing Intelligence Engine Integration ===\n")
    
    # Test 1: Import the intelligence engine
    try:
        from core.intelligence_engine import intelligence_engine
        print("✅ Intelligence engine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import intelligence engine: {e}")
        return
    
    # Test 2: Test the exact function call used in main_multi_model.py
    test_commands = [
        "hozz létre intelligence_test.txt fájlt",
        "listázd ki a fájlokat",
        "create a file called test.txt"
    ]
    
    for command in test_commands:
        print(f"\n--- Testing command: '{command}' ---")
        try:
            # This is the exact call from main_multi_model.py line 536
            intent_match = await intelligence_engine.analyze_intent_with_confidence(command)
            
            print(f"✅ Analysis successful:")
            print(f"  Intent Type: {intent_match.intent_type}")
            print(f"  Operation: {intent_match.operation}")
            print(f"  Confidence: {intent_match.confidence:.2%}")
            print(f"  Matched Patterns: {intent_match.matched_patterns}")
            print(f"  Parameters: {intent_match.parameters}")
            
            # Test confidence report formatting
            confidence_report = intelligence_engine.format_confidence_report(intent_match)
            print(f"  Confidence Report:\n{confidence_report}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_intelligence_integration())
