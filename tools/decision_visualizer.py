"""
Döntési Útvonal Vizualizáló Eszköz
---------------------------------
Ez az eszköz vizualizálja a döntési útvonalakat a LangGraph munkafolyamatokban.
"""
import os
import sys
import json
import time
import logging
import argparse
import asyncio
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

# Project-S importok
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from integrations.decision_router import decision_router
from integrations.advanced_decision_router import advanced_decision_router

# Logging beállítása
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("decision_visualizer")

class DecisionVisualizer:
    """A döntési útvonalak vizualizálására szolgáló osztály."""
    
    def __init__(self):
        """Inicializálja a döntési vizualizálót."""
        self.decision_routers = {
            "basic": decision_router,
            "advanced": advanced_decision_router
        }
    
    def get_workflow_decisions(self, graph_id: str, router_type: str = "basic") -> List[Dict[str, Any]]:
        """
        Lekéri egy munkafolyamat döntéstörténetét.
        
        Args:
            graph_id: A munkafolyamat azonosítója
            router_type: A döntési router típusa ("basic" vagy "advanced")
            
        Returns:
            A döntéstörténet listaként
        """
        router = self.decision_routers.get(router_type, decision_router)
        return router.get_decision_history(graph_id)
    
    def visualize_decision_path(self, graph_id: str, router_type: str = "basic", 
                               output_path: Optional[str] = None, show_plot: bool = True):
        """
        Vizualizálja egy munkafolyamat döntési útvonalát.
        
        Args:
            graph_id: A munkafolyamat azonosítója
            router_type: A döntési router típusa ("basic" vagy "advanced")
            output_path: A kimeneti fájl útvonala (opcionális)
            show_plot: Megjelenítse-e a grafikont
        """
        # Döntéstörténet lekérése
        decisions = self.get_workflow_decisions(graph_id, router_type)
        
        if not decisions:
            logger.warning(f"Nem található döntéstörténet a következő munkafolyamathoz: {graph_id}")
            return
        
        # Gráf létrehozása
        G = nx.DiGraph()
        
        # Csomópontok hozzáadása
        nodes = set()
        for decision in decisions:
            source_node = decision.get("source_node")
            selected_option = decision.get("selected_option")
            nodes.add(source_node)
            nodes.add(selected_option)
        
        for node in nodes:
            G.add_node(node)
        
        # Élek hozzáadása
        for i, decision in enumerate(decisions):
            source_node = decision.get("source_node")
            selected_option = decision.get("selected_option")
            
            # Él hozzáadása a döntési forrás és a kiválasztott opció között
            G.add_edge(source_node, selected_option, weight=2, decision=True)
            
            # Kapcsolódás a következő döntési ponthoz, ha van
            if i < len(decisions) - 1 and selected_option != decisions[i+1].get("source_node"):
                G.add_edge(selected_option, decisions[i+1].get("source_node"), weight=1, decision=False)
        
        # Gráf rajzolása
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Csomópontok rajzolása
        decision_nodes = [node for node in G.nodes() if any(d.get("source_node") == node for d in decisions)]
        other_nodes = [node for node in G.nodes() if node not in decision_nodes]
        
        nx.draw_networkx_nodes(G, pos, nodelist=decision_nodes, node_color="lightblue", 
                              node_size=700, alpha=0.8, node_shape="o")
        nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, node_color="lightgreen", 
                              node_size=700, alpha=0.8, node_shape="s")
        
        # Élek rajzolása
        decision_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("decision", False)]
        other_edges = [(u, v) for u, v, d in G.edges(data=True) if not d.get("decision", False)]
        
        nx.draw_networkx_edges(G, pos, edgelist=decision_edges, width=2, alpha=0.7, 
                              edge_color="red", style="solid", arrows=True, arrowsize=20)
        nx.draw_networkx_edges(G, pos, edgelist=other_edges, width=1, alpha=0.5, 
                              edge_color="grey", style="dashed", arrows=True)
        
        # Címkék
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
        
        # Jelmagyarázat
        decision_legend = Line2D([0], [0], color="red", linewidth=2, label="Döntési él")
        flow_legend = Line2D([0], [0], color="grey", linewidth=1, linestyle="dashed", label="Folyamat él")
        decision_node_legend = plt.scatter([], [], c="lightblue", s=100, label="Döntési csomópont")
        process_node_legend = plt.scatter([], [], c="lightgreen", s=100, marker="s", label="Feldolgozó csomópont")
        
        plt.legend(handles=[decision_legend, flow_legend, decision_node_legend, process_node_legend], 
                  loc="upper right")
        
        # Információ hozzáadása a címhez
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        plt.title(f"Döntési útvonal: {graph_id}\n{timestamp}")
        plt.axis("off")
        
        # Mentés, ha szükséges
        if output_path:
            plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"Döntési útvonal mentve: {output_path}")
        
        # Megjelenítés, ha szükséges
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def visualize_decision_stats(self, router_type: str = "advanced", 
                                output_path: Optional[str] = None, show_plot: bool = True):
        """
        Vizualizálja a globális döntési statisztikákat.
        
        Args:
            router_type: A döntési router típusa ("basic" vagy "advanced")
            output_path: A kimeneti fájl útvonala (opcionális)
            show_plot: Megjelenítse-e a grafikont
        """
        if router_type != "advanced":
            logger.warning("A globális döntési statisztikák csak a fejlett router esetén érhetők el.")
            return
        
        # Statisztikák lekérése
        stats = advanced_decision_router.analyze_global_decision_trends()
        
        if not stats:
            logger.warning("Nem találhatók globális döntési statisztikák.")
            return
        
        # Ábrák létrehozása
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Top döntési pontok
        top_nodes = stats.get("top_decision_points", {})
        if top_nodes:
            nodes = list(top_nodes.keys())
            values = list(top_nodes.values())
            ax1.bar(nodes, values, color="lightblue")
            ax1.set_title("Leggyakoribb döntési pontok")
            ax1.set_xlabel("Döntési pont")
            ax1.set_ylabel("Előfordulások száma")
            plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        
        # Gyakori útvonalak
        frequent_paths = stats.get("frequent_paths", {})
        if frequent_paths:
            paths = list(frequent_paths.keys())[:5]  # Top 5
            counts = [frequent_paths[p] for p in paths]
            ax2.bar(paths, counts, color="lightgreen")
            ax2.set_title("Leggyakoribb döntési útvonalak")
            ax2.set_xlabel("Útvonal")
            ax2.set_ylabel("Előfordulások száma")
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")
        
        # Összefoglaló statisztikák szövegként
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        plt.figtext(0.5, 0.01, 
                   f"Összes döntés: {stats.get('total_decisions', 0)} | "
                   f"Munkafolyamatok: {stats.get('total_workflows', 0)} | "
                   f"Időpont: {timestamp}", 
                   ha="center", fontsize=10, bbox={"facecolor":"white", "alpha":0.5, "pad":5})
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Mentés, ha szükséges
        if output_path:
            plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
            logger.info(f"Döntési statisztikák mentve: {output_path}")
        
        # Megjelenítés, ha szükséges
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def export_decisions_to_json(self, graph_id: str, router_type: str = "basic", 
                                output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Exportálja a döntéseket JSON formátumba.
        
        Args:
            graph_id: A munkafolyamat azonosítója
            router_type: A döntési router típusa ("basic" vagy "advanced")
            output_path: A kimeneti fájl útvonala (opcionális)
            
        Returns:
            A döntési adatok szótárként
        """
        # Döntések lekérése
        decisions = self.get_workflow_decisions(graph_id, router_type)
        
        if not decisions:
            logger.warning(f"Nem található döntéstörténet a következő munkafolyamathoz: {graph_id}")
            return {"error": "No decisions found"}
        
        # Adatok összeállítása
        data = {
            "graph_id": graph_id,
            "router_type": router_type,
            "total_decisions": len(decisions),
            "decisions": decisions,
            "export_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Ha fejlett router, akkor minták hozzáadása
        if router_type == "advanced":
            patterns = advanced_decision_router.detect_decision_patterns(graph_id)
            if patterns and patterns.get("status") != "no_data":
                data["patterns"] = patterns
        
        # Kiírás fájlba, ha szükséges
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Döntések exportálva: {output_path}")
        
        return data


async def main():
    """Fő függvény a parancssori interfészhez."""
    parser = argparse.ArgumentParser(description="Döntési útvonalak vizualizálása")
    
    parser.add_argument("--graph-id", type=str, help="A vizualizálandó munkafolyamat azonosítója")
    parser.add_argument("--router", type=str, choices=["basic", "advanced"], default="basic",
                       help="A használandó döntési router típusa (basic vagy advanced)")
    parser.add_argument("--output", type=str, help="A kimeneti fájl útvonala")
    parser.add_argument("--stats", action="store_true", help="Globális statisztikák megjelenítése")
    parser.add_argument("--export-json", action="store_true", help="Döntések exportálása JSON formátumban")
    parser.add_argument("--no-display", action="store_true", help="Ne jelenítse meg az ábrát")
    
    args = parser.parse_args()
    
    visualizer = DecisionVisualizer()
    
    if args.stats:
        visualizer.visualize_decision_stats(
            router_type=args.router,
            output_path=args.output,
            show_plot=not args.no_display
        )
    elif args.export_json:
        if not args.graph_id:
            logger.error("A --graph-id paraméter kötelező a JSON exportáláshoz")
            return
        
        json_output = args.output or f"decision_export_{args.graph_id}.json"
        visualizer.export_decisions_to_json(
            graph_id=args.graph_id,
            router_type=args.router,
            output_path=json_output
        )
    else:
        if not args.graph_id:
            logger.error("A --graph-id paraméter kötelező a vizualizációhoz")
            return
        
        visualizer.visualize_decision_path(
            graph_id=args.graph_id,
            router_type=args.router,
            output_path=args.output,
            show_plot=not args.no_display
        )


if __name__ == "__main__":
    asyncio.run(main())
