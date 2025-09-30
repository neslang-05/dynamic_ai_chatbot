# 🚀 Quick Start - Docker Deployment

## Prerequisites
- Docker Desktop installed and running
- 4GB+ RAM available
- 2GB+ free disk space

## 1-Minute Setup

```powershell
# Clone the repository
git clone https://github.com/neslang-05/dynamic_ai_chatbot.git
cd dynamic_ai_chatbot

# Copy environment file
copy .env.docker .env

# Start all services
.\docker-run.ps1 start -Detached

# Check status
.\docker-run.ps1 status
```

## Access Your Chatbot

| Service | URL | Purpose |
|---------|-----|---------|
| 🤖 **Chatbot UI** | http://localhost:8000/static/chatbot_secure.html | Main chat interface |
| 📊 **Dashboard** | http://localhost:3000 | Analytics dashboard |
| 📚 **API Docs** | http://localhost:8000/docs | API documentation |

## Essential Commands

```powershell
# Start everything
.\docker-run.ps1 start -Detached

# Stop everything  
.\docker-run.ps1 stop

# View live logs
.\docker-run.ps1 logs -Follow

# Development mode (hot reload)
.\docker-run.ps1 dev

# Production mode (with Nginx)
.\docker-run.ps1 prod

# Clean restart
.\docker-run.ps1 clean
.\docker-run.ps1 build
.\docker-run.ps1 start -Detached
```

## Troubleshooting

**Services won't start?**
```powershell
# Check what's running
docker-compose ps

# View error logs
.\docker-run.ps1 logs

# Clean and rebuild
.\docker-run.ps1 clean
.\docker-run.ps1 build
```

**Port conflicts?**
```powershell
# Check port usage
netstat -ano | findstr :8000

# Kill conflicting process
taskkill /PID <PID> /F
```

**Need help?**
```powershell
.\docker-run.ps1 help
```

## Architecture Overview

```
🌐 Frontend (3000) ← User Interface
     ↓
📊 Dashboard Backend (5000) ← Analytics API  
     ↓
🤖 Chatbot API (8000) ← Main AI Service
     ↓
🗄️ Redis (6379) + MongoDB (27017) ← Data Storage
```

## What's Included

- ✅ FastAPI chatbot with NLP capabilities
- ✅ React analytics dashboard  
- ✅ Redis session management
- ✅ MongoDB conversation storage
- ✅ Authentication system
- ✅ Multi-platform connectors (Slack, Telegram)
- ✅ Real-time analytics
- ✅ Production-ready Nginx proxy

## Development vs Production

**Development Mode** (`.\docker-run.ps1 dev`):
- Hot reload enabled
- Verbose logging
- Direct port access
- Development-friendly settings

**Production Mode** (`.\docker-run.ps1 prod`):
- Nginx reverse proxy
- Optimized builds
- Unified access point
- Production security settings

---
**Need the full guide?** See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)