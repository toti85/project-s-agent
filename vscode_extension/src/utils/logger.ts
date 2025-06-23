/**
 * Logger utility for the Project-S VSCode extension
 */
import * as vscode from 'vscode';

/**
 * Log levels
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * Logger class for managing extension logs
 */
export class Logger {
  constructor(private outputChannel: vscode.OutputChannel) {}
  
  /**
   * Log a debug message
   */
  public debug(message: string): void {
    this.log(LogLevel.DEBUG, message);
  }
  
  /**
   * Log an info message
   */
  public info(message: string): void {
    this.log(LogLevel.INFO, message);
  }
  
  /**
   * Log a warning message
   */
  public warn(message: string): void {
    this.log(LogLevel.WARN, message);
  }
  
  /**
   * Log an error message
   */
  public error(message: string): void {
    this.log(LogLevel.ERROR, message);
  }
  
  /**
   * Log a message with the specified level
   */
  private log(level: LogLevel, message: string): void {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level}] ${message}`;
    
    // Output to the channel
    this.outputChannel.appendLine(formattedMessage);
    
    // Also output to console for development purposes
    if (level === LogLevel.ERROR) {
      console.error(formattedMessage);
    } else if (level === LogLevel.WARN) {
      console.warn(formattedMessage);
    } else {
      console.log(formattedMessage);
    }
  }
  
  /**
   * Show the output channel
   */
  public show(): void {
    this.outputChannel.show();
  }
}
