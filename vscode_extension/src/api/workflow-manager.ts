/**
 * Workflow Manager for Project-S VSCode Extension
 * Handles workflow creation, execution, and management
 */
import { ApiClient } from './api-client';
import { Logger } from '../utils/logger';
import { outputChannel } from '../extension';
import * as vscode from 'vscode';
import { EventEmitter } from 'events';

/**
 * Workflow type definitions
 */
export enum WorkflowType {
  CODE_ANALYSIS = 'code_analysis',
  CODE_GENERATION = 'code_generation',
  DOCUMENTATION = 'documentation',
  REFACTORING = 'refactoring',
  TESTING = 'testing',
  CUSTOM = 'custom'
}

/**
 * Workflow status definitions
 */
export enum WorkflowStatus {
  CREATED = 'created',
  RUNNING = 'running',
  WAITING_FOR_DECISION = 'waiting_for_decision',
  COMPLETED = 'completed',
  FAILED = 'failed',
  TERMINATED = 'terminated'
}

/**
 * Workflow interface
 */
export interface Workflow {
  id: string;
  name: string;
  type: WorkflowType;
  status: WorkflowStatus;
  created_at: string;
  updated_at: string;
  config: any;
  result?: any;
}

/**
 * WorkflowStep interface
 */
export interface WorkflowStep {
  node_name: string;
  data: any;
}

/**
 * WorkflowDecision interface
 */
export interface WorkflowDecision {
  decision_point: string;
  selected_option: string;
  context?: any;
}

/**
 * Workflow Manager class
 */
export class WorkflowManager extends EventEmitter {
  private workflows: Map<string, Workflow> = new Map();
  private logger: Logger;

  constructor(private apiClient: ApiClient) {
    super();
    this.logger = new Logger(outputChannel);
    
    // Set up event listeners
    this.apiClient.on('workflow_update', this.handleWorkflowUpdate.bind(this));
  }

  /**
   * Handle workflow update events
   */
  private handleWorkflowUpdate(message: any): void {
    const workflowId = message.workflow_id;
    
    if (workflowId && this.workflows.has(workflowId)) {
      const workflow = this.workflows.get(workflowId)!;
      
      // Update workflow status
      if (message.status) {
        workflow.status = message.status;
      }
      
      // Update result if available
      if (message.result) {
        workflow.result = message.result;
      }
      
      // Update workflow in map
      this.workflows.set(workflowId, workflow);
      
      // Emit update event
      this.emit('workflow_update', workflow);
      
      // Handle completed workflows
      if (workflow.status === WorkflowStatus.COMPLETED || 
          workflow.status === WorkflowStatus.FAILED) {
        this.emit('workflow_completed', workflow);
      }
      
      // Handle workflows waiting for decisions
      if (workflow.status === WorkflowStatus.WAITING_FOR_DECISION) {
        this.emit('workflow_decision_required', workflow);
      }
    }
  }

  /**
   * Create a new workflow
   */
  public async createWorkflow(name: string, type: WorkflowType, config: any = {}, initialContext: any = {}): Promise<Workflow> {
    try {
      const response = await this.apiClient.axiosInstance.post('/api/v1/workflow', {
        name,
        type,
        config,
        initial_context: initialContext
      });
      
      const workflow: Workflow = response.data;
      
      // Add workflow to map
      this.workflows.set(workflow.id, workflow);
      
      // Log and emit event
      this.logger.info(`Workflow created: ${workflow.id} (${workflow.name})`);
      this.emit('workflow_created', workflow);
      
      return workflow;
    } catch (error) {
      this.logger.error(`Error creating workflow: ${error}`);
      throw error;
    }
  }

  /**
   * Get a workflow by ID
   */
  public async getWorkflow(id: string): Promise<Workflow> {
    try {
      // Check if we have it cached
      if (this.workflows.has(id)) {
        const workflow = this.workflows.get(id)!;
        
        // Refresh from server to get latest status
        const response = await this.apiClient.axiosInstance.get(`/api/v1/workflow/${id}`);
        const updatedWorkflow: Workflow = response.data;
        
        // Update cache
        this.workflows.set(id, updatedWorkflow);
        
        return updatedWorkflow;
      }
      
      // Get from server
      const response = await this.apiClient.axiosInstance.get(`/api/v1/workflow/${id}`);
      const workflow: Workflow = response.data;
      
      // Add to cache
      this.workflows.set(id, workflow);
      
      return workflow;
    } catch (error) {
      this.logger.error(`Error getting workflow ${id}: ${error}`);
      throw error;
    }
  }

  /**
   * List all workflows with optional status filter
   */
  public async listWorkflows(status?: WorkflowStatus): Promise<Workflow[]> {
    try {
      let url = '/api/v1/workflow';
      
      if (status) {
        url += `?status=${status}`;
      }
      
      const response = await this.apiClient.axiosInstance.get(url);
      const workflows: Workflow[] = response.data;
      
      // Update workflow cache
      workflows.forEach(workflow => {
        this.workflows.set(workflow.id, workflow);
      });
      
      return workflows;
    } catch (error) {
      this.logger.error(`Error listing workflows: ${error}`);
      throw error;
    }
  }

  /**
   * Execute a workflow step
   */
  public async executeWorkflowStep(workflowId: string, step: WorkflowStep): Promise<any> {
    try {
      const response = await this.apiClient.axiosInstance.post(`/api/v1/workflow/${workflowId}/step`, step);
      return response.data;
    } catch (error) {
      this.logger.error(`Error executing workflow step: ${error}`);
      throw error;
    }
  }

  /**
   * Make a decision in a workflow
   */
  public async makeWorkflowDecision(workflowId: string, decision: WorkflowDecision): Promise<any> {
    try {
      const response = await this.apiClient.axiosInstance.post(`/api/v1/workflow/${workflowId}/decision`, decision);
      return response.data;
    } catch (error) {
      this.logger.error(`Error making workflow decision: ${error}`);
      throw error;
    }
  }

  /**
   * Delete a workflow
   */
  public async deleteWorkflow(id: string): Promise<boolean> {
    try {
      await this.apiClient.axiosInstance.delete(`/api/v1/workflow/${id}`);
      
      // Remove from cache
      this.workflows.delete(id);
      
      return true;
    } catch (error) {
      this.logger.error(`Error deleting workflow ${id}: ${error}`);
      throw error;
    }
  }

  /**
   * Get pending decisions for a workflow
   */
  public async getPendingDecisions(workflowId: string): Promise<any[]> {
    try {
      const response = await this.apiClient.axiosInstance.get(`/api/v1/decision/pending/${workflowId}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Error getting pending decisions for workflow ${workflowId}: ${error}`);
      throw error;
    }
  }

  /**
   * Get decision history for a workflow
   */
  public async getDecisionHistory(workflowId: string): Promise<any[]> {
    try {
      const response = await this.apiClient.axiosInstance.get(`/api/v1/decision/history/${workflowId}`);
      return response.data;
    } catch (error) {
      this.logger.error(`Error getting decision history for workflow ${workflowId}: ${error}`);
      throw error;
    }
  }
}
