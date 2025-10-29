# =============================================================================
# MCP Auditor - Inicio sin Docker (modo local)
# =============================================================================

Write-Host ""
Write-Host "🐍 MCP Auditor - Modo Local (sin Docker)" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Docker no está disponible - usando Python local" -ForegroundColor Yellow
Write-Host ""

$ProjectRoot = "E:\scripts-python\webscanMCP"
cd $ProjectRoot

# Check Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python no encontrado" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host ""
Write-Host "🔍 Verificando Node.js..." -ForegroundColor Cyan
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Node.js $nodeVersion" -ForegroundColor Green

    # Check if Node is 22+
    if ($nodeVersion -match "v(\d+)\.") {
        $majorVersion = [int]$matches[1]
        if ($majorVersion -lt 22) {
            Write-Host "  ⚠️  Se requiere Node.js 22+ para Lighthouse (actual: v$majorVersion)" -ForegroundColor Yellow
            Write-Host "  📥 Descarga desde: https://nodejs.org" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  ⚠️  Node.js no encontrado (algunas herramientas no funcionarán)" -ForegroundColor Yellow
}

# Check .env
Write-Host ""
Write-Host "🔍 Verificando .env..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "  ✅ Archivo .env encontrado" -ForegroundColor Green

    # Load env vars
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim() -replace '^["'']|["'']$'
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }

    # Check critical vars
    $waveKey = $env:WAVE_API_KEY
    if ($waveKey) {
        Write-Host "  ✅ WAVE_API_KEY configurada" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WAVE_API_KEY no encontrada (scan_wave no funcionará)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "  📄 Crea uno desde .env.example" -ForegroundColor Gray
}

# Install Python dependencies
Write-Host ""
Write-Host "📦 Verificando dependencias Python..." -ForegroundColor Cyan

$pipList = pip list 2>&1
if ($pipList -match "fastmcp") {
    Write-Host "  ✅ fastmcp instalado" -ForegroundColor Green
} else {
    Write-Host "  📥 Instalando fastmcp..." -ForegroundColor Yellow
    pip install fastmcp
}

if ($pipList -match "playwright") {
    Write-Host "  ✅ playwright instalado" -ForegroundColor Green
} else {
    Write-Host "  📥 Instalando playwright..." -ForegroundColor Yellow
    pip install playwright
    playwright install chromium
}

if ($pipList -match "httpx") {
    Write-Host "  ✅ httpx instalado" -ForegroundColor Green
} else {
    Write-Host "  📥 Instalando httpx..." -ForegroundColor Yellow
    pip install httpx
}

# Install Node dependencies
Write-Host ""
Write-Host "📦 Verificando dependencias Node..." -ForegroundColor Cyan

if (Test-Path "node-tools/package.json") {
    cd node-tools

    if (-not (Test-Path "node_modules")) {
        Write-Host "  📥 Instalando paquetes npm..." -ForegroundColor Yellow
        npm install
    } else {
        Write-Host "  ✅ node_modules encontrado" -ForegroundColor Green
    }

    cd ..
}

# Start server
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Iniciando Servidor MCP Auditor" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Servidor iniciándose en:" -ForegroundColor Green
Write-Host "   http://localhost:8000/mcp" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Para detener: Presiona Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
Write-Host ""

# Start the server
python mcp/server.py
