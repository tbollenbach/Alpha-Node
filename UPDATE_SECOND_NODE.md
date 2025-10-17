# 🚀 Update Second Node to v2.0.0

## Quick Update Guide

### Option 1: Automatic Update (Recommended)

**On your second node, run:**

```bash
# 1. Set the coordinator URL
export COORDINATOR_URL=https://alpha-node.onrender.com

# 2. Run the agent - it will auto-update
python main.py run
```

The agent will automatically:
- ✅ Check for updates from the server
- ✅ Download v2.0.0 with resource pooling
- ✅ Install the update
- ✅ Restart with new features

### Option 2: Manual Update

**If automatic update fails:**

```bash
# 1. Pull latest code from GitHub
git pull origin main

# 2. Install new dependencies
pip install -r requirements.txt

# 3. Update config to enable resource pooling
# Edit config.json:
{
    "version": "2.0.0",
    "update_server": "https://alpha-node.onrender.com/updates.json",
    "check_interval": 3600,
    "auto_update": true,
    "modules_enabled": ["simple_coordinator.py", "resource_pool.py"],
    "backup_count": 3,
    "log_file": "agent.log"
}

# 4. Run with environment variable
export COORDINATOR_URL=https://alpha-node.onrender.com
python main.py run
```

## 🎯 What's New in v2.0.0

### ✨ New Features:
- **💻 Hardware Resource Pooling** - CPU, memory, storage, GPU monitoring
- **📊 Enhanced Dashboard** - Real-time resource statistics
- **🔄 Improved Coordination** - Better agent registration and heartbeat
- **📈 Resource Analytics** - Per-agent hardware details

### 📊 Dashboard Features:
- **Total Pooled Resources** - Combined CPU cores, memory, storage
- **Per-Agent Details** - Individual hardware specs and usage
- **Real-time Updates** - Live monitoring every 5 seconds
- **GPU Detection** - Automatic NVIDIA/AMD GPU detection

## 🌐 View Your Enhanced Dashboard

**Open:** https://alpha-node.onrender.com

You'll see:
- ✅ **8 Stat Cards** - Agents, tasks, and pooled resources
- ✅ **4 Information Panels** - Agents, tasks, hardware, summary
- ✅ **Real-time Updates** - Auto-refresh every 5 seconds
- ✅ **Resource Pooling** - Combined hardware from all nodes

## 🔧 Troubleshooting

### If the agent doesn't connect:
```bash
# Check environment variable
echo $COORDINATOR_URL

# Should show: https://alpha-node.onrender.com
```

### If update fails:
```bash
# Check server status
curl https://alpha-node.onrender.com/api/status

# Should return: {"status": "online"}
```

### If resource pooling doesn't work:
```bash
# Check if modules are enabled
cat config.json | grep modules_enabled

# Should include: "resource_pool.py"
```

## 🎉 Success Indicators

After updating, you should see:
- ✅ Agent connects to dashboard
- ✅ Resource data appears in dashboard
- ✅ Hardware stats show in real-time
- ✅ Multiple nodes pool resources together

**Your distributed system now has comprehensive hardware resource pooling!** 🎯
