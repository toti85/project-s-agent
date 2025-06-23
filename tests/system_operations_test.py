"""
System Operations Tests for Project-S
-----------------------------------
Ez a modul teszteli a rendszerszintű műveletek funkcionalitását
"""
import os
import sys
import pytest
import asyncio
import json
import yaml
import logging
import tempfile
import platform
from pathlib import Path

from integrations.system_operations import is_path_allowed, is_command_allowed
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from integrations.system_operations_manager import system_operations_manager

# Logging beállítása
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Teszteléshez használt könyvtár
TEST_DIR = tempfile.mkdtemp(prefix="system_ops_test_")


@pytest.fixture(scope="module")
def test_config_file():
    """Ideiglenes konfigurációs fájl a tesztekhez"""
    config_path = os.path.join(TEST_DIR, "test_config.json")
    test_config = {
        "app": {
            "name": "ProjectSTest",
            "version": "1.0.0"
        },
        "settings": {
            "theme": "dark",
            "language": "hu",
            "debug": True
        },
        "paths": {
            "data": "./data",
            "logs": "./logs"
        }
    }
    
    with open(config_path, "w") as f:
        json.dump(test_config, f, indent=2)
    
    yield config_path
    
    # Cleanup
    try:
        os.remove(config_path)
    except:
        pass


@pytest.fixture(scope="module")
def test_text_file():
    """Ideiglenes szövegfájl a tesztekhez"""
    file_path = os.path.join(TEST_DIR, "test_file.txt")
    
    with open(file_path, "w") as f:
        f.write("Ez egy teszt fájl.\nMásodik sor.\nHarmadik sor.")
    
    yield file_path
    
    # Cleanup
    try:
        os.remove(file_path)
    except:
        pass


def test_security_checks():
    """Biztonsági ellenőrzések tesztelése"""
    # Útvonal ellenőrzések
    assert is_path_allowed(TEST_DIR) == True
    assert is_path_allowed(os.path.join(TEST_DIR, "test.txt")) == True
    
    # Rendszermappák tiltása
    if platform.system() == "Windows":
        assert is_path_allowed(r"C:\Windows\System32") == False
    else:
        assert is_path_allowed("/etc/passwd") == False
        
    # Parancs ellenőrzések
    assert is_command_allowed(["echo", "hello"]) == True
    assert is_command_allowed(["ls", "-la"]) == True
    assert is_command_allowed(["rm", "-rf", "/"]) == False
    assert is_command_allowed(["format", "C:"]) == False


@pytest.mark.asyncio
async def test_file_operations(test_text_file):
    """Fájlrendszer műveletek tesztelése"""
    # Fájl olvasása
    read_result = await file_system_operations.read_file(test_text_file)
    assert read_result["success"] == True
    assert "Ez egy teszt fájl." in read_result["content"]
    assert read_result["metadata"]["path"] == test_text_file
    
    # Könyvtár listázása
    list_result = await file_system_operations.list_directory(TEST_DIR)
    assert list_result["success"] == True
    assert list_result["directory"] == TEST_DIR
    assert any(f["name"] == os.path.basename(test_text_file) for f in list_result["files"])
    
    # Fájl írása
    new_file_path = os.path.join(TEST_DIR, "new_file.txt")
    write_result = await file_system_operations.write_file(new_file_path, "Új fájl tartalma")
    assert write_result["success"] == True
    
    # Ellenőrzés, hogy létezik-e az új fájl
    exists_result = await file_system_operations.file_exists(new_file_path)
    assert exists_result["success"] == True
    assert exists_result["exists"] == True
    assert exists_result["is_file"] == True


@pytest.mark.asyncio
async def test_process_operations():
    """Folyamatkezelési műveletek tesztelése"""
    # Egyszerű parancs végrehajtása
    if platform.system() == "Windows":
        cmd = "echo Hello Project-S"
    else:
        cmd = ["echo", "Hello Project-S"]
        
    exec_result = await process_operations.execute_process(cmd)
    assert exec_result["success"] == True
    assert "Hello Project-S" in exec_result["stdout"]
    
    # Folyamatok listázása
    list_result = await process_operations.list_processes()
    assert list_result["success"] == True
    assert isinstance(list_result["processes"], list)
    
    # Ellenőrizzük, hogy van-e PID információ
    for proc in list_result["processes"]:
        assert "pid" in proc
        assert "name" in proc


