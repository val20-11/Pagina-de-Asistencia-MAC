# Guía de Linting y Calidad de Código

Esta guía explica cómo usar las herramientas de linting y formateo configuradas en el proyecto para mantener un código Python de alta calidad siguiendo PEP8 y mejores prácticas.

## Tabla de Contenidos

- [Herramientas Configuradas](#herramientas-configuradas)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Herramientas Individuales](#herramientas-individuales)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Integración con Docker](#integración-con-docker)
- [CI/CD](#cicd)
- [Configuración de IDEs](#configuración-de-ides)

## Herramientas Configuradas

### Formateo Automático
- **Black**: Formateador de código opinionado (PEP8)
- **isort**: Ordenador de imports
- **autopep8**: Corrector automático de PEP8

### Linting (Análisis Estático)
- **Flake8**: Verificador de estilo PEP8
- **pycodestyle**: Verificador oficial de PEP8
- **Pylint**: Analizador estático completo
- **Bandit**: Verificador de seguridad

### Type Checking
- **MyPy**: Verificador de tipos estáticos
- **django-stubs**: Type hints para Django
- **djangorestframework-stubs**: Type hints para DRF

### Testing
- **pytest**: Framework de testing
- **pytest-django**: Plugin para Django
- **pytest-cov**: Cobertura de tests
- **coverage**: Reporte de cobertura

## Instalación

### Opción 1: Usando Make (Recomendado)

```bash
# Instalar todas las dependencias de desarrollo
make install-dev
```

### Opción 2: Usando pip directamente

```bash
# Instalar dependencias de producción
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### Opción 3: En Docker

```bash
# Construir imagen con herramientas de desarrollo
docker-compose exec backend pip install -r requirements-dev.txt
```

## Uso Rápido

### Formatear Código Automáticamente

```bash
# Usando Make
make format

# O manualmente
bash scripts/format.sh
```

Este comando ejecutará automáticamente:
1. **isort** - Ordena los imports
2. **black** - Formatea el código
3. **autopep8** - Aplica correcciones adicionales de PEP8

### Verificar Calidad de Código

```bash
# Usando Make
make lint

# O manualmente
bash scripts/lint.sh
```

Este comando ejecutará:
1. Black (verificación sin modificar)
2. isort (verificación)
3. Flake8 (PEP8)
4. Pylint (análisis estático)
5. Bandit (seguridad)
6. MyPy (type checking)

### Ver Todos los Comandos Disponibles

```bash
make help
```

## Herramientas Individuales

### Black - Formateador de Código

```bash
# Verificar formato sin modificar
black --check --diff .

# Formatear todo el código
black .

# Formatear archivo específico
black path/to/file.py
```

**Configuración**: `pyproject.toml` - Longitud de línea: 120

### isort - Ordenador de Imports

```bash
# Verificar imports sin modificar
isort --check-only --diff .

# Ordenar imports
isort .

# Ordenar archivo específico
isort path/to/file.py
```

**Configuración**: `pyproject.toml` - Compatible con Black

### Flake8 - Verificador PEP8

```bash
# Verificar todo el proyecto
flake8 .

# Verificar directorio específico
flake8 authentication/

# Verificar archivo específico
flake8 path/to/file.py

# Ignorar reglas específicas
flake8 --ignore=E501,W503 .
```

**Configuración**: `.flake8`

### Pylint - Análisis Estático

```bash
# Analizar todo el código
pylint authentication attendance events mac_attendance

# Analizar archivo específico
pylint path/to/file.py

# Generar reporte de calificación
pylint --output-format=text authentication/ | tee pylint-report.txt
```

**Configuración**: `pyproject.toml`

### Bandit - Verificador de Seguridad

```bash
# Verificar seguridad en todo el proyecto
bandit -r . -c pyproject.toml

# Verificar directorio específico
bandit -r authentication/

# Generar reporte detallado
bandit -r . -f json -o bandit-report.json
```

**Configuración**: `pyproject.toml`

### MyPy - Type Checking

```bash
# Verificar tipos
mypy --config-file=pyproject.toml .

# Verificar archivo específico
mypy path/to/file.py

# Generar reporte HTML
mypy --html-report mypy-report .
```

**Configuración**: `pyproject.toml`

## Pre-commit Hooks

Los pre-commit hooks ejecutan automáticamente las herramientas de linting antes de cada commit.

### Instalar Hooks

```bash
pre-commit install
```

### Ejecutar Hooks Manualmente

```bash
# Ejecutar en archivos staged
pre-commit run

# Ejecutar en todos los archivos
pre-commit run --all-files

# Usando Make
make pre-commit-all
```

### Saltar Hooks (No Recomendado)

```bash
git commit --no-verify -m "mensaje"
```

### Actualizar Hooks

```bash
pre-commit autoupdate
```

## Integración con Docker

### Ejecutar Linting en Docker

```bash
# Formatear código
docker-compose exec backend bash scripts/format.sh

# Verificar código
docker-compose exec backend bash scripts/lint.sh

# Usando Make
docker-compose exec backend make format
docker-compose exec backend make lint
```

### Agregar al Dockerfile

```dockerfile
# En Dockerfile.backend, agregar antes del CMD
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

# Ejecutar linting en el build
RUN flake8 . || true
```

## CI/CD

### GitHub Actions

Crear `.github/workflows/lint.yml`:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements-dev.txt
      - name: Run linters
        run: |
          cd backend
          make lint
```

### GitLab CI

Crear `.gitlab-ci.yml`:

```yaml
lint:
  stage: test
  image: python:3.11
  script:
    - cd backend
    - pip install -r requirements-dev.txt
    - make lint
```

## Configuración de IDEs

### Visual Studio Code

Crear `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.banditEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "120"],
  "python.sortImports.args": ["--profile", "black"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.linting.flake8Args": ["--config=backend/.flake8"],
  "python.linting.pylintArgs": ["--rcfile=backend/pyproject.toml"]
}
```

### PyCharm

1. **Configurar Black**:
   - Settings → Tools → External Tools → Add
   - Name: Black
   - Program: `black`
   - Arguments: `$FilePath$`

2. **Configurar Flake8**:
   - Settings → Tools → External Tools → Add
   - Name: Flake8
   - Program: `flake8`
   - Arguments: `$FilePath$`

3. **Configurar File Watcher**:
   - Settings → Tools → File Watchers → Add
   - File type: Python
   - Program: `black`

## Métricas de Calidad

### Cobertura de Tests

```bash
# Ejecutar tests con cobertura
make coverage

# Ver reporte HTML
open htmlcov/index.html
```

### Complejidad Ciclomática

```bash
# Instalar radon
pip install radon

# Analizar complejidad
radon cc . -a -nb

# Generar reporte JSON
radon cc . -j > complexity-report.json
```

### Mantenibilidad

```bash
# Índice de mantenibilidad
radon mi . -s

# Mostrar solo archivos con baja mantenibilidad
radon mi . -s -n C
```

## Consejos y Mejores Prácticas

### 1. Formateo Automático

Ejecuta `make format` antes de cada commit para mantener el código formateado.

### 2. Pre-commit Hooks

Deja que los pre-commit hooks trabajen por ti. No los saltes a menos que sea absolutamente necesario.

### 3. Gradual

Si el proyecto tiene mucho código legacy, puedes aplicar linting gradualmente:

```bash
# Solo en archivos modificados
git diff --name-only | xargs flake8
```

### 4. Ignorar Reglas Específicas

Si necesitas ignorar una regla en una línea específica:

```python
# noqa: E501
long_line = "Esta línea es muy larga pero es necesaria"  # noqa: E501

# Para múltiples reglas
code = "something"  # noqa: E501,W503
```

### 5. Documentación

Mantén docstrings en funciones importantes:

```python
def calculate_attendance(student_id: int, event_id: int) -> float:
    """
    Calcula el porcentaje de asistencia de un estudiante.

    Args:
        student_id: ID del estudiante
        event_id: ID del evento

    Returns:
        Porcentaje de asistencia (0-100)

    Raises:
        ValueError: Si el estudiante o evento no existe
    """
    pass
```

## Solución de Problemas

### Error: "command not found"

Asegúrate de haber instalado las dependencias:
```bash
make install-dev
```

### Error: "pre-commit: command not found"

```bash
pip install pre-commit
pre-commit install
```

### Conflictos entre Black e isort

La configuración está ajustada para que sean compatibles. Si hay conflictos:
```bash
# Ejecutar en orden
isort .
black .
```

### Demasiados errores de Flake8

Puedes ajustar las reglas en `.flake8` o formatear automáticamente:
```bash
make format
```

## Referencias

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Pre-commit Documentation](https://pre-commit.com/)
