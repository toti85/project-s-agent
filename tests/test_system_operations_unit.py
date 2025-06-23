"""
Unit Test for System Operations
-----------------------------
Ez a modul a rendszerszintű műveletek komponenseit teszteli
"""
import os
import sys
import pytest
import asyncio
import json
import tempfile
from pathlib import Path

# Teszt konfiguráció importálása
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR

# Rendszerműveletek importálása
from integrations.system_operations import is_path_allowed, is_command_allowed
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from integrations.system_operations_manager import system_operations_manager


class TestSystemOperationsSecurity:
    """Biztonsági ellenőrzések tesztelése"""
    
    def test_path_validation(self):
        """Útvonal ellenőrzés tesztelése"""
        # Pozitív tesztek
        assert is_path_allowed(TEST_DATA_DIR) == True
        assert is_path_allowed(os.path.join(TEST_DATA_DIR, "test.txt")) == True
        
        # Negatív tesztek - rendszerkönyvtárak
        if os.name == "nt":  # Windows
            assert is_path_allowed(r"C:\Windows\System32") == False
        else:  # Linux/Mac
            assert is_path_allowed("/etc/passwd") == False
            
    def test_command_validation(self):
        """Parancs ellenőrzés tesztelése"""
        # Pozitív tesztek
        assert is_command_allowed(["echo", "hello"]) == True
        assert is_command_allowed("python --version") == True
        
        # Negatív tesztek
        assert is_command_allowed(["rm", "-rf", "/"]) == False
        assert is_command_allowed("sudo reboot") == False


@pytest.mark.asyncio
class TestFileSystemOperations:
    """Fájlrendszer műveletek tesztelése"""
    
    async def test_read_file(self):
        """Fájlolvasási műveletek tesztelése"""        # Create test file
        test_file = os.path.join(TEST_DATA_DIR, "read_test.txt")
        test_content = "This is test content.\nSecond line."
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
            
        # Fájl olvasás tesztelése
        result = await file_system_operations.read_file(test_file)
        
        # Ellenőrzés
        assert result["success"] == True
        assert result["content"] == test_content
        assert "metadata" in result
        assert result["metadata"]["path"] == test_file
        
    async def test_write_file(self):
        """Fájl írási műveletek tesztelése"""        # Test file path
        test_file = os.path.join(TEST_OUTPUT_DIR, "write_test.txt")
        test_content = "This is a write test.\nThird line."
        
        # Fájl írás tesztelése
        result = await file_system_operations.write_file(
            file_path=test_file,
            content=test_content,
            create_backup=True
        )
        
        # Ellenőrzés
        assert result["success"] == True
        assert os.path.exists(test_file)
        
        # Tartalmat is ellenőrizzük
        with open(test_file, "r") as f:
            read_content = f.read()
            
        assert read_content == test_content
        
    async def test_list_directory(self):
        """Könyvtárlistázás tesztelése"""
        # Teszt könyvtár létrehozása struktúrával
        test_dir = os.path.join(TEST_OUTPUT_DIR, "list_test")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            
        # Néhány fájl létrehozása
        for i in range(3):            with open(os.path.join(test_dir, f"file_{i}.txt"), "w", encoding="utf-8") as f:
                f.write(f"Test file {i}")
                
        # Alkönyvtár létrehozása
        sub_dir = os.path.join(test_dir, "subdir")
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
              with open(os.path.join(sub_dir, "subfile.txt"), "w", encoding="utf-8") as f:
            f.write("Subdirectory file")
            
        # Könyvtár listázás tesztelése
        result = await file_system_operations.list_directory(
            directory_path=test_dir,
            recursive=True
        )
        
        # Ellenőrzés
        assert result["success"] == True
        assert "items" in result
        assert len(result["items"]) >= 4  # 3 fájl + 1 könyvtár
        
        # Rekurzív listázás ellenőrzése
        has_subdir_file = False
        for item in result["items"]:
            if item["name"].endswith("subfile.txt"):
                has_subdir_file = True
                break
                
        assert has_subdir_file == True


