// Project-S Agent - Popup Script
// Handles configuration of the agent

let port = null;

// Establish persistent connection to background script
function establishConnection() {
  try {
    port = chrome.runtime.connect({ name: "project-s-popup" });
    console.log('Project-S Agent popup: connected to background');
    port.onDisconnect.addListener((p) => {
      console.error('Project-S Agent popup: disconnected', chrome.runtime.lastError);
      setTimeout(establishConnection, 1000);
    });
    port.onMessage.addListener((msg) => {
      console.log('Project-S Agent popup received message:', msg);
      // Handle messages from background if needed
    });
  } catch (error) {
    console.error('Project-S Agent popup: failed to connect', error);
    setTimeout(establishConnection, 2000);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Load configuration from storage
  chrome.storage.sync.get(['apiUrl', 'pollingInterval', 'enabled'], (result) => {
    document.getElementById('apiUrl').value = result.apiUrl || 'http://localhost:8000/api/dom';
    document.getElementById('pollingInterval').value = result.pollingInterval || 1000;
    document.getElementById('enableAgent').checked = result.enabled !== undefined ? result.enabled : true;
    
    // Check connection to the agent
    checkConnection(result.apiUrl || 'http://localhost:8000/api/dom');

    // Initialize background connection
    establishConnection();
  });
  
  // Save button click handler
  document.getElementById('saveButton').addEventListener('click', () => {
    const apiUrl = document.getElementById('apiUrl').value;
    const pollingInterval = parseInt(document.getElementById('pollingInterval').value);
    const enabled = document.getElementById('enableAgent').checked;
    
    // Validate inputs
    if (!apiUrl) {
      alert('API URL is required');
      return;
    }
    
    if (isNaN(pollingInterval) || pollingInterval < 500 || pollingInterval > 5000) {
      alert('Polling interval must be between 500 and 5000 ms');
      return;
    }
    
    // Save configuration to storage
    chrome.storage.sync.set({
      apiUrl,
      pollingInterval,
      enabled
    }, () => {
      // Show success message
      const statusElement = document.getElementById('status');
      statusElement.textContent = 'Settings saved successfully';
      statusElement.className = 'status online';
      
      // Notify background to update content scripts
      if (port) {
        port.postMessage({ action: 'updateConfig', apiUrl, pollingInterval, enabled });
      }
      
      // Check connection to the agent
      checkConnection(apiUrl);
    });
  });
  
  // Enable/disable toggle handler
  document.getElementById('enableAgent').addEventListener('change', (event) => {
    const enabled = event.target.checked;
    
    // Send message to content script to toggle monitoring
    if (port) {
      port.postMessage({ action: 'toggle', enabled });
    }
    
    // Save the setting to storage
    chrome.storage.sync.set({
      enabled
    });
  });
  
  // Check connection to the agent
  function checkConnection(apiUrl) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = 'Checking connection...';
    statusElement.className = 'status';
    // Determine status endpoint (defaults to /api/status)
    const statusUrl = apiUrl.replace(/\/api\/dom(\/command)?$/, '') + '/api/status';
    fetch(statusUrl, { method: 'GET' })
      .then(response => {
        if (response.ok) {
          statusElement.textContent = 'Connected to agent';
          statusElement.className = 'status online';
        } else {
          throw new Error(`Status code: ${response.status}`);
        }
      })
      .catch((error) => {
        statusElement.textContent = 'Could not connect to agent';
        statusElement.className = 'status offline';
        console.error('Connection error:', error);
      });
  }
});