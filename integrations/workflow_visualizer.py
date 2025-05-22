"""
Project-S + LangGraph munkafolyamat vizualizáció
-----------------------------------------------
Ez a modul a LangGraph munkafolyamatok vizualizálására szolgál,
segítve a hibakeresést és a rendszer működésének megértését.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Próbáljuk importálni a vizualizációs könyvtárakat
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Próbáljuk importálni a diagnosztikai kezelőt
try:
    from core.diagnostics import diagnostics_manager
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False
    
# Logger beállítása
logger = logging.getLogger(__name__)

class WorkflowVisualizer:
    """
    LangGraph munkafolyamatok állapotának és struktúrájának vizualizálása
    """
    
    def __init__(self, output_dir: Optional[str] = "diagnostics/workflows"):
        """
        Inicializálja a munkafolyamat vizualizációs komponenst
        
        Args:
            output_dir: A könyvtár, ahova a vizualizációk kerülnek
        """
        self.output_dir = output_dir
        
        # Ellenőrizzük, hogy rendelkezésre áll-e a vizualizációs lehetőség
        if not VISUALIZATION_AVAILABLE:
            logger.warning("A vizualizációs könyvtárak (matplotlib, networkx) nem elérhetők, "
                         "a munkamenet vizualizálás korlátozott lesz")
        
        # Könyvtár létrehozása
        os.makedirs(output_dir, exist_ok=True)
    
    async def visualize_workflow(self, workflow_id: str, workflow_state: Dict[str, Any],
                               format_type: str = "png") -> Optional[str]:
        """
        Egy munkafolyamat vizualizálása az állapota alapján
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            workflow_state: A munkafolyamat állapota (tartalmaznia kell a lépéseket)
            format_type: A kimeneti fájl formátuma ('png', 'svg', stb.)
            
        Returns:
            str: A generált kép útvonala, vagy None, ha nem sikerült
        """
        if not VISUALIZATION_AVAILABLE:
            logger.warning("A vizualizációs könyvtárak nem elérhetők, a vizualizáció nem lehetséges")
            return None
        
        try:
            # Állapotsúgó létrehozása, amely a workflow állapot adatait tartalmazza
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"{workflow_id}_{timestamp_str}.{format_type}")
            
            # Munkafolyamat lépéseinek kinyerése
            steps = workflow_state.get("context", {}).get("workflow_steps", [])
            if not steps:
                logger.warning(f"Nem találhatók lépések a munkafolyamatban ({workflow_id})")
                return None
                
            # Gráf létrehozása
            G = nx.DiGraph()
            
            # Csúcsok hozzáadása
            current_step_name = None
            if "current_task" in workflow_state and workflow_state["current_task"]:
                current_step_name = workflow_state["current_task"].get("name", "")
            
            for i, step in enumerate(steps):
                step_name = step.get("name", f"Step {i+1}")
                step_type = step.get("type", "unknown")
                step_status = "current" if step_name == current_step_name else "pending"
                
                # A már végrehajtott lépések megjelölése
                if "command_history" in workflow_state:
                    for cmd in workflow_state["command_history"]:
                        if cmd.get("name", "") == step_name:
                            step_status = "completed"
                            break
                
                # Csúcs hozzáadása a megfelelő tulajdonságokkal
                G.add_node(step_name, type=step_type, status=step_status)
            
            # Elágazások kezelése
            branches = workflow_state.get("context", {}).get("branches", {})
            
            # Alap útvonal - egymás után következő lépések
            for i in range(len(steps) - 1):
                G.add_edge(
                    steps[i].get("name", f"Step {i+1}"),
                    steps[i+1].get("name", f"Step {i+2}")
                )
            
            # Branch-ek hozzáadása
            for branch_name, branch_steps in branches.items():
                if branch_steps and len(branch_steps) > 0:
                    # Az első lépés hozzáadása a gráfhoz
                    branch_start_name = branch_steps[0].get("name", f"Branch {branch_name} Step 1")
                    branch_start_type = branch_steps[0].get("type", "unknown")
                    G.add_node(branch_start_name, type=branch_start_type, branch=branch_name)
                    
                    # Többi lépés hozzáadása
                    for i in range(len(branch_steps) - 1):
                        step_name = branch_steps[i].get("name", f"Branch {branch_name} Step {i+1}")
                        next_step_name = branch_steps[i+1].get("name", f"Branch {branch_name} Step {i+2}")
                        G.add_edge(step_name, next_step_name)
            
            # Gráf kirajzolása
            plt.figure(figsize=(12, 10))
            pos = nx.spring_layout(G, seed=42)  # Elrendezés
            
            # Csúcsok színezése a típus és állapot alapján
            node_colors = []
            node_sizes = []
            
            for node in G.nodes():
                node_data = G.nodes[node]
                node_type = node_data.get("type", "unknown")
                node_status = node_data.get("status", "pending")
                
                # Színek a státusz alapján
                if node_status == "completed":
                    node_colors.append("#4CAF50")  # Zöld - befejezett
                    node_sizes.append(2000)
                elif node_status == "current":
                    node_colors.append("#FF9800")  # Narancs - aktuális
                    node_sizes.append(2500)  # Nagyobb, hogy kitűnjön
                else:
                    # Típus szerinti színezés, ha még nincs végrehajtva
                    if node_type == "command":
                        node_colors.append("#2196F3")  # Kék - parancs
                    elif node_type == "decision":
                        node_colors.append("#FFC107")  # Sárga - döntés
                    else:
                        node_colors.append("#9C27B0")  # Lila - egyéb
                    
                    node_sizes.append(2000)
            
            # Gráf kirajzolása
            nx.draw(
                G, pos,
                with_labels=True,
                node_color=node_colors,
                node_size=node_sizes,
                font_size=10,
                font_weight="bold",
                arrowsize=20,
                edge_color="#555555"
            )
            
            # Státusz információ
            status = workflow_state.get("status", "unknown")
            retry_count = workflow_state.get("retry_count", 0)
            
            title_parts = [
                f"Munkafolyamat: {workflow_id}",
                f"Státusz: {status.upper()}"
            ]
            
            if retry_count > 0:
                title_parts.append(f"Újrapróbálkozások: {retry_count}")
                
            title = " | ".join(title_parts)
            plt.title(title)
            
            # Mentés
            plt.savefig(output_path, dpi=120, bbox_inches="tight")
            plt.close()
            
            logger.info(f"Munkafolyamat vizualizáció elmentve: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Hiba a munkafolyamat vizualizálása közben: {e}", exc_info=True)
            return None
    
    async def visualize_workflow_history(self, workflow_id: str, states_history: List[Dict[str, Any]],
                                       output_path: Optional[str] = None) -> Optional[str]:
        """
        Egy munkafolyamat állapotváltozásainak vizualizálása
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            states_history: A munkafolyamat állapotainak listája
            output_path: Opcionális kimeneti útvonal
            
        Returns:
            str: A generált animált GIF útvonala vagy None, ha nem sikerült
        """
        if not VISUALIZATION_AVAILABLE:
            logger.warning("A vizualizációs könyvtárak nem elérhetők, a vizualizáció nem lehetséges")
            return None
            
        try:
            import imageio
            import tempfile
            
            # Ha nincs explicit kimenet megadva, generálunk egyet
            if not output_path:
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.output_dir, f"{workflow_id}_history_{timestamp_str}.gif")
            
            # Ideiglenes könyvtár a képkockákhoz
            with tempfile.TemporaryDirectory() as temp_dir:
                frame_paths = []
                
                # Minden állapothoz egy képkocka
                for i, state in enumerate(states_history):
                    frame_path = os.path.join(temp_dir, f"frame_{i:03d}.png")
                    frame_paths.append(frame_path)
                    
                    # Gráf létrehozása az aktuális állapothoz
                    G = nx.DiGraph()
                    
                    # Lépések kinyerése
                    steps = state.get("context", {}).get("workflow_steps", [])
                    current_step_name = None
                    if "current_task" in state and state["current_task"]:
                        current_step_name = state["current_task"].get("name", "")
                    
                    # Csúcsok hozzáadása
                    for j, step in enumerate(steps):
                        step_name = step.get("name", f"Step {j+1}")
                        step_type = step.get("type", "unknown")
                        step_status = "current" if step_name == current_step_name else "pending"
                        
                        # Már végrehajtott lépések megjelölése
                        if "command_history" in state:
                            for cmd in state["command_history"]:
                                if cmd.get("name", "") == step_name:
                                    step_status = "completed"
                                    break
                        
                        # Csúcs hozzáadása
                        G.add_node(step_name, type=step_type, status=step_status)
                    
                    # Élek hozzáadása
                    for j in range(len(steps) - 1):
                        G.add_edge(
                            steps[j].get("name", f"Step {j+1}"),
                            steps[j+1].get("name", f"Step {j+2}")
                        )
                    
                    # Kép kirajzolása
                    plt.figure(figsize=(10, 8))
                    pos = nx.spring_layout(G, seed=42)  # Mindig ugyanazt az elrendezést használjuk
                    
                    # Csúcsok színezése
                    node_colors = []
                    for node in G.nodes():
                        node_data = G.nodes[node]
                        node_status = node_data.get("status", "pending")
                        
                        if node_status == "completed":
                            node_colors.append("#4CAF50")  # Zöld - befejezett
                        elif node_status == "current":
                            node_colors.append("#FF9800")  # Narancs - aktuális
                        else:
                            node_colors.append("#2196F3")  # Kék - függőben
                    
                    # Gráf kirajzolása
                    nx.draw(
                        G, pos,
                        with_labels=True,
                        node_color=node_colors,
                        node_size=2000,
                        font_size=10,
                        font_weight="bold",
                        arrowsize=20
                    )
                    
                    # Állapot információ
                    title = f"Munkafolyamat: {workflow_id} | Állapot: {i+1}/{len(states_history)}"
                    plt.title(title)
                    
                    # Kép mentése
                    plt.savefig(frame_path, dpi=100, bbox_inches="tight")
                    plt.close()
                
                # Animált GIF létrehozása
                if frame_paths:
                    images = [imageio.imread(frame_path) for frame_path in frame_paths]
                    imageio.mimsave(output_path, images, duration=1.0)  # 1 másodperc képkockánként
                    
                    logger.info(f"Munkafolyamat történet animáció elmentve: {output_path}")
                    return output_path
                else:
                    logger.warning("Nem sikerült képkockákat generálni az animációhoz")
                    return None
                
        except Exception as e:
            logger.error(f"Hiba a munkafolyamat történet vizualizálása közben: {e}", exc_info=True)
            return None
    
    def export_workflow_data(self, workflow_id: str, workflow_state: Dict[str, Any],
                          output_path: Optional[str] = None, format: str = "json") -> Optional[str]:
        """
        Exportálja egy munkafolyamat adatait olvasható formátumban
        
        Args:
            workflow_id: A munkafolyamat azonosítója
            workflow_state: A munkafolyamat állapota
            output_path: A kimeneti fájl útvonala, vagy None az alapértelmezett használatához
            format: A kimeneti formátum ('json', 'yaml')
            
        Returns:
            str: A generált fájl útvonala, vagy None, ha nem sikerült
        """
        try:
            # Exportálható adatok előkészítése
            export_data = {
                "workflow_id": workflow_id,
                "status": workflow_state.get("status", "unknown"),
                "created_at": workflow_state.get("context", {}).get("created_at", "unknown"),
                "steps": workflow_state.get("context", {}).get("workflow_steps", []),
                "current_task": workflow_state.get("current_task"),
                "command_history": workflow_state.get("command_history", []),
                "error_info": workflow_state.get("error_info"),
                "retry_count": workflow_state.get("retry_count", 0),
                "branch": workflow_state.get("branch"),
                "branches": workflow_state.get("context", {}).get("branches", {}),
                "exported_at": datetime.now().isoformat()
            }
            
            # Ha nincs explicit kimenet megadva, generálunk egyet
            if not output_path:
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.output_dir, f"{workflow_id}_data_{timestamp_str}.{format}")
            
            # Exportálás a megfelelő formátumban
            if format.lower() == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, default=str)
            elif format.lower() in ("yaml", "yml"):
                import yaml  # Lazy import
                with open(output_path, "w", encoding="utf-8") as f:
                    yaml.dump(export_data, f, sort_keys=False, default_flow_style=False)
            else:
                logger.warning(f"Nem támogatott formátum: {format}")
                return None
            
            logger.info(f"Munkafolyamat adatok exportálva: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Hiba a munkafolyamat adatok exportálása közben: {e}", exc_info=True)
            return None

# Globális vizualizáló példány
workflow_visualizer = WorkflowVisualizer()


# Segédfüggvény
async def visualize_current_workflows(workflow_states: Dict[str, Dict[str, Any]], 
                                    output_dir: Optional[str] = None) -> List[str]:
    """
    Vizualizálja az összes jelenleg aktív munkafolyamatot
    
    Args:
        workflow_states: A munkafolyamat azonosítók és állapotok szótára
        output_dir: Opcionális kimeneti könyvtár
        
    Returns:
        List[str]: A generált képek útvonalainak listája
    """
    visualizer = workflow_visualizer
    
    # Ha egyedi kimeneti könyvtárat adtak meg, új példányt hozunk létre
    if output_dir:
        visualizer = WorkflowVisualizer(output_dir=output_dir)
    
    image_paths = []
    for workflow_id, state in workflow_states.items():
        image_path = await visualizer.visualize_workflow(workflow_id, state)
        if image_path:
            image_paths.append(image_path)
    
    return image_paths
