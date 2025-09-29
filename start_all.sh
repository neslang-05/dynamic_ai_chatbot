#!/bin/bash

# Dynamic AI Chatbot - All Services Startup Script
# This script starts all necessary services for the complete chatbot system

set -e  # Exit on any error

PROJECT_ROOT=$(pwd)
CHATBOT_PORT=8000
DASHBOARD_BACKEND_PORT=5000
DASHBOARD_FRONTEND_PORT=3000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        print_warning "Killing existing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start within timeout period"
    return 1
}

# Function to start service in background
start_service() {
    local command="$1"
    local service_name="$2"
    local working_dir="$3"
    local log_file="$4"
    
    print_status "Starting $service_name..."
    
    if [ ! -z "$working_dir" ]; then
        cd "$working_dir"
    fi
    
    # Start the service in background and redirect output to log file
    nohup bash -c "$command" > "$log_file" 2>&1 &
    local pid=$!
    
    # Store PID for cleanup
    echo $pid >> "$PROJECT_ROOT/.service_pids"
    
    print_success "$service_name started (PID: $pid)"
    
    # Return to project root
    cd "$PROJECT_ROOT"
}

# Function to cleanup on exit
cleanup() {
    print_header "\n🛑 Shutting down services..."
    
    if [ -f "$PROJECT_ROOT/.service_pids" ]; then
        while read pid; do
            if [ ! -z "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                print_status "Stopping process $pid"
                kill -TERM "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
            fi
        done < "$PROJECT_ROOT/.service_pids"
        rm -f "$PROJECT_ROOT/.service_pids"
    fi
    
    # Kill services by port as backup
    kill_port $CHATBOT_PORT
    kill_port $DASHBOARD_BACKEND_PORT
    kill_port $DASHBOARD_FRONTEND_PORT
    
    print_success "All services stopped"
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM EXIT

# Main startup sequence
print_header "🚀 Starting Dynamic AI Chatbot - All Services"
print_header "============================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -f "runner.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create logs directory
mkdir -p logs
rm -f .service_pids

# Stop any existing services
print_status "Checking for existing services..."
if check_port $CHATBOT_PORT; then
    print_warning "Port $CHATBOT_PORT is in use"
    kill_port $CHATBOT_PORT
fi

if check_port $DASHBOARD_BACKEND_PORT; then
    print_warning "Port $DASHBOARD_BACKEND_PORT is in use"
    kill_port $DASHBOARD_BACKEND_PORT
fi

if check_port $DASHBOARD_FRONTEND_PORT; then
    print_warning "Port $DASHBOARD_FRONTEND_PORT is in use"
    kill_port $DASHBOARD_FRONTEND_PORT
fi

# Check dependencies
print_status "Checking dependencies..."

# Check Python dependencies
if ! python -c "import fastapi, uvicorn, pydantic" 2>/dev/null; then
    print_warning "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Check dashboard backend dependencies
if [ -f "dashboard/backend/requirements.txt" ]; then
    if ! python -c "import flask, flask_cors" 2>/dev/null; then
        print_warning "Installing dashboard backend dependencies..."
        pip install -r dashboard/backend/requirements.txt
    fi
fi

# Check Node.js and npm
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is required but not installed"
    exit 1
fi

# Check dashboard frontend dependencies
if [ -d "dashboard/frontend" ] && [ ! -d "dashboard/frontend/node_modules" ]; then
    print_warning "Installing dashboard frontend dependencies..."
    cd dashboard/frontend
    npm install
    cd "$PROJECT_ROOT"
fi

print_success "All dependencies checked"

# Start services
print_header "\n🔧 Starting Services..."

# 1. Start Main Chatbot API
print_status "1/3 Starting Main Chatbot API..."
start_service \
    "python runner.py --host 0.0.0.0 --port $CHATBOT_PORT" \
    "Main Chatbot API" \
    "$PROJECT_ROOT" \
    "$PROJECT_ROOT/logs/chatbot.log"

# Wait for chatbot API to be ready
if ! wait_for_service "http://localhost:$CHATBOT_PORT/health" "Main Chatbot API"; then
    print_error "Failed to start Main Chatbot API"
    exit 1
fi

# 2. Start Dashboard Backend
print_status "2/3 Starting Dashboard Backend..."
start_service \
    "python app.py" \
    "Dashboard Backend" \
    "$PROJECT_ROOT/dashboard/backend" \
    "$PROJECT_ROOT/logs/dashboard-backend.log"

# Wait for dashboard backend to be ready
if ! wait_for_service "http://localhost:$DASHBOARD_BACKEND_PORT/api/health" "Dashboard Backend"; then
    print_error "Failed to start Dashboard Backend"
    exit 1
fi

# 3. Start Dashboard Frontend
print_status "3/3 Starting Dashboard Frontend..."
start_service \
    "npm start" \
    "Dashboard Frontend" \
    "$PROJECT_ROOT/dashboard/frontend" \
    "$PROJECT_ROOT/logs/dashboard-frontend.log"

# Wait for frontend to be ready
if ! wait_for_service "http://localhost:$DASHBOARD_FRONTEND_PORT" "Dashboard Frontend"; then
    print_error "Failed to start Dashboard Frontend"
    exit 1
fi

# Display status
print_header "\n✅ All Services Started Successfully!"
print_header "====================================="

echo ""
print_success "🤖 Main Chatbot API:     http://localhost:$CHATBOT_PORT"
print_success "📊 Dashboard Backend:     http://localhost:$DASHBOARD_BACKEND_PORT"
print_success "🎨 Dashboard Frontend:    http://localhost:$DASHBOARD_FRONTEND_PORT"

if [ ! -z "$CODESPACE_NAME" ]; then
    echo ""
    print_header "🌐 Codespace URLs:"
    print_success "🤖 Main Chatbot API:     https://$CODESPACE_NAME-$CHATBOT_PORT.app.github.dev"
    print_success "📊 Dashboard Backend:     https://$CODESPACE_NAME-$DASHBOARD_BACKEND_PORT.app.github.dev"
    print_success "🎨 Dashboard Frontend:    https://$CODESPACE_NAME-$DASHBOARD_FRONTEND_PORT.app.github.dev"
fi

echo ""
print_header "📋 Quick Tests:"
echo "curl http://localhost:$CHATBOT_PORT/health"
echo "curl http://localhost:$DASHBOARD_BACKEND_PORT/api/health"
echo ""

print_header "📁 Log Files:"
echo "Main Chatbot:     logs/chatbot.log"
echo "Dashboard Backend: logs/dashboard-backend.log"
echo "Dashboard Frontend: logs/dashboard-frontend.log"

echo ""
print_warning "Press Ctrl+C to stop all services"
echo ""

# Keep script running and monitor services
print_status "Monitoring services... (Press Ctrl+C to stop)"

while true; do
    # Check if services are still running
    if ! check_port $CHATBOT_PORT; then
        print_error "Main Chatbot API stopped unexpectedly!"
        break
    fi
    
    if ! check_port $DASHBOARD_BACKEND_PORT; then
        print_error "Dashboard Backend stopped unexpectedly!"
        break
    fi
    
    if ! check_port $DASHBOARD_FRONTEND_PORT; then
        print_error "Dashboard Frontend stopped unexpectedly!"
        break
    fi
    
    sleep 10
done