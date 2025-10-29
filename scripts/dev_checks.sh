#!/usr/bin/env bash
# Development checks script for MCP Auditor Local

set -euo pipefail

echo "🔍 Running MCP Auditor Local Development Checks"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "mcp/server.py" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo "📋 Checking Python code quality..."

# Python linting with ruff
echo "Running ruff check..."
if ruff check mcp; then
    print_status 0 "Ruff linting passed"
else
    print_status 1 "Ruff linting failed"
    exit 1
fi

# Python formatting with black
echo "Running black format check..."
if black --check mcp; then
    print_status 0 "Black formatting passed"
else
    print_status 1 "Black formatting failed"
    echo "Run 'black mcp' to fix formatting issues"
    exit 1
fi

echo ""
echo "📋 Checking Node.js code quality..."

# Change to node-tools directory
cd node-tools

# Node.js linting
echo "Running ESLint..."
if npm run lint; then
    print_status 0 "ESLint passed"
else
    print_status 1 "ESLint failed"
    cd ..
    exit 1
fi

# Node.js formatting check
echo "Running Prettier check..."
if npm run format:check; then
    print_status 0 "Prettier formatting passed"
else
    print_status 1 "Prettier formatting failed"
    echo "Run 'npm run format' to fix formatting issues"
    cd ..
    exit 1
fi

# Node.js tests
echo "Running Node.js tests..."
if npm test; then
    print_status 0 "Node.js tests passed"
else
    print_status 1 "Node.js tests failed"
    cd ..
    exit 1
fi

# Return to project root
cd ..

echo ""
echo "📋 Running Python tests..."

# Python tests
if python -m pytest tests/ -v; then
    print_status 0 "Python tests passed"
else
    print_status 1 "Python tests failed"
    exit 1
fi

echo ""
echo "📋 Running E2E tests..."

# E2E tests
if python scripts/run_e2e.py; then
    print_status 0 "E2E tests passed"
else
    print_status 1 "E2E tests failed"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 All development checks passed!${NC}"
echo "=============================================="