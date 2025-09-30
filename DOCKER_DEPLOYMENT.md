# 🐳 Docker Deployment Guide

Complete guide to run the Dynamic AI Chatbot project using Docker Compose.

## 📋 Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+ (usually included with Docker Desktop)
- **Git** (to clone the repository)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 2GB free space
- **CPU**: 2+ cores recommended

## 🚀 Quick Start

### 1. Clone and Setup
```powershell
# Clone the repository
git clone https://github.com/neslang-05/dynamic_ai_chatbot.git
cd dynamic_ai_chatbot

# Copy environment configuration
copy .env.docker .env

# Make the PowerShell script executable (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Start All Services
```powershell
# Using the PowerShell script (Recommended)
.\docker-run.ps1 start -Detached

# Or using Docker Compose directly
docker-compose up -d
```

### 3. Verify Installation
```powershell
# Check service status
.\docker-run.ps1 status

# Or manually check
docker-compose ps
```

## 🛠️ Detailed Setup Instructions

### Step 1: Environment Configuration

1. **Copy the environment file:**
   ```powershell
   copy .env.docker .env
   ```

2. **Edit `.env` file** (optional but recommended):
   ```bash
   # Essential settings (update if needed)
   MONGODB_URL=mongodb://root:password@mongodb:27017
   OPENAI_API_KEY=your_openai_api_key_here  # Optional
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
   ```

### Step 2: Build and Start Services

#### Option A: Using PowerShell Script (Recommended)
```powershell
# Build all images first
.\docker-run.ps1 build

# Start in development mode (with hot reload)
.\docker-run.ps1 dev

# OR start in production mode (with Nginx proxy)
.\docker-run.ps1 prod -Detached

# OR start basic services
.\docker-run.ps1 start -Detached
```

#### Option B: Using Docker Compose Directly
```powershell
# Build all services
docker-compose build

# Start all services in background
docker-compose up -d

# Start with production profile (includes Nginx)
docker-compose --profile production up -d
```

### Step 3: Verify Services

1. **Check running containers:**
   ```powershell
   docker-compose ps
   ```

2. **Check service health:**
   ```powershell
   # Main API health
   curl http://localhost:8000/health
   
   # Dashboard backend health  
   curl http://localhost:5000/api/health
   
   # Frontend (should return HTML)
   curl http://localhost:3000
   ```

3. **View logs:**
   ```powershell
   # All services
   .\docker-run.ps1 logs
   
   # Specific service
   docker-compose logs chatbot
   docker-compose logs dashboard-backend
   docker-compose logs dashboard-frontend
   ```

## 🌐 Access Points

Once all services are running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Chatbot API** | http://localhost:8000 | FastAPI backend |
| **API Documentation** | http://localhost:8000/docs | Swagger UI |
| **Secure Chat UI** | http://localhost:8000/static/chatbot_secure.html | Web chat interface |
| **Dashboard Backend** | http://localhost:5000 | Flask API for dashboard |
| **Dashboard Frontend** | http://localhost:3000 | React dashboard |
| **Production (Nginx)** | http://localhost | Unified access point |
| **Redis** | localhost:6379 | Cache database |
| **MongoDB** | localhost:27017 | Main database |

### Production URLs (with Nginx)
- **Main Application**: http://localhost
- **Dashboard**: http://localhost/dashboard
- **API Endpoints**: http://localhost/api/

## 🔧 Management Commands

### Using PowerShell Script

```powershell
# Start services
.\docker-run.ps1 start [-Detached] [-Build]

# Stop services  
.\docker-run.ps1 stop

# Restart services
.\docker-run.ps1 restart

# View logs
.\docker-run.ps1 logs [-Follow]

# Check status
.\docker-run.ps1 status

# Development mode (with hot reload)
.\docker-run.ps1 dev

# Production mode (with Nginx)
.\docker-run.ps1 prod

# Clean everything
.\docker-run.ps1 clean

# Show help
.\docker-run.ps1 help
```

### Using Docker Compose

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Rebuild and restart specific service
docker-compose up -d --build chatbot

# Scale services (if needed)
docker-compose up -d --scale chatbot=2

# Clean up
docker-compose down -v --rmi all
```

