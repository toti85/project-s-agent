/**
 * CodeLens Provider for Project-S VSCode Extension
 * Provides CodeLens for additional functionality directly in the code editor
 */
import * as vscode from 'vscode';
import { apiClient, workflowManager } from '../extension';
import { Logger } from '../utils/logger';

/**
 * Provides CodeLens items for the Project-S extension
 */
export class ProjectSCodeLensProvider implements vscode.CodeLensProvider {
  private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
  public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;
  private _logger: Logger = new Logger('CodeLensProvider');
  
  /**
   * Constructor
   */
  constructor() {
    // Refresh when connection status changes
    apiClient.on('connect', () => {
      this._onDidChangeCodeLenses.fire();
    });
    
    apiClient.on('disconnect', () => {
      this._onDidChangeCodeLenses.fire();
    });
    
    // Refresh when workflows are updated
    workflowManager.on('workflow_update', () => {
      this._onDidChangeCodeLenses.fire();
    });
  }
    /**
   * Provide CodeLens for a given document
   * @param document The document to provide CodeLens for
   * @param token A cancellation token
   * @returns An array of CodeLens
   */
  public async provideCodeLenses(document: vscode.TextDocument, token: vscode.CancellationToken): Promise<vscode.CodeLens[]> {
    // Check if CodeLens is enabled in settings
    const config = vscode.workspace.getConfiguration('project-s');
    if (!config.get<boolean>('enableCodeLens', true)) {
      return [];
    }
    
    // Only provide CodeLens if connected to the server
    if (!apiClient.isConnected()) {
      return [];
    }
    
    const codeLenses: vscode.CodeLens[] = [];
    
    try {
      // Add CodeLens to functions and classes
      const functionRegex = /(?:function|class|interface|enum)\s+([A-Za-z0-9_]+)/g;
      const text = document.getText();
      let matches;
      
      while ((matches = functionRegex.exec(text)) !== null) {
        // Get the range for the matched function/class name
        const position = document.positionAt(matches.index);
        const line = document.lineAt(position.line);
        const range = new vscode.Range(position, line.range.end);
        
        // Add CodeLens for documentation
        codeLenses.push(
          new vscode.CodeLens(range, {
            title: "📝 Document",
            command: "project-s.documentSelected",
            arguments: [document.uri, range]
          })
        );
        
        // Add CodeLens for analyzing
        codeLenses.push(
          new vscode.CodeLens(range, {
            title: "🔍 Analyze",
            command: "project-s.analyzeSelected",
            arguments: [document.uri, range]
          })
        );
        
        // Add available workflows if we have any
        try {
          const workflows = await workflowManager.listWorkflows();
          if (workflows && workflows.length > 0) {
            // Add the first workflow as a direct action
            codeLenses.push(
              new vscode.CodeLens(range, {
                title: `⚙️ Run ${workflows[0].name}`,
                command: "project-s.executeWorkflow",
                arguments: [workflows[0].id, document.uri, range]
              })
            );
            
            // Add "More workflows" if there are more than one
            if (workflows.length > 1) {
              codeLenses.push(
                new vscode.CodeLens(range, {
                  title: "⋯ More workflows",
                  command: "project-s.showWorkflowsQuickPick",
                  arguments: [document.uri, range]
                })
              );
            }
          }
        } catch (error) {
          this._logger.error(`Error fetching workflows for CodeLens: ${error}`);
        }
      }
    } catch (error) {
      this._logger.error(`Error providing CodeLenses: ${error}`);
    }
    
    return codeLenses;
  }
}

/**
 * Register the CodeLens provider
 */
export function registerCodeLensProvider(context: vscode.ExtensionContext) {
  // Create and register the CodeLens provider
  const codeLensProvider = new ProjectSCodeLensProvider();
  
  // Register for all languages
  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider(
      { scheme: 'file' },
      codeLensProvider
    )
  );
  
  // Register commands used by CodeLens
  context.subscriptions.push(
    vscode.commands.registerCommand('project-s.documentSelected', async (uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get the selected code
        const document = await vscode.workspace.openTextDocument(uri);
        const selectedText = document.getText(range);
        
        // Call the document command with the selected code
        await vscode.commands.executeCommand('project-s.document', selectedText);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to document code: ${error}`);
      }
    }),
    
    vscode.commands.registerCommand('project-s.analyzeSelected', async (uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get the selected code
        const document = await vscode.workspace.openTextDocument(uri);
        const selectedText = document.getText(range);
        
        // Call the analyze command with the selected code
        await vscode.commands.executeCommand('project-s.analyze', selectedText);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to analyze code: ${error}`);
      }
    }),
    
    vscode.commands.registerCommand('project-s.showWorkflowsQuickPick', async (uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get workflows
        const workflows = await workflowManager.listWorkflows();
        if (!workflows || workflows.length === 0) {
          vscode.window.showInformationMessage('No workflows available');
          return;
        }
        
        // Show quick pick for workflows
        const selected = await vscode.window.showQuickPick(
          workflows.map(workflow => ({
            label: workflow.name,
            description: workflow.type || 'Standard Workflow',
            detail: `ID: ${workflow.id}`,
            workflow
          })),
          { placeHolder: 'Select a workflow to run' }
        );
        
        if (selected) {
          // Execute the selected workflow
          vscode.commands.executeCommand('project-s.executeWorkflow', selected.workflow.id, uri, range);
        }
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to show workflows: ${error}`);
      }
    }),
    
    vscode.commands.registerCommand('project-s.executeWorkflow', async (workflowId: string, uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get the selected code
        const document = await vscode.workspace.openTextDocument(uri);
        const selectedText = document.getText(range);
        
        // Get workflow
        const workflow = await workflowManager.getWorkflow(workflowId);
        
        // Execute workflow with code context
        await workflowManager.executeWorkflowStep(workflow.id, {
          node_name: 'start',
          data: {
            language: document.languageId,
            text: selectedText,
            fileName: document.fileName
          }
        });
        
        vscode.window.showInformationMessage(`Workflow ${workflow.name} started`);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to execute workflow: ${error}`);
      }
    })
  );
  
  return codeLensProvider;
}
