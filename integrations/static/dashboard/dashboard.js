// Dashboard JavaScript

// Charts
let systemChart = null;
let workflowChart = null;

// Update interval (milliseconds)
const UPDATE_INTERVAL = 10000;

// Initialize the dashboard
function initDashboard() {
    // Initialize charts
    initSystemChart();
    initWorkflowChart();
    
    // Load initial data
    updateDashboard();
    
    // Set up refresh interval
    setInterval(updateDashboard, UPDATE_INTERVAL);
}

// Initialize system metrics chart
function initSystemChart() {
    const ctx = document.getElementById('system-chart').getContext('2d');
    systemChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'CPU (%)',
                    data: [],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Memory (%)',
                    data: [],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Initialize workflow statistics chart
function initWorkflowChart() {
    const ctx = document.getElementById('workflow-chart').getContext('2d');
    workflowChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Failed'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#4CAF50', '#F44336']
            }]
        },
        options: {
            responsive: true
        }
    });
}

// Update the dashboard with fresh data
async function updateDashboard() {
    try {
        // Fetch system metrics
        const systemMetrics = await fetchData('/api/system');
        updateSystemMetrics(systemMetrics);
        
        // Fetch error statistics
        const errorStats = await fetchData('/api/errors');
        updateErrorStats(errorStats);
        
        // Fetch workflow statistics
        const workflowStats = await fetchData('/api/workflows');
        updateWorkflowStats(workflowStats);
        
        // Fetch alerts
        const alerts = await fetchData('/api/alerts');
        updateAlerts(alerts);
        
        // Fetch history data for charts
        const history = await fetchData('/api/history');
        updateCharts(history);
        
        // Update last refresh timestamp
        document.getElementById('last-update').textContent = new Date().toLocaleString();
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Fetch data from API endpoint
async function fetchData(endpoint) {
    const response = await fetch(endpoint);
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    return response.json();
}

// Update system metrics display
function updateSystemMetrics(data) {
    document.getElementById('cpu-usage').textContent = `${data.cpu_percent.toFixed(1)}%`;
    document.getElementById('memory-usage').textContent = `${data.memory_percent.toFixed(1)}%`;
    document.getElementById('uptime').textContent = formatDuration(data.uptime_seconds);
    document.getElementById('threads').textContent = data.threads_count;
}

// Update error statistics display
function updateErrorStats(data) {
    document.getElementById('error-count').textContent = data.total_errors;
    document.getElementById('error-rate').textContent = `${data.error_rate.toFixed(2)}/hr`;
    
    // Update error types list
    const errorTypesContainer = document.getElementById('error-types');
    errorTypesContainer.innerHTML = '';
    
    Object.entries(data.top_error_types || {}).forEach(([type, count]) => {
        const div = document.createElement('div');
        div.className = 'd-flex justify-content-between mb-1';
        div.innerHTML = `
            <span>${type}</span>
            <span class="badge bg-danger">${count}</span>
        `;
        errorTypesContainer.appendChild(div);
    });
}

// Update workflow statistics display
function updateWorkflowStats(data) {
    document.getElementById('workflows-completed').textContent = data.completed;
    document.getElementById('workflows-failed').textContent = data.failed;
    document.getElementById('workflow-success-rate').textContent = `${data.success_rate.toFixed(1)}%`;
    
    // Update workflow chart
    workflowChart.data.datasets[0].data = [data.completed, data.failed];
    workflowChart.update();
}

// Update alerts display
function updateAlerts(data) {
    const alertsContainer = document.getElementById('alerts-container');
    alertsContainer.innerHTML = '';
    
    if (data.length === 0) {
        alertsContainer.innerHTML = '<p>No recent alerts</p>';
        return;
    }
    
    data.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item ${alert.level.toLowerCase()}`;
        
        const timestamp = new Date(alert.timestamp).toLocaleTimeString();
        alertDiv.innerHTML = `
            <div class="d-flex justify-content-between">
                <strong>${alert.message}</strong>
                <small>${timestamp}</small>
            </div>
            <div>${alert.source}</div>
        `;
        
        alertsContainer.appendChild(alertDiv);
    });
}

// Update charts with history data
function updateCharts(history) {
    // Update system chart
    const times = history.map(item => item.time);
    const cpuData = history.map(item => item.cpu_percent);
    const memoryData = history.map(item => item.memory_percent);
    
    systemChart.data.labels = times;
    systemChart.data.datasets[0].data = cpuData;
    systemChart.data.datasets[1].data = memoryData;
    systemChart.update();
}

// Format seconds into a human-readable duration
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${secs}s`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDashboard);
