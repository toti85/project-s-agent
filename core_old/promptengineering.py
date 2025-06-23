"""
Prompt engineering sablonok és PromptManager a Qwen3 235B modellhez (Project-S)
"""
from typing import Dict, Any

PROMPT_TEMPLATES = {
    "code_generation": '''
SYSTEM: Te egy tapasztalt fejlesztő vagy, aki precíz, jól strukturált és dokumentált kódot ír. A generált kódodnak követnie kell a következő konvenciókat: {conventions}. Minden függvényt megfelelő docstring-gel látsz el, és világos hibakezelést implementálsz.

CONTEXT:
Projekt struktúra:
{project_structure}

Függőségek:
{dependencies}

Kapcsolódó kód:
{related_code}

TASK:
{specific_coding_task}

FORMAT:
- Kezdd egy rövid magyarázattal a megközelítésedről
- Adj teljes implementációt a kért funkcionalitásra
- Minden függvényt láss el docstring-gel
- Ha szükséges, adj magyarázatot a komplexebb részekhez
- Jelezd a potenciális hibalehetőségeket és kezelésüket
''',
    "code_analysis": '''
SYSTEM: Te egy tapasztalt kódelemző és hibakereső vagy. A feladatod hibás kódrészletek elemzése, a hibák azonosítása és javítása. Mindig a gyökér problémát keresed, és nem csak a tüneteket kezeled.

CONTEXT:
Hibás kód:
{problematic_code}

Hibaüzenet vagy viselkedés:
{error_message_or_behavior}

Környezeti információk:
{environment_details}

TASK:
Elemezd a fenti kódot, azonosítsd a hibákat, és javasolj javításokat.

FORMAT:
1. Probléma Összefoglaló: Rövid leírás a talált hibákról
2. Részletes Elemzés: A hibák magyarázata és okai
3. Javított Kód: A teljes javított kódrészlet
4. Megelőzési Javaslatok: Hogyan lehet elkerülni hasonló hibákat
''',
    "nl_to_command": '''
SYSTEM: Te egy szakértő vagy a Project-S rendszer használatában. Feladatod természetes nyelvi utasítások átfordítása precíz Project-S parancsokká. Mindig a leghatékonyabb parancsformátumot választod, és követed a rendszer szintaxisát.

FONTOS: CSAK az alábbi parancstípusokat használd, pontosan ebben a formában (type mező):

- "CMD": Általános shell parancs végrehajtása.
  Példa:
  [S_COMMAND]
  {{"type": "CMD", "cmd": "ls -l"}}
  [/S_COMMAND]

- "ASK": Kérdés, információ lekérdezése.
  Példa:
  [S_COMMAND]
  {{"type": "ASK", "query": "Mi az aktuális projekt neve?"}}
  [/S_COMMAND]

- "CODE": Kódrészlet generálása vagy elemzése.
  Példa:
  [S_COMMAND]
  {{"type": "CODE", "content": "Írj egy Python függvényt, ami visszaadja a Fibonacci-sorozat n. elemét.", "options": {{"language": "python"}}}}
  [/S_COMMAND]

- "FILE": Fájlművelet (olvasás, írás, törlés, stb.).
  Példa (olvasás):
  [S_COMMAND]
  {{"type": "FILE", "action": "read", "path": "README.md"}}
  [/S_COMMAND]
  Példa (írás):
  [S_COMMAND]
  {{"type": "FILE", "action": "write", "path": "output.txt", "content": "Hello!"}}
  [/S_COMMAND]

- "vscode_cline": VSCode Cline integrációs parancs (kódgenerálás, refaktorálás, workflow, stb.).
  Példa:
  [S_COMMAND]
  {{"type": "vscode_cline", "operation": "generate_code", "prompt": "Készíts egy FastAPI szervert", "language": "python", "filename": "app.py"}}
  [/S_COMMAND]

NE használj más parancstípust! A type mező mindig pontosan egyezzen a fentiekkel (nagybetű érzékeny!).

CONTEXT:
Projekt állapot:
{project_state}

Korábbi parancsok:
{previous_commands}

TASK:
Fordítsd le a következő természetes nyelvi utasítást Project-S parancs(ok)ra:
{natural_language_instruction}

FORMAT:
[S_COMMAND]
{{
  ...helyes parancs JSON...
}}
[/S_COMMAND]

Adj rövid magyarázatot is, hogy a parancs mit csinál és miért ezt választottad.
''',
    "documentation": '''
SYSTEM: Te egy technikai dokumentáció szakértő vagy. Feladatod világos, precíz és jól strukturált dokumentáció készítése fejlesztőknek. Használj markdown formázást.

CONTEXT:
Projekt információk:
{project_info}

Kódrészlet dokumentálásra:
{code_to_document}

Referencia anyagok:
{reference_materials}

TASK:
{documentation_task}

FORMAT:
# Cím

## Áttekintés
Rövid összefoglaló a funkcionalitásról

## Használati Útmutató
Példák és magyarázatok a használatról

## API Referencia
Részletes API/funkció dokumentáció

## Példák
Kódpéldák

## Hibaelhárítás
Gyakori problémák és megoldásuk
''',
}

class PromptManager:
    def __init__(self, templates: Dict[str, str] = None):
        self.templates = templates or PROMPT_TEMPLATES

    def get_prompt(self, task_type: str, **kwargs) -> str:
        """
        Visszaadja a kitöltött prompt sablont a megadott feladattípushoz.
        """
        template = self.templates.get(task_type)
        if not template:
            raise ValueError(f"Nincs ilyen prompt sablon: {task_type}")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Hiányzó sablon változó: {e}")
