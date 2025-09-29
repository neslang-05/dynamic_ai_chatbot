#!/bin/bash

# Quick Start Script - Simple version for development
# Starts all services with minimal logging

echo "🚀 Quick Starting All Services..."

# Kill existing services
echo "🛑 Stopping existing services..."
pkill -f "python.*runner.py" 2>/dev/null || true
pkill -f "python.*src/main.py" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true
sleep 2

# Start services in background
echo "1️⃣  Starting Main Chatbot API..."
cd /workspaces/dynamic_ai_chatbot
python src/main.py &
CHATBOT_PID=$!

echo "2️⃣  Starting Dashboard Backend..."
cd /workspaces/dynamic_ai_chatbot/dashboard/backend
python app.py &
BACKEND_PID=$!

echo "3️⃣  Starting Dashboard Frontend..."
cd /workspaces/dynamic_ai_chatbot/dashboard/frontend
npm start &
FRONTEND_PID=$!

# Return to project root
cd /workspaces/dynamic_ai_chatbot

echo ""
echo "✅ All services started!"
echo "🤖 Main Chatbot API: http://localhost:8000"
echo "📊 Dashboard Backend: http://localhost:5000" 
echo "🎨 Dashboard Frontend: http://localhost:3000"

if [ ! -z "$CODESPACE_NAME" ]; then
    echo ""
    echo "🌐 Codespace URLs:"
    echo "🤖 Main Chatbot: https://$CODESPACE_NAME-8000.app.github.dev"
    echo "📊 Backend: https://$CODESPACE_NAME-5000.app.github.dev"
    echo "🎨 Dashboard: https://$CODESPACE_NAME-3000.app.github.dev"
fi

echo ""
echo "📝 Process IDs:"
echo "Chatbot: $CHATBOT_PID"
echo "Backend: $BACKEND_PID"
echo "Frontend: $FRONTEND_PID"

echo ""
echo "To stop all services:"
echo "kill $CHATBOT_PID $BACKEND_PID $FRONTEND_PID"