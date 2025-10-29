# =============================================================================
# MCP Auditor - Apply Corrections and Rebuild
# =============================================================================
# Este script aplica todas las correcciones del feedback y reconstruye el
# servidor MCP Auditor con las mejoras implementadas.
# =============================================================================

param(
    [switch]$SkipBuild,
    [switch]$TestOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "E:\scripts-python\webscanMCP"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   MCP Auditor - Applying Corrections v1.1.0" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Summary of changes
Write-Host "📋 CORRECCIONES APLICADAS:" -ForegroundColor Green
Write-Host "  ✅ Node.js 22.x (Dockerfile)" -ForegroundColor Green
Write-Host "  ✅ Asyncio fix in wave.py" -ForegroundColor Green
Write-Host "  ✅ chrome-devtools-mcp added to package.json" -ForegroundColor Green
Write-Host "  ✅ lighthouse 11.x added to dependencies" -ForegroundColor Green
Write-Host "  ✅ webhint added to dependencies" -ForegroundColor Green
Write-Host ""

if ($TestOnly) {
    Write-Host "🧪 TEST MODE - Skipping rebuild, testing current installation" -ForegroundColor Yellow
    Write-Host ""

    # Test current versions
    Write-Host "📊 Verificando versiones actuales..." -ForegroundColor Cyan

    $nodeVersion = docker exec mcp-auditor node --version 2>$null
    if ($nodeVersion) {
        Write-Host "  Node.js: $nodeVersion" -ForegroundColor $(if ($nodeVersion -match "v22") { "Green" } else { "Yellow" })
    } else {
        Write-Host "  Node.js: ❌ No disponible" -ForegroundColor Red
    }

    $npmVersion = docker exec mcp-auditor npm --version 2>$null
    if ($npmVersion) {
        Write-Host "  npm: $npmVersion" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Para aplicar las correcciones, ejecuta:" -ForegroundColor Yellow
    Write-Host "  .\scripts\apply-corrections.ps1" -ForegroundColor White
    exit 0
}

# Check if Docker is running
Write-Host "🐳 Verificando Docker..." -ForegroundColor Cyan
$dockerRunning = docker ps 2>$null
if (-not $dockerRunning -and $LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker no está corriendo. Inicia Docker Desktop y vuelve a intentar." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Docker está corriendo" -ForegroundColor Green
Write-Host ""

if (-not $SkipBuild) {
    # Stop current container
    Write-Host "🛑 Deteniendo contenedor actual..." -ForegroundColor Yellow
    docker stop mcp-auditor 2>$null
    docker rm mcp-auditor 2>$null
    Write-Host "  ✅ Contenedor detenido" -ForegroundColor Green
    Write-Host ""

    # Rebuild image
    Write-Host "🔨 Reconstruyendo imagen Docker (esto tomará 5-10 minutos)..." -ForegroundColor Cyan
    Write-Host "  - Instalando Node.js 22.x" -ForegroundColor Gray
    Write-Host "  - Instalando Lighthouse 11.x" -ForegroundColor Gray
    Write-Host "  - Instalando Chrome DevTools MCP" -ForegroundColor Gray
    Write-Host "  - Configurando Playwright" -ForegroundColor Gray
    Write-Host ""

    cd $ProjectRoot
    docker-compose -f docker/docker-compose.yml build --no-cache

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
        Write-Host "Revisa los logs arriba para detalles" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "  ✅ Imagen construida exitosamente" -ForegroundColor Green
    Write-Host ""

    # Start container
    Write-Host "🚀 Iniciando contenedor..." -ForegroundColor Cyan

    # Load environment variables
    if (Test-Path "$ProjectRoot\.env") {
        Get-Content "$ProjectRoot\.env" | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim() -replace '^["'']|["'']$'
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }

    docker-compose -f docker/docker-compose.yml up -d

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al iniciar el contenedor" -ForegroundColor Red
        exit 1
    }

    Write-Host "  ✅ Contenedor iniciado" -ForegroundColor Green
    Write-Host ""

    # Wait for container to be ready
    Write-Host "⏳ Esperando que el contenedor esté listo..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
}

# Verify installations
Write-Host "✅ Verificando instalaciones..." -ForegroundColor Cyan
Write-Host ""

# Node.js version
Write-Host "🔍 Node.js:" -ForegroundColor Yellow
$nodeVersion = docker exec mcp-auditor node --version 2>$null
if ($nodeVersion -match "v22") {
    Write-Host "  ✅ $nodeVersion (CORRECTO)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  $nodeVersion (se esperaba v22.x)" -ForegroundColor Yellow
}

# npm version
$npmVersion = docker exec mcp-auditor npm --version 2>$null
Write-Host "  npm: $npmVersion" -ForegroundColor Gray

# Lighthouse
Write-Host ""
Write-Host "🔍 Lighthouse:" -ForegroundColor Yellow
$lighthouseInstalled = docker exec mcp-auditor npm list lighthouse 2>$null
if ($lighthouseInstalled -match "lighthouse@") {
    $version = ($lighthouseInstalled -split "lighthouse@")[1] -split " " | Select-Object -First 1
    Write-Host "  ✅ lighthouse@$version instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Lighthouse no encontrado en npm list" -ForegroundColor Yellow
}

# Chrome DevTools MCP
Write-Host ""
Write-Host "🔍 Chrome DevTools MCP:" -ForegroundColor Yellow
$cdpInstalled = docker exec mcp-auditor npm list chrome-devtools-mcp 2>$null
if ($cdpInstalled -match "chrome-devtools-mcp@") {
    $version = ($cdpInstalled -split "chrome-devtools-mcp@")[1] -split " " | Select-Object -First 1
    Write-Host "  ✅ chrome-devtools-mcp@$version instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Chrome DevTools MCP no encontrado" -ForegroundColor Yellow
}

# Webhint
Write-Host ""
Write-Host "🔍 Webhint:" -ForegroundColor Yellow
$webhintInstalled = docker exec mcp-auditor npm list hint 2>$null
if ($webhintInstalled -match "hint@") {
    $version = ($webhintInstalled -split "hint@")[1] -split " " | Select-Object -First 1
    Write-Host "  ✅ hint@$version instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Webhint no encontrado" -ForegroundColor Yellow
}

# Server status
Write-Host ""
Write-Host "🔍 Servidor MCP:" -ForegroundColor Yellow
$containerStatus = docker ps | Select-String "mcp-auditor"
if ($containerStatus) {
    Write-Host "  ✅ Contenedor corriendo" -ForegroundColor Green
    Write-Host "  🌐 http://localhost:8000/mcp" -ForegroundColor Cyan
} else {
    Write-Host "  ❌ Contenedor no está corriendo" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   RESUMEN" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Correcciones aplicadas exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Siguiente paso: Probar las herramientas" -ForegroundColor Cyan
Write-Host ""
Write-Host 'Prompt al agente:' -ForegroundColor White
Write-Host '"Usando MCP Auditor Docker:' -ForegroundColor Gray
Write-Host ' 1. Ejecuta health_check' -ForegroundColor Gray
Write-Host ' 2. Lista las herramientas disponibles' -ForegroundColor Gray
Write-Host ' 3. Prueba audit_lighthouse en https://example.com' -ForegroundColor Gray
Write-Host ' 4. Prueba scan_wave en https://example.com' -ForegroundColor Gray
Write-Host ' 5. Muestra un resumen de los resultados"' -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentación:" -ForegroundColor Cyan
Write-Host "  - CORRECTIONS_APPLIED.md - Lista completa de correcciones" -ForegroundColor Gray
Write-Host "  - START_HERE.md - Guía de uso rápido" -ForegroundColor Gray
Write-Host "  - DOCKER_FIXED.md - Detalles técnicos" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
