#!/usr/bin/env python3
"""
KSSEM Virtual AI Assistant - Main Application Launcher
Starts both the API server and GUI interface for the kiosk-based virtual assistant
"""

import os
import sys
import subprocess
import time
import threading
import logging
from pathlib import Path
import argparse
import signal

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logging import setup_logger

class KSSEMAssistantLauncher:
    """
    Main application launcher for KSSEM Virtual AI Assistant
    Manages both API server and GUI components
    """
    
    def __init__(self, mode="full", api_port=8000, debug=False):
        """
        Initialize the launcher
        
        Args:
            mode: Launch mode ('api', 'gui', 'full')
            api_port: Port for API server
            debug: Enable debug mode
        """
        self.mode = mode
        self.api_port = api_port
        self.debug = debug
        self.logger = setup_logger("kssem_launcher", "DEBUG" if debug else "INFO")
        
        # Process management
        self.api_process = None
        self.gui_process = None
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.shutdown()
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.logger.info("Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'transformers', 'torch', 
            'customtkinter', 'matplotlib', 'requests', 'cryptography'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.error(f"Missing required packages: {missing_packages}")
            self.logger.info("Please install missing packages:")
            self.logger.info(f"pip install {' '.join(missing_packages)}")
            return False
        
        self.logger.info("✓ All dependencies are available")
        return True
    
    def setup_environment(self):
        """Setup environment variables and paths"""
        self.logger.info("Setting up environment...")
        
        # Set environment variables
        os.environ['KSSEM_API_PORT'] = str(self.api_port)
        os.environ['KSSEM_DEBUG'] = str(self.debug)
        
        # Ensure data directories exist
        data_dirs = [
            'data/kssem_campus_map',
            'data/knowledge_base',
            'data/training_data',
            'logs'
        ]
        
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("✓ Environment setup complete")
    
    def start_api_server(self):
        """Start the FastAPI server"""
        if self.mode in ['api', 'full']:
            self.logger.info(f"Starting API server on port {self.api_port}...")
            
            api_script = os.path.join('src', 'data_layer', 'api_gateway', 'api_endpoints.py')
            
            if not os.path.exists(api_script):
                self.logger.error(f"API script not found: {api_script}")
                return False
            
            try:
                # Start API server using uvicorn
                cmd = [
                    sys.executable, '-m', 'uvicorn',
                    'src.data_layer.api_gateway.api_endpoints:app',
                    '--host', '0.0.0.0',
                    '--port', str(self.api_port),
                    '--log-level', 'debug' if self.debug else 'info'
                ]
                
                if self.debug:
                    cmd.append('--reload')
                
                self.api_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Wait a moment for server to start
                time.sleep(3)
                
                # Check if process is still running
                if self.api_process.poll() is None:
                    self.logger.info(f"✓ API server started successfully on http://localhost:{self.api_port}")
                    return True
                else:
                    stdout, stderr = self.api_process.communicate()
                    self.logger.error(f"API server failed to start: {stderr}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to start API server: {e}")
                return False
        
        return True
    
    def start_gui_interface(self):
        """Start the GUI interface"""
        if self.mode in ['gui', 'full']:
            self.logger.info("Starting GUI interface...")
            
            gui_script = os.path.join('src', 'presentation_layer', 'gui', 'main_interface.py')
            
            if not os.path.exists(gui_script):
                self.logger.error(f"GUI script not found: {gui_script}")
                return False
            
            try:
                # Wait for API server if in full mode
                if self.mode == 'full':
                    self.logger.info("Waiting for API server to be ready...")
                    self.wait_for_api_server()
                
                # Start GUI
                cmd = [sys.executable, gui_script]
                
                self.gui_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                self.logger.info("✓ GUI interface started successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to start GUI interface: {e}")
                return False
        
        return True
    
    def wait_for_api_server(self, timeout=30):
        """Wait for API server to be ready"""
        import requests
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.api_port}/health", timeout=2)
                if response.status_code == 200:
                    self.logger.info("✓ API server is ready")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        self.logger.warning("API server may not be fully ready")
        return False
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed"""
        while self.running:
            try:
                # Check API process
                if self.api_process and self.api_process.poll() is not None:
                    self.logger.warning("API server process died, attempting restart...")
                    if not self.start_api_server():
                        self.logger.error("Failed to restart API server")
                        break
                
                # Check GUI process
                if self.gui_process and self.gui_process.poll() is not None:
                    self.logger.warning("GUI process died, attempting restart...")
                    if not self.start_gui_interface():
                        self.logger.error("Failed to restart GUI")
                        break
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                break
    
    def shutdown(self):
        """Shutdown all processes"""
        self.logger.info("Shutting down KSSEM Virtual AI Assistant...")
        self.running = False
        
        # Terminate GUI process
        if self.gui_process:
            try:
                self.gui_process.terminate()
                self.gui_process.wait(timeout=5)
                self.logger.info("✓ GUI process terminated")
            except subprocess.TimeoutExpired:
                self.gui_process.kill()
                self.logger.warning("GUI process killed (timeout)")
            except Exception as e:
                self.logger.error(f"Error terminating GUI process: {e}")
        
        # Terminate API process
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.logger.info("✓ API server terminated")
            except subprocess.TimeoutExpired:
                self.api_process.kill()
                self.logger.warning("API server killed (timeout)")
            except Exception as e:
                self.logger.error(f"Error terminating API server: {e}")
        
        self.logger.info("✓ Shutdown complete")
    
    def run(self):
        """Main run method"""
        self.logger.info("🎓 Starting KSSEM Virtual AI Assistant")
        self.logger.info(f"Mode: {self.mode}, Port: {self.api_port}, Debug: {self.debug}")
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Setup environment
        self.setup_environment()
        
        # Start components based on mode
        success = True
        
        if not self.start_api_server():
            success = False
        
        if success and not self.start_gui_interface():
            success = False
        
        if not success:
            self.logger.error("Failed to start all components")
            self.shutdown()
            return False
        
        self.logger.info("🚀 KSSEM Virtual AI Assistant is running!")
        
        if self.mode == 'full':
            self.logger.info(f"📡 API Documentation: http://localhost:{self.api_port}/docs")
            self.logger.info(f"🖥️  GUI Interface: Active")
        elif self.mode == 'api':
            self.logger.info(f"📡 API Only Mode: http://localhost:{self.api_port}/docs")
        elif self.mode == 'gui':
            self.logger.info("🖥️  GUI Only Mode: Active")
        
        # Monitor processes
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        try:
            # Wait for processes to complete
            if self.gui_process:
                self.gui_process.wait()
            elif self.api_process:
                self.api_process.wait()
            else:
                # Keep alive if no processes to wait for
                while self.running:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.shutdown()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="KSSEM Virtual AI Assistant Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start full system (API + GUI)
  python main.py --mode api         # Start API server only
  python main.py --mode gui         # Start GUI only
  python main.py --port 8080        # Use custom port
  python main.py --debug            # Enable debug mode
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'api', 'gui'],
        default='full',
        help='Launch mode (default: full)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='KSSEM Virtual AI Assistant v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Create and run launcher
    launcher = KSSEMAssistantLauncher(
        mode=args.mode,
        api_port=args.port,
        debug=args.debug
    )
    
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()