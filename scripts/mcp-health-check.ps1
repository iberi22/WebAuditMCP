<#
.SYNOPSIS
    MCP Auditor - Health Check

.DESCRIPTION
    Verifica que todas las dependencias y configuraciones estén correctas
    para ejecutar MCP Auditor.

.EXAMPLE
    .\mcp-health-check.ps1
#>

$ErrorActionPreference = "SilentlyContinue"

function Write-Check {
    param(
        [string]$Name,
        [string]$Status,  # "ok", "warning", "error", "info"
        [string]$Message
    )

    $icon = switch ($Status) {
        "ok"      { "✅"; $color = "Green" }
        "warning" { "⚠️ "; $color = "Yellow" }
        "error"   { "❌"; $color = "Red" }
        "info"    { "ℹ️ "; $color = "Cyan" }
        default   { "•"; $color = "White" }
    }

    Write-Host "$Name..." -NoNewline
    Write-Host " $icon $Message" -ForegroundColor $color
}

function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Banner
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       MCP Auditor - Health Check & Validation        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Variables para el resumen
$checks = @{
    total = 0
    passed = 0
    warnings = 0
    failed = 0
}

# Check 1: Python
Write-Host "1. " -NoNewline
$checks.total++
if (Test-Command "python") {
    $pyVersion = python --version 2>&1
    Write-Check "Python" "ok" $pyVersion
    $checks.passed++
} else {
    Write-Check "Python" "error" "No encontrado. Instala desde python.org"
    $checks.failed++
}

# Check 2: Node.js
Write-Host "2. " -NoNewline
$checks.total++
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Check "Node.js" "ok" $nodeVersion
    $checks.passed++
} else {
    Write-Check "Node.js" "error" "No encontrado. Instala desde nodejs.org"
    $checks.failed++
}

# Check 3: npm
Write-Host "3. " -NoNewline
$checks.total++
if (Test-Command "npm") {
    $npmVersion = npm --version
    Write-Check "npm" "ok" "v$npmVersion"
    $checks.passed++
} else {
    Write-Check "npm" "error" "No encontrado. Viene con Node.js"
    $checks.failed++
}

# Check 4: npx
Write-Host "4. " -NoNewline
$checks.total++
if (Test-Command "npx") {
    Write-Check "npx" "ok" "Disponible"
    $checks.passed++
} else {
    Write-Check "npx" "error" "No encontrado. Viene con npm 5.2+"
    $checks.failed++
}

# Check 5: Archivo .env
Write-Host "5. " -NoNewline
$checks.total++
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw

    # Check WAVE_API_KEY
    if ($envContent -match 'WAVE_API_KEY=(.+)') {
        $waveKey = $matches[1].Trim()
        if ($waveKey -and $waveKey -ne "your_wave_api_key_here") {
            Write-Check "Archivo .env" "ok" "WAVE_API_KEY configurada"
            $checks.passed++
        } else {
            Write-Check "Archivo .env" "warning" "WAVE_API_KEY no configurada (usar scan_axe como alternativa)"
            $checks.warnings++
        }
    } else {
        Write-Check "Archivo .env" "warning" "WAVE_API_KEY no encontrada"
        $checks.warnings++
    }
} else {
    Write-Check "Archivo .env" "error" "No existe. Copiar de .env.example"
    $checks.failed++
}

# Check 6: MCP Server
Write-Host "6. " -NoNewline
$checks.total++
if (Test-Path "mcp\server.py") {
    Write-Check "MCP Server" "ok" "mcp\server.py encontrado"
    $checks.passed++
} else {
    Write-Check "MCP Server" "error" "mcp\server.py no encontrado"
    $checks.failed++
}

# Check 7: Node tools
Write-Host "7. " -NoNewline
$checks.total++
$nodeToolsPath = "node-tools\axe-playwright.js"
if (Test-Path $nodeToolsPath) {
    Write-Check "Node Tools" "ok" "Scripts encontrados"
    $checks.passed++
} else {
    Write-Check "Node Tools" "error" "$nodeToolsPath no encontrado"
    $checks.failed++
}

# Check 8: Chrome DevTools MCP
Write-Host "8. " -NoNewline
$checks.total++
try {
    $cdpTest = npx -y chrome-devtools-mcp@latest --help 2>&1
    if ($LASTEXITCODE -eq 0 -or $cdpTest -match "Usage:") {
        Write-Check "Chrome DevTools MCP" "ok" "Disponible vía npx"
        $checks.passed++
    } else {
        Write-Check "Chrome DevTools MCP" "warning" "Puede no estar disponible"
        $checks.warnings++
    }
} catch {
    Write-Check "Chrome DevTools MCP" "warning" "No se pudo verificar"
    $checks.warnings++
}

# Check 9: Google Chrome
Write-Host "9. " -NoNewline
$checks.total++
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)
$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Check "Google Chrome" "ok" "Encontrado en $path"
        $chromeFound = $true
        $checks.passed++
        break
    }
}
if (-not $chromeFound) {
    Write-Check "Google Chrome" "warning" "No encontrado (requerido para Chrome DevTools MCP)"
    $checks.warnings++
}

