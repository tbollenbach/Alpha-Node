# Deploy Your Coordination Server in 10 Minutes

Pick one option and follow the steps:

---

## Option A: Render.com (Easiest - No Command Line)

**Total Time: 5 minutes**

### Step 1: Create GitHub Account (if you don't have one)
Go to https://github.com/signup

### Step 2: Upload Your Code to GitHub

**Via GitHub Website (No Git Required):**

1. Go to https://github.com/new
2. Repository name: `alpha-coordinator`
3. Click "Create repository"
4. Click "uploading an existing file"
5. Drag and drop these folders/files:
   - `coordinator_server/` (entire folder)
   - `.gitignore`
6. Click "Commit changes"

**OR Via Command Line:**
```bash
cd C:\Users\travi\Desktop\seed
git init
git add .
git commit -m "Initial commit"
git branch -M main
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/alpha-coordinator.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub
4. Click "New +" → "Web Service"
5. Click "Connect" next to your `alpha-coordinator` repo
6. Fill in:
   - **Name:** `alpha-coordinator`
   - **Environment:** `Python 3`
   - **Build Command:** `cd coordinator_server && pip install -r requirements.txt`
   - **Start Command:** `cd coordinator_server && gunicorn -w 4 -b 0.0.0.0:$PORT simple_server:app`
7. Click "Create Web Service"

### Step 4: Wait for Deployment (2-3 minutes)

Watch the logs. When you see:
```
==> Your service is live 🎉
```

### Step 5: Get Your URL

Render shows your URL: `https://alpha-coordinator.onrender.com`

### Step 6: Test It

Open in browser: `https://alpha-coordinator.onrender.com`

You should see the coordinator dashboard!

### Step 7: Connect Agents

On any computer with your agent:

```bash
# Windows PowerShell:
$env:COORDINATOR_URL="https://alpha-coordinator.onrender.com"

# Linux/macOS:
export COORDINATOR_URL=https://alpha-coordinator.onrender.com

# Edit config.json:
# "modules_enabled": ["simple_coordinator.py"]

# Run agent:
python main.py run
```

**DONE!** Your agent is now connected to the cloud server! 🎉

---

## Option B: Railway.app (Super Fast)

**Total Time: 3 minutes**

### Step 1: Install Railway CLI

```bash
# Windows PowerShell (Run as Administrator):
iwr https://railway.app/install.ps1 -useb | iex

# Or download from: https://railway.app/
```

### Step 2: Login

```bash
railway login
```

Browser opens → Sign up with GitHub → Authorize

### Step 3: Deploy

```bash
cd C:\Users\travi\Desktop\seed\coordinator_server
railway init
# Name your project: alpha-coordinator
railway up
```

### Step 4: Add Domain

```bash
railway domain
```

Returns: `https://alpha-coordinator-production.up.railway.app`

### Step 5: Connect Agents

```bash
export COORDINATOR_URL=https://alpha-coordinator-production.up.railway.app
python main.py run
```

**DONE!** ✅

---

## Option C: DigitalOcean ($6/month - Most Reliable)

**Total Time: 10 minutes**

### Step 1: Create Account

1. Go to https://www.digitalocean.com
2. Sign up (get $200 free credit with some links)
3. Add payment method

### Step 2: Create Droplet

1. Click "Create" → "Droplets"
2. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic → $6/month
   - **Datacenter:** Closest to you
   - **Authentication:** Password (set a strong one)
3. Click "Create Droplet"
4. Wait 1 minute for IP address

### Step 3: Connect to Server

```bash
# You'll get an IP like: 142.93.123.45
ssh root@YOUR_DROPLET_IP
# Enter password when prompted
```

### Step 4: Setup Server

```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3 python3-pip -y
pip3 install flask gunicorn
```

### Step 5: Upload Your Server Files

**On your local machine (new terminal):**

```bash
cd C:\Users\travi\Desktop\seed
scp -r coordinator_server root@YOUR_DROPLET_IP:~/
```

### Step 6: Run Server

**Back on the droplet:**

```bash
cd coordinator_server
gunicorn -w 4 -b 0.0.0.0:5000 simple_server:app &
```

### Step 7: Open Firewall

```bash
ufw allow 5000/tcp
ufw allow 22/tcp
ufw --force enable
```

### Step 8: Test

Open in browser: `http://YOUR_DROPLET_IP:5000`

### Step 9: Connect Agents

```bash
export COORDINATOR_URL=http://YOUR_DROPLET_IP:5000
python main.py run
```

### Step 10: Make It Permanent (Optional)

Create systemd service so it runs on boot:

```bash
cat > /etc/systemd/system/alpha-coordinator.service << EOF
[Unit]
Description=Alpha Coordination Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/coordinator_server
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 simple_server:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable alpha-coordinator
systemctl start alpha-coordinator
systemctl status alpha-coordinator
```

**DONE!** Server runs 24/7 now! ✅

---

## Testing Your Deployment

### Test 1: Check Dashboard

Open browser: `YOUR_URL`

Should see:
```
🌐 Alpha Update Agent - Coordination Server
📊 System Status
```

### Test 2: Check API

```bash
curl YOUR_URL/api/status
```

Should return:
```json
{
  "total_agents": 0,
  "online_agents": 0,
  "pending_tasks": 0,
  "completed_tasks": 0
}
```

### Test 3: Connect an Agent

```bash
export COORDINATOR_URL=YOUR_URL
python main.py run
```

In agent logs, you should see:
```
✓ Registered with coordinator at YOUR_URL
```

Refresh dashboard → Should show 1 agent online!

### Test 4: Submit Tasks

```bash
curl -X POST YOUR_URL/api/tasks/create-test
```

Agent should execute tasks and you'll see results in dashboard!

---

## Troubleshooting

### "Connection refused"
- Server not running
- Firewall blocking port
- Wrong URL/IP

**Fix:**
```bash
# Check if server is running:
# On server: netstat -tulpn | grep 5000

# Check firewall:
# On server: ufw status
```

### "502 Bad Gateway" (Render/Railway)
- Server starting up (wait 30 seconds)
- Check logs in dashboard

### Agent can't connect
- Check COORDINATOR_URL is correct
- Test URL in browser first
- Check agent has internet connection

---

## Quick Reference

| Platform | URL Format | Example |
|----------|-----------|---------|
| Render | `https://APP_NAME.onrender.com` | `https://alpha-coordinator.onrender.com` |
| Railway | `https://APP_NAME.up.railway.app` | `https://alpha-coordinator-production.up.railway.app` |
| Fly.io | `https://APP_NAME.fly.dev` | `https://alpha-coordinator.fly.dev` |
| DigitalOcean | `http://YOUR_IP:5000` | `http://142.93.123.45:5000` |
| AWS EC2 | `http://ec2-XX-XX-XX-XX.compute.amazonaws.com:5000` | `http://ec2-12-34-56-78.us-west-2.compute.amazonaws.com:5000` |

---

## What's Next?

✅ Server deployed
✅ Agents can connect

Now you can:

1. **Add more agents** - Install on other computers, all point to same URL
2. **Test from different networks** - Home, office, cloud
3. **Add authentication** - Secure your server
4. **Enable HTTPS** - For production use
5. **Scale up** - Add more server resources as needed

## Need Help?

- Check server logs for errors
- Verify agents have correct URL
- Test URL in browser first
- Make sure ports are open

**Your coordination server is now live!** 🚀

