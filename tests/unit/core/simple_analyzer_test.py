#!/usr/bin/env python
"""
Web Content Analyzer - Simple Test
----------------------------------
Egyszerűsített teszt a Web Content Analyzer működésének ellenőrzéséhez.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Projekt gyökér hozzáadása a Python keresési útvonalhoz
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

async def main():
    try:
        # Output könyvtár létrehozása
        output_dir = os.path.join(project_root, "analysis_results", "simple_test")
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        print(f"Python version: {sys.version}")
        print(f"Current working directory: {os.getcwd()}")
        
        print("Checking module availability...")
        try:
            import langgraph
            print(f"LangGraph is available")
        except ImportError as e:
            print(f"LangGraph not available: {e}")
        
        # Import the WebContentAnalyzer
        print("Importing WebContentAnalyzer...")
        from intelligent_workflow_system import WebContentAnalyzer, SmartToolOrchestrator
        
        # First initialize tools
        print("Initializing tools...")
        tool_orchestrator = SmartToolOrchestrator()
        await tool_orchestrator.register_available_tools()
        print(f"Available tools: {list(tool_orchestrator.available_tools.keys())}")
        
        # Create an instance
        print("Creating WebContentAnalyzer instance...")
        analyzer = WebContentAnalyzer(output_dir=output_dir)
        
        # Initialize
        print("Initializing WebContentAnalyzer...")
        init_result = await analyzer.initialize()
        print(f"Initialization result: {init_result}")
        
        # Check if graph was created
        print(f"Graph object exists: {analyzer.graph is not None}")
        
        # Test URL
        url = "https://python.org"
        print(f"Analyzing URL: {url}")
        
        # Start analysis
        start_time = datetime.now()
        result = await analyzer.analyze_url(url)
        end_time = datetime.now()
        
        print(f"Analysis completed in {(end_time-start_time).total_seconds():.2f} seconds")
        print("Result:", result)
        
        # Print generated files
        print("\nGenerated files:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) / 1024  # KB
                print(f"- {file} ({file_size:.2f} KB)")
                
                # For text files, print first 100 chars of content
                if file.endswith((".txt", ".md", ".json")):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(200)
                            print(f"  Preview: {content[:100]}...")
                    except Exception as e:
                        print(f"  Could not read file: {e}")
        
        if "success" in result:
            return result["success"]
        return False
        
    except Exception as e:
        print(f"ERROR in main function: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
