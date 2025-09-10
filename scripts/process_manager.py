#!/usr/bin/env python3
"""
Process Manager for ROI Calculator
Ensures single instance, handles graceful shutdown, and monitors health
"""

import os
import sys
import signal
import subprocess
import time
import psutil
import logging
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/process_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages Streamlit application lifecycle"""
    
    def __init__(self):
        self.pid_file = Path('.streamlit_pid')
        self.log_dir = Path('logs')
        self.log_dir.mkdir(exist_ok=True)
        self.process = None
        self.port = int(os.getenv('STREAMLIT_PORT', '8501'))
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def is_running(self) -> bool:
        """Check if a Streamlit instance is already running"""
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text())
                process = psutil.Process(pid)
                # Check if it's actually a streamlit process
                if 'streamlit' in ' '.join(process.cmdline()).lower():
                    return True
            except (psutil.NoSuchProcess, ValueError):
                # Clean up stale PID file
                self.pid_file.unlink(missing_ok=True)
        return False
    
    def kill_existing(self):
        """Kill any existing Streamlit processes"""
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline_list = proc.info.get('cmdline')
                if cmdline_list is None:
                    continue
                cmdline = ' '.join(cmdline_list)
                if 'streamlit' in cmdline.lower() and 'run' in cmdline:
                    logger.info(f"Killing existing Streamlit process: PID {proc.info['pid']}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
                continue
        
        if killed_count > 0:
            logger.info(f"Killed {killed_count} existing Streamlit processes")
            time.sleep(2)  # Give processes time to clean up
    
    def start(self) -> bool:
        """Start the Streamlit application"""
        if self.is_running():
            logger.warning("Streamlit is already running")
            return False
        
        # Kill any zombie processes first
        self.kill_existing()
        
        # Load environment variables
        env = os.environ.copy()
        if Path('.env').exists():
            with open('.env') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env[key] = value.strip('"')
        
        # Start Streamlit with proper configuration
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', str(self.port),
            '--server.headless', 'true',
            '--client.showSidebarNavigation', 'false',
            '--server.maxUploadSize', '100',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'true'
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Save PID
            self.pid_file.write_text(str(self.process.pid))
            logger.info(f"Started Streamlit on port {self.port} with PID {self.process.pid}")
            
            # Wait for startup
            time.sleep(3)
            
            # Verify it's running
            if self.process.poll() is None:
                logger.info("Streamlit started successfully")
                return True
            else:
                logger.error("Streamlit failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Streamlit: {e}")
            return False
    
    def stop(self):
        """Stop the Streamlit application gracefully"""
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text())
                process = psutil.Process(pid)
                
                logger.info(f"Stopping Streamlit process {pid}")
                process.terminate()
                
                try:
                    process.wait(timeout=10)
                    logger.info("Streamlit stopped gracefully")
                except psutil.TimeoutExpired:
                    logger.warning("Force killing Streamlit")
                    process.kill()
                    
            except (psutil.NoSuchProcess, ValueError):
                logger.warning("Process not found")
            finally:
                self.pid_file.unlink(missing_ok=True)
        else:
            logger.info("No PID file found")
    
    def restart(self):
        """Restart the Streamlit application"""
        logger.info("Restarting Streamlit...")
        self.stop()
        time.sleep(2)
        return self.start()
    
    def health_check(self) -> dict:
        """Check application health"""
        health = {
            'status': 'unknown',
            'uptime': 0,
            'memory_mb': 0,
            'cpu_percent': 0,
            'port': self.port,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text())
                process = psutil.Process(pid)
                
                # Get process info
                with process.oneshot():
                    health['status'] = 'running'
                    health['uptime'] = time.time() - process.create_time()
                    health['memory_mb'] = process.memory_info().rss / 1024 / 1024
                    health['cpu_percent'] = process.cpu_percent(interval=1)
                
                # Check if port is listening
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', self.port))
                sock.close()
                
                if result != 0:
                    health['status'] = 'unhealthy'
                    logger.warning(f"Port {self.port} is not responding")
                    
            except (psutil.NoSuchProcess, ValueError):
                health['status'] = 'stopped'
        else:
            health['status'] = 'stopped'
        
        return health
    
    def monitor(self):
        """Monitor and auto-restart if needed"""
        retry_count = 0
        
        while retry_count < self.max_retries:
            health = self.health_check()
            
            if health['status'] == 'stopped':
                logger.warning("Application is stopped, attempting restart...")
                if self.start():
                    retry_count = 0
                else:
                    retry_count += 1
                    time.sleep(self.retry_delay)
                    
            elif health['status'] == 'unhealthy':
                logger.warning("Application is unhealthy, restarting...")
                self.restart()
                retry_count += 1
                
            elif health['status'] == 'running':
                # Check resource usage
                if health['memory_mb'] > 1024:  # 1GB limit
                    logger.warning(f"High memory usage: {health['memory_mb']:.1f}MB")
                    self.restart()
                    
                retry_count = 0
            
            # Log health status
            logger.info(f"Health: {json.dumps(health, indent=2)}")
            
            # Sleep before next check
            time.sleep(30)  # Check every 30 seconds
        
        logger.error(f"Max retries ({self.max_retries}) reached. Giving up.")
    
    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point"""
    manager = ProcessManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, manager.handle_signal)
    signal.signal(signal.SIGINT, manager.handle_signal)
    
    # Parse command
    if len(sys.argv) < 2:
        print("Usage: process_manager.py [start|stop|restart|status|monitor]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        if manager.start():
            print(f"✅ Streamlit started on port {manager.port}")
        else:
            print("❌ Failed to start Streamlit")
            sys.exit(1)
            
    elif command == 'stop':
        manager.stop()
        print("✅ Streamlit stopped")
        
    elif command == 'restart':
        if manager.restart():
            print("✅ Streamlit restarted")
        else:
            print("❌ Failed to restart Streamlit")
            sys.exit(1)
            
    elif command == 'status':
        health = manager.health_check()
        print(json.dumps(health, indent=2))
        
    elif command == 'monitor':
        print(f"🔍 Monitoring Streamlit on port {manager.port}...")
        try:
            manager.monitor()
        except KeyboardInterrupt:
            manager.stop()
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()