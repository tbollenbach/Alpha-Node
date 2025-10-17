# Alpha Update Agent

A lightweight, cross-platform self-updating agent that checks for updates from a remote server, downloads and verifies them, applies them safely, and can evolve over time.

## 🎯 Features

- **Automatic Updates**: Checks remote server for new versions and updates automatically
- **Integrity Verification**: Uses SHA256 checksums to verify update authenticity
- **Safe Rollback**: Automatic rollback if updates fail
- **Modular Architecture**: Dynamically load/unload feature modules
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Secure**: HTTPS downloads, checksum verification, future-ready for authentication
- **Multiple Run Modes**: Continuous, single-run, or check-only modes

## 📁 Project Structure

```
seed/
├── main.py                 # Entry point
├── updater.py              # Update logic and management
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── agent.log              # Application logs (generated)
├── modules/               # Optional feature modules
│   ├── __init__.py
│   ├── gpu_share.py       # GPU compute sharing
│   ├── disk_share.py      # Distributed storage
│   └── network_bridge.py  # Network tunneling
├── backups/               # Automatic backups (generated)
└── server_example/        # Test server files
    ├── test_server.py     # Local test server
    ├── create_update_package.py
    ├── updates.json       # Update manifest
    └── updates/           # Update packages (generated)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install Python 3.10 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.json` to customize settings:

```json
{
    "version": "1.0.0",
    "update_server": "https://example.com/updates.json",
    "check_interval": 3600,
    "auto_update": true,
    "modules_enabled": [],
    "backup_count": 3,
    "log_file": "agent.log"
}
```

**Configuration Options:**

- `version`: Current version of the agent
- `update_server`: URL to the update manifest JSON file
- `check_interval`: Seconds between update checks (default: 3600 = 1 hour)
- `auto_update`: Enable/disable automatic updates
- `modules_enabled`: List of modules to load (e.g., `["gpu_share.py"]`)
- `backup_count`: Number of backups to keep
- `log_file`: Path to log file

### 3. Running the Agent

```bash
# Run continuously (checks for updates every hour)
python main.py run

# Run once and exit
python main.py once

# Check for updates only
python main.py check

# Show version
python main.py version

# Show help
python main.py help
```

## 🧪 Testing Locally

### Step 1: Create Update Packages

```bash
cd server_example
python create_update_package.py
```

This creates:
- `updates/1.0.1.zip` - First update package
- `updates/1.0.2.zip` - Second update package
- Updates `updates.json` with correct checksums

### Step 2: Start Test Server

```bash
python test_server.py
```

The server will run on `http://localhost:8000`

### Step 3: Configure Agent

Update your `config.json`:

```json
{
    "version": "1.0.0",
    "update_server": "http://localhost:8000/updates.json",
    "check_interval": 60,
    "auto_update": true,
    "modules_enabled": []
}
```

### Step 4: Test Update

```bash
# Check for and apply updates
python main.py check

# You should see output like:
# INFO - Checking for updates...
# INFO - Current: 1.0.0, Remote: 1.0.1
# INFO - Update available: 1.0.1
# INFO - Downloading update...
# INFO - Verifying update integrity...
# INFO - Creating backup...
# INFO - Applying update...
# INFO - Successfully updated to version 1.0.1
```

### Step 5: Verify Update

```bash
python main.py version
# Should show: Alpha Update Agent v1.0.1
```

## 📦 Update Package Format

### Update Manifest (updates.json)

```json
{
    "version": "1.0.1",
    "modules": ["gpu_share.py", "disk_share.py"],
    "url": "https://example.com/updates/1.0.1.zip",
    "checksum": "sha256_hash_of_zip_file",
    "release_date": "2025-10-16",
    "changelog": [
        "Added GPU sharing module",
        "Improved stability"
    ],
    "required": false,
    "min_version": "1.0.0"
}
```

### Update Package Structure

The ZIP file should contain:

```
1.0.1.zip
├── modules/
│   ├── __init__.py
│   ├── gpu_share.py
│   └── disk_share.py
└── (optional) main.py, updater.py, etc.
```

## 🔧 Creating Modules

Modules are Python files in the `modules/` directory. Each module should implement:

```python
def init():
    """Called when module is loaded"""
    pass

def tick():
    """Called periodically in continuous mode"""
    pass

def run():
    """Called once in single-run mode"""
    pass

def cleanup():
    """Called when module is unloaded"""
    pass
```

Example module structure:

```python
"""
My Custom Module
Description of what this module does.
"""

import logging

logger = None
enabled = False

def init():
    global logger, enabled
    logger = logging.getLogger('my_module')
    logger.info("My module initializing...")
    # Setup code here
    enabled = True

def tick():
    if not enabled:
        return
    # Periodic tasks here
    logger.debug("Tick")

def run():
    if not enabled:
        return
    # One-time tasks here
    logger.info("Running task")

def cleanup():
    global enabled
    logger.info("Cleaning up...")
    # Cleanup code here
    enabled = False

__version__ = "1.0.0"
__description__ = "My custom module"
```

