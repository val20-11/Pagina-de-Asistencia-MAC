# Guía de Importación de Datos desde Excel

Este documento describe cómo importar eventos y asistencias históricas desde archivos Excel al sistema.

## Requisitos Previos

1. Tener el contenedor Docker del backend ejecutándose
2. Tener los archivos Excel preparados con el formato correcto
3. Conocer el número de cuenta de un asistente autorizado para realizar la importación

## 1. Importación de Eventos

### Formato del Archivo Excel (eventos.xlsx)

El archivo debe tener una hoja llamada **"Eventos"** con las siguientes columnas en la primera fila (encabezados):

| Columna | Tipo | Requerido | Descripción | Ejemplo |
|---------|------|-----------|-------------|---------|
| titulo | Texto | ✓ | Título de la ponencia | "Introducción a Python" |
| descripcion | Texto | ✓ | Descripción del evento | "Taller introductorio sobre Python para principiantes" |
| tipo | Texto | ✓ | Tipo de evento | conference, workshop, panel, seminar |
| modalidad | Texto | ✓ | Modalidad del evento | presencial, online, hybrid |
| ponente | Texto | ✓ | Nombre del ponente | "Dr. Juan Pérez" |
| fecha | Fecha/Texto | ✓ | Fecha del evento | 2024-03-15 o 15/03/2024 |
| hora_inicio | Hora/Texto | ✓ | Hora de inicio | 10:00 |
| hora_fin | Hora/Texto | ✓ | Hora de finalización | 12:00 |
| ubicacion | Texto | ✓ | Ubicación o plataforma | "Aula A-101" o "Zoom" |
| capacidad | Número | ✓ | Capacidad máxima | 100 |
| enlace_reunion | URL | - | Enlace de reunión (para eventos online/hybrid) | https://zoom.us/j/123456 |
| id_reunion | Texto | - | ID de reunión | "123 456 789" |

### Ejemplo de Archivo Excel - Eventos

```
| titulo                    | descripcion                      | tipo       | modalidad   | ponente          | fecha      | hora_inicio | hora_fin | ubicacion | capacidad | enlace_reunion | id_reunion |
|--------------------------|----------------------------------|------------|-------------|------------------|------------|-------------|----------|-----------|-----------|----------------|------------|
| Introducción a Python    | Taller básico de Python          | workshop   | presencial  | Dr. Juan Pérez   | 2024-03-15 | 10:00       | 12:00    | Aula A-101| 50        |                |            |
| Desarrollo Web Moderno   | Conferencia sobre React y Django | conference | online      | Ing. María López | 2024-03-16 | 14:00       | 16:00    | Zoom      | 100       | https://zoom... | 123456789  |
```

### Comando de Importación de Eventos

```bash
# Ingresar al contenedor Docker
docker-compose exec backend bash

# Importar eventos (con validación de fechas)
python manage.py import_events /path/to/eventos.xlsx

# Importar eventos históricos (sin validación de fechas pasadas)
python manage.py import_events /path/to/eventos.xlsx --skip-validation

# Especificar nombre de hoja diferente
python manage.py import_events /path/to/eventos.xlsx --sheet "MisEventos"
```

### Copiar Archivo al Contenedor

Si tu archivo está en tu computadora local, primero cópialo al contenedor:

```bash
# Desde tu terminal local (fuera del contenedor)
docker cp eventos.xlsx pagina-de-asistencia-mac-backend-1:/app/

# Luego importa desde dentro del contenedor
docker-compose exec backend python manage.py import_events /app/eventos.xlsx --skip-validation
```

---

## 2. Importación de Asistencias

### Formato del Archivo Excel (asistencias.xlsx)

El archivo debe tener una hoja llamada **"Asistencias"** con las siguientes columnas en la primera fila (encabezados):

