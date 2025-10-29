<#
.SYNOPSIS
    Setup Test Credentials - Interactive configuration helper

.DESCRIPTION
    Guía interactiva para configurar credenciales de prueba
    para MCP Auditor en tu proyecto web.

.EXAMPLE
    .\setup-test-credentials.ps1
#>

$ErrorActionPreference = "Stop"

function Show-Banner {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   MCP Auditor - Configuración de Credenciales        ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Read-SecureInput {
    param(
        [string]$Prompt,
        [string]$Default = "",
        [bool]$IsPassword = $false
    )

    if ($Default) {
        $promptText = "$Prompt [$Default]: "
    } else {
        $promptText = "$Prompt: "
    }

    Write-Host $promptText -NoNewline -ForegroundColor Yellow

    if ($IsPassword) {
        $secure = Read-Host -AsSecureString
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        $value = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    } else {
        $value = Read-Host
    }

    if ([string]::IsNullOrWhiteSpace($value) -and $Default) {
        return $Default
    }

    return $value
}

Show-Banner

Write-Host "Esta herramienta te ayudará a configurar credenciales de prueba" -ForegroundColor Cyan
Write-Host "para testing automatizado de tu aplicación web." -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANTE: NO uses credenciales reales o de producción" -ForegroundColor Yellow
Write-Host ""

# Check if .env exists
$envExists = Test-Path ".env"
if ($envExists) {
    Write-Host "📄 Encontrado archivo .env existente" -ForegroundColor Green
    $overwrite = Read-Host "¿Deseas actualizar las credenciales existentes? (s/n)"
    if ($overwrite -ne 's' -and $overwrite -ne 'S') {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "📄 Creando nuevo archivo .env desde .env.example" -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  1. API Keys (Opcional - presiona Enter para omitir)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$waveKey = Read-SecureInput "WAVE API Key (https://wave.webaim.org/api/)" ""
$zapKey = Read-SecureInput "ZAP API Key (generada por ZAP)" ""

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  2. Usuario de Prueba Básico" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$testUser = Read-SecureInput "Username" "testuser"
$testPass = Read-SecureInput "Password" "testpass123" $true
$testEmail = Read-SecureInput "Email" "test@example.com"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  3. Usuario Administrador de Prueba" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$adminUser = Read-SecureInput "Username" "admin"
$adminPass = Read-SecureInput "Password" "admin123" $true
$adminEmail = Read-SecureInput "Email" "admin@example.com"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  4. Usuario Estudiante (CGP Sanpatricio)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$studentUser = Read-SecureInput "Username" "estudiante.prueba"
$studentPass = Read-SecureInput "Password" "estudiante123" $true
$studentEmail = Read-SecureInput "Email" "estudiante@cgpsanpatricio.com"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  5. Usuario Padre (CGP Sanpatricio)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$parentUser = Read-SecureInput "Username" "padre.prueba"
$parentPass = Read-SecureInput "Password" "padre123" $true
$parentEmail = Read-SecureInput "Email" "padre@cgpsanpatricio.com"

# Update .env file
Write-Host ""
Write-Host "💾 Guardando configuración..." -ForegroundColor Cyan

$envContent = Get-Content ".env" -Raw

# Update API keys
if ($waveKey) {
    $envContent = $envContent -replace 'WAVE_API_KEY=.*', "WAVE_API_KEY=$waveKey"
}
if ($zapKey) {
    $envContent = $envContent -replace 'ZAP_API_KEY=.*', "ZAP_API_KEY=$zapKey"
}

# Update test credentials
$envContent = $envContent -replace 'TEST_USERNAME=.*', "TEST_USERNAME=$testUser"
$envContent = $envContent -replace 'TEST_PASSWORD=.*', "TEST_PASSWORD=$testPass"
$envContent = $envContent -replace 'TEST_EMAIL=.*', "TEST_EMAIL=$testEmail"

$envContent = $envContent -replace 'TEST_ADMIN_USERNAME=.*', "TEST_ADMIN_USERNAME=$adminUser"
$envContent = $envContent -replace 'TEST_ADMIN_PASSWORD=.*', "TEST_ADMIN_PASSWORD=$adminPass"
$envContent = $envContent -replace 'TEST_ADMIN_EMAIL=.*', "TEST_ADMIN_EMAIL=$adminEmail"

$envContent = $envContent -replace 'TEST_STUDENT_USERNAME=.*', "TEST_STUDENT_USERNAME=$studentUser"
$envContent = $envContent -replace 'TEST_STUDENT_PASSWORD=.*', "TEST_STUDENT_PASSWORD=$studentPass"
$envContent = $envContent -replace 'TEST_STUDENT_EMAIL=.*', "TEST_STUDENT_EMAIL=$studentEmail"

$envContent = $envContent -replace 'TEST_PARENT_USERNAME=.*', "TEST_PARENT_USERNAME=$parentUser"
$envContent = $envContent -replace 'TEST_PARENT_PASSWORD=.*', "TEST_PARENT_PASSWORD=$parentPass"
$envContent = $envContent -replace 'TEST_PARENT_EMAIL=.*', "TEST_PARENT_EMAIL=$parentEmail"

# Save updated .env
$envContent | Set-Content ".env" -NoNewline

Write-Host ""
Write-Host "✅ Configuración guardada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Resumen de Credenciales Configuradas" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "👤 Usuario Básico:" -ForegroundColor Yellow
Write-Host "   Username: $testUser" -ForegroundColor White
Write-Host "   Email:    $testEmail" -ForegroundColor White
Write-Host ""

Write-Host "👑 Administrador:" -ForegroundColor Yellow
Write-Host "   Username: $adminUser" -ForegroundColor White
Write-Host "   Email:    $adminEmail" -ForegroundColor White
Write-Host ""

Write-Host "🎓 Estudiante:" -ForegroundColor Yellow
Write-Host "   Username: $studentUser" -ForegroundColor White
Write-Host "   Email:    $studentEmail" -ForegroundColor White
Write-Host ""

Write-Host "👨‍👩‍👧 Padre:" -ForegroundColor Yellow
Write-Host "   Username: $parentUser" -ForegroundColor White
Write-Host "   Email:    $parentEmail" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Próximos Pasos" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Crear estos usuarios en tu aplicación web" -ForegroundColor Cyan
Write-Host "2. Verificar que las credenciales funcionan manualmente" -ForegroundColor Cyan
Write-Host "3. Usar con MCP Auditor:" -ForegroundColor Cyan
Write-Host ""
Write-Host '   Prompt al agente:' -ForegroundColor Gray
Write-Host '   "Haz login automático en http://localhost:3000/login' -ForegroundColor Gray
Write-Host '    usando el usuario estudiante de prueba"' -ForegroundColor Gray
Write-Host ""
Write-Host "4. Verificar herramientas disponibles:" -ForegroundColor Cyan
Write-Host "   python scripts/test_mcp_client.py" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  Recordatorio de Seguridad:" -ForegroundColor Yellow
Write-Host "   • Archivo .env está en .gitignore" -ForegroundColor White
Write-Host "   • NO commitear credenciales al repositorio" -ForegroundColor White
Write-Host "   • Cambiar credenciales en producción" -ForegroundColor White
Write-Host ""
