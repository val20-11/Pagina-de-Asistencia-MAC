#!/bin/bash
# Script para formatear automáticamente el código

set -e

echo "=================================="
echo "   Formateo Automático de Código"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. isort - Ordenar imports
echo -e "${YELLOW}▶ Ordenando imports con isort...${NC}"
isort .
echo -e "${GREEN}✓ Imports ordenados${NC}"
echo ""

# 2. Black - Formatear código
echo -e "${YELLOW}▶ Formateando código con black...${NC}"
black .
echo -e "${GREEN}✓ Código formateado${NC}"
echo ""

# 3. autopep8 - Correcciones adicionales de PEP8 (opcional)
echo -e "${YELLOW}▶ Aplicando correcciones adicionales de PEP8...${NC}"
autopep8 --in-place --aggressive --aggressive --recursive .
echo -e "${GREEN}✓ Correcciones PEP8 aplicadas${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}✓ Formateo completado${NC}"
echo "=================================="
echo ""
echo "Tip: Ejecuta './scripts/lint.sh' para verificar la calidad del código"
