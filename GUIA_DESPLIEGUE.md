# Guía de Despliegue a Producción
## Sistema de Asistencia MAC - FES Acatlán

Esta guía describe los pasos necesarios para desplegar el Sistema de Asistencia MAC en un entorno de producción.

---

## 📋 Requisitos del Servidor

### Hardware Mínimo Recomendado
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disco:** 20 GB SSD
- **Red:** Conexión estable a internet

### Software Requerido
- **Sistema Operativo:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Docker:** Versión 20.10+
- **Docker Compose:** Versión 2.0+
- **Dominio:** (Opcional) Para acceso público con SSL

### Puertos Necesarios
- **80** (HTTP) - Nginx
- **443** (HTTPS) - Nginx con SSL (opcional pero recomendado)
- **5432** (PostgreSQL) - Solo si necesita acceso externo a la base de datos

---

## 🚀 Instalación Paso a Paso

### 1. Preparar el Servidor

#### Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade -y
```

#### Instalar Docker
```bash
# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Agregar repositorio oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verificar instalación
docker --version
```

#### Instalar Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker-compose --version
```

#### Agregar usuario al grupo Docker (opcional)
```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### 2. Clonar el Proyecto

```bash
# Crear directorio para el proyecto
sudo mkdir -p /opt/mac-attendance
cd /opt/mac-attendance

# Clonar el repositorio
git clone <URL-DEL-REPOSITORIO> .

# O si recibiste el proyecto comprimido
# Descomprimir el archivo en /opt/mac-attendance
```

---

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con nano o vim
nano .env
```

#### Configuración CRÍTICA de Seguridad

**⚠️ IMPORTANTE:** Cambie TODOS estos valores antes de desplegar:

```env
# ==============================================
# Django Settings
# ==============================================
DEBUG=False

# Generar SECRET_KEY único (ejecutar este comando en Python):
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=<GENERAR-CLAVE-ALEATORIA-AQUÍ>

# Dominio o IP del servidor (separados por coma)
ALLOWED_HOSTS=midominio.com,www.midominio.com,IP_DEL_SERVIDOR

# ==============================================
# Security Settings
# ==============================================
RATELIMIT_ENABLE=True
SECURE_SSL_REDIRECT=True  # Solo si tiene SSL configurado
SESSION_COOKIE_SECURE=True  # Solo si tiene SSL configurado
CSRF_COOKIE_SECURE=True  # Solo si tiene SSL configurado

# CORS y CSRF
CORS_ALLOWED_ORIGINS=https://midominio.com
CSRF_TRUSTED_ORIGINS=https://midominio.com

# ==============================================
# Database - PostgreSQL
# ==============================================
DB_NAME=mac_attendance
DB_USER=mac_user
DB_PASSWORD=<CONTRASEÑA-SEGURA-AQUÍ>  # Cambiar por contraseña fuerte
DB_HOST=db
DB_PORT=5432
```

#### Generar SECRET_KEY Seguro

```bash
# Ejecutar dentro del contenedor después de construirlo la primera vez
docker-compose run --rm backend python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copiar el resultado y pegarlo en SECRET_KEY del archivo .env
```

---

### 4. Configurar PostgreSQL

Edite las credenciales de PostgreSQL en `docker-compose.yml` para que coincidan con su `.env`:

```bash
nano docker-compose.yml
```

Busque la sección de `db` y actualice:
```yaml
environment:
  - POSTGRES_DB=mac_attendance
  - POSTGRES_USER=mac_user
  - POSTGRES_PASSWORD=<MISMA-CONTRASEÑA-DEL-ENV>  # Debe coincidir con DB_PASSWORD
```

---

### 5. Construir e Iniciar los Contenedores

```bash
# Construir las imágenes
docker-compose build

# Iniciar los servicios en segundo plano
docker-compose up -d

# Verificar que todos los contenedores están corriendo
docker-compose ps
```

**Salida esperada:**
```
NAME                      STATUS
pagina-mac-og-backend-1   Up
pagina-mac-og-db-1        Up (healthy)
pagina-mac-og-nginx-1     Up
```

---

### 6. Aplicar Migraciones de Base de Datos

```bash
# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Verificar que no hay errores
```

---

### 7. Crear Superusuario (Administrador)

```bash
# Crear superusuario para acceder al panel de administración
docker-compose exec backend python manage.py createsuperuser
```

Siga las instrucciones e ingrese:
- **Username:** admin (o el que prefiera)
- **Email:** admin@mac.unam.mx (o su email)
- **Password:** (contraseña segura)

---

### 8. Recolectar Archivos Estáticos

```bash
# Recolectar archivos estáticos de Django
docker-compose exec backend python manage.py collectstatic --noinput
```

---

### 9. Verificar el Despliegue

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Verificar logs del backend
docker-compose logs backend

# Verificar logs de nginx
docker-compose logs nginx

