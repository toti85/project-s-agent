/**
 * API Client for communicating with the Project-S API server
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import * as WebSocket from 'ws';
import * as vscode from 'vscode';
import { Logger } from '../utils/logger';
import { outputChannel } from '../extension';
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { TokenManager } from '../utils/token-manager';

/**
 * Command types for Project-S API
 */
export enum CommandType {
  ASK = 'ASK',
  CMD = 'CMD',
  ANALYZE = 'ANALYZE',
  GENERATE = 'GENERATE',
  DOCUMENT = 'DOCUMENT'
}

/**
 * API Client for Project-S server
 */
export class ApiClient extends EventEmitter {
  private axiosInstance: AxiosInstance;
  private ws: WebSocket | null = null;
  private connectionId: string = '';
  private isConnected: boolean = false;
  private reconnectInterval: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private logger: Logger;
  private tokenManager: TokenManager;

  constructor(private baseUrl: string) {
    super();
    this.logger = new Logger(outputChannel);
    this.axiosInstance = axios.create({
      baseURL: baseUrl
    });
    this.tokenManager = new TokenManager();
  }

  /**
   * Connect to the Project-S server
   */
  public async connect(): Promise<boolean> {
    try {
      // Check if already connected
      if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.logger.info('Already connected to Project-S server');
        return true;
      }

      // Authenticate and get token if not already available
      if (!await this.ensureAuthenticated()) {
        return false;
      }

      // Connect to WebSocket
      await this.connectWebSocket();
      return true;
    } catch (error) {
      this.logger.error(`Connection error: ${error}`);
      return false;
    }
  }

  /**
   * Ensure authentication by retrieving token
   */
  private async ensureAuthenticated(): Promise<boolean> {
    const token = await this.tokenManager.getToken();
    
    if (token) {
      this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      return true;
    }
    
    // Try to authenticate with credentials
    const username = vscode.workspace.getConfiguration('project-s').get<string>('username');
    
    if (!username) {
      // Prompt for username
      const inputUsername = await vscode.window.showInputBox({
        prompt: 'Enter your Project-S username',
        placeHolder: 'Username'
      });
      
      if (!inputUsername) {
        return false;
      }
      
      // Save username to settings
      await vscode.workspace.getConfiguration('project-s').update('username', inputUsername, true);
    }
    
    // Prompt for password
    const password = await vscode.window.showInputBox({
      prompt: 'Enter your Project-S password',
      password: true
    });
    
    if (!password) {
      return false;
    }
    
    // Authenticate with the server
    try {
      const storedUsername = vscode.workspace.getConfiguration('project-s').get<string>('username');
      const response = await this.axiosInstance.post('/token', 
        new URLSearchParams({
          'username': storedUsername || '',
          'password': password
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );
      
      const newToken = response.data.access_token;
      await this.tokenManager.saveToken(newToken);
      this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      return true;
    } catch (error) {
      this.logger.error(`Authentication failed: ${error}`);
      vscode.window.showErrorMessage('Failed to authenticate with Project-S server');
      return false;
    }
  }

  /**
   * Connect to the WebSocket API
   */
  private async connectWebSocket(): Promise<void> {
    try {
      // Generate a unique connection ID
      this.connectionId = uuidv4();
      
      // Get authentication token
      const token = await this.tokenManager.getToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      
      // Close existing connection if any
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
      
      // Connect to the authenticated WebSocket endpoint
      const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws/auth/${this.connectionId}?token=${token}`;
      this.ws = new WebSocket(wsUrl);
      
      // Setup event handlers
      this.ws.onopen = this.handleWebSocketOpen.bind(this);
      this.ws.onmessage = this.handleWebSocketMessage.bind(this);
      this.ws.onerror = this.handleWebSocketError.bind(this);
      this.ws.onclose = this.handleWebSocketClose.bind(this);
      
      // Wait for connection to establish
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 10000);
        
        const checkOpen = setInterval(() => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            clearTimeout(timeout);
            clearInterval(checkOpen);
            resolve();
          }
        }, 100);
      });
    } catch (error) {
      this.logger.error(`WebSocket connection error: ${error}`);
      throw error;
    }
  }

  /**
   * Handle WebSocket open event
   */
  private handleWebSocketOpen(): void {
    this.isConnected = true;
    this.logger.info('WebSocket connected');
    
    // Start ping interval to keep connection alive
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Ping every 30 seconds
    
    // Emit connect event
    this.emit('connect');
  }

  /**
   * Handle WebSocket message event
   */
  private handleWebSocketMessage(event: WebSocket.MessageEvent): void {
    try {
      const message = JSON.parse(event.data.toString());
      this.logger.debug(`Received WebSocket message: ${JSON.stringify(message)}`);
      
      // Handle different message types
      switch (message.type) {
        case 'workflow_update':
          this.emit('workflow_update', message);
          break;
        case 'system_event':
          this.emit('system_event', message);
          break;
        case 'command_result':
          this.emit('command_result', message);
          break;
        case 'pong':
          // Pong response, do nothing
          break;
        case 'error':
          this.logger.error(`WebSocket error: ${message.error}`);
          this.emit('error', message.error);
          break;
        default:
          this.emit('message', message);
          break;
      }
    } catch (error) {
      this.logger.error(`Error processing WebSocket message: ${error}`);
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleWebSocketError(event: WebSocket.ErrorEvent): void {
    this.logger.error(`WebSocket error: ${event}`);
    this.emit('error', event);
  }

  /**
   * Handle WebSocket close event
   */
  private handleWebSocketClose(): void {
    this.isConnected = false;
    this.logger.info('WebSocket disconnected');
    
    // Clear ping interval
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    // Attempt reconnect if not intentionally disconnected
    if (!this.reconnectInterval) {
      this.reconnectInterval = setInterval(async () => {
        try {
          await this.connect();
          if (this.isConnected) {
            clearInterval(this.reconnectInterval!);
            this.reconnectInterval = null;
          }
        } catch (error) {
          this.logger.error(`Reconnection error: ${error}`);
        }
      }, 5000); // Try reconnect every 5 seconds
    }
    
    // Emit disconnect event
    this.emit('disconnect');
  }

  /**
   * Disconnect from the WebSocket API
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
      this.reconnectInterval = null;
    }
    
    this.isConnected = false;
  }

  /**
   * Execute a command on the Project-S server
   */
  public async executeCommand(type: CommandType, content: any): Promise<any> {
    try {
      // Ensure connected
      if (!this.isConnected) {
        await this.connect();
      }
      
      // Generate unique command ID
      const commandId = uuidv4();
      
      // Create command object
      const command = {
        id: commandId,
        type: type,
        ...content
      };
      
      // Send command to server
      const response = await this.axiosInstance.post('/api/v1/command/sync', command);
      return response.data;
    } catch (error) {
      this.logger.error(`Command execution error: ${error}`);
      throw error;
    }
  }

  /**
   * Ask a question to the AI
   */
  public async ask(query: string): Promise<any> {
    return this.executeCommand(CommandType.ASK, { query });
  }

  /**
   * Execute a shell command
   */
  public async executeShellCommand(cmd: string): Promise<any> {
    return this.executeCommand(CommandType.CMD, { cmd });
  }

  /**
   * Analyze code
   */
  public async analyzeCode(code: string, language: string): Promise<any> {
    return this.executeCommand(CommandType.ANALYZE, { code, language });
  }

  /**
   * Generate code
   */
  public async generateCode(prompt: string, language: string): Promise<any> {
    return this.executeCommand(CommandType.GENERATE, { prompt, language });
  }

  /**
   * Generate documentation for code
   */
  public async documentCode(code: string, language: string): Promise<any> {
    return this.executeCommand(CommandType.DOCUMENT, { code, language });
  }

  /**
   * Get system status
   */
  public async getSystemStatus(): Promise<any> {
    try {
      const response = await this.axiosInstance.get('/api/v1/system/status');
      return response.data;
    } catch (error) {
      this.logger.error(`Error getting system status: ${error}`);
      throw error;
    }
  }
}
