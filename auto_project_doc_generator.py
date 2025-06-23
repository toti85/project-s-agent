"""
Project-S Automatikus Projekt Dokumentáció Generáló
--------------------------------------------------
Ez a modul a Project-S eszköz rendszerét használja egy komplex,
több AI-t használó dokumentáció generáló workflow létrehozására.

A script a következő lépéseket hajtja végre:
1. Projekt fájl struktúra elemzése
2. Forráskód analízise
3. Több AI modell orkesztrálása különböző feladatokra
   - GPT-4: Architektúra elemzés, design patterns felismerés
   - Claude: Kód minőség értékelés, best practices javaslatok
4. Dokumentáció generálása strukturált formában
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
import json
from datetime import datetime
import re
import traceback
from typing import Dict, List, Any, Optional, Tuple, Set

# Hozzáadjuk a projekt gyökérkönyvtárát a keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Konfiguráljuk a naplózást
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("auto_doc_generator")

# Project-S importok
try:
    from tools import register_all_tools
    from tools.file_tools import FileSearchTool, FileReadTool, FileWriteTool, FileInfoTool
    from tools.web_tools import WebPageFetchTool
    from tools.code_tools import CodeExecutionTool, PythonModuleInfoTool
    logger.info("Project-S eszköz modulok sikeresen importálva")
except ImportError as e:
    logger.error(f"Hiba történt a Project-S modulok importálásakor: {e}")
    sys.exit(1)

# AI integráció osztály (mock)
class AIModelIntegration:
    """
    AI modell integrációs osztály, amely lehetővé teszi különböző AI modellek használatát
    különböző feladatokra.
    
    Valós implementáció esetén ez kapcsolódna az OpenAI, Anthropic, stb. API-khoz.
    """
    
    async def analyze_with_model(self, model: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Az adott modellel elemzi a megadott prompt-ot és kontextust.
        """
        logger.info(f"[{model}] Elemzés a következő prompt-tal: {prompt[:50]}...")
        
        # Ebben a példában csak szimulált válaszokat generálunk
        if model == "gpt-4":
            result = self._simulate_gpt4_response(prompt, context)
        elif model == "claude-sonnet":
            result = self._simulate_claude_response(prompt, context)
        else:
            result = {"error": f"Ismeretlen modell: {model}"}
            
        return result
    
    def _simulate_gpt4_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Szimulálja egy GPT-4 válaszát (valós implementációban ez az OpenAI API-t hívná).
        """
        if "architecture" in prompt.lower():
            return {
                "model": "gpt-4",
                "content": "# Architektúra Elemzés\n\n"
                          "A Project-S egy moduláris, eszköz-alapú ágens rendszer, amely a következő fő komponensekből áll:\n\n"
                          "- **Core rendszer**: Alapvető eseménykezelés és vezérlő logika\n"
                          "- **Tools alrendszer**: Különböző eszközök implementációja egységes interfész alapján\n"
                          "- **LangGraph integráció**: Munkafolyamat-vezérlő komponens az eszközök összekapcsolására\n\n"
                          "A rendszer fő design pattern-jei közé tartozik:\n"
                          "- **Observer pattern**: Az eseménykezelő rendszerben\n"
                          "- **Factory pattern**: Az eszközök dinamikus regisztrációjához\n"
                          "- **Adapter pattern**: A külső szolgáltatások integrálásához\n"
                          "- **Strategy pattern**: A különböző végrehajtási stratégiák váltogatásához"
            }
        elif "code structure" in prompt.lower():
            return {
                "model": "gpt-4",
                "content": "# Kód Struktúra Elemzés\n\n"
                          "A Project-S kódja jól strukturált, moduláris felépítésű:\n\n"
                          "- `tools/` könyvtár: Az összes eszköz implementációját tartalmazza\n"
                          "  - `tool_interface.py`: Az alapvető BaseTool absztrakt osztályt definiálja\n"
                          "  - `tool_registry.py`: Az eszközök regisztrációját kezeli\n"
                          "  - Különböző eszköz típusok (file_tools.py, web_tools.py, stb.)\n\n"
                          "- `core/` könyvtár: A rendszer magját adó komponenseket tartalmazza\n\n"
                          "- Különböző futtatható példák és tesztek a gyökérkönyvtárban"
            }
        else:
            return {
                "model": "gpt-4",
                "content": "A Project-S rendszer egy moduláris, kiterjeszthető eszköz-alapú ágens platform."
            }
    
    def _simulate_claude_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Szimulálja egy Claude válaszát (valós implementációban ez az Anthropic API-t hívná).
        """
        if "best practices" in prompt.lower():
            return {
                "model": "claude-sonnet",
                "content": "# Kód Minőség és Best Practices\n\n"
                          "A Project-S rendszer számos jó gyakorlatot követ:\n\n"
                          "## Erősségek\n"
                          "- ✅ **Tiszta interfészek**: Az eszközök jól definiált, egységes interfészt követnek\n"
                          "- ✅ **Hibakezelés**: A kód megfelelően kezeli a hibákat és kivételeket\n"
                          "- ✅ **Aszinkronitás**: Az asyncio használata lehetővé teszi a párhuzamos végrehajtást\n\n"
                          "## Fejlesztési lehetőségek\n"
                          "- 🔄 **Dokumentáció**: Néhány komponens dokumentációja hiányos\n"
                          "- 🔄 **Tesztek**: A tesztlefedettség növelhető lenne"
            }
        elif "security" in prompt.lower():
            return {
                "model": "claude-sonnet",
                "content": "# Biztonsági Értékelés\n\n"
                          "A Project-S rendszer biztonsági szempontból:\n\n"
                          "- ✅ A CodeSandbox használata megfelelő homokozó környezetet biztosít a kód futtatásához\n"
                          "- ✅ A SystemCommandTool szigorú validációt végez a parancsokra\n"
                          "- ✅ Az eszközök regisztráció során biztonsági ellenőrzésen mennek keresztül\n\n"
                          "### Javaslatok\n"
                          "- 🔒 További input validációk implementálása\n"
                          "- 🔒 A rendszerparancs végrehajtás még további korlátozásokat igényelhet"
            }
        else:
            return {
                "model": "claude-sonnet",
                "content": "A Project-S eszköz rendszer jól strukturált, megfelelő biztonsági mechanizmusokkal rendelkezik, de néhány területen tovább fejleszthető."
            }

