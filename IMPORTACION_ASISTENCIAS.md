# 📥 Guía de Importación/Exportación de Asistencias

## 📋 Descripción General

El sistema permite importar y exportar asistencias y estadísticas desde el admin de Django usando archivos Excel (.xlsx) o CSV.

## ✨ Características

### 1. **Asistencias (Attendance)**

#### Importar Asistencias
- ✅ Botón "Importar" disponible en `/admin/attendance/attendance/`
- ✅ Formatos soportados: Excel (.xlsx), CSV (.csv)
- ✅ **Permite importar asistencias pasadas** (fuera de ventana de tiempo)
- ✅ Valida duplicados y eventos simultáneos automáticamente
- ✅ Auto-crea permisos de Asistente si no existen

#### Exportar Asistencias
- ✅ Botón "Exportar" disponible en la lista
- ✅ Formatos: Excel (.xlsx), CSV (.csv)

### 2. **Estadísticas de Asistencia (AttendanceStats)**

#### Importar Estadísticas
- ✅ Botón "Importar" disponible en `/admin/attendance/attendancestats/`
- ✅ Permite actualizar estadísticas masivamente

#### Exportar Estadísticas
- ✅ Botón "Exportar" para todas las estadísticas
- ✅ Acción "📊 Exportar estadísticas seleccionadas"
- ✅ Acción "📊 Exportar estudiantes que cumplen requisito para constancia"
- ✅ Acción "🔄 Actualizar estadísticas seleccionadas"

---

## 📊 Formato del Archivo Excel para Importar Asistencias

### Columnas Requeridas:

| Columna | Descripción | Ejemplo | Obligatorio |
|---------|-------------|---------|-------------|
| `account_number` | Número de cuenta del estudiante (8 dígitos) | 32114471 | ✅ Sí |
| `student_name` | Nombre completo del estudiante | Lopez Martinez Valeria | ❌ No (solo referencia) |
| `event_title` | Título exacto del evento | Matemáticas Aplicadas a Medicina... | ✅ Sí |
| `registered_by_account` | Cuenta del asistente que registra | 11111111 | ❌ No (default: 11111111) |
| `timestamp` | Fecha y hora del registro | 2025-10-21 11:30:00 | ❌ No (default: ahora) |
| `registration_method` | Método de registro | manual | ❌ No (default: manual) |
| `notes` | Notas adicionales | Importado desde Excel | ❌ No |
| `is_valid` | ¿Es válida la asistencia? | True | ❌ No (default: True) |

### Ejemplo de Archivo Excel:

```
account_number | student_name              | event_title                                      | registered_by_account
32114471       | Lopez Martinez Valeria    | Matemáticas Aplicadas a Medicina...              | 11111111
31904405       | Lopez Martinez Angel      | La presión fiscal como oportunidad...            | 11111111
42510571       | Almaraz Ramirez Rafael    | Tecnologías IIoT al servicio de la Industria     | 11111111
```

---

## ⚙️ Comportamiento del Sistema

### 🔓 skip_validation=True

Cuando se importan asistencias, el sistema usa `skip_validation=True` que:

✅ **PERMITE:**
- Importar asistencias fuera de la ventana de tiempo del evento
- Importar asistencias de eventos pasados
- Procesar importaciones masivas históricas

✅ **MANTIENE VALIDACIÓN DE:**
- ❌ **Duplicados**: No permite crear dos asistencias del mismo estudiante al mismo evento
- ❌ **Eventos simultáneos**: No permite asistencia a dos eventos que ocurren al mismo tiempo

### 🔐 Permisos de Asistente

El sistema **automáticamente**:
1. Busca el asistente por `registered_by_account`
2. Si no existe, usa el asistente por defecto (11111111)
3. Verifica si tiene permisos en la tabla `Asistente`
4. Si no tiene permisos, los crea automáticamente con `can_manage_events=True`

---

## 🚀 Cómo Usar

### Importar Asistencias desde Admin

1. Ve a `/admin/attendance/attendance/`
2. Click en botón **"IMPORTAR"** (arriba a la derecha)
3. Selecciona tu archivo Excel o CSV
4. El sistema muestra una **vista previa** de los cambios
5. Revisa los errores si los hay
6. Click en **"Confirmar importación"**
7. ✅ Listo! Las asistencias se importaron

### Exportar Asistencias

1. Ve a `/admin/attendance/attendance/`
2. Click en botón **"EXPORTAR"**
3. Selecciona formato (Excel o CSV)
4. Se descarga el archivo automáticamente

### Exportar Estudiantes con Constancia

1. Ve a `/admin/attendance/attendancestats/`
2. Selecciona estudiantes (o déjalos todos)
3. En "Acción": selecciona **"📊 Exportar estudiantes que cumplen requisito para constancia"**
4. Click en **"Ir"**
5. Se descarga Excel con estudiantes que cumplen el % mínimo

---

## ⚠️ Errores Comunes y Soluciones

### Error: "Estudiante con cuenta XXXXX no encontrado"
**Causa:** El número de cuenta no existe en la base de datos
**Solución:** Verifica que el estudiante esté registrado en el sistema

### Error: "Evento 'XXXXX' no encontrado"
**Causa:** El título del evento no coincide exactamente
**Solución:** Copia el título exacto desde `/admin/events/event/`

### Error: "Este estudiante ya tiene asistencia registrada para este evento"
**Causa:** Ya existe una asistencia para ese estudiante en ese evento
**Solución:** Es un duplicado, omítelo o elimina el existente primero

### Error: "El estudiante ya tiene asistencia registrada en un evento simultáneo"
**Causa:** El estudiante tiene asistencia en otro evento que ocurre al mismo tiempo
**Solución:** El estudiante no puede estar en dos lugares a la vez. Elige uno solo.

---

## 🔄 Actualizar Estadísticas después de Importar

Las estadísticas se actualizan **automáticamente** después de cada importación.

Si necesitas actualizar manualmente:
1. Ve a `/admin/attendance/attendancestats/`
2. Selecciona los estudiantes
3. Acción: **"🔄 Actualizar estadísticas seleccionadas"**
4. Click en **"Ir"**

---

## 📝 Notas Importantes

1. **Solo superusuarios** pueden importar asistencias
2. El sistema **normaliza automáticamente** números de cuenta (elimina espacios, guiones)
3. Los **certificados SSL** pueden variar entre máquinas (regenerar con `./docker/generate_ssl_certs.sh`)
4. La **base de datos NO se sincroniza con Git**, solo el código
5. Para sincronizar datos entre máquinas, usa **backup/restore de PostgreSQL**

---

## 🛠️ Desarrollo

### Archivos Modificados:
- `backend/attendance/admin.py` - Admin con ImportExportMixin
- `backend/attendance/models.py` - Modelo con skip_validation

### Dependencias:
- `django-import-export` - Manejo de importación/exportación
- `openpyxl` - Lectura de archivos Excel
- `pandas` - Procesamiento de datos (opcional)

---

## 📚 Referencias

- Django Import-Export: https://django-import-export.readthedocs.io/
- Admin de Django: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
