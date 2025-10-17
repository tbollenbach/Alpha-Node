"""
Real-time Dashboard for Alpha Update Agent Coordination Server
Professional dark-theme design with modern aesthetics.
"""

from flask import render_template_string

def dashboard():
    """Renders the professional real-time dashboard."""
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha Coordinator - Control Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --bg-primary: #0a0e27;
            --bg-secondary: #111630;
            --bg-card: #1a1f3a;
            --accent-primary: #00d4ff;
            --accent-secondary: #7b2ff7;
            --accent-tertiary: #ff6b35;
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: rgba(255, 255, 255, 0.1);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Animated background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(123, 47, 247, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 107, 53, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        .dashboard {
            position: relative;
            z-index: 1;
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Header */
        .header {
            margin-bottom: 3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: 800;
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        }
        
        .title-section h1 {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }
        
        .title-section p {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        
        .status-badge {
            padding: 0.5rem 1rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 20px;
            color: var(--success);
            font-size: 0.875rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: 0 20px 40px rgba(0, 212, 255, 0.1);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        
        .stat-trend {
            font-size: 0.75rem;
            color: var(--success);
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        /* Content Grid */
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
        }
        
        .panel-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .panel-title {
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .panel-badge {
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent-primary);
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        
        .panel-body {
            padding: 1.5rem;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .panel-body::-webkit-scrollbar {
            width: 8px;
        }
        
        .panel-body::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        .panel-body::-webkit-scrollbar-thumb {
            background: var(--accent-primary);
            border-radius: 4px;
        }
        
        /* Agent Items */
        .agent-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
        }
        
        .agent-item:hover {
            border-color: var(--accent-primary);
            transform: translateX(4px);
        }
        
        .agent-info {
            flex: 1;
        }
        
        .agent-name {
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.25rem;
            color: var(--text-primary);
        }
        
        .agent-details {
            font-size: 0.75rem;
            color: var(--text-secondary);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .agent-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--success);
            box-shadow: 0 0 12px var(--success);
            animation: pulse 2s infinite;
        }
        
        .status-indicator.offline {
            background: var(--danger);
            box-shadow: 0 0 12px var(--danger);
            animation: none;
        }
        
        .status-text {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        /* Resource Bars */
        .resource-bar {
            margin-top: 0.5rem;
        }
        
        .resource-bar-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }
        
        .resource-bar-track {
            height: 4px;
            background: var(--bg-primary);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .resource-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 2px;
            transition: width 0.3s ease;
        }
        
        /* Empty States */
        .empty-state {
            text-align: center;
            padding: 3rem 1rem;
            color: var(--text-secondary);
        }
        
        .empty-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.3;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .footer-link {
            color: var(--accent-primary);
            text-decoration: none;
            transition: color 0.2s ease;
        }
        
        .footer-link:hover {
            color: var(--accent-secondary);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .dashboard {
                padding: 1rem;
            }
            
            .header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-value {
                font-size: 2rem;
            }
        }
        
        /* Gradient Text */
        .gradient-text {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Glow Effect */
        .glow {
            animation: glow 3s ease-in-out infinite;
        }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 255, 0.2); }
            50% { box-shadow: 0 0 40px rgba(0, 212, 255, 0.4); }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <header class="header">
            <div class="logo-section">
                <div class="logo glow">α</div>
                <div class="title-section">
                    <h1>ALPHA CONTROL CENTER</h1>
                    <p>Distributed Computing Coordination Platform</p>
                </div>
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                <span id="last-update">SYSTEM ONLINE</span>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Agents Online</div>
                <div class="stat-value gradient-text" id="online-count">0</div>
                <div class="stat-trend">● Active nodes</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total CPU Cores</div>
                <div class="stat-value gradient-text" id="total-cpu-cores">0</div>
                <div class="stat-trend">● Pooled compute</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total Memory</div>
                <div class="stat-value gradient-text"><span id="total-memory-gb">0</span> GB</div>
                <div class="stat-trend">● Available RAM</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total Storage</div>
                <div class="stat-value gradient-text"><span id="total-storage-gb">0</span> GB</div>
                <div class="stat-trend">● Distributed disk</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">GPU Devices</div>
                <div class="stat-value gradient-text" id="total-gpu-count">0</div>
                <div class="stat-trend">● Accelerators</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Pending Tasks</div>
                <div class="stat-value gradient-text" id="pending-count">0</div>
                <div class="stat-trend">● In queue</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Completed Tasks</div>
                <div class="stat-value gradient-text" id="completed-count">0</div>
                <div class="stat-trend">● Processed</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Total Agents</div>
                <div class="stat-value gradient-text" id="total-count">0</div>
                <div class="stat-trend">● Registered</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">
                        Connected Nodes
                    </div>
                    <div class="panel-badge" id="agents-badge">0</div>
                </div>
                <div class="panel-body" id="agents-list">
                    <div class="empty-state">
                        <div class="empty-icon">⚡</div>
                        <div>No agents connected</div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">
                        Task Queue
                    </div>
                    <div class="panel-badge" id="tasks-badge">0</div>
                </div>
                <div class="panel-body" id="tasks-list">
                    <div class="empty-state">
                        <div class="empty-icon">📋</div>
                        <div>No pending tasks</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">
                        Hardware Resources
                    </div>
                    <div class="panel-badge" id="resources-badge">0</div>
                </div>
                <div class="panel-body" id="resources-list">
                    <div class="empty-state">
                        <div class="empty-icon">💻</div>
                        <div>No resource data available</div>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <div class="panel-header">
                    <div class="panel-title">
                        System Metrics
                    </div>
                    <div class="panel-badge">LIVE</div>
                </div>
                <div class="panel-body" id="resource-summary">
                    <div class="empty-state">
                        <div class="empty-icon">📊</div>
                        <div>Loading metrics...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="footer">
            <div>Alpha Distributed Computing Platform v2.0.0</div>
            <div class="footer-links">
                <a href="/api/status" class="footer-link">API Status</a>
                <a href="https://github.com/tbollenbach/Alpha-Node" class="footer-link">GitHub</a>
                <a href="/api/dashboard-data" class="footer-link">Raw Data</a>
            </div>
        </footer>
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
                    const agentsBadge = document.getElementById('agents-badge');
                    agentsBadge.textContent = data.agents.length;
                    
                    if (data.agents.length === 0) {
                        agentsList.innerHTML = '<div class="empty-state"><div class="empty-icon">⚡</div><div>No agents connected</div></div>';
                    } else {
                        agentsList.innerHTML = data.agents.map(agent => `
                            <div class="agent-item">
                                <div class="agent-info">
                                    <div class="agent-name">${agent.agent_id}</div>
                                    <div class="agent-details">
                                        <span>Host: ${agent.hostname}</span>
                                        <span>Last seen: ${agent.last_seen_text}</span>
                                    </div>
                                </div>
                                <div class="agent-status">
                                    <div class="status-indicator ${agent.online ? '' : 'offline'}"></div>
                                    <span class="status-text">${agent.online ? 'ONLINE' : 'OFFLINE'}</span>
                                </div>
                            </div>
                        `).join('');
                    }
                    
                    // Update tasks list
                    const tasksList = document.getElementById('tasks-list');
                    const tasksBadge = document.getElementById('tasks-badge');
                    tasksBadge.textContent = data.tasks.length;
                    
                    if (data.tasks.length === 0) {
                        tasksList.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><div>No pending tasks</div></div>';
                    } else {
                        tasksList.innerHTML = data.tasks.map(task => `
                            <div class="agent-item">
                                <div class="agent-info">
                                    <div class="agent-name">Task ${task.task_id}</div>
                                    <div class="agent-details">
                                        <span>Type: ${task.type}</span>
                                        <span>${task.description}</span>
                                    </div>
                                </div>
                            </div>
                        `).join('');
                    }
                })
                .catch(error => console.error('Error fetching dashboard data:', error));
            
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
                    const resourcesBadge = document.getElementById('resources-badge');
                    resourcesBadge.textContent = resourceData.agents.length;
                    
                    if (resourceData.agents.length === 0) {
                        resourcesList.innerHTML = '<div class="empty-state"><div class="empty-icon">💻</div><div>No resource data available</div></div>';
                    } else {
                        resourcesList.innerHTML = resourceData.agents.map(agent => `
                            <div class="agent-item">
                                <div class="agent-info">
                                    <div class="agent-name">${agent.hostname} · ${agent.platform}</div>
                                    <div class="agent-details">
                                        <span>CPU: ${agent.cpu_cores} cores</span>
                                        <span>RAM: ${agent.memory_gb}GB</span>
                                        <span>Storage: ${agent.storage_gb}GB</span>
                                        ${agent.gpu_available ? `<span>GPU: ${agent.gpu_count}x</span>` : ''}
                                    </div>
                                    <div class="resource-bar">
                                        <div class="resource-bar-label">
                                            <span>CPU Usage</span>
                                            <span>${agent.cpu_usage}%</span>
                                        </div>
                                        <div class="resource-bar-track">
                                            <div class="resource-bar-fill" style="width: ${agent.cpu_usage}%"></div>
                                        </div>
                                    </div>
                                    <div class="resource-bar">
                                        <div class="resource-bar-label">
                                            <span>Memory Usage</span>
                                            <span>${agent.memory_usage}%</span>
                                        </div>
                                        <div class="resource-bar-track">
                                            <div class="resource-bar-fill" style="width: ${agent.memory_usage}%"></div>
                                        </div>
                                    </div>
                                </div>
                                <div class="agent-status">
                                    <div class="status-text">${agent.uptime_hours}h</div>
                                </div>
                            </div>
                        `).join('');
                    }
                    
                    // Update resource summary
                    const resourceSummary = document.getElementById('resource-summary');
                    if (resourceData.total_agents > 0) {
                        resourceSummary.innerHTML = `
                            <div style="padding: 1rem 0;">
                                <div style="margin-bottom: 1.5rem;">
                                    <div class="stat-label">Total Pooled Resources</div>
                                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                                        Aggregated from ${resourceData.total_agents} active node${resourceData.total_agents > 1 ? 's' : ''}
                                    </div>
                                </div>
                                
                                <div class="agent-item" style="flex-direction: column; align-items: stretch;">
                                    <div class="agent-details" style="gap: 1rem; margin-bottom: 1rem;">
                                        <div style="flex: 1;">
                                            <div style="font-size: 2rem; font-weight: 800; color: var(--accent-primary);">${resourceData.total_cpu_cores}</div>
                                            <div style="font-size: 0.75rem; color: var(--text-secondary);">CPU CORES</div>
                                        </div>
                                        <div style="flex: 1;">
                                            <div style="font-size: 2rem; font-weight: 800; color: var(--accent-secondary);">${resourceData.total_memory_gb}</div>
                                            <div style="font-size: 0.75rem; color: var(--text-secondary);">GB RAM</div>
                                        </div>
                                    </div>
                                    <div class="agent-details" style="gap: 1rem;">
                                        <div style="flex: 1;">
                                            <div style="font-size: 2rem; font-weight: 800; color: var(--success);">${resourceData.total_storage_gb}</div>
                                            <div style="font-size: 0.75rem; color: var(--text-secondary);">GB STORAGE</div>
                                        </div>
                                        <div style="flex: 1;">
                                            <div style="font-size: 2rem; font-weight: 800; color: var(--accent-tertiary);">${resourceData.gpu_count}</div>
                                            <div style="font-size: 0.75rem; color: var(--text-secondary);">GPU DEVICES</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Update last update time
                    const now = new Date();
                    document.getElementById('last-update').textContent = `UPDATED ${now.toLocaleTimeString()}`;
                })
                .catch(error => console.error('Error fetching resource data:', error));
        }
        
        // Initial update
        updateDashboard();
        
        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
    """)
