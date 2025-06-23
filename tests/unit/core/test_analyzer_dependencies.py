"""
Quick test for Website Analyzer dependencies
"""
import sys
import os
from pathlib import Path

print("Testing Website Analyzer dependencies...")

# Setup paths
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Test 1: Basic imports
try:
    from core.event_bus import event_bus
    from core.error_handler import ErrorHandler
    print("✅ Core components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import core components: {e}")
    sys.exit(1)

# Test 2: File tools
try:
    from tools.file_tools import FileReadTool, FileWriteTool
    print("✅ File tools imported successfully")
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"❌ File tools not available: {e}")
    TOOLS_AVAILABLE = False

# Test 3: Web tools
try:
    from tools.web_tools import WebPageFetchTool
    print("✅ Web tools imported successfully")
    WEB_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Web tools not available: {e}")
    WEB_TOOLS_AVAILABLE = False

print(f"\nDependency Status:")
print(f"File Tools Available: {TOOLS_AVAILABLE}")
print(f"Web Tools Available: {WEB_TOOLS_AVAILABLE}")
print(f"Ready for Website Analysis: {TOOLS_AVAILABLE and WEB_TOOLS_AVAILABLE}")

if TOOLS_AVAILABLE and WEB_TOOLS_AVAILABLE:
    print("\n✅ All dependencies are available!")
    print("You can proceed with website analysis.")
else:
    print("\n❌ Some dependencies are missing.")
    print("Website analysis functionality will be limited.")
