"""
Simple Coordination Server
Central server that coordinates multiple Alpha Update Agents across different networks.

Agents connect TO this server (outbound connections work through NAT/firewalls).
Server tracks agents, distributes tasks, collects results.

Run this on a machine with a public IP or accessible network location.
"""

from flask import Flask, request, jsonify
import time
from datetime import datetime
import threading
import json

app = Flask(__name__)

# In-memory storage (use Redis/database for production)
agents = {}  # agent_id -> {info, last_heartbeat}
tasks = []  # Pending tasks queue
task_assignments = {}  # task_id -> agent_id
results = {}  # task_id -> result
resources = {}  # agent_id -> {resource_data, last_updated}

# Lock for thread-safe operations
lock = threading.Lock()


@app.route('/')
def index():
    """Redirect to the enhanced dashboard."""
    from flask import redirect
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard page."""
    try:
        from dashboard import dashboard as dashboard_route
        return dashboard_route()
    except ImportError:
        # Fallback to simple dashboard if dashboard module not available
        online_agents = [
            agent_id for agent_id, data in agents.items()
            if time.time() - data['last_heartbeat'] < 60
        ]
        
        return f"""
        <html>
        <head>
            <title>Alpha Coordinator</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                h1 {{ color: #333; }}
                .stat {{ background: #e8f4fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .agent {{ background: #f0f8f0; padding: 10px; margin: 5px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌐 Alpha Update Agent - Coordination Server</h1>
                <hr>
                <h2>📊 System Status</h2>
                <div class="stat"><strong>Total Agents Registered:</strong> {len(agents)}</div>
                <div class="stat"><strong>Agents Online:</strong> {len(online_agents)}</div>
                <div class="stat"><strong>Pending Tasks:</strong> {len(tasks)}</div>
                <div class="stat"><strong>Completed Tasks:</strong> {len(results)}</div>
                <hr>
                <h2>🤖 Connected Agents</h2>
                {''.join(f'<div class="agent">{aid} - Last seen: {time.time() - agents[aid]["last_heartbeat"]:.0f}s ago</div>' 
                         for aid in online_agents) if online_agents else '<div class="agent">No agents connected</div>'}
                <hr>
                <p><em>Auto-refresh every 5 seconds | <a href="/api/status">JSON API</a></em></p>
            </div>
        </body>
        </html>
        """


@app.route('/api/register', methods=['POST'])
def register_agent():
    """Register a new agent."""
    data = request.json
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    with lock:
        agents[agent_id] = {
            'info': data,
            'registered_at': time.time(),
            'last_heartbeat': time.time()
        }
    
    print(f"✓ Agent registered: {agent_id} ({data.get('hostname', 'unknown')})")
    
    return jsonify({
        'status': 'registered',
        'agent_id': agent_id,
        'message': 'Registration successful'
    })


@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Receive heartbeat from agent."""
    data = request.json
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    with lock:
        if agent_id in agents:
            agents[agent_id]['last_heartbeat'] = time.time()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'error': 'agent not registered'}), 404


@app.route('/api/tasks/next', methods=['GET'])
def get_next_task():
    """Get next available task for an agent."""
    agent_id = request.args.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    with lock:
        # Find unassigned task
        for task in tasks:
            if task['task_id'] not in task_assignments:
                # Assign task to this agent
                task_assignments[task['task_id']] = agent_id
                print(f"📤 Assigned task {task['task_id']} to agent {agent_id}")
                return jsonify(task)
    
    # No tasks available
    return jsonify({})


@app.route('/api/tasks/submit', methods=['POST'])
def submit_task():
    """Submit a new task to the queue."""
    data = request.json
    
    task_id = f"task_{int(time.time() * 1000)}"
    task = {
        'task_id': task_id,
        'type': data.get('type', 'compute'),
        'description': data.get('description', 'No description'),
        'params': data.get('params', {}),
        'submitted_at': time.time()
    }
    
    with lock:
        tasks.append(task)
    
    print(f"✓ New task submitted: {task_id} - {task['description']}")
    
    return jsonify({
        'status': 'submitted',
        'task_id': task_id
    })


@app.route('/api/tasks/result', methods=['POST'])
def submit_result():
    """Receive task result from agent."""
    data = request.json
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({'error': 'task_id required'}), 400
    
    with lock:
        results[task_id] = data
        # Remove from pending tasks
        tasks[:] = [t for t in tasks if t['task_id'] != task_id]
    
    print(f"✓ Result received for task {task_id} from agent {data.get('agent_id')}")
    
    return jsonify({'status': 'received'})


@app.route('/api/unregister', methods=['POST'])
def unregister_agent():
    """Unregister an agent."""
    data = request.json
    agent_id = data.get('agent_id')
    
    with lock:
        if agent_id in agents:
            del agents[agent_id]
            print(f"✓ Agent unregistered: {agent_id}")
    
    return jsonify({'status': 'unregistered'})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status as JSON."""
    online_agents = [
        {
            'agent_id': agent_id,
            'hostname': data['info'].get('hostname'),
            'last_seen': time.time() - data['last_heartbeat']
        }
        for agent_id, data in agents.items()
        if time.time() - data['last_heartbeat'] < 60
    ]
    
    return jsonify({
        'total_agents': len(agents),
        'online_agents': len(online_agents),
        'pending_tasks': len(tasks),
        'completed_tasks': len(results),
        'agents': online_agents,
        'tasks': [{'task_id': t['task_id'], 'type': t['type']} for t in tasks]
    })

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


@app.route('/api/resources/report', methods=['POST'])
def report_resources():
    """Receive resource information from agents."""
    data = request.json
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    with lock:
        resources[agent_id] = {
            'data': data,
            'last_updated': time.time()
        }
    
    print(f"✓ Resources updated for agent: {agent_id}")
    return jsonify({'status': 'received'})

@app.route('/api/resources/summary')
def get_resources_summary():
    """Get aggregated resource summary across all agents."""
    with lock:
        current_time = time.time()
        
        # Filter to only recent resource reports (within 5 minutes)
        recent_resources = {
            agent_id: data for agent_id, data in resources.items()
            if current_time - data['last_updated'] < 300  # 5 minutes
        }
        
        if not recent_resources:
            return jsonify({
                'total_agents': 0,
                'total_cpu_cores': 0,
                'total_memory_gb': 0,
                'total_storage_gb': 0,
                'gpu_count': 0,
                'agents': []
            })
        
        # Aggregate resources
        total_cpu_cores = 0
        total_memory_gb = 0
        total_storage_gb = 0
        gpu_count = 0
        agent_summaries = []
        
        for agent_id, resource_data in recent_resources.items():
            data = resource_data['data']
            
            # CPU cores
            cpu_cores = data.get('cpu', {}).get('cores_logical', 0)
            total_cpu_cores += cpu_cores
            
            # Memory
            memory_gb = data.get('memory', {}).get('total_gb', 0)
            total_memory_gb += memory_gb
            
            # Storage
            storage_gb = sum(disk.get('total_gb', 0) for disk in data.get('storage', []))
            total_storage_gb += storage_gb
            
            # GPU
            gpu_info = data.get('gpu', {})
            if gpu_info.get('available', False):
                gpu_count += gpu_info.get('count', 0)
            
            # Agent summary
            agent_summaries.append({
                'agent_id': agent_id,
                'hostname': data.get('system', {}).get('hostname', 'Unknown'),
                'platform': data.get('system', {}).get('platform', 'Unknown'),
                'cpu_cores': cpu_cores,
                'memory_gb': memory_gb,
                'storage_gb': storage_gb,
                'gpu_available': gpu_info.get('available', False),
                'gpu_count': gpu_info.get('count', 0),
                'cpu_usage': data.get('cpu', {}).get('usage_percent', 0),
                'memory_usage': data.get('memory', {}).get('usage_percent', 0),
                'last_updated': resource_data['last_updated'],
                'uptime_hours': round(data.get('system', {}).get('uptime_seconds', 0) / 3600, 1)
            })
        
        return jsonify({
            'total_agents': len(recent_resources),
            'total_cpu_cores': total_cpu_cores,
            'total_memory_gb': round(total_memory_gb, 2),
            'total_storage_gb': round(total_storage_gb, 2),
            'gpu_count': gpu_count,
            'agents': agent_summaries
        })

@app.route('/api/tasks/create-test', methods=['POST'])
def create_test_tasks():
    """Create some test tasks for demonstration."""
    test_tasks = [
        {
            'type': 'ping',
            'description': 'Simple ping test',
            'params': {}
        },
        {
            'type': 'compute',
            'description': 'Compute sum of squares',
            'params': {'n': 1000}
        },
        {
            'type': 'info',
            'description': 'Get agent information',
            'params': {}
        }
    ]
    
    created = []
    for task_data in test_tasks:
        task_id = f"task_{int(time.time() * 1000000)}"
        task = {
            'task_id': task_id,
            **task_data,
            'submitted_at': time.time()
        }
        with lock:
            tasks.append(task)
        created.append(task_id)
        time.sleep(0.001)  # Ensure unique IDs
    
    print(f"✓ Created {len(created)} test tasks")
    
    return jsonify({
        'status': 'created',
        'task_ids': created
    })


def cleanup_offline_agents():
    """Periodically clean up agents that haven't sent heartbeat in 5 minutes."""
    while True:
        time.sleep(60)  # Check every minute
        
        with lock:
            current_time = time.time()
            offline = [
                agent_id for agent_id, data in agents.items()
                if current_time - data['last_heartbeat'] > 300  # 5 minutes
            ]
            
            for agent_id in offline:
                del agents[agent_id]
                if offline:
                    print(f"⚠ Removed offline agent: {agent_id}")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Alpha Update Agent - Coordination Server             ║
╚══════════════════════════════════════════════════════════════╝

Server starting on http://0.0.0.0:5000

This server coordinates multiple agents across different networks.
Agents connect TO this server (works through NAT/firewalls).

Dashboard: http://localhost:5000
API: http://localhost:5000/api/...

To connect agents, set environment variable:
    COORDINATOR_URL=http://YOUR_SERVER_IP:5000

Press Ctrl+C to stop.
    """)
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_offline_agents, daemon=True)
    cleanup_thread.start()
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000, debug=False)

