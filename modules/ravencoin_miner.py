"""
Ravencoin Mining Module
Coordinates distributed Ravencoin (RVN) mining across connected agents.
Uses kawpow mining algorithm via popular mining software.
"""

import logging
import subprocess
import platform
import os
import time
import requests
import hashlib
import socket
import uuid
from pathlib import Path
import json

# Module state
logger = None
agent_id = None
coordinator_url = None
miner_process = None
mining_active = False
last_report = 0

# Mining configuration
MINING_CONFIG = {
    'pool_url': os.getenv('RVN_POOL_URL', 'stratum+tcp://rvn.2miners.com:6060'),
    'wallet_address': os.getenv('RVN_WALLET', ''),  # User must provide
    'worker_name': None,  # Will be set to agent_id
    'intensity': os.getenv('RVN_INTENSITY', 'auto'),
    'gpu_enabled': True,
    'cpu_enabled': False,  # Ravencoin is GPU-optimized
}

def init():
    """Initialize Ravencoin mining module."""
    global logger, agent_id, coordinator_url, MINING_CONFIG
    
    logger = logging.getLogger('ravencoin_miner')
    
    # Generate unique agent ID
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())[2:]
    agent_id = f"{hostname}_{hashlib.md5(mac.encode()).hexdigest()[:8]}"
    
    # Set worker name
    MINING_CONFIG['worker_name'] = agent_id
    
    # Get coordinator URL
    coordinator_url = os.getenv('COORDINATOR_URL', 'http://localhost:5000')
    
    logger.info(f"Ravencoin mining module initializing for agent: {agent_id}")
    
    # Check wallet address
    if not MINING_CONFIG['wallet_address']:
        logger.warning("RVN_WALLET not set! Mining will not start until wallet address is configured.")
        logger.info("Set your Ravencoin wallet address: export RVN_WALLET=your_wallet_address")
        return
    
    # Check for GPU
    gpu_info = check_gpu()
    if not gpu_info['available']:
        logger.warning("No GPU detected. Ravencoin mining requires a GPU for optimal performance.")
        return
    
    logger.info(f"GPU detected: {gpu_info['vendor']} - {gpu_info['count']} device(s)")
    logger.info(f"Pool: {MINING_CONFIG['pool_url']}")
    logger.info(f"Wallet: {MINING_CONFIG['wallet_address'][:10]}...{MINING_CONFIG['wallet_address'][-10:]}")
    logger.info(f"Worker: {MINING_CONFIG['worker_name']}")

