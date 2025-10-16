#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Sistema de Asistencia MAC - Instalador"
echo "========================================"
echo ""

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker no está instalado.${NC}"
    echo ""
    echo "Por favor instala Docker desde:"
    echo "https://docs.docker.com/get-docker/"
    echo ""
    exit 1
fi

# Verificar si Docker Compose está disponible
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker Compose no está disponible.${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ [1/5] Docker encontrado correctamente${NC}"
docker --version
echo ""

echo -e "${YELLOW}🔨 [2/5] Deteniendo contenedores previos (si existen)...${NC}"
docker-compose down > /dev/null 2>&1
echo ""

echo -e "${BLUE}🏗️  [3/5] Construyendo imágenes Docker...${NC}"
echo "(Esto puede tomar 5-10 minutos la primera vez)"
echo ""
if ! docker-compose build; then
    echo ""
    echo -e "${RED}❌ ERROR: Falló la construcción de imágenes${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🚀 [4/5] Iniciando contenedores...${NC}"
if ! docker-compose up -d; then
    echo ""
    echo -e "${RED}❌ ERROR: Falló al iniciar contenedores${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}⏳ [5/5] Esperando que los servicios estén listos...${NC}"
sleep 8

echo ""
echo "📊 Estado de los contenedores:"
docker-compose ps

echo ""
echo "========================================"
echo -e "${GREEN}✅ ¡Instalación completada exitosamente!${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}🌐 La aplicación está disponible en:${NC}"
echo "   http://localhost"
echo ""
echo -e "${BLUE}🔐 Panel de administración:${NC}"
echo "   http://localhost/admin"
echo ""
echo -e "${BLUE}👤 Usuario de prueba:${NC}"
echo "   Número de cuenta: 3123123"
echo ""
echo -e "${YELLOW}📚 Comandos útiles:${NC}"
echo "   Detener:    docker-compose down"
echo "   Ver logs:   docker-compose logs -f"
echo "   Reiniciar:  docker-compose restart"
echo ""
echo "📖 Para más información, consulta README.md"
echo ""
