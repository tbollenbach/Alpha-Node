"""
Real-time Dashboard for Alpha Update Agent Coordination Server
Shows live status of all connected agents, tasks, and system metrics.
"""

from flask import Flask, render_template_string, jsonify
import time
from datetime import datetime
import threading
from collections import defaultdict

# Import the coordination server components
from simple_server import agents, tasks, results, lock

app = Flask(__name__)

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha Coordinator Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p { 
            font-size: 1.2em; 
            opacity: 0.9;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .stat-card { 
            background: white; 
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { 
            font-size: 2.5em; 
            font-weight: bold; 
            margin-bottom: 10px; 
        }
        .stat-label { 
            color: #666; 
            font-size: 1.1em; 
        }
        .agents-online .stat-number { color: #27ae60; }
        .agents-total .stat-number { color: #3498db; }
        .tasks-pending .stat-number { color: #f39c12; }
        .tasks-completed .stat-number { color: #9b59b6; }
        .resource-cpu .stat-number { color: #e67e22; }
        .resource-memory .stat-number { color: #3498db; }
        .resource-storage .stat-number { color: #27ae60; }
        .resource-gpu .stat-number { color: #8e44ad; }
        
        .content-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
            margin-bottom: 30px;
        }
        .panel { 
            background: white; 
            border-radius: 15px; 
            padding: 25px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .panel h2 { 
            margin-bottom: 20px; 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .agent-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 15px; 
            margin-bottom: 10px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            border-left: 4px solid #27ae60;
        }
        .agent-item.offline { 
            border-left-color: #e74c3c; 
            opacity: 0.6; 
        }
        .agent-info { 
            flex: 1; 
        }
        .agent-id { 
            font-weight: bold; 
            color: #2c3e50; 
        }
        .agent-hostname { 
            color: #7f8c8d; 
            font-size: 0.9em; 
        }
        .agent-status { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
        }
        .status-indicator { 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            background: #27ae60; 
            animation: pulse 2s infinite;
        }
        .status-indicator.offline { 
            background: #e74c3c; 
            animation: none; 
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .last-seen { 
            font-size: 0.8em; 
            color: #95a5a6; 
        }
        
        .task-item { 
            padding: 12px; 
            margin-bottom: 8px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            border-left: 4px solid #f39c12;
        }
        .task-id { 
            font-family: monospace; 
            font-size: 0.9em; 
            color: #7f8c8d; 
        }
        .task-type { 
            font-weight: bold; 
            color: #2c3e50; 
        }
        
        .footer { 
            text-align: center; 
            color: white; 
            margin-top: 40px; 
            opacity: 0.8; 
        }
        .refresh-info { 
            font-size: 0.9em; 
            color: #95a5a6; 
            margin-top: 15px; 
        }
        
        @media (max-width: 768px) {
            .content-grid { 
                grid-template-columns: 1fr; 
            }
            .stats-grid { 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Alpha Coordinator Dashboard</h1>
            <p>Real-time monitoring of distributed agents</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card agents-online">
                <div class="stat-number" id="online-count">0</div>
                <div class="stat-label">Agents Online</div>
            </div>
            <div class="stat-card agents-total">
                <div class="stat-number" id="total-count">0</div>
                <div class="stat-label">Total Agents</div>
            </div>
            <div class="stat-card tasks-pending">
                <div class="stat-number" id="pending-count">0</div>
                <div class="stat-label">Pending Tasks</div>
            </div>
            <div class="stat-card tasks-completed">
                <div class="stat-number" id="completed-count">0</div>
                <div class="stat-label">Completed Tasks</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card resource-cpu">
                <div class="stat-number" id="total-cpu-cores">0</div>
                <div class="stat-label">Total CPU Cores</div>
            </div>
            <div class="stat-card resource-memory">
                <div class="stat-number" id="total-memory-gb">0</div>
                <div class="stat-label">Total Memory (GB)</div>
            </div>
            <div class="stat-card resource-storage">
                <div class="stat-number" id="total-storage-gb">0</div>
                <div class="stat-label">Total Storage (GB)</div>
            </div>
            <div class="stat-card resource-gpu">
                <div class="stat-number" id="total-gpu-count">0</div>
                <div class="stat-label">GPU Devices</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <h2>🤖 Connected Agents</h2>
                <div id="agents-list">
                    <div style="text-align: center; color: #7f8c8d; padding: 40px;">
                        No agents connected
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>📋 Task Queue</h2>
                <div id="tasks-list">
                    <div style="text-align: center; color: #7f8c8d; padding: 40px;">
                        No pending tasks
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <h2>💻 Hardware Resources</h2>
                <div id="resources-list">
                    <div style="text-align: center; color: #7f8c8d; padding: 40px;">
                        No resource data available
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>📊 Resource Summary</h2>
                <div id="resource-summary">
                    <div style="text-align: center; color: #7f8c8d; padding: 40px;">
                        Loading resource data...
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="refresh-info">
                Last updated: <span id="last-update">--</span> | Auto-refresh every 5 seconds
            </div>
            <p>&copy; 2025 Alpha Update Agent | Built with ❤️ for distributed systems</p>
        </div>
    </div>

    <script>
        function updateDashboard() {
            // Fetch dashboard data
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => {
                    // Update stats
                    document.getElementById('online-count').textContent = data.online_agents;
                    document.getElementById('total-count').textContent = data.total_agents;
                    document.getElementById('pending-count').textContent = data.pending_tasks;
                    document.getElementById('completed-count').textContent = data.completed_tasks;
                    
                    // Update agents list
                    const agentsList = document.getElementById('agents-list');
                    if (data.agents.length === 0) {
                        agentsList.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 40px;">No agents connected</div>';
                    } else {
                        agentsList.innerHTML = data.agents.map(agent => `
                            <div class="agent-item ${agent.online ? '' : 'offline'}">
                                <div class="agent-info">
                                    <div class="agent-id">${agent.agent_id}</div>
                                    <div class="agent-hostname">${agent.hostname || 'Unknown'}</div>
                                </div>
                                <div class="agent-status">
                                    <div class="status-indicator ${agent.online ? '' : 'offline'}"></div>
                                    <div class="last-seen">${agent.last_seen_text}</div>
                                </div>
                            </div>
                        `).join('');
                    }
                    
                    // Update tasks list
                    const tasksList = document.getElementById('tasks-list');
                    if (data.tasks.length === 0) {
                        tasksList.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 40px;">No pending tasks</div>';
                    } else {
                        tasksList.innerHTML = data.tasks.map(task => `
                            <div class="task-item">
                                <div class="task-id">${task.task_id}</div>
                                <div class="task-type">${task.type}</div>
                                <div style="font-size: 0.9em; color: #7f8c8d;">${task.description}</div>
                            </div>
                        `).join('');
                    }
                    
                    // Update last refresh time
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                });
            
            // Fetch resource data
            fetch('/api/resources/summary')
                .then(response => response.json())
                .then(resourceData => {
                    // Update resource stats
                    document.getElementById('total-cpu-cores').textContent = resourceData.total_cpu_cores;
                    document.getElementById('total-memory-gb').textContent = resourceData.total_memory_gb;
                    document.getElementById('total-storage-gb').textContent = resourceData.total_storage_gb;
                    document.getElementById('total-gpu-count').textContent = resourceData.gpu_count;
                    
                    // Update resources list
                    const resourcesList = document.getElementById('resources-list');
                    if (resourceData.agents.length === 0) {
                        resourcesList.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 40px;">No resource data available</div>';
                    } else {
                        resourcesList.innerHTML = resourceData.agents.map(agent => `
                            <div class="agent-item">
                                <div class="agent-info">
                                    <div class="agent-id">${agent.hostname} (${agent.platform})</div>
                                    <div class="agent-hostname">
                                        CPU: ${agent.cpu_cores} cores (${agent.cpu_usage}% used) | 
                                        RAM: ${agent.memory_gb}GB (${agent.memory_usage}% used) | 
                                        Storage: ${agent.storage_gb}GB
                                        ${agent.gpu_available ? ` | GPU: ${agent.gpu_count} devices` : ''}
                                    </div>
                                </div>
                                <div class="agent-status">
                                    <div class="status-indicator"></div>
                                    <div class="last-seen">${agent.uptime_hours}h uptime</div>
                                </div>
                            </div>
                        `).join('');
                    }
                    
                    // Update resource summary
                    const resourceSummary = document.getElementById('resource-summary');
                    resourceSummary.innerHTML = `
                        <div style="padding: 20px;">
                            <div style="margin-bottom: 15px;">
                                <strong>Total Pooled Resources:</strong>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
                                <div>CPU Cores: <strong>${resourceData.total_cpu_cores}</strong></div>
                                <div>Memory: <strong>${resourceData.total_memory_gb}GB</strong></div>
                                <div>Storage: <strong>${resourceData.total_storage_gb}GB</strong></div>
                                <div>GPUs: <strong>${resourceData.gpu_count}</strong></div>
                            </div>
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                                <div style="font-size: 0.8em; color: #7f8c8d;">
                                    Resources from ${resourceData.total_agents} active agents
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(error => {
                    console.error('Error fetching resource data:', error);
                });
        }
        
        // Update dashboard every 5 seconds
        updateDashboard();
        setInterval(updateDashboard, 5000);
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers for stat cards
            document.querySelectorAll('.stat-card').forEach(card => {
                card.addEventListener('click', function() {
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = 'translateY(-5px)';
                    }, 150);
                });
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint for dashboard data."""
    with lock:
        current_time = time.time()
        
        # Calculate online agents
        online_agents = []
        for agent_id, data in agents.items():
            last_seen_ago = current_time - data['last_heartbeat']
            is_online = last_seen_ago < 60  # Online if heartbeat within 60 seconds
            
            online_agents.append({
                'agent_id': agent_id,
                'hostname': data['info'].get('hostname', 'Unknown'),
                'online': is_online,
                'last_seen': last_seen_ago,
                'last_seen_text': format_last_seen(last_seen_ago)
            })
        
        # Sort agents (online first, then by last seen)
        online_agents.sort(key=lambda x: (not x['online'], x['last_seen']))
        
        # Get pending tasks
        pending_tasks = []
        for task in tasks:
            pending_tasks.append({
                'task_id': task['task_id'],
                'type': task.get('type', 'unknown'),
                'description': task.get('description', 'No description'),
                'submitted_at': task.get('submitted_at', 0)
            })
        
        return jsonify({
            'total_agents': len(agents),
            'online_agents': len([a for a in online_agents if a['online']]),
            'pending_tasks': len(tasks),
            'completed_tasks': len(results),
            'agents': online_agents,
            'tasks': pending_tasks,
            'server_time': current_time
        })

def format_last_seen(seconds_ago):
    """Format last seen time in human readable format."""
    if seconds_ago < 60:
        return f"{int(seconds_ago)}s ago"
    elif seconds_ago < 3600:
        return f"{int(seconds_ago // 60)}m ago"
    elif seconds_ago < 86400:
        return f"{int(seconds_ago // 3600)}h ago"
    else:
        return f"{int(seconds_ago // 86400)}d ago"

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Alpha Coordinator Dashboard                     ║
╚══════════════════════════════════════════════════════════════╝

Dashboard: http://localhost:5000
API: http://localhost:5000/api/dashboard-data

Real-time monitoring of all connected agents and tasks.
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
