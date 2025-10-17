"""
Script to create update packages for testing.
Creates a ZIP file with updated modules and calculates its checksum.
"""

import os
import sys
import json
import hashlib
import zipfile
from pathlib import Path
import shutil


def calculate_sha256(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def create_update_package(version, modules_to_include, output_dir):
    """
    Create an update package ZIP file.
    
    Args:
        version: Version string (e.g., "1.0.1")
        modules_to_include: List of module filenames to include
        output_dir: Directory to save the package
    """
    print(f"\n{'='*60}")
    print(f"Creating update package for version {version}")
    print(f"{'='*60}\n")
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    modules_dir = base_dir / "modules"
    updates_dir = Path(output_dir)
    updates_dir.mkdir(exist_ok=True)
    
    package_name = f"{version}.zip"
    package_path = updates_dir / package_name
    
    # Create the ZIP file
    print(f"Creating package: {package_path}")
    
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add modules
        print(f"\nIncluding modules:")
        for module_file in modules_to_include:
            module_path = modules_dir / module_file
            if module_path.exists():
                # Add to modules/ directory in ZIP
                arcname = f"modules/{module_file}"
                zipf.write(module_path, arcname)
                print(f"  ✓ {module_file}")
            else:
                print(f"  ✗ {module_file} (not found)")
        
        # Add __init__.py for modules
        init_path = modules_dir / "__init__.py"
        if init_path.exists():
            zipf.write(init_path, "modules/__init__.py")
            print(f"  ✓ __init__.py")
    
    # Calculate checksum
    checksum = calculate_sha256(package_path)
    
    print(f"\n{'='*60}")
    print(f"Package created successfully!")
    print(f"{'='*60}")
    print(f"File: {package_path}")
    print(f"Size: {package_path.stat().st_size} bytes")
    print(f"SHA256: {checksum}")
    print(f"{'='*60}\n")
    
    return package_name, checksum


def update_json_file(json_file, version, checksum, modules):
    """Update the JSON file with the correct checksum."""
    print(f"Updating {json_file} with checksum...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    data['checksum'] = checksum
    data['version'] = version
    data['modules'] = modules
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"✓ Updated {json_file}\n")


def main():
    """Main function to create update packages."""
    
    server_dir = Path(__file__).parent
    updates_dir = server_dir / "updates"
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Alpha Update Agent - Update Package Creator             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create version 1.0.1 package
    print("Creating version 1.0.1...")
    modules_1_0_1 = ["gpu_share.py", "disk_share.py"]
    package_1, checksum_1 = create_update_package(
        "1.0.1",
        modules_1_0_1,
        updates_dir
    )
    
    # Update the JSON file
    json_file_1 = server_dir / "updates.json"
    update_json_file(json_file_1, "1.0.1", checksum_1, modules_1_0_1)
    
    # Create version 1.0.2 package
    print("\nCreating version 1.0.2...")
    modules_1_0_2 = ["gpu_share.py", "disk_share.py", "network_bridge.py"]
    package_2, checksum_2 = create_update_package(
        "1.0.2",
        modules_1_0_2,
        updates_dir
    )
    
    # Update the JSON file
    json_file_2 = server_dir / "updates_1.0.2.json"
    update_json_file(json_file_2, "1.0.2", checksum_2, modules_1_0_2)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    Packages Created!                         ║
╚══════════════════════════════════════════════════════════════╝

Created packages:
  • {updates_dir / '1.0.1.zip'}
  • {updates_dir / '1.0.2.zip'}

Updated JSON files:
  • {json_file_1}
  • {json_file_2}

Next steps:
  1. Start the test server: python test_server.py
  2. Run the agent with: python main.py check
  3. The agent should detect and apply the update!

    """)


if __name__ == "__main__":
    main()

