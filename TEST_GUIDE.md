# Testing Guide for Alpha Update Agent

This guide walks you through comprehensive testing of all features.

## Prerequisites

```bash
# Install dependencies
pip install requests
```

## Test 1: Basic Functionality

### 1.1 Version Check
```bash
python main.py version
```
**Expected Output:**
```
Alpha Update Agent v1.0.0
```

### 1.2 Help Command
```bash
python main.py help
```
**Expected Output:** Help text showing all commands

### 1.3 Single Run (No Updates)
```bash
python main.py once
```
**Expected Output:**
```
=== Alpha Update Agent - Single Run Mode ===
Current version: 1.0.0
Checking for updates...
Failed to check for updates: Connection error
```
(This is expected since the server isn't configured yet)

## Test 2: Module System

### 2.1 Enable Modules

Edit `config.json`:
```json
{
    "version": "1.0.0",
    "update_server": "https://example.com/updates.json",
    "check_interval": 3600,
    "auto_update": true,
    "modules_enabled": ["gpu_share.py", "disk_share.py", "network_bridge.py"],
    "backup_count": 3,
    "log_file": "agent.log"
}
```

### 2.2 Run with Modules
```bash
python main.py once
```

**Expected Output:**
```
Loading module: gpu_share
Module gpu_share initialized
Loading module: disk_share
Module disk_share initialized
Loading module: network_bridge
Module network_bridge initialized
Running module: gpu_share
GPU Share: Running single execution task
...
```

### 2.3 Check Logs
```bash
# Windows PowerShell
Get-Content agent.log

# Linux/macOS
cat agent.log
```

**Expected:** Detailed logs of module initialization and execution

## Test 3: Update System (Local)

### 3.1 Create Update Packages

```bash
cd server_example
python create_update_package.py
```

**Expected Output:**
```
Creating update package for version 1.0.1
...
Package created successfully!
SHA256: <checksum>
...
Creating update package for version 1.0.2
...
```

**Verify Files Created:**
```bash
# Should exist:
# server_example/updates/1.0.1.zip
# server_example/updates/1.0.2.zip
```

### 3.2 Start Test Server

In Terminal 1:
```bash
cd server_example
python test_server.py
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║           Alpha Update Agent - Test Update Server           ║
╚══════════════════════════════════════════════════════════════╝

Server URL: http://localhost:8000/
...
Server started on port 8000
```

### 3.3 Configure Agent for Local Server

In Terminal 2, edit `config.json`:
```json
{
    "version": "1.0.0",
    "update_server": "http://localhost:8000/updates.json",
    "check_interval": 60,
    "auto_update": true,
    "modules_enabled": [],
    "backup_count": 3,
    "log_file": "agent.log"
}
```

### 3.4 Test Update Check

```bash
python main.py check
```

**Expected Output:**
```
Checking for updates...
Current: 1.0.0, Remote: 1.0.1
Update available: 1.0.1
Downloading update from http://localhost:8000/updates/1.0.1.zip
Download complete: <temp_file>
Verifying update integrity...
Checksum verification passed
Creating backup: <backup_path>
Backup created successfully
Applying update...
Update to version 1.0.1 completed successfully
Successfully updated to version 1.0.1
Update applied! Please restart the agent.
```

**Verify in Terminal 1:** Should see HTTP requests logged

### 3.5 Verify Update Applied

```bash
python main.py version
```

**Expected Output:**
```
Alpha Update Agent v1.0.1
```

**Check Backup Created:**
```bash
# Windows PowerShell
dir backups

# Linux/macOS
ls -la backups/
```

Should see a backup directory created.

## Test 4: Second Update

### 4.1 Configure for Version 1.0.2

With test server still running, edit `server_example/updates.json` or change config:
```json
{
    "update_server": "http://localhost:8000/updates_1.0.2.json"
}
```

### 4.2 Apply Second Update

```bash
python main.py check
```

**Expected:** Update from 1.0.1 → 1.0.2

### 4.3 Verify

```bash
python main.py version
# Should show: v1.0.2
```

## Test 5: Module Loading After Update

### 5.1 Enable Modules

Edit `config.json`:
```json
{
    "modules_enabled": ["gpu_share.py", "disk_share.py", "network_bridge.py"]
}
```

### 5.2 Run Agent

```bash
python main.py once
```

**Expected:** All three modules should load and run successfully

## Test 6: Continuous Mode

### 6.1 Run Continuously

```bash
python main.py run
```

**Expected Output:**
```
=== Alpha Update Agent Starting ===
Current version: 1.0.2
Loading module: gpu_share
...
```

Agent will run continuously, checking for updates every 60 seconds (as configured).

### 6.2 Test Graceful Shutdown

Press `Ctrl+C`

**Expected Output:**
```
Keyboard interrupt received
GPU Share module shutting down...
=== Alpha Update Agent Stopped ===
```

## Test 7: Rollback Mechanism

### 7.1 Simulate Failed Update

Create a corrupt update package:
```bash
cd server_example/updates
echo "corrupt" > test_corrupt.zip
```

### 7.2 Update manifest with corrupt package:
```json
{
    "version": "1.0.3",
    "url": "http://localhost:8000/updates/test_corrupt.zip",
    "checksum": "invalid_checksum_here"
}
```

### 7.3 Attempt Update
```bash
python main.py check
```

**Expected:** Should fail verification and NOT apply update

## Test 8: Error Handling

### 8.1 Test with Server Down

Stop the test server (Ctrl+C in Terminal 1)

```bash
python main.py check
```

**Expected Output:**
```
Checking for updates...
Failed to check for updates: Connection error
No updates available
```

### 8.2 Test Invalid Config

Rename config.json temporarily:
```bash
python main.py once
```

**Expected:** Error about missing configuration file

## Test 9: Logging

### 9.1 Generate Activity

```bash
python main.py once
python main.py check
python main.py version
```

### 9.2 Review Logs

```bash
# View full log
cat agent.log  # or Get-Content agent.log on Windows

# Tail log in real-time (Linux/macOS)
tail -f agent.log

# PowerShell (Windows)
Get-Content agent.log -Wait
```

**Expected:** Comprehensive logs of all operations

## Test 10: Edge Cases

### 10.1 Already Up-to-Date

With version 1.0.2 installed:
```bash
python main.py check
```

**Expected:**
```
Already up to date
No updates available
```

### 10.2 Downgrade Protection

Try to "update" to an older version by changing updates.json to version 1.0.0

**Expected:** Should not apply the "update" (older version)

### 10.3 Invalid Module

Edit config.json:
```json
{
    "modules_enabled": ["nonexistent_module.py"]
}
```

Run:
```bash
python main.py once
```

**Expected:** Error logged, but agent continues running

## Success Criteria

✅ All commands run without crashes
✅ Updates download and apply correctly
✅ Checksums verify properly
✅ Backups are created before updates
✅ Modules load and execute
✅ Logging captures all events
✅ Graceful shutdown works
✅ Error handling prevents crashes

## Troubleshooting Test Issues

### "Module not found: requests"
```bash
pip install requests
```

### "Port 8000 already in use"
Edit `server_example/test_server.py` and change `PORT = 8000` to another port

### "Permission denied"
- Run with appropriate permissions
- Check file ownership
- On Windows: Run as Administrator if needed

### Logs not showing expected output
- Check `agent.log` file directly
- Increase logging level in code if needed
- Verify config.json is correct

## Clean Up After Testing

```bash
# Remove backups
rm -rf backups/  # or rmdir /s backups on Windows

# Remove logs
rm agent.log  # or del agent.log on Windows

# Reset version
# Edit config.json back to version 1.0.0

# Remove generated update packages
rm -rf server_example/updates/  # or rmdir /s server_example\updates
```

## Performance Testing

### Test Update Speed

Time the update process:
```bash
# Linux/macOS
time python main.py check

# Windows PowerShell
Measure-Command { python main.py check }
```

**Expected:** Should complete in a few seconds for small packages

### Test Module Load Time

```bash
# With 3 modules enabled
time python main.py once
```

**Expected:** <1 second for module loading and execution

## Security Testing

### Test HTTPS (Production)

Change config to use HTTPS URL and verify connection works

### Test Checksum Verification

1. Create update package
2. Manually change one byte in the ZIP file
3. Attempt update
4. Should fail verification

### Test Backup/Rollback

1. Create backup manually
2. Delete main.py
3. Run rollback (via Python shell)
4. Verify main.py is restored

---

**After completing these tests, your Alpha Update Agent is production-ready!**

