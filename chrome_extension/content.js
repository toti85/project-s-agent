// Project-S Agent - Content Script
// Handles detection of commands in the chat interface and communicates with the agent

(function() {
  // Debug mode and logging utilities
  const DEBUG_MODE = true;
  function logDebug(message, data) {
    if (DEBUG_MODE) {
      if (data !== undefined) console.log(`Project-S Debug: ${message}`, data);
      else console.log(`Project-S Debug: ${message}`);
    }
  }
  function logError(message, error) {
    console.error(`Project-S Error: ${message}`, error);
  }

  // A már megjelenített válaszok nyilvántartása a duplikáció elkerüléséhez
  const processedResponses = new Set();
  
  // Tracking változók a parancsok és válaszok követéséhez
  let lastCommand = "";
  let lastCommandTime = 0;
  const commandCooldown = 3000; // 3 másodperc cooldown az ismétlődő parancsok között
  
  // DOM manipuláció a Project-S válaszokhoz
  let currentMessageElement = null;
  let pendingResponses = {};
  let processingResponse = false;
  
  logDebug('content script loaded');
  
  // Figyelő a chat változásaira
  const domObserver = new MutationObserver((mutations) => {
    checkForCommands();
  });
  
  function initObserver() {
    if (document.body) {
      domObserver.observe(document.body, { childList: true, subtree: true });
      logDebug('MutationObserver initialized');
    } else {
      logError('MutationObserver failed: document.body is null');
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initObserver);
  } else {
    initObserver();
  }

  // Configuration
  const config = {
    apiUrl: 'http://localhost:8000/api/dom',
    pollingInterval: 1000,  // 1 second
    enabled: true
  };
  
  // Load configuration from storage
  chrome.storage.sync.get(['apiUrl', 'pollingInterval', 'enabled'], (result) => {
    if (result.apiUrl) config.apiUrl = result.apiUrl;
    if (result.pollingInterval) config.pollingInterval = result.pollingInterval;
    if (result.enabled !== undefined) config.enabled = result.enabled;
    
    logDebug('config loaded', config);
    
    // Start monitoring if enabled
    if (config.enabled) {
      startMonitoring();
    }
  });
  
  // Listen for messages from the popup or background
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    logDebug('received message', message);
    
    // Beállítások frissítése
    if (message.action === 'toggle') {
      config.enabled = message.enabled;
      if (config.enabled) startMonitoring();
      else stopMonitoring();
      sendResponse({status: 'success', enabled: config.enabled});
    } 
    else if (message.action === 'updateConfig') {
      config.apiUrl = message.apiUrl || config.apiUrl;
      config.pollingInterval = message.pollingInterval || config.pollingInterval;
      config.enabled = message.enabled !== undefined ? message.enabled : config.enabled;
      logDebug('updated config via message', config);
      if (config.enabled) startMonitoring();
      else stopMonitoring();
      sendResponse({status: 'success', config});
    }
    // Válaszkezelés a background script-től
    else if (message.action === 'responseChunk') {
      const { responseId, chunk, isLast } = message;
      logDebug('Received response chunk', { responseId, chunk: chunk.substring(0, 50) + '...', isLast });
      
      if (pendingResponses[responseId]) {
        const response = pendingResponses[responseId];
        response.content += chunk;
        
        createResultBlockInDOM(response.messageElement, response.content);
        
        if (isLast) {
          delete pendingResponses[responseId];
        }
      } else if (currentMessageElement) {
        // Ha nincs pendingResponse, de van currentMessageElement
        createResultBlockInDOM(currentMessageElement, chunk);
      }
      
      sendResponse({ success: true });
      return true;
    }
    // Tömeges válaszok kezelése
    else if (message.action === 'bulkResponses') {
      logDebug('Received bulk responses', message.responses);
      
      for (const [commandId, responseData] of Object.entries(message.responses)) {
        const responseText = JSON.stringify(responseData, null, 2);
        const responseHash = hashString(responseText);
        
        // Csak az új válaszokat jelenítsük meg
        if (!processedResponses.has(responseHash)) {
          processedResponses.add(responseHash);
          
          if (currentMessageElement) {
            createResultBlockInDOM(currentMessageElement, responseText);
          } else {
            // Ha nincs konkrét üzenetelem, mutassuk lebegő ablakként
            displayResponseAsFloatingBox('[S_RESPONSE]\n' + responseText + '\n[/S_RESPONSE]');
          }
        }
      }
      
      sendResponse({ success: true });
    }
  });
  
  let pollingInterval = null;
  
  // Start monitoring the DOM for commands
  function startMonitoring() {
    if (pollingInterval) { clearInterval(pollingInterval); }
    
    // Initial scan
    checkForCommands();
    
    // Set up periodic checking
    pollingInterval = setInterval(() => {
      checkForCommands();
      checkForNewResponses();
    }, config.pollingInterval);
    
    logDebug('monitoring started with interval=' + config.pollingInterval + 'ms');
  }
  
  // Stop monitoring the DOM
  function stopMonitoring() {
    if (pollingInterval) { 
      clearInterval(pollingInterval); 
      pollingInterval = null; 
    }
    logDebug('monitoring stopped');
  }
  
  // Check for commands in the DOM
  function checkForCommands() {
    if (!config.enabled) return;
    
    logDebug('checking for commands');
    
    let commandFound = false;
    
    // Keresd meg az AI üzeneteit (Claude és ChatGPT specifikus szelektorokkal)
    const selectors = [
      'div[data-message-author-role="assistant"] div.markdown', // ChatGPT
      '.claude-message', // Claude
      '.markdown', // Általános markdown
      '.prose' // Általános tartalom
    ];
    
    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      
      for (const element of elements) {
        // Ellenőrizzük, hogy nem dolgoztuk-e már fel ezt az elemet
        if (element.hasAttribute('data-s-processed')) continue;
        
        // Keressünk S_COMMAND blokkokat
        const text = element.textContent;
        const commandMatch = text.match(/\[S_COMMAND\]([\s\S]*?)\[\/S_COMMAND\]/);
        
        if (commandMatch) {
          // Jelöljük meg az elemet mint feldolgozottat
          element.setAttribute('data-s-processed', 'true');
          currentMessageElement = element;
          
          // Parancs feldolgozása
          const commandText = commandMatch[1].trim();
          processCommand(commandText, element);
          
          commandFound = true;
        }
      }
    }
    
    return commandFound;
  }
  
  // Process a detected command
  function processCommand(commandText, messageElement) {
    if (!commandText.startsWith('{')) {
      logDebug('Skipping non-JSON S_COMMAND block', commandText);
      return false;
    }
    
    // Cooldown check
    const now = Date.now();
    const commandHash = hashString(commandText);
    
    if (commandHash === lastCommand && (now - lastCommandTime < commandCooldown)) {
      logDebug('Command recently processed, skipping', {hash: commandHash, cooldown: now - lastCommandTime});
      return false;
    }
    
    logDebug('Command found for processing', commandText);
    
    // Parse and process the command
    let commandData;
    try {
      // Safer JSON parsing
      commandData = JSON.parse(commandText);
      logDebug('Parsed command data', commandData);
    } catch (parseErr) {
      // Fallback JSON parsing - fix common issues
      try {
        const fixedJSON = commandText
          .replace(/(['"])?([a-zA-Z0-9_]+)(['"])?:/g, '"$2":') // Ensure property names are quoted
          .replace(/'/g, '"'); // Replace single quotes with double quotes
          
        commandData = JSON.parse(fixedJSON);
        logDebug('Parsed command with fallback method', commandData);
      } catch (fallbackErr) {
        logError('Failed to parse command JSON with both methods', {
          original: parseErr, 
          fallback: fallbackErr
        });
        return false;
      }
    }
    
    // Update tracking
    lastCommand = commandHash;
    lastCommandTime = now;
    
    // Send to background script for execution
    chrome.runtime.sendMessage(
      { action: "executeCommand", command: commandData },
      (response) => {
        if (response && response.responseId) {
          pendingResponses[response.responseId] = {
            messageElement: messageElement,
            content: ""
          };
          logDebug('Created pending response', { responseId: response.responseId });
        }
      }
    );
    
    return true;
  }
  
  // Eredmény blokk beszúrása a DOM-ba
  function createResultBlockInDOM(messageElement, content) {
    try {
      // Ellenőrizzük, hogy van-e már eredmény blokk
      let resultElement = messageElement.querySelector('.s-result-container');
      
      if (!resultElement) {
        // Hozzunk létre egy új eredmény blokkot
        resultElement = document.createElement('div');
        resultElement.className = 's-result-container';
        resultElement.style.margin = '10px 0';
        resultElement.style.padding = '10px';
        resultElement.style.backgroundColor = '#f0f8ff';
        resultElement.style.border = '1px solid #0078D7';
        resultElement.style.borderRadius = '5px';
        resultElement.style.fontFamily = 'monospace';
        resultElement.style.whiteSpace = 'pre-wrap';
        resultElement.style.position = 'relative';
        resultElement.style.zIndex = '1000';
        
        // A Claude és ChatGPT eltérő DOM struktúrája miatt ez szükséges
        const targetElement = messageElement.querySelector('.markdown-content') || 
                              messageElement.querySelector('.markdown') ||
                              messageElement;
        
        // Adjuk hozzá az eredeti üzenethez
        if (targetElement.nextSibling) {
          targetElement.parentNode.insertBefore(resultElement, targetElement.nextSibling);
        } else {
          targetElement.parentNode.appendChild(resultElement);
        }
        
        // Görgessünk a válaszhoz
        setTimeout(() => {
          resultElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
      
      // Frissítsük a tartalmat
      resultElement.textContent = '[S_RESPONSE]\n' + content + '\n[/S_RESPONSE]';
      
      // Vizuális visszajelzés - háttér villogtatás
      resultElement.style.transition = 'background-color 0.5s ease';
      resultElement.style.backgroundColor = '#e6f0ff';
      setTimeout(() => {
        resultElement.style.backgroundColor = '#f0f8ff';
      }, 500);
      
      return resultElement;
    } catch (e) {
      logError('Error creating result block in DOM', e);
      // Fallback: lebegő doboz
      displayResponseAsFloatingBox('[S_RESPONSE]\n' + content + '\n[/S_RESPONSE]');
      return null;
    }
  }
  
  // Lebegő doboz létrehozása
  function displayResponseAsFloatingBox(responseText) {
    try {
      // Create floating container
      const floatingContainer = document.createElement('div');
      floatingContainer.style.position = 'fixed';
      floatingContainer.style.bottom = '20px';
      floatingContainer.style.right = '20px';
      floatingContainer.style.width = '500px';
      floatingContainer.style.maxWidth = '80%';
      floatingContainer.style.maxHeight = '80vh';
      floatingContainer.style.overflowY = 'auto';
      floatingContainer.style.backgroundColor = '#003366';
      floatingContainer.style.color = 'white';
      floatingContainer.style.fontFamily = 'Consolas, monospace';
      floatingContainer.style.fontSize = '14px';
      floatingContainer.style.padding = '15px';
      floatingContainer.style.borderRadius = '8px';
      floatingContainer.style.boxShadow = '0 5px 15px rgba(0,0,0,0.3)';
      floatingContainer.style.zIndex = '2147483647'; // Maximum z-index
      
      // Add a header with close button
      const header = document.createElement('div');
      header.style.display = 'flex';
      header.style.justifyContent = 'space-between';
      header.style.alignItems = 'center';
      header.style.marginBottom = '10px';
      header.style.paddingBottom = '5px';
      header.style.borderBottom = '1px solid #0078D7';
      
      const title = document.createElement('div');
      title.style.fontWeight = 'bold';
      title.textContent = "Project-S Response";
      header.appendChild(title);
      
      const closeButton = document.createElement('button');
      closeButton.textContent = "×";
      closeButton.style.backgroundColor = 'transparent';
      closeButton.style.border = 'none';
      closeButton.style.color = 'white';
      closeButton.style.fontSize = '20px';
      closeButton.style.cursor = 'pointer';
      closeButton.style.width = '30px';
      closeButton.style.height = '30px';
      closeButton.style.display = 'flex';
      closeButton.style.alignItems = 'center';
      closeButton.style.justifyContent = 'center';
      closeButton.onclick = function() {
        document.body.removeChild(floatingContainer);
      };
      header.appendChild(closeButton);
      
      floatingContainer.appendChild(header);
      
      // Add content
      const content = document.createElement('pre');
      content.style.whiteSpace = 'pre-wrap';
      content.style.wordBreak = 'break-word';
      content.style.margin = '0';
      content.textContent = responseText;
      floatingContainer.appendChild(content);
      
      // Add a copy button
      const copyButton = document.createElement('button');
      copyButton.textContent = "Copy Response";
      copyButton.style.marginTop = '10px';
      copyButton.style.padding = '5px 10px';
      copyButton.style.backgroundColor = '#0078D7';
      copyButton.style.border = 'none';
      copyButton.style.borderRadius = '4px';
      copyButton.style.color = 'white';
      copyButton.style.cursor = 'pointer';
      copyButton.onclick = function() {
        navigator.clipboard.writeText(responseText).then(
          () => { copyButton.textContent = "Copied!"; },
          () => { copyButton.textContent = "Copy Failed"; }
        );
        setTimeout(() => { copyButton.textContent = "Copy Response"; }, 2000);
      };
      floatingContainer.appendChild(copyButton);
      
      // Add to body
      document.body.appendChild(floatingContainer);
      
      // Make draggable
      makeDraggable(floatingContainer, header);
      
      // Auto-close after 5 minutes
      setTimeout(() => {
        if (document.body.contains(floatingContainer)) {
          document.body.removeChild(floatingContainer);
        }
      }, 5 * 60 * 1000);
      
      return true;
    } catch (e) {
      logError('Error displaying as floating box', e);
      return false;
    }
  }
  
  // Helper function to make an element draggable
  function makeDraggable(element, handle) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    if (handle) {
      handle.style.cursor = 'move';
      handle.onmousedown = dragMouseDown;
    } else {
      element.onmousedown = dragMouseDown;
    }
    
    function dragMouseDown(e) {
      e.preventDefault();
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      document.onmousemove = elementDrag;
    }
    
    function elementDrag(e) {
      e.preventDefault();
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      
      const newTop = (element.offsetTop - pos2);
      const newLeft = (element.offsetLeft - pos1);
      
      // Ensure the element stays within viewport bounds
      const maxX = window.innerWidth - element.offsetWidth;
      const maxY = window.innerHeight - element.offsetHeight;
      
      element.style.top = `${Math.max(0, Math.min(maxY, newTop))}px`;
      element.style.left = `${Math.max(0, Math.min(maxX, newLeft))}px`;
    }
    
    function closeDragElement() {
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }
  
  // Simple hash function for strings
  function hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return hash.toString();
  }
  
  // Check for new responses from the server
  function checkForNewResponses() {
    chrome.runtime.sendMessage(
      { action: "checkResponses" },
      (response) => {
        if (response && response.checking) {
          logDebug('Checking for new responses from server');
        }
      }
    );
  }
})();