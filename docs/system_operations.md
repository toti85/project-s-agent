# System Operations Components
## Project-S Rendszerszintű Műveletek Dokumentációja

Ez a dokumentáció a Project-S rendszer rendszerszintű műveletek komponenseit írja le, amelyek lehetővé teszik a fájlrendszerrel, folyamatokkal és konfigurációs beállításokkal való interakciót a LangGraph munkafolyamatokban.

## Áttekintés

A rendszerszintű műveletek komponensei LangGraph-kompatibilis eszközöket biztosítanak rendszerszintű feladatok végrehajtásához. Ezek az eszközök biztonságos, hibakezeléssel ellátott interfészt nyújtanak a fájlrendszerhez, folyamatokhoz és konfigurációs beállításokhoz.

## Fő Komponensek

### 1. Fájlrendszerműveletek (file_system_operations.py)

Fájlrendszerrel kapcsolatos műveletek végrehajtása:

- **Fájlok Olvasása**: Biztonságos fájlolvasás méretkorlátozással és hibaellenőrzéssel
- **Fájlok Írása**: Fájlok írása biztonsági ellenőrzésekkel
- **Könyvtárak Listázása**: Könyvtárak tartalmának listázása rekurzív mód támogatással
- **Fájl Ellenőrzés**: Fájlok létezésének és tulajdonságainak ellenőrzése

#### Használati példa:

```python
result = await file_system_operations.read_file("/path/to/file.txt")
if result["success"]:
    content = result["content"]
    size = result["metadata"]["size"]
else:
    error_msg = result["error"]
```

### 2. Folyamatkezelés (process_operations.py)

Folyamatok indításával és kezelésével kapcsolatos műveletek:

- **Folyamat Futtatás**: Parancsok biztonságos végrehajtása időtúllépés kezeléssel
- **Folyamatok Leállítása**: Folyamatok ellenőrzött leállítása
- **Folyamatok Listázása**: Futó folyamatok lekérdezése
- **Folyamat Információk**: Részletes információ egy adott folyamatról

#### Használati példa:

```python
result = await process_operations.execute_process("echo Hello", timeout=10)
if result["success"]:
    output = result["stdout"]
    process_id = result["process_id"]
else:
    error_msg = result["error"]
```

### 3. Konfigurációkezelés (config_operations.py)

Konfigurációs fájlok kezelésére szolgáló műveletek:

- **Konfiguráció Betöltése**: JSON, YAML és egyszerű konfigurációs fájlok beolvasása
- **Konfiguráció Mentése**: Konfigurációs adatok mentése különböző formátumokban
- **Konfiguráció Frissítése**: Meglévő konfigurációs fájlok részleges frissítése
- **Értékek Lekérése**: Specifikus értékek kinyerése a konfigurációból

#### Használati példa:

```python
result = await config_operations.load_config("config/settings.yaml")
if result["success"]:
    config = result["config"]
    theme = config.get("settings", {}).get("theme", "default")
    
    # Konfiguráció frissítése
    await config_operations.update_config("config/settings.yaml", {
        "settings": {"theme": "dark"}
    })
```

### 4. Rendszerszintű Műveletek Menedzser (system_operations_manager.py)

Az összes rendszerszintű műveletet integráló komponens LangGraph munkafolyamatokkal:

- **Munkafolyamatok Létrehozása**: Specializált és kombinált munkafolyamatok létrehozása
- **Eszközök Integrálása**: Az összes eszköz összegyűjtése és integrálása
- **Hibakezelés**: Hibatűrő munkafolyamatok létrehozása
- **Eseménykezelés**: Esemény alapú integráció a Project-S rendszerrel

#### Használati példa:

```python
# Specializált munkafolyamat létrehozása
file_workflow = system_operations_manager.create_file_operations_workflow()

# Kombinált munkafolyamat létrehozása
combined_workflow = system_operations_manager.create_combined_system_workflow()

# Munkafolyamat végrehajtása
result = await system_operations_manager.execute_example_workflow()
```

### 5. Rendszerszintű Műveletek Alapja (system_operations.py)

Közös alapfunkciók és biztonsági mechanizmusok:

- **Biztonsági Ellenőrzések**: Útvonalak és parancsok biztonsági ellenőrzése
- **Típusdefiníciók**: Állapotkezeléshez szükséges típusok
- **Biztonsági Dekorátorok**: Műveletek végrehajtása előtti biztonsági ellenőrzések

