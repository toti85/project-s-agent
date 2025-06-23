"""
Test Config for Project-S
------------------------
Ez a modul a tesztelési konfiguráció beállításait tartalmazza
"""
import os
import sys
import logging
from pathlib import Path
import pytest
import asyncio

# Alap könyvtárak beállítása
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Tesztelési könyvtárak
TEST_DATA_DIR = os.path.join(PROJECT_ROOT, "tests", "test_data")
TEST_CONFIG_DIR = os.path.join(PROJECT_ROOT, "tests", "test_config")
TEST_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "test_output")

# Győződjünk meg arról, hogy a tesztkönyvtárak léteznek
for dir_path in [TEST_DATA_DIR, TEST_CONFIG_DIR, TEST_OUTPUT_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Teszt konfiguráció - minden unit tesztben importálható
TEST_CONFIG = {
    # Integráció tesztelés beállításai
    "mock_llm_response": True,
    "use_lightweight_models": True,
    "skip_web_requests": True,
    
    # Teljesítmény tesztelés beállításai
    "performance_test_iterations": 5,
    "performance_test_load": 10,
    
    # Rendszerszintű műveletek teszt beállításai
    "allowed_test_paths": [TEST_DATA_DIR, TEST_CONFIG_DIR, TEST_OUTPUT_DIR],
    "test_process_timeout": 5,  # másodpercek
    
    # LangGraph teszt beállításai
    "langraph_debug_mode": True,
    "mock_tool_responses": True
}

# Logolás beállítása a tesztekhez
def setup_test_logging():
    """Beállítja a logging konfigurációt a tesztekhez"""
    log_dir = os.path.join(PROJECT_ROOT, "logs", "tests")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "test_run.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("project_s_tests")

# Test fixture létrehozása az aszinkron teszteléshez
@pytest.fixture
def event_loop():
    """Pytest fixture az asyncio event loop számára"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
    
# Teszt logger létrehozása
test_logger = setup_test_logging()

# Alap mock adatok
DEFAULT_MOCK_LLM_RESPONSE = {
    "content": "Ez egy teszt válasz a mock LLM-től.",
    "model": "test-model",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}

# Mock fájlok és konfigok létrehozása a tesztekhez
def create_test_files():
    """Létrehozza a teszt adatfájlokat, ha még nem léteznek"""
    # Teszt konfigurációs fájl
    test_config_path = os.path.join(TEST_CONFIG_DIR, "test_config.json")
    if not os.path.exists(test_config_path):
        import json
        with open(test_config_path, "w") as f:
            json.dump({
                "test_setting": "test_value",
                "nested": {
                    "setting1": 1,
                    "setting2": "two"
                },
                "list_setting": [1, 2, 3]
            }, f, indent=2)
              # Test text file
    test_text_path = os.path.join(TEST_DATA_DIR, "test_file.txt")
    if not os.path.exists(test_text_path):
        with open(test_text_path, "w", encoding="utf-8") as f:
            f.write("This is a test file.\nSecond line.\nThird line.")
    
    return {
        "config_path": test_config_path,
        "text_path": test_text_path
    }

# Teszt futtatás előtt inicializálás
create_test_files()
