#!/usr/bin/env python3
"""
Create Update Package v2.0.0
Includes resource pooling system and enhanced dashboard.
"""

import os
import zipfile
import hashlib
import json
from pathlib import Path

def create_update_package():
    """Create update package with resource pooling system."""
    
    # Version info
    version = "2.0.0"
    update_name = f"alpha-agent-{version}"
    
    # Create update directory
    update_dir = Path(f"updates/{update_name}")
    update_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include in update (relative to project root)
    files_to_include = [
        "../main.py",
        "../updater.py", 
        "../config.json",
        "../requirements.txt",
        "../modules/__init__.py",
        "../modules/simple_coordinator.py",
        "../modules/resource_pool.py",  # New resource pooling module
        "../modules/gpu_share.py",
        "../modules/network_bridge.py", 
        "../modules/disk_share.py"
    ]
    
    print(f"Creating update package: {update_name}")
    
    # Copy files to update directory
    for file_path in files_to_include:
        src_path = Path(file_path)
        if src_path.exists():
            dst_path = update_dir / file_path
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
                dst.write(src.read())
            print(f"  + Added: {file_path}")
        else:
            print(f"  - Missing: {file_path}")
    
    # Create update zip
    zip_path = f"updates/{update_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(update_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(update_dir)
                zipf.write(file_path, arc_path)
    
    # Calculate checksum
    with open(zip_path, 'rb') as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    
    # Get file size
    file_size = os.path.getsize(zip_path)
    
    print(f"  + Created: {zip_path}")
    print(f"  + Size: {file_size:,} bytes")
    print(f"  + SHA256: {checksum}")
    
    # Create update manifest
    manifest = {
        "version": version,
        "release_date": "2025-10-16T20:30:00Z",
        "description": "Alpha Update Agent v2.0.0 - Resource Pooling System",
        "changes": [
            "Added hardware resource pooling module",
            "Enhanced dashboard with resource monitoring", 
            "Real-time CPU, memory, storage, and GPU tracking",
            "Improved coordinator server with resource APIs",
            "Better error handling and logging"
        ],
        "download_url": f"https://alpha-node.onrender.com/updates/{update_name}.zip",
        "file_size": file_size,
        "checksum": {
            "algorithm": "sha256",
            "value": checksum
        },
        "requirements": {
            "python": ">=3.10",
            "dependencies": [
                "requests>=2.31.0",
                "psutil>=5.9.0",
                "flask>=3.0.0"
            ]
        },
        "installation": {
            "backup": True,
            "restart_required": True,
            "modules_to_enable": [
                "simple_coordinator.py",
                "resource_pool.py"
            ]
        }
    }
    
    # Save manifest
    manifest_path = f"updates/{update_name}_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"  + Manifest: {manifest_path}")
    
    return manifest

if __name__ == "__main__":
    manifest = create_update_package()
    print(f"\n[SUCCESS] Update package created successfully!")
    print(f"Version: {manifest['version']}")
    print(f"Description: {manifest['description']}")
