"""
Mock Objects for Testing Project-S Components
------------------------------------------
Ez a modul mockokat biztosít a Project-S komponensek teszteléséhez
"""
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
from unittest.mock import AsyncMock, MagicMock, patch
import random
import time

# Mockolt válasz tartalmak különböző forgatókönyvekhez
MOCK_RESPONSE_TEMPLATES = {
    # Elemzési válaszok
    "analyze": {
        "technology": """
        A(z) {technology} elemzése:
        
        Előnyök:
        - Skálázható és rugalmas architektúra
        - Hatékony erőforrás-kezelés
        - Széles körű közösségi támogatás
        
        Hátrányok:
        - Magas kezdeti komplexitás
        - Meredek tanulási görbe
        - Üzemeltetési költségek
        
        Használati esetek:
        - Skálázható webalkalmazások
        - Mikroszolgáltatás architektúrák
        - Felhőalapú rendszerek
        """,
        "code": """
        A kód elemzése:
        
        Erősségek:
        - Megfelelő struktúra és szervezés
        - Jól dokumentált funkciók
        - Hatékony hibakezelés
        
        Gyengeségek:
        - Néhány redundáns kódrészlet
        - Hiányzó tesztek kritikus funkciókhoz
        - Lehetséges optimalizációs lehetőségek
        
        Javaslatok:
        - Refaktorálás a {pattern} tervezési minta alapján
        - Tesztlefedettség növelése
        - Hiányzó dokumentáció pótlása
        """
    },
    
    # Tervezési válaszok
    "planning": {
        "simple": """
        1. Probléma elemzése és követelmények meghatározása
        2. Rendszerkomponensek tervezése
        3. API-k és adatmodellek definiálása
        4. Implementáció és egységtesztelés
        5. Integrációs tesztek és hibajavítás
        6. Dokumentáció és átadás
        """,
        "complex": """
        1. Projektelőkészítés
           - Követelmények elemzése
           - Erőforrástervezés
           - Ütemezés
           
        2. Architektúra tervezés
           - Komponensek meghatározása
           - Technológiai stack kiválasztása
           - Integrációs pontok definiálása
           
        3. Implementációs fázis
           - Backend fejlesztés
           - Frontend fejlesztés
           - Adatbázis implementáció
           
        4. Tesztelés
           - Egységtesztek
           - Integrációs tesztek
           - Teljesítménytesztek
           
        5. Dokumentáció és átadás
           - Fejlesztői dokumentációk
           - Felhasználói útmutatók
           - Telepítési útmutató
        """
    },
    
    # Kreatív válaszok
    "creative": {
        "story": """
        Az AI asszisztens épp egy újabb kódot generált, amikor észrevette, 
        hogy valami furcsa történik a rendszerben. A fájlok mintha 
        önálló életre keltek volna, és átrendeződtek volna. Ez nem lehetett 
        normális működés eredménye. Talán egy bug? Vagy valami más?
        
        Az asszisztens elkezdett mélyebbre ásni...
        """,
        
        "description": """
        A Project-S egy forradalmi hibrid intelligencia rendszer, amely 
        egyesíti a legmodernebb nyelvi modellek erejét a robusztus 
        rendszerszintű műveletekkel. Képzelje el úgy, mint egy digitális 
        zsenialitás és mérnöki precizitás találkozását, amely révén 
        a számítógép nem csak megérti az Ön szándékát, hanem 
        képes azt hatékonyan és biztonságosan végrehajtani.
        """
    },
    
    # Összefoglaló válaszok
    "summarize": """
    A dokumentum fő pontjai:
    
    1. {point1}
    2. {point2}
    3. {point3}
    
    Legfontosabb megállapítások:
    - {insight1}
    - {insight2}
    
    Következtetések:
    {conclusion}
    """
}


class MockLLMResponse:
    """Mock osztály az LLM válaszainak szimulációjához"""
    def __init__(self, content: str, model: str = "test-model"):
        self.content = content
        self.model = model
        self.usage = {
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(100, 500),
            "total_tokens": None  # Ezt a __post_init__ számolja ki
        }
        self.usage["total_tokens"] = self.usage["prompt_tokens"] + self.usage["completion_tokens"]
        self.finish_reason = "stop"
        
    def __str__(self):
        return self.content
        
    def model_dump(self) -> Dict[str, Any]:
        """Az LLM válasz adatainak szótárként való visszaadása"""
        return {
            "content": self.content,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason
        }


