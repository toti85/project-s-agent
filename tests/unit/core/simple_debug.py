print("=== SIMPLE DEBUG TEST ===")

try:
    print("1. Testing basic imports...")
    from integrations.model_manager import model_manager
    print("✅ model_manager imported successfully")
    
    from tools.tool_registry import tool_registry
    print("✅ tool_registry imported successfully")
    
    print(f"Available tools: {list(tool_registry.tools.keys())}")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()

print("=== TEST COMPLETE ===")
