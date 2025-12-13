#!/bin/bash

# Personal Knowledge Assistant - Startup Script

echo " Starting Personal Knowledge Assistant..."

# Check if .env exists
if [ ! -f .env ]; then
    echo " .env file not found!"
    echo "Please create a .env file with your API keys"
    exit 1
fi

# Kill existing processes
echo " Stopping existing processes..."
pkill -f "python api.py" 2>/dev/null
sleep 2

# Start FastAPI backend
echo " Starting FastAPI backend on port 8000..."
nohup uv run python api.py > api.log 2>&1 &
sleep 5

# Check if backend started
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo " FastAPI backend is running"
else
    echo "  Backend starting (this is normal)..."
    sleep 3
    if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
        echo " FastAPI backend is running"
    else
        echo " FastAPI backend failed to start - check api.log"
        exit 1
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Personal Knowledge Assistant is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo " Access points:"
echo "   • API Backend: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo " Knowledge Base: $(ls -1 knowledge_base/*.pdf 2>/dev/null | wc -l) PDFs"
echo ""
echo " To start the Next.js frontend:"
echo "   cd frontend && ./start-frontend.sh"
echo "   Then open: http://localhost:3000"
echo ""
echo "To view logs:"
echo "   • Application: tail -f logs/app.log"
echo "   • Errors only: tail -f logs/error.log"
echo "   • API output: tail -f api.log"
echo ""
echo "To stop all services:"
echo "   ./stop.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
