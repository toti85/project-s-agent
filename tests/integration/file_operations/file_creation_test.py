import asyncio
import os

async def test_file_creation():
    from core.ai_command_handler import AICommandHandler
    handler = AICommandHandler()
    # Simulate a FILE command to create a file with a specific name
    command = {
        "type": "FILE",
        "command": {
            "action": "write",
            "filename": "test123.txt",
            "content": "Ez egy teszt fájl."
        }
    }
    print("Küldött parancs:", command)
    result = await handler.process_json_command(command)
    print("Eredmény:", result)
    # Ellenőrizzük, hogy a fájl tényleg létrejött-e
    if os.path.exists("test123.txt"):
        print("✅ SIKER: test123.txt létrejött!")
        with open("test123.txt", encoding="utf-8") as f:
            print("Tartalom:", f.read())
    else:
        print("❌ HIBA: test123.txt NEM jött létre!")

if __name__ == "__main__":
    asyncio.run(test_file_creation())
