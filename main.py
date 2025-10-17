"""
Alpha Update Agent - Main Entry Point
A lightweight, cross-platform self-updating agent.
"""

import os
import sys
import time
import json
import logging
import importlib
import signal
from pathlib import Path
from typing import List, Dict
from updater import Updater, UpdaterException


class AlphaAgent:
    """
    Main agent class that manages updates and module loading.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the Alpha Agent.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.updater = Updater(config_path)
        self.logger = self._setup_logging()
        self.running = True
        self.loaded_modules = {}
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the agent."""
        logger = logging.getLogger('AlphaAgent')
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            log_file = self.updater.config.get('log_file', 'agent.log')
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def load_modules(self) -> bool:
        """
        Load enabled modules dynamically.
        
        Returns:
            True if all modules loaded successfully
        """
        modules_enabled = self.updater.config.get('modules_enabled', [])
        
        if not modules_enabled:
            self.logger.info("No modules enabled")
            return True
        
        modules_dir = self.updater.modules_dir
        if not modules_dir.exists():
            self.logger.warning(f"Modules directory not found: {modules_dir}")
            return False
        
        # Add modules directory to Python path
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))
        
        success = True
        for module_name in modules_enabled:
            try:
                # Remove .py extension if present
                module_name_clean = module_name.replace('.py', '')
                
                self.logger.info(f"Loading module: {module_name_clean}")
                
                # Import or reload module
                if module_name_clean in self.loaded_modules:
                    module = importlib.reload(self.loaded_modules[module_name_clean])
                else:
                    module = importlib.import_module(module_name_clean)
                
                self.loaded_modules[module_name_clean] = module
                
                # Call module's init function if it exists
                if hasattr(module, 'init'):
                    module.init()
                    self.logger.info(f"Module {module_name_clean} initialized")
                
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")
                success = False
        
        return success
    
    def unload_modules(self):
        """Unload all loaded modules."""
        for module_name, module in self.loaded_modules.items():
            try:
                # Call module's cleanup function if it exists
                if hasattr(module, 'cleanup'):
                    module.cleanup()
                    self.logger.info(f"Module {module_name} cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up module {module_name}: {e}")
        
        self.loaded_modules.clear()
    
    def check_and_update(self) -> bool:
        """
        Check for updates and apply if available.
        
        Returns:
            True if update was applied (requires restart)
        """
        if not self.updater.config.get('auto_update', True):
            self.logger.info("Auto-update is disabled")
            return False
        
        self.logger.info("Checking for updates...")
        success, message = self.updater.perform_update()
        
        if success and "Successfully updated" in message:
            self.logger.info(message)
            self.logger.info("Update applied, restart required")
            return True
        else:
            self.logger.info(message)
            return False
    
    def restart(self):
        """Restart the agent to apply updates."""
        self.logger.info("Restarting agent...")
        
        # Unload modules
        self.unload_modules()
        
        # Restart the script
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def run_once(self):
        """
        Run one update check cycle.
        Useful for testing or cron-based execution.
        """
        self.logger.info("=== Alpha Update Agent - Single Run Mode ===")
        self.logger.info(f"Current version: {self.updater.get_current_version()}")
        
        # Check for updates
        update_needed = self.check_and_update()
        
        if update_needed:
            self.logger.info("Update was applied, please restart the agent")
            return True
        
        # Load and run modules
        self.load_modules()
        
        # Run module tasks if they exist
        for module_name, module in self.loaded_modules.items():
            if hasattr(module, 'run'):
                try:
                    self.logger.info(f"Running module: {module_name}")
                    module.run()
                except Exception as e:
                    self.logger.error(f"Error running module {module_name}: {e}")
        
        # Cleanup
        self.unload_modules()
        
        return False
    
    def run(self):
        """
        Main run loop for continuous operation.
        Checks for updates periodically.
        """
        self.logger.info("=== Alpha Update Agent Starting ===")
        self.logger.info(f"Current version: {self.updater.get_current_version()}")
        
        # Load modules on startup
        self.load_modules()
        
        check_interval = self.updater.config.get('check_interval', 3600)
        last_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check for updates at specified interval
                if current_time - last_check >= check_interval:
                    update_needed = self.check_and_update()
                    last_check = current_time
                    
                    if update_needed:
                        self.restart()
                        break  # Should not reach here
                
                # Run module tasks if they exist
                for module_name, module in self.loaded_modules.items():
                    if hasattr(module, 'tick'):
                        try:
                            module.tick()
                        except Exception as e:
                            self.logger.error(f"Error in module {module_name}: {e}")
                
                # Sleep to avoid busy waiting
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(10)
        
        # Cleanup
        self.unload_modules()
        self.logger.info("=== Alpha Update Agent Stopped ===")


def print_help():
    """Print usage information."""
    print("""
Alpha Update Agent - Help

Usage:
    python main.py [command]

Commands:
    run         Run in continuous mode (default)
    once        Run once and exit
    check       Check for updates only
    version     Show current version
    help        Show this help message

Examples:
    python main.py              # Run continuously
    python main.py once         # Run once and exit
    python main.py check        # Just check for updates
    """)


def main():
    """Entry point for the application."""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = 'run'
    
    try:
        agent = AlphaAgent()
        
        if command == 'help':
            print_help()
        elif command == 'version':
            print(f"Alpha Update Agent v{agent.updater.get_current_version()}")
        elif command == 'check':
            print("Checking for updates...")
            success, message = agent.updater.perform_update()
            print(message)
            if success and "Successfully updated" in message:
                print("Update applied! Please restart the agent.")
        elif command == 'once':
            agent.run_once()
        elif command == 'run':
            agent.run()
        else:
            print(f"Unknown command: {command}")
            print_help()
            sys.exit(1)
            
    except UpdaterException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutdown requested")
        sys.exit(0)


if __name__ == "__main__":
    main()

