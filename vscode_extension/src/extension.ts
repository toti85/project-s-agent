/**
 * Extension entry point for the Project-S VSCode Integration
 */
import * as vscode from 'vscode';
import { ApiClient } from './api/api-client';
import { WorkflowManager } from './api/workflow-manager';
import { CommandRegistry } from './commands/command-registry';
import { SidebarProvider } from './views/sidebar-provider';
import { StatusBarManager } from './utils/status-bar-manager';
import { Logger } from './utils/logger';
import { registerCodeLensProvider } from './features/code-lens-provider';
import { registerCompletionProvider } from './features/completion-provider';

// Global extension state
export let apiClient: ApiClient;
export let workflowManager: WorkflowManager;
export let outputChannel: vscode.OutputChannel;
export let statusBarManager: StatusBarManager;
export let logger: Logger;

/**
 * This method is called when the extension is activated
 * Extension is activated at startup or when a relevant command is executed
 */
export async function activate(context: vscode.ExtensionContext): Promise<void> {
  // Create output channel for logging
  outputChannel = vscode.window.createOutputChannel('Project-S');
  logger = new Logger(outputChannel);
  logger.info('Project-S Extension Activated');
  
  // Initialize API client
  const serverUrl = vscode.workspace.getConfiguration('project-s').get<string>('serverUrl');
  apiClient = new ApiClient(serverUrl || 'http://localhost:8000');
  
  // Initialize workflow manager
  workflowManager = new WorkflowManager(apiClient);
  
  // Initialize status bar
  statusBarManager = new StatusBarManager();
  
  // Export modules for use by other parts of the extension
  const exports = {
    apiClient,
    workflowManager,
    logger,
    statusBarManager
  };
  
  // Register views
  const sidebarProvider = new SidebarProvider(context.extensionUri);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('project-s-workflows', sidebarProvider),
  );
  
  // Register commands
  const commandRegistry = new CommandRegistry(context, apiClient, workflowManager);
  commandRegistry.registerCommands();
    // Register advanced editor integrations
  registerCodeLensProvider(context);
  registerCompletionProvider(context);
  
  // Auto connect if configured
  const autoConnect = vscode.workspace.getConfiguration('project-s').get<boolean>('autoConnect');
  if (autoConnect) {
    try {
      await apiClient.connect();
      statusBarManager.setConnected(true);
      logger.info('Successfully connected to Project-S server');
    } catch (error) {
      statusBarManager.setConnected(false);
      logger.error(`Failed to connect to Project-S server: ${error}`);
    }
  }
    logger.info('Project-S Extension Ready');
  
  // Return the exports
  return exports;
}

/**
 * This method is called when the extension is deactivated
 */
export function deactivate(): void {
  // Close any open connections
  if (apiClient) {
    apiClient.disconnect();
  }
  
  logger?.info('Project-S Extension Deactivated');
}
