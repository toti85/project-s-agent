#!/usr/bin/env python3
"""
Project-S többféle fájl típus teszt
"""

from integrations.model_manager import ModelManager
import os
import json

def test_multiple_file_types():
    print("🚀 TÖBBFÉLE FÁJL TÍPUS TESZT")
    print("=" * 50)
    
    mm = ModelManager()
    
    # 1. JSON fájl teszt
    print("📊 JSON fájl teszt...")
    result1 = mm.process_ai_request('Hozz létre egy test_data.json fájlt JSON tartalommal')
    print(f"JSON eredmény: {result1.get('execution_result', {})}")
    
    # 2. Python fájl teszt  
    print("\n🐍 Python fájl teszt...")
    result2 = mm.process_ai_request('Készíts egy hello.py fájlt print Hello World kóddal')
    print(f"Python eredmény: {result2.get('execution_result', {})}")
    
    # 3. Mappa elemzés teszt
    print("\n📂 Mappa elemzés teszt...")
    result3 = mm.process_ai_request('SHELL parancs: listázd a mappában lévő fájlokat')
    print(f"Shell eredmény: {result3.get('execution_result', {})}")
    
    # 4. Fájlok ellenőrzése
    print("\n📋 Létrehozott fájlok:")
    for f in sorted([f for f in os.listdir('.') if f.endswith(('.json', '.py', '.txt'))]):
        size = os.path.getsize(f)
        print(f"   ✅ {f} ({size} bytes)")
        
        # Tartalom minta
        if f.endswith('.txt') and size < 200:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()[:100]
                print(f"      📄 Tartalom: {content}...")
    
    print("\n🎯 TESZT BEFEJEZVE")

if __name__ == "__main__":
    test_multiple_file_types()
