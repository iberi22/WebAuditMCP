#!/bin/bash
# Quick Start Script for MCP Auditor Local

set -e

echo "🚀 MCP Auditor Local - Quick Start"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created. Please edit it to add your API keys if needed."
    echo ""
fi

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Check Node.js
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"
echo ""

# Install Python dependencies
echo "📥 Installing Python dependencies..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
cd node-tools
npm install --silent
echo "✅ Node.js dependencies installed"
echo ""

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
npx playwright install --with-deps chromium
cd ..
echo "✅ Playwright browsers installed"
echo ""

# Run linting
echo "🔍 Running linters..."
npm run lint
echo "✅ Linting passed"
echo ""

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -q
echo "✅ Tests completed"
echo ""

echo "✨ Setup complete!"
echo ""
echo "To start the server:"
echo "  python mcp/server.py"
echo ""
echo "Or with Docker:"
echo "  docker-compose -f docker/docker-compose.yml up -d"
echo ""
