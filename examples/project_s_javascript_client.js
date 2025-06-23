/**
 * Project-S JavaScript Client
 * --------------------------
 * Example JavaScript client for interacting with the Project-S API
 * 
 * This client demonstrates:
 * 1. REST API usage (fetch API)
 * 2. Authentication with JWT tokens
 * 3. WebSocket communication
 * 4. Workflow management
 * 5. Decision routing integration
 */

class ProjectSClient {
    /**
     * Initialize the Project-S client
     * @param {string} baseUrl - The base URL of the Project-S API server
     */
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.apiUrl = `${baseUrl}/api/v1`;
        this.token = null;
        this.socket = null;
        this.connectionId = null;
        this.callbacks = {
            message: [],
            error: [],
            workflowUpdate: [],
            statusChange: []
        };
    }

    /**
     * Authenticate with the API server
     * @param {string} username - The username for authentication
     * @param {string} password - The password for authentication
     * @returns {Promise<boolean>} - True if authentication succeeded
     */
    async authenticate(username, password) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${this.baseUrl}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Authentication failed: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            this.token = data.access_token;
            return true;
        } catch (error) {
            console.error('Authentication error:', error);
            return false;
        }
    }

    /**
     * Get the authorization header for API requests
     * @returns {Object} - Headers object with Authorization header
     */
    getAuthHeaders() {
        if (!this.token) {
            throw new Error('Not authenticated. Call authenticate() first');
        }
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Get the current system status
     * @returns {Promise<Object>} - System status information
     */
    async getSystemStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/system/status`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`Failed to get system status: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting system status:', error);
            throw error;
        }
    }

    /**
     * Ask a question to the AI
     * @param {string} query - The question to ask
     * @returns {Promise<Object>} - AI response
     */
    async ask(query) {
        try {
            const commandId = this._generateId();
            const command = {
                type: 'ASK',
                id: commandId,
                query: query
            };

            const response = await fetch(`${this.apiUrl}/command/sync`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(command)
            });

            if (!response.ok) {
                throw new Error(`Failed to ask question: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error asking question:', error);
            throw error;
        }
    }

    /**
     * Execute a shell command
     * @param {string} command - The shell command to execute
     * @returns {Promise<Object>} - Command execution result
     */
    async executeCommand(command) {
        try {
            const commandId = this._generateId();
            const commandObj = {
                type: 'CMD',
                id: commandId,
                cmd: command
            };

            const response = await fetch(`${this.apiUrl}/command/sync`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(commandObj)
            });

            if (!response.ok) {
                throw new Error(`Failed to execute command: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error executing command:', error);
            throw error;
        }
    }

    /**
     * Create a new workflow
     * @param {string} name - The name of the workflow
     * @param {string} type - The type of workflow
     * @param {Object} config - Configuration options for the workflow
     * @param {Object} initialContext - Initial context data for the workflow
     * @returns {Promise<Object>} - Workflow creation result
     */
    async createWorkflow(name, type, config = {}, initialContext = {}) {
        try {
            const workflowConfig = {
                name,
                type,
                config,
                initial_context: initialContext
            };

            const response = await fetch(`${this.apiUrl}/workflow`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(workflowConfig)
            });

            if (!response.ok) {
                throw new Error(`Failed to create workflow: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating workflow:', error);
            throw error;
        }
    }

    /**
     * Get status of a workflow
     * @param {string} workflowId - The ID of the workflow
     * @returns {Promise<Object>} - Workflow status
     */
    async getWorkflowStatus(workflowId) {
        try {
            const response = await fetch(`${this.apiUrl}/workflow/${workflowId}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`Failed to get workflow status: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting workflow status:', error);
            throw error;
        }
    }

    /**
     * Execute a step in a workflow
     * @param {string} workflowId - The ID of the workflow
     * @param {string} nodeName - The name of the node to execute
     * @param {Object} data - Data for the step execution
     * @returns {Promise<Object>} - Step execution result
     */
    async executeWorkflowStep(workflowId, nodeName, data = {}) {
        try {
            const step = {
                node_name: nodeName,
                data
            };

            const response = await fetch(`${this.apiUrl}/workflow/${workflowId}/step`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(step)
            });

            if (!response.ok) {
                throw new Error(`Failed to execute workflow step: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error executing workflow step:', error);
            throw error;
        }
    }

    /**
     * Make a decision in a workflow
     * @param {string} workflowId - The ID of the workflow
     * @param {string} decisionPoint - The decision point
     * @param {string} selectedOption - The selected option
     * @param {Object} context - Additional context for the decision
     * @returns {Promise<Object>} - Decision result
     */
    async makeWorkflowDecision(workflowId, decisionPoint, selectedOption, context = {}) {
        try {
            const decision = {
                decision_point: decisionPoint,
                selected_option: selectedOption,
                context
            };

            const response = await fetch(`${this.apiUrl}/workflow/${workflowId}/decision`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(decision)
            });

            if (!response.ok) {
                throw new Error(`Failed to make workflow decision: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error making workflow decision:', error);
            throw error;
        }
    }

    /**
     * Get decision history for a workflow
     * @param {string} workflowId - The ID of the workflow
     * @returns {Promise<Object>} - Decision history
     */
    async getDecisionHistory(workflowId) {
        try {
            const response = await fetch(`${this.apiUrl}/decision/history/${workflowId}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`Failed to get decision history: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting decision history:', error);
            throw error;
        }
    }

    /**
     * Analyze decision patterns for a workflow
     * @param {string} workflowId - The ID of the workflow
     * @returns {Promise<Object>} - Decision analysis
     */
    async analyzeDecisionPatterns(workflowId) {
        try {
            const response = await fetch(`${this.apiUrl}/decision/analyze/${workflowId}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`Failed to analyze decision patterns: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error analyzing decision patterns:', error);
            throw error;
        }
    }

    /**
     * Connect to the WebSocket server for real-time updates
     * @param {Function} messageCallback - Callback for message events
     * @param {Function} errorCallback - Callback for error events
     * @returns {Promise<boolean>} - True if connection succeeded
     */
    async connectWebSocket(messageCallback, errorCallback) {
        if (!this.token) {
            throw new Error('Not authenticated. Call authenticate() first');
        }

        try {
            this.connectionId = this._generateId();
            const wsUrl = `${this.baseUrl.replace('http', 'ws')}/ws/auth/${this.connectionId}?token=${this.token}`;
            
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('WebSocket connection established');
                // Send ping to test connection
                this.socket.send(JSON.stringify({ type: 'ping' }));
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    
                    // Handle specific message types
                    if (message.type === 'workflow_update') {
                        this._notifyCallbacks('workflowUpdate', message);
                    } else if (message.type === 'system_event') {
                        this._notifyCallbacks('statusChange', message);
                    } else {
                        this._notifyCallbacks('message', message);
                    }
                    
                    if (messageCallback) {
                        messageCallback(message);
                    }
                } catch (error) {
                    console.error('Error processing WebSocket message:', error);
                    if (errorCallback) {
                        errorCallback(error);
                    }
                }
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this._notifyCallbacks('error', error);
                if (errorCallback) {
                    errorCallback(error);
                }
            };
            
            this.socket.onclose = () => {
                console.log('WebSocket connection closed');
                this.socket = null;
            };
            
            // Wait for connection to be established
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(this.socket && this.socket.readyState === WebSocket.OPEN);
                }, 1000);
            });
        } catch (error) {
            console.error('Error connecting to WebSocket:', error);
            if (errorCallback) {
                errorCallback(error);
            }
            return false;
        }
    }

    /**
     * Subscribe to workflow updates
     * @param {string} workflowId - The ID of the workflow to subscribe to
     */
    subscribeToWorkflow(workflowId) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket not connected. Call connectWebSocket() first');
        }
        
        this.socket.send(JSON.stringify({
            type: 'subscribe_workflow',
            workflow_id: workflowId
        }));
    }

    /**
     * Send a command via WebSocket
     * @param {Object} command - The command to send
     */
    sendCommand(command) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            throw new Error('WebSocket not connected. Call connectWebSocket() first');
        }
        
        this.socket.send(JSON.stringify({
            type: 'command',
            command
        }));
    }

    /**
     * Add a callback for specific event types
     * @param {string} event - Event type: 'message', 'error', 'workflowUpdate', 'statusChange'
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    /**
     * Notify callbacks about events
     * @param {string} event - Event type
     * @param {any} data - Event data
     * @private
     */
    _notifyCallbacks(event, data) {
        if (this.callbacks[event]) {
            for (const callback of this.callbacks[event]) {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            }
        }
    }

    /**
     * Generate a random ID for commands
     * @returns {string} - Random ID
     * @private
     */
    _generateId() {
        return 'cmd_' + Math.random().toString(36).substring(2, 15);
    }
}

// Example usage

// HTML to include in your application:
/*
<div id="output"></div>
<script>
  const client = new ProjectSClient('http://localhost:8000');
  
  async function testClient() {
    const output = document.getElementById('output');
    
    // Authenticate
    output.innerHTML += '<p>Authenticating...</p>';
    const authResult = await client.authenticate('admin', 'secret');
    output.innerHTML += `<p>Authentication ${authResult ? 'successful' : 'failed'}</p>`;
    
    if (authResult) {
      // Get system status
      output.innerHTML += '<p>Getting system status...</p>';
      const status = await client.getSystemStatus();
      output.innerHTML += `<p>System status: ${JSON.stringify(status)}</p>`;
      
      // Ask a question
      output.innerHTML += '<p>Asking a question...</p>';
      const askResult = await client.ask('How can I use Project-S decision routing?');
      output.innerHTML += `<p>Answer: ${askResult.response || askResult.result || JSON.stringify(askResult)}</p>`;
      
      // Create a workflow
      output.innerHTML += '<p>Creating a workflow...</p>';
      const workflow = await client.createWorkflow('Test Workflow', 'content_processing', {
        use_advanced_routing: true
      });
      output.innerHTML += `<p>Workflow created: ${JSON.stringify(workflow)}</p>`;
      
      if (workflow.workflow_id) {
        // Connect WebSocket for real-time updates
        output.innerHTML += '<p>Connecting to WebSocket...</p>';
        await client.connectWebSocket(
          (message) => {
            output.innerHTML += `<p>WebSocket message: ${JSON.stringify(message)}</p>`;
          },
          (error) => {
            output.innerHTML += `<p>WebSocket error: ${error.message}</p>`;
          }
        );
        
        // Subscribe to workflow updates
        client.subscribeToWorkflow(workflow.workflow_id);
        output.innerHTML += `<p>Subscribed to workflow: ${workflow.workflow_id}</p>`;
        
        // Add a special listener for workflow updates
        client.on('workflowUpdate', (data) => {
          output.innerHTML += `<p>Workflow update: ${JSON.stringify(data)}</p>`;
        });
      }
    }
  }
  
  // Run the test
  testClient().catch(error => {
    document.getElementById('output').innerHTML += `<p>Error: ${error.message}</p>`;
  });
</script>
*/
