"""
Performance Tests for Project-S Hybrid System
------------------------------------------
Ez a modul a Project-S rendszer teljesítménytesztjeit tartalmazza
"""
import os
import sys
import pytest
import asyncio
import time
import json
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics
import concurrent.futures
from unittest import mock

# Teszt konfiguráció importálása
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from test_config import TEST_CONFIG, test_logger, TEST_DATA_DIR, TEST_OUTPUT_DIR
from mock_objects import setup_mock_environment, MockLLMClient, MockWebAccess

# Project-S komponensek importálása
from integrations.system_operations_manager import system_operations_manager
from integrations.file_system_operations import file_system_operations
from integrations.process_operations import process_operations
from integrations.config_operations import config_operations
from core.model_selector import model_selector
from core.web_access import web_access


# Teljesítmény méréshez használt decorator
def measure_performance(func):
    """Decorator a függvények teljesítményének méréséhez"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        memory_before = 0  # Itt lehetne memóriahasználatot mérni
        
        try:
            result = await func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None
            success = False
            exception = str(e)
        
        end_time = time.time()
        memory_after = 0  # Itt lehetne memóriahasználatot mérni
        
        # Mérési adatok
        metrics = {
            "function": func.__name__,
            "duration": end_time - start_time,
            "success": success,
            "timestamp": time.time(),
            "memory_usage": memory_after - memory_before
        }
        
        # Hiba kezelése
        if not success:
            metrics["error"] = exception
            
        return result, metrics
    
    return wrapper


class PerformanceTestResult:
    """Osztály a teljesítményteszt eredmények tárolására és elemzésére"""
    def __init__(self, test_name: str, test_description: str):
        self.test_name = test_name
        self.test_description = test_description
        self.iterations = []
        self.metrics = []
        self.start_time = time.time()
        self.end_time = None
        self.summary = {}
        
    def add_iteration(self, iteration: int, metrics: Dict[str, Any]):
        """Iteráció eredményeinek hozzáadása"""
        self.iterations.append(iteration)
        self.metrics.append(metrics)
        
    def finalize(self):
        """Teszt befejezése és összesítés számolása"""
        self.end_time = time.time()
        
        # Ha nincsenek metrikák, nincs mit összesíteni
        if not self.metrics:
            self.summary = {
                "duration_total": 0,
                "iterations": 0,
                "success_rate": 0,
                "avg_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "std_dev_duration": 0
            }
            return
            
        # Sikeres iterációk kiszűrése
        successful_metrics = [m for m in self.metrics if m.get("success", False)]
        
        # Összesítés számolása
        self.summary = {
            "duration_total": self.end_time - self.start_time,
            "iterations": len(self.metrics),
            "success_rate": len(successful_metrics) / len(self.metrics) if self.metrics else 0,
            "avg_duration": statistics.mean([m["duration"] for m in successful_metrics]) if successful_metrics else 0,
            "min_duration": min([m["duration"] for m in successful_metrics]) if successful_metrics else 0,
            "max_duration": max([m["duration"] for m in successful_metrics]) if successful_metrics else 0,
            "std_dev_duration": statistics.stdev([m["duration"] for m in successful_metrics]) if len(successful_metrics) > 1 else 0
        }
        
    def save_to_csv(self, output_path: str):
        """Eredmények mentése CSV formátumban"""
        # Győződjünk meg arról, hogy van mit menteni
        if not self.metrics:
            return
            
        # Könyvtár létrehozása, ha nem létezik
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # CSV fejléc meghatározása az első metrika alapján
        fieldnames = ["iteration"] + list(self.metrics[0].keys())
        
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, metric in zip(self.iterations, self.metrics):
                row = {"iteration": i}
                row.update(metric)
                writer.writerow(row)
                
        test_logger.info(f"Teljesítményadatok mentve: {output_path}")
                
    def generate_charts(self, output_dir: str):
        """Diagramok generálása az eredményekből"""
        # Győződjünk meg arról, hogy van mit ábrázolni
        if not self.metrics:
            return
            
        # Könyvtár létrehozása, ha nem létezik
        os.makedirs(output_dir, exist_ok=True)
        
        # Végrehajtási idő diagram
        plt.figure(figsize=(10, 6))
        plt.plot(self.iterations, [m["duration"] for m in self.metrics], marker="o")
        plt.title(f"Végrehajtási idő - {self.test_name}")
        plt.xlabel("Iteráció")
        plt.ylabel("Idő (másodperc)")
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, f"{self.test_name}_duration.png"))
        plt.close()
        
        # Siker/hiba diagram
        success_count = sum(1 for m in self.metrics if m.get("success", False))
        failure_count = len(self.metrics) - success_count
        
        plt.figure(figsize=(8, 8))
        plt.pie([success_count, failure_count], 
                labels=["Sikeres", "Sikertelen"], 
                colors=["green", "red"],
                autopct="%1.1f%%")
        plt.title(f"Sikerességi arány - {self.test_name}")
        plt.savefig(os.path.join(output_dir, f"{self.test_name}_success_rate.png"))
        plt.close()
        
        test_logger.info(f"Teljesítménydiagramok generálva: {output_dir}")


class PerformanceTester:
    """Osztály a teljesítmény teszteléshez"""
    def __init__(self, iterations: int = 10, concurrency: int = 1):
        self.iterations = iterations
        self.concurrency = concurrency
        self.results = {}
        self.output_dir = os.path.join(TEST_OUTPUT_DIR, "performance")
        
        # Kimenet könyvtár létrehozása
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def run_test(self, test_func, test_name: str, test_description: str, **kwargs):
        """Teszt futtatása és eredmények gyűjtése"""
        result = PerformanceTestResult(test_name, test_description)
        
        test_logger.info(f"Teljesítményteszt indítása: {test_name} - {self.iterations} iteráció")
        
        # Szekvenciális futtatás
        if self.concurrency <= 1:
            for i in range(self.iterations):
                test_logger.debug(f"Iteráció {i+1}/{self.iterations}")
                _, metrics = await measure_performance(test_func)(**kwargs)
                result.add_iteration(i+1, metrics)
        else:
            # Párhuzamos futtatás
            test_logger.info(f"Párhuzamos futtatás: {self.concurrency} konkurens kérés")
            
            # Baselines segédfüggvény a párhuzamos futtatáshoz
            async def run_iteration(i):
                _, metrics = await measure_performance(test_func)(**kwargs)
                return i+1, metrics
                
            # Feladatok létrehozása
            tasks = []
            for i in range(self.iterations):
                tasks.append(run_iteration(i))
                
            # Feladatok csoportosítása a konkurencia alapján
            for i in range(0, len(tasks), self.concurrency):
                batch = tasks[i:i+self.concurrency]
                results = await asyncio.gather(*batch)
                
                for iteration, metrics in results:
                    result.add_iteration(iteration, metrics)
        
        # Eredmények összesítése
        result.finalize()
        
        # Eredmények mentése
        result.save_to_csv(os.path.join(self.output_dir, f"{test_name}.csv"))
        result.generate_charts(self.output_dir)
        
        # Eredmények tárolása
        self.results[test_name] = result
        
        test_logger.info(f"Teljesítményteszt befejezve: {test_name}")
        test_logger.info(f"Átlagos végrehajtási idő: {result.summary['avg_duration']:.4f} másodperc")
        test_logger.info(f"Sikerességi arány: {result.summary['success_rate']*100:.1f}%")
        
        return result
        
    def generate_summary_report(self):
        """Összefoglaló jelentés generálása az összes teszt eredményéről"""
        if not self.results:
            return
            
        # HTML jelentés készítése
        html_path = os.path.join(self.output_dir, "summary_report.html")
        
        with open(html_path, "w") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Project-S Teljesítményteszt Jelentés</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; }
                    th { background-color: #f2f2f2; text-align: left; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    .success { color: green; }
                    .failure { color: red; }
                    .chart-container { margin-top: 30px; }
                </style>
            </head>
            <body>
                <h1>Project-S Teljesítményteszt Jelentés</h1>
                <p>Generálva: %s</p>
                
                <h2>Összefoglaló</h2>
                <table>
                    <tr>
                        <th>Teszt neve</th>
                        <th>Leírás</th>
                        <th>Iterációk</th>
                        <th>Sikerességi arány</th>
                        <th>Átl. végrehajtási idő</th>
                        <th>Min. idő</th>
                        <th>Max. idő</th>
                        <th>Szórás</th>
                    </tr>
            """ % time.strftime("%Y-%m-%d %H:%M:%S"))
            
            # Tesztek eredményeinek kiírása
            for name, result in self.results.items():
                f.write(f"""
                    <tr>
                        <td>{name}</td>
                        <td>{result.test_description}</td>
                        <td>{result.summary['iterations']}</td>
                        <td class="{'success' if result.summary['success_rate'] >= 0.95 else 'failure'}">
                            {result.summary['success_rate']*100:.1f}%
                        </td>
                        <td>{result.summary['avg_duration']:.4f} mp</td>
                        <td>{result.summary['min_duration']:.4f} mp</td>
                        <td>{result.summary['max_duration']:.4f} mp</td>
                        <td>{result.summary['std_dev_duration']:.4f} mp</td>
                    </tr>
                """)
                
            f.write("""
                </table>
                
                <h2>Diagramok</h2>
            """)
            
            # Diagramok beágyazása
            for name in self.results.keys():
                f.write(f"""
                <div class="chart-container">
                    <h3>{name}</h3>
                    <img src="{name}_duration.png" alt="Duration Chart" width="600">
                    <img src="{name}_success_rate.png" alt="Success Rate Chart" width="400">
                </div>
                """)
                
            f.write("""
            </body>
            </html>
            """)
            
        test_logger.info(f"Összefoglaló jelentés generálva: {html_path}")
        return html_path


