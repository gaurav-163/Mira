#!/bin/bash

# ============================================
# Personal Knowledge Assistant - Quick Setup
# ============================================

echo "🧠 Personal Knowledge Assistant - Quick Setup"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "Checking Python installation... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found!"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check Node.js
echo -n "Checking Node.js installation... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node $NODE_VERSION"
else
    echo -e "${RED}✗${NC} Node.js not found!"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

# Check npm
echo -n "Checking npm installation... "
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓${NC} npm $NPM_VERSION"
else
    echo -e "${RED}✗${NC} npm not found!"
    exit 1
fi

echo ""
echo "=============================================="
echo "Installing Dependencies"
echo "=============================================="

# Install Python dependencies
echo -n "Installing Python packages... "
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Failed to install Python dependencies"
    exit 1
fi

# Install frontend dependencies
echo -n "Installing frontend packages... "
cd frontend
npm install > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "Failed to install frontend dependencies"
    exit 1
fi
cd ..

echo ""
echo "=============================================="
echo "Configuration"
echo "=============================================="

# Check for .env file
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}!${NC} Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}!${NC} Please edit .env and add your API keys"
    echo ""
    echo "   1. Get your Cohere API key from: https://dashboard.cohere.com/api-keys"
    echo "   2. Edit .env file: nano .env"
    echo "   3. Replace 'your-cohere-api-key-here' with your actual key"
    echo "   4. Save and run: ./start.sh"
    echo ""
    exit 0
fi

# Check if API key is set
if grep -q "your-cohere-api-key-here" .env; then
    echo -e "${YELLOW}!${NC} Please configure your API key in .env file"
    echo ""
    echo "   1. Get your key from: https://dashboard.cohere.com/api-keys"
    echo "   2. Edit .env: nano .env"
    echo "   3. Replace the placeholder with your actual key"
    echo ""
    exit 0
else
    echo -e "${GREEN}✓${NC} API key configured"
fi

# Create directories
echo -n "Creating directories... "
mkdir -p data/knowledge_base
mkdir -p data/vector_db
mkdir -p logs
echo -e "${GREEN}✓${NC}"

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Add your PDF documents to: data/knowledge_base/"
echo "   cp your-file.pdf data/knowledge_base/"
echo ""
echo "2. Start the application:"
echo "   ./start.sh"
echo ""
echo "3. Open in browser:"
echo "   http://localhost:3000"
echo ""
echo "=============================================="
echo "For help, see: README.md or INSTALLATION.md"
echo "=============================================="
