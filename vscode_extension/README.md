# Project-S VSCode Extension

A Visual Studio Code extension for integrating with the Project-S hybrid AI system.

## Features

This extension provides a seamless integration between Visual Studio Code and the Project-S system, enabling:

- **Code Analysis**: Analyze code quality, structure, and potential issues with AI assistance
- **Code Generation**: Generate high-quality code snippets and functions based on natural language descriptions
- **Documentation**: Automatically create and update documentation for your code
- **LangGraph Workflows**: Create, manage, and execute custom LangGraph workflows
- **Real-time Updates**: Get instant feedback and results through WebSocket integration

## Installation

### From Marketplace

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Project-S"
4. Click Install

### From VSIX

1. Download the latest `.vsix` file from [Releases](https://github.com/organization/project-s-vscode-extension/releases)
2. In VS Code, go to Extensions (Ctrl+Shift+X)
3. Click "..." at the top right of the Extensions panel
4. Select "Install from VSIX..."
5. Choose the downloaded file

## Getting Started

1. After installation, click on the Project-S icon in the Activity Bar
2. Configure your Project-S server URL in the settings
3. Connect to the server using the "Connect" button in the sidebar
4. Start using the available tools and workflows

## Requirements

- Visual Studio Code 1.60.0 or higher
- Node.js 14.0.0 or higher
- Project-S server running and accessible

## Extension Settings

This extension contributes the following settings:

* `project-s.serverUrl`: URL of the Project-S API server
* `project-s.authToken`: Authentication token for the Project-S API server
* `project-s.username`: Username for Project-S API authentication
* `project-s.autoConnect`: Automatically connect to Project-S API server on startup
* `project-s.showNotifications`: Show notification messages for Project-S operations

## Documentation

For detailed documentation on how to use the extension, see:

- [Installation Guide](docs/installation-guide.md)
- [Feature Guide](docs/feature-guide.md)

## Development

### Building the Extension

1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm run compile` to compile the extension
4. Press F5 in VS Code to launch the extension in debug mode

### Running Tests

```bash
npm run test
```

### Packaging the Extension

```bash
npm run package
```

## License

[MIT](LICENSE)

## Release Notes

### 0.1.0

- Initial release
- Basic integration with Project-S server
- Code analysis, generation, and documentation features
- LangGraph workflow integration
- Real-time feedback through WebSockets
