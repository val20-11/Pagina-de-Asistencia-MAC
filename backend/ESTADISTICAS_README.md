# Sistema de Estadísticas de Asistencia

## Cambios Implementados

### 1. Actualización Automática de Estadísticas

Se implementó un sistema de señales (signals) que **actualiza automáticamente** las estadísticas de asistencia cuando:

- **Se elimina un evento**: Todas las estadísticas de todos los estudiantes se recalculan automáticamente
- **Se crea un nuevo evento**: Todas las estadísticas se actualizan para reflejar el nuevo total de eventos
- **Se elimina una asistencia**: Solo se actualizan las estadísticas del estudiante afectado

**Archivos modificados:**
- `backend/attendance/signals.py` (nuevo)
- `backend/attendance/apps.py` (modificado para registrar señales)
- `backend/attendance/__init__.py` (modificado)

### 2. Prevención de Importación Inconsistente

El admin de Django para **AttendanceStats** ahora:

- ✅ **Solo permite EXPORTAR** estadísticas (no importar)
- ✅ Los campos `total_events`, `attended_events` y `attendance_percentage` **siempre se calculan automáticamente**
- ✅ No es posible importar valores manualmente que causen inconsistencias

**Archivos modificados:**
- `backend/attendance/admin.py` - Cambiado de `ImportExportMixin` a `ExportMixin`

### 3. Comando de Recálculo Manual

Se puede ejecutar manualmente el recálculo de estadísticas con:

```bash
docker exec pagina-de-asistencia-mac-backend-1 python manage.py recalculate_stats
```

Este comando:
- ✅ Recalcula las estadísticas de **TODOS** los estudiantes
- ✅ Crea estadísticas para estudiantes que no las tienen
- ✅ Garantiza que **todos los estudiantes tengan el mismo total_events**

**Cuándo usarlo:**
- Después de importar asistencias históricas
- Si sospechas que hay inconsistencias en las estadísticas
- Después de eliminar eventos manualmente desde la BD

## Garantías del Sistema

### ✅ Total de Eventos Consistente

**TODOS los estudiantes siempre tendrán el mismo valor en `total_events`**, que representa el número total de "bloques de horario" de eventos activos en el sistema.

### ✅ Actualización Automática

No es necesario recalcular manualmente las estadísticas en operaciones normales:
- Eliminar un evento → Estadísticas se actualizan automáticamente
- Agregar asistencias → Estadísticas se actualizan automáticamente
- Eliminar asistencias → Estadísticas se actualizan automáticamente

### ✅ Importación Segura y Optimizada

Al importar asistencias desde Excel:
- ✅ Se pueden importar estudiantes y eventos asistidos
- ✅ Las estadísticas se actualizan **automáticamente al finalizar** la importación
- ✅ **Optimización de rendimiento**: Las estadísticas se actualizan en batch (una vez por estudiante afectado, no una vez por asistencia)
- ✅ **NO** se pueden importar valores de `total_events` directamente (son calculados automáticamente)

**Ejemplo de optimización:**
```
Importando 1000 asistencias de 50 estudiantes diferentes:
- ❌ Sin optimización: 1000 actualizaciones de estadísticas
- ✅ Con optimización: 50 actualizaciones (una por estudiante)
```

**Proceso de importación:**
1. Se importan todas las asistencias
2. Se registra qué estudiantes fueron afectados
3. Al finalizar, se actualizan las estadísticas solo de los estudiantes afectados
4. Mensaje de confirmación: `[IMPORTACIÓN] ✓ Estadísticas actualizadas para X estudiante(s)`

## Verificación

Para verificar que todas las estadísticas son consistentes:

```bash
docker exec pagina-de-asistencia-mac-backend-1 python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings.local')
django.setup()
from attendance.models import AttendanceStats

stats = AttendanceStats.objects.all()
total_events_values = stats.values_list('total_events', flat=True).distinct()
print(f'Valores únicos de total_events: {list(total_events_values)}')
if len(total_events_values) == 1:
    print('✓ CORRECTO: Todos tienen el mismo total')
else:
    print('✗ ERROR: Hay inconsistencias')
"
```

## Importación de Asistencias desde Excel

### Paso a Paso

1. **Preparar archivo Excel** con las siguientes columnas:

   **⚠️ IMPORTANTE: NO incluir columna 'id' - se genera automáticamente**

   - `account_number`: Matrícula del estudiante (8 dígitos) **[REQUERIDO]**
   - `student_name`: Nombre del estudiante (opcional, solo informativo)
   - `event_title`: Título exacto del evento (debe existir en la BD) **[REQUERIDO]**
   - `timestamp`: Fecha y hora de registro (opcional)
     - Formatos aceptados:
       - `DD/MM/YYYY HH:MM` (ej: 24/10/2025 11:44)
       - `DD/MM/YYYY HH:MM:SS` (ej: 24/10/2025 11:44:00)
       - `YYYY-MM-DD HH:MM:SS` (ej: 2025-10-24 11:44:00)
       - `YYYY-MM-DD HH:MM` (ej: 2025-10-24 11:44)
   - `registered_by_account`: Matrícula del asistente (opcional, default: 11111111)
   - `registration_method`: manual o barcode (opcional, default: manual)
   - `notes`: Notas adicionales (opcional)
   - `is_valid`: True o False (opcional, default: True)

2. **Ir al Django Admin** → Asistencias → IMPORTAR

3. **Seleccionar el archivo Excel**

4. **Vista previa**: Revisar que los datos se vean correctos

5. **Confirmar importación**

