#!/usr/bin/env python3
"""
Simple test to verify analyzer can run and create files
"""
import os
from datetime import datetime

print("Starting simple test...")

# Test 1: Create directory
try:
    os.makedirs('test_analysis_output', exist_ok=True)
    print("✅ Directory created successfully")
except Exception as e:
    print(f"❌ Directory creation failed: {e}")

# Test 2: Write file
try:
    with open('test_analysis_output/test_file.txt', 'w', encoding='utf-8') as f:
        f.write(f"Test successful at {datetime.now()}")
    print("✅ File creation successful")
except Exception as e:
    print(f"❌ File creation failed: {e}")

# Test 3: Check if we can import WebPageFetchTool
try:
    import sys
    sys.path.append('.')
    from tools.web_tools import WebPageFetchTool
    print("✅ WebPageFetchTool import successful")
except Exception as e:
    print(f"❌ WebPageFetchTool import failed: {e}")

print("Test completed!")
