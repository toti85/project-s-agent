# Project-S VSCode Extension Installation and Configuration Guide

This guide provides step-by-step instructions for installing, configuring, and using the Project-S VSCode extension for code analysis, generation, and documentation.

## Installation

### Prerequisites

Before installing the extension, ensure you have:

1. Visual Studio Code version 1.60.0 or later
2. Node.js version 14.0.0 or later
3. Project-S server running and accessible

### Installation Methods

#### From VSIX File

1. Download the latest `project-s-extension.vsix` file from the releases page
2. Open Visual Studio Code
3. Navigate to the Extensions view (Ctrl+Shift+X or Cmd+Shift+X)
4. Click on the "..." menu in the top right of the Extensions view
5. Select "Install from VSIX..."
6. Navigate to and select the downloaded VSIX file
7. Restart VSCode when prompted

#### From Source Code

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/project-s-vscode-extension.git
   ```

2. Navigate to the extension directory:
   ```bash
   cd project-s-vscode-extension
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Build the extension:
   ```bash
   npm run compile
   ```

5. Package the extension:
   ```bash
   npm run package
   ```

6. Install the packaged extension:
   ```bash
   code --install-extension project-s-extension-*.vsix
   ```

## Configuration

After installation, you need to configure the extension to connect to your Project-S server:

1. Open VSCode Settings (File > Preferences > Settings or Ctrl+,)
2. Search for "Project-S"
3. Configure the following settings:
   - **Project-S: Server URL**: The URL of your Project-S server (e.g., `http://localhost:8000`)
   - **Project-S: API Key**: Your API key for authentication (if applicable)
   - **Project-S: Auto Connect**: Whether to automatically connect to the server on VSCode startup

Alternatively, you can add these settings to your `settings.json` file:

```json
{
  "project-s.serverUrl": "http://localhost:8000",
  "project-s.apiKey": "your-api-key",
  "project-s.autoConnect": true
}
```

## Usage

### Connecting to the Project-S Server

1. Open the Project-S sidebar view by clicking on the Project-S icon in the Activity Bar
2. Click the "Connect" button in the sidebar
3. If the connection is successful, the status indicator will turn green and display "Connected"

### Working with Workflows

The Project-S sidebar displays all available workflows from the server.

#### Creating a New Workflow

1. Click the "+" button in the Workflows section header
2. Follow the prompt to provide a name and select the type of workflow
3. The new workflow will appear in the workflows list

#### Executing a Workflow

1. Find the workflow you want to run in the workflows list
2. Click the play button (▶) next to the workflow
3. The workflow will execute on the current file or selection

#### Deleting a Workflow

1. Find the workflow you want to delete in the workflows list
2. Click the "✕" button next to the workflow
3. Confirm the deletion when prompted

### Using Tools

The Project-S sidebar provides quick access to common tools:

#### Code Analysis

1. Select the code you want to analyze or position your cursor in a file
2. Click the "Analyze Code" button in the sidebar
3. View the analysis results in the output panel

#### Code Generation

1. Position your cursor where you want to insert generated code
2. Click the "Generate Code" button in the sidebar
3. Follow the prompts to specify what code to generate
4. The generated code will be inserted at the cursor position

#### Code Documentation

1. Select the code you want to document or position your cursor in a file
2. Click the "Document Code" button in the sidebar
3. Documentation will be generated and inserted as comments

## Troubleshooting

### Connection Issues

If you cannot connect to the Project-S server:

1. Verify that the server URL in settings is correct
2. Check that the server is running and accessible
3. Ensure your API key is valid
4. Check for network issues or firewalls blocking the connection

### Extension Not Working

If the extension is not functioning properly:

1. Restart VSCode
2. Check the Output panel (View > Output) and select "Project-S" from the dropdown
3. Look for error messages in the logs
4. Try reinstalling the extension

## Support

For further assistance:

- Submit issues on our [GitHub repository](https://github.com/organization/project-s-vscode-extension/issues)
- Contact support at support@project-s.example.com
- Check the [documentation website](https://docs.project-s.example.com) for detailed guides