# Check 10: Docker (opcional)
Write-Host "10. " -NoNewline
$checks.total++
if (Test-Command "docker") {
    $dockerVersion = docker --version
    Write-Check "Docker" "ok" "$dockerVersion (opcional)"
    $checks.passed++
} else {
    Write-Check "Docker" "info" "No instalado (opcional para deployment)"
    $checks.total--  # No contar como check obligatorio
}

# Check 11: Artifacts directory
Write-Host "11. " -NoNewline
$checks.total++
if (Test-Path "artifacts") {
    $artifactCount = (Get-ChildItem "artifacts" -File -ErrorAction SilentlyContinue).Count
    Write-Check "Artifacts dir" "ok" "$artifactCount archivo(s) en artifacts/"
    $checks.passed++
} else {
    Write-Check "Artifacts dir" "info" "Será creado automáticamente"
    $checks.total--  # No contar como check obligatorio
}

# Check 12: .vscode/mcp.json
Write-Host "12. " -NoNewline
$checks.total++
if (Test-Path ".vscode\mcp.json") {
    try {
        $mcpConfig = Get-Content ".vscode\mcp.json" -Raw | ConvertFrom-Json
        $serverCount = ($mcpConfig.servers | Get-Member -MemberType NoteProperty).Count
        Write-Check "VS Code MCP Config" "ok" "$serverCount servidor(es) configurado(s)"
        $checks.passed++
    } catch {
        Write-Check "VS Code MCP Config" "warning" "Existe pero puede tener errores de formato"
        $checks.warnings++
    }
} else {
    Write-Check "VS Code MCP Config" "warning" "No existe. Crear .vscode\mcp.json"
    $checks.warnings++
}

# Resumen
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      RESUMEN                          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$passRate = if ($checks.total -gt 0) {
    [math]::Round(($checks.passed / $checks.total) * 100, 1)
} else {
    0
}

Write-Host "Total de checks: " -NoNewline
Write-Host $checks.total -ForegroundColor Cyan

Write-Host "Pasados: " -NoNewline
Write-Host $checks.passed -ForegroundColor Green

if ($checks.warnings -gt 0) {
    Write-Host "Advertencias: " -NoNewline
    Write-Host $checks.warnings -ForegroundColor Yellow
}

if ($checks.failed -gt 0) {
    Write-Host "Fallidos: " -NoNewline
    Write-Host $checks.failed -ForegroundColor Red
}

Write-Host ""
Write-Host "Tasa de éxito: " -NoNewline
if ($passRate -ge 80) {
    Write-Host "$passRate%" -ForegroundColor Green
    $status = "LISTO PARA USAR ✅"
    $statusColor = "Green"
} elseif ($passRate -ge 60) {
    Write-Host "$passRate%" -ForegroundColor Yellow
    $status = "FUNCIONAL CON LIMITACIONES ⚠️"
    $statusColor = "Yellow"
} else {
    Write-Host "$passRate%" -ForegroundColor Red
    $status = "REQUIERE CONFIGURACIÓN ❌"
    $statusColor = "Red"
}

Write-Host ""
Write-Host "Estado: " -NoNewline
Write-Host $status -ForegroundColor $statusColor

# Recomendaciones
if ($checks.failed -gt 0 -or $checks.warnings -gt 0) {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║                   RECOMENDACIONES                     ║" -ForegroundColor Yellow
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""

    if (-not (Test-Path ".env")) {
        Write-Host "• Crear archivo .env:" -ForegroundColor Yellow
        Write-Host "  Copy-Item .env.example .env" -ForegroundColor Gray
    }

    if (-not (Test-Path ".vscode\mcp.json")) {
        Write-Host "• Crear configuración de VS Code:" -ForegroundColor Yellow
        Write-Host "  Ver PROFESSIONAL_WEB_AUDIT_GUIDE.md para ejemplos" -ForegroundColor Gray
    }

    if ($checks.failed -gt 0) {
        Write-Host "• Instalar dependencias faltantes:" -ForegroundColor Yellow
        if (-not (Test-Command "python")) {
            Write-Host "  - Python: https://www.python.org/downloads/" -ForegroundColor Gray
        }
        if (-not (Test-Command "node")) {
            Write-Host "  - Node.js: https://nodejs.org/" -ForegroundColor Gray
        }
    }
}

# Próximos pasos
if ($passRate -ge 80) {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                   PRÓXIMOS PASOS                      ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Iniciar MCP Server:" -ForegroundColor Cyan
    Write-Host "   python mcp\server.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. O iniciar con Chrome DevTools:" -ForegroundColor Cyan
    Write-Host "   .\scripts\chrome-mcp-helper.ps1 -Action start" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Ejecutar tests:" -ForegroundColor Cyan
    Write-Host "   python scripts\test_mcp_client.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Leer la guía completa:" -ForegroundColor Cyan
    Write-Host "   PROFESSIONAL_WEB_AUDIT_GUIDE.md" -ForegroundColor Gray
}

Write-Host ""
