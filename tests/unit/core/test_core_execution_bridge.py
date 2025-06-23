import asyncio
from integrations.model_manager import model_manager

async def main():
    print("=== CORE EXECUTION BRIDGE TESZT ===")
    query = "Hozz létre test.txt fájlt, tartalommal: Ez egy Project-S teszt!"
    result = await model_manager.execute_task_with_core_system(query)
    print("Eredmény:")
    print(result)
    print("\nEllenőrzés: Létrejött-e a test.txt?")
    try:
        with open("test.txt", "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ test.txt létezik, tartalom: {content[:100]}")
    except Exception as e:
        print(f"❌ test.txt NEM jött létre! Hiba: {e}")

if __name__ == "__main__":
    asyncio.run(main())
