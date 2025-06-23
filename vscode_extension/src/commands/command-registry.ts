/**
 * Command Registry for registering VSCode commands
 */
import * as vscode from 'vscode';
import { ApiClient } from '../api/api-client';
import { WorkflowManager, WorkflowType } from '../api/workflow-manager';
import { Logger } from '../utils/logger';
import { outputChannel, statusBarManager } from '../extension';

/**
 * Registers all commands for the extension
 */
export class CommandRegistry {
  private logger: Logger;
  
  constructor(
    private context: vscode.ExtensionContext,
    private apiClient: ApiClient,
    private workflowManager: WorkflowManager
  ) {
    this.logger = new Logger(outputChannel);
  }
    /**
   * Register all commands
   */
  public registerCommands(): void {
    this.registerConnectCommand();
    this.registerAnalyzeCommand();
    this.registerGenerateCommand();
    this.registerDocumentCommand();
    this.registerCreateWorkflowCommand();
    this.registerExecuteWorkflowCommand();
    this.registerSettingsCommand();
    this.registerShowOutputCommand();
    this.registerAnalyzeSelectedCommand();
    this.registerDocumentSelectedCommand();
    this.registerToggleCodeLensCommand();
    this.registerToggleIntelliSenseCommand();
  }
  
  /**
   * Register connect command
   */
  private registerConnectCommand(): void {
    const command = vscode.commands.registerCommand('project-s.connect', async () => {
      try {
        statusBarManager.setProcessing(true);
        const connected = await this.apiClient.connect();
        
        if (connected) {
          statusBarManager.setConnected(true);
          vscode.window.showInformationMessage('Successfully connected to Project-S server');
        } else {
          statusBarManager.setConnected(false);
          vscode.window.showErrorMessage('Failed to connect to Project-S server');
        }
      } catch (error) {
        statusBarManager.setConnected(false);
        vscode.window.showErrorMessage(`Connection error: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register analyze command
   */
  private registerAnalyzeCommand(): void {
    const command = vscode.commands.registerCommand('project-s.analyze', async () => {
      try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
          vscode.window.showWarningMessage('No active editor');
          return;
        }
        
        const document = editor.document;
        const selection = editor.selection;
        
        // Get selected text or entire document
        const text = selection.isEmpty ? 
          document.getText() : 
          document.getText(selection);
        
        if (!text) {
          vscode.window.showWarningMessage('No text to analyze');
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info('Analyzing code...');
        
        // Get language identifier
        const language = document.languageId;
        
        // Analyze the code
        const result = await this.apiClient.analyzeCode(text, language);
        
        // Show results
        const resultDocument = await vscode.workspace.openTextDocument({
          content: JSON.stringify(result, null, 2),
          language: 'json'
        });
        
        await vscode.window.showTextDocument(resultDocument);
        vscode.window.showInformationMessage('Code analysis completed');
      } catch (error) {
        this.logger.error(`Error analyzing code: ${error}`);
        vscode.window.showErrorMessage(`Error analyzing code: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register generate command
   */
  private registerGenerateCommand(): void {
    const command = vscode.commands.registerCommand('project-s.generate', async () => {
      try {
        // Prompt for the specification
        const prompt = await vscode.window.showInputBox({
          prompt: 'Enter code specification',
          placeHolder: 'E.g., Create a function to sort an array of objects by a specific property'
        });
        
        if (!prompt) {
          return;
        }
        
        // Prompt for language
        const language = await vscode.window.showQuickPick([
          'typescript',
          'javascript',
          'python',
          'java',
          'csharp',
          'go',
          'rust'
        ], {
          placeHolder: 'Select programming language'
        });
        
        if (!language) {
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info(`Generating ${language} code...`);
        
        // Generate code
        const result = await this.apiClient.generateCode(prompt, language);
        
        // Get generated code from the result
        const generatedCode = result.code || result.response || JSON.stringify(result, null, 2);
        
        // Create a new document with the generated code
        const document = await vscode.workspace.openTextDocument({
          content: generatedCode,
          language: language
        });
        
        await vscode.window.showTextDocument(document);
        vscode.window.showInformationMessage('Code generation completed');
      } catch (error) {
        this.logger.error(`Error generating code: ${error}`);
        vscode.window.showErrorMessage(`Error generating code: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register document command
   */
  private registerDocumentCommand(): void {
    const command = vscode.commands.registerCommand('project-s.document', async () => {
      try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
          vscode.window.showWarningMessage('No active editor');
          return;
        }
        
        const document = editor.document;
        const selection = editor.selection;
        
        // Get selected text or entire document
        const text = selection.isEmpty ? 
          document.getText() : 
          document.getText(selection);
        
        if (!text) {
          vscode.window.showWarningMessage('No text to document');
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info('Generating documentation...');
        
        // Get language identifier
        const language = document.languageId;
        
        // Generate documentation
        const result = await this.apiClient.documentCode(text, language);
        
        // Get documented code
        const documentedCode = result.code || result.response || JSON.stringify(result, null, 2);
        
        // Apply edits if selection is not empty, otherwise create new document
        if (!selection.isEmpty) {
          const edit = new vscode.WorkspaceEdit();
          edit.replace(document.uri, selection, documentedCode);
          await vscode.workspace.applyEdit(edit);
          vscode.window.showInformationMessage('Documentation applied');
        } else {
          // Create a new document with the documented code
          const newDocument = await vscode.workspace.openTextDocument({
            content: documentedCode,
            language: language
          });
          
          await vscode.window.showTextDocument(newDocument);
          vscode.window.showInformationMessage('Documentation generated');
        }
      } catch (error) {
        this.logger.error(`Error documenting code: ${error}`);
        vscode.window.showErrorMessage(`Error documenting code: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register create workflow command
   */
  private registerCreateWorkflowCommand(): void {
    const command = vscode.commands.registerCommand('project-s.createWorkflow', async () => {
      try {
        // Prompt for workflow name
        const name = await vscode.window.showInputBox({
          prompt: 'Enter workflow name',
          placeHolder: 'My Workflow'
        });
        
        if (!name) {
          return;
        }
        
        // Prompt for workflow type
        const typeOptions = [
          { label: 'Code Analysis', value: WorkflowType.CODE_ANALYSIS },
          { label: 'Code Generation', value: WorkflowType.CODE_GENERATION },
          { label: 'Documentation', value: WorkflowType.DOCUMENTATION },
          { label: 'Refactoring', value: WorkflowType.REFACTORING },
          { label: 'Testing', value: WorkflowType.TESTING },
          { label: 'Custom', value: WorkflowType.CUSTOM }
        ];
        
        const typeSelection = await vscode.window.showQuickPick(typeOptions, {
          placeHolder: 'Select workflow type'
        });
        
        if (!typeSelection) {
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info(`Creating workflow: ${name} (${typeSelection.value})`);
        
        // Create workflow
        const workflow = await this.workflowManager.createWorkflow(
          name,
          typeSelection.value,
          {},
          {}
        );
        
        vscode.window.showInformationMessage(`Workflow created: ${workflow.id}`);
      } catch (error) {
        this.logger.error(`Error creating workflow: ${error}`);
        vscode.window.showErrorMessage(`Error creating workflow: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register execute workflow command
   */
  private registerExecuteWorkflowCommand(): void {
    const command = vscode.commands.registerCommand('project-s.executeWorkflow', async () => {
      try {
        statusBarManager.setProcessing(true);
        
        // Get all workflows
        const workflows = await this.workflowManager.listWorkflows();
        
        if (workflows.length === 0) {
          vscode.window.showInformationMessage('No workflows available');
          return;
        }
        
        // Create workflow options
        const workflowOptions = workflows.map(workflow => ({
          label: workflow.name,
          description: workflow.type,
          detail: `ID: ${workflow.id}`,
          workflow: workflow
        }));
        
        // Prompt for workflow selection
        const selection = await vscode.window.showQuickPick(workflowOptions, {
          placeHolder: 'Select workflow to execute'
        });
        
        if (!selection) {
          return;
        }
        
        const workflow = selection.workflow;
        
        // Get current editor content for context
        const editor = vscode.window.activeTextEditor;
        let contextData = {};
        
        if (editor) {
          contextData = {
            language: editor.document.languageId,
            text: editor.document.getText(),
            fileName: editor.document.fileName
          };
        }
        
        // Execute first step of the workflow
        this.logger.info(`Executing workflow: ${workflow.id}`);
        const result = await this.workflowManager.executeWorkflowStep(workflow.id, {
          node_name: 'start',
          data: contextData
        });
        
        vscode.window.showInformationMessage(`Workflow ${workflow.id} started`);
      } catch (error) {
        this.logger.error(`Error executing workflow: ${error}`);
        vscode.window.showErrorMessage(`Error executing workflow: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register settings command
   */
  private registerSettingsCommand(): void {
    const command = vscode.commands.registerCommand('project-s.settings', async () => {
      await vscode.commands.executeCommand(
        'workbench.action.openSettings',
        'project-s'
      );
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register show output command
   */
  private registerShowOutputCommand(): void {
    const command = vscode.commands.registerCommand('project-s.showOutput', () => {
      outputChannel.show();
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register analyze selected command
   */
  private registerAnalyzeSelectedCommand(): void {
    const command = vscode.commands.registerCommand('project-s.analyzeSelected', async (uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get the document and text
        const document = await vscode.workspace.openTextDocument(uri);
        const text = document.getText(range);
        
        if (!text) {
          vscode.window.showWarningMessage('No text to analyze');
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info('Analyzing selected code...');
        
        // Get language identifier
        const language = document.languageId;
        
        // Analyze the code
        const result = await this.apiClient.analyzeCode(text, language);
        
        // Show results
        const resultDocument = await vscode.workspace.openTextDocument({
          content: JSON.stringify(result, null, 2),
          language: 'json'
        });
        
        await vscode.window.showTextDocument(resultDocument);
        vscode.window.showInformationMessage('Code analysis completed');
      } catch (error) {
        this.logger.error(`Error analyzing selected code: ${error}`);
        vscode.window.showErrorMessage(`Error analyzing code: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register document selected command
   */
  private registerDocumentSelectedCommand(): void {
    const command = vscode.commands.registerCommand('project-s.documentSelected', async (uri: vscode.Uri, range: vscode.Range) => {
      try {
        // Get the document and text
        const document = await vscode.workspace.openTextDocument(uri);
        const text = document.getText(range);
        
        if (!text) {
          vscode.window.showWarningMessage('No text to document');
          return;
        }
        
        statusBarManager.setProcessing(true);
        this.logger.info('Generating documentation for selected code...');
        
        // Get language identifier
        const language = document.languageId;
        
        // Generate documentation
        const result = await this.apiClient.documentCode(text, language);
        
        // Get documented code
        const documentedCode = result.code || result.response || JSON.stringify(result, null, 2);
        
        // Apply edits
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, documentedCode);
        await vscode.workspace.applyEdit(edit);
        vscode.window.showInformationMessage('Documentation applied');
      } catch (error) {
        this.logger.error(`Error documenting selected code: ${error}`);
        vscode.window.showErrorMessage(`Error documenting code: ${error}`);
      } finally {
        statusBarManager.setProcessing(false);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register toggle CodeLens command
   */
  private registerToggleCodeLensCommand(): void {
    const command = vscode.commands.registerCommand('project-s.toggleCodeLens', async () => {
      try {
        // Get current setting
        const config = vscode.workspace.getConfiguration('project-s');
        const currentSetting = config.get<boolean>('enableCodeLens', true);
        
        // Update setting
        await config.update('enableCodeLens', !currentSetting, vscode.ConfigurationTarget.Global);
        
        vscode.window.showInformationMessage(
          `Project-S CodeLens ${!currentSetting ? 'enabled' : 'disabled'}`
        );
      } catch (error) {
        this.logger.error(`Error toggling CodeLens: ${error}`);
        vscode.window.showErrorMessage(`Error toggling CodeLens: ${error}`);
      }
    });
    
    this.context.subscriptions.push(command);
  }
  
  /**
   * Register toggle IntelliSense command
   */
  private registerToggleIntelliSenseCommand(): void {
    const command = vscode.commands.registerCommand('project-s.toggleIntelliSense', async () => {
      try {
        // Get current setting
        const config = vscode.workspace.getConfiguration('project-s');
        const currentSetting = config.get<boolean>('enableIntelliSense', true);
        
        // Update setting
        await config.update('enableIntelliSense', !currentSetting, vscode.ConfigurationTarget.Global);
        
        vscode.window.showInformationMessage(
          `Project-S IntelliSense ${!currentSetting ? 'enabled' : 'disabled'}`
        );
      } catch (error) {
        this.logger.error(`Error toggling IntelliSense: ${error}`);
        vscode.window.showErrorMessage(`Error toggling IntelliSense: ${error}`);
      }
    });
    
    this.context.subscriptions.push(command);
  }
}
