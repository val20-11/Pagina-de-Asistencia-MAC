# Guía para Poner en Producción

Esta guía te ayudará a desplegar el sistema en un servidor de producción cuando tengas acceso.

## 📋 Checklist Pre-Producción

Antes de desplegar en producción, asegúrate de tener:

- [ ] Acceso al servidor de producción (IP: 132.248.80.77 según configuración)
- [ ] Docker y Docker Compose instalados en el servidor
- [ ] Certificados SSL válidos (o configurar Let's Encrypt)
- [ ] Dominio configurado (opcional, puedes usar solo IP)
- [ ] Credenciales de producción seguras preparadas
- [ ] Backup de los datos actuales (si hay)

## 🚀 Pasos para Desplegar en Producción

### 1. Preparar el Servidor

```bash
# Conectarse al servidor (SSH)
ssh usuario@132.248.80.77

# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 2. Clonar el Repositorio

```bash
# Clonar en el servidor
cd /opt  # o el directorio que prefieras
sudo git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
cd Pagina-de-Asistencia-MAC
```

### 3. Configurar Variables de Entorno de Producción

```bash
# Copiar el template
cp .env.production.example .env.production

# Editar con tus credenciales SEGURAS
nano .env.production
```

**IMPORTANTE:** Configura estas variables en `.env.production`:

```env
# Django
DEBUG=False
SECRET_KEY=<GENERAR_CLAVE_NUEVA_SEGURA>
ALLOWED_HOSTS=132.248.80.77,tu-dominio.com

# Base de Datos
DB_NAME=mac_attendance
DB_USER=mac_user
DB_PASSWORD=<CONTRASEÑA_SEGURA_AQUÍ>
DB_HOST=db
DB_PORT=5432

# CORS (solo HTTPS en producción)
CORS_ALLOWED_ORIGINS=https://132.248.80.77,https://tu-dominio.com

# Security
CSRF_TRUSTED_ORIGINS=https://132.248.80.77,https://tu-dominio.com
SECURE_SSL_REDIRECT=True
```

**Generar SECRET_KEY segura:**
```bash
docker run --rm python:3.11-slim python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Generar contraseña segura de BD:**
```bash
openssl rand -base64 32
```

### 4. Configurar Certificados SSL

#### Opción A: Certificados Autofirmados (para pruebas)

Los certificados autofirmados ya están configurados en `docker/ssl/README.md`.

#### Opción B: Let's Encrypt (Recomendado para producción)

```bash
# Instalar certbot
sudo apt install certbot

# Generar certificados (necesitas un dominio)
sudo certbot certonly --standalone -d tu-dominio.com

# Los certificados estarán en:
# /etc/letsencrypt/live/tu-dominio.com/fullchain.pem
# /etc/letsencrypt/live/tu-dominio.com/privkey.pem

# Copiar a la ubicación de Docker
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem docker/ssl/server.crt
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem docker/ssl/server.key
sudo chmod 644 docker/ssl/server.crt
sudo chmod 600 docker/ssl/server.key
```

**Renovación automática:**
```bash
# Crear script de renovación
sudo crontab -e

# Agregar (renueva cada 2 meses, los certificados duran 3 meses):
0 0 1 */2 * certbot renew --quiet && cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem /opt/Pagina-de-Asistencia-MAC/docker/ssl/server.crt && cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem /opt/Pagina-de-Asistencia-MAC/docker/ssl/server.key && docker-compose -f /opt/Pagina-de-Asistencia-MAC/docker-compose.yml restart nginx
```

### 5. Construir e Iniciar Contenedores

```bash
# Construir imágenes
docker-compose build

# Iniciar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 6. Verificar que Todo Funciona

```bash
# Ver estado de contenedores
docker-compose ps

# Verificar logs del backend
docker-compose logs backend | tail -50

# Verificar que la base de datos esté saludable
docker-compose exec db pg_isready -U mac_user -d mac_attendance
```

### 7. Verificar Usuarios Creados

```bash
# Listar usuarios creados
docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import User; [print(f'{u.username} - Superuser: {u.is_superuser}') for u in User.objects.all()]"
```

Si los fixtures se cargaron correctamente, verás tu superusuario "Admin" y otros usuarios.

### 8. Acceder al Sistema

Abre tu navegador y ve a:
- **Aplicación:** https://132.248.80.77 (o https://tu-dominio.com)
- **Admin:** https://132.248.80.77/admin

## 🔒 Seguridad Post-Despliegue

### Cambiar Contraseñas

**IMPORTANTE:** Si estás usando los fixtures con contraseñas de desarrollo, cámbialas:

```bash
# Cambiar contraseña del superusuario
docker-compose exec backend python manage.py changepassword Admin

# O crear un nuevo superusuario
docker-compose exec backend python manage.py createsuperuser
```

### Configurar Firewall

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Verificar
sudo ufw status
```

### Configurar Fail2Ban (Protección contra fuerza bruta)

```bash
# Instalar fail2ban
sudo apt install fail2ban

# Configurar (opcional, para proteger SSH y Django)
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📊 Backups en Producción

### Backup Manual

```bash
# Crear backup de la base de datos
docker-compose exec db pg_dump -U mac_user mac_attendance > backup_$(date +%Y%m%d_%H%M%S).sql

# Guardar en un lugar seguro (S3, Google Drive, etc.)
```

### Backup Automático Diario

```bash
# Crear script de backup
sudo nano /opt/backup_mac.sh
```

Contenido del script:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose -f /opt/Pagina-de-Asistencia-MAC/docker-compose.yml exec -T db pg_dump -U mac_user mac_attendance > $BACKUP_DIR/backup_$DATE.sql

# Mantener solo los últimos 30 días
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete

echo "Backup completado: backup_$DATE.sql"
```

```bash
# Hacer ejecutable
sudo chmod +x /opt/backup_mac.sh

# Agregar a crontab (diario a las 2 AM)
sudo crontab -e
# Agregar:
0 2 * * * /opt/backup_mac.sh
```

## 🔄 Actualizar el Sistema en Producción

Cuando hay cambios en el código:

```bash
# 1. Hacer backup
docker-compose exec db pg_dump -U mac_user mac_attendance > backup_pre_update.sql

# 2. Detener servicios
docker-compose down

# 3. Actualizar código
git pull origin main

# 4. Reconstruir imágenes
docker-compose build

# 5. Iniciar servicios
docker-compose up -d

# 6. Verificar logs
docker-compose logs -f
```

## 📈 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo nginx
docker-compose logs -f nginx

# Solo BD
docker-compose logs -f db
```

### Estadísticas de Uso

```bash
# Uso de recursos
docker stats

# Espacio en disco
df -h
docker system df
```

## 🚨 Problemas Comunes

### "502 Bad Gateway"
```bash
# Verificar que el backend esté corriendo
docker-compose ps backend

# Ver logs del backend
docker-compose logs backend

# Reiniciar backend
docker-compose restart backend
```

### "Base de datos no conecta"
```bash
# Verificar salud de la BD
docker-compose exec db pg_isready

# Ver logs
docker-compose logs db

# Verificar credenciales en .env.production
```

### "Certificado SSL inválido"
```bash
# Verificar que los archivos existen
ls -la docker/ssl/

# Verificar permisos
chmod 644 docker/ssl/server.crt
chmod 600 docker/ssl/server.key

# Reiniciar nginx
docker-compose restart nginx
```

## 📞 Mantenimiento

### Limpieza Regular

```bash
# Limpiar imágenes no usadas (mensual)
docker system prune -a

# Limpiar volúmenes huérfanos
docker volume prune
```

### Actualizar Dependencias

```bash
# Actualizar imágenes base
docker-compose pull
docker-compose build --no-cache
docker-compose up -d
```

## 📝 Checklist Post-Despliegue

- [ ] Sistema accesible via HTTPS
- [ ] Certificados SSL válidos
- [ ] Usuarios pueden iniciar sesión
- [ ] Contraseñas de desarrollo cambiadas
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] Monitoreo funcionando
- [ ] Logs revisados (sin errores críticos)
- [ ] Documentación actualizada
- [ ] Equipo notificado de la URL de producción

---

## 🎯 Resumen: Comandos Rápidos para Producción

```bash
# Iniciar
docker-compose up -d

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f

# Backup
docker-compose exec db pg_dump -U mac_user mac_attendance > backup.sql

# Actualizar
git pull && docker-compose build && docker-compose up -d

# Estado del sistema
docker-compose ps
docker stats
```

---

**¡El sistema está listo para producción cuando tengas acceso al servidor! 🚀**
