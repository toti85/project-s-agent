#!/usr/bin/env python3
"""
Final verification test - simulate user input to main system
"""
import asyncio
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_main_system():
    """Test the complete main system flow with simulated user input"""
    
    print("=== Final Full System Test ===\n")
    
    # Import the main interactive function
    from main_multi_model import interactive_main
    
    # Simulate user input: command + exit
    test_input = "hozz létre intelligence_test.txt fájlt\nexit\n"
    
    # Capture output
    output_capture = StringIO()
    
    try:
        # Mock input to simulate user commands
        with patch('builtins.input', side_effect=test_input.strip().split('\n')):
            with patch('sys.stdout', output_capture):
                await interactive_main()
    except SystemExit:
        pass  # Normal exit is expected
    except Exception as e:
        print(f"System completed with: {e}")
    
    # Get captured output
    captured_output = output_capture.getvalue()
    print("=== Captured Main System Output ===")
    print(captured_output)
    
    # Check for Phase 2 features in output
    phase2_indicators = [
        "🎯 Intent Analysis:",
        "confidence",
        "Very High",
        "FILE_OPERATION"
    ]
    
    found_features = []
    for indicator in phase2_indicators:
        if indicator in captured_output:
            found_features.append(indicator)
    
    print(f"\n=== Phase 2 Feature Detection ===")
    print(f"Found {len(found_features)}/{len(phase2_indicators)} Phase 2 indicators:")
    for feature in found_features:
        print(f"✅ {feature}")
    
    missing_features = set(phase2_indicators) - set(found_features)
    for feature in missing_features:
        print(f"❌ {feature}")

if __name__ == "__main__":
    asyncio.run(test_full_main_system())