6. **Verificar mensaje**:
   ```
   [IMPORTACIÓN] Actualizando estadísticas de X estudiante(s) afectado(s)...
   [IMPORTACIÓN] ✓ Estadísticas actualizadas para X estudiante(s)
   ```

### Ejemplo de Excel

**✅ CORRECTO (sin columna 'id'):**
```
account_number | student_name    | event_title                          | timestamp
42502372      | Aramburo Chang  | App Kachi México y su cultura       | 24/10/2025 18:30
31720256      | Arenas Juarez   | App Kachi México y su cultura       | 24/10/2025 18:30
42610156      | Barraza Casta.  | De principiante a protector...      | 24/10/2025 19:30
```

**❌ INCORRECTO (con columna 'id'):**
```
id   | account_number | student_name    | event_title                    | timestamp
1815 | 42502372      | Aramburo Chang  | App Kachi México y su cultura | 24/10/2025 18:30
```
⚠️ NO incluir la columna 'id' - causará errores

### Validaciones Automáticas

Durante la importación se valida:
- ✅ Que el estudiante exista en la BD
- ✅ Que el evento exista en la BD
- ✅ Que no haya duplicados (mismo estudiante + mismo evento)
- ✅ Que no haya eventos simultáneos (estudiante no puede estar en dos eventos a la vez)

Si hay errores, se mostrarán en rojo y las filas con error NO se importarán.

### Después de la Importación

**NO es necesario** ejecutar ningún comando adicional. Las estadísticas se actualizan automáticamente.

Si quieres verificar:
```bash
docker exec pagina-de-asistencia-mac-backend-1 python -c "
from attendance.models import AttendanceStats
stats = AttendanceStats.objects.all()
print(f'Total de estudiantes: {stats.count()}')
print(f'Valores de total_events: {set(stats.values_list(\"total_events\", flat=True))}')
"
```

## Administración desde Django Admin

### Acciones disponibles en AttendanceStats Admin:

1. **📊 Exportar estadísticas seleccionadas**
   - Exporta las estadísticas de los estudiantes seleccionados

2. **📊 Exportar estudiantes que cumplen requisito para constancia**
   - Exporta solo los estudiantes que tienen el porcentaje mínimo de asistencia

3. **🔄 Actualizar estadísticas seleccionadas**
   - Recalcula las estadísticas de los estudiantes seleccionados
   - Útil si se modificaron eventos o asistencias

## Notas Técnicas

### Cálculo de Total de Eventos (Bloques de Horario)

El sistema usa **bloques de horario** en lugar de contar eventos individuales:
- Eventos simultáneos en la misma fecha/hora se cuentan como **1 solo bloque**
- El estudiante solo necesita asistir a **uno de los eventos simultáneos** para marcar ese bloque como asistido
- Dos eventos son simultáneos si tienen la **misma fecha, misma hora de inicio y misma hora de fin**

**Ejemplo real del sistema:**
```
21 eventos activos en total:

Bloques con múltiples eventos simultáneos:
- 21/Oct 11:00-12:00: 2 eventos (cuenta como 1 bloque)
  • Matemáticas Aplicadas a Medicina...
  • Tecnologías IIoT al servicio de la Industria

- 21/Oct 12:00-13:00: 2 eventos (cuenta como 1 bloque)
  • La presión fiscal como oportunidad...
  • Matemáticas Aplicadas y Computación...

- 23/Oct 11:00-12:00: 2 eventos (cuenta como 1 bloque)
  • MAC aplicado en el sector de aseguradoras
  • Análisis de Escenas Auditivas

- 23/Oct 12:00-13:00: 2 eventos (cuenta como 1 bloque)
  • Investigación en MAC con IA
  • Cuando los datos hablan...

Total de bloques = 21 eventos - 8 (que se combinan en 4 pares) + 4 (bloques únicos) = 17 bloques
```

**IMPORTANTE:** Si tienes 21 eventos activos pero 4 pares son simultáneos, el `total_events` será **17**, no 21.

### Logs de las Señales

Las señales imprimen mensajes en la consola del contenedor Docker:

```
[SIGNAL] Evento 'Nombre del Evento' eliminado. Actualizando estadísticas de todos los estudiantes...
[SIGNAL] Se actualizaron las estadísticas de 6359 estudiantes.
```

Para ver los logs:
```bash
docker logs -f pagina-de-asistencia-mac-backend-1
```

## Solución de Problemas

### Problema: "Tengo estudiantes con diferentes total_events"

**Solución:**
```bash
docker exec pagina-de-asistencia-mac-backend-1 python manage.py recalculate_stats
```

### Problema: "Las estadísticas no se actualizan al eliminar un evento"

**Verificar:**
1. Que el contenedor Docker esté corriendo
2. Que no haya errores en los logs: `docker logs pagina-de-asistencia-mac-backend-1`
3. Ejecutar recalculate_stats manualmente si es necesario

### Problema: "Quiero importar estadísticas desde Excel"

**Solución:**
- NO importes estadísticas directamente
- En su lugar, importa solo las **asistencias** (estudiantes + eventos)
- Las estadísticas se calcularán automáticamente
- Luego ejecuta: `python manage.py recalculate_stats` para asegurar consistencia

## Migración de Datos Históricos

Si tienes datos históricos con estadísticas inconsistentes:

1. **Respalda tu base de datos** (por si acaso)
2. Ejecuta el comando de recálculo:
   ```bash
   docker exec pagina-de-asistencia-mac-backend-1 python manage.py recalculate_stats
   ```
3. Verifica la consistencia con el script de verificación
4. Exporta las estadísticas actualizadas desde el admin

---

**Fecha de implementación:** Octubre 2025
**Versión:** 1.0
