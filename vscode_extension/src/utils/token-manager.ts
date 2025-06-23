/**
 * Token Manager for handling authentication tokens
 */
import * as vscode from 'vscode';

/**
 * Manages authentication tokens for the Project-S API
 */
export class TokenManager {
  private static readonly TOKEN_KEY = 'project-s-auth-token';
  
  /**
   * Save authentication token to secure storage
   */
  public async saveToken(token: string): Promise<void> {
    try {
      await vscode.workspace.getConfiguration('project-s').update('authToken', token, true);
      
      // Store in secrets storage if available
      try {
        const secretStorage = vscode.workspace.getConfiguration('project-s').get<boolean>('useSecretStorage');
        if (secretStorage && vscode.workspace.isTrusted) {
          const secrets = vscode.SecretStorage;
          if (secrets) {
            await vscode.SecretStorage.store(TokenManager.TOKEN_KEY, token);
          }
        }
      } catch (error) {
        // Fallback to configuration storage in case of error
        console.log('Could not store token in secret storage, fallback to configuration');
      }
    } catch (error) {
      console.error('Error saving auth token:', error);
      throw error;
    }
  }
  
  /**
   * Get authentication token from storage
   */
  public async getToken(): Promise<string | undefined> {
    try {
      // Try to get from secret storage first
      try {
        const secrets = vscode.SecretStorage;
        if (secrets) {
          const token = await vscode.SecretStorage.get(TokenManager.TOKEN_KEY);
          if (token) {
            return token;
          }
        }
      } catch (error) {
        // Fallback to configuration storage
      }
      
      // Get from configuration
      return vscode.workspace.getConfiguration('project-s').get<string>('authToken');
    } catch (error) {
      console.error('Error getting auth token:', error);
      return undefined;
    }
  }
  
  /**
   * Delete authentication token from storage
   */
  public async deleteToken(): Promise<void> {
    try {
      // Remove from configuration
      await vscode.workspace.getConfiguration('project-s').update('authToken', '', true);
      
      // Remove from secret storage
      try {
        const secrets = vscode.SecretStorage;
        if (secrets) {
          await vscode.SecretStorage.delete(TokenManager.TOKEN_KEY);
        }
      } catch (error) {
        // Ignore error
      }
    } catch (error) {
      console.error('Error deleting auth token:', error);
      throw error;
    }
  }
}
