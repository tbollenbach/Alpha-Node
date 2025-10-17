"""
Resource Pool Module
Collects and reports hardware resources (CPU, memory, GPU, storage) from agents.
This enables distributed resource sharing and monitoring.
"""

import logging
import psutil
import platform
import time
import json
import requests
import os
import socket
import uuid
import hashlib

# Module state
logger = None
agent_id = None
coordinator_url = None
last_report = 0

def init():
    """Initialize resource pooling module."""
    global logger, agent_id, coordinator_url
    
    logger = logging.getLogger('resource_pool')
    
    # Generate unique agent ID
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())[2:]
    agent_id = f"{hostname}_{hashlib.md5(mac.encode()).hexdigest()[:8]}"
    
    # Get coordinator URL
    coordinator_url = os.getenv('COORDINATOR_URL', 'http://localhost:5000')
    
    logger.info(f"Resource pool module initializing for agent: {agent_id}")
    
    # Report initial resources
    report_resources()

def get_system_resources():
    """Collect comprehensive system resource information."""
    try:
        # CPU information
        cpu_info = {
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'usage_percent': psutil.cpu_percent(interval=1),
            'frequency_current': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'frequency_max': psutil.cpu_freq().max if psutil.cpu_freq() else None,
            'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'usage_percent': memory.percent,
            'free_gb': round(memory.free / (1024**3), 2)
        }
        
        # Storage information
        storage_info = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                storage_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(partition_usage.total / (1024**3), 2),
                    'used_gb': round(partition_usage.used / (1024**3), 2),
                    'free_gb': round(partition_usage.free / (1024**3), 2),
                    'usage_percent': round((partition_usage.used / partition_usage.total) * 100, 2)
                })
            except (PermissionError, OSError):
                continue
        
        # Network information
        network_info = {
            'interfaces': len(psutil.net_if_addrs()),
            'connections': len(psutil.net_connections()),
            'bytes_sent': psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
            'bytes_recv': psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0
        }
        
        # GPU information (if available)
        gpu_info = get_gpu_info()
        
        # System information
        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': socket.gethostname(),
            'boot_time': psutil.boot_time(),
            'uptime_seconds': time.time() - psutil.boot_time()
        }
        
        # Process information
        process_info = {
            'total_processes': len(psutil.pids()),
            'python_processes': len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]),
            'memory_usage_mb': round(psutil.Process().memory_info().rss / (1024**2), 2)
        }
        
        return {
            'agent_id': agent_id,
            'timestamp': time.time(),
            'cpu': cpu_info,
            'memory': memory_info,
            'storage': storage_info,
            'network': network_info,
            'gpu': gpu_info,
            'system': system_info,
            'processes': process_info
        }
        
    except Exception as e:
        logger.error(f"Error collecting system resources: {e}")
        return {
            'agent_id': agent_id,
            'timestamp': time.time(),
            'error': str(e)
        }

def get_gpu_info():
    """Get GPU information if available."""
    gpu_info = {
        'available': False,
        'count': 0,
        'devices': []
    }
    
    try:
        # Try to detect NVIDIA GPUs
        import subprocess
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            gpu_info['available'] = True
            gpu_info['vendor'] = 'NVIDIA'
            lines = result.stdout.strip().split('\n')
            gpu_info['count'] = len(lines)
            
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) >= 4:
                    gpu_info['devices'].append({
                        'index': i,
                        'name': parts[0],
                        'memory_total_mb': int(parts[1]),
                        'memory_used_mb': int(parts[2]),
                        'utilization_percent': int(parts[3])
                    })
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    try:
        # Try to detect AMD GPUs
        import subprocess
        result = subprocess.run(['rocm-smi', '--showmemuse', '--showuse'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and 'GPU' in result.stdout:
            gpu_info['available'] = True
            gpu_info['vendor'] = 'AMD'
            gpu_info['count'] = result.stdout.count('GPU')
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return gpu_info

def report_resources():
    """Report current system resources to coordinator."""
    try:
        resources = get_system_resources()
        
        response = requests.post(
            f"{coordinator_url}/api/resources/report",
            json=resources,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.debug(f"Resources reported successfully")
            return True
        else:
            logger.warning(f"Resource reporting failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to report resources: {e}")
        return False

def tick():
    """Called periodically to update resource information."""
    global last_report
    
    current_time = time.time()
    
    # Report resources every 30 seconds
    if current_time - last_report > 30:
        report_resources()
        last_report = current_time

def run():
    """Called in single-run mode to report resources once."""
    logger.info("Resource pool: Running single execution")
    report_resources()

def cleanup():
    """Clean up on shutdown."""
    logger.info("Resource pool module shutting down...")

# Module metadata
__version__ = "1.0.0"
__description__ = "Hardware resource pooling and monitoring"
__author__ = "Alpha Update Agent"