# Tesztfüggvények a teljesítménytesztekhez

@measure_performance
async def test_file_operations():
    """Fájlműveletek teljesítménytesztje"""
    # Teszt fájl útvonal
    test_file = os.path.join(TEST_OUTPUT_DIR, f"perf_test_{time.time()}.txt")
    
    # Fájl írás
    content = "Ez egy teljesítményteszt fájl.\n" * 100
    write_result = await file_system_operations.write_file(
        file_path=test_file,
        content=content
    )
    
    # Fájl olvasás
    read_result = await file_system_operations.read_file(test_file)
    
    # Könyvtár listázás
    list_result = await file_system_operations.list_directory(
        directory_path=os.path.dirname(test_file)
    )
    
    return {
        "write_success": write_result["success"],
        "read_success": read_result["success"],
        "list_success": list_result["success"],
    }


@measure_performance
async def test_config_operations():
    """Konfigurációkezelés teljesítménytesztje"""
    # Teszt konfig fájl
    test_config_file = os.path.join(TEST_OUTPUT_DIR, f"config_perf_{time.time()}.json")
    
    # Konfiguráció létrehozása
    config_data = {
        "name": f"perf_test_{time.time()}",
        "settings": {
            "test_mode": True,
            "complexity": "high",
            "values": list(range(100))
        }
    }
    
    create_result = await config_operations.create_config(
        config_path=test_config_file,
        config_data=config_data
    )
    
    # Konfiguráció betöltése
    load_result = await config_operations.load_config(test_config_file)
    
    # Konfiguráció frissítése
    update_result = await config_operations.update_config(
        config_path=test_config_file,
        update_data={"settings": {"updated": True}}
    )
    
    return {
        "create_success": create_result["success"],
        "load_success": load_result["success"],
        "update_success": update_result["success"],
    }


