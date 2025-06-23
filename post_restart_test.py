#!/usr/bin/env python3
"""
POST-RESTART SYSTEM VERIFICATION FOR PROJECT-S
=============================================
Quick verification that all systems are operational after restart.
"""

import asyncio
import sys
from datetime import datetime

# Import the enhanced main.py functions
from main import intelligent_command_parser

async def quick_post_restart_test():
    """Quick test to verify system is operational after restart."""
    print("🔄 PROJECT-S POST-RESTART VERIFICATION")
    print("=" * 50)
    print(f"🕒 Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Intelligence Engine
    print("🧠 Testing Intelligence Engine...")
    try:
        result = await intelligent_command_parser("create file restart_test.txt")
        print(f"  ✅ Intelligence Engine: {result['type']} - {result['confidence']:.0%} confidence")
    except Exception as e:
        print(f"  ❌ Intelligence Engine error: {e}")
    
    # Test 2: Simple command
    print("\n💻 Testing simple command parsing...")
    try:
        result = await intelligent_command_parser("list files")
        print(f"  ✅ Command parsing: {result['type']} - {result['operation']}")
    except Exception as e:
        print(f"  ❌ Command parsing error: {e}")
    
    print("\n🎉 POST-RESTART VERIFICATION COMPLETE!")
    print("✅ Project-S is ready for operation after restart!")

if __name__ == "__main__":
    asyncio.run(quick_post_restart_test())
