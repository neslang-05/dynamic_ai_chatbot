#!/bin/bash

# Stop All Services Script

echo "🛑 Stopping Dynamic AI Chatbot Services..."

# Function to kill processes by pattern
kill_by_pattern() {
    local pattern="$1"
    local service_name="$2"
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null || true)
    if [ ! -z "$pids" ]; then
        echo "Stopping $service_name..."
        echo "$pids" | xargs kill -TERM 2>/dev/null || true
        sleep 2
        # Force kill if still running
        echo "$pids" | xargs kill -9 2>/dev/null || true
        echo "✅ $service_name stopped"
    else
        echo "ℹ️  $service_name not running"
    fi
}

# Function to kill by port
kill_by_port() {
    local port="$1"
    local service_name="$2"
    
    local pid=$(lsof -ti :$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        echo "Stopping $service_name on port $port (PID: $pid)..."
        kill -TERM $pid 2>/dev/null || kill -9 $pid 2>/dev/null || true
        echo "✅ $service_name stopped"
    else
        echo "ℹ️  No service running on port $port"
    fi
}

# Stop services by process pattern
kill_by_pattern "python.*src/main.py" "Main Chatbot API"
kill_by_pattern "python.*runner.py" "Chatbot Runner"
kill_by_pattern "python.*app.py" "Dashboard Backend"
kill_by_pattern "npm.*start" "Dashboard Frontend"
kill_by_pattern "node.*react-scripts" "React Development Server"

# Stop services by port as backup
kill_by_port 8000 "Chatbot API"
kill_by_port 5000 "Dashboard Backend"
kill_by_port 3000 "Dashboard Frontend"

# Clean up PID file if exists
if [ -f ".service_pids" ]; then
    echo "Cleaning up PID file..."
    rm -f .service_pids
fi

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "To start all services again:"
echo "  ./start_all.sh      # Full monitoring version"
echo "  ./quick_start.sh    # Quick development version"
echo "  python runner.py all # Using runner command"