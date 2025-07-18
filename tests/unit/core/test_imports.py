
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from tools.tool_registry import tool_registry
    print('Tool registry import successful')
except Exception as e:
    print(f'Error importing tool_registry: {e}')

try:
    from tools import FileReadTool
    print('FileReadTool import successful')
except Exception as e:
    print(f'Error importing FileReadTool: {e}')

print('Test complete')

