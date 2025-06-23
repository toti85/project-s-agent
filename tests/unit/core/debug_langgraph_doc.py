"""
Debug script to run the LangGraph documentation generator with detailed error handling.
"""

import traceback
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    # Import the main function
    from auto_project_doc_langgraph import main
    
    # Run the main function and print the output
    import asyncio
    result = asyncio.run(main())
    
    print("\n=== Debug Results ===")
    print(f"Success: {result.get('success', False)}")
    print(f"Output: {result}")
    
except Exception as e:
    print("\n=== ERROR OCCURRED ===")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\n=== Traceback ===")
    traceback.print_exc()
    
    # If it's an import error, print more details
    if isinstance(e, ImportError):
        print("\n=== Import path details ===")
        print(f"Sys.path: {sys.path}")
        
        # Try to import individual modules to narrow down the issue
        modules_to_check = [
            "tools",
            "tools.file_tools",
            "tools.langgraph_integration",
            "auto_project_doc_generator",
            "langgraph.graph"
        ]
        
        print("\n=== Checking individual modules ===")
        for module in modules_to_check:
            try:
                __import__(module)
                print(f"✅ Successfully imported: {module}")
            except Exception as module_error:
                print(f"❌ Failed to import {module}: {str(module_error)}")