@pytest.mark.asyncio
async def test_config_operations(test_config_file):
    """Konfigurációkezelési műveletek tesztelése"""
    # Konfiguráció betöltése
    load_result = await config_operations.load_config(test_config_file)
    assert load_result["success"] == True
    assert "app" in load_result["config"]
    assert load_result["config"]["app"]["name"] == "ProjectSTest"
    
    # Konfiguráció frissítése
    updates = {
        "settings": {
            "theme": "light",
            "new_setting": "value"
        }
    }
    update_result = await config_operations.update_config(test_config_file, updates)
    assert update_result["success"] == True
    
    # Ellenőrizzük, hogy a frissítés megtörtént
    load_result_after = await config_operations.load_config(test_config_file, use_cache=False)
    assert load_result_after["config"]["settings"]["theme"] == "light"
    assert load_result_after["config"]["settings"]["new_setting"] == "value"
    assert load_result_after["config"]["settings"]["language"] == "hu"  # Megmaradt az eredeti érték
    
    # Specifikus érték lekérése
    value_result = await config_operations.get_config_value(test_config_file, "settings.theme")
    assert value_result["success"] == True
    assert value_result["value"] == "light"
    
    # Nem létező érték esetén az alapértelmezett
    default_result = await config_operations.get_config_value(test_config_file, "settings.nonexistent", "default")
    assert default_result["success"] == True
    assert default_result["value"] == "default"
    assert default_result["found"] == False


@pytest.mark.asyncio
async def test_system_operations_manager():
    """System Operations Manager tesztelése"""
    # Munkafolyamatok létrehozása
    file_workflow = system_operations_manager.create_file_operations_workflow()
    process_workflow = system_operations_manager.create_process_operations_workflow()
    config_workflow = system_operations_manager.create_config_operations_workflow()
    combined_workflow = system_operations_manager.create_combined_system_workflow()
    error_workflow = system_operations_manager.create_error_handling_workflow()
    
    # Ellenőrizzük, hogy a munkafolyamatok létrejöttek
    assert hasattr(file_workflow, "add_node")
    assert hasattr(process_workflow, "add_node")
    assert hasattr(config_workflow, "add_node")
    assert hasattr(combined_workflow, "add_node")
    assert hasattr(error_workflow, "add_node")
    
    # Tool node-ok lekérdezése
    all_tools = system_operations_manager.get_all_tool_nodes()
    assert len(all_tools) > 0
    assert "read_file" in all_tools
    assert "execute_process" in all_tools
    assert "load_config" in all_tools


@pytest.mark.asyncio
async def test_yaml_config():
    """YAML konfiguráció kezelés tesztelése"""
    # Teszt YAML fájl létrehozása
    yaml_path = os.path.join(TEST_DIR, "test_config.yaml")
    test_yaml = {
        "app": {
            "name": "YamlTest",
            "version": "1.0.0"
        },
        "settings": {
            "theme": "dark",
            "features": ["feature1", "feature2"]
        }
    }
    
    with open(yaml_path, "w") as f:
        yaml.dump(test_yaml, f)
    
    # Konfiguráció betöltése
    load_result = await config_operations.load_config(yaml_path)
    assert load_result["success"] == True
    assert load_result["config"]["app"]["name"] == "YamlTest"
    assert "feature1" in load_result["config"]["settings"]["features"]
    
    # Konfiguráció frissítése
    updates = {
        "settings": {
            "features": ["feature1", "feature2", "feature3"]
        }
    }
    update_result = await config_operations.update_config(yaml_path, updates)
    assert update_result["success"] == True
    
    # Ellenőrizzük a frissítést
    load_after = await config_operations.load_config(yaml_path, use_cache=False)
    assert "feature3" in load_after["config"]["settings"]["features"]


@pytest.mark.asyncio
async def test_complex_file_operations():
    """Komplex fájlrendszer műveletek tesztelése"""
    # Ideiglenes könyvtárstruktúra létrehozása teszteléshez
    test_subdir = os.path.join(TEST_DIR, "subdir")
    os.makedirs(test_subdir, exist_ok=True)
    
    # Fájlok létrehozása
    for i in range(3):
        with open(os.path.join(test_subdir, f"file{i}.txt"), "w") as f:
            f.write(f"File {i} content")
    
    # Rekurzív könyvtárlistázás
    list_result = await file_system_operations.list_directory(TEST_DIR, recursive=True)
    assert list_result["success"] == True
    
    # Ellenőrizzük, hogy megtaláljuk a rekurzívan listázott fájlokat
    subdir_files = [f for f in list_result["files"] if "subdir" in f["path"]]
    assert len(subdir_files) >= 3
    
    # Ellenőrizzük, hogy a könyvtár is benne van a listában
    assert any(d["name"] == "subdir" for d in list_result["directories"])


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    """Teszt után takarítás"""
    yield
    # Teszt könyvtár törlése
    try:
        import shutil
        shutil.rmtree(TEST_DIR)
    except:
        pass


if __name__ == "__main__":
    # Kézi futtatás esetén
    logging.basicConfig(level=logging.INFO)
    
    # Létrehozzuk a tesztkönyvtárat
    os.makedirs(TEST_DIR, exist_ok=True)
    
    # Config fájl a tesztekhez
    config_path = os.path.join(TEST_DIR, "test_config.json")
    with open(config_path, "w") as f:
        json.dump({"test": "data"}, f)
    
    # Teszteset futtatása
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_file_operations(os.path.join(TEST_DIR, "test_config.json")))
    loop.run_until_complete(test_config_operations(config_path))
