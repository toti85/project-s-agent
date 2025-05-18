from llm_clients.openrouter_client import OpenRouterClient
import asyncio

async def test():
    client = OpenRouterClient(model='qwen/qwen3-235b-a22b:free')
    result = await client.generate('Mi Magyarország fővárosa?')
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
