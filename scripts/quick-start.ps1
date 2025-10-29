# Quick Start Script for MCP Auditor Local (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🚀 MCP Auditor Local - Quick Start" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env created. Please edit it to add your API keys if needed." -ForegroundColor Green
    Write-Host ""
}

# Check Python
Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check Node.js
Write-Host "📦 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Install Python dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
if (-not (Test-Path .venv)) {
    python -m venv .venv
}
& .venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
Write-Host "✅ Python dependencies installed" -ForegroundColor Green
Write-Host ""

# Install Node.js dependencies
Write-Host "📥 Installing Node.js dependencies..." -ForegroundColor Yellow
Set-Location node-tools
npm install --silent
Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
Write-Host ""

# Install Playwright browsers
Write-Host "🎭 Installing Playwright browsers..." -ForegroundColor Yellow
npx playwright install --with-deps chromium
Set-Location ..
Write-Host "✅ Playwright browsers installed" -ForegroundColor Green
Write-Host ""

# Run linting
Write-Host "🔍 Running linters..." -ForegroundColor Yellow
npm run lint
Write-Host "✅ Linting passed" -ForegroundColor Green
Write-Host ""

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
python -m pytest tests/ -q
Write-Host "✅ Tests completed" -ForegroundColor Green
Write-Host ""

Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the server:" -ForegroundColor Cyan
Write-Host "  python mcp/server.py" -ForegroundColor White
Write-Host ""
Write-Host "Or with Docker:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker/docker-compose.yml up -d" -ForegroundColor White
Write-Host ""
