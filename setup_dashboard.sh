#!/bin/bash

# Dashboard Setup Script for Dynamic AI Chatbot
echo "🚀 Setting up Dynamic AI Chatbot Dashboard..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install backend dependencies
echo "📦 Installing dashboard backend dependencies..."
cd dashboard/backend
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing dashboard frontend dependencies..."
cd ../frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install npm first."
    exit 1
fi

npm install

# Install Tailwind CSS
echo "🎨 Setting up Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo "✅ Dashboard setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the main chatbot API: python runner.py"
echo "2. Start the dashboard backend: python dashboard/backend/app.py"
echo "3. Start the dashboard frontend: cd dashboard/frontend && npm start"
echo ""
echo "🌐 Access the dashboard at: http://localhost:3000"