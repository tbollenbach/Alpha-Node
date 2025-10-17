# Coordination Server for Distributed Agents

This server allows multiple Alpha Update Agents on **different networks** to communicate and coordinate tasks.

## How It Works

```
Agent 1 (Home)  ──┐
Agent 2 (Office) ─┼──> Coordination Server (Public IP)
Agent 3 (Cloud)  ──┘

All agents connect TO the server (outbound).
Server distributes tasks and collects results.
NO direct agent-to-agent communication needed!
```

## Quick Start

### 1. Install Dependencies

```bash
pip install flask
```

### 2. Start the Server

```bash
cd coordinator_server
python simple_server.py
```

Server will run at `http://localhost:5000`

### 3. Enable Coordinator Module on Agents

Edit your agent's `config.json`:
```json
{
    "modules_enabled": ["simple_coordinator.py"]
}
```

Set the coordinator URL:
```bash
# Linux/macOS
export COORDINATOR_URL=http://localhost:5000

# Windows PowerShell
$env:COORDINATOR_URL="http://localhost:5000"

# Windows CMD
set COORDINATOR_URL=http://localhost:5000
```

### 4. Run Agents

```bash
# Terminal 1
python main.py run

# Terminal 2 (on different machine or terminal)
python main.py run

# Terminal 3 (on different machine or terminal)
python main.py run
```

### 5. Submit Tasks

```bash
# Create test tasks
curl -X POST http://localhost:5000/api/tasks/create-test

# Or submit custom task
curl -X POST http://localhost:5000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "type": "compute",
    "description": "Calculate sum of squares",
    "params": {"n": 5000}
  }'
```

### 6. View Dashboard

Open browser: `http://localhost:5000`

You'll see:
- Connected agents
- Task queue
- Completed tasks

## API Endpoints

### Register Agent
```bash
POST /api/register
{
  "agent_id": "agent_123",
  "hostname": "my-computer",
  "capabilities": {...}
}
```

### Heartbeat
```bash
POST /api/heartbeat
{
  "agent_id": "agent_123",
  "timestamp": 1234567890
}
```

### Get Next Task
```bash
GET /api/tasks/next?agent_id=agent_123
```

### Submit Task
```bash
POST /api/tasks/submit
{
  "type": "compute",
  "description": "My task",
  "params": {...}
}
```

### Submit Result
```bash
POST /api/tasks/result
{
  "task_id": "task_123",
  "agent_id": "agent_123",
  "status": "completed",
  "result": {...}
}
```

### Get Status
```bash
GET /api/status
```

## Deploying to Production

### Option 1: Cloud VM (AWS, DigitalOcean, etc.)

```bash
# 1. Launch Ubuntu VM with public IP

# 2. Install dependencies
sudo apt update
sudo apt install python3 python3-pip
pip3 install flask

# 3. Upload server files
scp simple_server.py user@your-server-ip:~/

# 4. Run server
python3 simple_server.py

# 5. Configure firewall
sudo ufw allow 5000/tcp
```

Update agent config to use public IP:
```bash
export COORDINATOR_URL=http://your-server-ip:5000
```

### Option 2: Heroku (Free)

```bash
# 1. Create Procfile
echo "web: python simple_server.py" > Procfile

# 2. Create requirements.txt
echo "flask" > requirements.txt

# 3. Deploy
heroku create my-alpha-coordinator
git push heroku main
```

Get URL: `https://my-alpha-coordinator.herokuapp.com`

### Option 3: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY simple_server.py .
RUN pip install flask
EXPOSE 5000
CMD ["python", "simple_server.py"]
```

```bash
docker build -t alpha-coordinator .
docker run -p 5000:5000 alpha-coordinator
```

### Option 4: Production-Grade (with Gunicorn)

```bash
# Install
pip install gunicorn

# Run
gunicorn -w 4 -b 0.0.0.0:5000 simple_server:app
```

## Security Considerations

**Current implementation is for testing only!**

For production, add:

1. **Authentication**
```python
@app.before_request
def check_auth():
    token = request.headers.get('Authorization')
    if token != 'Bearer YOUR_SECRET_TOKEN':
        return jsonify({'error': 'Unauthorized'}), 401
```

2. **HTTPS** (use Let's Encrypt + Nginx)

3. **Rate Limiting**
```bash
pip install flask-limiter
```

4. **Database** (instead of in-memory)
```bash
pip install redis  # or PostgreSQL
```

## Testing Multiple Agents Locally

You can simulate multiple agents on one machine:

```bash
# Terminal 1: Server
python simple_server.py

# Terminal 2: Agent 1
python main.py run

# Terminal 3: Agent 2
HOSTNAME=agent2 python main.py run

# Terminal 4: Agent 3
HOSTNAME=agent3 python main.py run

# Terminal 5: Submit tasks
curl -X POST http://localhost:5000/api/tasks/create-test
```

Watch the logs - tasks will be distributed to agents!

## Scaling to Large Networks

For large deployments (100+ agents):

1. **Use Redis** for task queue
2. **Use PostgreSQL** for results storage
3. **Load balance** with multiple server instances
4. **Use WebSockets** for real-time updates
5. **Add monitoring** (Prometheus, Grafana)

## Troubleshooting

### "Connection refused"
- Server not running
- Firewall blocking port 5000
- Wrong IP/hostname

### Agents not connecting
- Check COORDINATOR_URL is set correctly
- Verify network connectivity: `curl http://server:5000`
- Check server logs

### Tasks not distributing
- Agents need to have coordinator module enabled
- Check agent logs for errors
- Verify tasks are in queue: `curl http://server:5000/api/status`

## Next Steps

1. Test locally with multiple terminals
2. Deploy server to cloud
3. Connect real agents on different networks
4. Build custom task types for your use case
5. Add authentication for production

