#!/usr/bin/env python3
"""
Service Status Checker for Dynamic AI Chatbot
Checks the status of all services and their health
"""

import subprocess
import requests
import psutil
from pathlib import Path
import sys


def check_port_status(port, service_name):
    """Check if a port is in use and what's using it."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            try:
                proc = psutil.Process(conn.pid)
                return f"✅ {service_name} (Port {port}): Running - {proc.name()} (PID: {conn.pid})"
            except:
                return f"✅ {service_name} (Port {port}): In use by unknown process"
    
    return f"❌ {service_name} (Port {port}): Not running"


def check_http_service(url, service_name):
    """Check if an HTTP service is responding."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"✅ {service_name}: Healthy (HTTP 200)"
        else:
            return f"⚠️  {service_name}: Responding but status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return f"❌ {service_name}: Not responding"
    except requests.exceptions.Timeout:
        return f"⚠️  {service_name}: Timeout"
    except Exception as e:
        return f"❌ {service_name}: Error - {e}"


def check_docker_services():
    """Check Docker services status."""
    project_root = Path(__file__).parent
    
    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout
            redis_running = "redis" in output and "Up" in output
            mongodb_running = "mongodb" in output and "Up" in output
            
            redis_status = "✅ Redis: Running" if redis_running else "❌ Redis: Not running"
            mongodb_status = "✅ MongoDB: Running" if mongodb_running else "❌ MongoDB: Not running"
            
            return [redis_status, mongodb_status]
        else:
            return ["❌ Docker services: Cannot check status"]
            
    except FileNotFoundError:
        return ["❌ Docker Compose: Not installed"]
    except Exception as e:
        return [f"❌ Docker services: Error - {e}"]


def check_processes():
    """Check for running chatbot processes."""
    patterns = [
        ("Chatbot API", ["src/main.py", "src\\main.py"]),
        ("Dashboard Backend", ["dashboard/backend/app.py", "dashboard\\backend\\app.py", "app.py"]),
        ("Dashboard Frontend", ["npm start", "react-scripts start"])
    ]
    
    results = []
    
    for service_name, process_patterns in patterns:
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for pattern in process_patterns:
                    if pattern in cmdline:
                        results.append(f"✅ {service_name}: Running (PID: {proc.info['pid']})")
                        found = True
                        break
                if found:
                    break
            except:
                continue
        
        if not found:
            results.append(f"❌ {service_name}: Not running")
    
    return results


def main():
    """Main status check function."""
    print("📊 Dynamic AI Chatbot - Service Status")
    print("=" * 42)
    
    # Check Docker services
    print("\n🐳 Docker Services:")
    docker_status = check_docker_services()
    for status in docker_status:
        print(f"  {status}")
    
    # Check port usage
    print("\n🔌 Port Status:")
    services = [
        (6379, "Redis"),
        (27017, "MongoDB"),
        (8000, "Chatbot API"),
        (5000, "Dashboard Backend"),
        (3000, "Dashboard Frontend")
    ]
    
    for port, service in services:
        status = check_port_status(port, service)
        print(f"  {status}")
    
    # Check process status
    print("\n🔄 Process Status:")
    process_status = check_processes()
    for status in process_status:
        print(f"  {status}")
    
    # Check HTTP health
    print("\n🌐 HTTP Health Checks:")
    http_services = [
        ("http://localhost:8000/health", "Chatbot API Health"),
        ("http://localhost:8000/docs", "Chatbot API Docs"),
        ("http://localhost:5000", "Dashboard Backend"),
        ("http://localhost:3000", "Dashboard Frontend")
    ]
    
    for url, service in http_services:
        status = check_http_service(url, service)
        print(f"  {status}")
    
    print("\n" + "=" * 42)
    print("💡 To start services: python start_services.py")
    print("💡 To stop services:  python stop_services.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)