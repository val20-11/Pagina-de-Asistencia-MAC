# Sistema de Asistencia MAC - FES Acatlán

Sistema de gestión de asistencia para ponencias y eventos académicos de Matemáticas Aplicadas y Computación (MAC).

## 🚀 Características

- **Gestión de Eventos**: Crear y administrar ponencias, talleres, seminarios
- **Registro de Asistencia**: Manual, por código de barras o usuarios externos
- **Panel de Estudiantes**: Consulta de estadísticas y eventos disponibles
- **Panel de Asistentes**: Administración completa y registro de asistencias
- **Usuarios Externos**: Sistema de aprobación para asistentes externos
- **Estadísticas**: Seguimiento de porcentaje de asistencia por estudiante
- **Seguridad Avanzada**: JWT, rate limiting, auditoría completa
- **Sistema de Auditoría**: Registro automático de eventos de seguridad

## 📋 Requisitos Previos

### Opción 1: Con Docker (Recomendado)
- Docker y Docker Compose instalados
- Puertos 80 y 5432 disponibles

### Opción 2: Instalación Manual
- Python 3.11+
- Node.js 18+
- npm o yarn
- PostgreSQL 15+

## 🛠️ Instalación

### Opción 1: Con Docker (Recomendado)

#### Producción

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd pagina-mac-og

# Copiar variables de entorno
cp .env.example .env

# IMPORTANTE: Editar .env y cambiar las credenciales para producción
# Cambiar: SECRET_KEY, DB_PASSWORD, etc.

# Construir e iniciar contenedores
docker-compose up --build -d

# Ver logs
docker-compose logs -f

# Acceder a la aplicación
# http://localhost
```

El sistema estará disponible en `http://localhost` con:
- **Frontend**: Servido por Nginx en puerto 80
- **Backend**: API REST en `/api/`
- **PostgreSQL**: Base de datos (puerto 5432 expuesto)

#### Desarrollo

```bash
# Usar configuración de desarrollo
docker-compose -f docker-compose.dev.yml up --build -d

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Acceder al contenedor backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Ejecutar tests
docker-compose -f docker-compose.dev.yml exec backend tox -e test

# Ver documentación completa de desarrollo
# docs/DESARROLLO.md
```

**Características del entorno de desarrollo:**
- ✅ Hot reload automático (Django runserver)
- ✅ Todas las herramientas de testing y calidad de código
- ✅ PostgreSQL con puerto expuesto para acceso desde host
- ✅ Debugging con ipdb
- ✅ Ver `docs/DESARROLLO.md` para más detalles

### Opción 2: Instalación Manual

### Backend (Django)

1. Crear entorno virtual:
```bash
cd backend
python -m venv venv
```

2. Activar entorno virtual:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

**⚠️ IMPORTANTE**: Si acabas de clonar el repositorio o actualizaste con nuevas funcionalidades de importación/exportación, ejecuta:
```bash
pip install django-import-export openpyxl tablib
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Ejecutar migraciones:
```bash
python manage.py migrate
```

6. Crear superusuario (opcional):
```bash
python manage.py createsuperuser
```

7. Ejecutar servidor:
```bash
python manage.py runserver
```

El backend estará disponible en `http://127.0.0.1:8000`

### Frontend (React + Vite)

1. Instalar dependencias:
```bash
cd frontend
npm install
```

2. Ejecutar servidor de desarrollo:
```bash
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📥 Importación y Exportación de Datos

El sistema incluye funcionalidades de importación/exportación de estudiantes y asistentes mediante archivos Excel (.xlsx) o CSV.

### Formato de Archivos para Importación

Los archivos deben tener **exactamente 2 columnas**:

| account_number | full_name |
|----------------|-----------|
| 1234567 | Juan Pérez García |
| 7654321 | María López Sánchez |

### Desde el Panel de Admin de Django

1. Ve a `http://127.0.0.1:8000/admin/`
2. Selecciona **Estudiantes** o **Asistentes (Perfiles)**
3. Haz clic en **"Importar"** en la esquina superior derecha
4. Selecciona tu archivo Excel (.xlsx) o CSV
5. Revisa los cambios propuestos
6. Confirma la importación

### Exportación

