"""
Simple Coordinator Module
Connects agent to a central coordination server for distributed task execution.

This allows multiple agents on different networks to:
- Register their capabilities
- Receive tasks from a central server
- Submit results back

All communication is outbound from agents (works through NAT/firewalls).
"""

import logging
import requests
import socket
import json
import time
from pathlib import Path

# Module state
logger = None
agent_id = None
coordinator_url = None
last_heartbeat = 0

def init():
    """Initialize coordinator connection."""
    global logger, agent_id, coordinator_url
    
    logger = logging.getLogger('simple_coordinator')
    
    # Generate unique agent ID (hostname + MAC address hash)
    import hashlib
    hostname = socket.gethostname()
    mac = hex(uuid.getnode())[2:]
    agent_id = f"{hostname}_{hashlib.md5(mac.encode()).hexdigest()[:8]}"
    
    # Get coordinator URL from environment or config
    import os
    coordinator_url = os.getenv('COORDINATOR_URL', 'http://localhost:5000')
    
    logger.info(f"Coordinator module initializing as: {agent_id}")
    
    # Register with coordinator
    try:
        register_agent()
        logger.info(f"✓ Registered with coordinator at {coordinator_url}")
    except Exception as e:
        logger.error(f"Failed to register with coordinator: {e}")
        logger.info("Will retry on next tick...")

def register_agent():
    """Register this agent with the coordination server."""
    import os
    import psutil
    
    capabilities = {
        'agent_id': agent_id,
        'hostname': socket.gethostname(),
        'platform': os.name,
        'cpu_cores': os.cpu_count(),
        'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2) if 'psutil' in dir() else 'unknown',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
    }
    
    try:
        response = requests.post(
            f"{coordinator_url}/api/register",
            json=capabilities,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Registration successful")
            return True
        else:
            logger.warning(f"Registration returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.warning(f"Coordinator not reachable at {coordinator_url}")
        return False

def tick():
    """
    Periodically called by main agent.
    - Send heartbeat
    - Check for new tasks
    - Execute and report results
    """
    global last_heartbeat
    
    current_time = time.time()
    
    # Send heartbeat every 30 seconds
    if current_time - last_heartbeat > 30:
        send_heartbeat()
        last_heartbeat = current_time
    
    # Check for tasks
    check_for_tasks()

def send_heartbeat():
    """Send heartbeat to coordinator to show agent is alive."""
    try:
        response = requests.post(
            f"{coordinator_url}/api/heartbeat",
            json={'agent_id': agent_id, 'timestamp': time.time()},
            timeout=3
        )
        logger.debug(f"Heartbeat sent")
    except Exception as e:
        logger.debug(f"Heartbeat failed: {e}")

def check_for_tasks():
    """Check if coordinator has any tasks for this agent."""
    try:
        response = requests.get(
            f"{coordinator_url}/api/tasks/next",
            params={'agent_id': agent_id},
            timeout=5
        )
        
        if response.status_code == 200:
            task = response.json()
            
            if task and task.get('task_id'):
                logger.info(f"📥 Received task: {task['task_id']} - {task.get('description', 'No description')}")
                result = execute_task(task)
                submit_result(result)
        
    except Exception as e:
        logger.debug(f"Task check failed: {e}")

def execute_task(task):
    """
    Execute a task received from coordinator.
    
    Args:
        task: Dict with task_id, type, and parameters
        
    Returns:
        Dict with task_id, status, and result
    """
    task_id = task['task_id']
    task_type = task.get('type', 'unknown')
    
    logger.info(f"🔧 Executing task {task_id} (type: {task_type})")
    
    try:
        # Task execution logic based on type
        if task_type == 'ping':
            result_data = {'message': 'pong', 'agent_id': agent_id}
            status = 'completed'
        
        elif task_type == 'compute':
            # Example: Simple computation task
            result_data = perform_computation(task.get('params', {}))
            status = 'completed'
        
        elif task_type == 'info':
            # Return agent information
            result_data = get_agent_info()
            status = 'completed'
        
        else:
            result_data = {'error': f'Unknown task type: {task_type}'}
            status = 'failed'
        
        logger.info(f"✓ Task {task_id} completed")
        
        return {
            'task_id': task_id,
            'agent_id': agent_id,
            'status': status,
            'result': result_data,
            'completed_at': time.time()
        }
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        return {
            'task_id': task_id,
            'agent_id': agent_id,
            'status': 'failed',
            'error': str(e),
            'completed_at': time.time()
        }

def perform_computation(params):
    """Example computation task."""
    import time
    
    # Simulate some work
    n = params.get('n', 100)
    result = sum(i**2 for i in range(n))
    
    return {
        'computation': f'sum of squares up to {n}',
        'result': result
    }

def get_agent_info():
    """Get current agent information."""
    import os
    
    return {
        'agent_id': agent_id,
        'hostname': socket.gethostname(),
        'platform': os.name,
        'cwd': str(Path.cwd()),
        'timestamp': time.time()
    }

def submit_result(result):
    """Submit task results back to coordinator."""
    try:
        response = requests.post(
            f"{coordinator_url}/api/tasks/result",
            json=result,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"📤 Result submitted for task {result['task_id']}")
        else:
            logger.warning(f"Result submission returned status {response.status_code}")
    
    except Exception as e:
        logger.error(f"Failed to submit result: {e}")

def run():
    """Called when running in single-execution mode."""
    logger.info("Running coordinator in single-execution mode")
    
    # Register and check once
    register_agent()
    send_heartbeat()
    check_for_tasks()

def cleanup():
    """Clean up on shutdown."""
    logger.info("Coordinator module shutting down...")
    
    # Unregister from coordinator
    try:
        requests.post(
            f"{coordinator_url}/api/unregister",
            json={'agent_id': agent_id},
            timeout=3
        )
        logger.info("✓ Unregistered from coordinator")
    except:
        pass

# Module metadata
__version__ = "1.0.0"
__description__ = "Simple coordinator for distributed task execution"
__author__ = "Alpha Update Agent"

# Required imports
import sys
import uuid

