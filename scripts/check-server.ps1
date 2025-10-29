# =============================================================================
# Helper - Verificar Servidor de Desarrollo
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Url = "http://localhost:3000"
)

Write-Host ""
Write-Host "🔍 Verificando Servidor de Desarrollo" -ForegroundColor Cyan
Write-Host "URL: $Url" -ForegroundColor Gray
Write-Host ""

# Extract host and port
if ($Url -match 'http://([^:]+):(\d+)') {
    $host = $matches[1]
    $port = $matches[2]
} else {
    Write-Host "❌ URL inválida. Use formato: http://localhost:3000" -ForegroundColor Red
    exit 1
}

# Check if server is responding
Write-Host "⏳ Probando conexión..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $Url -Method HEAD -TimeoutSec 5 -ErrorAction Stop

    Write-Host "✅ Servidor respondiendo" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalles:" -ForegroundColor Cyan
    Write-Host "  Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Gray
    Write-Host "  Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Gray
    Write-Host ""
    Write-Host "✅ El servidor está listo para auditar" -ForegroundColor Green

    exit 0

} catch {
    $errorType = $_.Exception.GetType().Name

    Write-Host "❌ Servidor no responde" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $errorType" -ForegroundColor Yellow
    Write-Host "Mensaje: $($_.Exception.Message)" -ForegroundColor Gray
    Write-Host ""

    if ($errorType -eq "WebException" -or $_.Exception.Message -match "refused") {
        Write-Host "💡 Soluciones:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1️⃣  Inicia tu servidor de desarrollo:" -ForegroundColor White
        Write-Host "   npm run dev" -ForegroundColor Gray
        Write-Host "   # o" -ForegroundColor Gray
        Write-Host "   yarn dev" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2️⃣  Verifica que el puerto sea correcto:" -ForegroundColor White
        Write-Host "   Port actual: $port" -ForegroundColor Gray
        Write-Host "   Cambia la URL si tu app usa otro puerto" -ForegroundColor Gray
        Write-Host ""
        Write-Host "3️⃣  Verifica procesos usando el puerto:" -ForegroundColor White
        Write-Host "   netstat -ano | findstr :$port" -ForegroundColor Gray
        Write-Host ""
    }

    # Check if any process is listening on the port
    Write-Host "🔍 Verificando puerto $port..." -ForegroundColor Cyan

    $connections = netstat -ano | Select-String ":$port"

    if ($connections) {
        Write-Host "✅ Hay procesos usando el puerto:" -ForegroundColor Yellow
        $connections | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        Write-Host ""
        Write-Host "⚠️  El puerto está ocupado pero el servidor no responde HTTP" -ForegroundColor Yellow
        Write-Host "   Posibles causas:" -ForegroundColor White
        Write-Host "   - El servidor está arrancando (espera 10-30 segundos)" -ForegroundColor Gray
        Write-Host "   - Error en la aplicación (revisa logs)" -ForegroundColor Gray
        Write-Host "   - Firewall bloqueando conexiones" -ForegroundColor Gray
    } else {
        Write-Host "❌ No hay procesos escuchando en puerto $port" -ForegroundColor Red
        Write-Host ""
        Write-Host "👉 Inicia tu servidor de desarrollo primero" -ForegroundColor Yellow
    }

    exit 1
}
