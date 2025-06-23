"""
Direct Project-S Downloads Analysis Test
--------------------------------------
Közvetlenül végrehajtja a Downloads elemzési feladatot Project-S használatával.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Fix Unicode encoding issues FIRST
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import fix_unicode_encoding

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Core components imports
from integrations.model_manager import model_manager
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.advanced_langgraph_workflow import AdvancedLangGraphWorkflow
from integrations.persistent_state_manager import persistent_state_manager

async def run_downloads_analysis():
    """Run the Downloads analysis task with Project-S multi-model AI."""
    
    print("🤖 PROJECT-S MULTI-MODEL AI - DOWNLOADS ELEMZÉS")
    print("=" * 60)
    print("Qwen3 235B + GPT-4 sophisticated multi-AI system")
    print("=" * 60)
    
    try:
        # Initialize advanced workflow
        print("🔧 Multi-model AI workflow inicializálása...")
        workflow = AdvancedLangGraphWorkflow()
        logger.info("Advanced LangGraph workflow initialized")
        
        # Create new session for this task
        print("📂 Új session létrehozása...")
        session_id = await persistent_state_manager.create_session()
        logger.info(f"Created new session: {session_id}")
        
        # The Hungarian Downloads analysis task
        task = """S, elemezd a Downloads mappámat: 
1. Kategorizálj minden fájlt típus szerint 
2. Azonosítsd a duplikátumokat 
3. Javasolj szervezési struktúrát 
4. Készíts cleanup action plan-t"""
        
        print(f"\n📋 FELADAT:")
        print(f"{'-'*30}")
        print(task)
        print(f"{'-'*30}")
        
        print(f"\n🚀 Multi-model AI feldolgozás indítása...")
        print("(Qwen3 235B + GPT-4 + advanced workflow)")
        print()
        
        # Process with workflow
        result = await workflow.process_with_multi_model(
            command=task,
            session_id=session_id
        )
        
        print(f"\n{'='*60}")
        print("📊 PROJECT-S MULTI-AI EREDMÉNY:")
        print(f"{'='*60}")
        print(result)
        print(f"{'='*60}")
        
        # Save to session
        await persistent_state_manager.save_to_session(
            session_id, 
            "user", 
            task
        )
        await persistent_state_manager.save_to_session(
            session_id, 
            "assistant", 
            result
        )
        
        print(f"\n✅ Feladat sikeresen feldolgozva!")
        print(f"📁 Session ID: {session_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in downloads analysis: {e}", exc_info=True)
        print(f"\n❌ Hiba történt: {e}")
        return None

async def main():
    """Main entry point."""
    try:
        await run_downloads_analysis()
    except KeyboardInterrupt:
        print("\n\n⏹️  Leállítás...")
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"\n💥 Kritikus hiba: {e}")

if __name__ == "__main__":
    asyncio.run(main())
