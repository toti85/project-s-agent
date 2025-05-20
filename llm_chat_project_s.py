"""
Egyszerű chat-szerű CLI, ahol szabad szövegesen írhatsz, a Qwen3 4B (OpenRouter) lefordítja Project-S parancsra, a Project-S végrehajtja, és visszakapod az eredményt.
"""
import asyncio
from project_s_client import ProjectSClient
from llm_clients.openrouter_client import OpenRouterClient
from core.promptengineering import PromptManager

async def main():
    client = ProjectSClient()
    llm = OpenRouterClient(model="qwen/qwen3-4b:free")
    prompt_manager = PromptManager()
    
    # Új beszélgetés indítása
    conv = await client.create_conversation("LLM chat teszt")
    conv_id = conv["id"]
    print(f"\nProject-S LLM chat teszt (Qwen3 4B)\nBeszélgetés ID: {conv_id}\nKilépéshez: exit\n")
    
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"): break
        # 1. Prompt engineering: szövegből Project-S parancs prompt
        command_prompt = prompt_manager.get_prompt(
            "nl_to_command",
            natural_language_instruction=user_input,
            project_state="",  # Itt adhatsz át projekt állapotot, ha van
            previous_commands=""
        )
        # 2. LLM: kérés Qwen3-hoz
        llm_response = await llm.generate(command_prompt)
        import re
        text = llm_response["text"] if isinstance(llm_response, dict) else str(llm_response)
        # Keressük az összes [S_COMMAND] blokkot
        matches = re.findall(r"\[S_COMMAND\](.*?)\[/S_COMMAND\]", text, re.DOTALL)
        if not matches:
            print(f"[LLM válasz értelmezési hiba]: Nincs S_COMMAND blokk!\n{llm_response}")
            continue
        for block in matches:
            block = block.strip()
            try:
                import json
                command = json.loads(block)
                # --- Command type normalization ---
                if isinstance(command, dict):
                    if command.get("type") == "file_list":
                        command["type"] = "FILE"
                    # Add more normalization rules here if needed
                # 4. Project-S API: parancs végrehajtása
                result = await client.execute_command(conv_id, command)
                print(f"[Eredmény]: {result}\n")
            except Exception as e:
                print(f"[LLM válasz értelmezési hiba]: {e}\n{block}")
                continue

if __name__ == "__main__":
    asyncio.run(main())
