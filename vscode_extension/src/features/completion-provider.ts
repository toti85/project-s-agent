/**
 * Completion Item Provider for Project-S VSCode Extension
 * Provides intelligent code completion using the Project-S system
 */
import * as vscode from 'vscode';
import { apiClient } from '../extension';
import { Logger } from '../utils/logger';

/**
 * Provides IntelliSense completion items for Project-S
 */
export class ProjectSCompletionItemProvider implements vscode.CompletionItemProvider {
  private _logger: Logger = new Logger('CompletionProvider');
  private _lastRequestTime: number = 0;  private _minTimeBetweenRequests: number = 500; // ms
  
  /**
   * Constructor
   */
  constructor() {
    // Get delay from settings
    const config = vscode.workspace.getConfiguration('project-s');
    this._minTimeBetweenRequests = config.get<number>('codeCompletionDelay', 500);
    
    // Listen for configuration changes
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('project-s.codeCompletionDelay')) {
        const newConfig = vscode.workspace.getConfiguration('project-s');
        this._minTimeBetweenRequests = newConfig.get<number>('codeCompletionDelay', 500);
      }
    });
  }
  
  /**
   * Provide completion items for a given position in a document
   * @param document The document to provide completion items for
   * @param position The position in the document
   * @param token A cancellation token
   * @param context The completion context
   * @returns A list of completion items or a completion list
   */  public async provideCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    token: vscode.CancellationToken,
    context: vscode.CompletionContext
  ): Promise<vscode.CompletionItem[] | vscode.CompletionList> {
    // Check if IntelliSense is enabled in settings
    const config = vscode.workspace.getConfiguration('project-s');
    if (!config.get<boolean>('enableIntelliSense', true)) {
      return [];
    }
    
    // Only provide completions if connected to the server
    if (!apiClient.isConnected()) {
      return [];
    }
    
    // Throttle requests to avoid overwhelming the server
    const now = Date.now();
    if (now - this._lastRequestTime < this._minTimeBetweenRequests) {
      return [];
    }
    this._lastRequestTime = now;
    
    try {
      // Get the current line text and position
      const lineText = document.lineAt(position.line).text;
      const linePrefix = lineText.substring(0, position.character);
      
      // Don't provide completion if we're in a comment
      if (linePrefix.trim().startsWith('//') || linePrefix.trim().startsWith('/*')) {
        return [];
      }
      
      // Get context around the current position
      const contextRange = new vscode.Range(
        Math.max(0, position.line - 10), 0,
        Math.min(document.lineCount - 1, position.line + 10), 0
      );
      const contextText = document.getText(contextRange);
      
      // Call the API to get completion suggestions
      const response = await apiClient.sendRequest('POST', '/completions', {
        language: document.languageId,
        text: contextText,
        position: {
          line: position.line - contextRange.start.line,
          character: position.character
        },
        prefix: linePrefix
      });
        if (!response.success || !response.data || !response.data.completions) {
        return [];
      }
      
      // Get max results setting
      const maxResults = vscode.workspace.getConfiguration('project-s').get<number>('maxCompletionResults', 10);
        // Convert API responses to CompletionItems
      const completionItems: vscode.CompletionItem[] = [];
      
      // Limit to maxResults
      const limitedCompletions = response.data.completions.slice(0, maxResults);
      
      for (const completion of limitedCompletions) {
        const item = new vscode.CompletionItem(completion.label, this.mapCompletionKind(completion.kind));
        item.detail = completion.detail || 'Project-S suggestion';
        item.documentation = new vscode.MarkdownString(completion.documentation || '');
        item.insertText = completion.insertText ? new vscode.SnippetString(completion.insertText) : undefined;
        item.filterText = completion.filterText;
        item.sortText = completion.sortText || String(completion.score || '0').padStart(5, '0');
        
        completionItems.push(item);
      }
      
      return completionItems;
    } catch (error) {
      this._logger.error(`Error providing completions: ${error}`);
      return [];
    }
  }
  
  /**
   * Maps API completion kinds to VSCode CompletionItemKind
   */
  private mapCompletionKind(kind: string): vscode.CompletionItemKind {
    switch (kind?.toLowerCase()) {
      case 'method':
        return vscode.CompletionItemKind.Method;
      case 'function':
        return vscode.CompletionItemKind.Function;
      case 'constructor':
        return vscode.CompletionItemKind.Constructor;
      case 'field':
        return vscode.CompletionItemKind.Field;
      case 'variable':
        return vscode.CompletionItemKind.Variable;
      case 'class':
        return vscode.CompletionItemKind.Class;
      case 'interface':
        return vscode.CompletionItemKind.Interface;
      case 'module':
        return vscode.CompletionItemKind.Module;
      case 'property':
        return vscode.CompletionItemKind.Property;
      case 'unit':
        return vscode.CompletionItemKind.Unit;
      case 'value':
        return vscode.CompletionItemKind.Value;
      case 'enum':
        return vscode.CompletionItemKind.Enum;
      case 'keyword':
        return vscode.CompletionItemKind.Keyword;
      case 'snippet':
        return vscode.CompletionItemKind.Snippet;
      case 'text':
        return vscode.CompletionItemKind.Text;
      case 'color':
        return vscode.CompletionItemKind.Color;
      case 'file':
        return vscode.CompletionItemKind.File;
      case 'reference':
        return vscode.CompletionItemKind.Reference;
      case 'folder':
        return vscode.CompletionItemKind.Folder;
      case 'constant':
        return vscode.CompletionItemKind.Constant;
      default:
        return vscode.CompletionItemKind.Text;
    }
  }
}

/**
 * Register the completion provider
 */
export function registerCompletionProvider(context: vscode.ExtensionContext) {
  // Create and register the completion provider
  const completionProvider = new ProjectSCompletionItemProvider();
  
  // Register for common programming languages
  const supportedLanguages = [
    'javascript', 'typescript', 'python', 'java', 'csharp', 'cpp', 'go',
    'rust', 'php', 'ruby', 'html', 'css', 'json', 'yaml'
  ];
  
  context.subscriptions.push(
    vscode.languages.registerCompletionItemProvider(
      supportedLanguages.map(language => ({ scheme: 'file', language })),
      completionProvider,
      '.', '(', '{', '[', '"', "'", '`'
    )
  );
  
  return completionProvider;
}
