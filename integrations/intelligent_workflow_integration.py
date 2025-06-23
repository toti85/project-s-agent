"""
Intelligent Workflow Integration for Project-S Multi-Model System
---------------------------------------------------------------
Ez a modul integrálja az Intelligent Workflow System-et (intelligent_workflow_system.py)
a teljes Project-S multi-modelles rendszerbe.

A WebContentAnalyzer és más speciális workflow-k itt kerülnek regisztrálásra
és integrálásra a fő rendszerbe.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Multi-model system components (dynamic import to avoid circular imports)
from integrations.multi_model_ai_client import multi_model_ai_client
from integrations.persistent_state_manager import persistent_state_manager

# Intelligent workflow components
try:
    from intelligent_workflow_system import (
        WebContentAnalyzer, 
        SmartToolOrchestrator, 
        WorkflowDecisionEngine,
        WorkflowContextManager
    )
    INTELLIGENT_WORKFLOWS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Intelligent workflow system imported successfully")
except ImportError as e:
    INTELLIGENT_WORKFLOWS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"❌ Intelligent workflow system import failed: {e}")

class IntelligentWorkflowOrchestrator:
    """
    Orchestrates intelligent workflows within the Project-S multi-model system.
    This class bridges the gap between simple commands and sophisticated multi-step workflows.
    """
    
    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.available_workflows = {}
        self.active_workflows = {}
        
        # Register built-in workflows if available
        if INTELLIGENT_WORKFLOWS_AVAILABLE:
            self._register_builtin_workflows()
        
        logger.info(f"Intelligent Workflow Orchestrator initialized with {len(self.available_workflows)} workflows")
    
    def _register_builtin_workflows(self):
        """Register the built-in intelligent workflows."""
        
        # Web Content Analysis Workflow
        self.available_workflows["web_analysis"] = {
            "name": "Web Content Analysis",
            "description": "Comprehensive web content analysis with multi-step processing",
            "class": WebContentAnalyzer,
            "keywords": ["web", "webpage", "url", "website", "analyze", "content", "fetch"],
            "task_types": ["web_analysis", "content_analysis", "research"],
            "supported_languages": ["hu", "en"],
            "example_commands": [
                "Elemezd ezt a weboldalt: https://example.com",
                "Analyze this webpage: https://example.com",
                "Tölts le és elemezz egy weboldalt",
                "Prepare a comprehensive analysis of a website"
            ]
        }
        
        # Future workflows can be added here
        # self.available_workflows["document_analysis"] = { ... }
        # self.available_workflows["code_review"] = { ... }
        # self.available_workflows["data_pipeline"] = { ... }
        
    async def detect_workflow_intent(self, command: str) -> Optional[str]:
        """
        Detect if a command requires an intelligent workflow.
        
        Args:
            command: The user command/query
            
        Returns:
            Optional[str]: The workflow type if detected, None otherwise
        """
        command_lower = command.lower()
        
        # Check each workflow for keyword matches
        for workflow_id, workflow_info in self.available_workflows.items():
            keywords = workflow_info.get("keywords", [])
            
            # Check for keyword matches
            if any(keyword in command_lower for keyword in keywords):
                logger.info(f"🎯 Detected workflow intent: {workflow_id} for command: {command}")
                return workflow_id
        
        # Special patterns for web analysis
        if any(pattern in command_lower for pattern in ["http://", "https://", "www.", ".com", ".org", ".net"]):
            logger.info("🌐 Detected URL in command, suggesting web_analysis workflow")
            return "web_analysis"
        
        return None
    
    async def execute_workflow(self, workflow_type: str, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific intelligent workflow.
        
        Args:
            workflow_type: The type of workflow to execute
            command: The original user command
            **kwargs: Additional parameters for the workflow
            
        Returns:
            Dict[str, Any]: The workflow execution result
        """
        if workflow_type not in self.available_workflows:
            return {
                "success": False,
                "error": f"Unknown workflow type: {workflow_type}",
                "available_workflows": list(self.available_workflows.keys())
            }
        
        workflow_info = self.available_workflows[workflow_type]
        workflow_class = workflow_info["class"]
        
        try:
            # Create workflow instance
            workflow_instance = workflow_class()
            
            # Initialize the workflow
            init_success = await workflow_instance.initialize()
            if not init_success:
                return {
                    "success": False,
                    "error": f"Failed to initialize {workflow_type} workflow"
                }
            
            # Execute based on workflow type
            if workflow_type == "web_analysis":
                return await self._execute_web_analysis(workflow_instance, command, **kwargs)
            
            # Future workflow types can be handled here
            else:
                return {
                    "success": False,
                    "error": f"Execution not implemented for workflow type: {workflow_type}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error executing {workflow_type} workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_type": workflow_type
            }
    
    async def _execute_web_analysis(self, analyzer: 'WebContentAnalyzer', command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute web content analysis workflow.
        
        Args:
            analyzer: The WebContentAnalyzer instance
            command: The original command
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        # Extract URL from command
        url = self._extract_url_from_command(command)
        
        if not url:
            # If no URL in command, ask user or use provided URL
            url = kwargs.get("url")
            
        if not url:
            return {
                "success": False,
                "error": "No URL found in command. Please provide a URL to analyze.",
                "suggestion": "Example: 'Analyze this website: https://example.com'"
            }
        
        logger.info(f"🌐 Starting web analysis for URL: {url}")
        
        # Execute the analysis
        try:
            result = await analyzer.analyze_url(url)
            
            # Enhance result with multi-model AI analysis if requested
            if kwargs.get("ai_enhancement", True):
                result = await self._enhance_with_ai_analysis(result, command)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Web analysis failed: {e}")
            return {
                "success": False,
                "error": f"Web analysis failed: {str(e)}",
                "url": url
            }
    
    def _extract_url_from_command(self, command: str) -> Optional[str]:
        """Extract URL from user command."""
        import re
        
        # URL pattern matching
        url_pattern = r'https?://[^\s]+'
        matches = re.findall(url_pattern, command)
        
        if matches:
            return matches[0]
        
        # Check for www. patterns without protocol
        www_pattern = r'www\.[^\s]+'
        www_matches = re.findall(www_pattern, command)
        
        if www_matches:
            return f"https://{www_matches[0]}"
        
        return None
    
    async def _enhance_with_ai_analysis(self, workflow_result: Dict[str, Any], original_command: str) -> Dict[str, Any]:
        """
        Enhance workflow results with AI analysis using the multi-model system.
        
        Args:
            workflow_result: The original workflow result
            original_command: The original user command
            
        Returns:
            Dict[str, Any]: Enhanced result with AI insights
        """
        if not workflow_result.get("success"):
            return workflow_result
        
        try:
            # Prepare context for AI analysis
            context = {
                "workflow_type": "web_analysis",
                "original_command": original_command,
                "analysis_results": workflow_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate AI insights
            ai_prompt = f"""
Based on the web content analysis results, provide intelligent insights:

Original Command: {original_command}
URL Analyzed: {workflow_result.get('url', 'N/A')}
Content Type: {workflow_result.get('content_type', 'N/A')}

Analysis Results Summary:
- Files Generated: {len(workflow_result.get('output_paths', {}))} files
- Workflow Branch: {workflow_result.get('branch', 'N/A')}

Please provide:
1. Key insights from the analysis
2. Recommended next actions
3. Potential applications of this content
4. Any notable findings or patterns

Keep the response concise but informative.
"""
              # Use the multi-model AI client to generate insights
            ai_response = await multi_model_ai_client.generate_response(
                prompt=ai_prompt,
                task_type="analysis",
                temperature=0.3
            )
            
            # Handle both string and dict responses
            if isinstance(ai_response, dict):
                ai_content = ai_response.get("content", str(ai_response))
            else:
                ai_content = str(ai_response)
            
            if ai_content:
                workflow_result["ai_insights"] = ai_content
                workflow_result["enhanced_with_ai"] = True
                logger.info("✅ Workflow result enhanced with AI insights")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to enhance workflow with AI analysis: {e}")
            workflow_result["ai_enhancement_error"] = str(e)
        
        return workflow_result
    
    def list_available_workflows(self) -> Dict[str, Any]:
        """List all available intelligent workflows."""
        return {
            "available_workflows": [
                {
                    "id": wf_id,
                    "name": wf_info["name"],
                    "description": wf_info["description"],
                    "example_commands": wf_info.get("example_commands", [])
                }
                for wf_id, wf_info in self.available_workflows.items()
            ],
            "total_workflows": len(self.available_workflows),
            "intelligent_workflows_available": INTELLIGENT_WORKFLOWS_AVAILABLE
        }

# Global instance
intelligent_workflow_orchestrator = IntelligentWorkflowOrchestrator()

async def process_with_intelligent_workflow(command: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for processing commands with intelligent workflows.
    
    Args:
        command: The user command
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Processing result
    """
    # Detect if command needs intelligent workflow
    workflow_type = await intelligent_workflow_orchestrator.detect_workflow_intent(command)
    
    if workflow_type:
        logger.info(f"🚀 Executing intelligent workflow: {workflow_type}")
        return await intelligent_workflow_orchestrator.execute_workflow(workflow_type, command, **kwargs)
    else:
        return {
            "success": False,
            "workflow_detected": False,
            "message": "No intelligent workflow detected for this command",
            "suggestion": "This command may be better suited for basic task execution"
        }
