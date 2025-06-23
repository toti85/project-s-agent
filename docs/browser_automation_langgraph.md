# Browser Automation with LangGraph Integration
## Project-S Browser Automation Module Documentation

This document describes the LangGraph-compatible browser automation module for Project-S, designed to automate browser interactions through LangGraph workflows.

## Overview

The Project-S browser automation module allows for controlled browser automation through LangGraph workflows. It provides state management, error handling, and a comprehensive set of browser interaction tools that can be used in LangGraph graphs.

## Key Components

### 1. BrowserStateManager (`browser_state.py`)

Handles the state of browser automation within LangGraph workflows. Key features:

- **State Persistence**: Save and load browser states
- **Error Tracking**: Monitor and handle errors in browser automation
- **Action History**: Track performed browser actions
- **Data Extraction**: Store data extracted from web pages

Usage example:
```python
# Initialize the state manager
state_manager = BrowserStateManager()

# Create initial state for a workflow
state = state_manager.create_initial_state("workflow_123", "chrome")

# Update state with new data
state = state_manager.update_state(state, {"current_url": "https://example.com"})

# Add action to sequence
state = state_manager.add_action_to_sequence(state, "navigate", {"url": "https://example.com"})
```

### 2. BrowserAutomationTool (`browser_automation_tool.py`)

Base class for browser automation tools that provides:

- **WebDriver Management**: Initialize and control browser drivers
- **Safe Operation Execution**: Execute browser operations with retry mechanism
- **Error Handling**: Robust error handling for browser automation
- **State Updates**: Update state based on browser actions
- **Event Integration**: Emit events to Project-S event bus

### 3. Browser Commands (`browser_commands.py`)

High-level browser commands:

- **Navigation**: Load URLs, back/forward navigation
- **Interaction**: Click elements, fill forms
- **Waiting**: Wait for elements to appear/change
- **Form Handling**: Fill and submit forms

Usage example:
```python
# Initialize the browser commands
browser_cmd = BrowserCommands(state_manager)

# Navigate to URL
state = await browser_cmd.navigate_to_url(state, "https://www.example.com")

# Click on element
state = await browser_cmd.click_element(state, "#login-button", "css")

# Fill form field
state = await browser_cmd.fill_form_field(state, "#username", "user123")
```

### 4. Browser Search Tools (`browser_search_tools.py`)

Web search and information extraction tools:

- **Search Engines**: Execute searches on Google and other engines
- **Content Extraction**: Extract structured data from web pages
- **Result Processing**: Process and structure search results

Usage example:
```python
# Initialize search tools
search_tools = BrowserSearchTools(state_manager)

# Perform Google search
state = await search_tools.perform_google_search(state, "Project-S automation")

# Extract content from page
state = await search_tools.extract_page_content(state, "text")
```

### 5. Browser Workflow Examples (`browser_workflow_examples.py`)

Example LangGraph workflows:

- **Information Extraction Workflow**: Extract content from web pages
- **Search Workflow**: Search and process results
- **Form Filling Workflow**: Fill and submit forms
- **Error Handling Workflow**: Handle errors in browser automation

## Integration with LangGraph

### Creating Tool Nodes

Convert browser tools to LangGraph tool nodes:

```python
from langgraph.prebuilt import ToolNode

# Create tool node for browser navigation
navigate_node = ToolNode("navigate_to_url")
```

### Building Workflows

Create LangGraph workflows with browser automation:

```python
from langgraph.graph import StateGraph

# Create graph
graph = StateGraph()

# Add nodes
graph.add_node("initialize", initialize_node)
graph.add_node("navigate", navigate_node)
graph.add_node("extract", extract_node)

# Define edges
graph.add_edge("initialize", "navigate")
graph.add_edge("navigate", "extract")

# Set entry point
graph.set_entry_point("initialize")
```

### Running Workflows

Execute LangGraph workflows with browser automation:

```python
# Create workflow
workflow_id = "browser_task_123"
graph = create_web_information_extraction_workflow(workflow_id)

# Configure inputs
config = {
    "initialize_browser": {"state": initial_state},
    "navigate_to_url": {"url": "https://example.com"}
}

# Execute workflow
result = await graph.invoke(config)
```

## Error Handling

The browser automation module includes robust error handling:

1. **Automatic Retries**: Retry failed operations
2. **Error State Tracking**: Track error states in the browser state
3. **Error Event Emission**: Emit error events through Project-S event bus
4. **Conditional Routing**: Route workflow based on error conditions

## Event Integration

Browser automation tools emit events to Project-S event bus:

- `browser.navigation_completed`: Browser navigation completed
- `browser.element_clicked`: Element clicked in browser
- `browser.form_field_filled`: Form field filled
- `browser.search_completed`: Web search completed
- `browser.content_extracted`: Content extracted from page
- `browser.error`: Browser automation error

## Next Steps and Development

Future improvements:

1. Add more sophisticated web search algorithms
2. Improve error recovery mechanisms
3. Add support for headless browsing
4. Implement browser profile management
5. Add website login/authentication helpers

## Usage Guidelines

- Use safe browser automation practices
- Handle errors appropriately
- Test workflows thoroughly
- Be mindful of website terms of service
- Avoid overwhelming websites with too many requests
"""