1. Selecciona los registros que deseas exportar
2. En el menú de acciones, selecciona **"📊 Exportar estudiantes/asistentes seleccionados"**
3. Haz clic en **"Ir"**
4. Se descargará un archivo Excel con los datos

### Creación Manual

También puedes crear estudiantes y asistentes manualmente:
1. Ve al panel de admin de Django
2. Selecciona **Estudiantes** o **Asistentes (Perfiles)**
3. Haz clic en **"Agregar estudiante"** o **"Agregar asistente"**
4. Completa los campos:
   - Número de cuenta (7 dígitos)
   - Nombre completo
5. Guarda - el sistema creará automáticamente el usuario de Django asociado

## 📁 Estructura del Proyecto

```
mac_attendance/
├── backend/
│   ├── attendance/          # App de registro de asistencias
│   ├── authentication/      # App de autenticación y auditoría
│   ├── events/             # App de eventos y usuarios externos
│   ├── mac_attendance/     # Configuración principal y middleware
│   ├── scripts/            # Scripts de utilidad
│   │   ├── check_production.py   # Verificar config de producción
│   │   └── test_ratelimit.py     # Probar rate limiting
│   ├── static/             # Archivos estáticos
│   ├── media/              # Archivos subidos
│   ├── logs/               # Archivos de log (no trackeados)
│   ├── requirements.txt    # Dependencias Python
│   └── .env.example       # Ejemplo de variables de entorno
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── contexts/      # Contextos (AuthContext)
│   │   └── services/      # Servicios API
│   └── package.json       # Dependencias Node
├── docker/                 # Archivos Docker
│   ├── Dockerfile.backend        # Dockerfile producción
│   ├── Dockerfile.backend.dev    # Dockerfile desarrollo
│   ├── Dockerfile.frontend       # Dockerfile frontend
│   └── nginx.conf                # Configuración Nginx
├── docs/                   # Documentación del proyecto
│   ├── SECURITY.md               # Guía de seguridad completa
│   ├── RATE_LIMITING.md          # Documentación rate limiting
│   ├── AUDIT.md                  # Sistema de auditoría
│   ├── POSTGRESQL_MIGRATION.md   # Migración a PostgreSQL
│   ├── DESARROLLO.md             # Guía de desarrollo completa
│   └── ESTRUCTURA_PROYECTO.md    # Estructura del proyecto
├── docker-compose.yml      # Docker Compose producción
├── docker-compose.dev.yml  # Docker Compose desarrollo
├── .env.example           # Ejemplo de variables de entorno
└── README.md
```

## 🔐 Configuración Inicial

### Crear Superusuario (Administrador)

Después de iniciar los contenedores, crea un superusuario para acceder al panel de administración:

```bash
# Con Docker
docker-compose exec backend python manage.py createsuperuser

# O en desarrollo
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

Sigue las instrucciones para crear:
- Username
- Email
- Password

### Acceso al Sistema

**Panel de Administración Django:**
- URL: `http://localhost/admin/`
- Usuario: El superusuario que acabas de crear

**Aplicación Web:**
- URL: `http://localhost/`
- Los usuarios (asistentes y estudiantes) deben ser creados desde el panel de administración
- Usuarios externos pueden registrarse desde el formulario público

## 📊 Modelos Principales

### UserProfile
- Tipo de usuario (estudiante/asistente)
- Número de cuenta (7 dígitos)
- Información personal

### Event
- Título, descripción, ponente
- Fecha, hora de inicio/fin
- Modalidad (presencial/online/híbrido)
- Capacidad máxima

### Attendance
- Estudiante o usuario externo
- Evento asociado
- Método de registro (manual/barcode/external)
- Registrado por (asistente)

### ExternalUser
- Usuarios externos pendientes de aprobación
- Información de institución y motivo
- ID temporal único

## 🔧 Configuración Adicional

### Variables de Entorno (.env)
```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### CORS
El backend está configurado para aceptar peticiones desde:
- `http://localhost:5173` (desarrollo)
- `http://127.0.0.1:5173` (desarrollo)

## 🔒 Seguridad

Este proyecto implementa múltiples capas de seguridad:

