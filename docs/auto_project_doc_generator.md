# Automatikus Projekt Dokumentáció Generáló

## Áttekintés

Az Automatikus Projekt Dokumentáció Generáló egy specializált alrendszere a Project-S hibrid rendszernek, amely képes egy projekt teljes struktúrájának elemzésére és dokumentáció automatikus létrehozására. A rendszer több AI modellt használ különböző elemzési feladatok végrehajtására, így biztosítva a részletes és pontos projektdokumentációt.

## Fő jellemzők

- **Projekt Struktúra Analízis**: Automatikusan feltérképezi a projekt fájlstruktúráját
- **Kód Elemzés**: Azonosítja a főbb osztályokat, függvényeket és komponenseket
- **Többmodelles AI Elemzés**: GPT-4 és Claude modellek specializált feladatokra
- **Strukturált Dokumentáció**: README.md és PROJECT_ANALYSIS.md generálása
- **LangGraph Munkafolyamatok**: Moduláris és bővíthető dokumentációs folyamatok

## Implementációk

A dokumentáció generátor két változatban áll rendelkezésre:

1. **Standard verzió** (`auto_project_doc_generator.py`): 
   - Alapvető dokumentáció generálás
   - Egyszerű folyamat struktúra
   - Hibatűrő működés

2. **LangGraph verzió** (`auto_project_doc_langgraph.py`):
   - Munkafolyamat alapú implementáció
   - Fejlett hibakezelés és állapotkövetés
   - Moduláris felépítés és könnyű bővíthetőség

## Architektúra

A rendszer három fő komponensből áll:

### ProjectStructureAnalyzer

Ez a komponens felelős a projekt fájlstruktúrájának elemzéséért:

- Fájlok és könyvtárak felderítése
- Különböző fájltípusok azonosítása (Python, konfiguráció, dokumentáció)
- Python fájlok mélyebb elemzése (osztályok, függvények, docstringek)

### AIModelIntegration

A különböző AI modellek integrációját végzi:

- GPT-4 használata architektúra és kód struktúra elemzéshez
- Claude használata kód minőség és biztonsági aspektusok értékeléséhez
- Modellek közötti párhuzamos végrehajtás

### DocumentationGenerator

A dokumentációs fájlokat generálja:

- README.md létrehozása a projekt átfogó áttekintésével
- PROJECT_ANALYSIS.md generálása részletes technikai elemzéssel
- Automatikus frissítés a PROJECT_STATUS.md fájlban

## Használat

A dokumentáció generátor közvetlenül futtatható a projekt gyökérkönyvtárából:

```bash
# Standard verzió futtatása
python auto_project_doc_generator.py

# LangGraph verzió futtatása (fejlesztés alatt)
python auto_project_doc_langgraph.py
```

A generált dokumentáció az `outputs` könyvtárban található.

## Jelenlegi Állapot

- A standard verzió (**v0.2.2**) teljesen működőképes
- A LangGraph verzió (**v0.2.3**) fejlesztés alatt áll, jelenleg közvetlen módban működik (nem használja a LangGraph munkafolyamatot)
- A rendszer sikeresen generálja a dokumentációs fájlokat

## Továbbfejlesztési Lehetőségek

- Valós API integráció a szimulált helyett
- További AI modellek integrációja (pl. Gemini, Llama)
- Részletesebb kód minőségi metrikák
- Vizualizációk és diagramok generálása
- Konfigurálható dokumentációs sablonok