| Columna | Tipo | Requerido | Descripción | Ejemplo |
|---------|------|-----------|-------------|---------|
| numero_cuenta | Texto | ✓ | Número de cuenta del asistente (8 dígitos) | "12345678" |
| nombre_completo | Texto | ✓ | Nombre completo del asistente | "Ana García Rodríguez" |
| titulo_evento | Texto | ✓ | Título exacto del evento (debe existir) | "Introducción a Python" |
| fecha_evento | Fecha/Texto | ✓ | Fecha del evento | 2024-03-15 o 15/03/2024 |
| metodo_registro | Texto | - | Método de registro | manual, barcode, external (default: manual) |
| notas | Texto | - | Notas adicionales | "Llegó tarde" |

### Ejemplo de Archivo Excel - Asistencias

```
| numero_cuenta | nombre_completo      | titulo_evento            | fecha_evento | metodo_registro | notas |
|--------------|----------------------|--------------------------|--------------|-----------------|-------|
| 12345678     | Ana García Rodríguez | Introducción a Python    | 2024-03-15   | manual          |       |
| 87654321     | Carlos Ruiz Martínez | Introducción a Python    | 2024-03-15   | barcode         |       |
| 11223344     | Luis Fernández Pérez | Desarrollo Web Moderno   | 2024-03-16   | external        |       |
```

### Comando de Importación de Asistencias

```bash
# Ingresar al contenedor Docker
docker-compose exec backend bash

# Importar asistencias (REQUIERE número de cuenta del asistente que importa)
python manage.py import_attendance /path/to/asistencias.xlsx --registrador 12345678

# Importar asistencias históricas (sin validación de horarios)
python manage.py import_attendance /path/to/asistencias.xlsx --registrador 12345678 --skip-validation

# Crear automáticamente usuarios externos si no existen
python manage.py import_attendance /path/to/asistencias.xlsx --registrador 12345678 --skip-validation --create-external

# Especificar nombre de hoja diferente
python manage.py import_attendance /path/to/asistencias.xlsx --registrador 12345678 --sheet "MisAsistencias" --skip-validation
```

### Copiar Archivo al Contenedor

```bash
# Desde tu terminal local (fuera del contenedor)
docker cp asistencias.xlsx pagina-de-asistencia-mac-backend-1:/app/

# Luego importa desde dentro del contenedor
docker-compose exec backend python manage.py import_attendance /app/asistencias.xlsx --registrador 12345678 --skip-validation --create-external
```

---

## Flujo Completo de Importación

### Paso 1: Preparar los archivos Excel

1. Crear `eventos.xlsx` con la hoja "Eventos" y los datos de las conferencias
2. Crear `asistencias.xlsx` con la hoja "Asistencias" y los registros de asistencia

### Paso 2: Copiar archivos al contenedor Docker

```bash
docker cp eventos.xlsx pagina-de-asistencia-mac-backend-1:/app/
docker cp asistencias.xlsx pagina-de-asistencia-mac-backend-1:/app/
```

### Paso 3: Importar eventos primero

```bash
docker-compose exec backend python manage.py import_events /app/eventos.xlsx --skip-validation
```

### Paso 4: Importar asistencias

```bash
# Reemplaza 12345678 con el número de cuenta de un asistente autorizado
docker-compose exec backend python manage.py import_attendance /app/asistencias.xlsx --registrador 12345678 --skip-validation --create-external
```

### Paso 5: Verificar la importación

Puedes verificar en:
- Admin de Django: http://localhost/admin/
- API de eventos: http://localhost/api/events/
- API de asistencias: http://localhost/api/attendance/

---

## Notas Importantes

### Para Eventos Históricos

- **IMPORTANTE**: Usa `--skip-validation` para eventos que ya pasaron, de lo contrario el sistema rechazará eventos con fechas pasadas.
- Los eventos en línea o híbridos requieren un `enlace_reunion`

### Para Asistencias Históricas

- **IMPORTANTE**: Usa `--skip-validation` para asistencias de eventos pasados.
- Los eventos deben existir ANTES de importar asistencias (importa eventos primero).
- El `titulo_evento` y `fecha_evento` deben coincidir exactamente con un evento existente.
- El número de cuenta del asistente debe ser de 8 dígitos.

