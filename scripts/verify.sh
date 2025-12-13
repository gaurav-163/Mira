#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "           PERSONAL KNOWLEDGE ASSISTANT"
echo "             Verification & Test Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check FastAPI
echo " FastAPI Backend:"
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    echo "    Running on http://localhost:8000"
    echo "    API Docs: http://localhost:8000/docs"
else
    echo "    Not running (start with: ./start.sh)"
fi

echo ""

# Check Knowledge Base
echo " Knowledge Base:"
PDF_COUNT=$(ls -1 knowledge_base/*.pdf 2>/dev/null | wc -l)
echo "    PDFs in folder: $PDF_COUNT"

echo ""

# Get API Status
echo "📊 System Status:"
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    STATUS=$(curl -s http://localhost:8000/api/status)
    DOCS=$(echo $STATUS | python -c "import sys, json; print(json.load(sys.stdin)['stats']['documents'])" 2>/dev/null || echo "0")
    PROVIDER=$(echo $STATUS | python -c "import sys, json; print(json.load(sys.stdin)['provider'])" 2>/dev/null || echo "N/A")
    INIT=$(echo $STATUS | python -c "import sys, json; print(json.load(sys.stdin)['initialized'])" 2>/dev/null || echo "False")
    
    echo "   🤖 LLM Provider: $PROVIDER"
    echo "   📊 Vector DB Documents: $DOCS"
    echo "    Initialized: $INIT"
fi

echo ""

# Test Chat
echo "💬 Testing Chat Functionality:"
if curl -s http://localhost:8000/api/status > /dev/null 2>&1; then
    if curl -s -X POST http://localhost:8000/api/initialize > /dev/null 2>&1; then
        echo "    Backend initialized"
    fi
    
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello"}' 2>/dev/null)
    
    if [ ! -z "$RESPONSE" ]; then
        ANSWER=$(echo $RESPONSE | python -c "import sys, json; d=json.load(sys.stdin); print(d.get('answer', 'Error')[:60])" 2>/dev/null || echo "Error")
        echo "   💬 Response: $ANSWER..."
        echo "    Chat is working!"
    else
        echo "    Chat test failed"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    SYSTEM STATUS "
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "    Access Points:"
echo "      • API: http://localhost:8000"
echo "      • Docs: http://localhost:8000/docs"
echo "      • Frontend: http://localhost:3000 (if running)"
echo ""
echo "   📁 Files:"
echo "      • PDFs: $PDF_COUNT in knowledge_base/"
echo "      • Chunks: $DOCS in vector database"
echo ""
echo "   🎯 Quick Commands:"
echo "      • Start Backend: ./start.sh"
echo "      • Start Frontend: cd frontend && ./start-frontend.sh"
echo "      • Stop All: ./stop.sh"
echo "      • View Logs: tail -f api.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
