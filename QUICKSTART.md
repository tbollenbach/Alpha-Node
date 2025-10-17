# 🚀 Quick Start Guide

Get the Alpha Update Agent running in 5 minutes!

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 2: Test the Agent (1 minute)

```bash
# Check the version
python main.py version

# Run once to verify everything works
python main.py once
```

You should see output like:
```
=== Alpha Update Agent - Single Run Mode ===
Current version: 1.0.0
Checking for updates at https://example.com/updates.json
...
```

## Step 3: Test Updates Locally (3 minutes)

### Terminal 1: Create and serve updates

```bash
cd server_example

# Create update packages
python create_update_package.py

# Start local test server
python test_server.py
```

### Terminal 2: Configure and test agent

```bash
# Edit config.json and change update_server to:
# "update_server": "http://localhost:8000/updates.json"

# Check for updates
python main.py check
```

You should see the agent download and apply the update from 1.0.0 → 1.0.1!

## Step 4: Verify Update Worked

```bash
python main.py version
# Should now show: Alpha Update Agent v1.0.1
```

## Step 5: Enable Modules (optional)

Edit `config.json`:
```json
{
    "modules_enabled": ["gpu_share.py", "disk_share.py"]
}
```

Run the agent:
```bash
python main.py once
```

You should see the modules loading and executing!

## 🎉 Success!

You now have a working self-updating agent. Next steps:

1. **Read the full README.md** for detailed documentation
2. **Create custom modules** for your use case
3. **Deploy to production** with a real update server
4. **Run as a service** for continuous operation
5. **Connect multiple agents** - See DEMO_DISTRIBUTED.md
6. **Deploy coordination server** - See DEPLOY_NOW.md for hosting options

## Common Issues

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### "Connection error" when checking updates
- Make sure test_server.py is running
- Verify config.json has correct URL
- Check firewall isn't blocking port 8000

### Port 8000 already in use
- Kill the process using port 8000
- Or edit test_server.py to use a different PORT

---

**Need help?** Check README.md or the troubleshooting section.

