#!/usr/bin/env python3
"""
Quick status check for the autonomous system
"""

import os
import sys
import time
from datetime import datetime

def check_autonomous_status():
    """Check if autonomous system is running and show key metrics"""
    
    print("🔍 PROJECT-S AUTONOMOUS SYSTEM STATUS CHECK")
    print("=" * 50)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if autonomous system files exist
    autonomous_files = [
        "autonomous_main.py",
        "core/autonomous_manager.py",
        "test_autonomous_capabilities.py"
    ]
    
    print("📁 Autonomous System Files:")
    for file_path in autonomous_files:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"  ✅ {file_path} ({size} bytes)")
        else:
            print(f"  ❌ {file_path} (NOT FOUND)")
    
    print()
    
    # Check diagnostics directory
    diagnostics_dir = "diagnostics"
    if os.path.exists(diagnostics_dir):
        print(f"📊 Diagnostics Directory: ✅ {diagnostics_dir}/")
        files = os.listdir(diagnostics_dir)
        print(f"  📄 Contains {len(files)} files")
        if files:
            print("  Recent files:")
            for file in sorted(files)[-5:]:  # Show last 5 files
                print(f"    - {file}")
    else:
        print(f"📊 Diagnostics Directory: ❌ {diagnostics_dir}/ (NOT FOUND)")
    
    print()
    
    # Check if dashboard is accessible
    try:
        import requests
        response = requests.get("http://localhost:7777", timeout=2)
        print("🌐 Dashboard Status: ✅ Accessible at http://localhost:7777")
    except:
        print("🌐 Dashboard Status: ❌ Not accessible or not running")
    
    print()
    
    # Check core modules
    core_modules = [
        "core.event_bus",
        "core.diagnostics",
        "core.cognitive_core_langgraph",
        "core.autonomous_manager"
    ]
    
    print("🧠 Core Modules Status:")
    for module in core_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module} - {str(e)}")
        except Exception as e:
            print(f"  ⚠️ {module} - {str(e)}")
    
    print()
    print("✅ Status check complete!")

if __name__ == "__main__":
    check_autonomous_status()
