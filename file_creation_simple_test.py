import asyncio
import os

async def test_simple_file_creation():
    from core.ai_command_handler import AICommandHandler
    handler = AICommandHandler()
    # Simulate a FILE command to create a simple txt file
    command = {
        "type": "FILE",
        "command": {
            "action": "write",
            "filename": "hello_simple.txt",
            "content": "Egyszerű szöveg."
        }
    }
    print("Küldött parancs:", command)
    result = await handler.process_json_command(command)
    print("Eredmény:", result)
    # Ellenőrizzük, hogy a fájl tényleg létrejött-e
    if os.path.exists("hello_simple.txt"):
        print("✅ SIKER: hello_simple.txt létrejött!")
        with open("hello_simple.txt", encoding="utf-8") as f:
            print("Tartalom:", f.read())
    else:
        print("❌ HIBA: hello_simple.txt NEM jött létre!")

if __name__ == "__main__":
    asyncio.run(test_simple_file_creation())