class MockLLMClient:
    """Mock osztály az LLM kliens szimulációjához"""
    def __init__(self, model_name: str = "test-model"):
        self.model_name = model_name
        self.response_delay = 0.2  # Másodpercek
        self.failure_rate = 0.05  # 5% esély a hibára
        self.call_count = 0
        
    async def generate(self, prompt: str, **kwargs) -> str:
        """Szöveges válasz generálása egy promptra"""
        self.call_count += 1
        
        # Késleltetés szimulációja a valószerűség érdekében
        await asyncio.sleep(self.response_delay)
        
        # Random hiba szimulálása
        if random.random() < self.failure_rate:
            raise Exception("Szimulált LLM API hiba")
        
        # Válasz generálása a prompt alapján
        response = self._generate_response(prompt)
        return response
        
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> MockLLMResponse:
        """Chat válasz generálása üzenetekre"""
        self.call_count += 1
        
        # Késleltetés szimulációja
        await asyncio.sleep(self.response_delay)
        
        # Random hiba szimulálása
        if random.random() < self.failure_rate:
            raise Exception("Szimulált LLM API hiba")
        
        # Az utolsó üzenet kinyerése a prompthoz
        last_message = messages[-1] if messages else {"content": ""}
        prompt = last_message.get("content", "")
        
        # Válasz generálása
        response_text = self._generate_response(prompt)
        return MockLLMResponse(content=response_text, model=self.model_name)
    
    def _generate_response(self, prompt: str) -> str:
        """Válasz generálása a prompt alapján"""
        prompt_lower = prompt.lower()
        
        # Elemzési promptokra
        if "elemezd" in prompt_lower or "analiz" in prompt_lower:
            if "technológia" in prompt_lower or "technology" in prompt_lower:
                # Kinyerjük a technológia nevét, vagy alapértelmezettet használunk
                tech_words = ["kubernetes", "docker", "blockchain", "ai", "machine learning"]
                technology = next((word for word in tech_words if word in prompt_lower), "technológia")
                return MOCK_RESPONSE_TEMPLATES["analyze"]["technology"].format(technology=technology)
            else:
                patterns = ["MVC", "Singleton", "Factory", "Observer"]
                return MOCK_RESPONSE_TEMPLATES["analyze"]["code"].format(pattern=random.choice(patterns))
                
        # Tervezési promptokra
        elif "terv" in prompt_lower or "plan" in prompt_lower:
            if len(prompt) > 200:  # Komplex prompt
                return MOCK_RESPONSE_TEMPLATES["planning"]["complex"]
            else:
                return MOCK_RESPONSE_TEMPLATES["planning"]["simple"]
                
        # Kreatív promptokra
        elif "kreatív" in prompt_lower or "creative" in prompt_lower or "story" in prompt_lower:
            if "történet" in prompt_lower or "story" in prompt_lower:
                return MOCK_RESPONSE_TEMPLATES["creative"]["story"]
            else:
                return MOCK_RESPONSE_TEMPLATES["creative"]["description"]
                
        # Összefoglaló promptokra
        elif "összefoglal" in prompt_lower or "summary" in prompt_lower:
            return MOCK_RESPONSE_TEMPLATES["summarize"].format(
                point1="Első fontos pont a dokumentumból",
                point2="Második kulcsinformáció",
                point3="Harmadik lényeges elem",
                insight1="Kritikus megállapítás a témáról",
                insight2="További fontos következtetés",
                conclusion="A dokumentum alapján megállapítható, hogy ez egy tesztelési példa."
            )
            
        # Alapértelmezett válasz
        else:
            return "Ez egy általános válasz a mock LLM modelltől. A prompt nem tartalmazott specifikus kulcsszavakat."


