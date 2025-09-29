#!/usr/bin/env python3
"""
Runner script for the Dynamic AI Chatbot project.
Provides convenient commands to start, test, and manage the chatbot.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def run_server(host="0.0.0.0", port=8000, reload=False, log_level="info"):
    """Run the FastAPI server."""
    print(f"🚀 Starting Dynamic AI Chatbot server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Auto-reload: {reload}")
    print(f"📝 Log level: {log_level}")
    print("-" * 50)
    
    # Set environment variables
    os.environ["API_HOST"] = host
    os.environ["API_PORT"] = str(port)
    os.environ["API_RELOAD"] = str(reload).lower()
    os.environ["LOG_LEVEL"] = log_level.upper()
    
    try:
        from src.main import main
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    print("-" * 50)
    
    test_commands = [
        ["python", "-m", "pytest", "tests/", "-v"],
        ["python", "test_basic.py"]
    ]
    
    for cmd in test_commands:
        try:
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)} - PASSED")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"❌ {' '.join(cmd)} - FAILED")
                if result.stderr:
                    print(result.stderr)
        except FileNotFoundError:
            print(f"⚠️  {cmd[0]} not found, skipping {' '.join(cmd)}")


def install_dependencies(minimal=False):
    """Install project dependencies."""
    print("📦 Installing dependencies...")
    print("-" * 50)
    
    if minimal:
        # Install only essential packages for basic functionality
        essential_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "pydantic-settings",
            "loguru",
            "vaderSentiment",
            "python-dotenv"
        ]
        
        cmd = ["pip", "install"] + essential_packages
        print(f"Installing minimal dependencies: {', '.join(essential_packages)}")
    else:
        # Install from requirements.txt
        cmd = ["pip", "install", "-r", "requirements.txt"]
        print("Installing from requirements.txt...")
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
        else:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)


def check_health(host="localhost", port=8000):
    """Check if the server is running."""
    print("🏥 Checking server health...")
    print("-" * 50)
    
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data.get('message', 'OK')}")
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
    except ImportError:
        print("⚠️  requests library not installed, using curl instead...")
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://{host}:{port}/health"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"✅ Server is healthy: {result.stdout}")
            else:
                print("❌ Server is not responding")
        except Exception as e:
            print(f"❌ Cannot check health: {e}")
    except Exception as e:
        print(f"❌ Server is not reachable: {e}")


def show_info():
    """Show project information and available endpoints."""
    print("🤖 Dynamic AI Chatbot - Project Information")
    print("=" * 60)
    print("📁 Project Structure:")
    print("  ├── src/                 # Source code")
    print("  │   ├── api/             # FastAPI application")
    print("  │   ├── nlp/             # NLP processing modules")
    print("  │   ├── ai/              # AI response generation")
    print("  │   ├── connectors/      # Platform integrations")
    print("  │   ├── utils/           # Utility functions")
    print("  │   └── analytics/       # Analytics and monitoring")
    print("  ├── tests/               # Test files")
    print("  └── logs/                # Application logs")
    print()
    print("🌐 Available Endpoints (when server is running):")
    print("  • Health Check:     GET  /health")
    print("  • API Docs:         GET  /docs")
    print("  • Chat:             POST /chat")
    print("  • Session Info:     GET  /session/{session_id}")
    print("  • Delete Session:   DEL  /session/{session_id}")
    print("  • Analytics:        GET  /analytics/stats")
    print("  • Slack Webhook:    POST /webhook/slack")
    print("  • Telegram Webhook: POST /webhook/telegram")
    print()
    print("🔧 Configuration:")
    print("  Set environment variables to customize:")
    print("  • API_HOST=0.0.0.0")
    print("  • API_PORT=8000")
    print("  • OPENAI_API_KEY=your_key")
    print("  • SLACK_BOT_TOKEN=your_token")
    print("  • TELEGRAM_BOT_TOKEN=your_token")


def start_dashboard_backend():
    """Start the dashboard backend server."""
    print("📊 Starting Dashboard Backend...")
    print("-" * 50)
    
    dashboard_backend_path = project_root / "dashboard" / "backend"
    if not dashboard_backend_path.exists():
        print("❌ Dashboard backend not found! Run setup first.")
        sys.exit(1)
    
    try:
        subprocess.run(["python", "app.py"], cwd=dashboard_backend_path)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard backend: {e}")
        sys.exit(1)


def start_dashboard_frontend():
    """Start the dashboard frontend server."""
    print("🎨 Starting Dashboard Frontend...")
    print("-" * 50)
    
    dashboard_frontend_path = project_root / "dashboard" / "frontend"
    if not dashboard_frontend_path.exists():
        print("❌ Dashboard frontend not found! Run setup first.")
        sys.exit(1)
    
    try:
        subprocess.run(["npm", "start"], cwd=dashboard_frontend_path)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard frontend: {e}")
        sys.exit(1)


def start_all_services():
    """Start all services (chatbot + dashboard) using the start_all.sh script."""
    print("🚀 Starting All Services...")
    print("-" * 50)
    
    start_script = project_root / "start_all.sh"
    if not start_script.exists():
        print("❌ start_all.sh script not found!")
        sys.exit(1)
    
    try:
        subprocess.run(["bash", str(start_script)], cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 All services stopped by user")
    except Exception as e:
        print(f"❌ Error starting all services: {e}")
        sys.exit(1)


def setup_dashboard():
    """Set up the dashboard components."""
    print("🏗️  Setting up Dashboard...")
    print("-" * 50)
    
    setup_script = project_root / "setup_dashboard.sh"
    if not setup_script.exists():
        print("❌ Setup script not found!")
        sys.exit(1)
    
    try:
        subprocess.run(["bash", str(setup_script)], cwd=project_root)
        print("✅ Dashboard setup completed!")
    except Exception as e:
        print(f"❌ Error setting up dashboard: {e}")
        sys.exit(1)


def docker_run():
    """Run the project using Docker Compose."""
    print("🐳 Starting with Docker Compose...")
    print("-" * 50)
    
    if not (project_root / "docker-compose.yml").exists():
        print("❌ docker-compose.yml not found!")
        sys.exit(1)
    
    try:
        subprocess.run(["docker-compose", "up", "--build"], cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 Docker containers stopped by user")
        subprocess.run(["docker-compose", "down"], cwd=project_root)
    except Exception as e:
        print(f"❌ Error running Docker: {e}")
        sys.exit(1)


def main():
    """Main runner function."""
    parser = argparse.ArgumentParser(
        description="Dynamic AI Chatbot Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runner.py                          # Start server with default settings
  python runner.py --port 3000             # Start on port 3000
  python runner.py --reload                # Start with auto-reload for development
  python runner.py test                     # Run tests
  python runner.py install                  # Install dependencies
  python runner.py install --minimal       # Install minimal dependencies
  python runner.py health                   # Check server health
  python runner.py info                     # Show project information
  python runner.py docker                   # Run with Docker Compose
  python runner.py dashboard-setup          # Set up dashboard components
  python runner.py dashboard-backend        # Start dashboard backend
  python runner.py dashboard-frontend       # Start dashboard frontend
  python runner.py all                      # Start all services (chatbot + dashboard)
        """
    )
    
    parser.add_argument(
        "command", 
        nargs="?", 
        choices=["test", "install", "health", "info", "docker", "dashboard-setup", "dashboard-backend", "dashboard-frontend", "all"],
        help="Command to execute"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", choices=["debug", "info", "warning", "error"], 
                       default="info", help="Log level (default: info)")
    parser.add_argument("--minimal", action="store_true", 
                       help="Install only minimal dependencies (use with install command)")
    
    args = parser.parse_args()
    
    if args.command == "test":
        run_tests()
    elif args.command == "install":
        install_dependencies(minimal=args.minimal)
    elif args.command == "health":
        check_health(args.host, args.port)
    elif args.command == "info":
        show_info()
    elif args.command == "docker":
        docker_run()
    elif args.command == "dashboard-setup":
        setup_dashboard()
    elif args.command == "dashboard-backend":
        start_dashboard_backend()
    elif args.command == "dashboard-frontend":
        start_dashboard_frontend()
    elif args.command == "all":
        start_all_services()
    else:
        # Default: run the server
        run_server(args.host, args.port, args.reload, args.log_level)


if __name__ == "__main__":
    main()