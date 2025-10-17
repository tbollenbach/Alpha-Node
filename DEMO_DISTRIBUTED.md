# Demo: Distributed Agents on Different Networks

This guide shows you how to test multiple agents communicating through a central coordination server, **even when they're on different networks**.

## The Problem You Asked About

**Question:** "How will all the nodes connect when they are on different networks?"

**Answer:** They don't connect to each other directly! They all connect TO a central server (outbound connections work through NAT/firewalls).

## Visual Example

```
┌─────────────────┐          ┌─────────────────┐
│   Your Home     │          │   Your Office   │
│   Network       │          │   Network       │
│   (NAT/Router)  │          │   (Firewall)    │
│                 │          │                 │
│  ┌───────────┐  │          │  ┌───────────┐  │
│  │  Agent 1  │──┼──┐       │  │  Agent 2  │──┼──┐
│  └───────────┘  │  │       │  └───────────┘  │  │
└─────────────────┘  │       └─────────────────┘  │
                     │                            │
                     │    ┌─────────────────┐     │
                     └───▶│ Coordination    │◀────┘
                          │ Server          │
                          │ (Public Cloud)  │
                          └─────────────────┘
                                  ▲
                     ┌────────────┴────────────┐
                     │                         │
              ┌──────▼──────┐          ┌──────▼──────┐
              │   Agent 3   │          │   Agent 4   │
              │   (AWS)     │          │  (Azure)    │
              └─────────────┘          └─────────────┘
```

**Key Point:** All connections are **outbound from agents**, which works through ANY network setup!

## Quick Demo (3 Minutes)

### Step 1: Install Dependencies

```bash
pip install flask psutil
```

### Step 2: Start Coordination Server

**Terminal 1:**
```bash
cd coordinator_server
python simple_server.py
```

You'll see:
```
╔══════════════════════════════════════════════════════════════╗
║        Alpha Update Agent - Coordination Server             ║
╚══════════════════════════════════════════════════════════════╝

Server starting on http://0.0.0.0:5000
Dashboard: http://localhost:5000
```

### Step 3: Start First Agent

**Terminal 2:**
```bash
# Configure coordinator URL
# Windows PowerShell:
$env:COORDINATOR_URL="http://localhost:5000"

# Linux/macOS:
export COORDINATOR_URL=http://localhost:5000

# Enable coordinator module
# Edit config.json and add:
# "modules_enabled": ["simple_coordinator.py"]

# Run agent
python main.py run
```

You'll see:
```
Loading module: simple_coordinator
✓ Registered with coordinator at http://localhost:5000
```

### Step 4: Start Second Agent

**Terminal 3:**
```bash
# Set different hostname to simulate different machine
# Windows PowerShell:
$env:HOSTNAME="agent-2"
$env:COORDINATOR_URL="http://localhost:5000"

# Run agent
python main.py run
```

### Step 5: Start Third Agent

**Terminal 4:**
```bash
# Windows PowerShell:
$env:HOSTNAME="agent-3"
$env:COORDINATOR_URL="http://localhost:5000"

# Run agent
python main.py run
```

### Step 6: View Dashboard

Open browser: **http://localhost:5000**

You should see:
- **3 agents online**
- Their hostnames
- Last heartbeat times

### Step 7: Submit Tasks

**Terminal 5:**
```bash
# Windows PowerShell:
Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/tasks/create-test"

# Linux/macOS:
curl -X POST http://localhost:5000/api/tasks/create-test
```

### Step 8: Watch Tasks Execute!

Look at your agent terminals (2, 3, 4). You'll see:
```
📥 Received task: task_1234567890 - Simple ping test
🔧 Executing task task_1234567890 (type: ping)
✓ Task task_1234567890 completed
📤 Result submitted for task task_1234567890
```

**Tasks are distributed across agents automatically!**

## Extending to Real Different Networks

### Scenario 1: Friend's Computer

1. **Deploy server to cloud** (free options):
   - Heroku: `heroku create my-coordinator`
   - Railway.app
   - Render.com
   - Or any VPS with public IP

2. **Get public URL**: `https://my-coordinator.herokuapp.com`

3. **On your computer:**
```bash
export COORDINATOR_URL=https://my-coordinator.herokuapp.com
python main.py run
```

