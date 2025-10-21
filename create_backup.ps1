# Script para crear un backup de la base de datos en Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Creación de Backup de Base de Datos MAC" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que los contenedores estén corriendo
$dbStatus = docker-compose ps db 2>$null
if ($dbStatus -notmatch "Up") {
    Write-Host "❌ Error: El contenedor de base de datos no está corriendo" -ForegroundColor Red
    Write-Host "Ejecuta: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "📦 Creando backup de la base de datos..." -ForegroundColor Yellow
Write-Host ""

# Crear el directorio de fixtures si no existe
if (-Not (Test-Path "backend\fixtures")) {
    New-Item -ItemType Directory -Path "backend\fixtures" -Force | Out-Null
}

# Crear el backup
docker-compose exec -T db pg_dump -U mac_user mac_attendance > backend\fixtures\db_full_backup.sql

if ($LASTEXITCODE -eq 0) {
    # Obtener el tamaño del archivo
    $size = (Get-Item "backend\fixtures\db_full_backup.sql").Length / 1MB
    $sizeFormatted = "{0:N2} MB" -f $size

    Write-Host "✅ ¡Backup creado exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📄 Archivo: backend\fixtures\db_full_backup.sql" -ForegroundColor White
    Write-Host "📊 Tamaño: $sizeFormatted" -ForegroundColor White
    Write-Host ""
    Write-Host "Ahora puedes compartir este backup con tus colaboradores:" -ForegroundColor Cyan
    Write-Host "  1. Sube el archivo a GitHub:" -ForegroundColor White
    Write-Host "     git add backend/fixtures/db_full_backup.sql" -ForegroundColor Gray
    Write-Host "     git commit -m `"Actualizar backup de base de datos`"" -ForegroundColor Gray
    Write-Host "     git push origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. O compártelo por otro medio (Google Drive, Dropbox, etc.)" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Error al crear el backup" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
