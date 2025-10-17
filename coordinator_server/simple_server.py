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

# Lock for thread-safe operations
lock = threading.Lock()


@app.route('/')
def index():
    """Dashboard showing system status."""
    online_agents = [
        agent_id for agent_id, data in agents.items()
        if time.time() - data['last_heartbeat'] < 60
    ]
    
    return f"""
    <html>
    <head><title>Alpha Coordinator</title></head>
    <body style="font-family: monospace; padding: 20px;">
        <h1>🌐 Alpha Update Agent - Coordination Server</h1>
        <hr>
        <h2>📊 System Status</h2>
        <p><strong>Total Agents Registered:</strong> {len(agents)}</p>
        <p><strong>Agents Online:</strong> {len(online_agents)}</p>
        <p><strong>Pending Tasks:</strong> {len(tasks)}</p>
        <p><strong>Completed Tasks:</strong> {len(results)}</p>
        <hr>
        <h2>🤖 Connected Agents</h2>
        <ul>
        {''.join(f'<li>{aid} - Last seen: {time.time() - agents[aid]["last_heartbeat"]:.0f}s ago</li>' 
                 for aid in online_agents)}
        </ul>
        <hr>
        <h2>📝 API Endpoints</h2>
        <ul>
            <li>POST /api/register - Register agent</li>
            <li>POST /api/heartbeat - Send heartbeat</li>
            <li>GET /api/tasks/next - Get next task</li>
            <li>POST /api/tasks/submit - Submit new task</li>
            <li>POST /api/tasks/result - Submit task result</li>
            <li>GET /api/status - Get system status (JSON)</li>
        </ul>
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

