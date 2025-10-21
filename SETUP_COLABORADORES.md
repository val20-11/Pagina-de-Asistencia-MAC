# Guía de Configuración para Colaboradores

Esta guía te ayudará a configurar el proyecto en tu máquina local con todos los datos necesarios ya precargados.

## 🚀 Inicio Rápido (5 minutos)

### Prerrequisitos
- Docker y Docker Compose instalados
- Git instalado

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
cd Pagina-de-Asistencia-MAC
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.development.example .env.development

# (Opcional) Puedes editar .env.development si necesitas cambiar algo
# Por defecto viene configurado y listo para usar
```

### Paso 3: Iniciar el Proyecto

```bash
# Iniciar todos los contenedores
docker-compose -f docker-compose.dev.yml up --build -d

# Ver los logs (CTRL+C para salir)
docker-compose -f docker-compose.dev.yml logs -f
```

### Paso 4: Acceder al Sistema

**¡Listo!** El sistema estará disponible en:

- **Aplicación:** http://localhost
- **Panel Admin:** http://localhost/admin

## 👤 Usuarios Precargados

El sistema viene con usuarios ya creados que puedes usar inmediatamente:

### Superusuario (Admin)
- **Usuario:** `Admin`
- **Contraseña:** (la contraseña del usuario Admin original)
- **Acceso:** Panel de administración completo

### Asistentes
- **Usuario:** `asst_11111111`
- **Contraseña:** `11111111` (mismo que el número de cuenta)
- **Acceso:** Panel de asistentes

*Nota: Todos los usuarios y datos están en `backend/fixtures/initial_data.json`*

## 🔄 Cómo Funciona la Inicialización Automática

Cuando inicias el proyecto por primera vez:

1. **Docker Compose** ejecuta las migraciones de Django
2. **Script `init_db.py`** detecta si la base de datos está vacía
3. Si está vacía, carga automáticamente los **fixtures** desde `backend/fixtures/`
4. Los fixtures incluyen:
   - Usuarios (superusuarios y asistentes)
   - Perfiles de usuario
   - Eventos (si existen)
   - Asistencias (si existen)

**No necesitas hacer nada manualmente** - todo se configura automáticamente.

## 🔧 Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose -f docker-compose.dev.yml logs -f
```

### Reiniciar contenedores
```bash
docker-compose -f docker-compose.dev.yml restart
```

### Detener el proyecto
```bash
docker-compose -f docker-compose.dev.yml down
```

### Resetear la base de datos completamente
```bash
# Esto elimina todos los datos y volúmenes
docker-compose -f docker-compose.dev.yml down -v

# Luego volver a iniciar (se recargarán los fixtures automáticamente)
docker-compose -f docker-compose.dev.yml up -d
```

### Crear un nuevo superusuario (opcional)
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

### Acceder a la consola de Django
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py shell
```

### Ejecutar tests
```bash
docker-compose -f docker-compose.dev.yml exec backend pytest
```

## 📊 Actualizar con Nuevos Datos

Si el equipo comparte nuevos datos:

### Opción 1: Actualizar desde Git (Recomendado)

```bash
# Obtener los últimos cambios
git pull origin main

# Reiniciar los contenedores para cargar los nuevos fixtures
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Opción 2: Cargar fixtures manualmente

```bash
# Si solo quieres cargar fixtures específicos sin borrar todo
docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata backend/fixtures/initial_data.json
```

## 🎯 Compartir tus Cambios

Si quieres que otros colaboradores tengan tus datos:

### 1. Exportar los datos actuales

Usa el script de exportación:

```bash
# En Windows PowerShell
python export_fixtures.py

# En Linux/Mac
python3 export_fixtures.py
```

Esto creará/actualizará archivos en `backend/fixtures/`:
- `initial_users.json` - Usuarios y perfiles
- `initial_events.json` - Eventos y asistencias (si existen)

### 2. Subir a GitHub

```bash
git add backend/fixtures/
git commit -m "Actualizar fixtures con nuevos datos"
git push origin main
```

### 3. Notificar al equipo

Avisa a tu equipo que ejecuten:
```bash
git pull origin main
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

## ❓ Problemas Comunes

### "El contenedor backend no inicia"
```bash
# Ver logs del backend
docker-compose -f docker-compose.dev.yml logs backend

# Reintentar con build limpio
docker-compose -f docker-compose.dev.yml up --build
```

### "No puedo acceder a http://localhost"
1. Verifica que los contenedores estén corriendo:
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```
2. Verifica que el puerto 80 no esté ocupado
3. Prueba con `http://127.0.0.1`

### "La base de datos no tiene datos"
```bash
# Verificar que los fixtures existan
ls -la backend/fixtures/

# Cargar manualmente si es necesario
docker-compose -f docker-compose.dev.yml exec backend python init_db.py
```

### "Error al cargar fixtures"
```bash
# Verificar que los archivos JSON sean válidos
cat backend/fixtures/initial_data.json | python -m json.tool

# Ver logs detallados
docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata backend/fixtures/initial_data.json --verbosity 2
```

## 📁 Estructura de Archivos Importantes

```
Pagina-de-Asistencia-MAC/
├── .env.development           # Variables de entorno (NO en Git)
├── .env.development.example   # Plantilla de variables de entorno
├── docker-compose.dev.yml     # Configuración Docker para desarrollo
├── export_fixtures.py         # Script para exportar datos
├── backend/
│   ├── init_db.py            # Script de inicialización automática
│   └── fixtures/             # Datos iniciales (fixtures)
│       ├── initial_data.json # Usuarios y perfiles
│       └── initial_events.json # Eventos (si existen)
└── SETUP_COLABORADORES.md     # Esta guía
```

## 🔐 Seguridad

- **NO subas archivos `.env`** a GitHub (ya están en `.gitignore`)
- Los fixtures pueden contener **contraseñas hasheadas** (seguras)
- Si compartes fixtures, asegúrate de que no contengan **datos sensibles reales**
- En producción, siempre cambia las contraseñas por defecto

## 📞 Soporte

Si tienes problemas:

1. Revisa esta guía
2. Verifica los logs: `docker-compose -f docker-compose.dev.yml logs`
3. Consulta el README principal del proyecto
4. Pregunta al equipo de desarrollo

---

**¡Bienvenido al equipo de desarrollo! 🎉**