### Autenticación y Autorización
- ✅ **JWT (JSON Web Tokens)** para autenticación stateless
- ✅ **Control de acceso basado en roles** (estudiante/asistente)
- ✅ **Tokens de corta duración** (1 hora) con refresh tokens (7 días)

### Protección contra Ataques
- ✅ **Rate Limiting**: Límites en todos los endpoints críticos
  - Login: 5 intentos/minuto por IP
  - Registro externo: 3/hora por IP
  - Ver `docs/RATE_LIMITING.md` para detalles
- ✅ **Headers de seguridad** HTTP (HSTS, X-Frame-Options, etc.)
- ✅ **Sanitización automática** de datos sensibles en logs

### Sistema de Auditoría
- ✅ **Registro automático** de eventos de seguridad
- ✅ **Trazabilidad completa**: IP, user agent, timestamp
- ✅ **Logs inmutables** consultables desde Django Admin
- ✅ Ver `docs/AUDIT.md` para documentación completa

### Documentación de Seguridad
- 📄 `docs/SECURITY.md` - Guía de seguridad y checklist de producción
- 📄 `docs/RATE_LIMITING.md` - Configuración de rate limiting
- 📄 `docs/AUDIT.md` - Sistema de auditoría

## 🧪 Testing y Calidad de Código

El proyecto incluye un entorno completo de testing y calidad de código usando **Tox**.

### Ejecutar Tests

```bash
# Con Docker (desarrollo)
docker-compose -f docker-compose.dev.yml exec backend tox -e test

# Tests rápidos
docker-compose -f docker-compose.dev.yml exec backend tox -e test-fast

# Con cobertura
docker-compose -f docker-compose.dev.yml exec backend tox -e coverage
```

### Herramientas Disponibles

- **Testing**: pytest, pytest-django, pytest-cov, factory-boy
- **Linting**: flake8, pylint, black, isort
- **Type Checking**: mypy con stubs para Django/DRF
- **Seguridad**: bandit, safety
- **Métricas**: radon (complejidad ciclomática)

Ver `docs/DESARROLLO.md` para documentación completa.

## 🐘 PostgreSQL

El sistema usa PostgreSQL como base de datos para producción.

### Acceso desde Host

⚠️ **Configurar credenciales en archivo .env antes de usar:**

```bash
Host: localhost
Port: 5432
Database: [DB_NAME del .env]
User: [DB_USER del .env]
Password: [DB_PASSWORD del .env]
```

### Comandos Útiles

```bash
# Conectarse con psql
psql -h localhost -p 5432 -U mac_user -d mac_attendance

# Backup
docker-compose exec db pg_dump -U mac_user mac_attendance > backup.sql

# Restore
cat backup.sql | docker-compose exec -T db psql -U mac_user mac_attendance
```

Ver `docs/POSTGRESQL_MIGRATION.md` para más detalles.

## 📚 Documentación

- `docs/DESARROLLO.md` - Guía completa de desarrollo
- `docs/SECURITY.md` - Guía de seguridad y checklist de producción
- `docs/RATE_LIMITING.md` - Configuración de rate limiting
- `docs/AUDIT.md` - Sistema de auditoría
- `docs/POSTGRESQL_MIGRATION.md` - Migración a PostgreSQL
- `docs/ESTRUCTURA_PROYECTO.md` - Estructura del proyecto

## 🚧 Mejoras Futuras

- [x] Implementar JWT para autenticación
- [x] Sistema de auditoría y logging
- [x] Rate limiting en endpoints
- [x] Dockerización del proyecto
- [x] Migración a PostgreSQL
- [x] Entorno de desarrollo con Tox
- [ ] Agregar exportación de reportes (CSV/PDF)
- [ ] Implementar lector de códigos de barras
- [ ] Notificaciones por email
- [ ] Panel de estadísticas avanzadas
- [ ] Cobertura de tests > 80%

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 👥 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📧 Soporte

Para preguntas o soporte técnico sobre el sistema, contactar a:
- Matemáticas Aplicadas y Computación (MAC)
- FES Acatlán - UNAM

---

**Desarrollado para:** Matemáticas Aplicadas y Computación (MAC)
**Institución:** FES Acatlán - UNAM
**Año:** 2025