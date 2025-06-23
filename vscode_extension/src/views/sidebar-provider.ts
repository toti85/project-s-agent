/**
 * Sidebar Provider for Project-S VSCode Extension
 * Provides the webview content for the sidebar
 */
import * as vscode from 'vscode';
import { apiClient, workflowManager } from '../extension';

/**
 * Provides the sidebar webview for Project-S
 */
export class SidebarProvider implements vscode.WebviewViewProvider {
  constructor(private readonly _extensionUri: vscode.Uri) {}
  
  /**
   * Resolves the webview view
   */
  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    token: vscode.CancellationToken
  ) {
    // Set options for the webview
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };
    
    // Set the HTML content
    webviewView.webview.html = this._getWebviewContent(webviewView.webview);
    
    // Handle messages from the webview
    this._setWebviewMessageListener(webviewView);
    
    // Refresh view when connection status changes
    apiClient.on('connect', () => {
      webviewView.webview.postMessage({ type: 'connectionStatus', connected: true });
      this._refreshWorkflows(webviewView);
    });
    
    apiClient.on('disconnect', () => {
      webviewView.webview.postMessage({ type: 'connectionStatus', connected: false });
    });
    
    // Refresh view when workflows are updated
    workflowManager.on('workflow_update', () => {
      this._refreshWorkflows(webviewView);
    });
    
    workflowManager.on('workflow_created', () => {
      this._refreshWorkflows(webviewView);
    });
  }
  
  /**
   * Get the HTML content for the webview
   */
  private _getWebviewContent(webview: vscode.Webview): string {
    // Get path to media files
    const styleResetUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'reset.css')
    );
    
    const styleVSCodeUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'vscode.css')
    );
    
    const styleMainUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'sidebar.css')
    );
    
    const scriptUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, 'media', 'sidebar.js')
    );
    
    // Use a nonce to allow only specific scripts to be run
    const nonce = getNonce();
    
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
      <link href="${styleResetUri}" rel="stylesheet">
      <link href="${styleVSCodeUri}" rel="stylesheet">
      <link href="${styleMainUri}" rel="stylesheet">
      <title>Project-S Sidebar</title>
    </head>
    <body>
      <div class="container">
        <div class="section">
          <div class="section-header">
            <h3>Connection Status</h3>
          </div>
          <div class="connection-status">
            <div id="status-indicator" class="status-indicator disconnected"></div>
            <span id="connection-text">Disconnected</span>
            <button id="connect-button" class="action-button">Connect</button>
          </div>
        </div>
        
        <div class="section">
          <div class="section-header">
            <h3>Workflows</h3>
            <button id="create-workflow-button" class="icon-button" title="Create Workflow">+</button>
          </div>
          <div id="workflow-list" class="list-container">
            <div class="loading">Loading workflows...</div>
          </div>
        </div>
        
        <div class="section">
          <div class="section-header">
            <h3>Tools</h3>
          </div>
          <div class="tools-container">
            <button class="tool-button" id="analyze-button">Analyze Code</button>
            <button class="tool-button" id="generate-button">Generate Code</button>
            <button class="tool-button" id="document-button">Document Code</button>
          </div>
        </div>
      </div>
      
      <script nonce="${nonce}" src="${scriptUri}"></script>
    </body>
    </html>`;
  }
  
  /**
   * Set up message listener for the webview
   */
  private _setWebviewMessageListener(webviewView: vscode.WebviewView) {
    webviewView.webview.onDidReceiveMessage(
      async (message) => {
        switch (message.command) {
          case 'connect':
            vscode.commands.executeCommand('project-s.connect');
            break;
            
          case 'createWorkflow':
            vscode.commands.executeCommand('project-s.createWorkflow');
            break;
            
          case 'executeWorkflow':
            if (message.workflowId) {
              try {
                const workflow = await workflowManager.getWorkflow(message.workflowId);
                
                // Execute workflow with context from active editor
                const editor = vscode.window.activeTextEditor;
                let contextData = {};
                
                if (editor) {
                  contextData = {
                    language: editor.document.languageId,
                    text: editor.document.getText(),
                    fileName: editor.document.fileName
                  };
                }
                
                await workflowManager.executeWorkflowStep(workflow.id, {
                  node_name: 'start',
                  data: contextData
                });
                
                vscode.window.showInformationMessage(`Workflow ${workflow.name} started`);
              } catch (error) {
                vscode.window.showErrorMessage(`Failed to execute workflow: ${error}`);
              }
            }
            break;
            
          case 'deleteWorkflow':
            if (message.workflowId) {
              try {
                await workflowManager.deleteWorkflow(message.workflowId);
                this._refreshWorkflows(webviewView);
                vscode.window.showInformationMessage('Workflow deleted');
              } catch (error) {
                vscode.window.showErrorMessage(`Failed to delete workflow: ${error}`);
              }
            }
            break;
            
          case 'analyze':
            vscode.commands.executeCommand('project-s.analyze');
            break;
            
          case 'generate':
            vscode.commands.executeCommand('project-s.generate');
            break;
            
          case 'document':
            vscode.commands.executeCommand('project-s.document');
            break;
            
          case 'refresh':
            this._refreshWorkflows(webviewView);
            break;
        }
      },
      undefined,
      undefined
    );
  }
  
  /**
   * Refresh the workflows list in the webview
   */
  private async _refreshWorkflows(webviewView: vscode.WebviewView) {
    try {
      if (apiClient && workflowManager) {
        const workflows = await workflowManager.listWorkflows();
        webviewView.webview.postMessage({
          type: 'workflowsUpdate',
          workflows: workflows
        });
      }
    } catch (error) {
      console.error('Error refreshing workflows:', error);
    }
  }
}

/**
 * Generate a nonce string
 */
function getNonce() {
  let text = '';
  const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
