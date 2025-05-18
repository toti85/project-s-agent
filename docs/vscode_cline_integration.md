# VSCode Cline Integration for Project-S

This document describes how to use the VSCode Cline integration with Project-S to leverage the Qwen3 model through OpenRouter for code generation and other development tasks.

## Overview

The integration allows Claude and other AI assistants to collaborate with Qwen3 for development tasks:
- Claude plans and designs solutions
- Qwen3 generates and refactors code through VSCode
- Project-S orchestrates this collaboration

## Setup

1. **Install VSCode and Cline Extension**
   - Download and install Visual Studio Code
   - The integration will automatically install the Cline extension if not already present

2. **Configure OpenRouter API Key**
   - Sign up for OpenRouter at https://openrouter.ai
   - Get your API key
   - Set the environment variable: `OPENROUTER_API_KEY=your_api_key_here`

3. **Start Project-S**
   - Run the main.py script: `python main.py`
   - Confirm that the "VSCode Cline integration is active" message appears

## Usage Examples

### Generate Code with Qwen3

Using Claude or other AI interfaces, send the following command:

```
[S_COMMAND]
{
  "type": "vscode_cline",
  "operation": "generate_code",
  "prompt": "Create a Python FastAPI server with SQLite database, user management",
  "language": "python",
  "filename": "app.py"
}
[/S_COMMAND]
```

### Refactor Existing Code

```
[S_COMMAND]
{
  "type": "vscode_cline",
  "operation": "refactor_code",
  "code": "def calculate(a, b):\n    return a + b",
  "instructions": "Modify the function to support addition, subtraction, multiplication and division operations based on a mode parameter"
}
[/S_COMMAND]
```

### Execute Complex Development Workflow

```
[S_COMMAND]
{
  "type": "vscode_cline",
  "operation": "execute_workflow",
  "workflow": "create_rest_api",
  "parameters": {
    "endpoints": ["users", "products", "orders"],
    "database": "sqlite",
    "auth": true
  }
}
[/S_COMMAND]
```

## Available Workflows

1. **create_rest_api**: Create a REST API project
2. **add_feature**: Add new functionality to existing code
3. **test_and_debug**: Write tests and debug code
4. **refactor_module**: Refactor and optimize code
5. **document_code**: Generate code documentation

## Configuration

The integration can be configured in `config/vscode_cline.yaml`. Key options include:
- Model selection (default: qwen/qwen-72b)
- Command timeout
- Auto formatting and saving options
- Context window size

## Troubleshooting

If you encounter issues:

1. Check that the OPENROUTER_API_KEY environment variable is set correctly
2. Verify that VSCode is installed and in your PATH
3. Check the logs in `logs/system.log` for specific errors
4. Ensure you have a stable internet connection for API calls

## Limitations

- The integration requires VSCode to be installed
- OpenRouter API key and internet connection are required
- Some workflows may take significant time to complete
- The integration is optimized for Python but supports other languages

## Further Development

Planned enhancements for future versions:
- Support for more AI models through OpenRouter
- Additional specialized workflows
- Integration with version control systems
- Support for multi-file projects and workspaces
