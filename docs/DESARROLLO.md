# Guía de Desarrollo - Sistema de Asistencia MAC

Esta guía describe cómo configurar y usar el entorno de desarrollo con todas las herramientas de calidad de código, testing y análisis.

## Índice

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Herramientas de Desarrollo](#herramientas-de-desarrollo)
3. [Testing con Tox](#testing-con-tox)
4. [Acceso a PostgreSQL](#acceso-a-postgresql)
5. [Comandos Útiles](#comandos-útiles)
6. [Flujo de Trabajo](#flujo-de-trabajo)

---

## Configuración del Entorno

### Requisitos Previos

- Docker y Docker Compose instalados
- Git
- Puerto 80 (nginx), 5432 (PostgreSQL) disponibles

### Iniciar Entorno de Desarrollo

**Opción 1: Usando docker-compose.dev.yml (Recomendado para desarrollo)**

```bash
# Construir e iniciar todos los servicios
docker-compose -f docker-compose.dev.yml up --build

# En modo detached (segundo plano)
docker-compose -f docker-compose.dev.yml up -d --build
```

**Opción 2: Usando docker-compose.yml (Producción)**

```bash
docker-compose up --build
```

### Diferencias entre Entornos

| Característica | docker-compose.yml (Producción) | docker-compose.dev.yml (Desarrollo) |
|----------------|--------------------------------|-------------------------------------|
| Servidor | Gunicorn (3 workers) | Django runserver |
| Herramientas dev | ❌ No incluidas | ✅ Tox, pytest, linters, etc. |
| Puerto PostgreSQL | ✅ Expuesto (5432) | ✅ Expuesto (5432) |
| Debugging | ❌ Limitado | ✅ ipdb, logging detallado |
| Volúmenes | Solo static/media | Código completo montado |
| Hot reload | ❌ No | ✅ Sí (Django runserver) |

---

## Herramientas de Desarrollo

### Instaladas en el Contenedor

El archivo `backend/requirements-dev.txt` incluye:

#### **Linting y Formateo**
- **flake8** - Verificador de estilo PEP8
- **pycodestyle** - Verificador de estilo PEP8
- **autopep8** - Corrector automático de PEP8
- **black** - Formateador de código opinionado
- **isort** - Ordenador de imports

#### **Análisis Estático**
- **pylint** - Analizador de código estático
- **mccabe** - Complejidad ciclomática
- **radon** - Métricas de código

#### **Type Checking**
- **mypy** - Verificador de tipos estáticos
- **django-stubs** - Type stubs para Django
- **djangorestframework-stubs** - Type stubs para DRF

#### **Seguridad**
- **bandit** - Verificador de seguridad
- **safety** - Verificador de vulnerabilidades

#### **Testing**
- **pytest** - Framework de testing
- **pytest-django** - Plugin pytest para Django
- **pytest-cov** - Cobertura de tests
- **coverage** - Herramienta de cobertura
- **factory-boy** - Factories para testing

#### **Testing Automation**
- **tox** - Automatización de testing multi-entorno

#### **Utilidades**
- **django-extensions** - Extensiones útiles para Django
- **ipython** - Shell interactivo mejorado
- **ipdb** - Debugger interactivo
- **pre-commit** - Framework de pre-commit hooks

---

## Testing con Tox

Tox automatiza testing en múltiples entornos. Configurado en `backend/tox.ini`.

### Entornos Disponibles

```bash
# Entrar al contenedor backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Ver todos los entornos disponibles
tox -l
```

**Salida esperada:**
```
py311-django52
test
test-fast
lint
format
format-check
type-check
security
security-full
coverage
coverage-report
metrics
complexity
docs
clean
```

### Ejecutar Tests

**Tests completos con cobertura:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e py311-django52
```

**Tests rápidos (sin cobertura):**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e test-fast
```

**Solo tests unitarios:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e test -- -m unit
```

**Solo tests de integración:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e test -- -m integration
```

### Linting y Formateo

**Ejecutar linters (flake8 + pylint):**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e lint
```

**Verificar formato (sin modificar):**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e format-check
```

**Formatear código automáticamente:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e format
```

### Type Checking

**Verificar tipos con mypy:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e type-check
```

### Análisis de Seguridad

**Escaneo de seguridad básico:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e security
```

**Escaneo completo (genera reportes JSON):**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e security-full
```

### Cobertura de Código

**Generar reporte de cobertura:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e coverage
```

**Ver reporte en consola:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e coverage-report
```

**Reporte HTML** se genera en `backend/htmlcov/index.html`

### Métricas de Código

**Complejidad ciclomática y mantenibilidad:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e metrics
```

**Solo complejidad (con promedio):**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e complexity
```

### Limpieza

**Eliminar archivos generados:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox -e clean
```

### Ejecutar Todos los Entornos

**Ejecutar todos los chequeos:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox
```

⚠️ **Nota:** Esto puede tardar varios minutos.

---

## Acceso a PostgreSQL

### Desde tu Laptop (Host)

El puerto 5432 está expuesto en ambos entornos (producción y desarrollo).

**Credenciales por defecto:**
- **Host:** localhost
- **Puerto:** 5432
- **Database:** mac_attendance
- **Usuario:** mac_user
- **Password:** mac_password_2024_secure

#### **Con psql (línea de comandos)**

```bash
psql -h localhost -p 5432 -U mac_user -d mac_attendance
```

#### **Con pgAdmin**

1. Abrir pgAdmin
2. Crear nueva conexión:
   - Name: MAC Attendance
   - Host: localhost
   - Port: 5432
   - Database: mac_attendance
   - Username: mac_user
   - Password: mac_password_2024_secure

#### **Con DBeaver / DataGrip**

Similar a pgAdmin, usar las credenciales arriba.

### Desde el Contenedor Backend

```bash
# Entrar al contenedor backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Conectarse a PostgreSQL
psql -h db -U mac_user -d mac_attendance
```

### Comandos Útiles de PostgreSQL

**Listar tablas:**
```sql
\dt
```

**Describir tabla:**
```sql
\d authentication_student
```

**Ver tamaño de base de datos:**
```sql
SELECT pg_size_pretty(pg_database_size('mac_attendance'));
```

**Ver conexiones activas:**
```sql
SELECT * FROM pg_stat_activity;
```

**Contar registros:**
```sql
SELECT COUNT(*) FROM authentication_student;
SELECT COUNT(*) FROM events_event;
SELECT COUNT(*) FROM attendance_attendance;
```

---

## Comandos Útiles

### Gestión de Contenedores

**Ver logs en tiempo real:**
```bash
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f db
```

**Entrar al contenedor backend:**
```bash
docker-compose -f docker-compose.dev.yml exec backend bash
```

**Ejecutar comando Django:**
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py <comando>
```

**Crear superusuario:**
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

**Hacer migraciones:**
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py makemigrations
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
```

**Django shell:**
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell
```

**Django shell_plus (con django-extensions):**
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell_plus
```

### Backup y Restore

**Backup de base de datos:**
```bash
docker-compose -f docker-compose.dev.yml exec db pg_dump -U mac_user mac_attendance > backup_$(date +%Y%m%d).sql
```

**Restaurar backup:**
```bash
cat backup.sql | docker-compose -f docker-compose.dev.yml exec -T db psql -U mac_user mac_attendance
```

---

## Flujo de Trabajo

### 1. Desarrollo de Nueva Funcionalidad

```bash
# 1. Iniciar entorno de desarrollo
docker-compose -f docker-compose.dev.yml up -d

# 2. Crear rama de feature
git checkout -b feature/nueva-funcionalidad

# 3. Desarrollar (los cambios se reflejan automáticamente)
# Editar archivos en backend/ o frontend/

# 4. Ejecutar tests mientras desarrollas
docker-compose -f docker-compose.dev.yml exec backend tox -e test-fast

# 5. Verificar formato antes de commit
docker-compose -f docker-compose.dev.yml exec backend tox -e format-check

# 6. Formatear código si es necesario
docker-compose -f docker-compose.dev.yml exec backend tox -e format

# 7. Ejecutar linters
docker-compose -f docker-compose.dev.yml exec backend tox -e lint

# 8. Verificar tipos
docker-compose -f docker-compose.dev.yml exec backend tox -e type-check

# 9. Verificar seguridad
docker-compose -f docker-compose.dev.yml exec backend tox -e security

# 10. Ejecutar suite completa antes de commit
docker-compose -f docker-compose.dev.yml exec backend tox
```

### 2. Debugging

**Con ipdb:**

```python
# En tu código Python
import ipdb; ipdb.set_trace()
```

Luego:
```bash
docker-compose -f docker-compose.dev.yml up
# El contenedor se pausará en el breakpoint
```

**Ver logs detallados:**
```bash
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 3. Testing

```bash
# Tests rápidos durante desarrollo
docker-compose -f docker-compose.dev.yml exec backend pytest

# Con cobertura
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=.

# Solo una app
docker-compose -f docker-compose.dev.yml exec backend pytest authentication/

# Solo un archivo
docker-compose -f docker-compose.dev.yml exec backend pytest authentication/tests/test_models.py

# Solo una función de test
docker-compose -f docker-compose.dev.yml exec backend pytest authentication/tests/test_models.py::test_student_creation
```

### 4. Antes de Hacer Commit

**Checklist:**

- [ ] Tests pasan: `tox -e test`
- [ ] Código formateado: `tox -e format`
- [ ] Linters limpios: `tox -e lint`
- [ ] Type checking OK: `tox -e type-check`
- [ ] Sin vulnerabilidades: `tox -e security`
- [ ] Cobertura > 80%: `tox -e coverage`

**Ejecutar todo de una vez:**
```bash
docker-compose -f docker-compose.dev.yml exec backend tox
```

### 5. Pre-commit Hooks (Opcional)

Para automatizar chequeos antes de cada commit:

```bash
# Dentro del contenedor backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

---

## Solución de Problemas

### "Database does not exist"

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### "Port 5432 already in use"

Cambiar el puerto en `docker-compose.dev.yml`:
```yaml
ports:
  - "5433:5432"  # Usar puerto 5433 en host
```

### "Permission denied" en archivos

```bash
# Dentro del contenedor
chown -R $(whoami) /app
```

### Limpiar todo y empezar de nuevo

```bash
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a
docker volume prune
docker-compose -f docker-compose.dev.yml up --build
```

---

## Recursos Adicionales

- [Documentación de Django](https://docs.djangoproject.com/)
- [Documentación de Django REST Framework](https://www.django-rest-framework.org/)
- [Documentación de Tox](https://tox.wiki/)
- [Documentación de pytest](https://docs.pytest.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## Fecha de Creación

**Octubre 15, 2025**

---

**Nota:** Este documento describe el entorno de desarrollo completo con todas las herramientas de calidad de código, testing y análisis integradas.
