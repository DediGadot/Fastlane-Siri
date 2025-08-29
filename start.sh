#!/bin/bash
set -e

cd /home/fiod/fastlane

echo "🚀 Starting Fast Lane Price Service"

# Kill any existing process
if [ -f service.pid ]; then
    PID=$(cat service.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🔄 Stopping existing service (PID: $PID)"
        kill $PID
        sleep 2
    fi
    rm -f service.pid
fi

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install/upgrade dependencies
source venv/bin/activate
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements_local.txt > /dev/null

# Start the service in background
echo "🎯 Starting service on port 8080..."
nohup python run_production.py > service.log 2>&1 &
echo $! > service.pid

# Wait a moment and check if it started
sleep 3

if ps -p $(cat service.pid) > /dev/null 2>&1; then
    PID=$(cat service.pid)
    echo "✅ Service started successfully"
    echo "   PID: $PID"
    echo "   Log: tail -f service.log"
    echo ""
    echo "🌐 Endpoints:"
    echo "   Local:  http://localhost:8080/price"
    echo "   Remote: http://$(hostname -I | awk '{print $1}'):8080/price"
    echo ""
    echo "📱 For Siri shortcut, use the Remote URL above"
    
    # Test the service
    echo "🧪 Testing service..."
    sleep 2
    if curl -s localhost:8080/health | grep -q "healthy"; then
        echo "✅ Health check passed"
    else
        echo "⚠️  Health check failed"
    fi
    
else
    echo "❌ Failed to start service"
    echo "Check service.log for errors:"
    tail service.log
    exit 1
fi