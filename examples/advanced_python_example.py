"""
Advanced Project-S Python Client Example
----------------------------------------
This example demonstrates more advanced usage of the Project-S Python client,
focusing on integration with cognitive core and decision making capabilities.
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from project_s_python_client import ProjectSClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Main example class
class AdvancedProjectSExample:
    def __init__(self, base_url="http://localhost:8000"):
        self.client = ProjectSClient(base_url)
        self.active_workflows = {}  # workflow_id -> workflow_data
        self.event_loop = None
    
    async def initialize(self, username, password):
        """Initialize the client and authenticate"""
        if not self.client.authenticate(username, password):
            logger.error("Authentication failed")
            return False
        
        logger.info("Authentication successful")
        return True
    
    async def monitor_workflow(self, workflow_id, timeout=300):
        """Monitor a workflow until completion or timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = self.client.get_workflow_status(workflow_id)
                current_status = status.get('status')
                logger.info(f"Workflow {workflow_id} status: {current_status}")
                
                # Check for completion
                if current_status in ['completed', 'failed', 'terminated']:
                    return status
                
                # Check for pending decisions
                pending_decisions = self.client.get_pending_decisions(workflow_id)
                if pending_decisions:
                    logger.info(f"Found {len(pending_decisions)} pending decisions")
                    for decision in pending_decisions:
                        await self.handle_decision(workflow_id, decision)
                
                # Wait before checking again
                await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Error monitoring workflow: {e}")
                await asyncio.sleep(5)
        
        logger.warning(f"Workflow monitoring timed out after {timeout} seconds")
        return None
    
    async def handle_decision(self, workflow_id, decision_data):
        """Handle a pending decision in a workflow"""
        try:
            decision_point = decision_data.get('decision_point')
            options = decision_data.get('options', [])
            
            logger.info(f"Decision point: {decision_point}")
            logger.info(f"Available options: {options}")
            
            # This is where you would implement your decision logic
            # For this example, we'll just pick the first option
            if options:
                selected_option = options[0]
                
                # Make the decision
                result = self.client.make_workflow_decision(
                    workflow_id=workflow_id,
                    decision_point=decision_point,
                    selected_option=selected_option,
                    context={"auto_selected": True}
                )
                
                logger.info(f"Selected option: {selected_option}")
                logger.info(f"Decision result: {result}")
                return result
            
            logger.warning("No options available for decision")
            return None
        
        except Exception as e:
            logger.error(f"Error handling decision: {e}")
            return None
    
    async def create_cognitive_analysis_workflow(self, data_source, analysis_type):
        """Create a workflow for cognitive analysis"""
        try:
            workflow = self.client.create_workflow(
                name=f"Cognitive Analysis - {analysis_type}",
                workflow_type="cognitive_analysis",
                config={
                    "analysis_type": analysis_type,
                    "depth": "deep",
                    "max_iterations": 5
                },
                initial_context={
                    "data_source": data_source,
                    "timestamp": time.time()
                }
            )
            
            workflow_id = workflow.get("id")
            logger.info(f"Created cognitive analysis workflow: {workflow_id}")
            self.active_workflows[workflow_id] = workflow
            
            # Monitor the workflow
            asyncio.create_task(self.monitor_workflow(workflow_id))
            
            return workflow_id
        
        except Exception as e:
            logger.error(f"Error creating cognitive analysis workflow: {e}")
            return None
    
    async def run_decision_tree_workflow(self, initial_query, max_depth=3):
        """Run a decision tree workflow with the given initial query"""
        try:
            workflow = self.client.create_workflow(
                name=f"Decision Tree - {initial_query[:20]}...",
                workflow_type="decision_tree",
                config={
                    "max_depth": max_depth,
                    "auto_expand": True
                },
                initial_context={
                    "user_query": initial_query,
                    "timestamp": time.time()
                }
            )
            
            workflow_id = workflow.get("id")
            logger.info(f"Created decision tree workflow: {workflow_id}")
            self.active_workflows[workflow_id] = workflow
            
            # Monitor the workflow
            result = await self.monitor_workflow(workflow_id)
            
            # Get the decision history
            history = self.client.get_decision_history(workflow_id)
            logger.info(f"Decision history: {json.dumps(history, indent=2)}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in decision tree workflow: {e}")
            return None
    
    def handle_websocket_message(self, message):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get('type')
            
            if message_type == 'workflow_update':
                workflow_id = message.get('workflow_id')
                status = message.get('status')
                logger.info(f"Workflow {workflow_id} update: {status}")
                
                # Update the workflow in our cache
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id].update(message)
            
            elif message_type == 'decision_required':
                workflow_id = message.get('workflow_id')
                decision_data = message.get('decision_data')
                logger.info(f"Decision required for workflow {workflow_id}")
                
                # Create a task to handle the decision
                if self.event_loop:
                    self.event_loop.create_task(
                        self.handle_decision(workflow_id, decision_data)
                    )
            
            elif message_type == 'system_event':
                logger.info(f"System event: {message.get('event')}")
            
            else:
                logger.info(f"Received message: {message}")
        
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    def handle_websocket_error(self, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
    
    async def run_advanced_example(self):
        """Run the advanced example"""
        try:
            # Get the current event loop
            self.event_loop = asyncio.get_event_loop()
            
            # Connect to WebSocket for real-time updates
            self.client.connect_websocket(
                self.handle_websocket_message,
                self.handle_websocket_error
            )
            logger.info("WebSocket connected")
            
            # Get system status
            status = self.client.get_system_status()
            logger.info(f"System status: {status}")
            
            # Create and run a cognitive analysis workflow
            data_source = {
                "type": "text",
                "content": "The quick brown fox jumps over the lazy dog. This sentence contains all the letters in the English alphabet."
            }
            await self.create_cognitive_analysis_workflow(data_source, "sentiment_analysis")
            
            # Wait a bit to allow the first workflow to start
            await asyncio.sleep(2)
            
            # Run a decision tree workflow
            await self.run_decision_tree_workflow(
                "What is the best approach to analyze sentiment in customer reviews?"
            )
            
            # Use the cognitive core to analyze a complex query
            response = self.client.ask(
                "Analyze the pros and cons of using transformer models for sentiment analysis"
            )
            logger.info(f"Cognitive core response: {json.dumps(response, indent=2)}")
            
            # Let's execute a command to demonstrate integration
            result = self.client.execute_command("echo 'Demonstrating system integration'")
            logger.info(f"Command execution result: {result}")
            
            # Sleep to allow for some more WebSocket messages
            await asyncio.sleep(10)
            
            logger.info("Advanced example completed successfully")
        
        except Exception as e:
            logger.error(f"Error in advanced example: {e}")
        
        finally:
            # Disconnect WebSocket
            self.client.disconnect_websocket()
            logger.info("WebSocket disconnected")


# Run the example
async def main():
    example = AdvancedProjectSExample()
    initialized = await example.initialize("admin", "password123")
    
    if initialized:
        await example.run_advanced_example()
    else:
        logger.error("Failed to initialize example")


if __name__ == "__main__":
    asyncio.run(main())
