#!/bin/bash

echo " Starting Next.js Frontend..."
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo " Backend not running!"
    echo "   Please start the backend first:"
    echo "   cd .. && ./start.sh"
    exit 1
fi

echo " Backend is running"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo " Starting Next.js development server..."
echo "   URL: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
