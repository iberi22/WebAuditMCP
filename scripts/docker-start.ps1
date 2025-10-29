# =============================================================================
# MCP Auditor Docker - Script de Inicio
# =============================================================================
# Este script inicia el servidor MCP Auditor en Docker cargando las
# variables de entorno necesarias desde el archivo .env
# =============================================================================

param(
    [switch]$Rebuild,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Status
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot ".env"
$DockerComposePath = Join-Path $ProjectRoot "docker\docker-compose.yml"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   MCP Auditor - Docker Management Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to load .env file
function Load-EnvFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Write-Host "⚠️  WARNING: .env file not found at $Path" -ForegroundColor Yellow
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item "$ProjectRoot\.env.example" $Path
        Write-Host "✅ Created .env file. Please configure it before continuing." -ForegroundColor Green
        Write-Host ""
        Write-Host "Run: .\scripts\setup-test-credentials.ps1" -ForegroundColor Cyan
        exit 1
    }

    Write-Host "📄 Loading environment variables from .env..." -ForegroundColor Cyan

    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()

            # Remove quotes if present
            $value = $value -replace '^["'']|["'']$'

            # Set environment variable
            [Environment]::SetEnvironmentVariable($name, $value, "Process")

            # Show loaded vars (hide sensitive data)
            if ($name -like "*KEY*" -or $name -like "*PASSWORD*") {
                if ($value) {
                    Write-Host "  ✓ $name = ***configured***" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠ $name = (not set)" -ForegroundColor Yellow
                }
            } else {
                Write-Host "  ✓ $name = $value" -ForegroundColor Green
            }
        }
    }
    Write-Host ""
}

# Show status
if ($Status) {
    Write-Host "📊 Container Status:" -ForegroundColor Cyan
    docker ps -a | Select-String "mcp-auditor"
    Write-Host ""
    Write-Host "🌐 Mapped Ports:" -ForegroundColor Cyan
    docker port mcp-auditor 2>$null
    Write-Host ""
    Write-Host "💾 Environment Variables:" -ForegroundColor Cyan
    docker exec mcp-auditor env 2>$null | Select-String "WAVE_API_KEY|TEST_USERNAME|CHROME_HEADLESS"
    exit 0
}

# Show logs
if ($Logs) {
    Write-Host "📋 Container Logs (last 50 lines):" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
    Write-Host ""
    docker logs mcp-auditor --tail 50 --follow
    exit 0
}

# Stop containers
if ($Stop) {
    Write-Host "🛑 Stopping MCP Auditor..." -ForegroundColor Yellow
    docker-compose -f $DockerComposePath down
    Write-Host "✅ Containers stopped" -ForegroundColor Green
    exit 0
}

# Load environment variables
Load-EnvFile -Path $EnvFile

# Rebuild if requested
if ($Rebuild) {
    Write-Host "🔨 Rebuilding Docker image..." -ForegroundColor Cyan
    docker-compose -f $DockerComposePath build --no-cache
    Write-Host "✅ Image rebuilt" -ForegroundColor Green
    Write-Host ""
}

# Start containers
Write-Host "🚀 Starting MCP Auditor Docker container..." -ForegroundColor Cyan
docker-compose -f $DockerComposePath up -d

# Wait for container to be healthy
Write-Host ""
Write-Host "⏳ Waiting for container to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check status
$container = docker ps | Select-String "mcp-auditor"
if ($container) {
    Write-Host "✅ MCP Auditor is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "   Server Information" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Server URL: http://localhost:8000/mcp" -ForegroundColor Green
    Write-Host "📊 Health check: http://localhost:8000/mcp" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 Configuration:" -ForegroundColor Cyan
    $waveKey = docker exec mcp-auditor env 2>$null | Select-String "WAVE_API_KEY" | Out-String
    if ($waveKey -match "WAVE_API_KEY=(.+)") {
        if ($matches[1].Trim()) {
            Write-Host "  ✓ WAVE API Key: configured" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ WAVE API Key: not configured" -ForegroundColor Yellow
        }
    }
    Write-Host "  ✓ Chrome Headless: enabled" -ForegroundColor Green
    Write-Host "  ✓ HTTP Transport: port 8000" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 Usage:" -ForegroundColor Cyan
    Write-Host "  1. Update your VS Code mcp.json with:" -ForegroundColor White
    Write-Host '     "auditor-docker": {' -ForegroundColor Gray
    Write-Host '       "url": "http://localhost:8000/mcp"' -ForegroundColor Gray
    Write-Host '     }' -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Ask your AI agent to use MCP tools" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
    Write-Host "  View logs:   .\scripts\docker-start.ps1 -Logs" -ForegroundColor Gray
    Write-Host "  Check status: .\scripts\docker-start.ps1 -Status" -ForegroundColor Gray
    Write-Host "  Stop server:  .\scripts\docker-start.ps1 -Stop" -ForegroundColor Gray
    Write-Host "  Rebuild:      .\scripts\docker-start.ps1 -Rebuild" -ForegroundColor Gray
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan

} else {
    Write-Host "❌ ERROR: Container failed to start" -ForegroundColor Red
    Write-Host ""
    Write-Host "📋 Last 30 lines of logs:" -ForegroundColor Yellow
    docker logs mcp-auditor --tail 30 2>&1
    Write-Host ""
    Write-Host "💡 Try:" -ForegroundColor Cyan
    Write-Host "  - Check logs: docker logs mcp-auditor" -ForegroundColor Gray
    Write-Host "  - Rebuild: .\scripts\docker-start.ps1 -Rebuild" -ForegroundColor Gray
    Write-Host "  - Check .env file configuration" -ForegroundColor Gray
    exit 1
}
