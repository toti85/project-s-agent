# Project-S Minimális Rendszer - Indítási Útmutató

## Rendszerkövetelmények

- Python 3.8 vagy újabb
- Minimális szabad memória: 512MB
- Internetkapcsolat (az AI integrációhoz)

## Előkészületek

1. **Környezet létrehozása**:
   ```bash
   # Virtuális környezet létrehozása
   python -m venv venv
   
   # Virtuális környezet aktiválása (Windows)
   venv\Scripts\activate
   
   # Virtuális környezet aktiválása (Linux/Mac)
   source venv/bin/activate
   ```

2. **Függőségek telepítése**:
   ```bash
   pip install -r requirements_minimal.txt
   ```

3. **API kulcsok beállítása**:
   - OpenAI API kulcs **VAGY** OpenRouter API kulcs szükséges
   
   **Windows**:
   ```
   set OPENAI_API_KEY=your_key_here
   ```
   
   **Linux/Mac**:
   ```
   export OPENAI_API_KEY=your_key_here
   ```
   
   **Alternatíva**: A `start_minimal.bat` vagy `start_minimal.sh` fájlokban is megadhatók.

## Rendszer ellenőrzése

Az indítás előtt ellenőrizd, hogy minden komponens megfelelően van-e telepítve és konfigurálva:

```bash
python check_minimal_system.py
```

## Indítási sorrend

A minimális rendszer több szinten is indítható, növekvő komplexitással:

### 1. Csak alaprendszer (event_bus + error_handler)

```bash
python main_minimal.py
```

Csak az alapvető eseménykezelő rendszert indítja el. Ideális annak tesztelésére, hogy az alaprendszer működik-e.

### 2. LangGraph integráció

```bash
python main_minimal_langgraph.py
```

Az eseménykezelő rendszer mellett a LangGraph munkafolyamat-kezelőt is elindítja. Ez lehetővé teszi a parancsok komplex feldolgozását.

### 3. Teljes minimális rendszer (AI integrációval)

```bash
python main_minimal_full.py
```

A teljes minimális rendszert indítja el, amely tartalmazza az eseménykezelőt, a LangGraph munkafolyamat-kezelőt, és az AI integrációt is. Interaktív parancssor, ahol az AI válaszol a parancsokra.

### Egyszerűsített indítás

Az egyszerűsített indítás használatához:

**Windows**:
```
start_minimal.bat
```

**Linux/Mac**:
```
chmod +x start_minimal.sh
./start_minimal.sh
```

## Komponensek és kommunikáció

A minimális rendszer komponensei és azok kapcsolatai:

1. **Eseménykezelő (event_bus)**
   - A központi kommunikációs csatorna
   - Minden komponens ezen keresztül küld és fogad üzeneteket

2. **Hibakezelő (error_handler)**
   - A hibák egységes kezelése
   - Naplózás és hibajelentés

3. **LangGraph integráció (langgraph_minimal)**
   - Parancsok feldolgozása strukturált munkafolyamatban
   - Állapotgép a parancs feldolgozási logikához

4. **AI integráció (simple_ai)**
   - Kapcsolat az AI szolgáltatóval (OpenAI vagy OpenRouter)
   - Válaszok generálása a parancsokra

## Események és Üzenetfolyam

A minimális rendszer a következő eseményeket használja:

- `command.received`: Új parancs érkezett
- `command.processing`: Parancs feldolgozása folyamatban
- `command.processed`: Parancs feldolgozása befejezve
- `response.generating`: Válasz generálása folyamatban
- `response.ready`: Válasz kész

## Hibaelhárítás

### API kulcs problémák

Ha az "API hiba történt" üzenetet kapod:
- Ellenőrizd, hogy helyesen adtad-e meg az API kulcsot
- Ellenőrizd az internetkapcsolatot
- Ellenőrizd, hogy az API kulcs érvényes-e

### LangGraph problémák

Ha "LangGraph nem elérhető" hibát kapsz:
- Ellenőrizd, hogy a langgraph csomag telepítve van-e: `pip install langgraph`
- Ellenőrizd, hogy a minimális futtatókörnyezeted Python 3.9 vagy újabb verzió

### Általános problémák

- **Importálási hibák**: Győződj meg róla, hogy a fájlok a megfelelő helyeken vannak, és a projekt gyökérkönyvtárából indítod a szkripteket
- **Naplófájlok ellenőrzése**: A `logs/minimal_system.log` fájl tartalmazza a részletes hibaüzeneteket
- **Függőségek újratelepítése**: Probléma esetén próbáld meg újratelepíteni a függőségeket: `pip install -r requirements_minimal.txt --force-reinstall`

## Komponensek fokozatos hozzáadása

A minimális rendszer sikeres elindítása után fokozatosan adhatók hozzá további komponensek:

1. **További AI modellek**: A `simple_ai.py` fájl kiegészítése más modellekkel
2. **Webes interfész**: Egyszerű webes API hozzáadása
3. **Bővített hibakezelés**: A hibadiagnosztika fejlesztése
4. **Memóriarendszer**: Kontextus és előzmények tárolása
5. **Pluginrendszer**: Új képességek hozzáadása pluginek formájában

## További lépések

A minimális rendszer elindítása után a következő lépések ajánlottak:

1. **Parancsok tesztelése**: Próbálj ki egyszerű parancsokat a teljes minimális rendszerben
2. **Konfiguráció testreszabása**: A `config/minimal_config.yaml` fájl módosítása
3. **API integráció**: További API-k integrálása
4. **Naplók elemzése**: A teljesítmény és hibák figyelése a naplófájlokban
