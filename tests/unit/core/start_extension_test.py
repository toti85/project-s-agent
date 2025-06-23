"""
start_extension_test.py
Script to initialize the system and prepare for Chrome extension testing.
"""

import asyncio
from run import initialize_system
from interfaces.api_server import api_server

async def main():
    # Initialize the system (starts API server and all components)
    await initialize_system()
    # Notify user
    print('=' * 80)
    print('A RENDSZER KÉSZ A CHROME BŐVÍTMÉNY TESZTELÉSÉRE')
    print('API szerver fut a http://localhost:8000 címen')
    print('Telepítsd a Chrome bővítményt a chrome://extensions oldalon')
    print('Majd nyiss meg egy Claude vagy ChatGPT oldalt a teszteléshez')
    print('=' * 80)
    # Keep the program alive
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Rendszer leállítva.')