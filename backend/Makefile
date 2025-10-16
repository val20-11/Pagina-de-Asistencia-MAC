# Makefile para comandos comunes del proyecto

.PHONY: help install install-dev lint format test coverage clean run migrate shell

# Variables
PYTHON := python
PIP := pip
MANAGE := $(PYTHON) manage.py

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Mostrar ayuda
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Instalar dependencias de producción
	@echo "$(YELLOW)Instalando dependencias de producción...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencias instaladas$(NC)"

install-dev: install ## Instalar dependencias de desarrollo
	@echo "$(YELLOW)Instalando dependencias de desarrollo...$(NC)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Dependencias de desarrollo instaladas$(NC)"
	@echo ""
	@echo "$(YELLOW)Instalando pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks instalados$(NC)"

lint: ## Ejecutar linters (flake8, pylint, bandit)
	@echo "$(YELLOW)Ejecutando análisis de código...$(NC)"
	@bash scripts/lint.sh

format: ## Formatear código automáticamente (black, isort, autopep8)
	@echo "$(YELLOW)Formateando código...$(NC)"
	@bash scripts/format.sh

test: ## Ejecutar tests
	@echo "$(YELLOW)Ejecutando tests...$(NC)"
	pytest -v

coverage: ## Ejecutar tests con cobertura
	@echo "$(YELLOW)Ejecutando tests con cobertura...$(NC)"
	pytest --cov=. --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "$(GREEN)✓ Reporte de cobertura generado en htmlcov/index.html$(NC)"

clean: ## Limpiar archivos temporales
	@echo "$(YELLOW)Limpiando archivos temporales...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Archivos temporales eliminados$(NC)"

run: ## Ejecutar servidor de desarrollo
	@echo "$(YELLOW)Iniciando servidor de desarrollo...$(NC)"
	$(MANAGE) runserver

migrate: ## Aplicar migraciones
	@echo "$(YELLOW)Aplicando migraciones...$(NC)"
	$(MANAGE) migrate

makemigrations: ## Crear migraciones
	@echo "$(YELLOW)Creando migraciones...$(NC)"
	$(MANAGE) makemigrations

shell: ## Abrir shell de Django
	$(MANAGE) shell_plus --ipython || $(MANAGE) shell

superuser: ## Crear superusuario
	$(MANAGE) createsuperuser

check: ## Verificar proyecto Django
	@echo "$(YELLOW)Verificando proyecto...$(NC)"
	$(MANAGE) check

collectstatic: ## Recolectar archivos estáticos
	@echo "$(YELLOW)Recolectando archivos estáticos...$(NC)"
	$(MANAGE) collectstatic --noinput

security: ## Verificar vulnerabilidades de seguridad
	@echo "$(YELLOW)Verificando vulnerabilidades...$(NC)"
	safety check
	bandit -r . -c pyproject.toml

pre-commit-all: ## Ejecutar pre-commit en todos los archivos
	@echo "$(YELLOW)Ejecutando pre-commit en todos los archivos...$(NC)"
	pre-commit run --all-files

setup: install-dev migrate ## Setup inicial del proyecto
	@echo ""
	@echo "$(GREEN)✓ Setup completado$(NC)"
	@echo ""
	@echo "Próximos pasos:"
	@echo "  1. Crea un superusuario: make superuser"
	@echo "  2. Ejecuta el servidor: make run"
	@echo "  3. Revisa la ayuda: make help"