def check_gpu():
    """Check for GPU availability and type."""
    gpu_info = {
        'available': False,
        'vendor': None,
        'count': 0,
        'devices': []
    }
    
    try:
        # Check for NVIDIA GPU
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            gpu_info['available'] = True
            gpu_info['vendor'] = 'NVIDIA'
            gpu_info['devices'] = result.stdout.strip().split('\n')
            gpu_info['count'] = len(gpu_info['devices'])
            return gpu_info
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        # Check for AMD GPU
        result = subprocess.run(
            ['rocm-smi', '--showproductname'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'GPU' in result.stdout:
            gpu_info['available'] = True
            gpu_info['vendor'] = 'AMD'
            gpu_info['count'] = result.stdout.count('GPU')
            return gpu_info
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return gpu_info

def get_miner_path():
    """Get the appropriate miner executable for the system."""
    system = platform.system()
    miners_dir = Path('miners')
    
    gpu_info = check_gpu()
    
    if gpu_info['vendor'] == 'NVIDIA':
        if system == 'Windows':
            return miners_dir / 'kawpowminer' / 'kawpowminer.exe'
        else:
            return miners_dir / 'kawpowminer' / 'kawpowminer'
    elif gpu_info['vendor'] == 'AMD':
        if system == 'Windows':
            return miners_dir / 'teamredminer' / 'teamredminer.exe'
        else:
            return miners_dir / 'teamredminer' / 'teamredminer'
    
    return None

def download_miner():
    """Download appropriate mining software if not present."""
    logger.info("Downloading mining software...")
    
    gpu_info = check_gpu()
    miners_dir = Path('miners')
    miners_dir.mkdir(exist_ok=True)
    
    # Note: In production, you would download the actual miners
    # For now, we'll provide instructions
    logger.warning("Mining software not found!")
    logger.info("Please download the appropriate miner:")
    
    if gpu_info['vendor'] == 'NVIDIA':
        logger.info("NVIDIA GPU detected - Recommended miners:")
        logger.info("1. T-Rex Miner: https://github.com/trexminer/T-Rex/releases")
        logger.info("2. KawPow Miner: https://github.com/RavenCommunity/kawpowminer/releases")
        logger.info("3. NBMiner: https://github.com/NebuTech/NBMiner/releases")
    elif gpu_info['vendor'] == 'AMD':
        logger.info("AMD GPU detected - Recommended miners:")
        logger.info("1. TeamRedMiner: https://github.com/todxx/teamredminer/releases")
        logger.info("2. lolMiner: https://github.com/Lolliedieb/lolMiner-releases/releases")
    
    logger.info(f"Extract to: {miners_dir.absolute()}")
    return False

def start_mining():
    """Start the Ravencoin mining process."""
    global miner_process, mining_active
    
    if not MINING_CONFIG['wallet_address']:
        logger.error("Cannot start mining: No wallet address configured")
        return False
    
    gpu_info = check_gpu()
    if not gpu_info['available']:
        logger.error("Cannot start mining: No GPU detected")
        return False
    
    miner_path = get_miner_path()
    if not miner_path or not miner_path.exists():
        logger.warning("Mining software not found")
        download_miner()
        return False
    
    # Build mining command
    pool_url = MINING_CONFIG['pool_url']
    wallet = MINING_CONFIG['wallet_address']
    worker = MINING_CONFIG['worker_name']
    
    # Example command for different miners
    # T-Rex: t-rex -a kawpow -o stratum+tcp://pool:port -u wallet.worker -p x
    cmd = [
        str(miner_path),
        '-a', 'kawpow',
        '-o', pool_url,
        '-u', f"{wallet}.{worker}",
        '-p', 'x',
        '--api-bind-http', '127.0.0.1:4067'  # Local API for stats
    ]
    
    try:
        logger.info(f"Starting miner: {miner_path.name}")
        logger.info(f"Pool: {pool_url}")
        logger.info(f"Worker: {worker}")
        
        miner_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=miner_path.parent
        )
        
        mining_active = True
        logger.info("Mining started successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start mining: {e}")
        return False

def stop_mining():
    """Stop the mining process."""
    global miner_process, mining_active
    
    if miner_process:
        logger.info("Stopping mining...")
        miner_process.terminate()
        try:
            miner_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            miner_process.kill()
        
        miner_process = None
        mining_active = False
        logger.info("Mining stopped")
        return True
    
    return False

def get_mining_stats():
    """Get current mining statistics."""
    if not mining_active or not miner_process:
        return {
            'status': 'stopped',
            'hashrate': 0,
            'accepted_shares': 0,
            'rejected_shares': 0,
            'uptime': 0
        }
    
    # Try to get stats from miner API
    try:
        response = requests.get('http://127.0.0.1:4067/summary', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'mining',
                'hashrate': data.get('hashrate', 0),
                'accepted_shares': data.get('accepted_shares', 0),
                'rejected_shares': data.get('rejected_shares', 0),
                'uptime': data.get('uptime', 0),
                'gpu_temp': data.get('gpu_temp', []),
                'gpu_power': data.get('gpu_power', [])
            }
    except Exception:
        pass
    
    # Fallback: basic status
    return {
        'status': 'mining',
        'hashrate': 0,
        'accepted_shares': 0,
        'rejected_shares': 0,
        'uptime': 0
    }

def report_mining_stats():
    """Report mining statistics to coordinator."""
    try:
        stats = get_mining_stats()
        stats['agent_id'] = agent_id
        stats['worker_name'] = MINING_CONFIG['worker_name']
        stats['pool'] = MINING_CONFIG['pool_url']
        
        response = requests.post(
            f"{coordinator_url}/api/mining/report",
            json=stats,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.debug("Mining stats reported successfully")
            return True
        else:
            logger.warning(f"Failed to report mining stats: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to report mining stats: {e}")
        return False

def tick():
    """Called periodically by main agent."""
    global last_report
    
    current_time = time.time()
    
    # Check if mining should be active
    if MINING_CONFIG['wallet_address'] and not mining_active:
        gpu_info = check_gpu()
        if gpu_info['available']:
            start_mining()
    
    # Report stats every 60 seconds
    if mining_active and current_time - last_report > 60:
        report_mining_stats()
        last_report = current_time
    
    # Check if miner process is still running
    if mining_active and miner_process:
        if miner_process.poll() is not None:
            logger.warning("Miner process died, restarting...")
            mining_active = False
            start_mining()

def run():
    """Called in single-run mode."""
    logger.info("Ravencoin miner: Running single execution")
    
    if not MINING_CONFIG['wallet_address']:
        logger.error("No wallet address configured. Set RVN_WALLET environment variable.")
        return
    
    gpu_info = check_gpu()
    if not gpu_info['available']:
        logger.error("No GPU detected. Cannot mine Ravencoin.")
        return
    
    start_mining()

def cleanup():
    """Clean up on shutdown."""
    logger.info("Ravencoin miner shutting down...")
    stop_mining()

# Module metadata
__version__ = "1.0.0"
__description__ = "Distributed Ravencoin (RVN) mining coordination"
__author__ = "Alpha Update Agent"
__coin__ = "Ravencoin (RVN)"
__algorithm__ = "KawPow"
