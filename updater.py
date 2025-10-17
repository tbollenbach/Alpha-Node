"""
Alpha Update Agent - Updater Module
Handles version checking, downloading, and applying updates.
"""

import os
import sys
import json
import hashlib
import shutil
import zipfile
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests


class UpdaterException(Exception):
    """Custom exception for updater errors."""
    pass


class Updater:
    """
    Manages the update lifecycle: check, download, verify, apply, rollback.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the updater with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.base_dir = Path(__file__).parent.absolute()
        self.modules_dir = self.base_dir / "modules"
        self.backup_dir = self.base_dir / "backups"
        
        # Ensure directories exist
        self.modules_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise UpdaterException(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise UpdaterException(f"Invalid JSON in config file: {e}")
    
    def _save_config(self):
        """Save current configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the updater."""
        logger = logging.getLogger('AlphaUpdater')
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_file = self.config.get('log_file', 'agent.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def get_current_version(self) -> str:
        """Get the current version from config."""
        return self.config.get('version', '0.0.0')
    
    def check_for_updates(self) -> Optional[Dict]:
        """
        Check remote server for available updates.
        
        Returns:
            Update info dict if newer version available, None otherwise
        """
        update_server = self.config.get('update_server')
        if not update_server:
            self.logger.error("No update server configured")
            return None
        
        try:
            self.logger.info(f"Checking for updates at {update_server}")
            response = requests.get(update_server, timeout=10)
            response.raise_for_status()
            
            update_info = response.json()
            remote_version = update_info.get('version', '0.0.0')
            current_version = self.get_current_version()
            
            self.logger.info(f"Current: {current_version}, Remote: {remote_version}")
            
            if self._is_newer_version(remote_version, current_version):
                self.logger.info(f"Update available: {remote_version}")
                return update_info
            else:
                self.logger.info("Already up to date")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to check for updates: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid update info JSON: {e}")
            return None
    
    def _is_newer_version(self, remote: str, current: str) -> bool:
        """
        Compare version strings (simple semantic versioning).
        
        Args:
            remote: Remote version string
            current: Current version string
            
        Returns:
            True if remote is newer than current
        """
        try:
            remote_parts = [int(x) for x in remote.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad to same length
            max_len = max(len(remote_parts), len(current_parts))
            remote_parts += [0] * (max_len - len(remote_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return remote_parts > current_parts
        except (ValueError, AttributeError):
            self.logger.warning("Invalid version format, assuming no update")
            return False
    
    def download_update(self, update_info: Dict) -> Optional[Path]:
        """
        Download update package from remote server.
        
        Args:
            update_info: Update information dictionary
            
        Returns:
            Path to downloaded file or None on failure
        """
        url = update_info.get('url')
        if not url:
            self.logger.error("No download URL in update info")
            return None
        
        try:
            self.logger.info(f"Downloading update from {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Download to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_path = Path(temp_file.name)
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.logger.debug(f"Download progress: {progress:.1f}%")
            
            self.logger.info(f"Download complete: {temp_path}")
            return temp_path
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Download failed: {e}")
            return None
    
    def verify_update(self, file_path: Path, update_info: Dict) -> bool:
        """
        Verify integrity of downloaded update using checksum.
        
        Args:
            file_path: Path to downloaded file
            update_info: Update information with checksum
            
        Returns:
            True if verification successful
        """
        expected_checksum = update_info.get('checksum')
        if not expected_checksum:
            self.logger.warning("No checksum provided, skipping verification")
            return True  # Allow updates without checksums (for testing)
        
        try:
            self.logger.info("Verifying update integrity...")
            
            # Calculate SHA256 checksum
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_checksum = sha256_hash.hexdigest()
            
            if actual_checksum.lower() == expected_checksum.lower():
                self.logger.info("Checksum verification passed")
                return True
            else:
                self.logger.error(
                    f"Checksum mismatch! Expected: {expected_checksum}, "
                    f"Got: {actual_checksum}"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    def create_backup(self) -> Path:
        """
        Create a backup of current installation.
        
        Returns:
            Path to backup directory
        """
        current_version = self.get_current_version()
        backup_name = f"backup_{current_version}_{int(Path.ctime(Path(__file__)))}"
        backup_path = self.backup_dir / backup_name
        
        try:
            self.logger.info(f"Creating backup: {backup_path}")
            backup_path.mkdir(exist_ok=True)
            
            # Backup main files
            for file in ['main.py', 'updater.py', 'config.json']:
                src = self.base_dir / file
                if src.exists():
                    shutil.copy2(src, backup_path / file)
            
            # Backup modules directory
            if self.modules_dir.exists():
                shutil.copytree(
                    self.modules_dir,
                    backup_path / 'modules',
                    dirs_exist_ok=True
                )
            
            self.logger.info("Backup created successfully")
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            raise UpdaterException(f"Failed to create backup: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backups, keeping only the most recent ones."""
        backup_count = self.config.get('backup_count', 3)
        
        try:
            backups = sorted(
                [d for d in self.backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Remove old backups
            for old_backup in backups[backup_count:]:
                self.logger.info(f"Removing old backup: {old_backup}")
                shutil.rmtree(old_backup)
                
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old backups: {e}")
    
    def apply_update(self, update_file: Path, update_info: Dict) -> bool:
        """
        Extract and apply the update package.
        
        Args:
            update_file: Path to update zip file
            update_info: Update information dictionary
            
        Returns:
            True if update applied successfully
        """
        try:
            self.logger.info("Applying update...")
            
            # Extract update to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract zip file
                with zipfile.ZipFile(update_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Copy files to installation directory
                for item in temp_path.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(temp_path)
                        dest_path = self.base_dir / rel_path
                        
                        # Create parent directories if needed
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(item, dest_path)
                        self.logger.debug(f"Updated: {rel_path}")
            
            # Update version in config
            self.config['version'] = update_info['version']
            
            # Update enabled modules list
            if 'modules' in update_info:
                self.config['modules_enabled'] = update_info['modules']
            
            self._save_config()
            
            self.logger.info(f"Update to version {update_info['version']} completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply update: {e}")
            return False
    
    def rollback(self, backup_path: Path) -> bool:
        """
        Rollback to a previous backup.
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            True if rollback successful
        """
        try:
            self.logger.warning(f"Rolling back to backup: {backup_path}")
            
            # Restore files from backup
            for item in backup_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(backup_path)
                    dest_path = self.base_dir / rel_path
                    
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
                    self.logger.debug(f"Restored: {rel_path}")
            
            # Reload config
            self.config = self._load_config()
            
            self.logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def perform_update(self) -> Tuple[bool, str]:
        """
        Complete update workflow: check, download, verify, backup, apply.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check for updates
            update_info = self.check_for_updates()
            if not update_info:
                return True, "No updates available"
            
            # Download update
            update_file = self.download_update(update_info)
            if not update_file:
                return False, "Download failed"
            
            try:
                # Verify integrity
                if not self.verify_update(update_file, update_info):
                    return False, "Integrity verification failed"
                
                # Create backup
                backup_path = self.create_backup()
                
                # Apply update
                if not self.apply_update(update_file, update_info):
                    # Rollback on failure
                    self.logger.error("Update failed, attempting rollback")
                    if self.rollback(backup_path):
                        return False, "Update failed, rolled back to previous version"
                    else:
                        return False, "Update and rollback both failed!"
                
                return True, f"Successfully updated to version {update_info['version']}"
                
            finally:
                # Cleanup downloaded file
                if update_file.exists():
                    update_file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Update process failed: {e}")
            return False, str(e)

