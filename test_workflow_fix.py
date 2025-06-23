#!/usr/bin/env python3
"""
Quick test for workflow fix
"""
import asyncio
import time
from core.enhanced_execution_coordinator import EnhancedExecutionCoordinator

async def test_workflow():
    print("🧪 Testing Multi-Step Workflow Fix")
    
    try:
        coordinator = EnhancedExecutionCoordinator()
        
        # Complex development setup scenario
        workflow_definition = {
            "name": "development_environment_setup",
            "description": "Set up a complete Python development environment",
            "steps": [
                {
                    "id": "create_directory",
                    "action": "create_project_directory",
                    "params": {"name": "test_project"}
                },
                {
                    "id": "init_git",
                    "action": "initialize_git_repository",
                    "depends_on": ["create_directory"]
                }
            ]
        }
        
        start_time = time.time()
        result = await coordinator.execute_workflow(
            workflow_id=workflow_definition["name"],
            steps=workflow_definition["steps"],
            context={"description": workflow_definition["description"]}
        )
        execution_time = time.time() - start_time
        
        success = result and result.get("status") == "success"
        completed_steps = result.get("completed_steps", []) if result else []
        
        print(f"   ✅ Success: {success}")
        print(f"   ⏱️ Time: {execution_time:.2f}s")
        print(f"   📝 Result: {str(result)[:200]}...")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_workflow())
