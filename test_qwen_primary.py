#!/usr/bin/env python3
"""
Test Qwen3 256B as Primary AI Supervisor
"""
import asyncio
from core.universal_request_processor import UniversalRequestProcessor

async def test_qwen_primary():
    print("🎯 QWEN3 256B PRIMARY AI FELÜGYELŐ TESZT")
    print("=" * 50)
    
    processor = UniversalRequestProcessor()
    result = await processor.process_request({
        'type': 'ASK',
        'query': 'Te vagy a Qwen3 256B primary AI felügyelő? Mutatkozz be röviden magyarul!'
    })
    
    print(f'✅ Status: {result.get("status", "unknown")}')
    print(f'📝 Response: {result.get("response", "No response")}')
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_qwen_primary())
