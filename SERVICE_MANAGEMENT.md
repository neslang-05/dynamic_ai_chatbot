# 🚀 Service Management Guide

## Quick Start Options

### 🎯 **Option 1: Full Production Setup (Recommended)**
```bash
./start_all.sh
```
**Features:**
- ✅ Comprehensive health checks
- ✅ Dependency verification
- ✅ Service monitoring
- ✅ Automatic log files
- ✅ Graceful shutdown on Ctrl+C
- ✅ Error handling and recovery

### ⚡ **Option 2: Quick Development Start**
```bash
./quick_start.sh
```
**Features:**
- ✅ Fast startup (no health checks)
- ✅ Background processes
- ✅ Minimal output
- ✅ Development-friendly

### 🛠️ **Option 3: Using Runner Command**
```bash
python runner.py all
```
**Features:**
- ✅ Integrated with project runner
- ✅ Same as start_all.sh
- ✅ Consistent with other commands

### 🔧 **Option 4: Manual Individual Services**
```bash
# Terminal 1: Main Chatbot API
python runner.py

# Terminal 2: Dashboard Backend  
python runner.py dashboard-backend

# Terminal 3: Dashboard Frontend
python runner.py dashboard-frontend
```

## 🛑 Stopping Services

### Stop All Services
```bash
./stop_all.sh
```

### Stop Individual Services
```bash
# By process pattern
pkill -f "python.*src/main.py"     # Main chatbot
pkill -f "python.*app.py"          # Dashboard backend
pkill -f "npm.*start"              # Dashboard frontend

# By port
kill $(lsof -ti :8000)  # Main chatbot
kill $(lsof -ti :5000)  # Dashboard backend  
kill $(lsof -ti :3000)  # Dashboard frontend
```

## 🌐 Service URLs

### Local Development
- 🤖 **Main Chatbot API**: http://localhost:8000
- 📊 **Dashboard Backend**: http://localhost:5000
- 🎨 **Dashboard Frontend**: http://localhost:3000
- 📚 **API Documentation**: http://localhost:8000/docs

### GitHub Codespaces
- 🤖 **Main Chatbot API**: https://CODESPACE-8000.app.github.dev
- 📊 **Dashboard Backend**: https://CODESPACE-5000.app.github.dev  
- 🎨 **Dashboard Frontend**: https://CODESPACE-3000.app.github.dev
- 📚 **API Documentation**: https://CODESPACE-8000.app.github.dev/docs

## 📋 Health Checks

### Quick Status Check
```bash
# Check all services
curl -s http://localhost:8000/health && echo " ✅ Chatbot API"
curl -s http://localhost:5000/api/health && echo " ✅ Dashboard Backend"
curl -s http://localhost:3000 >/dev/null && echo " ✅ Dashboard Frontend"
```

### Individual Service Tests
```bash
# Test chatbot API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test"}'

# Test dashboard backend
curl http://localhost:5000/api/kpis

# Test dashboard frontend (open in browser)
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
./stop_all.sh  # Stop all services
./start_all.sh # Restart
```

**Missing Dependencies:**
```bash
# Install main dependencies
pip install -r requirements.txt

# Install dashboard dependencies  
pip install -r dashboard/backend/requirements.txt
cd dashboard/frontend && npm install
```

**Service Won't Start:**
```bash
# Check logs
tail -f logs/chatbot.log
tail -f logs/dashboard-backend.log
tail -f logs/dashboard-frontend.log

# Check what's using ports
lsof -i :8000
lsof -i :5000  
lsof -i :3000
```

**Dashboard Can't Connect to API:**
```bash
# Verify main API is running
curl http://localhost:8000/health

# Check CORS settings in dashboard/backend/app.py
# Ensure frontend API URL is correct in dashboard/frontend/src/api.js
```

## 📁 Log Files

When using `start_all.sh`, logs are saved to:
- **Main Chatbot**: `logs/chatbot.log`
- **Dashboard Backend**: `logs/dashboard-backend.log` 
- **Dashboard Frontend**: `logs/dashboard-frontend.log`

## 🔄 Development Workflow

### For Active Development:
1. Use `./quick_start.sh` for fast iteration
2. Edit code in your IDE
3. Services auto-reload (chatbot has --reload, React has hot reload)
4. Use `./stop_all.sh` when done

### For Testing/Demo:
1. Use `./start_all.sh` for full monitoring
2. Check health endpoints
3. View logs for troubleshooting
4. Use Ctrl+C for graceful shutdown

### For Production:
1. Use Docker deployment (see docker-compose.yml)
2. Set proper environment variables
3. Use reverse proxy for HTTPS
4. Monitor with external tools

## 🎛️ Configuration

### Environment Variables
```bash
# Main Chatbot
export API_HOST=0.0.0.0
export API_PORT=8000
export OPENAI_API_KEY=your_key

# Dashboard Backend
export CHATBOT_API_URL=http://localhost:8000
export DASHBOARD_PORT=5000

# Dashboard Frontend  
export REACT_APP_API_URL=http://localhost:5000
```

### Customization
- **Ports**: Edit variables in scripts
- **Features**: Enable/disable in config files
- **Styling**: Modify Tailwind config in dashboard/frontend/
- **Data**: Adjust mock data in dashboard/backend/app.py