## Biztonsági Jellemzők

A rendszerszintű műveletek komponensei számos biztonsági mechanizmust tartalmaznak:

1. **Útvonal Ellenőrzés**: Tiltott mappákhoz és fájlokhoz való hozzáférés megakadályozása
2. **Parancsellenőrzés**: Veszélyes parancsok futtatásának megakadályozása
3. **Méretkorlátozás**: Nagy fájlok olvasásának korlátozása
4. **Hozzáférési Jogosultságok**: Műveletek engedélyezésének/tiltásának kezelése
5. **Eseménynapló**: Minden művelet naplózása és felügyelete

## LangGraph Integráció

A rendszerszintű műveletek komponensei LangGraph munkafolyamatokba integrálhatók:

- **Tool Node-ok**: Minden művelet LangGraph ToolNode-ként is elérhető
- **Munkafolyamatok**: Előre definiált munkafolyamatok különböző feladatokhoz
- **Állapotkezelés**: Rendszerszintű műveletek állapotának követése és kezelése
- **Feltételes Elágazások**: Dinamikus munkafolyamatok hibakezeléssel

## Hibakezelés

A rendszerszintű műveletek komponensei átfogó hibakezelést biztosítanak:

1. **Strukturált Hibajelzés**: Minden művelet szabványos hibaformátumot ad vissza
2. **Retry Mechanizmus**: Hibák esetén automatikus újrapróbálkozás
3. **Események**: Hibákról események kibocsátása a rendszer többi része felé
4. **Naplózás**: Részletes hibanaplózás a hibakereséshez

## Keresztplatform Támogatás

A rendszer különböző operációs rendszereken működik:

- **Windows Kompatibilitás**: Speciális Windows-specifikus út- és parancskezelés
- **Unix/Linux Kompatibilitás**: POSIX-kompatibilis műveletek
- **Platformfüggetlen Absztrakciók**: Az operációs rendszertől függetlenül használható API

## Példák

### Fájlrendszerműveletek Példa

```python
# Könyvtár listázása
list_result = await file_system_operations.list_directory("/path/to/folder", recursive=True)
for file in list_result["files"]:
    print(f"Fájl: {file['name']}, Méret: {file['size']}")

# Fájl olvasása
read_result = await file_system_operations.read_file("/path/to/document.txt")
if read_result["success"]:
    print(f"Tartalom: {read_result['content']}")
```

### Folyamat Végrehajtás Példa

```python
# Parancs végrehajtása
exec_result = await process_operations.execute_process(
    ["python", "-c", "print('Hello from subprocess')"],
    timeout=5
)
if exec_result["success"]:
    print(f"Kimenet: {exec_result['stdout']}")
    print(f"Folyamat azonosító: {exec_result['process_id']}")
    
    # Folyamat információk lekérése
    info = await process_operations.get_process_info(process_id=exec_result["process_id"])
    print(f"Folyamat adatok: {info['process']}")
```

### Konfiguráció Kezelés Példa

```python
# Konfiguráció betöltése
config = await config_operations.load_config("config/app_settings.json")

# Specifikus érték lekérése
theme = await config_operations.get_config_value(
    "config/app_settings.json", 
    "ui.theme",
    default_value="light"
)

# Konfiguráció frissítése
await config_operations.update_config(
    "config/app_settings.json",
    {
        "ui": {
            "theme": "dark",
            "font_size": 14
        }
    }
)
```

### LangGraph Munkafolyamat Példa

```python
# Fájlművelet munkafolyamat létrehozása
file_workflow = system_operations_manager.create_file_operations_workflow()

# Végrehajtási konfiguráció
config = {
    "list_directory": {
        "directory_path": "/path/to/data",
        "recursive": True
    }
}

# Végrehajtás
result = await file_workflow.invoke(config)
```

## Továbbfejlesztési Lehetőségek

1. **Jogosultságkezelés Bővítése**: Részletesebb jogosultságkezelési rendszer
2. **Titkosítási Támogatás**: Fájlok és konfigurációk titkosítása
3. **Távoli Rendszerek**: Távoli rendszerek kezelésének támogatása
4. **Monitoring Bővítése**: Részletesebb folyamat és fájlrendszer monitorozás
5. **Kontextus-függő Műveletek**: Az LLM kontextusára érzékenyebb műveletek
