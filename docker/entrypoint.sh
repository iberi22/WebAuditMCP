#!/bin/bash
# ==============================================================================
# MCP Auditor - Docker Entrypoint Script
# ==============================================================================
# Robust startup script with dependency checks and error handling
# ==============================================================================

set -e  # Exit on error

echo "================================================"
echo "MCP Auditor - Starting Server"
echo "================================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify Python installation
if ! command_exists python3; then
    echo "❌ ERROR: Python3 not found"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Verify Node.js installation
if ! command_exists node; then
    echo "❌ ERROR: Node.js not found"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Verify npm installation
if ! command_exists npm; then
    echo "❌ ERROR: npm not found"
    exit 1
fi
echo "✅ npm: $(npm --version)"

# Check if artifacts directory is writable
if [ ! -w "/app/artifacts" ]; then
    echo "⚠️  WARNING: /app/artifacts is not writable"
    mkdir -p /app/artifacts || echo "Failed to create artifacts directory"
fi
echo "✅ Artifacts directory: /app/artifacts"

# Display environment configuration
echo ""
echo "Environment Configuration:"
echo "- CHROME_MCP_ENABLED: ${CHROME_MCP_ENABLED:-not set}"
echo "- CHROME_HEADLESS: ${CHROME_HEADLESS:-not set}"
echo "- WAVE_API_KEY: ${WAVE_API_KEY:+***configured***}"
echo "- TEST_USERNAME: ${TEST_USERNAME:-not set}"
echo ""

# Check Python dependencies
echo "Checking Python dependencies..."
if ! python3 -c "import fastmcp" 2>/dev/null; then
    echo "⚠️  WARNING: fastmcp not found, installing dependencies..."
    pip3 install --no-cache-dir -r /app/requirements.txt || {
        echo "❌ ERROR: Failed to install Python dependencies"
        exit 1
    }
fi
echo "✅ Python dependencies OK"

# Check Node.js dependencies
echo "Checking Node.js dependencies..."
if [ ! -d "/app/node-tools/node_modules" ]; then
    echo "⚠️  WARNING: node_modules not found, installing..."
    cd /app/node-tools && npm install --omit=dev --no-audit --no-fund || {
        echo "❌ ERROR: Failed to install Node.js dependencies"
        exit 1
    }
    cd /app
fi
echo "✅ Node.js dependencies OK"

# Check Playwright browsers
echo "Checking Playwright browsers..."
if ! npx playwright --version >/dev/null 2>&1; then
    echo "⚠️  WARNING: Playwright not found, installing..."
    npx playwright install --with-deps chromium || {
        echo "❌ ERROR: Failed to install Playwright browsers"
        exit 1
    }
fi
echo "✅ Playwright browsers OK"

echo ""
echo "================================================"
echo "🚀 Starting MCP Auditor Server on port 8000"
echo "================================================"
echo ""

# Start the MCP server with HTTP transport
exec python3 /app/mcp/server.py