## 🔐 Security Features

### Current Implementation

- ✅ HTTPS support for secure downloads
- ✅ SHA256 checksum verification
- ✅ Automatic rollback on failed updates
- ✅ Backup system for safe recovery
- ✅ Signed packages (checksum-based)

### Future Enhancements

- 🔄 RSA/GPG signature verification
- 🔄 Authentication tokens for update server
- 🔄 Encrypted update packages
- 🔄 Certificate pinning
- 🔄 Rate limiting and retry logic

## 🛠️ Advanced Usage

### Custom Update Server

Deploy your own update server:

1. Host `updates.json` on your server
2. Host update packages in a `/updates/` directory
3. Update `config.json` with your server URL
4. Ensure HTTPS is enabled

### Running as a Service

#### Linux (systemd)

Create `/etc/systemd/system/alpha-agent.service`:

```ini
[Unit]
Description=Alpha Update Agent
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/seed
ExecStart=/usr/bin/python3 /path/to/seed/main.py run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable alpha-agent
sudo systemctl start alpha-agent
sudo systemctl status alpha-agent
```

#### Windows (NSSM)

1. Download NSSM (Non-Sucking Service Manager)
2. Install as service:
```cmd
nssm install AlphaAgent "C:\Python310\python.exe" "C:\path\to\seed\main.py run"
nssm start AlphaAgent
```

#### macOS (launchd)

Create `~/Library/LaunchAgents/com.alpha.agent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.alpha.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/seed/main.py</string>
        <string>run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.alpha.agent.plist
```

### System Tray App (Future Enhancement)

The agent can be extended with a GUI using:
- **PyQt6** or **PySide6** for cross-platform GUI
- **pystray** for system tray icon
- **Tkinter** for simple dialogs

Example structure:
```python
import pystray
from PIL import Image
# ... create icon, menu, and tray app
```

## 📊 Logging

Logs are written to `agent.log` (configurable in `config.json`).

Log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Warning messages
- **ERROR**: Error messages

View logs in real-time:
```bash
# Linux/macOS
tail -f agent.log

# Windows (PowerShell)
Get-Content agent.log -Wait
```

## 🔄 Rollback

If an update fails, the system automatically rolls back to the previous version.

Manual rollback:
```python
from updater import Updater
updater = Updater()
backup_path = Path("backups/backup_1.0.0_...")
updater.rollback(backup_path)
```

## 🐛 Troubleshooting

### Update Check Fails

```
ERROR - Failed to check for updates: Connection error
```

**Solutions:**
- Check internet connection
- Verify update_server URL in config.json
- Check firewall settings
- Verify server is accessible

### Checksum Verification Fails

```
ERROR - Checksum mismatch!
```

**Solutions:**
- Corrupted download - retry
- Update package was modified - security risk!
- Regenerate update package with correct checksum

### Module Won't Load

```
ERROR - Failed to load module gpu_share: ModuleNotFoundError
```

**Solutions:**
- Verify module file exists in `modules/` directory
- Check module filename in `modules_enabled` config
- Check module for syntax errors

### Permission Denied

```
ERROR - PermissionError: [Errno 13] Permission denied
```

**Solutions:**
- Run with appropriate permissions
- Check file/directory ownership
- On Linux/macOS: may need `chmod +x main.py`

## 🚦 Development Roadmap

### Phase 1: MVP ✅
- [x] Basic update checking
- [x] Download and apply updates
- [x] Checksum verification
- [x] Rollback mechanism
- [x] Module loading system

### Phase 2: Enhanced Security 🔄
- [ ] GPG signature verification
- [ ] Authentication tokens
- [ ] Encrypted updates
- [ ] Rate limiting

### Phase 3: Hardware Features 🔄
- [ ] GPU compute sharing (CUDA/OpenCL)
- [ ] Network bridging/tunneling
- [ ] Distributed storage
- [ ] CPU task distribution

### Phase 4: Advanced Features 🔄
- [ ] WebSocket/MQTT for real-time commands
- [ ] Web dashboard for monitoring
- [ ] System tray GUI
- [ ] Multi-node coordination
- [ ] Resource scheduling

## 📝 Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues or questions:
- Check the troubleshooting section
- Review logs in `agent.log`
- Open an issue on the project repository

## 🎓 Example Use Cases

### Distributed Computing Network
Deploy agents across multiple machines for distributed computing tasks.

### IoT Device Management
Remotely update and manage IoT devices with new features.

### Edge Computing
Deploy compute tasks to edge devices dynamically.

### Resource Sharing Network
Create a network of machines sharing GPU, storage, or bandwidth.

### Automated Testing
Deploy test agents that self-update with new test scenarios.

---

**Built with ❤️ for the future of distributed systems**

