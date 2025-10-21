#!/bin/bash
# Script para restaurar la base de datos compartida

echo "=========================================="
echo "Restauración de Base de Datos MAC"
echo "=========================================="
echo ""

# Verificar que exista el archivo de backup
if [ ! -f "backend/fixtures/db_full_backup.sql" ]; then
    echo "❌ Error: No se encontró el archivo de backup en backend/fixtures/db_full_backup.sql"
    echo "Por favor, asegúrate de tener el archivo de backup."
    exit 1
fi

echo "📋 Archivo de backup encontrado"
echo ""

# Preguntar confirmación
echo "⚠️  ADVERTENCIA: Este proceso eliminará todos los datos actuales de la base de datos."
read -p "¿Estás seguro de que deseas continuar? (si/no): " confirmacion

if [ "$confirmacion" != "si" ]; then
    echo "❌ Operación cancelada."
    exit 0
fi

echo ""
echo "🔄 Deteniendo contenedores..."
docker-compose down

echo ""
echo "🗑️  Eliminando volumen de base de datos anterior..."
docker volume rm pagina-de-asistencia-mac_postgres_data 2>/dev/null || true

echo ""
echo "🚀 Iniciando contenedor de base de datos..."
docker-compose up -d db

echo ""
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 10

echo ""
echo "📥 Restaurando backup..."
docker-compose exec -T db psql -U mac_user -d mac_attendance < backend/fixtures/db_full_backup.sql

echo ""
echo "🚀 Iniciando todos los servicios..."
docker-compose up -d

echo ""
echo "✅ ¡Base de datos restaurada exitosamente!"
echo ""
echo "Puedes iniciar sesión con:"
echo "  - Superusuario: admin / admin123"
echo "  - Asistente: 11111111"
echo "  - Estudiante: Cualquier número de cuenta de 8 dígitos"
echo ""
echo "=========================================="
