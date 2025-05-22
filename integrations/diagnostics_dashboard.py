"""
Diagnostic Dashboard for Project-S + LangGraph
--------------------------------------------
This module provides a web-based diagnostic dashboard for monitoring the
Project-S + LangGraph hybrid system in real-time.
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import threading
import time

from core.diagnostics import diagnostics_manager
from integrations.langgraph_error_monitor import error_monitor

try:
    import aiohttp
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

logger = logging.getLogger(__name__)

class DiagnosticsDashboard:
    """
    Web-based dashboard for monitoring system diagnostics.
    
    Provides real-time insights into system performance, errors, 
    workflows, and other diagnostic information.
    """
    
    def __init__(self, 
                 host: str = "127.0.0.1", 
                 port: int = 7777,
                 refresh_interval: int = 10,  # seconds
                 diagnostics_dir: str = "diagnostics"):
        """
        Initialize the diagnostic dashboard
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
            refresh_interval: Data refresh interval in seconds
            diagnostics_dir: Directory to store diagnostic data
        """
        self.host = host
        self.port = port
        self.refresh_interval = refresh_interval
        self.diagnostics_dir = diagnostics_dir
        self._app = None
        self._runner = None
        self._site = None
        self._is_running = False
        self._update_thread = None
        
        # Cache for dashboard data
        self._cache = {
            "last_update": datetime.now(),
            "system_metrics": {},
            "error_stats": {},
            "workflow_stats": {},
            "alerts": [],
            "history": []  # Time-series data for charts
        }
        
        # Ensure the diagnostics directory exists
        os.makedirs(diagnostics_dir, exist_ok=True)
        
        # Check if web server dependencies are available
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available, dashboard server will not start")
    
    async def start(self):
        """Start the dashboard server"""
        if not AIOHTTP_AVAILABLE:
            logger.error("Cannot start dashboard: aiohttp not available")
            return False
        
        if self._is_running:
            logger.warning("Dashboard is already running")
            return True
        
        try:
            # Create the web application
            self._app = web.Application()
            
            # Setup routes
            self._setup_routes()
            
            # Start the server
            self._runner = web.AppRunner(self._app)
            await self._runner.setup()
            self._site = web.TCPSite(self._runner, self.host, self.port)
            await self._site.start()
            
            # Mark as running
            self._is_running = True
            
            # Start update thread
            self._start_update_thread()
            
            logger.info(f"Diagnostic Dashboard is running at http://{self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start diagnostic dashboard: {e}")
            return False
    
    async def stop(self):
        """Stop the dashboard server"""
        if not self._is_running:
            return
        
        # Stop update thread
        if self._update_thread and self._update_thread.is_alive():
            self._is_running = False
            self._update_thread.join(timeout=5)
        
        # Shutdown the server
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()
        
        self._is_running = False
        logger.info("Diagnostic Dashboard stopped")
    
    def _setup_routes(self):
        """Set up the web routes for the dashboard"""
        # Static file directory for dashboard assets
        static_dir = os.path.join(os.path.dirname(__file__), "static", "dashboard")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir, exist_ok=True)
            # Create a simple index.html if it doesn't exist
            self._create_default_dashboard_files(static_dir)
            
        # API routes
        self._app.router.add_get("/api/system", self._handle_system_metrics)
        self._app.router.add_get("/api/errors", self._handle_error_stats)
        self._app.router.add_get("/api/workflows", self._handle_workflow_stats)
        self._app.router.add_get("/api/alerts", self._handle_alerts)
        self._app.router.add_get("/api/history", self._handle_history)
        
        # Visualization routes
        self._app.router.add_get("/visualizations/{path:.*}", self._handle_visualizations)
        
        # Interface routes (static files)
        self._app.router.add_static("/", static_dir)
    
    def _create_default_dashboard_files(self, static_dir):
        """Create default dashboard HTML and JS files"""
        # Create index.html
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project-S Diagnostics Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { padding-top: 20px; background-color: #f8f9fa; }
        .dashboard-card { margin-bottom: 20px; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,.075); }
        .card-header { background-color: #f1f8ff; }
        .alert-item { border-left: 4px solid #dc3545; padding-left: 10px; margin-bottom: 10px; }
        .alert-item.warning { border-left-color: #ffc107; }
        .alert-item.info { border-left-color: #0d6efd; }
        .stats-value { font-size: 1.5rem; font-weight: bold; }
        .refresh-timestamp { font-size: 0.8rem; color: #6c757d; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <header class="pb-3 mb-4 border-bottom">
            <h1>Project-S Diagnostics Dashboard</h1>
            <p class="lead">Real-time monitoring for Project-S + LangGraph hybrid system</p>
        </header>

        <div class="row">
            <!-- System Metrics -->
            <div class="col-md-6">
                <div class="card dashboard-card">
                    <div class="card-header">
                        <h5>System Metrics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <p>CPU Usage</p>
                                <p class="stats-value" id="cpu-usage">--</p>
                            </div>
                            <div class="col-6">
                                <p>Memory Usage</p>
                                <p class="stats-value" id="memory-usage">--</p>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-6">
                                <p>Uptime</p>
                                <p class="stats-value" id="uptime">--</p>
                            </div>
                            <div class="col-6">
                                <p>Threads</p>
                                <p class="stats-value" id="threads">--</p>
                            </div>
                        </div>
                        <canvas id="system-chart" height="200"></canvas>
                    </div>
                </div>
            </div>

            <!-- Error Statistics -->
            <div class="col-md-6">
                <div class="card dashboard-card">
                    <div class="card-header">
                        <h5>Error Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-6">
                                <p>Total Errors</p>
                                <p class="stats-value" id="error-count">--</p>
                            </div>
                            <div class="col-6">
                                <p>Error Rate</p>
                                <p class="stats-value" id="error-rate">--</p>
                            </div>
                        </div>
                        <h6 class="mt-3">Top Error Types</h6>
                        <div id="error-types">
                            <!-- Will be populated by JS -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Workflow Statistics -->
            <div class="col-md-6">
                <div class="card dashboard-card">
                    <div class="card-header">
                        <h5>Workflow Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-4">
                                <p>Completed</p>
                                <p class="stats-value" id="workflows-completed">--</p>
                            </div>
                            <div class="col-4">
                                <p>Failed</p>
                                <p class="stats-value" id="workflows-failed">--</p>
                            </div>
                            <div class="col-4">
                                <p>Success Rate</p>
                                <p class="stats-value" id="workflow-success-rate">--</p>
                            </div>
                        </div>
                        <canvas id="workflow-chart" height="200"></canvas>
                    </div>
                </div>
            </div>

            <!-- Recent Alerts -->
            <div class="col-md-6">
                <div class="card dashboard-card">
                    <div class="card-header">
                        <h5>Recent Alerts</h5>
                    </div>
                    <div class="card-body">
                        <div id="alerts-container">
                            <!-- Will be populated by JS -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <p class="refresh-timestamp">Last updated: <span id="last-update">--</span></p>
    </div>

    <script src="dashboard.js"></script>
</body>
</html>
"""

        # Create dashboard.js
        dashboard_js = """// Dashboard JavaScript

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
"""

        # Write the files
        with open(os.path.join(static_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(index_html)
            
        with open(os.path.join(static_dir, "dashboard.js"), "w", encoding="utf-8") as f:
            f.write(dashboard_js)
            
        logger.info(f"Created default dashboard files in {static_dir}")
    
    def _start_update_thread(self):
        """Start a background thread to update cached data periodically"""
        def update_loop():
            while self._is_running:
                try:
                    # Update cache with fresh data
                    self._update_cache()
                    # Sleep until next update
                    time.sleep(self.refresh_interval)
                except Exception as e:
                    logger.error(f"Error in dashboard update loop: {e}")
                    time.sleep(5)  # Sleep briefly before retrying
        
        self._update_thread = threading.Thread(
            target=update_loop,
            daemon=True,
            name="dashboard-updater"
        )
        self._update_thread.start()
    
    def _update_cache(self):
        """Update the dashboard data cache"""
        # Update timestamp
        now = datetime.now()
        self._cache["last_update"] = now
        
        # System metrics
        metrics = diagnostics_manager.get_current_metrics() if hasattr(diagnostics_manager, "get_current_metrics") else {}
        self._cache["system_metrics"] = metrics
        
        # Error statistics
        error_stats = diagnostics_manager.get_error_statistics() if hasattr(diagnostics_manager, "get_error_statistics") else {}
        self._cache["error_stats"] = error_stats
        
        # Workflow statistics from performance report
        report = diagnostics_manager.generate_performance_report(output_path=None, include_graphs=False)
        self._cache["workflow_stats"] = report.get("workflows", {}) if isinstance(report, dict) else {}
        
        # Recent alerts
        alerts = diagnostics_manager.alert_history[-10:] if hasattr(diagnostics_manager, "alert_history") else []
        self._cache["alerts"] = [alert.to_dict() if hasattr(alert, "to_dict") else alert for alert in alerts]
        
        # Add current metrics to history for time-series charts
        if metrics:
            history_item = {
                "time": now.strftime("%H:%M:%S"),
                "timestamp": now.isoformat(),
                "cpu_percent": metrics.get("cpu_percent", 0),
                "memory_percent": metrics.get("memory_percent", 0)
            }
            self._cache["history"].append(history_item)
            
            # Limit history to avoid memory growth
            max_history = 60  # Keep last 60 data points
            if len(self._cache["history"]) > max_history:
                self._cache["history"] = self._cache["history"][-max_history:]
    
    # API route handlers
    async def _handle_system_metrics(self, request):
        """Handle request for system metrics"""
        metrics = self._cache["system_metrics"]
        return web.json_response(metrics)
    
    async def _handle_error_stats(self, request):
        """Handle request for error statistics"""
        stats = self._cache["error_stats"]
        
        # Add derived metrics
        if isinstance(stats, dict):
            # Calculate error rate per hour
            total_errors = stats.get("total_errors", 0)
            uptime_seconds = self._cache["system_metrics"].get("process_uptime_seconds", 3600)
            hours = max(1, uptime_seconds / 3600)
            stats["error_rate"] = total_errors / hours
        
        return web.json_response(stats)
    
    async def _handle_workflow_stats(self, request):
        """Handle request for workflow statistics"""
        return web.json_response(self._cache["workflow_stats"])
    
    async def _handle_alerts(self, request):
        """Handle request for alerts"""
        return web.json_response(self._cache["alerts"])
    
    async def _handle_history(self, request):
        """Handle request for time-series history data"""
        return web.json_response(self._cache["history"])
    
    async def _handle_visualizations(self, request):
        """Handle requests for visualization images"""
        # Extract the requested path
        rel_path = request.match_info["path"]
        full_path = os.path.join(self.diagnostics_dir, rel_path)
        
        # Verify the path exists and is safe
        if not os.path.exists(full_path) or not Path(full_path).is_relative_to(Path(self.diagnostics_dir)):
            return web.Response(status=404, text="Visualization not found")
            
        # Determine content type based on file extension
        content_type = "image/png"  # Default
        if full_path.endswith(".jpg") or full_path.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif full_path.endswith(".gif"):
            content_type = "image/gif"
        elif full_path.endswith(".svg"):
            content_type = "image/svg+xml"
            
        # Return the file
        return web.FileResponse(full_path, content_type=content_type)


# Singleton instance
dashboard = DiagnosticsDashboard()


async def start_dashboard():
    """Start the diagnostics dashboard"""
    await dashboard.start()


async def stop_dashboard():
    """Stop the diagnostics dashboard server"""
    if not dashboard._is_running:
        logger.info("Dashboard is not running")
        return True
    
    try:
        await dashboard.stop()
        logger.info("Diagnostics dashboard stopped")
        return True
    except Exception as e:
        logger.error(f"Error stopping diagnostics dashboard: {e}")
        return False
