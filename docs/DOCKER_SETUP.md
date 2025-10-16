# Configuración Docker con Nginx

Esta configuración permite ejecutar la aplicación completa (Frontend React + Backend Django) usando Docker con Nginx como servidor web.

## Arquitectura

```
┌─────────────────────────────────────────┐
│           Nginx (Puerto 80)              │
│  - Sirve Frontend (React build)          │
│  - Proxy reverso para Backend Django     │
└─────────────────────────────────────────┘
           │                    │
           │                    │
           ▼                    ▼
    ┌──────────┐         ┌──────────┐
    │ Frontend │         │ Backend  │
    │  React   │         │  Django  │
    │  (Vite)  │         │ (Puerto  │
    └──────────┘         │  8000)   │
                         └──────────┘
                              │
                              ▼
                         ┌──────────┐
                         │PostgreSQL│
                         │   DB     │
                         └──────────┘
```

## Archivos Creados

- `Dockerfile.frontend` - Build del frontend React
- `Dockerfile.backend` - Configuración del backend Django
- `docker-compose.yml` - Orquestación de servicios
- `nginx/nginx.conf` - Configuración de Nginx
- `.dockerignore` - Archivos excluidos del build

## Requisitos Previos

- Docker Desktop instalado
- Docker Compose instalado

## Instrucciones de Uso

### 1. Configurar Variables de Entorno

Edita el archivo `docker-compose.yml` y ajusta las variables de entorno del servicio `backend`:

```yaml
environment:
  - SECRET_KEY=tu-secret-key-super-segura-cambiar-en-produccion
  - ALLOWED_HOSTS=localhost,127.0.0.1,nginx,tu-dominio.com
```

### 2. Construir y Levantar los Contenedores

```bash
# Construir las imágenes
docker-compose build

# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 3. Acceder a la Aplicación

- **Frontend**: http://localhost
- **API Backend**: http://localhost/api/
- **Admin Django**: http://localhost/admin/

### 4. Comandos Útiles

```bash
# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (¡cuidado, elimina la base de datos!)
docker-compose down -v

# Reconstruir un servicio específico
docker-compose build backend
docker-compose up -d backend

# Ver logs de un servicio específico
docker-compose logs -f nginx
docker-compose logs -f backend

# Ejecutar comandos en el backend
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py migrate

# Reiniciar un servicio
docker-compose restart backend
```

### 5. Gestión de la Base de Datos

```bash
# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser

# Backup de la base de datos (PostgreSQL)
docker-compose exec db pg_dump -U postgres mac_attendance > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres mac_attendance < backup.sql
```

## Configuración para Producción

### 1. Usar SQLite en lugar de PostgreSQL

Si prefieres usar SQLite (más simple pero menos escalable):

En `docker-compose.yml`:
- Comenta o elimina el servicio `db`
- Comenta la línea `DATABASE_URL` en el servicio `backend`
- Asegúrate de que Django esté configurado para usar SQLite en `settings.py`

### 2. Variables de Entorno Seguras

Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-secret-key-muy-segura-y-larga
DEBUG=False
ALLOWED_HOSTS=localhost,tu-dominio.com
DB_NAME=mac_attendance
DB_USER=postgres
DB_PASSWORD=password-super-seguro
DB_HOST=db
DB_PORT=5432
```

Modifica `docker-compose.yml` para usar el archivo `.env`:

```yaml
services:
  backend:
    env_file:
      - .env
```

### 3. HTTPS con Certificados SSL

Para habilitar HTTPS, necesitas:

1. Obtener certificados SSL (Let's Encrypt, Certbot, etc.)
2. Modificar `nginx/nginx.conf` para escuchar en el puerto 443
3. Agregar la configuración SSL

Ejemplo:

```nginx
server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # ... resto de la configuración
}

server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}
```

### 4. Optimizaciones de Producción

En `Dockerfile.backend`, ajusta workers de Gunicorn según tu servidor:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "mac_attendance.wsgi:application"]
```

Regla general: `workers = (2 x CPU cores) + 1`

## Troubleshooting

### El frontend no carga

```bash
# Verificar logs del nginx
docker-compose logs nginx

# Reconstruir el frontend
docker-compose build nginx --no-cache
docker-compose up -d nginx
```

### Error de conexión al backend

```bash
# Verificar que el backend esté corriendo
docker-compose ps

# Ver logs del backend
docker-compose logs backend

# Verificar conectividad
docker-compose exec nginx ping backend
```

### Problemas con migraciones

```bash
# Entrar al contenedor del backend
docker-compose exec backend sh

# Ejecutar migraciones manualmente
python manage.py migrate --run-syncdb
```

### Permisos en archivos media/static

```bash
# Dar permisos al directorio
docker-compose exec backend chmod -R 755 /app/media
docker-compose exec backend chmod -R 755 /app/staticfiles
```

## Monitoreo y Logs

```bash
# Ver uso de recursos
docker stats

# Ver todos los logs
docker-compose logs --tail=100

# Seguir logs en tiempo real
docker-compose logs -f --tail=100
```

## Limpieza

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes sin usar
docker image prune -a

# Limpiar volúmenes sin usar
docker volume prune

# Limpieza completa (¡cuidado!)
docker system prune -a --volumes
```

## Mejoras Futuras

- [ ] Configurar Redis para caché
- [ ] Agregar Celery para tareas asíncronas
- [ ] Implementar health checks más robustos
- [ ] Configurar logging centralizado
- [ ] Agregar monitoreo con Prometheus/Grafana
- [ ] Implementar CI/CD con GitHub Actions
