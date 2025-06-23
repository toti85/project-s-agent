"""
Technology Analysis Workflow Graph Visualization
-------------------------------------------
Ez a modul a technológiai elemzési munkafolyamat grafikus megjelenítését biztosítja.
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tech_analysis_workflow import TechAnalysisWorkflow
from graphviz import Digraph

def generate_workflow_graph(output_file="tech_analysis_workflow_graph"):
    """
    Vizualizálja a technológiai elemzés munkafolyamatot Graphviz segítségével
    
    Args:
        output_file: A kimeneti fájl neve
    """
    # Workflow létrehozása
    workflow = TechAnalysisWorkflow()
    
    # GraphViz diagram létrehozása
    dot = Digraph(comment='Technológia Elemzési Munkafolyamat', format='png')
    dot.attr(rankdir='TB', size='8,8', dpi='300')
    
    # Csomópontok definiálása
    # Fő csomópontok
    dot.attr('node', shape='box', style='filled', color='lightblue')
    dot.node('initialize', 'Inicializálás')
    dot.node('search_web', 'Web Keresés')
    dot.node('analyze_info', 'Információ Elemzés')
    dot.node('create_document', 'Dokumentum Létrehozás')
    dot.node('finalize', 'Befejezés')
    
    # Hibakezelő csomópont
    dot.attr('node', shape='diamond', style='filled', color='lightcoral')
    dot.node('error_recovery', 'Hibajavítás')
    
    # Rendszerműveletek csomópontok
    dot.attr('node', shape='ellipse', style='filled', color='lightgreen')
    dot.node('system_read_file', 'Fájl Olvasás')
    dot.node('system_write_file', 'Fájl Írás')
    dot.node('system_load_config', 'Konfig Betöltés')
    dot.node('system_execute_process', 'Folyamat Indítás')
    
    # Végállapot
    dot.attr('node', shape='doublecircle', style='filled', color='lightgrey')
    dot.node('END', 'Vége')
    
    # Normál élek hozzáadása
    dot.attr('edge', color='black')
    dot.edge('initialize', 'search_web')
    dot.edge('search_web', 'analyze_info')
    dot.edge('analyze_info', 'create_document')
    dot.edge('create_document', 'finalize')
    dot.edge('finalize', 'END')
    
    # Hibakezelési élek
    dot.attr('edge', color='red', style='dashed')
    dot.edge('search_web', 'error_recovery', label='hiba')
    dot.edge('analyze_info', 'error_recovery', label='hiba')
    dot.edge('create_document', 'error_recovery', label='hiba')
    
    # Visszatérési élek
    dot.edge('error_recovery', 'search_web', label='újrapróbálkozás')
    dot.edge('error_recovery', 'analyze_info', label='újrapróbálkozás')
    dot.edge('error_recovery', 'create_document', label='újrapróbálkozás')
    dot.edge('error_recovery', 'finalize', label='max próba')
    
    # Rendszerműveletek kapcsolatai
    dot.attr('edge', color='green', style='dotted')
    dot.edge('search_web', 'system_write_file')
    dot.edge('analyze_info', 'system_read_file')
    dot.edge('create_document', 'system_write_file')
    dot.edge('initialize', 'system_load_config')
    
    # Diagram mentése
    dot.render(output_file, view=True)
    print(f"Munkafolyamat diagram létrehozva: {output_file}.png")

if __name__ == "__main__":
    generate_workflow_graph()