class MockWebAccess:
    """Mock osztály a webes hozzáférések szimulációjához"""
    def __init__(self):
        self.call_count = 0
        self.search_delay = 0.3  # Másodpercek
        self.failure_rate = 0.1  # 10% esély a hibára
        
        # Mock adatok különböző keresési kulcsszavakhoz
        self.mock_data = {
            "default": [
                {"title": "Általános Találat 1", "link": "https://example.com/1", "snippet": "Ez egy általános találati szöveg."},
                {"title": "Általános Találat 2", "link": "https://example.com/2", "snippet": "További találati információk itt."}
            ],
            "kubernetes": [
                {"title": "Kubernetes - Official Documentation", "link": "https://kubernetes.io/docs/", 
                 "snippet": "Kubernetes is an open-source container orchestration system for automating software deployment, scaling, and management."},
                {"title": "Getting Started with Kubernetes", "link": "https://kubernetes.io/docs/setup/", 
                 "snippet": "Kubernetes clusters can be deployed on either physical or virtual machines."}
            ],
            "python": [
                {"title": "Python.org", "link": "https://www.python.org/", 
                 "snippet": "Python is a programming language that lets you work quickly and integrate systems more effectively."},
                {"title": "Python Tutorial - W3Schools", "link": "https://www.w3schools.com/python/", 
                 "snippet": "Python is a popular programming language. Python can be used on a server to create web applications."}
            ]
        }
        
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Webes keresés szimulálása"""
        self.call_count += 1
        
        # Késleltetés szimulációja
        await asyncio.sleep(self.search_delay)
        
        # Random hiba szimulálása
        if random.random() < self.failure_rate:
            raise Exception("Szimulált webes keresési hiba")
        
        # Kulcsszavak keresése a lekérdezésben
        query_lower = query.lower()
        result_key = "default"
        
        for key in self.mock_data.keys():
            if key in query_lower:
                result_key = key
                break
                
        # Találatok visszaadása
        results = self.mock_data.get(result_key, self.mock_data["default"])
        return results[:max_results]
        
    async def fetch_content(self, url: str) -> str:
        """Weboldal tartalom lekérésének szimulálása"""
        self.call_count += 1
        
        # Késleltetés szimulációja
        await asyncio.sleep(self.search_delay * 1.5)  # Hosszabb, mint a keresés
        
        # Random hiba szimulálása
        if random.random() < self.failure_rate:
            raise Exception("Szimulált tartalom lekérési hiba")
        
        # Tartalom generálása az URL alapján
        if "kubernetes" in url.lower():
            return """
            <h1>Kubernetes Documentation</h1>
            <p>Kubernetes is an open-source container orchestration system for automating software deployment, scaling, and management.</p>
            <h2>Features</h2>
            <ul>
                <li>Automated rollouts and rollbacks</li>
                <li>Service discovery and load balancing</li>
                <li>Storage orchestration</li>
                <li>Self-healing</li>
            </ul>
            """
        elif "python" in url.lower():
            return """
            <h1>Python Programming Language</h1>
            <p>Python is an interpreted, high-level, general-purpose programming language.</p>
            <h2>Key Features</h2>
            <ul>
                <li>Simple, easy to learn syntax</li>
                <li>Interpreted language</li>
                <li>Cross-platform</li>
                <li>Extensive standard library</li>
            </ul>
            """
        else:
            return f"""
            <h1>Example Content for {url}</h1>
            <p>This is mock content for testing purposes.</p>
            <p>The requested URL was: {url}</p>
            <p>Generated at: {time.time()}</p>
            """


class MockFileSystem:
    """Mock osztály a fájlrendszer műveletek szimulációjához"""
    def __init__(self):
        self.files = {}  # Virtuális fájlrendszer
        self.call_count = 0
        
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Fájl olvasás szimulálása"""
        self.call_count += 1
        
        # Normalizáljuk az útvonalat
        file_path = os.path.normpath(file_path)
        
        # Ellenőrizzük, hogy létezik-e a fájl
        if file_path not in self.files:
            return {
                "success": False,
                "error": f"A fájl nem létezik: {file_path}"
            }
            
        # Visszaadjuk a fájl tartalmát
        return {
            "success": True,
            "content": self.files[file_path]["content"],
            "metadata": {
                "path": file_path,
                "encoding": encoding,
                "size": len(self.files[file_path]["content"]),
                "modified": self.files[file_path]["modified"]
            }
        }
        
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8", 
                       create_backup: bool = False) -> Dict[str, Any]:
        """Fájl írás szimulálása"""
        self.call_count += 1
        
        # Normalizáljuk az útvonalat
        file_path = os.path.normpath(file_path)
        
        # Ha a fájl már létezik és backup-ot kell készíteni
        if file_path in self.files and create_backup:
            backup_path = f"{file_path}.bak"
            self.files[backup_path] = self.files[file_path].copy()
            
        # Fájl írása
        self.files[file_path] = {
            "content": content,
            "modified": time.time(),
            "encoding": encoding
        }
        
        return {
            "success": True,
            "path": file_path
        }
        
    async def list_directory(self, directory_path: str, recursive: bool = False) -> Dict[str, Any]:
        """Könyvtár listázás szimulálása"""
        self.call_count += 1
        
        # Normalizáljuk az útvonalat
        directory_path = os.path.normpath(directory_path)
        
        # Készítünk egy listát a könyvtárban található fájlokról
        items = []
        for path in self.files.keys():
            # Ellenőrizzük, hogy a fájl a megadott könyvtárban van-e
            if path.startswith(directory_path):
                # Ha nem rekurzív, csak a közvetlen fájlokat adjuk hozzá
                if not recursive and os.path.dirname(path) != directory_path:
                    continue
                    
                items.append({
                    "name": os.path.basename(path),
                    "path": path,
                    "is_file": True,
                    "size": len(self.files[path]["content"]),
                    "modified": self.files[path]["modified"]
                })
                
        return {
            "success": True,
            "directory": directory_path,
            "items": items
        }
    
    def setup_test_files(self) -> None:
        """Teszt fájlok létrehozása a virtuális fájlrendszerben"""
        self.files = {
            # Konfiguráció
            "/test/config/test_config.json": {
                "content": json.dumps({
                    "name": "test_config",
                    "version": "1.0",
                    "settings": {
                        "test_mode": True,
                        "log_level": "DEBUG"
                    }
                }, indent=2),
                "modified": time.time(),
                "encoding": "utf-8"
            },
            
            # Teszt fájlok
            "/test/data/test_file.txt": {
                "content": "Ez egy egyszerű teszt szövegfájl.\nTöbb sorral.",
                "modified": time.time(),
                "encoding": "utf-8"
            },
            
            "/test/data/sample.json": {
                "content": json.dumps({
                    "name": "sample",
                    "items": [1, 2, 3],
                    "active": True
                }, indent=2),
                "modified": time.time(),
                "encoding": "utf-8"
            }
        }


