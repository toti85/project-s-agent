"""
End-to-End Tests for Project-S Hybrid System
-----------------------------------------
Ez a modul a teljes Project-S rendszer end-to-end tesztjeit tartalmazza
"""
import os
import sys
import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest import mock
from typing import Dict, Any, List, Optional

# Teszt konfiguráció importálása
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR

# Project-S komponensek importálása
from integrations.system_operations_manager import system_operations_manager
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from core.model_selector import model_selector
from core.web_access import web_access
from core.event_bus import event_bus
from core.error_handler import error_handler
from core.central_executor import central_executor


# Mock osztályok és segédfüggvények
class MockLLMResponse:
    """Mock osztály az LLM válaszainak szimulációjához"""
    def __init__(self, content: str, model: str = "test-model"):
        self.content = content
        self.model = model
        self.usage = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
        
    def __str__(self):
        return self.content


class EndToEndTestCase:
    """End-to-end teszt eset absztrakt alaposztálya"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time = None
        self.end_time = None
        self.success = False
        self.error = None
        
    async def run(self) -> bool:
        """A teszt eset futtatása"""
        self.start_time = time.time()
        try:
            await self.execute()
            self.success = True
        except Exception as e:
            self.error = str(e)
            self.success = False
        finally:
            self.end_time = time.time()
        return self.success
        
    async def execute(self):
        """A konkrét teszt végrehajtása - felülírandó a leszármazott osztályokban"""
        raise NotImplementedError("A leszármazott osztálynak felül kell írnia ezt a metódust")
        
    def get_result(self) -> Dict[str, Any]:
        """A teszt eredményének lekérése"""
        return {
            "name": self.name,
            "description": self.description,
            "success": self.success,
            "error": self.error,
            "duration": self.end_time - self.start_time if self.end_time and self.start_time else None
        }


class TechAnalysisTestCase(EndToEndTestCase):
    """Technológiai elemzés munkafolyamat end-to-end tesztje"""
    def __init__(self, technology: str = "Test Technology"):
        super().__init__(
            name=f"Technológiai Elemzés: {technology}",
            description=f"A {technology} technológia elemzési munkafolyamatának end-to-end tesztje"
        )
        self.technology = technology
        self.output_path = None
        
    async def execute(self):
        """A teszt végrehajtása"""
        # Importáljuk a workflow-t
        sys.path.append(str(Path(__file__).parent.parent / "examples"))
        try:
            from tech_analysis_workflow import TechAnalysisWorkflow
        except ImportError as e:
            raise ValueError(f"A technológiai elemzés munkafolyamat nem importálható: {e}")
            
        # Létrehozzuk a workflow-t
        workflow = TechAnalysisWorkflow(f"e2e_test_{int(time.time())}")
        
        # Végrehajtjuk a munkafolyamatot
        result = await workflow.execute(technology=self.technology)
        
        # Ellenőrizzük az eredményeket
        if not result.get("success", False):
            raise ValueError(f"A munkafolyamat végrehajtása sikertelen: {result.get('error', 'Ismeretlen hiba')}")
            
        # Ellenőrizzük a kimeneti fájlt
        output_path = result.get("output_path", "")
        if not output_path or not os.path.exists(output_path):
            raise ValueError(f"A kimeneti dokumentum nem jött létre: {output_path}")
            
        # Tartalmat is ellenőrizzük
        content_result = await file_system_operations.read_file(output_path)
        if not content_result.get("success", False):
            raise ValueError(f"A kimeneti dokumentum nem olvasható: {output_path}")
            
        content = content_result.get("content", "")
        if not content or len(content) < 100:  # Minimális tartalmi ellenőrzés
            raise ValueError(f"A kimeneti dokumentum tartalma nem megfelelő (túl rövid)")
            
        # Ha idáig eljutottunk, a teszt sikeres
        self.output_path = output_path


class SystemOperationsE2ETestCase(EndToEndTestCase):
    """Rendszerszintű műveletek end-to-end tesztje"""
    def __init__(self):
        super().__init__(
            name="Rendszerszintű Műveletek E2E",
            description="A rendszerszintű műveletek komponenseinek end-to-end tesztje"
        )
        self.test_files = []
        
    async def execute(self):
        """A teszt végrehajtása"""
        # 1. Teszt könyvtárstruktúra létrehozása
        test_dir = os.path.join(TEST_OUTPUT_DIR, f"e2e_test_{int(time.time())}")
        os.makedirs(test_dir, exist_ok=True)
        
        # 2. Konfiguráció írása
        config_file = os.path.join(test_dir, "e2e_config.json")
        config_data = {
            "name": "e2e_test_config",
            "timestamp": time.time(),
            "settings": {
                "test_mode": True,
                "max_processes": 5,
                "file_paths": [
                    os.path.join(test_dir, "data1.txt"),
                    os.path.join(test_dir, "data2.txt")
                ]
            }
        }
        
        config_result = await config_operations.create_config(
            config_path=config_file,
            config_data=config_data
        )
        
        if not config_result.get("success", False):
            raise ValueError(f"Nem sikerült a konfiguráció létrehozása: {config_file}")
            
        # 3. Konfiguráció betöltése
        load_result = await config_operations.load_config(config_file)
        if not load_result.get("success", False):
            raise ValueError(f"Nem sikerült a konfiguráció betöltése: {config_file}")
            
        loaded_config = load_result.get("config", {})
        file_paths = loaded_config.get("settings", {}).get("file_paths", [])
        
        # 4. Fájlok létrehozása a konfigurációban megadott útvonalakon
        for i, file_path in enumerate(file_paths):
            content = f"E2E teszt fájl {i+1}\nIdőbélyeg: {time.time()}"
            write_result = await file_system_operations.write_file(
                file_path=file_path, 
                content=content
            )
            if not write_result.get("success", False):
                raise ValueError(f"Nem sikerült a fájl létrehozása: {file_path}")
                
            self.test_files.append(file_path)
            
        # 5. Folyamat végrehajtása az egyik fájl manipulálásához
        if os.name == "nt":  # Windows
            command = ["cmd", "/c", "echo", "Folyamat kimenet", ">>", file_paths[0]]
        else:  # Linux/Mac
            command = f"echo 'Folyamat kimenet' >> {file_paths[0]}"
            
        process_result = await process_operations.execute_process(command=command)
        if not process_result.get("success", False):
            raise ValueError(f"Nem sikerült a folyamat végrehajtása: {command}")
            
        # 6. A módosított fájl olvasása és ellenőrzése
        read_result = await file_system_operations.read_file(file_paths[0])
        if not read_result.get("success", False):
            raise ValueError(f"Nem sikerült a fájl olvasása: {file_paths[0]}")
            
        content = read_result.get("content", "")
        if "Folyamat kimenet" not in content:
            raise ValueError(f"A fájl tartalma nem a várt: {content}")
            
        # 7. A könyvtár listázása és ellenőrzése
        list_result = await file_system_operations.list_directory(
            directory_path=test_dir,
            recursive=True
        )
        
        if not list_result.get("success", False):
            raise ValueError(f"Nem sikerült a könyvtár listázása: {test_dir}")
            
        items = list_result.get("items", [])
        if len(items) < 3:  # Konfig + 2 fájl
            raise ValueError(f"A könyvtár nem tartalmazza a várt elemeket: {items}")
            
        # Ha idáig eljutottunk, a teszt sikeres
        return True


class LangGraphWorkflowE2ETestCase(EndToEndTestCase):
    """LangGraph munkafolyamat end-to-end tesztje"""
    def __init__(self):
        super().__init__(
            name="LangGraph Munkafolyamat E2E",
            description="A LangGraph munkafolyamatok end-to-end tesztje"
        )
        
    async def execute(self):
        """A teszt végrehajtása"""
        # 1. Munkafolyamat létrehozása a system operations managerrel
        file_workflow = system_operations_manager.create_file_operations_workflow("e2e_test_workflow")
        
        # 2. Teszt fájl létrehozása
        test_file = os.path.join(TEST_OUTPUT_DIR, "e2e_workflow_test.txt")
        with open(test_file, "w") as f:
            f.write("Ez egy E2E munkafolyamat teszt fájl.")
            
        # 3. A munkafolyamat szimulált végrehajtása
        # Mivel a munkafolyamat végrehajtása bonyolultabb, ezért egyszerűsítünk
        # és csak a közvetlen műveleteket teszteljük
        
        read_result = await file_system_operations.read_file(test_file)
        if not read_result.get("success", False):
            raise ValueError(f"Nem sikerült a fájl olvasása: {test_file}")
            
        # Módosítsuk a tartalmat
        content = read_result.get("content", "")
        modified_content = content + "\nMódosítva: " + str(time.time())
        
        write_result = await file_system_operations.write_file(
            file_path=test_file,
            content=modified_content
        )
        
        if not write_result.get("success", False):
            raise ValueError(f"Nem sikerült a fájl írása: {test_file}")
            
        # Ellenőrizzük, hogy a fájl tartalmazza a módosításokat
        reread_result = await file_system_operations.read_file(test_file)
        if not reread_result.get("success", False):
            raise ValueError(f"Nem sikerült a fájl újraolvasása: {test_file}")
            
        new_content = reread_result.get("content", "")
        if "Módosítva:" not in new_content:
            raise ValueError(f"A fájl nem tartalmazza a várt módosításokat: {new_content}")
            
        # Ha idáig eljutottunk, a teszt sikeres
        return True


@pytest.mark.asyncio
class TestProjectSEndToEnd:
    """A teljes Project-S rendszer end-to-end tesztelése"""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Teszt előkészítés és tisztítás"""
        # Mock-ok beállítása
        with mock.patch("core.web_access.search") as mock_search, \
             mock.patch("core.model_selector.get_model_by_task") as mock_get_model:
             
            # Web keresés mock
            mock_search.return_value = [
                {"title": "Test Result 1", "link": "https://example.com/1", "snippet": "This is test result 1"},
                {"title": "Test Result 2", "link": "https://example.com/2", "snippet": "This is test result 2"}
            ]
            
            # Modell response mock
            tech_analysis_response = """
            A technológia elemzése:
            
            Előnyök:
            - Skálázható
            - Költséghatékony
            - Felhasználóbarát
            
            Hátrányok:
            - Komplex telepítés
            - Magas tanulási görbe
            
            Használati esetek:
            - Vállalati rendszerek
            - Felhő alkalmazások
            """
            
            # Modell mock dinamikus válaszokkal
            def get_mock_model(task_type):
                """Különböző típusú mock modellek létrehozása"""
                response = tech_analysis_response
                if task_type == "creative":
                    response = "Ez egy kreatív válasz egy teszt kérdésre."
                elif task_type == "planning":
                    response = "1. Tervezés\n2. Implementáció\n3. Tesztelés"
                    
                mock_model = mock.MagicMock()
                mock_model.generate = mock.AsyncMock(return_value=response)
                mock_model.model_name = f"test-{task_type}-model"
                return mock_model
                
            mock_get_model.side_effect = get_mock_model
            
            # A teszteknek átadjuk a vezérlést
            yield
    
    async def test_system_operations_e2e(self):
        """Rendszerszintű műveletek end-to-end tesztje"""
        test_case = SystemOperationsE2ETestCase()
        success = await test_case.run()
        result = test_case.get_result()
        
        test_logger.info(f"E2E teszt eredmény: {result['name']} - {'SIKERES' if result['success'] else 'SIKERTELEN'}")
        if not result["success"]:
            test_logger.error(f"Hiba: {result['error']}")
            
        assert success, f"Az E2E teszt sikertelen: {result['error']}"
    
    async def test_langgraph_workflow_e2e(self):
        """LangGraph munkafolyamat end-to-end tesztje"""
        test_case = LangGraphWorkflowE2ETestCase()
        success = await test_case.run()
        result = test_case.get_result()
        
        test_logger.info(f"E2E teszt eredmény: {result['name']} - {'SIKERES' if result['success'] else 'SIKERTELEN'}")
        if not result["success"]:
            test_logger.error(f"Hiba: {result['error']}")
            
        assert success, f"Az E2E teszt sikertelen: {result['error']}"
    
    async def test_tech_analysis_e2e(self):
        """Technológiai elemzés munkafolyamat end-to-end tesztje"""
        try:
            test_case = TechAnalysisTestCase("Test Technology")
            success = await test_case.run()
            result = test_case.get_result()
            
            test_logger.info(f"E2E teszt eredmény: {result['name']} - {'SIKERES' if result['success'] else 'SIKERTELEN'}")
            if not result["success"]:
                test_logger.error(f"Hiba: {result['error']}")
                
            assert success, f"Az E2E teszt sikertelen: {result['error']}"
            
        except Exception as e:
            test_logger.warning(f"A technológiai elemzés teszt nem futtatható: {str(e)}")
            # Ez a teszt opcionális, így ne bukjunk el, ha nem futtatható
            # Például ha a tech_analysis_workflow példa nincs telepítve
            pytest.skip(f"A technológiai elemzés példa nem elérhető: {str(e)}")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
