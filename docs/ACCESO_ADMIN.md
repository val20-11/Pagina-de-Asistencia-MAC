# Acceso al Panel de Administración de Django

## Estado Actual

Los contenedores Docker están corriendo correctamente:
- ✅ **Frontend (Nginx)**: http://localhost
- ✅ **Backend (Django)**: Disponible en http://localhost/api/
- ✅ **Panel Admin**: http://localhost/admin/

## Problema Resuelto

Se han corregido los siguientes problemas:

1. **STATIC_ROOT no configurado**: Se agregó `STATIC_ROOT = BASE_DIR / 'staticfiles'` en `settings.py`
2. **MEDIA_ROOT no configurado**: Se agregó `MEDIA_ROOT = BASE_DIR / 'media'` en `settings.py`
3. **Variables de entorno faltantes**: Se agregaron todas las variables necesarias en `docker-compose.yml`
4. **PostgreSQL removido**: Se simplificó usando SQLite para facilitar el desarrollo

## Crear Superusuario

Para acceder al panel de administración, primero necesitas crear un superusuario.

### En Windows (PowerShell):

```powershell
docker-compose exec backend python manage.py createsuperuser
```

### En Linux/Mac:

```bash
bash create_superuser.sh
```

O manualmente:

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Proceso Interactivo:

El comando te pedirá:
1. **Username**: Ingresa un nombre de usuario (ejemplo: admin)
2. **Email**: Ingresa un email (ejemplo: admin@example.com)
3. **Password**: Ingresa una contraseña segura
4. **Password (again)**: Confirma la contraseña

Ejemplo:
```
Username: admin
Email address: admin@example.com
Password: **********
Password (again): **********
Superuser created successfully.
```

## Acceder al Panel de Administración

1. Abre tu navegador web
2. Ve a: **http://localhost/admin/**
3. Ingresa tus credenciales (username y password que creaste)
4. ¡Listo! Ya puedes administrar tu aplicación

## URLs Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost | Aplicación React |
| API Backend | http://localhost/api/ | API REST de Django |
| Admin Django | http://localhost/admin/ | Panel de administración |
| Archivos Estáticos | http://localhost/static/ | CSS, JS, imágenes de Django |
| Archivos Media | http://localhost/media/ | Archivos subidos por usuarios |

## Verificar Estado de los Contenedores

```bash
# Ver estado de los contenedores
docker-compose ps

# Ver logs del backend
docker-compose logs backend

# Ver logs del nginx
docker-compose logs nginx

# Seguir logs en tiempo real
docker-compose logs -f
```

## Comandos Útiles de Django

```bash
# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario adicional
docker-compose exec backend python manage.py createsuperuser

# Acceder al shell de Django
docker-compose exec backend python manage.py shell

# Colectar archivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Ver rutas disponibles
docker-compose exec backend python manage.py show_urls
```

## Solución de Problemas

### Error 502 Bad Gateway

Si ves este error, verifica que el backend esté corriendo:

```bash
docker-compose logs backend
docker-compose restart backend
```

### No puedo acceder a /admin/

1. Verifica que el backend esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Verifica los logs de nginx:
   ```bash
   docker-compose logs nginx
   ```

3. Verifica que hayas creado un superusuario

### Error de permisos

Si hay errores de permisos en archivos:

```bash
# En el backend
docker-compose exec backend chmod -R 755 /app/staticfiles
docker-compose exec backend chmod -R 755 /app/media
```

### Reiniciar todo desde cero

Si algo sale mal, puedes reiniciar todo:

```bash
# Detener y eliminar todo (¡cuidado! elimina la base de datos)
docker-compose down -v

# Reconstruir
docker-compose build --no-cache

# Levantar
docker-compose up -d

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```

## Configuración de Producción

Para producción, debes cambiar estas variables en `docker-compose.yml`:

```yaml
environment:
  - DEBUG=False  # ⚠️ IMPORTANTE: Cambiar a False en producción
  - SECRET_KEY=cambiar-por-una-clave-super-segura-y-aleatoria
  - ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
  - SECURE_SSL_REDIRECT=True
  - SESSION_COOKIE_SECURE=True
  - CSRF_COOKIE_SECURE=True
```

También deberías considerar usar PostgreSQL en lugar de SQLite para producción.

## Arquitectura

```
┌─────────────────────────────────────────┐
│         Cliente (Navegador)              │
└────────────────┬────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────┐
│     Nginx (Puerto 80)                    │
│  ├─ / → Frontend React (build estático)  │
│  ├─ /api/* → Backend Django (proxy)      │
│  ├─ /admin/* → Django Admin (proxy)      │
│  ├─ /static/* → Archivos estáticos       │
│  └─ /media/* → Archivos media            │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
┌─────────────┐    ┌─────────────┐
│  Frontend   │    │   Backend   │
│  (React)    │    │  (Django)   │
│  /usr/share/│    │  Puerto:    │
│  nginx/html │    │  8000       │
└─────────────┘    └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   SQLite    │
                   │  (db.sqlite3)│
                   └─────────────┘
```

## Seguridad

- ✅ CORS configurado correctamente
- ✅ CSRF protection habilitado
- ✅ JWT Authentication para API
- ✅ Rate limiting disponible (deshabilitado en desarrollo)
- ⚠️ DEBUG=True (solo para desarrollo)
- ⚠️ Cambiar SECRET_KEY en producción
- ⚠️ Habilitar HTTPS en producción

## Próximos Pasos

1. ✅ Contenedores corriendo
2. ⚠️ Crear superusuario (pendiente - ejecuta el comando arriba)
3. ⚠️ Acceder a http://localhost/admin/
4. ⚠️ Configurar usuarios y permisos
5. ⚠️ Probar las funcionalidades de la aplicación