4. **On friend's computer** (different network):
```bash
export COORDINATOR_URL=https://my-coordinator.herokuapp.com
python main.py run
```

Both agents connect to same server, can execute tasks!

### Scenario 2: Home + Cloud

1. **Server on DigitalOcean/AWS** with public IP: `12.34.56.78`

2. **Home agent:**
```bash
export COORDINATOR_URL=http://12.34.56.78:5000
python main.py run
```

3. **AWS EC2 agent:**
```bash
export COORDINATOR_URL=http://12.34.56.78:5000
python main.py run
```

4. **Azure VM agent:**
```bash
export COORDINATOR_URL=http://12.34.56.78:5000
python main.py run
```

All communicate through central server!

### Scenario 3: Office Network (Behind Firewall)

Even if your office has strict firewall:
- **Outbound** HTTP/HTTPS usually allowed
- Agent connects TO server (outbound)
- Server can't connect TO agent (but doesn't need to!)

```bash
# Behind corporate firewall - still works!
export COORDINATOR_URL=https://coordinator.mycompany.com
python main.py run
```

## Testing Task Distribution

### Submit Custom Tasks

```bash
# PowerShell:
$body = @{
    type = "compute"
    description = "Calculate fibonacci"
    params = @{n = 100}
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5000/api/tasks/submit" `
    -ContentType "application/json" -Body $body

# Bash:
curl -X POST http://localhost:5000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "compute",
    "description": "Heavy computation",
    "params": {"n": 10000}
  }'
```

### View Results

```bash
# Get system status
curl http://localhost:5000/api/status

# Or check dashboard in browser
open http://localhost:5000  # macOS
start http://localhost:5000 # Windows
```

## Real-World Example: GPU Sharing

### Modify gpu_share.py to work with coordinator:

```python
# In modules/gpu_share.py, add:

def execute_gpu_task(task_params):
    """Execute GPU computation task"""
    # Your GPU computation here
    result = run_gpu_computation(task_params)
    return result
```

### Submit GPU tasks from anywhere:

```bash
curl -X POST http://your-server.com/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "gpu_compute",
    "description": "Render 3D scene",
    "params": {
      "scene_file": "scene.obj",
      "resolution": "1920x1080"
    }
  }'
```

Agent with GPU picks up task, executes, returns result!

## How It Solves NAT/Firewall Issues

### Traditional P2P (Doesn't Work)
```
Agent 1 (192.168.1.5) ──X──> Agent 2 (10.0.0.5)
       NAT makes this IP unreachable from outside
```

### Central Server (Works!)
```
Agent 1 ──┐
          │
          ├──> Server (Public: 12.34.56.78) <──┐
          │                                     │
Agent 2 ──┘                             Agent 3─┘

All agents connect TO server (outbound = no NAT issues)
```

## Production Deployment Checklist

- [ ] Deploy server to cloud with public IP/domain
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Add authentication tokens
- [ ] Set up database for persistence (Redis/PostgreSQL)
- [ ] Add monitoring (logs, metrics)
- [ ] Configure agent auto-start on boot
- [ ] Test from multiple actual networks
- [ ] Set up backup/recovery

## Common Questions

**Q: Do agents need to know about each other?**
A: No! They only know the server URL.

**Q: What if server goes down?**
A: Agents will retry connection. Add redundancy with multiple servers + load balancer.

**Q: How many agents can connect?**
A: Simple server: ~100 agents. With Redis/load balancing: 10,000+

**Q: Can I use this for actual GPU sharing?**
A: Yes! Extend gpu_share.py module to handle actual GPU tasks.

**Q: Is this secure?**
A: For testing yes. For production: add HTTPS + authentication + encryption.

**Q: Does this work across countries?**
A: Yes! Agent in USA + Agent in Europe + Agent in Asia = all connected.

## Next Steps

1. ✅ Test locally (3 terminals simulating 3 machines)
2. ✅ Deploy server to free cloud provider
3. ✅ Connect from 2+ real different networks
4. 🔄 Add authentication for production
5. 🔄 Implement your custom task types
6. 🔄 Scale to more agents

**You now understand how distributed agents communicate across networks!** 🎉

