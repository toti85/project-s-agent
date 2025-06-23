/**
 * Status Bar Manager for the Project-S VSCode extension
 */
import * as vscode from 'vscode';

/**
 * Manages the status bar item for the extension
 */
export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;
  private isConnected: boolean = false;
  private isProcessing: boolean = false;
  
  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    this.statusBarItem.command = 'project-s.connect';
    this.updateStatusBar();
    this.statusBarItem.show();
  }
  
  /**
   * Set connected state
   */
  public setConnected(connected: boolean): void {
    this.isConnected = connected;
    this.updateStatusBar();
  }
  
  /**
   * Set processing state
   */
  public setProcessing(processing: boolean): void {
    this.isProcessing = processing;
    this.updateStatusBar();
  }
  
  /**
   * Update the status bar appearance
   */
  private updateStatusBar(): void {
    if (this.isProcessing) {
      this.statusBarItem.text = `$(sync~spin) Project-S`;
      this.statusBarItem.tooltip = 'Project-S is processing a request';
    } else if (this.isConnected) {
      this.statusBarItem.text = `$(check) Project-S`;
      this.statusBarItem.tooltip = 'Project-S is connected';
    } else {
      this.statusBarItem.text = `$(plug) Project-S`;
      this.statusBarItem.tooltip = 'Click to connect to Project-S server';
    }
  }
  
  /**
   * Dispose the status bar item
   */
  public dispose(): void {
    this.statusBarItem.dispose();
  }
}
