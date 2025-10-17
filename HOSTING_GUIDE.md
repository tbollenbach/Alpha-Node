# Where to Host the Coordination Server

You need a server with a **public IP or domain name** that agents can reach from anywhere. Here are your options:

---

## 🎯 Quick Comparison

| Option | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **Render.com** | Free | ⭐ Easiest | Testing & small projects |
| **Railway.app** | Free tier | ⭐ Easy | Quick deployment |
| **Fly.io** | Free tier | ⭐⭐ Easy | Global deployment |
| **Heroku** | Free tier removed | ⭐ Easy | Was popular (now paid) |
| **DigitalOcean** | $6/month | ⭐⭐ Medium | Production, full control |
| **AWS EC2** | ~$5-10/month | ⭐⭐⭐ Complex | Enterprise scale |
| **Home Server** | Free | ⭐⭐⭐⭐ Hard | If you have public IP |

---

## Option 1: Render.com (RECOMMENDED - Easiest & Free)

### ✅ Pros
- **Completely free** tier
- Auto-deploy from GitHub
- HTTPS included
- No credit card required
- Easy setup (5 minutes)

### 📝 Step-by-Step Setup

**1. Prepare Your Files**

Create `requirements.txt` in `coordinator_server/`:
```txt
flask==3.0.0
gunicorn==21.2.0
```

Create `render.yaml` in project root:
```yaml
services:
  - type: web
    name: alpha-coordinator
    env: python
    buildCommand: pip install -r coordinator_server/requirements.txt
    startCommand: cd coordinator_server && gunicorn -w 4 -b 0.0.0.0:$PORT simple_server:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
```

**2. Push to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/alpha-agent.git
git push -u origin main
```

**3. Deploy on Render**

1. Go to https://render.com (sign up free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Render auto-detects settings
5. Click "Create Web Service"

**4. Get Your URL**

Render gives you: `https://alpha-coordinator.onrender.com`

**5. Use on Agents**

```bash
# On any agent, anywhere:
export COORDINATOR_URL=https://alpha-coordinator.onrender.com
python main.py run
```

**Done!** ✅

### ⚠️ Free Tier Limitations
- Sleeps after 15 min inactivity (wakes on request)
- 750 hours/month free

---

## Option 2: Railway.app (Also Great & Free)

### 📝 Setup

**1. Install Railway CLI**
```bash
npm install -g @railway/cli
```

**2. Deploy**
```bash
cd coordinator_server
railway login
railway init
railway up
```

**3. Get URL**
```bash
railway domain
# Returns: https://your-app.up.railway.app
```

### Free Tier
- $5 free credit/month
- No credit card required initially

---

## Option 3: Fly.io (Global Edge Network)

### 📝 Setup

**1. Install Fly CLI**
```bash
# Windows (PowerShell):
iwr https://fly.io/install.ps1 -useb | iex

# Linux/macOS:
curl -L https://fly.io/install.sh | sh
```

**2. Create fly.toml**
```toml
app = "alpha-coordinator"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  http_checks = []
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

**3. Deploy**
```bash
cd coordinator_server
fly auth login
fly launch
fly deploy
```

**4. Get URL**
```bash
fly info
# Returns: https://alpha-coordinator.fly.dev
```

### Free Tier
- 3 shared-cpu VMs free
- 160GB bandwidth/month

---

## Option 4: DigitalOcean Droplet (Full Control)

### 💰 Cost: $6/month (cheapest droplet)

### 📝 Setup

**1. Create Droplet**
1. Go to digitalocean.com
2. Create → Droplets
3. Choose: Ubuntu 22.04
4. Plan: Basic $6/month
5. Add SSH key
6. Create

**2. Connect**
```bash
ssh root@YOUR_DROPLET_IP
```

**3. Install Requirements**
```bash
apt update
apt install python3 python3-pip -y
pip3 install flask gunicorn
```

**4. Upload Server Files**
```bash
# From your computer:
scp -r coordinator_server root@YOUR_DROPLET_IP:~/
```

**5. Run Server**
```bash
# On droplet:
cd coordinator_server
gunicorn -w 4 -b 0.0.0.0:5000 simple_server:app
```

**6. Setup as Service (Auto-start)**

Create `/etc/systemd/system/alpha-coordinator.service`:
```ini
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
```

Enable it:
```bash
systemctl enable alpha-coordinator
systemctl start alpha-coordinator
systemctl status alpha-coordinator
```

**7. Setup Firewall**
```bash
ufw allow 5000/tcp
ufw allow 22/tcp  # SSH
ufw enable
```

**8. Use Your Server**
```bash
export COORDINATOR_URL=http://YOUR_DROPLET_IP:5000
python main.py run
```

### 🔒 Add HTTPS (Recommended)

**1. Install Nginx + Certbot**
```bash
apt install nginx certbot python3-certbot-nginx -y
```

**2. Setup Domain** (e.g., coordinator.yourdomain.com)
- Point A record to your droplet IP

**3. Configure Nginx**

Create `/etc/nginx/sites-available/alpha-coordinator`:
```nginx
server {
    listen 80;
    server_name coordinator.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/alpha-coordinator /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**4. Get SSL Certificate**
```bash
certbot --nginx -d coordinator.yourdomain.com
```

**5. Use HTTPS**
```bash
export COORDINATOR_URL=https://coordinator.yourdomain.com
python main.py run
```

---

## Option 5: AWS EC2 (Enterprise Scale)

### 💰 Cost: ~$3-10/month (t2.micro is free tier eligible for 1 year)

### 📝 Quick Setup

1. **Launch EC2 Instance**
   - Ubuntu 22.04
   - t2.micro (free tier)
   - Allow HTTP (80), HTTPS (443), Custom TCP (5000)

2. **Connect & Setup**
   ```bash
   ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com
   sudo apt update
   sudo apt install python3 python3-pip -y
   pip3 install flask gunicorn
   ```

3. **Upload & Run**
   Same as DigitalOcean steps above

4. **Get Public DNS**
   AWS gives you: `ec2-12-34-56-78.us-west-2.compute.amazonaws.com`

---

## Option 6: Home Server (Advanced)

### ⚠️ Only if you have:
- Static public IP or dynamic DNS
- Router access to forward ports
- 24/7 uptime

### 📝 Setup

**1. Forward Port on Router**
- Login to router (usually 192.168.1.1)
- Port forwarding: External 5000 → Internal YOUR_PC_IP:5000

**2. Get Public IP**
```bash
curl ifconfig.me
# Returns: 98.123.45.67
```

**3. Setup Dynamic DNS** (if IP changes)
- Use: No-IP.com, DuckDNS.org, or Cloudflare
- Get domain: `yourname.ddns.net`

**4. Run Server**
```bash
cd coordinator_server
python simple_server.py
```

**5. Use It**
```bash
export COORDINATOR_URL=http://98.123.45.67:5000
# Or with dynamic DNS:
export COORDINATOR_URL=http://yourname.ddns.net:5000
```

---

## 🎯 My Recommendation

### For Testing (Right Now)
**Use Render.com** - Free, easy, 5 minutes to deploy

### For Production (Long-term)
**Use DigitalOcean** - $6/month, full control, reliable

### For Enterprise (Scale)
**Use AWS/Azure** - Auto-scaling, global regions

---

## Quick Start: Deploy to Render.com Now

**1. Install Git (if not installed)**
```bash
# Check if installed:
git --version

# If not, download from: https://git-scm.com/
```

**2. Prepare Files**

I'll create the needed files for you:

