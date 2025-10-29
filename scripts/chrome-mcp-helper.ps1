<#
.SYNOPSIS
    Chrome MCP Helper - Gestión de Chrome con Remote Debugging para MCP Auditor

.DESCRIPTION
    Script para gestionar instancias de Chrome con remote debugging habilitado
    para uso con MCP Auditor y Chrome DevTools MCP.

.PARAMETER Action
    Acción a realizar: start, stop, status, clean

.PARAMETER UseProfile
    Usar perfil persistente en lugar de temporal

.PARAMETER Url
    URL inicial a abrir (default: http://localhost:3000)

.PARAMETER Port
    Puerto de remote debugging (default: 9222)

.EXAMPLE
    .\chrome-mcp-helper.ps1 -Action start
    Lanza Chrome con perfil temporal

.EXAMPLE
    .\chrome-mcp-helper.ps1 -Action start -UseProfile -Url "http://localhost:3000/admin"
    Lanza Chrome con perfil persistente y URL específica

.EXAMPLE
    .\chrome-mcp-helper.ps1 -Action status
    Muestra el estado de Chrome MCP

.EXAMPLE
    .\chrome-mcp-helper.ps1 -Action stop
    Detiene todas las instancias de Chrome con debugging

.EXAMPLE
    .\chrome-mcp-helper.ps1 -Action clean
    Limpia perfiles temporales antiguos
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "status", "clean")]
    [string]$Action = "start",

    [Parameter(Mandatory=$false)]
    [switch]$UseProfile,

    [Parameter(Mandatory=$false)]
    [string]$Url = "http://localhost:3000",

    [Parameter(Mandatory=$false)]
    [int]$Port = 9222
)

# Configuración
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$profileBaseDir = "$env:USERPROFILE\.chrome-profiles"
$profilePath = if ($UseProfile) {
    "$profileBaseDir\persistent-mcp-audit"
} else {
    "$env:TEMP\chrome-mcp-temp-$(Get-Date -Format 'yyyyMMddHHmmss')"
}

# Verificar que Chrome existe
if (-not (Test-Path $chromeExe)) {
    Write-Host "❌ Chrome no encontrado en: $chromeExe" -ForegroundColor Red
    Write-Host "   Por favor, actualiza la ruta en el script o instala Chrome." -ForegroundColor Yellow
    exit 1
}

# Funciones auxiliares
function Show-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         Chrome MCP Helper - MCP Auditor               ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Get-ChromeMCPProcesses {
    Get-Process chrome -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*remote-debugging-port=$Port*"
    }
}

function Test-DebugPort {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/json/version" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Acciones
Show-Banner

switch ($Action) {
    "start" {
        Write-Host "🚀 Lanzando Chrome con Remote Debugging..." -ForegroundColor Green
        Write-Host ""

        # Verificar si ya está corriendo
        $existing = Get-ChromeMCPProcesses
        if ($existing) {
            Write-Host "⚠️  Chrome MCP ya está corriendo (PID: $($existing.Id))" -ForegroundColor Yellow
            Write-Host "   Ejecuta: .\chrome-mcp-helper.ps1 -Action stop" -ForegroundColor Yellow
            Write-Host "   O usa el proceso existente en: http://127.0.0.1:$Port" -ForegroundColor Cyan
            exit 1
        }

        # Crear directorio de perfil
        New-Item -ItemType Directory -Force -Path $profilePath | Out-Null

        Write-Host "📊 Configuración:" -ForegroundColor Cyan
        Write-Host "   Puerto:      $Port" -ForegroundColor White
        Write-Host "   Perfil:      $profilePath" -ForegroundColor White
        Write-Host "   URL Inicial: $Url" -ForegroundColor White
        Write-Host "   Endpoint:    http://127.0.0.1:$Port" -ForegroundColor White
        Write-Host ""

        # Advertencia de seguridad
        Write-Host "⚠️  ADVERTENCIA DE SEGURIDAD:" -ForegroundColor Yellow
        Write-Host "   • El puerto de debugging da acceso COMPLETO al navegador" -ForegroundColor White
        Write-Host "   • NO navegues a sitios sensibles (banking, passwords, etc.)" -ForegroundColor White
        Write-Host "   • Cierra Chrome cuando termines" -ForegroundColor White
        Write-Host ""

        # Lanzar Chrome
        try {
            $process = Start-Process -FilePath $chromeExe -ArgumentList @(
                "--remote-debugging-port=$Port",
                "--user-data-dir=`"$profilePath`"",
                $Url
            ) -PassThru

            # Esperar a que el puerto esté listo
            Write-Host "⏳ Esperando a que Chrome inicie..." -NoNewline
            $maxWait = 10
            $waited = 0
            while (-not (Test-DebugPort) -and $waited -lt $maxWait) {
                Start-Sleep -Seconds 1
                Write-Host "." -NoNewline
                $waited++
            }
            Write-Host ""

            if (Test-DebugPort) {
                Write-Host ""
                Write-Host "✅ Chrome lanzado exitosamente!" -ForegroundColor Green
                Write-Host ""
                Write-Host "📌 Configuración en .vscode/mcp.json:" -ForegroundColor Cyan
                Write-Host '   {' -ForegroundColor Gray
                Write-Host '     "servers": {' -ForegroundColor Gray
                Write-Host '       "chrome-devtools": {' -ForegroundColor Gray
                Write-Host '         "command": "npx",' -ForegroundColor Gray
                Write-Host '         "args": ["-y", "chrome-devtools-mcp@latest",' -ForegroundColor Gray
                Write-Host "                  `"--browser-url=http://127.0.0.1:$Port`"]" -ForegroundColor Gray
                Write-Host '       }' -ForegroundColor Gray
                Write-Host '     }' -ForegroundColor Gray
                Write-Host '   }' -ForegroundColor Gray
                Write-Host ""
                Write-Host "💡 Ejemplos de prompts para el agente:" -ForegroundColor Cyan
                Write-Host '   "Toma screenshot de la página actual"' -ForegroundColor White
                Write-Host '   "Lista errores de consola"' -ForegroundColor White
                Write-Host '   "Analiza performance de la página"' -ForegroundColor White
                Write-Host '   "Ejecuta Lighthouse audit"' -ForegroundColor White
                Write-Host ""
                Write-Host "🛑 Para detener: .\chrome-mcp-helper.ps1 -Action stop" -ForegroundColor Yellow
            } else {
                Write-Host ""
                Write-Host "❌ Chrome se inició pero el puerto de debugging no responde" -ForegroundColor Red
                Write-Host "   Verifica manualmente: http://127.0.0.1:$Port/json/version" -ForegroundColor Yellow
            }

        } catch {
            Write-Host ""
            Write-Host "❌ Error al lanzar Chrome: $_" -ForegroundColor Red
            exit 1
        }
    }

    "stop" {
        Write-Host "🛑 Deteniendo Chrome con Remote Debugging..." -ForegroundColor Yellow
        Write-Host ""

        $processes = Get-ChromeMCPProcesses

        if ($processes) {
            Write-Host "   Encontrados $($processes.Count) proceso(s)" -ForegroundColor Cyan
            $processes | ForEach-Object {
                Write-Host "   • Cerrando PID: $($_.Id)" -ForegroundColor White
                Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
            }

            # Verificar que se cerraron
            Start-Sleep -Seconds 2
            $remaining = Get-ChromeMCPProcesses

            if (-not $remaining) {
                Write-Host ""
                Write-Host "✅ Chrome MCP detenido exitosamente" -ForegroundColor Green
            } else {
                Write-Host ""
                Write-Host "⚠️  Algunos procesos no se pudieron cerrar" -ForegroundColor Yellow
                Write-Host "   Intenta cerrar Chrome manualmente" -ForegroundColor Yellow
            }
        } else {
            Write-Host "ℹ️  No hay instancias de Chrome MCP corriendo" -ForegroundColor Cyan
        }
    }

    "status" {
        Write-Host "🔍 Estado de Chrome MCP" -ForegroundColor Cyan
        Write-Host ""

        $processes = Get-ChromeMCPProcesses

        if ($processes) {
            Write-Host "✅ Chrome MCP está corriendo" -ForegroundColor Green
            Write-Host ""
            Write-Host "📊 Detalles:" -ForegroundColor Cyan

            $processes | ForEach-Object {
                Write-Host "   • PID: $($_.Id)" -ForegroundColor White
                Write-Host "   • Memoria: $([math]::Round($_.WorkingSet64/1MB, 2)) MB" -ForegroundColor White
            }

            Write-Host ""

            # Test endpoint
            if (Test-DebugPort) {
                Write-Host "✅ Puerto de debugging respondiendo" -ForegroundColor Green
                Write-Host "   Endpoint: http://127.0.0.1:$Port" -ForegroundColor Cyan

                try {
                    $versionInfo = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json/version" -ErrorAction Stop
                    Write-Host "   Browser: $($versionInfo.Browser)" -ForegroundColor White
                    Write-Host "   WebSocket: $($versionInfo.webSocketDebuggerUrl)" -ForegroundColor White
                } catch {
                    Write-Host "   ⚠️  No se pudo obtener información de versión" -ForegroundColor Yellow
                }
            } else {
                Write-Host "❌ Puerto de debugging NO responde" -ForegroundColor Red
                Write-Host "   Verifica: http://127.0.0.1:$Port/json/version" -ForegroundColor Yellow
            }

            Write-Host ""
            Write-Host "📄 Páginas abiertas:" -ForegroundColor Cyan
            try {
                $pages = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json" -ErrorAction Stop
                $pages | ForEach-Object {
                    Write-Host "   • $($_.title)" -ForegroundColor White
                    Write-Host "     URL: $($_.url)" -ForegroundColor Gray
                }
            } catch {
                Write-Host "   ⚠️  No se pudieron listar las páginas" -ForegroundColor Yellow
            }

        } else {
            Write-Host "❌ Chrome MCP NO está corriendo" -ForegroundColor Red
            Write-Host ""
            Write-Host "💡 Para iniciar: .\chrome-mcp-helper.ps1 -Action start" -ForegroundColor Cyan
        }
    }

    "clean" {
        Write-Host "🧹 Limpiando perfiles temporales..." -ForegroundColor Yellow
        Write-Host ""

        # Limpiar perfiles temporales
        $tempProfiles = Get-ChildItem "$env:TEMP\chrome-mcp-temp-*" -Directory -ErrorAction SilentlyContinue

        if ($tempProfiles) {
            Write-Host "   Encontrados $($tempProfiles.Count) perfil(es) temporal(es)" -ForegroundColor Cyan

            $tempProfiles | ForEach-Object {
                try {
                    Write-Host "   • Eliminando: $($_.Name)" -ForegroundColor White
                    Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
                } catch {
                    Write-Host "     ⚠️  No se pudo eliminar: $_" -ForegroundColor Yellow
                }
            }

            Write-Host ""
            Write-Host "✅ Limpieza completada" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  No hay perfiles temporales para limpiar" -ForegroundColor Cyan
        }

        # Mostrar tamaño de perfiles persistentes
        if (Test-Path $profileBaseDir) {
            $persistentSize = (Get-ChildItem $profileBaseDir -Recurse -ErrorAction SilentlyContinue |
                Measure-Object -Property Length -Sum).Sum

            if ($persistentSize) {
                Write-Host ""
                Write-Host "📊 Perfiles persistentes:" -ForegroundColor Cyan
                Write-Host "   Ubicación: $profileBaseDir" -ForegroundColor White
                Write-Host "   Tamaño: $([math]::Round($persistentSize/1MB, 2)) MB" -ForegroundColor White
            }
        }
    }
}

Write-Host ""