## 📊 Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │    │  Frontend (3000)│    │  Backend (5000) │
│   Production    │    │     React       │    │     Flask       │
│     Proxy       │    │   Dashboard     │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Chatbot (8000)  │
                    │    FastAPI      │
                    │   Main API      │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Redis (6379)   │    │ MongoDB (27017) │    │   Logs Volume   │
│     Cache       │    │    Database     │    │   Persistent    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```powershell
   # Check what's using the port
   netstat -ano | findstr :8000
   
   # Kill the process (replace PID)
   taskkill /PID <PID> /F
   ```

2. **Docker Not Running**
   ```powershell
   # Start Docker Desktop
   # Or restart Docker service
   ```

3. **Build Failures**
   ```powershell
   # Clean and rebuild
   .\docker-run.ps1 clean
   .\docker-run.ps1 build
   ```

4. **Database Connection Issues**
   ```powershell
   # Check MongoDB container
   docker-compose logs mongodb
   
   # Restart database services
   docker-compose restart mongodb redis
   ```

5. **Frontend Not Loading**
   ```powershell
   # Check frontend container logs
   docker-compose logs dashboard-frontend
   
   # Rebuild frontend
   docker-compose up -d --build dashboard-frontend
   ```

### Debug Commands

```powershell
# Enter container shell
docker-compose exec chatbot bash
docker-compose exec dashboard-backend bash

# Check container resources
docker stats

# View detailed container info
docker-compose logs --details chatbot

# Check network connectivity
docker-compose exec chatbot ping mongodb
docker-compose exec dashboard-backend ping chatbot
```

### Performance Monitoring

```powershell
# Monitor resource usage
docker stats

# Check container health
docker-compose ps

# View system resource usage
docker system df

# Clean up unused resources
docker system prune
```

## 🔄 Development Workflow

### Hot Reload Development

```powershell
# Start in development mode
.\docker-run.ps1 dev

# This enables:
# - Frontend hot reload
# - Backend auto-restart on code changes
# - Verbose logging
```

### Making Code Changes

1. **Frontend Changes**: Files in `dashboard/frontend/src/` are mounted as volumes
2. **Backend Changes**: Files in `src/` and `dashboard/backend/` are mounted
3. **Configuration Changes**: Restart services after changing `.env`

### Database Management

```powershell
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Access Redis CLI
docker-compose exec redis redis-cli

# Backup MongoDB
docker-compose exec mongodb mongodump --out /data/backup

# Restore MongoDB
docker-compose exec mongodb mongorestore /data/backup
```

## 🔐 Security Considerations

### Production Deployment

1. **Change Default Passwords**:
   ```bash
   # In .env file
   MONGODB_ROOT_PASSWORD=your-secure-password
   JWT_SECRET_KEY=your-very-secure-secret-key
   ```

2. **Enable SSL/TLS** (for production):
   - Add SSL certificates to `nginx/ssl/`
   - Update `nginx/nginx.conf` for HTTPS

3. **Environment Variables**:
   - Never commit `.env` files to version control
   - Use Docker secrets for sensitive data in production

4. **Network Security**:
   - The compose setup uses isolated networks
   - Only necessary ports are exposed

## 📈 Scaling and Production

### Horizontal Scaling

```powershell
# Scale chatbot API instances
docker-compose up -d --scale chatbot=3

# Scale dashboard backend
docker-compose up -d --scale dashboard-backend=2
```

### Production Deployment

```powershell
# Use production profile with Nginx
docker-compose --profile production up -d

# Or start production mode
.\docker-run.ps1 prod
```

### Health Monitoring

```powershell
# Check all service health
curl http://localhost:8000/health
curl http://localhost:5000/api/health
curl http://localhost:3000

# Monitor with production setup
curl http://localhost/health
curl http://localhost/dashboard/api/health
```

## 🆘 Support

### Getting Help

1. **View Logs**: `.\docker-run.ps1 logs -Follow`
2. **Check Status**: `.\docker-run.ps1 status`
3. **Clean and Restart**: `.\docker-run.ps1 clean` then `.\docker-run.ps1 start`

### Reporting Issues

When reporting issues, please include:
- Output of `docker --version` and `docker-compose --version`
- Contents of `docker-compose ps`
- Relevant log output from `docker-compose logs`
- Your environment file (without sensitive data)

---

**Happy Chatbotting! 🤖✨**