# Estructura del Proyecto

Este documento describe la organización de carpetas y archivos del Sistema de Asistencia MAC.

## Estructura de Directorios

```
pagina-mac-og/
├── backend/                    # Aplicación Django (Backend)
│   ├── attendance/            # App de gestión de asistencias
│   ├── authentication/        # App de autenticación y usuarios
│   ├── events/               # App de gestión de eventos
│   ├── mac_attendance/       # Configuración principal de Django
│   ├── scripts/              # Scripts de utilidad y pruebas
│   ├── static/               # Archivos estáticos (CSS, JS)
│   ├── templates/            # Plantillas HTML
│   ├── db/                   # Base de datos SQLite
│   ├── logs/                 # Logs de la aplicación
│   ├── media/                # Archivos multimedia subidos
│   └── manage.py             # CLI de Django
│
├── frontend/                  # Aplicación React (Frontend)
│   ├── src/                  # Código fuente
│   │   ├── components/       # Componentes React
│   │   ├── contexts/         # Contextos (Auth, etc.)
│   │   ├── services/         # Servicios (API calls)
│   │   └── styles/           # Estilos CSS
│   ├── public/               # Archivos públicos
│   └── package.json          # Dependencias de Node.js
│
├── docker/                    # Configuración Docker
│   ├── Dockerfile.backend    # Dockerfile para Django
│   ├── Dockerfile.frontend   # Dockerfile para React + Nginx
│   └── nginx.conf            # Configuración de Nginx
│
├── docs/                      # Documentación
│   ├── ACCESO_ADMIN.md       # Guía de acceso al admin
│   ├── API_DOCUMENTATION.md  # Documentación de API
│   ├── DOCKER_SETUP.md       # Configuración de Docker
│   ├── GUIA_COMPARTIR_DOCKER.md  # Guía para compartir
│   ├── INSTRUCCIONES_GITHUB.md   # Instrucciones de Git
│   ├── ESTRUCTURA_PROYECTO.md    # Este archivo
│   └── postman_collection.json   # Colección de Postman
│
├── docker-compose.yml         # Orquestación de contenedores
├── .dockerignore             # Archivos ignorados por Docker
├── .env.example              # Ejemplo de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── install.sh                # Script de instalación (Linux/Mac)
├── install.bat               # Script de instalación (Windows)
├── create_superuser.sh       # Script para crear superusuario
├── README.md                 # Documentación principal
└── LICENSE                   # Licencia del proyecto
```

## Descripción de Componentes

### Backend (Django)

**Aplicaciones Django:**
- **attendance**: Gestión de asistencias y estadísticas
- **authentication**: Sistema de autenticación, usuarios, perfiles
- **events**: Gestión de eventos del MAC
- **mac_attendance**: Configuración principal del proyecto Django

**Archivos importantes:**
- `manage.py`: CLI de Django para ejecutar comandos
- `requirements.txt`: Dependencias de Python
- `db.sqlite3`: Base de datos SQLite (desarrollo)

### Frontend (React)

**Estructura:**
- `src/components/`: Componentes React organizados por rol (admin, student, attendance)
- `src/contexts/`: Contextos de React (AuthContext para autenticación)
- `src/services/`: Servicios para llamadas a la API
- `src/styles/`: Archivos CSS

### Docker

**Archivos:**
- `Dockerfile.backend`: Imagen de Docker para el backend Django
- `Dockerfile.frontend`: Imagen de Docker para el frontend React + Nginx
- `nginx.conf`: Configuración del servidor Nginx como proxy reverso

### Documentación

Toda la documentación técnica, guías de uso y configuración se encuentra en la carpeta `docs/`.

## Flujo de Trabajo

### Desarrollo

1. **Backend**: Modificar código en `backend/`
2. **Frontend**: Modificar código en `frontend/src/`
3. **Docker**: Los cambios se reflejan automáticamente con volúmenes

### Despliegue

1. Construir imágenes: `docker-compose build`
2. Iniciar servicios: `docker-compose up -d`
3. Verificar logs: `docker-compose logs -f`

## Scripts Útiles

### Backend (desde `backend/`)
```bash
python manage.py migrate          # Aplicar migraciones
python manage.py createsuperuser  # Crear superusuario
python manage.py collectstatic    # Recopilar archivos estáticos
python scripts/create_test_data.py # Crear datos de prueba
```

### Docker
```bash
docker-compose up -d              # Iniciar servicios
docker-compose down               # Detener servicios
docker-compose logs backend       # Ver logs del backend
docker-compose restart backend    # Reiniciar backend
```

## Variables de Entorno

Copia `.env.example` a `.env` y configura las variables según tu entorno:

```bash
cp .env.example .env
# Editar .env con tus valores
```

## Puertos

- **Frontend (Nginx)**: http://localhost (puerto 80)
- **Backend (Django)**: http://localhost:8000 (interno, proxy via Nginx)
- **Admin Django**: http://localhost/admin

## Notas Importantes

1. **Base de datos**: SQLite por defecto en desarrollo. Para producción, usar PostgreSQL.
2. **Archivos estáticos**: Servidos por Nginx en producción
3. **CORS**: Configurado para permitir localhost en desarrollo
4. **Logs**: Disponibles en `backend/logs/` y via `docker-compose logs`

## Convenciones

- **Backend**: Seguir guía de estilo PEP 8 para Python
- **Frontend**: Seguir guía de estilo de Airbnb para JavaScript/React
- **Commits**: Mensajes descriptivos en español
- **Branches**: `main` para producción, crear feature branches para desarrollo

## Soporte

Para más información, consulta:
- [README.md](../README.md) - Guía general del proyecto
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentación de la API
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Configuración detallada de Docker
