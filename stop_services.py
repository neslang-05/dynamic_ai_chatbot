#!/usr/bin/env python3
"""
Stop Services Script for Dynamic AI Chatbot
Stops all running services related to the chatbot project
"""

import sys
import subprocess
import psutil
from pathlib import Path


def stop_processes_by_name(process_names):
    """Stop processes by their command line patterns."""
    stopped = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            for pattern in process_names:
                if pattern in cmdline:
                    print(f"🛑 Stopping {proc.info['name']} (PID: {proc.info['pid']})")
                    print(f"   Command: {cmdline[:80]}...")
                    
                    try:
                        if sys.platform == "win32":
                            # Use taskkill on Windows for better process tree termination
                            subprocess.run(
                                ["taskkill", "/F", "/T", "/PID", str(proc.info['pid'])],
                                capture_output=True
                            )
                        else:
                            proc.terminate()
                            proc.wait(timeout=5)
                        
                        stopped.append(proc.info['name'])
                        
                    except psutil.NoSuchProcess:
                        pass  # Process already stopped
                    except psutil.TimeoutExpired:
                        try:
                            proc.kill()
                        except psutil.NoSuchProcess:
                            pass
                    except Exception as e:
                        print(f"   ⚠️  Could not stop process: {e}")
                    
                    break  # Don't match multiple patterns for the same process
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return stopped


def stop_docker_services():
    """Stop Docker services."""
    project_root = Path(__file__).parent
    
    print("🛑 Stopping Docker services...")
    try:
        result = subprocess.run(
            ["docker-compose", "stop", "redis", "mongodb"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  ✅ Docker services stopped")
        else:
            print(f"  ⚠️  Docker stop result: {result.stderr}")
            
        # Also try to remove containers to free up ports
        subprocess.run(
            ["docker-compose", "down"],
            cwd=project_root,
            capture_output=True,
            timeout=30
        )
        
    except subprocess.TimeoutExpired:
        print("  ⚠️  Docker stop timed out")
    except FileNotFoundError:
        print("  ⚠️  Docker Compose not found")
    except Exception as e:
        print(f"  ⚠️  Error stopping Docker services: {e}")


def stop_port_processes(ports):
    """Stop processes using specific ports."""
    print("🔍 Checking for processes using required ports...")
    
    for port in ports:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    print(f"🛑 Stopping process on port {port}: {proc.name()} (PID: {proc.pid})")
                    
                    if sys.platform == "win32":
                        subprocess.run(
                            ["taskkill", "/F", "/PID", str(proc.pid)],
                            capture_output=True
                        )
                    else:
                        proc.terminate()
                        proc.wait(timeout=5)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception as e:
                    print(f"   ⚠️  Could not stop process on port {port}: {e}")


def main():
    """Main stop function."""
    print("🛑 Dynamic AI Chatbot - Stop All Services")
    print("=" * 45)
    
    # Patterns to match our services
    process_patterns = [
        "src/main.py",           # Chatbot API
        "src\\main.py",          # Windows path
        "app.py",                # Dashboard backend
        "dashboard/backend",     # Backend path
        "dashboard\\backend",    # Windows backend path
        "npm start",             # Frontend
        "react-scripts start",   # React dev server
        "uvicorn",               # FastAPI server
        "flask run"              # Flask server
    ]
    
    # Required ports for our services
    required_ports = [3000, 5000, 8000]
    
    # Stop processes by pattern
    print("🔍 Looking for chatbot-related processes...")
    stopped = stop_processes_by_name(process_patterns)
    
    if stopped:
        print(f"✅ Stopped {len(stopped)} processes")
    else:
        print("ℹ️  No matching processes found")
    
    print()
    
    # Stop processes using our ports
    stop_port_processes(required_ports)
    
    print()
    
    # Stop Docker services
    stop_docker_services()
    
    print()
    print("✅ Service cleanup completed!")
    print("\n💡 If some processes are still running:")
    print("  • Check Task Manager (Windows) or Activity Monitor (Mac)")
    print("  • Look for: python, node, npm, uvicorn, or flask processes")
    print("  • For Docker: run 'docker-compose down' manually")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)