#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para procesar asistencias desde Registros_Asistencia.xlsx
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from authentication.models import UserProfile, Asistente
from events.models import Event
from attendance.models import Attendance, AttendanceStats
from django.utils import timezone
from django.core.exceptions import ValidationError

def process_registros():
    """Procesar registros de asistencia"""
    print("=" * 80)
    print("PROCESANDO REGISTROS_ASISTENCIA.XLSX")
    print("=" * 80)
    print()

    # Leer archivo
    df = pd.read_excel("/app/Registros_Asistencia.xlsx", sheet_name='Registros')

    print(f"Total de registros: {len(df)}")
    print(f"Columnas: {list(df.columns)}")
    print()

    # Obtener el asistente
    assistant_profile = UserProfile.objects.get(account_number='11111111', user_type='assistant')
    print(f"Asistente: {assistant_profile.full_name}")
    print()

    # Verificar/crear permisos de asistente
    asistente, created = Asistente.objects.get_or_create(
        user_profile=assistant_profile,
        defaults={'can_manage_events': True}
    )
    if created:
        print(f"✓ Permisos de asistente creados para {assistant_profile.full_name}")
    else:
        print(f"✓ Permisos de asistente ya existen para {assistant_profile.full_name}")
    print()

    # Procesar cada registro
    print("Procesando asistencias...")
    print()

    created_count = 0
    skipped_count = 0
    error_count = 0
    updated_students = set()

    for idx, row in df.iterrows():
        attendee_id = str(row['Attendee identifier']).strip()
        attendee_name = str(row['Attendee name']).strip()
        event_title = str(row['Evento']).strip()
        timestamp = row['Hora de registro']

        # Normalizar número de cuenta
        account_number = attendee_id.replace(' ', '').replace('-', '')[:8]

        print(f"[{idx+1}/{len(df)}] {account_number} - {attendee_name}")
        print(f"  Evento: {event_title}")

        # Buscar el evento
        try:
            event = Event.objects.get(title=event_title)
            print(f"  ✓ Evento encontrado (ID: {event.id})")
        except Event.DoesNotExist:
            print(f"  ✗ ERROR: Evento no encontrado - {event_title}")
            error_count += 1
            print()
            continue

        # Buscar el estudiante
        try:
            student_profile = UserProfile.objects.get(
                account_number=account_number,
                user_type='student'
            )

            if student_profile.full_name != attendee_name:
                print(f"  ⚠ Nombre diferente en BD: '{student_profile.full_name}'")
            else:
                print(f"  ✓ Estudiante encontrado")

        except UserProfile.DoesNotExist:
            print(f"  ✗ ERROR: Estudiante no encontrado en BD")
            error_count += 1
            print()
            continue

        # Verificar si ya existe
        existing = Attendance.objects.filter(
            student=student_profile,
            event=event
        ).first()

        if existing:
            print(f"  ⊘ Ya existe registro de asistencia - OMITIDO")
            skipped_count += 1
        else:
            # Crear asistencia
            try:
                # Convertir timestamp si es necesario
                if isinstance(timestamp, str):
                    # Intentar parsear
                    try:
                        timestamp_dt = datetime.strptime(timestamp, '%d/%m/%Y %H:%M')
                        timestamp_dt = timezone.make_aware(timestamp_dt)
                    except:
                        timestamp_dt = timezone.now()
                else:
                    timestamp_dt = timezone.now()

                attendance = Attendance(
                    student=student_profile,
                    event=event,
                    timestamp=timestamp_dt,
                    registered_by=assistant_profile,
                    registration_method='manual',
                    notes='Importado desde Registros_Asistencia.xlsx',
                    is_valid=True
                )
                attendance.save(skip_validation=True)

                print(f"  ✓ Asistencia creada (ID: {attendance.id})")
                created_count += 1
                updated_students.add(student_profile)

            except ValidationError as e:
                print(f"  ✗ ERROR: {e}")
                error_count += 1
            except Exception as e:
                print(f"  ✗ ERROR inesperado: {e}")
                error_count += 1

        print()

    # Actualizar estadísticas
    print("=" * 80)
    print("ACTUALIZANDO ESTADÍSTICAS")
    print("=" * 80)
    print()

    for student_profile in updated_students:
        try:
            stats, created = AttendanceStats.objects.get_or_create(
                student=student_profile
            )
            stats.update_stats()
            print(f"✓ {student_profile.full_name}: {stats.attended_events}/{stats.total_events} ({stats.attendance_percentage}%)")
        except Exception as e:
            print(f"✗ Error al actualizar {student_profile.full_name}: {e}")

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
    process_registros()
