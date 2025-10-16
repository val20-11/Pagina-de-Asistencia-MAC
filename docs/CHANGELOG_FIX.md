# Changelog - Corrección de Errores de Autenticación

**Fecha**: 2025-10-12
**Versión**: 1.0.1

## Problemas Resueltos

### 1. Error 403 CSRF en Login desde Navegador

**Síntoma**: Al intentar hacer login desde el navegador web, el backend retornaba error 403 (Forbidden) con mensaje "Acceso denegado (permisos insuficientes)".

**Causa Raíz**: Django estaba aplicando validación CSRF a todas las rutas, incluyendo las rutas de API REST que usan JWT para autenticación. El middleware `CsrfViewMiddleware` rechazaba requests sin token CSRF.

**Solución Implementada**:

1. **Creado nuevo middleware** `DisableCSRFOnAPIMiddleware` en `backend/mac_attendance/middleware.py`
   - Desactiva validación CSRF para todas las rutas que coincidan con `^api/.*$`
   - Colocado antes de `CsrfViewMiddleware` en la cadena de middleware

2. **Actualizado `settings.py`**:
   - Agregado `CSRF_EXEMPT_URLS = [r'^api/.*$']`
   - Actualizado `CORS_ALLOWED_ORIGINS` para incluir `http://localhost`
   - Agregado `CSRF_TRUSTED_ORIGINS` para desarrollo local
   - Agregado middleware en posición correcta (línea 45)

3. **Configuración final de middleware**:
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'mac_attendance.middleware.DisableCSRFOnAPIMiddleware',  # ← NUEVO
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mac_attendance.middleware.AuditMiddleware',
]
```

**Resultado**: ✅ Login desde navegador funciona correctamente sin error 403

---

### 2. Endpoint `/api/` Expuesto Públicamente

**Síntoma**: Cualquier usuario no autenticado podía acceder a `/api/` y `/api/docs/` para ver información sobre todos los endpoints del sistema.

**Riesgo de Seguridad**: Exposición de información sensible sobre la estructura de la API.

**Solución Implementada**:

1. **Actualizado `backend/mac_attendance/urls.py`**:
   - Agregado decorador `@permission_classes([IsAuthenticated])` a función `api_root()`
   - Agregado decorador `@permission_classes([IsAuthenticated])` a función `api_docs()`
   - Ambos endpoints ahora requieren token JWT válido

2. **Código modificado**:
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_root(request):
    """API root endpoint - Returns comprehensive API information (Protected)"""
    # ...

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_docs(request):
    """API documentation endpoint (Protected)"""
    # ...
```

**Resultado**:
- ✅ `/api/` sin autenticación → Error 401 "Las credenciales de autenticación no se proveyeron"
- ✅ `/api/` con token válido → Muestra información de la API
- ✅ `/api/docs/` ahora también protegido

---

## Archivos Modificados

### 1. `backend/mac_attendance/middleware.py`
- **Agregado**: Clase `DisableCSRFOnAPIMiddleware`
- **Líneas**: 103-126

### 2. `backend/mac_attendance/settings.py`
- **Modificado**: Lista `MIDDLEWARE` (línea 40-51)
- **Agregado**: `CSRF_EXEMPT_URLS` (línea 154)
- **Modificado**: `CORS_ALLOWED_ORIGINS` (línea 140-143)
- **Agregado**: `CSRF_TRUSTED_ORIGINS` (línea 148-151)

### 3. `backend/mac_attendance/urls.py`
- **Modificado**: Función `api_root()` - agregado autenticación (línea 23-26)
- **Modificado**: Función `api_docs()` - agregado autenticación (línea 138-140)

### 4. `API_DOCUMENTATION.md`
- **Actualizado**: Sección "Acceder a la Documentación" con advertencia de autenticación

---

## Testing Realizado

### Test 1: Login desde cURL (simulando navegador)
```bash
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost" \
  -d '{"account_number":"3123123"}'
```
**Resultado**: ✅ Status 200, retorna tokens JWT

### Test 2: API Root sin autenticación
```bash
curl -X GET http://localhost/api/
```
**Resultado**: ✅ Status 401, mensaje de error apropiado

### Test 3: API Root con autenticación
```bash
curl -X GET http://localhost/api/ \
  -H "Authorization: Bearer <token>"
```
**Resultado**: ✅ Status 200, retorna información de API

---

## Seguridad Mejorada

### Antes de la Corrección:
- ❌ Login fallaba con 403 desde navegador
- ❌ `/api/` accesible sin autenticación
- ❌ `/api/docs/` accesible sin autenticación
- ⚠️ Información de endpoints expuesta públicamente

### Después de la Corrección:
- ✅ Login funciona correctamente desde navegador
- ✅ `/api/` requiere autenticación JWT
- ✅ `/api/docs/` requiere autenticación JWT
- ✅ Información de API protegida
- ✅ CSRF deshabilitado solo en rutas API (usamos JWT)
- ✅ CSRF sigue activo en panel admin (usa sesiones)

---

## Notas Técnicas

### ¿Por qué deshabilitar CSRF en API?

Django REST Framework con JWT no necesita protección CSRF porque:
1. **No usa cookies de sesión**: JWT se envía en header `Authorization`
2. **Tokens stateless**: No hay estado de sesión en servidor
3. **CORS protege**: CORS ya previene requests desde orígenes no autorizados
4. **JWT expira**: Tokens tienen tiempo de vida limitado (1 hora)

### Alternativa No Recomendada
Usar `@csrf_exempt` en cada vista → ❌ Requiere modificar múltiples archivos
**Nuestra solución**: Middleware centralizado → ✅ Un solo punto de configuración

---

## Cómo Probar

### 1. Desde el navegador (http://localhost)
1. Abrir la aplicación
2. Ingresar número de cuenta: `3123123`
3. Click en "Iniciar Sesión"
4. ✅ Debe iniciar sesión exitosamente

### 2. Verificar protección de `/api/`
1. Abrir navegador e ir a http://localhost/api/
2. ✅ Debe mostrar: `{"detail": "Las credenciales de autenticación no se proveyeron."}`

### 3. Acceder a `/api/` autenticado
1. Hacer login primero
2. Copiar el access_token
3. Usar extensión de navegador o Postman:
   - URL: http://localhost/api/
   - Header: `Authorization: Bearer <access_token>`
4. ✅ Debe mostrar información completa de la API

---

## Próximos Pasos (Opcional)

- [ ] Implementar rate limiting específico para login (ya existe global)
- [ ] Agregar logs de accesos exitosos/fallidos a `/api/`
- [ ] Considerar implementar API key para documentación pública
- [ ] Agregar tests automatizados para validación CSRF

---

## Contacto

Si encuentras algún problema con estas correcciones, revisa:
1. Logs del backend: `docker-compose logs backend`
2. Logs de nginx: `docker-compose logs nginx`
3. Consola del navegador (F12) para ver errores de JavaScript

---

**Revisado y probado**: ✅
**Contenedores actualizados**: ✅
**Documentación actualizada**: ✅
