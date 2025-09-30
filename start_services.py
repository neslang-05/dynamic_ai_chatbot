#!/usr/bin/env python3
"""
Service Launcher for Dynamic AI Chatbot
Starts all required services: Redis, MongoDB, Chatbot API, Dashboard Backend, and Frontend
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import List, Dict, Optional
import psutil


class ServiceManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes: Dict[str, subprocess.Popen] = {}
        self.running = True
        
        # Service configurations
        self.services = {
            "docker": {
                "name": "Docker Services (Redis & MongoDB)",
                "command": ["docker-compose", "up", "redis", "mongodb", "-d"],
                "cwd": self.project_root,
                "check_command": ["docker-compose", "ps"],
                "background": True,
                "startup_delay": 5
            },
            "chatbot": {
                "name": "Chatbot API",
                "command": [sys.executable, "src/main.py"],
                "cwd": self.project_root,
                "env": self._get_chatbot_env(),
                "background": False,
                "startup_delay": 10,
                "health_check": "http://localhost:8000/health"
            },
            "dashboard_backend": {
                "name": "Dashboard Backend",
                "command": [sys.executable, "app.py"],
                "cwd": self.project_root / "dashboard" / "backend",
                "background": False,
                "startup_delay": 5,
                "health_check": "http://localhost:5000/health"
            },
            "dashboard_frontend": {
                "name": "Dashboard Frontend",
                "command": ["npm", "start"],
                "cwd": self.project_root / "dashboard" / "frontend",
                "background": False,
                "startup_delay": 15,
                "health_check": "http://localhost:3000"
            }
        }

    def _get_chatbot_env(self) -> Dict[str, str]:
        """Get environment variables for the chatbot service."""
        env = os.environ.copy()
        # Ensure the virtual environment is used
        venv_path = self.project_root / "venv"
        if venv_path.exists():
            if sys.platform == "win32":
                env["PATH"] = f"{venv_path / 'Scripts'};{env.get('PATH', '')}"
            else:
                env["PATH"] = f"{venv_path / 'bin'}:{env.get('PATH', '')}"
        return env

    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        dependencies = [
            ("Docker", ["docker", "--version"]),
            ("Docker Compose", ["docker-compose", "--version"]),
            ("Python", [sys.executable, "--version"]),
            ("Node.js", ["node", "--version"]),
            ("npm", ["npm", "--version"])
        ]
        
        missing = []
        for name, command in dependencies:
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"  ✅ {name}: Found")
                else:
                    missing.append(name)
                    print(f"  ❌ {name}: Not found or not working")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(name)
                print(f"  ❌ {name}: Not found")
        
        if missing:
            print(f"\n❌ Missing dependencies: {', '.join(missing)}")
            print("Please install the missing dependencies and try again.")
            return False
        
        print("✅ All dependencies found!")
        return True

    def check_ports(self) -> bool:
        """Check if required ports are available."""
        print("🔍 Checking port availability...")
        
        required_ports = [3000, 5000, 6379, 8000, 27017]
        busy_ports = []
        
        for port in required_ports:
            if self._is_port_in_use(port):
                busy_ports.append(port)
                print(f"  ⚠️  Port {port}: In use")
            else:
                print(f"  ✅ Port {port}: Available")
        
        if busy_ports:
            print(f"\n⚠️  Ports in use: {busy_ports}")
            print("You may need to stop existing services or the script will attempt to use existing services.")
            return True  # Continue anyway, might be our own services
        
        print("✅ All required ports are available!")
        return True

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False

    def start_service(self, service_name: str, config: Dict) -> bool:
        """Start a single service."""
        print(f"🚀 Starting {config['name']}...")
        
        try:
            if service_name == "docker":
                # Handle Docker services specially
                result = subprocess.run(
                    config["command"],
                    cwd=config["cwd"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"  ✅ {config['name']} started successfully")
                    time.sleep(config.get("startup_delay", 5))
                    return True
                else:
                    print(f"  ❌ Failed to start {config['name']}: {result.stderr}")
                    return False
            else:
                # Start regular services
                env = config.get("env", os.environ.copy())
                process = subprocess.Popen(
                    config["command"],
                    cwd=config["cwd"],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                self.processes[service_name] = process
                
                # Start output monitoring in a separate thread
                if not config.get("background", False):
                    threading.Thread(
                        target=self._monitor_service_output,
                        args=(service_name, process),
                        daemon=True
                    ).start()
                
                # Wait for startup
                print(f"  ⏳ Waiting {config.get('startup_delay', 5)} seconds for {config['name']} to start...")
                time.sleep(config.get("startup_delay", 5))
                
                # Check if process is still running
                if process.poll() is None:
                    print(f"  ✅ {config['name']} started successfully (PID: {process.pid})")
                    return True
                else:
                    print(f"  ❌ {config['name']} failed to start")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Error starting {config['name']}: {e}")
            return False

    def _monitor_service_output(self, service_name: str, process: subprocess.Popen):
        """Monitor service output and display important messages."""
        for line in iter(process.stdout.readline, ''):
            if not self.running:
                break
            line = line.strip()
            if line:
                # Filter and display important messages
                if any(keyword in line.lower() for keyword in 
                       ['error', 'failed', 'exception', 'starting', 'running', 'listening']):
                    print(f"  [{service_name.upper()}] {line}")

    def check_service_health(self, service_name: str, config: Dict) -> bool:
        """Check if a service is healthy."""
        health_check = config.get("health_check")
        if not health_check:
            return True
        
        try:
            import requests
            response = requests.get(health_check, timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_all_services(self):
        """Start all services in order."""
        print("🚀 Dynamic AI Chatbot - Service Launcher")
        print("=" * 50)
        
        # Check dependencies and ports
        if not self.check_dependencies():
            return False
        
        self.check_ports()
        print()
        
        # Start services in order
        for service_name, config in self.services.items():
            if not self.start_service(service_name, config):
                print(f"\n❌ Failed to start {config['name']}. Stopping...")
                self.stop_all_services()
                return False
            print()
        
        print("🎉 All services started successfully!")
        print("\n📊 Service URLs:")
        print("  • Chatbot API:        http://localhost:8000")
        print("  • API Documentation:  http://localhost:8000/docs")
        print("  • Dashboard Backend:  http://localhost:5000")
        print("  • Dashboard Frontend: http://localhost:3000")
        print("  • Redis:              localhost:6379")
        print("  • MongoDB:            localhost:27017")
        print("\n💡 Press Ctrl+C to stop all services")
        
        return True

    def stop_all_services(self):
        """Stop all running services."""
        print("\n🛑 Stopping all services...")
        
        # Stop Python processes
        for service_name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"  🛑 Stopping {service_name}...")
                try:
                    if sys.platform == "win32":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], 
                                     capture_output=True)
                    else:
                        process.terminate()
                        process.wait(timeout=10)
                except:
                    if sys.platform != "win32":
                        process.kill()
        
        # Stop Docker services
        try:
            print("  🛑 Stopping Docker services...")
            subprocess.run(
                ["docker-compose", "stop", "redis", "mongodb"],
                cwd=self.project_root,
                capture_output=True,
                timeout=30
            )
        except:
            pass
        
        print("✅ All services stopped!")

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\n🛑 Received shutdown signal...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

    def run(self):
        """Main run method."""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start all services
        if self.start_all_services():
            try:
                # Keep the main thread alive
                while self.running:
                    time.sleep(1)
                    
                    # Check if any critical process has died
                    for service_name, process in list(self.processes.items()):
                        if process and process.poll() is not None:
                            print(f"\n⚠️  {service_name} process has stopped unexpectedly!")
                            
            except KeyboardInterrupt:
                pass
        
        self.stop_all_services()


def main():
    """Main entry point."""
    try:
        manager = ServiceManager()
        manager.run()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()