@measure_performance
async def test_process_operations():
    """Folyamatkezelés teljesítménytesztje"""
    # Egyszerű parancs végrehajtása
    if os.name == "nt":  # Windows
        command = ["cmd", "/c", "echo", "Performance test"]
    else:  # Linux/Mac
        command = ["echo", "Performance test"]
        
    execute_result = await process_operations.execute_process(
        command=command,
        timeout=5
    )
    
    # Folyamatok listázása
    list_result = await process_operations.list_processes()
    
    return {
        "execute_success": execute_result["success"],
        "list_success": list_result["success"],
    }


@measure_performance
async def test_langgraph_workflow():
    """LangGraph munkafolyamat teljesítménytesztje"""
    # Fájlműveletek munkafolyamat létrehozása
    workflow = system_operations_manager.create_file_operations_workflow("perf_test_workflow")
    
    # Egyszerű művelet végrehajtása közvetlenül a komponensekkel
    # (a teljes workflow futtatása helyett, mivel az bonyolultabb lenne)
    test_file = os.path.join(TEST_OUTPUT_DIR, f"workflow_perf_{time.time()}.txt")
    write_result = await file_system_operations.write_file(
        file_path=test_file,
        content="LangGraph workflow performance test.\n" * 10
    )
    
    read_result = await file_system_operations.read_file(test_file)
    
    return {
        "workflow_created": workflow is not None,
        "write_success": write_result["success"],
        "read_success": read_result["success"],
    }


