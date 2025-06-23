#!/usr/bin/env python3
"""
CLI indentációs hiba javítása
"""

# Javítjuk az indentációs hibát a cli_main.py fájlban
with open('cli_main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 165 (0-indexed: 164) - javítjuk a túl sok szóközt
lines[164] = '        print("\\n🌐 Web Commands:")\\n'

with open('cli_main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Fixed CLI indentation error on line 165')
print('✅ Ready to test CLI commands')
