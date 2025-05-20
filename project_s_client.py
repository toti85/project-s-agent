"""
Project-S Python Client SDK (váz)
Egyszerűsített aszinkron kliens a Project-S API Agent-hez.
"""
import httpx
from typing import Optional, Dict, Any, List

class ProjectSClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def create_conversation(self, title: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict:
        payload = {"title": title, "metadata": metadata}
        resp = await self.client.post("/api/conversations", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def list_conversations(self) -> List[Dict]:
        resp = await self.client.get("/api/conversations")
        resp.raise_for_status()
        return resp.json()

    async def get_conversation(self, conv_id: str) -> Dict:
        resp = await self.client.get(f"/api/conversations/{conv_id}")
        resp.raise_for_status()
        return resp.json()

    async def add_message(self, conv_id: str, role: str, content: str, command: Optional[Dict] = None) -> Dict:
        payload = {
            "conversation_id": conv_id,
            "role": role,
            "content": content,
            "command": command,
        }
        resp = await self.client.post(f"/api/conversations/{conv_id}/messages", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def list_messages(self, conv_id: str) -> List[Dict]:
        resp = await self.client.get(f"/api/conversations/{conv_id}/messages")
        resp.raise_for_status()
        return resp.json()

    async def get_context(self, conv_id: str, limit: int = 20) -> List[Dict]:
        resp = await self.client.get(f"/api/conversations/{conv_id}/context", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()

    async def execute_command(self, conv_id: str, command: Dict) -> Dict:
        resp = await self.client.post(f"/api/conversations/{conv_id}/execute", json=command)
        resp.raise_for_status()
        return resp.json()

    async def execute_direct(self, command: Dict) -> Dict:
        resp = await self.client.post("/api/execute", json=command)
        resp.raise_for_status()
        return resp.json()

    # --- Segédfüggvények típusos parancsokhoz ---
    async def file_read(self, conv_id: str, path: str) -> Dict:
        cmd = {"type": "FILE", "action": "read", "path": path}
        return await self.execute_command(conv_id, cmd)

    async def execute_cmd(self, conv_id: str, cmdline: str) -> Dict:
        cmd = {"type": "CMD", "cmd": cmdline}
        return await self.execute_command(conv_id, cmd)

    async def close(self):
        await self.client.aclose()

# Példa használat:
# import asyncio
# client = ProjectSClient()
# conv = await client.create_conversation("Teszt")
# await client.add_message(conv["id"], "user", "Mi a helyzet?")
# await client.close()
