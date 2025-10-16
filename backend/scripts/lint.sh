#!/bin/bash
# Script para ejecutar todas las herramientas de linting y formateo

set -e  # Salir si algún comando falla

echo "=================================="
echo "   Análisis de Calidad de Código"
echo "=================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para ejecutar comando y capturar resultado
run_check() {
    local name=$1
    local cmd=$2

    echo -e "${YELLOW}▶ Ejecutando $name...${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ $name: OK${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $name: FALLÓ${NC}"
        echo ""
        return 1
    fi
}

# Contador de errores
ERRORS=0

# 1. Black - Verificar formato
if ! run_check "Black (formato)" "black --check --diff ."; then
    echo -e "${YELLOW}  Tip: Ejecuta 'black .' para formatear automáticamente${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. isort - Verificar imports
if ! run_check "isort (imports)" "isort --check-only --diff ."; then
    echo -e "${YELLOW}  Tip: Ejecuta 'isort .' para ordenar imports automáticamente${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Flake8 - Verificar PEP8
if ! run_check "Flake8 (PEP8)" "flake8 ."; then
    ERRORS=$((ERRORS + 1))
fi

# 4. Pylint - Análisis estático
if ! run_check "Pylint (análisis estático)" "pylint --rcfile=pyproject.toml --exit-zero authentication attendance events mac_attendance"; then
    echo -e "${YELLOW}  Nota: Pylint puede mostrar warnings que no son críticos${NC}"
    # No incrementar errores, pylint es solo informativo
fi

# 5. Bandit - Seguridad
if ! run_check "Bandit (seguridad)" "bandit -r . -c pyproject.toml"; then
    ERRORS=$((ERRORS + 1))
fi

# 6. MyPy - Type checking (opcional)
echo -e "${YELLOW}▶ Ejecutando MyPy (type checking)...${NC}"
if mypy --config-file=pyproject.toml . 2>/dev/null; then
    echo -e "${GREEN}✓ MyPy: OK${NC}"
else
    echo -e "${YELLOW}⚠ MyPy: Algunos errores de tipado (no críticos)${NC}"
fi
echo ""

# Resumen
echo "=================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Todos los checks pasaron correctamente${NC}"
    echo "=================================="
    exit 0
else
    echo -e "${RED}✗ $ERRORS check(s) fallaron${NC}"
    echo "=================================="
    exit 1
fi
