# Ellenőrzi a LangGraph könyvtár elérhetőségét
try:
    import langgraph
    print("LangGraph elérhető")
    try:
        print(f"LangGraph verzió: {langgraph.__version__}")
    except AttributeError:
        print("LangGraph verzió nem elérhető")
except ImportError:
    print("LangGraph NEM elérhető")
