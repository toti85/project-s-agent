"""
Minimális teszt a LangGraph integrációs modul betöltésére
"""
import importlib
import sys

def test_import():
    """Megpróbálja importálni a LangGraph integrációs modult"""
    print("LangGraph integrációs modul betöltési teszt...")
    
    try:
        # Próbáljuk betölteni a modult
        module = importlib.import_module("integrations.langgraph_integration")
        
        print(f"Modul sikeresen betöltve: {module.__name__}")
        
        # Ellenőrizzük a GraphState osztályt
        if hasattr(module, "GraphState"):
            print("GraphState osztály megtalálva")
            print(f"GraphState mezők: {module.GraphState.__annotations__ if hasattr(module.GraphState, '__annotations__') else 'nem érhetőek el'}")
        else:
            print("GraphState osztály nem található")
        
        # Ellenőrizzük a LangGraphIntegrator osztályt
        if hasattr(module, "LangGraphIntegrator"):
            print("LangGraphIntegrator osztály megtalálva")
        else:
            print("LangGraphIntegrator osztály nem található")
        
        return True
    except Exception as e:
        print(f"Hiba a modul betöltésekor: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_import()
    print(f"\nTeszt eredmény: {'SIKERES' if success else 'SIKERTELEN'}")
    sys.exit(0 if success else 1)
