# Migración a PostgreSQL

## Resumen

El Sistema de Asistencia MAC ha sido migrado de SQLite a PostgreSQL para mejorar el rendimiento, escalabilidad y prepararlo para producción.

## ¿Por qué PostgreSQL?

### Ventajas sobre SQLite

✅ **Escalabilidad**: Maneja millones de registros sin degradación de rendimiento
✅ **Concurrencia**: Múltiples usuarios simultáneos sin bloqueos
✅ **Rendimiento**: Mejor optimización de queries complejos
✅ **Integridad**: Constraints y validaciones más robustas
✅ **Backups**: Herramientas profesionales de respaldo (pg_dump, pg_basebackup)
✅ **Replicación**: Soporte nativo para alta disponibilidad
✅ **Producción**: Estándar en la industria para aplicaciones web

## Cambios Realizados

### 1. Backend - Requirements

**Archivo:** `backend/requirements.txt`

```python
# Database - PostgreSQL
psycopg2-binary==2.9.9
```

### 2. Backend - Settings

**Archivo:** `backend/mac_attendance/settings.py`

```python
# Database Configuration - PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='mac_attendance'),
        'USER': config('DB_USER', default='mac_user'),
        'PASSWORD': config('DB_PASSWORD', default='mac_password_2024_secure'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Conexiones persistentes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 3. Docker Compose

**Archivo:** `docker-compose.yml`

Se agregó el servicio de PostgreSQL:

```yaml
services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mac_attendance
      - POSTGRES_USER=mac_user
      - POSTGRES_PASSWORD=mac_password_2024_secure
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mac_user -d mac_attendance"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_ENGINE=postgresql
      - DB_NAME=mac_attendance
      - DB_USER=mac_user
      - DB_PASSWORD=mac_password_2024_secure
      - DB_HOST=db
      - DB_PORT=5432

volumes:
  postgres_data:
```

### 4. Variables de Entorno

**Archivo:** `.env.example`

```env
# Database - PostgreSQL (Producción)
DB_NAME=mac_attendance
DB_USER=mac_user
DB_PASSWORD=mac_password_2024_secure
DB_HOST=db
DB_PORT=5432
```

## Estado del Sistema

### Contenedores Activos

```bash
$ docker-compose ps
NAME                      STATUS
pagina-mac-og-backend-1   Up (running)
pagina-mac-og-db-1        Up (healthy)
pagina-mac-og-nginx-1     Up (running)
```

### Migraciones Aplicadas

✅ Todas las migraciones de Django aplicadas correctamente
✅ Base de datos creada: `mac_attendance`
✅ Usuario de base de datos: `mac_user`
✅ Tablas creadas: 16 tablas (auth, authentication, events, attendance, admin, sessions)

## Gestión de PostgreSQL

### Comandos Útiles

**Conectarse a PostgreSQL:**
```bash
docker-compose exec db psql -U mac_user -d mac_attendance
```

**Listar tablas:**
```sql
\dt
```

**Ver tamaño de base de datos:**
```sql
SELECT pg_size_pretty(pg_database_size('mac_attendance'));
```

**Backup de base de datos:**
```bash
docker-compose exec db pg_dump -U mac_user mac_attendance > backup.sql
```

**Restaurar backup:**
```bash
cat backup.sql | docker-compose exec -T db psql -U mac_user mac_attendance
```

**Ver conexiones activas:**
```sql
SELECT * FROM pg_stat_activity;
```

## Configuración de Producción

### 1. Cambiar Credenciales

**IMPORTANTE:** Antes de desplegar en producción, cambiar:

```env
DB_USER=tu_usuario_seguro
DB_PASSWORD=contraseña_muy_segura_y_compleja
SECRET_KEY=tu_secret_key_super_segura
```

### 2. Backups Automáticos

Configurar cron job para backups diarios:

```bash
#!/bin/bash
# /etc/cron.daily/postgres-backup

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mac_attendance_$DATE.sql"

mkdir -p $BACKUP_DIR
docker-compose exec -T db pg_dump -U mac_user mac_attendance > $BACKUP_FILE
gzip $BACKUP_FILE

# Mantener solo los últimos 30 días
find $BACKUP_DIR -type f -mtime +30 -delete
```

### 3. Optimización

**Configurar índices adicionales (si es necesario):**

```python
# En los modelos, agregar:
class Meta:
    indexes = [
        models.Index(fields=['account_number']),
        models.Index(fields=['event', 'student']),
    ]
```

### 4. Monitoring

**Ver queries lentas:**
```sql
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Capacidad y Límites

### Capacidad PostgreSQL

- **Tamaño máximo de base de datos**: Ilimitado
- **Tamaño máximo de tabla**: 32 TB
- **Filas por tabla**: Ilimitadas (prácticamente)
- **Usuarios concurrentes**: Miles

### Estimaciones para el Sistema MAC

**Escenario actual:**
- 1,000 estudiantes
- 100 eventos/año
- ~5,000 asistencias/año
- **Tamaño estimado**: < 100 MB/año

**Escenario a 10 años:**
- **Tamaño estimado**: < 1 GB
- **Performance**: Excelente

## Rollback (Volver a SQLite)

Si necesitas volver a SQLite por alguna razón:

### 1. Cambiar settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Comentar servicio db en docker-compose.yml

```yaml
# db:
#   image: postgres:15-alpine
#   ...
```

### 3. Reconstruir

```bash
docker-compose down -v
docker-compose up -d --build
```

## Verificación

### ✅ Checklist Post-Migración

- [✅] PostgreSQL corriendo y saludable
- [✅] Backend conectado a PostgreSQL
- [✅] Todas las migraciones aplicadas
- [✅] Aplicación accesible en http://localhost
- [✅] Variables de entorno configuradas
- [✅] Documentación actualizada

## Soporte

Para más información:
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Django con PostgreSQL](https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes)
- [psycopg2](https://www.psycopg.org/docs/)

## Fecha de Migración

**Octubre 14, 2025**

---

**Nota:** Este documento describe la migración a PostgreSQL para preparar el sistema para producción. Todas las funcionalidades permanecen idénticas, solo cambió el motor de base de datos.
