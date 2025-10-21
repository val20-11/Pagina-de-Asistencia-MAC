#!/bin/bash
# Script para crear un backup de la base de datos

echo "=========================================="
echo "Creación de Backup de Base de Datos MAC"
echo "=========================================="
echo ""

# Verificar que los contenedores estén corriendo
if ! docker-compose ps | grep -q "db.*Up"; then
    echo "❌ Error: El contenedor de base de datos no está corriendo"
    echo "Ejecuta: docker-compose up -d"
    exit 1
fi

echo "📦 Creando backup de la base de datos..."
echo ""

# Crear el directorio de fixtures si no existe
mkdir -p backend/fixtures

# Crear el backup
docker-compose exec -T db pg_dump -U mac_user mac_attendance > backend/fixtures/db_full_backup.sql

if [ $? -eq 0 ]; then
    # Obtener el tamaño del archivo
    SIZE=$(du -h backend/fixtures/db_full_backup.sql | cut -f1)

    echo "✅ ¡Backup creado exitosamente!"
    echo ""
    echo "📄 Archivo: backend/fixtures/db_full_backup.sql"
    echo "📊 Tamaño: $SIZE"
    echo ""
    echo "Ahora puedes compartir este backup con tus colaboradores:"
    echo "  1. Sube el archivo a GitHub:"
    echo "     git add backend/fixtures/db_full_backup.sql"
    echo "     git commit -m \"Actualizar backup de base de datos\""
    echo "     git push origin main"
    echo ""
    echo "  2. O compártelo por otro medio (Google Drive, Dropbox, etc.)"
    echo ""
else
    echo "❌ Error al crear el backup"
    exit 1
fi

echo "=========================================="
