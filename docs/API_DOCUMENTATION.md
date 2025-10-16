# Sistema de Asistencia MAC - Documentación de API

## Información General

- **Version**: 1.0.0
- **Base URL**: `http://localhost/api/`
- **Autenticación**: JWT Bearer Token
- **Formato**: JSON

## Índice

- [Inicio Rápido](#inicio-rápido)
- [Autenticación](#autenticación)
- [Endpoints](#endpoints)
  - [Authentication](#authentication-endpoints)
  - [Events](#events-endpoints)
  - [Attendance](#attendance-endpoints)
- [Códigos de Estado](#códigos-de-estado)
- [Ejemplos con cURL](#ejemplos-con-curl)
- [Testing con Postman](#testing-con-postman)

## Inicio Rápido

### Acceder a la Documentación

- **API Root (JSON)**: http://localhost/api/ 🔒 **Requiere Autenticación**
- **Documentación HTML**: http://localhost/api/docs/ 🔒 **Requiere Autenticación**
- **Panel Admin**: http://localhost/admin/

> **Nota**: Los endpoints `/api/` y `/api/docs/` ahora requieren autenticación JWT.
> Primero debes hacer login en `/api/auth/login/` para obtener un token de acceso.

### Flujo Básico

1. **Login**: Obtener tokens de acceso
2. **Usar Token**: Incluir en header `Authorization`
3. **Refrescar Token**: Cuando expire el access token

## Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### Obtener Token

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "account_number": "3123123"
}
```

**Respuesta:**
```json
{
  "message": "Login exitoso",
  "user": {
    "id": 3,
    "username": "3123123",
    "profile": {
      "account_number": "3123123",
      "user_type": "assistant",
      "full_name": "pancho"
    }
  },
  "tokens": {
    "access": "eyJhbGci....",
    "refresh": "eyJhbGci...."
  }
}
```

### Usar Token

Para endpoints que requieren autenticación, incluye el header:

```
Authorization: Bearer <your_access_token>
```

### Refrescar Token

```bash
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "<your_refresh_token>"
}
```

## Endpoints

### Authentication Endpoints

#### 1. Login
```
POST /api/auth/login/
```

**Descripción**: Iniciar sesión con número de cuenta

**Auth Required**: ❌ No

**Body**:
```json
{
  "account_number": "1234567"
}
```

**Response 200**:
```json
{
  "message": "Login exitoso",
  "user": { ... },
  "tokens": {
    "access": "...",
    "refresh": "..."
  }
}
```

**Response 400**:
```json
{
  "account_number": ["El número de cuenta debe tener exactamente 7 dígitos."]
}
```

---

#### 2. Logout
```
POST /api/auth/logout/
```

**Descripción**: Cerrar sesión

**Auth Required**: ✅ Sí

**Response 200**:
```json
{
  "message": "Logout exitoso"
}
```

---

#### 3. Get Profile
```
GET /api/auth/profile/
```

**Descripción**: Obtener perfil del usuario autenticado

**Auth Required**: ✅ Sí

**Response 200**:
```json
{
  "id": 3,
  "username": "3123123",
  "email": "",
  "profile": {
    "account_number": "3123123",
    "user_type": "assistant",
    "full_name": "pancho"
  },
  "is_staff": false
}
```

---

#### 4. Check Auth Status
```
GET /api/auth/check-auth/
```

**Descripción**: Verificar si el usuario está autenticado

**Auth Required**: ❌ No

**Response 200**:
```json
{
  "is_authenticated": true,
  "user": { ... }
}
```

---

#### 5. Refresh Token
```
POST /api/auth/token/refresh/
```

**Descripción**: Refrescar access token usando refresh token

**Auth Required**: ❌ No

**Body**:
```json
{
  "refresh": "<refresh_token>"
}
```

**Response 200**:
```json
{
  "access": "<new_access_token>"
}
```

---

#### 6. System Configuration
```
GET /api/auth/system-config/
```

**Descripción**: Obtener configuración del sistema

**Auth Required**: ✅ Sí

**Response 200**:
```json
{
  "minimum_attendance_percentage": 80.0,
  "minutes_before_event": 10,
  "minutes_after_start": 25
}
```

---

### Events Endpoints

#### 1. List Events
```
GET /api/events/
```

**Descripción**: Listar todos los eventos activos

**Auth Required**: ❌ No

**Response 200**:
```json
[
  {
    "id": 1,
    "title": "Inteligencia Artificial",
    "description": "Conferencia sobre IA",
    "event_type": "conference",
    "modality": "presencial",
    "speaker": "Dr. García",
    "date": "2025-10-12",
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "location": "Auditorio A",
    "max_capacity": 100,
    "is_active": true
  }
]
```

---

#### 2. Register External User
```
POST /api/events/external/register/
```

**Descripción**: Registrar un usuario externo para eventos

**Auth Required**: ✅ Sí (Solo asistentes)

**Body**:
```json
{
  "full_name": "Juan Pérez",
  "account_number": "9999999"
}
```

**Response 201**:
```json
{
  "id": 10,
  "full_name": "Juan Pérez",
  "account_number": "9999999",
  "status": "approved"
}
```

---

#### 3. Search External Users
```
GET /api/events/external/search/?account_number=9999999
```

**Descripción**: Buscar usuarios externos

**Auth Required**: ✅ Sí

**Query Parameters**:
- `account_number` (string): Número de cuenta a buscar

**Response 200**:
```json
[
  {
    "id": 10,
    "full_name": "Juan Pérez",
    "account_number": "9999999",
    "status": "approved"
  }
]
```

---

#### 4. Approve External User
```
POST /api/events/external/<user_id>/approve/
```

**Descripción**: Aprobar un usuario externo

**Auth Required**: ✅ Sí (Solo asistentes)

**Body**:
```json
{
  "approved": true
}
```

**Response 200**:
```json
{
  "message": "Usuario aprobado exitosamente"
}
```

---

### Attendance Endpoints

#### 1. Register Attendance
```
POST /api/attendance/
```

**Descripción**: Registrar asistencia a un evento

**Auth Required**: ✅ Sí (Solo asistentes)

**Body**:
```json
{
  "event_id": 1,
  "account_number": "3123123",
  "registration_method": "manual"
}
```

**Response 201**:
```json
{
  "id": 42,
  "event": 1,
  "timestamp": "2025-10-12T10:30:00Z",
  "is_valid": true
}
```

---

#### 2. Get Student Stats
```
GET /api/attendance/stats/?account_number=0000111
```

**Descripción**: Obtener estadísticas de asistencia de un estudiante

**Auth Required**: ✅ Sí

**Query Parameters**:
- `account_number` (string): Número de cuenta del estudiante

**Response 200**:
```json
{
  "total_events": 10,
  "attended_events": 8,
  "attendance_percentage": 80.0,
  "meets_minimum": true
}
```

---

#### 3. Get Recent Attendances
```
GET /api/attendance/recent/
```

**Descripción**: Obtener asistencias recientes (últimas 50)

**Auth Required**: ✅ Sí

**Response 200**:
```json
[
  {
    "id": 42,
    "student": {
      "account_number": "0000111",
      "full_name": "María García"
    },
    "event": {
      "id": 1,
      "title": "Inteligencia Artificial"
    },
    "timestamp": "2025-10-12T10:30:00Z",
    "is_valid": true
  }
]
```

---

#### 4. Get My Attendances
```
GET /api/attendance/my/
```

**Descripción**: Obtener mis asistencias registradas

**Auth Required**: ✅ Sí

**Response 200**:
```json
[
  {
    "id": 42,
    "event": {
      "id": 1,
      "title": "Inteligencia Artificial",
      "date": "2025-10-12",
      "start_time": "10:00:00"
    },
    "timestamp": "2025-10-12T10:30:00Z",
    "is_valid": true
  }
]
```

---

## Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado o token inválido |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |

## Ejemplos con cURL

### 1. Login y obtener token

```bash
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"account_number":"3123123"}'
```

### 2. Obtener perfil (con token)

```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost/api/auth/profile/ \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Listar eventos

```bash
curl -X GET http://localhost/api/events/
```

### 4. Registrar asistencia

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost/api/attendance/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "account_number": "0000111",
    "registration_method": "manual"
  }'
```

### 5. Obtener estadísticas

```bash
TOKEN="your_access_token_here"

curl -X GET "http://localhost/api/attendance/stats/?account_number=0000111" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Refrescar token

```bash
REFRESH_TOKEN="your_refresh_token_here"

curl -X POST http://localhost/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}"
```

## Testing con Postman

### Importar Collection

1. Descarga la colección: `postman_collection.json`
2. En Postman: File → Import
3. Selecciona el archivo JSON

### Variables de Entorno

Crea un entorno con estas variables:

```json
{
  "base_url": "http://localhost",
  "access_token": "",
  "refresh_token": "",
  "account_number": "3123123"
}
```

### Workflow de Testing

1. **Login**: Ejecuta el request de login
2. **Set Token**: Copia el access_token a la variable de entorno
3. **Test Endpoints**: Ejecuta otros requests usando `{{access_token}}`

## Rate Limiting

La API implementa rate limiting para prevenir abuso:

- **Login**: 5 intentos por minuto por IP
- **Check Auth**: 30 consultas por minuto por IP
- **Token Refresh**: 10 intentos por minuto por IP

## Errores Comunes

### 401 Unauthorized

**Causa**: Token inválido o expirado

**Solución**: Refrescar el token o hacer login nuevamente

```bash
# Refrescar token
curl -X POST http://localhost/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

### 400 Bad Request

**Causa**: Datos inválidos en el request

**Solución**: Verificar el formato y campos requeridos

```json
{
  "account_number": ["El número de cuenta debe tener exactamente 7 dígitos."]
}
```

### 429 Too Many Requests

**Causa**: Rate limit excedido

**Solución**: Esperar un minuto antes de reintentar

## Best Practices

### 1. Manejo de Tokens

```javascript
// Guardar tokens
localStorage.setItem('access_token', response.tokens.access);
localStorage.setItem('refresh_token', response.tokens.refresh);

// Incluir en requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
}

// Refrescar cuando expire
if (error.status === 401) {
  // Intentar refrescar
  const newToken = await refreshToken();
  // Reintentar request original
}
```

### 2. Manejo de Errores

```javascript
try {
  const response = await fetch('/api/endpoint/', options);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Request failed');
  }
  return await response.json();
} catch (error) {
  console.error('API Error:', error);
  // Mostrar mensaje al usuario
}
```

### 3. Rate Limiting

```javascript
// Implementar backoff exponencial
const retryWithBackoff = async (fn, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < retries - 1) {
        await new Promise(r => setTimeout(r, 2 ** i * 1000));
        continue;
      }
      throw error;
    }
  }
};
```

## Seguridad

### Headers de Seguridad

La API implementa los siguientes headers de seguridad:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### CORS

CORS está configurado para permitir requests desde:
- `http://localhost`
- `http://127.0.0.1`

### HTTPS

En producción, **siempre** usar HTTPS para proteger los tokens.

## Soporte

- **Documentación**: http://localhost/api/docs/
- **Admin Panel**: http://localhost/admin/
- **Issues**: https://github.com/yourusername/mac_attendance/issues

## Changelog

### v1.0.0 (2025-10-12)
- ✅ Autenticación JWT
- ✅ Gestión de eventos
- ✅ Registro de asistencias
- ✅ Estadísticas de asistencia
- ✅ Usuarios externos
- ✅ Rate limiting
- ✅ Documentación completa