class MockProcessOperations:
    """Mock osztály a folyamatkezelési műveletek szimulációjához"""
    def __init__(self):
        self.processes = {}  # Virtuális folyamatok
        self.next_pid = 1000
        self.call_count = 0
        
    async def execute_process(self, command: Union[str, List[str]], timeout: int = 30, 
                            capture_output: bool = True, **kwargs) -> Dict[str, Any]:
        """Folyamat végrehajtás szimulálása"""
        self.call_count += 1
        
        # Parancs stringgé alakítása
        if isinstance(command, list):
            cmd_str = " ".join(command)
        else:
            cmd_str = command
            
        # Folyamat azonosító generálása
        pid = self.next_pid
        self.next_pid += 1
        
        # A parancs alapján válasz generálása
        output = self._generate_command_output(cmd_str)
        
        # Folyamat adatok tárolása
        self.processes[pid] = {
            "pid": pid,
            "command": cmd_str,
            "start_time": time.time(),
            "status": "terminated",
            "output": output,
            "exit_code": 0,
            "execution_time": random.uniform(0.05, 0.2)
        }
        
        return {
            "success": True,
            "pid": pid,
            "output": output if capture_output else "",
            "exit_code": 0,
            "execution_time": self.processes[pid]["execution_time"]
        }
        
    async def list_processes(self, filter_name: Optional[str] = None) -> Dict[str, Any]:
        """Folyamatok listázásának szimulálása"""
        self.call_count += 1
        
        processes = list(self.processes.values())
        
        # Szűrés, ha van megadva
        if filter_name:
            processes = [p for p in processes if filter_name.lower() in p["command"].lower()]
            
        return {
            "success": True,
            "processes": processes
        }
        
    async def get_process_info(self, process_id: Optional[str] = None, 
                             pid: Optional[int] = None) -> Dict[str, Any]:
        """Folyamat információ lekérésének szimulálása"""
        self.call_count += 1
        
        # Azonosító konvertálása
        if process_id and isinstance(process_id, str) and process_id.isdigit():
            pid = int(process_id)
            
        # Folyamat keresése
        if pid in self.processes:
            return {
                "success": True,
                "process": self.processes[pid]
            }
        else:
            return {
                "success": False,
                "error": f"A folyamat nem található: {pid}"
            }
            
    def _generate_command_output(self, command: str) -> str:
        """Parancs kimenet generálása a parancs alapján"""
        cmd_lower = command.lower()
        
        if "echo" in cmd_lower:
            # Az echo parancs kimenetét visszaadjuk
            parts = command.split("echo", 1)
            if len(parts) > 1:
                return parts[1].strip().strip('"').strip("'")
                
        elif "dir" in cmd_lower or "ls" in cmd_lower:
            # Könyvtár listázás szimulálása
            return "file1.txt\nfile2.json\nsubdir/"
            
        elif "python" in cmd_lower:
            # Python parancs szimulálása
            if "--version" in cmd_lower:
                return "Python 3.9.5"
            else:
                return "Python script executed successfully."
                
        else:
            # Általános válasz
            return f"Command executed: {command}\nExit code: 0"


