# Script para restaurar la base de datos compartida en Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Restauración de Base de Datos MAC" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que exista el archivo de backup
if (-Not (Test-Path "backend\fixtures\db_full_backup.sql")) {
    Write-Host "❌ Error: No se encontró el archivo de backup en backend\fixtures\db_full_backup.sql" -ForegroundColor Red
    Write-Host "Por favor, asegúrate de tener el archivo de backup." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Archivo de backup encontrado" -ForegroundColor Green
Write-Host ""

# Preguntar confirmación
Write-Host "⚠️  ADVERTENCIA: Este proceso eliminará todos los datos actuales de la base de datos." -ForegroundColor Yellow
$confirmacion = Read-Host "¿Estás seguro de que deseas continuar? (si/no)"

if ($confirmacion -ne "si") {
    Write-Host "❌ Operación cancelada." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔄 Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "🗑️  Eliminando volumen de base de datos anterior..." -ForegroundColor Yellow
docker volume rm pagina-de-asistencia-mac_postgres_data 2>$null

Write-Host ""
Write-Host "🚀 Iniciando contenedor de base de datos..." -ForegroundColor Yellow
docker-compose up -d db

Write-Host ""
Write-Host "⏳ Esperando a que la base de datos esté lista..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "📥 Restaurando backup..." -ForegroundColor Yellow
Get-Content backend\fixtures\db_full_backup.sql | docker-compose exec -T db psql -U mac_user -d mac_attendance

Write-Host ""
Write-Host "🚀 Iniciando todos los servicios..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "✅ ¡Base de datos restaurada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Puedes iniciar sesión con:" -ForegroundColor Cyan
Write-Host "  - Superusuario: admin / admin123" -ForegroundColor White
Write-Host "  - Asistente: 11111111" -ForegroundColor White
Write-Host "  - Estudiante: Cualquier número de cuenta de 8 dígitos" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
