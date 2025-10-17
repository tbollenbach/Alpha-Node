# Distributed Networking Guide

## Understanding the Current Architecture

### What's Implemented (MVP)
```
Agent 1 (Network A)  ──┐
Agent 2 (Network B)  ──┼──> Central Update Server (Public Internet)
Agent 3 (Network C)  ──┘

Each agent:
- Checks update server independently
- Downloads updates
- NO direct agent-to-agent communication yet
```

**Current system:** All agents connect to ONE central server (update server), but don't talk to each other.

### What You're Asking About
```
Agent 1 (Home Network) <──> Agent 2 (Office Network) <──> Agent 3 (Cloud)
           ↕                        ↕                         ↕
         Tasks              Coordination                 Results

Distributed computing: Agents need to communicate for task distribution
```

## How to Connect Nodes Across Networks

There are several approaches, from simple to sophisticated:

---

## Approach 1: Central Coordination Server (Easiest)

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                   Coordination Server                       │
│            (Public IP or Cloud: e.g., AWS)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - WebSocket Server / REST API / MQTT Broker        │   │
│  │  - Task Queue (Redis, RabbitMQ)                     │   │
│  │  - Agent Registry (who's online, capabilities)      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────┬────────────────┬─────────────────┬──────────┘
               │                │                 │
        ┌──────▼─────┐   ┌─────▼──────┐   ┌─────▼──────┐
        │  Agent 1   │   │  Agent 2   │   │  Agent 3   │
        │ Home WiFi  │   │ Office LAN │   │   Cloud    │
        │ (NAT)      │   │ (Firewall) │   │  (Public)  │
        └────────────┘   └────────────┘   └────────────┘
```

### How It Works
1. **All agents connect TO the server** (outbound connections work through NAT/firewalls)
2. **Server coordinates everything** (task distribution, results collection)
3. **No direct agent-to-agent connection needed**

### Implementation Example

**Add to your agent - Coordination Client:**

```python
# modules/coordinator_client.py
"""
Coordination module - connects agent to central coordination server
"""
import logging
import websocket
import json
import threading

logger = None
ws = None
agent_id = None

def init():
    global logger, ws, agent_id
    logger = logging.getLogger('coordinator')
    agent_id = f"agent_{os.getenv('HOSTNAME', 'unknown')}"
    
    # Connect to coordination server
    server_url = "wss://your-server.com/agent-connect"  # WebSocket
    ws = websocket.WebSocketApp(
        server_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run WebSocket in background thread
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Register with server
    register_agent()
    logger.info(f"Connected to coordinator as {agent_id}")

def on_message(ws, message):
    """Handle incoming tasks from server"""
    data = json.loads(message)
    
    if data['type'] == 'task':
        logger.info(f"Received task: {data['task_id']}")
        result = execute_task(data)
        send_result(result)
    
    elif data['type'] == 'config_update':
        logger.info("Received configuration update")
        apply_config(data['config'])

def register_agent():
    """Tell server about this agent's capabilities"""
    capabilities = {
        'type': 'register',
        'agent_id': agent_id,
        'capabilities': {
            'gpu': has_gpu(),
            'cpu_cores': os.cpu_count(),
            'memory_gb': get_memory_gb(),
            'storage_gb': get_free_storage_gb()
        }
    }
    ws.send(json.dumps(capabilities))

def execute_task(task_data):
    """Execute a task and return results"""
    # Task execution logic here
    return {'status': 'completed', 'result': 'data'}

def send_result(result):
    """Send task results back to server"""
    ws.send(json.dumps({
        'type': 'result',
        'agent_id': agent_id,
        'result': result
    }))

def cleanup():
    global ws
    if ws:
        ws.close()
    logger.info("Disconnected from coordinator")
```

**Coordination Server (Simple Example):**

```python
# coordination_server.py
from flask import Flask
from flask_sock import Sock
import json

app = Flask(__name__)
sock = Sock(app)

agents = {}  # Connected agents
task_queue = []  # Pending tasks

@sock.route('/agent-connect')
def agent_connect(ws):
    """Handle agent WebSocket connections"""
    agent_id = None
    
    while True:
        message = ws.receive()
        if not message:
            break
            
        data = json.loads(message)
        
        if data['type'] == 'register':
            agent_id = data['agent_id']
            agents[agent_id] = {
                'ws': ws,
                'capabilities': data['capabilities']
            }
            print(f"Agent registered: {agent_id}")
            
            # Assign tasks if available
            if task_queue:
                task = task_queue.pop(0)
                ws.send(json.dumps(task))
        
        elif data['type'] == 'result':
            print(f"Result from {data['agent_id']}: {data['result']}")
            # Store result, notify clients, etc.
    
    # Cleanup on disconnect
    if agent_id and agent_id in agents:
        del agents[agent_id]
        print(f"Agent disconnected: {agent_id}")

@app.route('/submit-task', methods=['POST'])
def submit_task():
    """API endpoint for submitting tasks"""
    # Task submission logic
    task_queue.append(request.json)
    return {'status': 'queued'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Deployment
- **Server**: Deploy on AWS, DigitalOcean, Heroku, etc. with public IP
- **Agents**: Connect from anywhere (home, office, cloud) - they just need internet

---

## Approach 2: VPN Mesh Network (More Direct)

### Architecture
```
┌──────────────────────────────────────────────────────┐
│           VPN Mesh (e.g., Tailscale, ZeroTier)       │
│    All nodes get virtual IPs on same network         │
└──────────────────────────────────────────────────────┘
       │                    │                    │
   ┌───▼────┐         ┌────▼─────┐        ┌────▼─────┐
   │Agent 1 │◄───────►│ Agent 2  │◄──────►│ Agent 3  │
   │10.0.0.1│         │10.0.0.2  │        │10.0.0.3  │
   └────────┘         └──────────┘        └──────────┘
```

### How It Works
1. **Install VPN software** (Tailscale, ZeroTier, WireGuard) on all nodes
2. **All nodes appear on same virtual network** (e.g., 10.0.0.0/24)
3. **Direct peer-to-peer communication** using virtual IPs
4. **NAT/firewall transparent** - VPN handles it

### Implementation with Tailscale (Recommended)

**Setup:**
```bash
# On each machine:
# 1. Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Login and connect
tailscale up

# 3. Get your IP
tailscale ip -4
# Example output: 100.101.102.103
```

**Update coordination module:**
```python
# modules/p2p_coordinator.py
"""
Peer-to-peer coordination using VPN mesh
"""
import socket
import json

# Known peer IPs (from Tailscale)
PEERS = [
    '100.101.102.101',  # Agent 1
    '100.101.102.102',  # Agent 2
    '100.101.102.103',  # Agent 3
]

def init():
    # Start listening for peer connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9000))
    server.listen(5)
    
    # Handle connections in background
    threading.Thread(target=accept_connections, args=(server,)).start()

def accept_connections(server):
    while True:
        client, addr = server.accept()
        handle_peer(client, addr)

def send_to_peer(peer_ip, message):
    """Send message to another agent"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((peer_ip, 9000))
    sock.send(json.dumps(message).encode())
    sock.close()

def broadcast_to_all_peers(message):
    """Send to all known peers"""
    for peer in PEERS:
        try:
            send_to_peer(peer, message)
        except:
            pass  # Peer offline
```

---

## Approach 3: NAT Traversal / P2P (Advanced)

### Architecture
```
┌────────────┐                                ┌────────────┐
│  Agent 1   │                                │  Agent 2   │
│  (NAT)     │                                │  (NAT)     │
└──────┬─────┘                                └─────┬──────┘
       │                                            │
       └────────┐                          ┌────────┘
                │                          │
                ▼                          ▼
        ┌───────────────────────────────────────┐
        │   STUN/TURN Server (Public)           │
        │   Helps establish direct P2P          │
        └───────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Direct P2P tunnel│
              │ (hole punched)   │
              └──────────────────┘
```

### Libraries
- **Python**: `aiortc`, `pynats`, `libp2p`
- **Protocols**: WebRTC, STUN, TURN

---

## Approach 4: Cloud Message Broker (Simple & Scalable)

### Architecture
```
┌────────────────────────────────────────────────┐
│     Cloud Message Broker (MQTT/Redis Pub/Sub) │
│          e.g., AWS IoT, CloudMQTT              │
└─────┬──────────────┬────────────────┬─────────┘
      │              │                │
  ┌───▼────┐    ┌────▼─────┐    ┌────▼─────┐
  │Agent 1 │    │ Agent 2  │    │ Agent 3  │
  │Subscribe│   │Publish   │    │Subscribe │
  └────────┘    └──────────┘    └──────────┘
```

### Implementation (MQTT)

**Install:**
```bash
pip install paho-mqtt
```

**Module:**
```python
# modules/mqtt_coordinator.py
import paho.mqtt.client as mqtt
import json
import logging

logger = None
client = None
agent_id = None

def init():
    global logger, client, agent_id
    logger = logging.getLogger('mqtt_coordinator')
    agent_id = f"agent_{socket.gethostname()}"
    
    # Connect to MQTT broker
    client = mqtt.Client(agent_id)
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to broker (e.g., CloudMQTT, AWS IoT)
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()
    
    logger.info(f"Connected to MQTT broker as {agent_id}")

def on_connect(client, userdata, flags, rc):
    # Subscribe to topics
    client.subscribe("alpha/tasks/#")  # All tasks
    client.subscribe(f"alpha/agent/{agent_id}/#")  # This agent's commands

def on_message(client, userdata, msg):
    logger.info(f"Message on {msg.topic}: {msg.payload}")
    data = json.loads(msg.payload)
    
    if 'task' in data:
        result = execute_task(data['task'])
        publish_result(result)

def publish_result(result):
    topic = f"alpha/results/{agent_id}"
    client.publish(topic, json.dumps(result))

def publish_status():
    """Heartbeat - tell others you're alive"""
    topic = f"alpha/status/{agent_id}"
    status = {
        'agent_id': agent_id,
        'status': 'online',
        'capabilities': get_capabilities()
    }
    client.publish(topic, json.dumps(status))

def cleanup():
    global client
    if client:
        client.loop_stop()
        client.disconnect()
```

---

## Recommended Approach for Your Use Case

### For Small Scale (< 100 nodes)
**Use Approach 1 (Central Server) or Approach 4 (MQTT)**
- Easiest to implement
- Works through NAT/firewalls automatically
- No complex networking setup

### For Medium Scale (100-1000 nodes)
**Use Approach 2 (VPN Mesh) + Central Coordination**
- Tailscale/ZeroTier for connectivity
- Central server for task distribution
- Direct P2P for large data transfers

### For Large Scale (1000+ nodes)
**Use Approach 4 (Cloud Message Broker) + CDN**
- AWS IoT Core / Google Cloud Pub/Sub
- Handles millions of messages
- Built-in scaling and reliability

---

## Quick Implementation Example

Let me create a simple coordinator module you can add right now:

```python
# modules/simple_coordinator.py
"""
Simple HTTP-based coordinator for distributed agents.
Agents poll a central server for tasks.
"""
import logging
import requests
import socket
import json
import time

logger = None
coordinator_url = "https://your-server.com/api"
agent_id = None

def init():
    global logger, agent_id
    logger = logging.getLogger('simple_coordinator')
    agent_id = socket.gethostname()
    
    # Register with server
    register()
    logger.info(f"Registered with coordinator as {agent_id}")

def register():
    """Register this agent with coordinator"""
    try:
        response = requests.post(
            f"{coordinator_url}/agents/register",
            json={
                'agent_id': agent_id,
                'capabilities': {
                    'cpu': True,
                    'gpu': False,  # Detect actual GPU
                    'storage_gb': 100
                }
            }
        )
        logger.info(f"Registration response: {response.json()}")
    except Exception as e:
        logger.error(f"Registration failed: {e}")

def tick():
    """Periodically check for tasks"""
    try:
        # Poll for tasks
        response = requests.get(f"{coordinator_url}/tasks/next?agent_id={agent_id}")
        
        if response.status_code == 200:
            task = response.json()
            if task:
                logger.info(f"Received task: {task['task_id']}")
                result = execute_task(task)
                submit_result(result)
    except Exception as e:
        logger.error(f"Error checking for tasks: {e}")

def execute_task(task):
    """Execute the task"""
    # Task execution logic
    logger.info(f"Executing task {task['task_id']}")
    return {
        'task_id': task['task_id'],
        'status': 'completed',
        'result': 'Task done!'
    }

def submit_result(result):
    """Submit task results"""
    try:
        requests.post(
            f"{coordinator_url}/tasks/result",
            json=result
        )
        logger.info("Result submitted")
    except Exception as e:
        logger.error(f"Failed to submit result: {e}")

def cleanup():
    # Unregister
    try:
        requests.post(
            f"{coordinator_url}/agents/unregister",
            json={'agent_id': agent_id}
        )
    except:
        pass
```

---

## Summary: How Nodes Connect

| Method | Complexity | NAT-Friendly | Best For |
|--------|-----------|--------------|----------|
| Central Server | Low | ✅ Yes | Small-medium scale |
| VPN Mesh | Medium | ✅ Yes | Secure, direct P2P |
| NAT Traversal | High | ⚠️ Partial | Custom protocols |
| Message Broker | Low-Medium | ✅ Yes | Large scale |

**Bottom Line:** Start with a **central coordination server** or **MQTT broker**. All agents connect TO it (outbound), which works through any NAT/firewall. No direct agent-to-agent connection needed!


