#!/usr/bin/env python3
"""
Test script to simulate exactly what happens in the main system
"""
import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s - %(message)s')

async def test_main_system_intelligence():
    """Test the exact intelligence_command_parser function from main_multi_model.py"""
    
    print("=== Testing Main System Intelligence Integration ===\n")
    
    # Import the exact function from main_multi_model
    from main_multi_model import intelligent_command_parser
    
    test_commands = [
        "hozz létre intelligence_test.txt fájlt",
        "listázd ki a fájlokat"
    ]
    
    for command in test_commands:
        print(f"\n--- Testing main system with: '{command}' ---")
        try:
            # This is the exact call from main_multi_model.py
            parsed_command = await intelligent_command_parser(command)
            
            print(f"✅ Main system analysis successful:")
            print(f"  Type: {parsed_command.get('type', 'N/A')}")
            print(f"  Operation: {parsed_command.get('operation', 'N/A')}")
            print(f"  Confidence: {parsed_command.get('confidence', 0):.2%}")
            print(f"  Confidence Level: {parsed_command.get('confidence_level', 'N/A')}")
            print(f"  Matched Patterns: {parsed_command.get('matched_patterns', [])}")
            
            # This should show what the main system would display
            confidence = parsed_command.get("confidence", 0.0)
            confidence_level = parsed_command.get("confidence_level", "Unknown")
            print(f"\n🎯 Intent Analysis: {parsed_command['type']} ({confidence:.0%} confidence - {confidence_level})")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_main_system_intelligence())
