"""
Interactive Project-S Session
----------------------------------------
Interaktív módban futtatja a Project-S multi-model rendszert,
ahol manuálisan megadható feladatok.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Fix Unicode encoding issues FIRST
import fix_unicode_encoding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Core components imports
from core.event_bus import event_bus
from integrations.session_manager import session_manager
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager

async def initialize_system():
    """Initialize the Project-S multi-model system."""
    try:
        # Initialize event bus
        logger.info("Initializing event bus...")
        
        # Session manager is already initialized in its constructor
        logger.info("Session manager initialized")
        
        # Model manager is already initialized in its constructor
        logger.info("Model manager initialized")
        
        # Initialize advanced workflow
        workflow = AdvancedLangGraphWorkflow()
        logger.info("Advanced LangGraph workflow initialized")
        
        print("\n" + "="*60)
        print("Project-S Multi-Model AI System - Interactive Mode")
        print("="*60)
        print("\nRendszer sikeresen inicializálva!")
        print("Available AI Models:")
        
        try:
            models = multi_model_ai_client.list_available_models()
            if isinstance(models, dict):
                for provider, provider_models in models.items():
                    print(f"\n{provider.upper()}:")
                    if isinstance(provider_models, dict):
                        for model_id, model_info in provider_models.items():
                            description = model_info.get('description', 'No description') if isinstance(model_info, dict) else str(model_info)
                            name = model_info.get('name', model_id) if isinstance(model_info, dict) else model_id
                            print(f"  - {name}")
                            print(f"    {description}")
                    else:
                        print(f"  - {provider_models}")
            else:
                print("Model list format not recognized")
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
            print("Model listing skipped due to error")
        
        return workflow
        
    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        print(f"Hiba a rendszer inicializálása során: {e}")
        return None

async def process_task_with_multi_ai(workflow, task: str):
    """Process a task using the multi-AI system."""
    try:
        print(f"\n{'='*50}")
        print("Feladat feldolgozása...")
        print(f"{'='*50}")
        
        # Create new session for this task
        session_id = await persistent_state_manager.create_session()
        logger.info(f"Created new session: {session_id}")
        
        # Process with workflow
        print("Multi-model AI workflow indítása...")
          # Use the workflow to process the command
        result = await workflow.process_with_multi_model_graph(
            command=task
        )
        
        print(f"\n{'='*50}")
        print("Eredmény:")
        print(f"{'='*50}")
        print(result)
        print(f"{'='*50}")
          # Save to session
        await persistent_state_manager.add_conversation_entry(
            session_id, 
            "user", 
            task
        )
        await persistent_state_manager.add_conversation_entry(
            session_id, 
            "assistant", 
            str(result)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        print(f"Hiba a feladat feldolgozása során: {e}")
        return None

async def main():
    """Main interactive session."""
    print("Project-S Multi-Model AI System betöltése...")
    
    # Initialize system
    workflow = await initialize_system()
    if not workflow:
        print("Nem sikerült inicializálni a rendszert!")
        return
    
    print(f"\n{'='*60}")
    print("Interaktív mód aktív!")
    print("Írd be a feladatot, vagy 'exit' a kilépéshez.")
    print(f"{'='*60}")
    
    # Check if task provided as command line argument
    if len(sys.argv) > 1:
        # Use command line argument as task
        task = " ".join(sys.argv[1:])
        print(f"\n{'-'*30}")
        print(f"Parancssori feladat: {task}")
        await process_task_with_multi_ai(workflow, task)
        return
    
    while True:
        try:
            # Get user input
            print(f"\n{'-'*30}")
            user_input = input("Project-S> ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'kilep']:
                print("Kilépés...")
                break
            
            if not user_input:
                print("Kérlek, adj meg egy feladatot!")
                continue
            
            # Process the task
            await process_task_with_multi_ai(workflow, user_input)
            
        except KeyboardInterrupt:
            print("\n\nKilépés...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"Hiba történt: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print(f"Kritikus hiba: {e}")
