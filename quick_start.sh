#!/bin/bash

# ContextCloud Agents - Quick Start Script
# AWS AI Agents Hack Day

set -e

echo "🚀 Starting ContextCloud Agents..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the contextcloud root directory"
    exit 1
fi

echo "✅ Found ContextCloud project"

# Set up environment
echo "🔧 Setting up environment..."
chmod +x setup_env.sh
./setup_env.sh

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Start Weaviate
echo "🐳 Starting Weaviate..."
if ! docker ps | grep -q weaviate; then
    echo "Starting Weaviate container..."
    docker run -d \
        --name weaviate \
        -p 8080:8080 \
        -p 50051:50051 \
        -e QUERY_DEFAULTS_LIMIT=25 \
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
        -e PERSISTENCE_DATA_PATH='/var/lib/weaviate' \
        -e DEFAULT_VECTORIZER_MODULE='none' \
        -e CLUSTER_HOSTNAME='node1' \
        semitechnologies/weaviate:latest
    
    echo "⏳ Waiting for Weaviate to start..."
    sleep 10
else
    echo "✅ Weaviate is already running"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Backend dependencies installed"

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo "✅ Frontend dependencies installed"

# Create frontend environment file
echo "🔧 Setting up frontend environment..."
echo "REACT_APP_API_URL=http://localhost:8000" > .env

echo "✅ Frontend environment configured"

# Start backend in background
echo "🚀 Starting backend server..."
cd ../backend
source venv/bin/activate
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running and healthy"
else
    echo "❌ Backend failed to start. Check backend.log for details"
    exit 1
fi

# Start frontend
echo "🚀 Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "🎉 ContextCloud Agents is now running!"
echo ""
echo "📋 Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  Weaviate: http://localhost:8080"
echo ""
echo "📊 System Status:"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo "  Weaviate: Running in Docker"
echo ""
echo "🔧 To stop the system:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  docker stop weaviate"
echo ""
echo "📚 Check the README.md for usage instructions"
echo "🎯 Ready for AWS AI Agents Hack Day demo!"

# Keep script running
echo "Press Ctrl+C to stop all services"
wait