def setup_mock_environment():
    """
    Az összes mock objektum beállítása a tesztelési környezethez.
    Ezt a függvényt lehet meghívni a tesztek elején.
    """
    mock_web = MockWebAccess()
    mock_llm = MockLLMClient()
    mock_fs = MockFileSystem()
    mock_proc = MockProcessOperations()
    
    # Teszt fájlok létrehozása
    mock_fs.setup_test_files()
    
    # Patchelés a mock objektumokkal
    patches = [
        patch("core.web_access.search", side_effect=mock_web.search),
        patch("core.web_access.fetch_content", side_effect=mock_web.fetch_content),
        patch("core.model_selector.get_model_by_task", return_value=mock_llm),
        patch("integrations.file_system_operations.file_system_operations.read_file", 
               side_effect=mock_fs.read_file),
        patch("integrations.file_system_operations.file_system_operations.write_file", 
               side_effect=mock_fs.write_file),
        patch("integrations.file_system_operations.file_system_operations.list_directory", 
               side_effect=mock_fs.list_directory),
        patch("integrations.process_operations.process_operations.execute_process", 
               side_effect=mock_proc.execute_process),
        patch("integrations.process_operations.process_operations.list_processes", 
               side_effect=mock_proc.list_processes),
        patch("integrations.process_operations.process_operations.get_process_info", 
               side_effect=mock_proc.get_process_info),
    ]
    
    return patches, {
        "web": mock_web,
        "llm": mock_llm,
        "filesystem": mock_fs,
        "process": mock_proc
    }


# Példa használat:
"""
# Teszt függvényben
async def test_something():
    # Mock környezet beállítása
    patches, mocks = setup_mock_environment()
    
    # Patchek elindítása
    for p in patches:
        p.start()
        
    try:
        # Itt futnak a tesztek a mock környezetben
        result = await some_function_that_uses_dependencies()
        assert result == expected_result
        
        # Ellenőrizhetjük a mock objektumok használatát
        assert mocks["web"].call_count > 0
        assert mocks["llm"].call_count > 0
        
    finally:
        # Patchek leállítása
        for p in patches:
            p.stop()
"""

if __name__ == "__main__":
    # Példa a mock objektumok használatára
    async def example():
        mock_llm = MockLLMClient()
        response = await mock_llm.generate("Elemezd a Kubernetes technológiát.")
        print(f"LLM válasz: {response}")
        
        mock_web = MockWebAccess()
        results = await mock_web.search("kubernetes tutorial")
        print(f"Web keresés eredményei: {results}")
        
    asyncio.run(example())
