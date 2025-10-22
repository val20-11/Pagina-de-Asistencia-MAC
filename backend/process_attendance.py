#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar asistencias desde Excel y agregarlas a la base de datos.
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile
from events.models import Event
from attendance.models import Attendance, AttendanceStats
from django.utils import timezone


def process_attendance_file(excel_file, event_title, assistant_username):
    """
    Procesa el archivo de asistencias y las agrega a la base de datos.

    Args:
        excel_file: Ruta al archivo Excel
        event_title: Título de la conferencia/evento
        assistant_username: Username del asistente que registra
    """
    print("=" * 80)
    print("PROCESANDO ASISTENCIAS")
    print("=" * 80)
    print()

    # 1. Verificar que el evento existe
    print(f"[1/5] Buscando evento: '{event_title}'...")
    try:
        event = Event.objects.get(title=event_title)
        print(f"✓ Evento encontrado: {event.title} (ID: {event.id})")
        print(f"  Fecha: {event.date}")
        print(f"  Tipo: {event.event_type}")
    except Event.DoesNotExist:
        print(f"✗ ERROR: No se encontró el evento '{event_title}'")
        print("\nEventos disponibles:")
        for ev in Event.objects.all():
            print(f"  - {ev.title} ({ev.date})")
        return
    print()

    # 2. Verificar que el asistente existe
    print(f"[2/5] Buscando asistente: '{assistant_username}'...")
    try:
        assistant_user = User.objects.get(username=assistant_username)
        assistant_profile = UserProfile.objects.get(user=assistant_user, user_type='assistant')
        print(f"✓ Asistente encontrado: {assistant_profile.full_name}")
        print(f"  Username: {assistant_user.username}")
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        print(f"✗ ERROR: No se encontró el asistente '{assistant_username}'")
        print("\nAsistentes disponibles:")
        for profile in UserProfile.objects.filter(user_type='assistant'):
            print(f"  - {profile.user.username}: {profile.full_name}")
        return
    print()

    # 3. Leer archivo Excel
    print(f"[3/5] Leyendo archivo: {excel_file}...")
    try:
        df = pd.read_excel(excel_file)
        print(f"✓ Archivo leído correctamente")
        print(f"  Total de registros: {len(df)}")
        print(f"  Columnas: {list(df.columns)}")
    except Exception as e:
        print(f"✗ ERROR al leer el archivo: {e}")
        return
    print()

    # 4. Procesar cada registro
    print(f"[4/5] Procesando asistencias...")
    print()

    created_count = 0
    skipped_count = 0
    error_count = 0
    updated_students = []

    for idx, row in df.iterrows():
        account_number_raw = str(row['account_number']).strip()
        name_in_excel = str(row['full_name']).strip()

        # Normalizar número de cuenta: quitar espacios y tomar solo los primeros 8 dígitos
        account_number = account_number_raw.replace(' ', '').replace('-', '')[:8]

        print(f"  [{idx+1}/{len(df)}] Procesando: {account_number} (original: {account_number_raw}) - {name_in_excel}")

        # Buscar el estudiante en la BD
        try:
            student_profile = UserProfile.objects.get(
                account_number=account_number,
                user_type='student'
            )

            # Verificar si el nombre coincide
            if student_profile.full_name != name_in_excel:
                print(f"    ⚠ Nombre diferente en BD: '{student_profile.full_name}'")
            else:
                print(f"    ✓ Estudiante encontrado: {student_profile.full_name}")

            # Verificar si ya existe el registro de asistencia
            existing = Attendance.objects.filter(
                student=student_profile,
                event=event
            ).first()

            if existing:
                print(f"    ⊘ Ya existe registro de asistencia - OMITIDO")
                skipped_count += 1
                continue

            # Crear el registro de asistencia con skip_validation
            attendance = Attendance(
                student=student_profile,
                event=event,
                timestamp=timezone.now(),
                registered_by=assistant_profile,
                registration_method='manual',
                notes=f'Importado desde Excel: {os.path.basename(excel_file)}',
                is_valid=True
            )
            # Guardar omitiendo validaciones de tiempo
            attendance.save(skip_validation=True)

            print(f"    ✓ Asistencia creada (ID: {attendance.id})")
            created_count += 1
            updated_students.append(student_profile)

        except UserProfile.DoesNotExist:
            print(f"    ✗ ERROR: Estudiante no encontrado en BD - {account_number}")
            error_count += 1
        except Exception as e:
            print(f"    ✗ ERROR: {str(e)}")
            error_count += 1

    print()

    # 5. Actualizar estadísticas
    print(f"[5/5] Actualizando estadísticas de asistencia...")
    print()

    for student_profile in set(updated_students):  # Eliminar duplicados
        try:
            # Obtener o crear las estadísticas del estudiante
            stats, created = AttendanceStats.objects.get_or_create(
                student=student_profile
            )

            # Calcular estadísticas
            total_events = Event.objects.filter(is_active=True).count()
            attended = Attendance.objects.filter(
                student=student_profile,
                is_valid=True
            ).values('event').distinct().count()

            percentage = (attended / total_events * 100) if total_events > 0 else 0

            # Actualizar
            stats.total_events = total_events
            stats.attended_events = attended
            stats.attendance_percentage = round(percentage, 2)
            stats.last_updated = timezone.now()
            stats.save()

            print(f"  ✓ {student_profile.full_name}: {attended}/{total_events} eventos ({percentage:.2f}%)")

        except Exception as e:
            print(f"  ✗ Error al actualizar {student_profile.full_name}: {e}")

    print()
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"  Asistencias creadas:  {created_count}")
    print(f"  Registros omitidos:   {skipped_count} (ya existían)")
    print(f"  Errores:              {error_count}")
    print(f"  Total procesados:     {len(df)}")
    print()
    print("✓ Proceso completado")
    print("=" * 80)


if __name__ == "__main__":
    # Parámetros
    EXCEL_FILE = "/app/Asistencias_Procesadas.xlsx"
    EVENT_TITLE = "Tecnologías IIoT al servicio de la Industria"
    ASSISTANT_USERNAME = "asst_11111111"  # El único asistente que hay

    process_attendance_file(EXCEL_FILE, EVENT_TITLE, ASSISTANT_USERNAME)
