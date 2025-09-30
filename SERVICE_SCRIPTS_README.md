# 🚀 Service Management Scripts

This directory contains Python scripts to easily manage all Dynamic AI Chatbot services on Windows (and other platforms).

## 📋 Available Scripts

### 🎯 `start_services.py` - Full Production Setup
**Recommended for comprehensive setup**

```powershell
python start_services.py
```

**Features:**
- ✅ Comprehensive dependency checks
- ✅ Port availability verification
- ✅ Service health monitoring
- ✅ Graceful shutdown handling (Ctrl+C)
- ✅ Detailed startup logs
- ✅ Error recovery and reporting

### ⚡ `quick_start.py` - Fast Development Start
**For quick development when you just want to start everything**

```powershell
python quick_start.py
```

**Features:**
- ✅ Fast startup (minimal checks)
- ✅ Background process management
- ✅ Simple output
- ✅ Development-friendly

### 📊 `check_status.py` - Service Status Checker
**Check what's running and what's not**

```powershell
python check_status.py
```

**Shows:**
- 🐳 Docker service status (Redis, MongoDB)
- 🔌 Port usage (3000, 5000, 6379, 8000, 27017)
- 🔄 Process status
- 🌐 HTTP health checks

### 🛑 `stop_services.py` - Stop All Services
**Gracefully stop all chatbot-related services**

```powershell
python stop_services.py
```

**Stops:**
- 🛑 All Python processes (API, Backend)
- 🛑 Node.js processes (Frontend)
- 🛑 Docker containers (Redis, MongoDB)
- 🛑 Processes using required ports

## 🚦 Quick Usage Guide

### Starting Fresh
```powershell
# 1. Check current status
python check_status.py

# 2. Stop any existing services (if needed)
python stop_services.py

# 3. Start all services
python quick_start.py

# 4. Verify everything is running
python check_status.py
```

### Development Workflow
```powershell
# Start services
python quick_start.py

# Work on your code...

# Stop when done
python stop_services.py
```

## 🌐 Service URLs

Once started, access your services at:

- **Chatbot API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Dashboard Frontend**: http://localhost:3000
- **Dashboard Backend**: http://localhost:5000
- **Redis**: localhost:6379
- **MongoDB**: localhost:27017

## 🔧 Prerequisites

The scripts automatically check for:

- ✅ **Python 3.9+** - Your main application runtime
- ✅ **Docker & Docker Compose** - For Redis and MongoDB
- ✅ **Node.js & npm** - For the React dashboard
- ✅ **Virtual Environment** - Will use `venv/` if available

## 📁 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Service Stack                        │
├─────────────────────────────────────────────────────────┤
│  Frontend (React)           │  Port 3000                │
│  ├─ Dashboard UI            │  npm start                │
│  └─ Real-time Analytics     │                           │
├─────────────────────────────────────────────────────────┤
│  Backend APIs               │  Ports 5000, 8000         │
│  ├─ Dashboard API (Flask)   │  python app.py            │
│  └─ Chatbot API (FastAPI)   │  python src/main.py       │
├─────────────────────────────────────────────────────────┤
│  Databases (Docker)         │  Ports 6379, 27017        │
│  ├─ Redis (Session Cache)   │  docker-compose           │
│  └─ MongoDB (Data Store)    │                           │
└─────────────────────────────────────────────────────────┘
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```powershell
python stop_services.py  # Stop conflicting services
python check_status.py   # Verify ports are free
python quick_start.py    # Restart services
```

**Services Won't Start:**
```powershell
# Check dependencies
python start_services.py  # Uses comprehensive checks

# Manual verification
docker --version
node --version
python --version
```

**Virtual Environment Issues:**
```powershell
# Ensure you're in the virtual environment
.\venv\Scripts\activate

# Install missing packages
pip install -r requirements.txt
pip install psutil requests
```

**Frontend Won't Start:**
```powershell
cd dashboard\frontend
npm install  # Reinstall dependencies
cd ..\..
python quick_start.py
```

### Manual Process Management

If scripts don't work, manage processes manually:

```powershell
# Find chatbot processes
tasklist | findstr python
tasklist | findstr node

# Kill specific process
taskkill /PID <process_id> /F

# Check Docker
docker-compose ps
docker-compose down
```

## ⚙️ Configuration

The scripts use environment variables from your `.env` file:

```bash
# Key configurations
API_HOST=0.0.0.0
API_PORT=8000
REDIS_HOST=localhost
MONGODB_URL=mongodb://localhost:27017
```

## 📝 Logs

Service logs are displayed in the terminal. For persistent logging:

- **Chatbot API**: Logs to `logs/chatbot.log` (if configured)
- **Dashboard**: Terminal output
- **Docker Services**: `docker-compose logs redis mongodb`

## 🔄 Development Tips

1. **Use `quick_start.py` for daily development** - fastest startup
2. **Use `start_services.py` for testing/production** - comprehensive checks
3. **Run `check_status.py` regularly** - verify health
4. **Always `stop_services.py` when done** - clean shutdown

## 🆘 Getting Help

If services don't start:

1. Check `check_status.py` output
2. Verify all prerequisites are installed
3. Look at terminal error messages
4. Check the main `README.md` for setup instructions
5. Ensure your `.env` file is properly configured

---

**Happy coding!** 🚀