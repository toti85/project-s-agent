/**
 * Sidebar Webview Script for Project-S VSCode Extension
 * Handles the interactivity of the sidebar webview
 */

(function () {
  // Get VS Code API
  const vscode = acquireVsCodeApi();
  
  // Elements
  const connectButton = document.getElementById('connect-button');
  const statusIndicator = document.getElementById('status-indicator');
  const connectionText = document.getElementById('connection-text');
  const createWorkflowButton = document.getElementById('create-workflow-button');
  const workflowList = document.getElementById('workflow-list');
  const analyzeButton = document.getElementById('analyze-button');
  const generateButton = document.getElementById('generate-button');
  const documentButton = document.getElementById('document-button');
  
  // Event listeners
  connectButton.addEventListener('click', () => {
    vscode.postMessage({
      command: 'connect'
    });
  });
  
  createWorkflowButton.addEventListener('click', () => {
    vscode.postMessage({
      command: 'createWorkflow'
    });
  });
  
  analyzeButton.addEventListener('click', () => {
    vscode.postMessage({
      command: 'analyze'
    });
  });
  
  generateButton.addEventListener('click', () => {
    vscode.postMessage({
      command: 'generate'
    });
  });
  
  documentButton.addEventListener('click', () => {
    vscode.postMessage({
      command: 'document'
    });
  });
  
  // Handle messages from the extension
  window.addEventListener('message', event => {
    const message = event.data;
    
    switch (message.type) {
      case 'connectionStatus':
        updateConnectionStatus(message.connected);
        break;
        
      case 'workflowsUpdate':
        renderWorkflows(message.workflows);
        break;
    }
  });
  
  /**
   * Update the connection status UI
   * @param {boolean} connected - Whether the extension is connected to the Project-S server
   */
  function updateConnectionStatus(connected) {
    if (connected) {
      statusIndicator.className = 'status-indicator connected';
      connectionText.textContent = 'Connected';
      connectButton.textContent = 'Disconnect';
    } else {
      statusIndicator.className = 'status-indicator disconnected';
      connectionText.textContent = 'Disconnected';
      connectButton.textContent = 'Connect';
    }
  }
  
  /**
   * Render the workflows list
   * @param {Array} workflows - Array of workflow objects
   */
  function renderWorkflows(workflows) {
    // Clear the workflow list
    workflowList.innerHTML = '';
    
    // If no workflows, show message
    if (!workflows || workflows.length === 0) {
      const noWorkflowsEl = document.createElement('div');
      noWorkflowsEl.className = 'loading';
      noWorkflowsEl.textContent = 'No workflows available';
      workflowList.appendChild(noWorkflowsEl);
      return;
    }
    
    // Create elements for each workflow
    workflows.forEach(workflow => {
      const workflowEl = document.createElement('div');
      workflowEl.className = 'workflow-item';
      
      // Workflow info
      const infoEl = document.createElement('div');
      infoEl.className = 'workflow-info';
      
      const nameEl = document.createElement('div');
      nameEl.className = 'workflow-name';
      nameEl.textContent = workflow.name;
      infoEl.appendChild(nameEl);
      
      const typeEl = document.createElement('div');
      typeEl.className = 'workflow-type';
      typeEl.textContent = workflow.type || 'Standard Workflow';
      infoEl.appendChild(typeEl);
      
      workflowEl.appendChild(infoEl);
      
      // Workflow actions
      const actionsEl = document.createElement('div');
      actionsEl.className = 'workflow-actions';
      
      const runButton = document.createElement('button');
      runButton.className = 'icon-button';
      runButton.title = 'Execute Workflow';
      runButton.textContent = '▶';
      runButton.addEventListener('click', () => {
        vscode.postMessage({
          command: 'executeWorkflow',
          workflowId: workflow.id
        });
      });
      actionsEl.appendChild(runButton);
      
      const deleteButton = document.createElement('button');
      deleteButton.className = 'icon-button';
      deleteButton.title = 'Delete Workflow';
      deleteButton.textContent = '✕';
      deleteButton.addEventListener('click', () => {
        vscode.postMessage({
          command: 'deleteWorkflow',
          workflowId: workflow.id
        });
      });
      actionsEl.appendChild(deleteButton);
      
      workflowEl.appendChild(actionsEl);
      
      // Add to workflow list
      workflowList.appendChild(workflowEl);
    });
  }
  
  // Request initial data
  vscode.postMessage({
    command: 'refresh'
  });
})();