class ProjectStructureAnalyzer:
    """
    Elemzi a projekt struktúráját és releváns információkat gyűjt.
    """
    
    def __init__(self):
        self.file_search_tool = FileSearchTool()
        self.file_read_tool = FileReadTool()
        self.file_info_tool = FileInfoTool()
    
    async def get_project_structure(self, project_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Elemzi a projekt könyvtárszerkezetét és visszaadja a főbb komponenseket.
        """
        logger.info(f"Projekt struktúra elemzése: {project_path}")
          # Keressük meg az összes Python fájlt
        python_files = await self.file_search_tool.execute(
            pattern="**/*.py",
            root_dir=project_path,
            recursive=True
        )
        
        # Keressük meg az összes konfigurációs fájlt
        config_files = await self.file_search_tool.execute(
            pattern="**/*.{json,yaml,yml,ini,toml}",
            root_dir=project_path,
            recursive=True
        )
        
        # Keressük meg a dokumentációs fájlokat
        doc_files = await self.file_search_tool.execute(
            pattern="**/*.{md,rst,txt}",
            root_dir=project_path,
            recursive=True
        )
        
        return {
            "python_files": python_files.get("files", []),
            "config_files": config_files.get("files", []),
            "doc_files": doc_files.get("files", []),
            "project_path": project_path
        }
    
    async def analyze_python_files(self, files: List[str], max_files: int = 20) -> Dict[str, Any]:
        """
        Elemzi a Python fájlok tartalmát, azonosítja a főbb osztályokat, függvényeket.
        """
        logger.info(f"Python fájlok elemzése, {len(files)} fájl, max {max_files} elemzése")
        
        results = []
        
        # Korlátozzuk a fájlok számát, hogy ne elemezzünk túl sokat
        files = files[:max_files]
        
        for file_path in files:
            try:
                # Fájl információk lekérdezése
                file_info = await self.file_info_tool.execute(path=file_path)
                
                # Fájl tartalom olvasása
                file_content = await self.file_read_tool.execute(
                    path=file_path, 
                    max_size=50000  # Korlátozzuk a méretét
                )
                
                if not file_content.get("success", False):
                    logger.warning(f"Nem sikerült olvasni a fájlt: {file_path}")
                    continue
                
                content = file_content.get("content", "")
                
                # Egyszerű analízis - osztályok és függvények keresése
                classes = re.findall(r"class\s+(\w+)\s*\(", content)
                functions = re.findall(r"def\s+(\w+)\s*\(", content)
                
                # Docstring ellenőrzése
                has_module_docstring = bool(re.search(r'^"""[\s\S]+?"""', content))
                
                results.append({
                    "path": file_path,
                    "size": file_info.get("size", 0),
                    "last_modified": file_info.get("last_modified", ""),
                    "classes": classes,
                    "functions": functions,
                    "has_module_docstring": has_module_docstring,
                    "lines_of_code": content.count('\n') + 1
                })
            
            except Exception as e:
                logger.error(f"Hiba a fájl elemzése közben {file_path}: {str(e)}")
        
        return {
            "analyzed_files_count": len(results),
            "total_files_count": len(files),
            "files": results
        }

class DocumentationGenerator:
    """
    A dokumentáció generálását végző osztály.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Inicializálás, alap könyvtár beállítása.
        """
        self.output_dir = output_dir or str(Path.cwd() / "outputs")
        self.file_write_tool = FileWriteTool()
        # Előre létrehozzuk a könyvtárat
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_readme(self, project_data: Dict[str, Any], ai_results: Dict[str, Any]) -> str:
        """
        README.md generálás a projekt adatok és az AI elemzések alapján.
        """
        logger.info("README.md generálása...")
        
        # Tartalom összeállítása
        gpt_architecture = ai_results.get("architecture", {}).get("content", "")
        claude_best_practices = ai_results.get("best_practices", {}).get("content", "")
        
        project_name = Path(project_data.get("project_path", "")).name
        
        content = f"""# {project_name.upper()} Projekt Dokumentáció

## Projekt Leírás
A Project-S egy eszköz alapú, moduláris ágensrendszer, amely támogatja a munkafolyamat-vezérelt AI feladatokat.

## Főbb Komponensek
- Tools alrendszer különböző feladatok végrehajtására
- LangGraph integráció munkafolyamatok definiálására
- Több AI modell támogatása különböző specializált feladatokra

## Projektstruktúra
- Python fájlok: {len(project_data.get("python_files", []))}
- Konfigurációs fájlok: {len(project_data.get("config_files", []))}
- Dokumentációs fájlok: {len(project_data.get("doc_files", []))}

## Architektúra Összefoglaló
{gpt_architecture}

## Kód minőségi értékelés
{claude_best_practices}

## Telepítés és Használat
```bash
# Függőségek telepítése
pip install -r requirements.txt

# Alap rendszer futtatása
python main_minimal.py
```

Ez a dokumentáció automatikusan generált a Project-S dokumentáció generáló rendszerével.
Generálás ideje: {datetime.now().isoformat()}
"""
          # Biztosítjuk, hogy a könyvtár létezzen
        os.makedirs(os.path.dirname(self.output_dir), exist_ok=True)
        
        # Dokumentáció kiírása
        readme_path = os.path.join(self.output_dir, "README.md")
        result = await self.file_write_tool.execute(
            path=readme_path,
            content=content
        )
        
        if result.get("success", False):
            logger.info(f"README.md sikeresen létrehozva: {readme_path}")
        else:
            logger.error(f"Hiba a README.md írása közben: {result.get('error')}")
        
        return readme_path
    
    async def generate_project_analysis(self, project_data: Dict[str, Any], 
                                       file_analysis: Dict[str, Any],
                                       ai_results: Dict[str, Any]) -> str:
        """
        Részletes PROJECT_ANALYSIS.md generálás.
        """
        logger.info("PROJECT_ANALYSIS.md generálása...")
        
        # AI elemzések kinyerése
        gpt_structure = ai_results.get("code_structure", {}).get("content", "")
        claude_security = ai_results.get("security", {}).get("content", "")
        
        # Fájl statisztikák kiszámítása
        files = file_analysis.get("files", [])
        total_loc = sum(f.get("lines_of_code", 0) for f in files)
        classes_count = sum(len(f.get("classes", [])) for f in files)
        functions_count = sum(len(f.get("functions", [])) for f in files)
        
        # Legnagyobb fájlok azonosítása
        largest_files = sorted(files, key=lambda x: x.get("lines_of_code", 0), reverse=True)[:5]
        largest_files_content = "\n".join([f"- **{Path(f['path']).name}**: {f['lines_of_code']} sor" for f in largest_files])
        
        # Legtöbb osztályt tartalmazó fájlok
        most_classes = sorted(files, key=lambda x: len(x.get("classes", [])), reverse=True)[:5]
        most_classes_content = "\n".join([f"- **{Path(f['path']).name}**: {len(f['classes'])} osztály" for f in most_classes])
        
        # Projekt fájl struktúra
        main_dirs = set()
        for file in project_data.get("python_files", []):
            parts = Path(file).parts
            if len(parts) > 1:  # Ha van legalább egy könyvtár
                main_dirs.add(parts[0])
        
        directories_content = "\n".join([f"- **{dir}/**" for dir in sorted(main_dirs)])
        
        content = f"""# PROJECT-S RÉSZLETES ANALÍZIS

## Statisztikák
- **Python fájlok száma**: {len(project_data.get("python_files", []))}
- **Összes kódsor**: {total_loc}
- **Osztályok száma**: {classes_count}
- **Függvények száma**: {functions_count}
- **Konfigurációs fájlok**: {len(project_data.get("config_files", []))}
- **Dokumentációs fájlok**: {len(project_data.get("doc_files", []))}

## Főbb könyvtárak
{directories_content}

## Legnagyobb fájlok (kódsorok alapján)
{largest_files_content}

## Legtöbb osztályt tartalmazó fájlok
{most_classes_content}

## Kód struktúra elemzés
{gpt_structure}

## Biztonsági értékelés
{claude_security}

## Fejlesztési javaslatok
1. A dokumentáció további bővítése, különösen az API-k részleteinek leírása
2. Egységes hibaüzenetek és naplózási rendszer bevezetése
3. A tesztek lefedettségének növelése
4. Az eszközök közötti kapcsolatok jobb dokumentálása

Ez az elemzés a Project-S automatikus dokumentáció generáló rendszerével készült.
Generálás ideje: {datetime.now().isoformat()}
"""
          # Dokumentáció kiírása
        analysis_path = os.path.join(self.output_dir, "PROJECT_ANALYSIS.md")
        result = await self.file_write_tool.execute(
            path=analysis_path,
            content=content
        )
        
        if result.get("success", False):
            logger.info(f"PROJECT_ANALYSIS.md sikeresen létrehozva: {analysis_path}")
        else:
            logger.error(f"Hiba a PROJECT_ANALYSIS.md írása közben: {result.get('error')}")
        
        return analysis_path

class ProjectDocumentationGenerator:
    """
    Fő osztály a projekt dokumentáció generálásához, amely koordinálja a folyamatot.
    """
    
    def __init__(self, project_path: str):
        """
        Inicializálás a projekt útvonalával.
        """
        self.project_path = project_path
        self.output_dir = os.path.join(project_path, "outputs")
        
        # Komponensek létrehozása
        self.analyzer = ProjectStructureAnalyzer()
        self.ai_integration = AIModelIntegration()
        self.doc_generator = DocumentationGenerator(self.output_dir)
    
    async def generate_documentation(self) -> Dict[str, Any]:
        """
        A dokumentáció generálás teljes folyamata.
        """
        try:
            logger.info(f"Dokumentáció generálás indítása a következő projektre: {self.project_path}")
            
            # 1. Projekt struktúra elemzése
            logger.info("1. lépés: Projekt struktúra elemzése")
            project_data = await self.analyzer.get_project_structure(self.project_path)
            
            # 2. Python fájlok részletes elemzése
            logger.info("2. lépés: Python fájlok részletes elemzése")
            file_analysis = await self.analyzer.analyze_python_files(project_data["python_files"])
            
            # 3. AI elemzések végrehajtása
            logger.info("3. lépés: AI elemzések végrehajtása")
            ai_results = {}
            
            # GPT-4 használata architektúra elemzéshez
            logger.info("GPT-4 használata architektúra elemzéshez")
            ai_results["architecture"] = await self.ai_integration.analyze_with_model(
                model="gpt-4", 
                prompt="Elemezd a projekt architektúráját és azonosítsd a fő design pattern-eket.",
                context={"project_data": project_data, "file_analysis": file_analysis}
            )
            
            # GPT-4 használata kód struktúra elemzéshez
            logger.info("GPT-4 használata kód struktúra elemzéshez")
            ai_results["code_structure"] = await self.ai_integration.analyze_with_model(
                model="gpt-4", 
                prompt="Elemezd a projekt kód struktúráját és fő komponenseit.",
                context={"project_data": project_data, "file_analysis": file_analysis}
            )
            
            # Claude használata best practices elemzéshez
            logger.info("Claude használata best practices elemzéshez")
            ai_results["best_practices"] = await self.ai_integration.analyze_with_model(
                model="claude-sonnet", 
                prompt="Értékeld a kód minőségét és ajánlj best practices technikákat.",
                context={"project_data": project_data, "file_analysis": file_analysis}
            )
            
            # Claude használata biztonsági elemzéshez
            logger.info("Claude használata biztonsági elemzéshez")
            ai_results["security"] = await self.ai_integration.analyze_with_model(
                model="claude-sonnet", 
                prompt="Értékeld a projekt biztonsági aspektusait, különösen a kód futtatás és rendszerparancs végrehajtás szempontjából.",
                context={"project_data": project_data, "file_analysis": file_analysis}
            )
            
            # 4. Dokumentáció generálása
            logger.info("4. lépés: Dokumentáció generálása")
            readme_path = await self.doc_generator.generate_readme(project_data, ai_results)
            analysis_path = await self.doc_generator.generate_project_analysis(project_data, file_analysis, ai_results)
            
            return {
                "success": True,
                "readme_path": readme_path,
                "analysis_path": analysis_path,
                "project_data": project_data,
                "ai_results": ai_results
            }
            
        except Exception as e:
            logger.error(f"Hiba történt a dokumentáció generálása közben: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

async def update_status(status_path: str, new_status: Dict[str, Any]) -> bool:
    """
    A PROJECT_STATUS.md fájl frissítése az új státusszal.
    """
    try:
        # Olvasó és író eszközök létrehozása
        file_read_tool = FileReadTool()
        file_write_tool = FileWriteTool()
        
        # Jelenlegi tartalom olvasása
        result = await file_read_tool.execute(path=status_path)
        
        if not result.get("success", False):
            logger.error(f"Nem sikerült olvasni a státusz fájlt: {status_path}")
            return False
        
        content = result["content"]
        
        # Frissítjük a dátumot
        content = re.sub(
            r'- \*\*Utolsó frissítés\*\*: .*',
            f'- **Utolsó frissítés**: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            content
        )
        
        # Frissítjük az aktuális feladatot
        current_task_section = "## 🔄 JELENLEGI MUNKA"
        task_updated = False
        
        lines = content.split('\n')
        for i in range(len(lines)):
            if lines[i].strip() == current_task_section:
                if i + 1 < len(lines):
                    lines[i + 1] = f"**Aktuális feladat**: {new_status['current_task']}"
                if i + 2 < len(lines):
                    lines[i + 2] = f"**Utolsó módosítás**: {new_status['last_modification']}"
                if i + 3 < len(lines):
                    lines[i + 3] = f"**Következő lépés**: {new_status['next_step']}"
                task_updated = True
                break
        
        if not task_updated:
            logger.warning("Nem található a JELENLEGI MUNKA szekció a PROJECT_STATUS.md fájlban")
        
        # Frissítjük a fájl struktúrát az új fájlokkal
        if "new_files" in new_status:
            file_structure_section = "## 📁 FÁJLSTRUKTÚRA"
            structure_updated = False
            
            for i in range(len(lines)):
                if lines[i].strip() == file_structure_section:
                    for j in range(i+1, len(lines)):
                        if lines[j].strip() == "```":
                            # Keressük meg a befejező ```-t
                            for k in range(j+1, len(lines)):
                                if lines[k].strip() == "```":
                                    # Új fájlok hozzáadása a struktúrához
                                    for file, status in new_status["new_files"].items():
                                        new_line = f"├── {file} {status}"
                                        lines.insert(k, new_line)
                                    structure_updated = True
                                    break
                            break
                    break
            
            if not structure_updated:
                logger.warning("Nem található a FÁJLSTRUKTÚRA szekció a PROJECT_STATUS.md fájlban")
        
        # Összeállítjuk az új tartalmat és írjuk a fájlba
        new_content = '\n'.join(lines)
        
        # Mentjük a frissített státuszt
        write_result = await file_write_tool.execute(
            path=status_path,
            content=new_content
        )
        
        if write_result.get("success", False):
            logger.info(f"PROJECT_STATUS.md sikeresen frissítve")
            return True
        else:
            logger.error(f"Hiba a PROJECT_STATUS.md frissítése közben: {write_result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Hiba a státusz frissítésekor: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """
    Fő belépési pont a dokumentáció generáló futtatásához.
    """
    logger.info("=== Project-S Automatikus Dokumentáció Generáló ===")
    
    # Projekt könyvtár beállítása
    project_path = str(Path(__file__).parent)
    
    try:
        # Eszközök regisztrálása
        await register_all_tools()
        logger.info("✅ Eszközök sikeresen regisztrálva")
        
        # Dokumentáció generátor inicializálása
        doc_generator = ProjectDocumentationGenerator(project_path)
        
        # Frissítjük a PROJECT_STATUS.md-t az indulás jelzésére
        await update_status(
            os.path.join(project_path, "PROJECT_STATUS.md"),
            {
                "current_task": "Automatikus projekt dokumentáció generálás",
                "last_modification": "Dokumentáció generáló rendszer inicializálása",
                "next_step": "Dokumentáció generálása és mentése",
                "new_files": {
                    "auto_project_doc_generator.py": "✅ [Új]"
                }
            }
        )
        
        # Dokumentáció generálása
        result = await doc_generator.generate_documentation()
        
        if result.get("success", False):
            logger.info("🎉 Dokumentáció generálás sikeres!")
            logger.info(f"📄 README.md: {result.get('readme_path')}")
            logger.info(f"📄 PROJECT_ANALYSIS.md: {result.get('analysis_path')}")
            
            # Frissítjük a PROJECT_STATUS.md-t a befejezés jelzésére
            await update_status(
                os.path.join(project_path, "PROJECT_STATUS.md"),
                {
                    "current_task": "Automatikus projekt dokumentáció generálás",
                    "last_modification": "Dokumentáció generálás befejezve, README.md és PROJECT_ANALYSIS.md elkészült",
                    "next_step": "A generált dokumentáció ellenőrzése és finomhangolása",
                    "new_files": {
                        "outputs/README.md": "📝 [Generált]",
                        "outputs/PROJECT_ANALYSIS.md": "📝 [Generált]"
                    }
                }
            )
        else:
            logger.error(f"💥 Dokumentáció generálás sikertelen: {result.get('error')}")
            
            # Frissítjük a PROJECT_STATUS.md-t a hiba jelzésére
            await update_status(
                os.path.join(project_path, "PROJECT_STATUS.md"),
                {
                    "current_task": "Automatikus projekt dokumentáció generálás",
                    "last_modification": f"Dokumentáció generálás sikertelen: {result.get('error', 'Ismeretlen hiba')}",
                    "next_step": "A hiba javítása és újrapróbálkozás"
                }
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Hiba a dokumentáció generáló futtatása közben: {str(e)}")
        traceback.print_exc()
        
        # Frissítjük a PROJECT_STATUS.md-t a hiba jelzésére
        await update_status(
            os.path.join(project_path, "PROJECT_STATUS.md"),
            {
                "current_task": "Automatikus projekt dokumentáció generálás",
                "last_modification": f"Hibaelhárítás: {str(e)}",
                "next_step": "A hiba javítása és újrapróbálkozás"
            }
        )
        
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(main())
    
    print("\n=== Automatikus Dokumentáció Generáló Eredmény ===")
    if result.get("success", False):
        print("✅ A dokumentáció generálás sikeresen befejezve!")
        print(f"📊 Létrehozott fájlok:")
        print(f"  - {result.get('readme_path')}")
        print(f"  - {result.get('analysis_path')}")
    else:
        print(f"❌ Hiba: {result.get('error', 'Ismeretlen hiba')}")