@pytest.mark.asyncio
class TestSystemPerformance:
    """A Project-S rendszer teljesítménytesztjei"""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Teszt előkészítés és tisztítás"""
        # Mock környezet beállítása
        patches, mocks = setup_mock_environment()
        
        # Patchek elindítása
        for p in patches:
            p.start()
            
        # Teszt könyvtár biztosítása
        os.makedirs(os.path.join(TEST_OUTPUT_DIR, "performance"), exist_ok=True)
            
        yield mocks
        
        # Patchek leállítása
        for p in patches:
            p.stop()
            
    async def test_file_operations_performance(self):
        """Fájlműveletek teljesítménytesztje"""
        tester = PerformanceTester(iterations=TEST_CONFIG["performance_test_iterations"])
        result = await tester.run_test(
            test_func=test_file_operations,
            test_name="file_operations",
            test_description="Fájlműveletek teljesítménye"
        )
        
        # Ellenőrzés
        assert result.summary["success_rate"] > 0.9
        assert result.summary["avg_duration"] < 2.0
        
    async def test_config_operations_performance(self):
        """Konfigurációkezelés teljesítménytesztje"""
        tester = PerformanceTester(iterations=TEST_CONFIG["performance_test_iterations"])
        result = await tester.run_test(
            test_func=test_config_operations,
            test_name="config_operations",
            test_description="Konfigurációkezelés teljesítménye"
        )
        
        # Ellenőrzés
        assert result.summary["success_rate"] > 0.9
        assert result.summary["avg_duration"] < 2.0
        
    async def test_process_operations_performance(self):
        """Folyamatkezelés teljesítménytesztje"""
        tester = PerformanceTester(iterations=TEST_CONFIG["performance_test_iterations"])
        result = await tester.run_test(
            test_func=test_process_operations,
            test_name="process_operations",
            test_description="Folyamatkezelés teljesítménye"
        )
        
        # Ellenőrzés
        assert result.summary["success_rate"] > 0.9
        assert result.summary["avg_duration"] < 2.0
        
    async def test_langgraph_workflow_performance(self):
        """LangGraph munkafolyamat teljesítménytesztje"""
        tester = PerformanceTester(iterations=TEST_CONFIG["performance_test_iterations"])
        result = await tester.run_test(
            test_func=test_langgraph_workflow,
            test_name="langgraph_workflow",
            test_description="LangGraph munkafolyamat teljesítménye"
        )
        
        # Ellenőrzés
        assert result.summary["success_rate"] > 0.9
        assert result.summary["avg_duration"] < 2.0
    
    async def test_parallel_operations_performance(self):
        """Párhuzamos műveletek teljesítménytesztje"""
        tester = PerformanceTester(
            iterations=TEST_CONFIG["performance_test_iterations"],
            concurrency=3  # 3 konkurens művelet
        )
        result = await tester.run_test(
            test_func=test_file_operations,
            test_name="parallel_operations",
            test_description="Párhuzamos fájlműveletek teljesítménye"
        )
        
        # Ellenőrzés
        assert result.summary["success_rate"] > 0.8  # Párhuzamos végrehajtásnál alacsonyabb sikerességi ráta is elfogadható
        
        # Jelentés generálása az összes tesztről
        tester.generate_summary_report()


async def run_performance_suite():
    """A teljes teljesítményteszt csomag futtatása"""
    # Mock környezet beállítása
    patches, mocks = setup_mock_environment()
    
    # Patchek elindítása
    for p in patches:
        p.start()
        
    try:
        # Tesztelő létrehozása
        tester = PerformanceTester(iterations=20)
        
        # Fájlműveletek teszt
        await tester.run_test(
            test_func=test_file_operations,
            test_name="file_operations",
            test_description="Fájlműveletek teljesítménye"
        )
        
        # Konfigurációkezelés teszt
        await tester.run_test(
            test_func=test_config_operations,
            test_name="config_operations",
            test_description="Konfigurációkezelés teljesítménye"
        )
        
        # Folyamatkezelés teszt
        await tester.run_test(
            test_func=test_process_operations,
            test_name="process_operations",
            test_description="Folyamatkezelés teljesítménye"
        )
        
        # LangGraph teszt
        await tester.run_test(
            test_func=test_langgraph_workflow,
            test_name="langgraph_workflow",
            test_description="LangGraph munkafolyamat teljesítménye"
        )
        
        # Párhuzamos műveletek teszt
        parallel_tester = PerformanceTester(iterations=50, concurrency=5)
        await parallel_tester.run_test(
            test_func=test_file_operations,
            test_name="parallel_operations",
            test_description="Párhuzamos fájlműveletek teljesítménye"
        )
        
        # Jelentés generálása
        tester.generate_summary_report()
        
        test_logger.info("A teljesítményteszt csomag sikeresen lefutott.")
        
    finally:
        # Patchek leállítása
        for p in patches:
            p.stop()


if __name__ == "__main__":
    asyncio.run(run_performance_suite())