@pytest.mark.asyncio
class TestProcessOperations:
    """Folyamat műveletek tesztelése"""
    
    async def test_execute_process(self):
        """Folyamat végrehajtás tesztelése"""
        # Egyszerű echo parancs tesztelése
        if os.name == "nt":  # Windows
            command = ["cmd", "/c", "echo", "hello"]
        else:  # Linux/Mac
            command = ["echo", "hello"]
            
        result = await process_operations.execute_process(
            command=command,
            timeout=TEST_CONFIG["test_process_timeout"]
        )
        
        # Ellenőrzés
        assert result["success"] == True
        assert "output" in result
        assert "hello" in result["output"].lower()
        assert "execution_time" in result
        
    async def test_process_monitoring(self):
        """Folyamat monitorozás tesztelése"""
        # Folyamat lista lekérése
        result = await process_operations.list_processes()
        
        # Ellenőrzés
        assert result["success"] == True
        assert "processes" in result
        assert isinstance(result["processes"], list)
        assert len(result["processes"]) > 0
        
        # Ellenőrizzük, hogy legalább egy folyamat adatai helyesen vannak-e
        first_process = result["processes"][0]
        assert "pid" in first_process
        assert "name" in first_process
        assert "status" in first_process


@pytest.mark.asyncio
class TestConfigOperations:
    """Konfiguráció kezelés tesztelése"""
    
    async def test_load_config(self):
        """Konfiguráció betöltés tesztelése"""
        # Teszt konfig fájl létrehozása
        test_config_file = os.path.join(TEST_DATA_DIR, "test_config.json")
        test_config = {
            "name": "test_config",
            "version": "1.0",
            "settings": {
                "setting1": True,
                "setting2": 123
            }
        }
        
        with open(test_config_file, "w") as f:
            json.dump(test_config, f, indent=2)
            
        # Konfig betöltés tesztelése
        result = await config_operations.load_config(test_config_file)
        
        # Ellenőrzés
        assert result["success"] == True
        assert "config" in result
        assert result["config"]["name"] == "test_config"
        assert result["config"]["settings"]["setting1"] == True
        assert result["config"]["settings"]["setting2"] == 123
        
    async def test_update_config(self):
        """Konfiguráció frissítés tesztelése"""
        # Teszt konfig fájl létrehozása
        test_config_file = os.path.join(TEST_OUTPUT_DIR, "update_config.json")
        test_config = {
            "name": "original_config",
            "settings": {
                "setting1": False,
                "setting2": 456
            }
        }
        
        with open(test_config_file, "w") as f:
            json.dump(test_config, f, indent=2)
            
        # Konfig frissítés tesztelése
        update_data = {
            "name": "updated_config",
            "settings": {
                "setting1": True
            }
        }
        
        result = await config_operations.update_config(
            config_path=test_config_file,
            update_data=update_data
        )
        
        # Ellenőrzés
        assert result["success"] == True
        
        # Ellenőrizzük, hogy a változtatások mentésre kerültek
        with open(test_config_file, "r") as f:
            updated_config = json.load(f)
            
        assert updated_config["name"] == "updated_config"
        assert updated_config["settings"]["setting1"] == True
        assert updated_config["settings"]["setting2"] == 456  # Nem módosult érték


@pytest.mark.asyncio
class TestSystemOperationsManager:
    """System Operations Manager tesztelése"""
    
    async def test_tools_registration(self):
        """Eszköz regisztráció tesztelése"""
        # Eszközök lekérése
        tools = system_operations_manager.get_all_tool_nodes()
        
        # Ellenőrzés
        assert tools is not None
        assert len(tools) > 0
        
        # Ellenőrizzük a legfontosabb eszközöket
        essential_tools = ["read_file", "write_file", "execute_process", "load_config"]
        for tool in essential_tools:
            assert any(tool in name for name in tools.keys()), f"{tool} nem található a regisztrált eszközök között"
            
    async def test_workflow_creation(self):
        """Munkafolyamat létrehozás tesztelése"""
        # Fájl műveletek munkafolyamat létrehozása
        file_workflow = system_operations_manager.create_file_operations_workflow("test_file_workflow")
        
        # Ellenőrzés
        assert file_workflow is not None
        assert hasattr(file_workflow, "set_entry_point")
        
        # Kombinált munkafolyamat létrehozása
        combined_workflow = system_operations_manager.create_combined_system_workflow("test_combined_workflow")
        
        # Ellenőrzés
        assert combined_workflow is not None
        assert hasattr(combined_workflow, "add_edge")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
