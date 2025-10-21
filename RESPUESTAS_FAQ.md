# Preguntas Frecuentes - FAQ

## ❓ ¿Ya está la página en producción?

**Respuesta: NO, aún no está en producción.**

### Estado Actual

- ✅ **Proyecto configurado** para producción
- ✅ **Docker Compose** de producción listo
- ✅ **SSL/HTTPS** configurado (con certificados autofirmados)
- ✅ **Datos iniciales** preparados y listos para cargarse
- ❌ **NO desplegado** en un servidor público

### Dónde Funciona Ahora

- ✅ **Localmente** en tu máquina (http://localhost)
- ✅ **Desarrollo** con Docker (puerto 80)

### Para Poner en Producción

Ver [GUIA_PRODUCCION.md](GUIA_PRODUCCION.md) - Necesitas:

1. Acceso al servidor (IP configurada: 132.248.80.77)
2. Configurar variables de entorno de producción
3. Certificados SSL válidos (o Let's Encrypt)
4. Ejecutar: `docker-compose up -d`

---

## ❓ ¿Cuando alguien clone el repo, tendrá mi base de datos?

**Respuesta: SÍ, automáticamente. ✅**

### Cómo Funciona

Cuando alguien clona el repositorio y ejecuta:

```bash
git clone https://github.com/val20-11/Pagina-de-Asistencia-MAC.git
cd Pagina-de-Asistencia-MAC
cp .env.development.example .env.development
docker-compose -f docker-compose.dev.yml up -d
```

**Esto sucede automáticamente:**

1. Docker inicia PostgreSQL (base de datos vacía)
2. Django ejecuta migraciones (crea tablas)
3. **`init_db.py` se ejecuta automáticamente**
4. El script detecta que la BD está vacía
5. Carga los fixtures desde `backend/fixtures/initial_data.json`
6. Los datos se importan a PostgreSQL
7. ¡El colaborador tiene exactamente tus mismos datos!

### Qué Datos se Comparten

El archivo `backend/fixtures/initial_data.json` contiene:

- ✅ Tu usuario superusuario "Admin"
- ✅ Todos los usuarios asistentes que creaste
- ✅ Perfiles de usuario
- ✅ Eventos (si los exportaste)
- ✅ Asistencias registradas (si las exportaste)

**IMPORTANTE:** Las contraseñas están hasheadas (seguras), NO están en texto plano.

---

## ❓ ¿Pueden entrar con mi superusuario?

**Respuesta: SÍ, pero solo si conocen la contraseña. ✅**

### Seguridad de las Contraseñas

Las contraseñas en los fixtures están **hasheadas** (encriptadas). Ejemplo:

```json
{
  "username": "Admin",
  "password": "pbkdf2_sha256$1000000$6z4YF8h...$XgRW+e3Bw..."
}
```

Esto NO es la contraseña real, es un hash. Nadie puede ver la contraseña original.

### Cómo Funciona

Cuando un colaborador clona el repo:

1. ✅ Se crea el usuario "Admin" con el **mismo hash de contraseña**
2. ✅ Si el colaborador sabe tu contraseña original, puede entrar
3. ✅ Si NO sabe la contraseña, NO puede entrar

### ¿Qué Hacer?

#### Opción 1: Compartir la Contraseña (Equipo de Confianza)

Si confías en tus colaboradores:
- Compárteles la contraseña del superusuario "Admin"
- Todos pueden administrar el sistema

#### Opción 2: Que Cada Uno Cree su Superusuario

Si NO quieres compartir tu contraseña:

```bash
# Cada colaborador ejecuta:
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

# Y crea su propio usuario admin
```

#### Opción 3: Cambiar la Contraseña en los Fixtures (Recomendado)

Crea una contraseña genérica para desarrollo que todos conozcan:

1. En tu máquina local:
```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py changepassword Admin
# Nueva contraseña: admin123 (por ejemplo)
```

2. Exportar los nuevos fixtures:
```bash
python export_fixtures.py
```

3. Subir a GitHub:
```bash
git add backend/fixtures/
git commit -m "Actualizar contraseña de desarrollo"
git push origin main
```

4. Documentar en `SETUP_COLABORADORES.md`:
   - Usuario: Admin
   - Contraseña: admin123

**IMPORTANTE:** En producción, SIEMPRE cambia esta contraseña a una segura.

---

## ❓ ¿Cómo actualizo los datos que comparto?

**Respuesta: Con el script de exportación. ✅**

### Proceso

1. **Haz cambios** en tu base de datos local
   - Crea usuarios
   - Crea eventos
   - Registra asistencias
   - etc.

2. **Exporta los cambios:**
   ```bash
   python export_fixtures.py
   ```

3. **Sube a GitHub:**
   ```bash
   git add backend/fixtures/
   git commit -m "Actualizar datos iniciales"
   git push origin main
   ```

4. **Los colaboradores actualizan:**
   ```bash
   git pull origin main
   docker-compose -f docker-compose.dev.yml down -v  # Borra BD actual
   docker-compose -f docker-compose.dev.yml up -d     # Recarga fixtures
   ```

---

## ❓ ¿Qué pasa si NO quiero compartir todos mis datos?

**Respuesta: Puedes crear fixtures personalizados. ✅**

### Opción 1: Exportar Solo Ciertos Modelos

Modifica `export_fixtures.py` para exportar solo lo que quieras:

```python
# Solo usuarios, sin eventos
cmd = [
    "docker", "exec", "pagina-de-asistencia-mac-backend-1",
    "python", "manage.py", "dumpdata",
    "--indent", "2",
    "auth.user",                  # Solo esto
    "authentication.userprofile"  # Y esto
    # NO exportar eventos ni asistencias
]
```

### Opción 2: Crear Fixtures Mínimos

Crea fixtures básicos a mano con solo:
- 1 superusuario genérico
- 1-2 usuarios de ejemplo

### Opción 3: Usar Variables de Entorno

En producción, carga diferentes fixtures:

```bash
# En .env.production
LOAD_INITIAL_FIXTURES=false

# En init_db.py, verificar esta variable
```

---

## ❓ ¿Los fixtures se suben a GitHub?

**Respuesta: SÍ, están configurados para subirse. ✅**

### Qué se Sube

- ✅ `backend/fixtures/*.json` - Datos iniciales (usuarios, eventos)
- ✅ `backend/fixtures/*.sql` - Backups SQL (si existen)

### Qué NO se Sube

- ❌ `.env` - Variables de entorno (contraseñas, claves)
- ❌ `backend/db.sqlite3` - Base de datos SQLite
- ❌ `backend/media/` - Archivos subidos
- ❌ `backend/logs/` - Logs

Ver `.gitignore` para detalles.

---

## ❓ ¿Qué pasa en producción con los fixtures?

**Respuesta: Se cargan automáticamente si la BD está vacía. ✅**

### Primera Vez en Producción

```bash
# En el servidor de producción:
docker-compose up -d

[Automáticamente]:
1. PostgreSQL inicia (vacío)
2. Django migra las tablas
3. init_db.py detecta BD vacía
4. Carga backend/fixtures/initial_data.json
5. ¡Sistema listo con tus datos!
```

### Actualizaciones en Producción

Si la BD ya tiene datos, `init_db.py` NO los sobrescribe:

```python
# En init_db.py:
if User.objects.count() > 0:
    print("BD ya tiene usuarios, no se cargan fixtures")
    return
```

Esto previene duplicados y pérdida de datos.

---

## ❓ ¿Cómo funciona sin servidor de producción?

**Respuesta: Funciona perfectamente en modo desarrollo. ✅**

### Actualmente (Sin Servidor)

- ✅ Funciona en tu máquina local
- ✅ Colaboradores lo usan en sus máquinas
- ✅ Cada uno tiene su propia base de datos PostgreSQL local
- ✅ Todos comparten los mismos datos iniciales (via fixtures)

### Cuando Tengas Servidor

- ✅ Mismo código, misma configuración
- ✅ Solo cambias de `docker-compose.dev.yml` a `docker-compose.yml`
- ✅ Configuras variables de producción en `.env.production`
- ✅ ¡Listo para producción!

---

## ❓ Resumen de Respuestas Rápidas

| Pregunta | Respuesta |
|----------|-----------|
| ¿Está en producción? | NO, solo local. Listo para desplegar cuando tengas servidor. |
| ¿Los colaboradores tienen mi BD? | SÍ, automáticamente via fixtures. |
| ¿Pueden usar mi superusuario? | SÍ, si conocen la contraseña (está hasheada). |
| ¿Los fixtures se suben a Git? | SÍ, configurado en .gitignore. |
| ¿Cómo actualizar datos? | `python export_fixtures.py` + git push |
| ¿Funciona sin servidor? | SÍ, perfecto en modo desarrollo. |
| ¿Listo para producción? | SÍ, cuando tengas acceso al servidor. |

---

## 📞 Más Información

- **Inicio Rápido:** [QUICK_START.md](QUICK_START.md)
- **Para Colaboradores:** [SETUP_COLABORADORES.md](SETUP_COLABORADORES.md)
- **Para Producción:** [GUIA_PRODUCCION.md](GUIA_PRODUCCION.md)
- **Resumen Técnico:** [RESUMEN_CONFIGURACION.md](RESUMEN_CONFIGURACION.md)
