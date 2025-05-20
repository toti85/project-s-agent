import asyncio
from project_s_client import ProjectSClient

async def main():
    client = ProjectSClient()
    # 1. Beszélgetés létrehozása
    conv = await client.create_conversation("Teszt irányítás")
    print("Beszélgetés:", conv)

    # 2. Fájl olvasás parancs (pl. olvassuk be a README.md-t)
    result = await client.file_read(conv["id"], "README.md")
    print("Fájl olvasás eredmény:", result)

    # 3. Shell parancs (pl. listázd a mappát)
    import os
    shell_cmd = "dir" if os.name == 'nt' else "ls"
    result = await client.execute_cmd(conv["id"], shell_cmd)
    print("Shell parancs eredmény:", result)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
