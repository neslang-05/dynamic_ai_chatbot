#!/usr/bin/env python3
"""
Quick Start Script for Dynamic AI Chatbot
A simple version that starts services with minimal checks for fast development
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path


def run_command_async(name, command, cwd=None, env=None):
    """Run a command asynchronously and return the process."""
    print(f"🚀 Starting {name}...")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=True if sys.platform == "win32" else False
        )
        print(f"  ✅ {name} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"  ❌ Failed to start {name}: {e}")
        return None


def main():
    """Quick start all services."""
    project_root = Path(__file__).parent
    
    print("⚡ Quick Starting Dynamic AI Chatbot Services...")
    print("=" * 50)
    
    # Set up environment for Python virtual environment
    env = os.environ.copy()
    venv_path = project_root / "venv"
    if venv_path.exists():
        if sys.platform == "win32":
            env["PATH"] = f"{venv_path / 'Scripts'};{env.get('PATH', '')}"
            python_cmd = str(venv_path / "Scripts" / "python.exe")
        else:
            env["PATH"] = f"{venv_path / 'bin'}:{env.get('PATH', '')}"
            python_cmd = str(venv_path / "bin" / "python")
    else:
        python_cmd = sys.executable
    
    processes = []
    
    try:
        # 1. Start Docker services (Redis & MongoDB)
        print("\n1️⃣  Starting Database Services...")
        docker_process = run_command_async(
            "Redis & MongoDB",
            ["docker-compose", "up", "redis", "mongodb", "-d"],
            cwd=project_root
        )
        time.sleep(8)  # Wait for databases to be ready
        
        # 2. Start Chatbot API
        print("\n2️⃣  Starting Chatbot API...")
        chatbot_process = run_command_async(
            "Chatbot API",
            [python_cmd, "src/main.py"],
            cwd=project_root,
            env=env
        )
        if chatbot_process:
            processes.append(("Chatbot API", chatbot_process))
        time.sleep(10)  # Wait for API to start
        
        # 3. Start Dashboard Backend
        print("\n3️⃣  Starting Dashboard Backend...")
        backend_process = run_command_async(
            "Dashboard Backend",
            [python_cmd, "app.py"],
            cwd=project_root / "dashboard" / "backend",
            env=env
        )
        if backend_process:
            processes.append(("Dashboard Backend", backend_process))
        time.sleep(5)  # Wait for backend to start
        
        # 4. Start Dashboard Frontend
        print("\n4️⃣  Starting Dashboard Frontend...")
        frontend_process = run_command_async(
            "Dashboard Frontend",
            ["npm", "start"],
            cwd=project_root / "dashboard" / "frontend"
        )
        if frontend_process:
            processes.append(("Dashboard Frontend", frontend_process))
        
        print("\n🎉 All services started!")
        print("\n📊 Access your application:")
        print("  • Chatbot API:        http://localhost:8000")
        print("  • API Documentation:  http://localhost:8000/docs")
        print("  • Dashboard:          http://localhost:3000")
        print("  • Backend API:        http://localhost:5000")
        
        print("\n💡 Services are running in the background.")
        print("💡 Check the terminal for any error messages.")
        print("💡 To stop services: run 'python stop_services.py' or use Task Manager")
        
        # Show PIDs for manual management
        print("\n🔍 Process IDs (for manual management):")
        for name, process in processes:
            print(f"  • {name}: PID {process.pid}")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"  🛑 Stopped {name}")
            except:
                pass
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()