### Usuarios Externos

- Si un número de cuenta no existe como estudiante regular, el comando buscará en usuarios externos.
- Usa `--create-external` para crear automáticamente usuarios externos que no existan.
- Los usuarios externos creados automáticamente serán marcados como "aprobados".

### Números de Cuenta

- Todos los números de cuenta deben tener **8 dígitos**.
- Si tus datos antiguos tienen 7 dígitos, agrégales un 0 al inicio en Excel (ejemplo: 1234567 → 01234567).

### Formato de Fechas y Horas

Formatos aceptados:
- **Fechas**: `YYYY-MM-DD` (2024-03-15) o `DD/MM/YYYY` (15/03/2024)
- **Horas**: `HH:MM` (10:00, 14:30)

### Tipos de Evento

Valores válidos para la columna `tipo`:
- `conference` - Conferencia
- `workshop` - Taller
- `panel` - Mesa Redonda
- `seminar` - Seminario

### Modalidades

Valores válidos para la columna `modalidad`:
- `presencial` - Presencial
- `online` - En línea
- `hybrid` - Híbrido

### Métodos de Registro

Valores válidos para la columna `metodo_registro`:
- `manual` - Registro Manual (default)
- `barcode` - Código de Barras
- `external` - Usuario Externo

---

## Solución de Problemas

### Error: "Evento no encontrado"
- Verifica que el `titulo_evento` y `fecha_evento` coincidan exactamente con un evento existente.
- Importa los eventos antes de las asistencias.

### Error: "No se encontró un asistente"
- Verifica que el número de cuenta del `--registrador` sea válido y pertenezca a un asistente.

### Error: "Usuario no encontrado"
- Usa `--create-external` para crear automáticamente usuarios externos.
- O crea manualmente los usuarios/estudiantes antes de importar.

### Error: "Formato de fecha inválido"
- Verifica que las fechas estén en formato `YYYY-MM-DD` o `DD/MM/YYYY`.
- En Excel, formatea las columnas de fecha como "Texto" para evitar conversiones automáticas.

### Error: "Datos incompletos"
- Verifica que todas las columnas requeridas (marcadas con ✓) tengan valores.

---

## Ejemplo Completo

Aquí hay un ejemplo completo con dos eventos y sus asistencias:

### eventos.xlsx
```
titulo                    | descripcion                      | tipo       | modalidad   | ponente          | fecha      | hora_inicio | hora_fin | ubicacion | capacidad
Introducción a Python    | Taller básico de Python          | workshop   | presencial  | Dr. Juan Pérez   | 2024-03-15 | 10:00       | 12:00    | Aula A-101| 50
Desarrollo Web Moderno   | Conferencia sobre React y Django | conference | presencial  | Ing. María López | 2024-03-16 | 14:00       | 16:00    | Aula B-202| 100
```

### asistencias.xlsx
```
numero_cuenta | nombre_completo      | titulo_evento            | fecha_evento
12345678     | Ana García Rodríguez | Introducción a Python    | 2024-03-15
87654321     | Carlos Ruiz Martínez | Introducción a Python    | 2024-03-15
11223344     | Luis Fernández Pérez | Desarrollo Web Moderno   | 2024-03-16
12345678     | Ana García Rodríguez | Desarrollo Web Moderno   | 2024-03-16
```

### Comandos
```bash
# Copiar archivos
docker cp eventos.xlsx pagina-de-asistencia-mac-backend-1:/app/
docker cp asistencias.xlsx pagina-de-asistencia-mac-backend-1:/app/

# Importar eventos
docker-compose exec backend python manage.py import_events /app/eventos.xlsx --skip-validation

# Importar asistencias (asumiendo que 12345678 es un asistente)
docker-compose exec backend python manage.py import_attendance /app/asistencias.xlsx --registrador 12345678 --skip-validation --create-external
```
