#!/usr/bin/env python3
"""
Deployment automation script for Dynamic AI Chatbot
Usage: python deploy.py [platform]
Platforms: vercel, railway, render, docker
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    python_version = run_command("python --version")
    if python_version:
        print(f"✅ {python_version}")
    else:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    node_version = run_command("node --version")
    if node_version:
        print(f"✅ Node.js {node_version}")
    else:
        print("❌ Node.js not found")
        return False
    
    # Check Docker
    docker_version = run_command("docker --version")
    if docker_version:
        print(f"✅ {docker_version}")
    else:
        print("⚠️ Docker not found (optional)")
    
    return True

def build_frontend():
    """Build the React frontend"""
    print("📦 Building frontend...")
    frontend_path = Path("dashboard/frontend")
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("📥 Installing frontend dependencies...")
    if not run_command("npm install", cwd=frontend_path):
        return False
    
    # Build
    print("🔨 Building frontend...")
    if not run_command("npm run build", cwd=frontend_path):
        return False
    
    print("✅ Frontend built successfully")
    return True

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    
    # Check if Vercel CLI is installed
    if not run_command("vercel --version"):
        print("📥 Installing Vercel CLI...")
        if not run_command("npm install -g vercel"):
            print("❌ Failed to install Vercel CLI")
            return False
    
    # Build frontend first
    if not build_frontend():
        return False
    
    # Deploy
    print("🚀 Deploying to Vercel...")
    result = run_command("vercel --prod --yes")
    if result:
        print(f"✅ Deployed to Vercel: {result}")
        return True
    else:
        print("❌ Vercel deployment failed")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Check if Railway CLI is installed
    if not run_command("railway version"):
        print("📥 Installing Railway CLI...")
        install_cmd = "curl -sSL https://railway.app/install.sh | sh"
        if not run_command(install_cmd):
            print("❌ Failed to install Railway CLI")
            return False
    
    # Deploy
    print("🚀 Deploying to Railway...")
    result = run_command("railway up")
    if result:
        print("✅ Deployed to Railway successfully")
        return True
    else:
        print("❌ Railway deployment failed")
        return False

def deploy_to_render():
    """Deploy to Render (manual process)"""
    print("🚀 Deploying to Render...")
    print("📋 Render deployment requires manual setup:")
    print("1. Go to https://render.com")
    print("2. Connect your GitHub repository")
    print("3. Create a new Web Service")
    print("4. Use the settings from render.yaml")
    print("5. Set environment variables in Render dashboard")
    return True

def build_docker():
    """Build Docker image"""
    print("🐳 Building Docker image...")
    
    # Build production image
    cmd = "docker build -f Dockerfile.production -t dynamic-ai-chatbot:latest ."
    if run_command(cmd):
        print("✅ Docker image built successfully")
        
        # Optionally push to registry
        push = input("🤔 Push to GitHub Container Registry? (y/N): ")
        if push.lower() == 'y':
            # Tag and push
            repo_name = "ghcr.io/neslang-05/dynamic_ai_chatbot:latest"
            if run_command(f"docker tag dynamic-ai-chatbot:latest {repo_name}"):
                if run_command(f"docker push {repo_name}"):
                    print(f"✅ Pushed to {repo_name}")
                else:
                    print("❌ Failed to push image")
            else:
                print("❌ Failed to tag image")
        
        return True
    else:
        print("❌ Docker build failed")
        return False

def create_env_file():
    """Create production environment file"""
    print("📝 Creating production environment file...")
    
    env_content = """# Production Environment Configuration
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
MONGODB_URL=your-mongodb-connection-string

# AI Configuration
OPENAI_API_KEY=your-openai-api-key

# Security
JWT_SECRET_KEY=your-jwt-secret-key

# Optional: Session Configuration
SESSION_TIMEOUT=3600
MAX_CONTEXT_LENGTH=10

# Optional: Logging
LOG_LEVEL=INFO
"""
    
    with open(".env.production", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env.production file")
    print("⚠️ Please update the values in .env.production")

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("🤖 Dynamic AI Chatbot Deployment Tool")
        print("\nUsage: python deploy.py [platform]")
        print("\nAvailable platforms:")
        print("  vercel   - Deploy to Vercel")
        print("  railway  - Deploy to Railway")  
        print("  render   - Deploy to Render")
        print("  docker   - Build Docker image")
        print("  env      - Create environment file")
        print("\nExample: python deploy.py vercel")
        return
    
    platform = sys.argv[1].lower()
    
    print(f"🚀 Starting deployment to {platform}...")
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed")
        return
    
    # Deploy based on platform
    success = False
    
    if platform == "vercel":
        success = deploy_to_vercel()
    elif platform == "railway":
        success = deploy_to_railway()
    elif platform == "render":
        success = deploy_to_render()
    elif platform == "docker":
        success = build_docker()
    elif platform == "env":
        create_env_file()
        success = True
    else:
        print(f"❌ Unknown platform: {platform}")
        return
    
    if success:
        print(f"🎉 Deployment to {platform} completed successfully!")
        print("\n📋 Next steps:")
        print("1. Set up environment variables in your platform dashboard")
        print("2. Configure your domain (if needed)")
        print("3. Monitor logs for any issues")
        print("4. Test your deployment")
    else:
        print(f"❌ Deployment to {platform} failed")

if __name__ == "__main__":
    main()