"""
Project-S Qwen3 Integráció Közvetlen API Teszt
- Prompt engineering sablonok
- Qwen3 generálás
- Válaszok validálása
"""
from core.promptengineering import PromptManager
from llm_clients.openrouter_client import OpenRouterClient
import asyncio

async def main():
    prompt_manager = PromptManager()
    qwen_client = OpenRouterClient()

    # 1. Kódgenerálás teszt
    code_gen_context = {
        "conventions": "Python 3.8+, PEP8, FastAPI, hibakezelés",
        "project_structure": "Project-S alapstruktúra...",
        "dependencies": "Python 3.8+, FastAPI, SQLite",
        "related_code": "Kapcsolódó kódrészlet...",
        "specific_coding_task": "Készíts egy függvényt, ami beolvassa a config.yaml fájlt és visszaadja Python dict-ként."
    }
    prompt = prompt_manager.get_prompt("code_generation", **code_gen_context)
    print("--- Kódgenerálás prompt ---\n", prompt)
    response = await qwen_client.generate(prompt)
    print("\n--- Kódgenerálás válasz ---\n", response)

    # 2. Kódelemzés teszt
    code_analysis_context = {
        "problematic_code": "def add(a, b):\nreturn a + b\nprint(add(2))",
        "error_message_or_behavior": "TypeError: add() missing 1 required positional argument: 'b'",
        "environment_details": "Python 3.10, Windows 11"
    }
    prompt = prompt_manager.get_prompt("code_analysis", **code_analysis_context)
    print("\n--- Kódelemzés prompt ---\n", prompt)
    response = await qwen_client.generate(prompt)
    print("\n--- Kódelemzés válasz ---\n", response)

    # 3. Természetes nyelv → parancs konverzió teszt
    nl2cmd_context = {
        "project_state": "Projekt-S, üres workspace, nincs config fájl",
        "previous_commands": "",
        "natural_language_instruction": "Hozz létre egy új Python projektet, amiben van egy main.py és egy requirements.txt."
    }
    prompt = prompt_manager.get_prompt("nl_to_command", **nl2cmd_context)
    print("\n--- NL→Command prompt ---\n", prompt)
    response = await qwen_client.generate(prompt)
    print("\n--- NL→Command válasz ---\n", response)

    # 4. Dokumentáció generálás teszt
    doc_context = {
        "project_info": "Project-S, AI agent framework",
        "code_to_document": "def foo(x):\n    return x * 2",
        "reference_materials": "",
        "documentation_task": "Dokumentáld a foo függvényt."
    }
    prompt = prompt_manager.get_prompt("documentation", **doc_context)
    print("\n--- Dokumentáció prompt ---\n", prompt)
    response = await qwen_client.generate(prompt)
    print("\n--- Dokumentáció válasz ---\n", response)

if __name__ == "__main__":
    asyncio.run(main())