# Verificar logs de PostgreSQL
docker-compose logs db
```

#### Probar la Aplicación

1. Abrir navegador en: `http://IP_DEL_SERVIDOR` o `http://midominio.com`
2. Debería ver la página de login
3. Acceder al admin en: `http://IP_DEL_SERVIDOR/admin/`
4. Login con el superusuario creado

---

## 🔒 Configuración SSL (HTTPS) - Recomendado

### Opción 1: Con Let's Encrypt (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d midominio.com -d www.midominio.com

# El certificado se renovará automáticamente
```

### Opción 2: Con Certificado Propio

1. Copiar certificados SSL a `/opt/mac-attendance/ssl/`
2. Modificar `docker/nginx.conf` para incluir SSL
3. Reiniciar nginx: `docker-compose restart nginx`

---

## 🔧 Configuración de Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verificar reglas
sudo ufw status
```

---

## 📊 Backup y Recuperación

### Backup de Base de Datos

**Crear backup automático (recomendado):**

```bash
# Crear script de backup
sudo nano /opt/scripts/backup-mac-attendance.sh
```

Contenido del script:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/mac-attendance"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mac_attendance_$DATE.sql"

mkdir -p $BACKUP_DIR
docker-compose -f /opt/mac-attendance/docker-compose.yml exec -T db pg_dump -U mac_user mac_attendance > $BACKUP_FILE
gzip $BACKUP_FILE

# Mantener solo los últimos 30 días
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completado: $BACKUP_FILE.gz"
```

```bash
# Dar permisos de ejecución
sudo chmod +x /opt/scripts/backup-mac-attendance.sh

# Agregar a cron para ejecutar diariamente a las 2 AM
sudo crontab -e
```

Agregar línea:
```
0 2 * * * /opt/scripts/backup-mac-attendance.sh >> /var/log/mac-backup.log 2>&1
```

### Restaurar Backup

```bash
# Detener la aplicación
cd /opt/mac-attendance
docker-compose down

# Restaurar backup
gunzip backup_file.sql.gz
cat backup_file.sql | docker-compose exec -T db psql -U mac_user mac_attendance

# Reiniciar aplicación
docker-compose up -d
```

---

## 🔄 Actualización del Sistema

### Actualizar a Nueva Versión

```bash
cd /opt/mac-attendance

# Hacer backup antes de actualizar
docker-compose exec db pg_dump -U mac_user mac_attendance > backup_pre_update.sql

# Detener contenedores
docker-compose down

# Obtener nueva versión
git pull origin main
# O descomprimir nueva versión

# Reconstruir contenedores
docker-compose build

# Iniciar contenedores
docker-compose up -d

# Aplicar nuevas migraciones
docker-compose exec backend python manage.py migrate

# Recolectar archivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Verificar logs
docker-compose logs -f
```

---

## 📈 Monitoreo

### Ver Estado de Contenedores

```bash
docker-compose ps
```

### Ver Uso de Recursos

```bash
docker stats
```

### Ver Logs

```bash
# Todos los logs
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo backend
docker-compose restart backend

# Reiniciar solo nginx
docker-compose restart nginx
```

---

## ⚠️ Solución de Problemas

### Error: "502 Bad Gateway"

**Causa:** Backend no está respondiendo.

**Solución:**
```bash
# Verificar logs del backend
docker-compose logs backend

# Reiniciar backend
docker-compose restart backend

# Si persiste, reconstruir
docker-compose down
docker-compose up -d --build
```

### Error: "Connection refused" en PostgreSQL

**Causa:** Base de datos no está lista.

**Solución:**
```bash
# Verificar estado de PostgreSQL
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db

# Esperar a que esté "healthy"
docker-compose ps
```

### Error: "CSRF verification failed"

**Causa:** Configuración incorrecta de dominios en .env

**Solución:**
```bash
# Verificar que ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS incluyen su dominio
nano .env

# Reiniciar backend
docker-compose restart backend
```

---

## 📋 Checklist de Producción

Antes de poner en producción, verificar:

- [ ] **Seguridad:**
  - [ ] DEBUG=False en .env
  - [ ] SECRET_KEY único y aleatorio
  - [ ] DB_PASSWORD seguro y único
  - [ ] ALLOWED_HOSTS configurado correctamente
  - [ ] SSL/HTTPS habilitado (recomendado)
  - [ ] Firewall configurado

- [ ] **Base de Datos:**
  - [ ] PostgreSQL corriendo y saludable
  - [ ] Migraciones aplicadas
  - [ ] Backup automático configurado

- [ ] **Aplicación:**
  - [ ] Superusuario creado
  - [ ] Archivos estáticos recolectados
  - [ ] Aplicación accesible en navegador
  - [ ] Login funcionando correctamente

- [ ] **Monitoreo:**
  - [ ] Logs configurados
  - [ ] Alertas configuradas (opcional)
  - [ ] Backup verificado y probado

---

## 📞 Soporte Técnico

Para problemas durante el despliegue:
1. Revisar logs: `docker-compose logs -f`
2. Consultar documentación: `docs/`
3. Contactar a soporte técnico MAC

---

**Última actualización:** Octubre 2025
**Versión del documento:** 1.0
