#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar estudiantes faltantes y registrar sus asistencias.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from authentication.models import UserProfile
from events.models import Event
from attendance.models import Attendance, AttendanceStats
from django.utils import timezone

def add_missing_students_and_attendance():
    """Agregar estudiantes faltantes y sus asistencias"""
    print("=" * 80)
    print("AGREGANDO ESTUDIANTES FALTANTES Y SUS ASISTENCIAS")
    print("=" * 80)
    print()

    # Obtener los eventos
    event_iiot = Event.objects.get(id=46)  # Conferencia IIoT
    event_math = Event.objects.get(id=48)  # Conferencia Matemáticas

    # Obtener el asistente
    assistant_profile = UserProfile.objects.get(account_number='11111111', user_type='assistant')

    print(f"Evento 1: {event_iiot.title}")
    print(f"Evento 2: {event_math.title}")
    print(f"Asistente: {assistant_profile.full_name}")
    print()
    print("-" * 80)
    print()

    # Lista de estudiantes a agregar con sus asistencias
    students_to_add = [
        {
            'account_number': '32030968',
            'full_name': 'Coria Zambrano Ana Fernanda',  # Normalizado: apellidos primero
            'events': [event_iiot]  # Solo asistió a la conferencia IIoT
        },
        {
            'account_number': '34220729',
            'full_name': 'Montoya Santiago Francisco',
            'events': [event_iiot]  # Solo asistió a la conferencia IIoT
        },
        {
            'account_number': '32119639',
            'full_name': 'Roca Nava Laura Elena',
            'events': [event_iiot, event_math]  # Asistió a AMBAS conferencias
        }
    ]

    created_students = 0
    created_attendances = 0

    for student_data in students_to_add:
        account_number = student_data['account_number']
        full_name = student_data['full_name']
        events = student_data['events']

        print(f"[{account_number}] {full_name}")

        # Verificar si ya existe
        existing = UserProfile.objects.filter(
            account_number=account_number,
            user_type='student'
        ).first()

        if existing:
            print(f"  ⚠ Ya existe en BD: {existing.full_name}")
            student_profile = existing
        else:
            # Crear el estudiante
            student_profile = UserProfile.objects.create(
                account_number=account_number,
                user_type='student',
                full_name=full_name
            )
            print(f"  ✓ Estudiante creado en BD")
            created_students += 1

        # Registrar asistencias
        for event in events:
            # Verificar si ya existe la asistencia
            existing_attendance = Attendance.objects.filter(
                student=student_profile,
                event=event
            ).first()

            if existing_attendance:
                print(f"    ⊘ Ya existe asistencia para: {event.title}")
            else:
                # Crear asistencia
                attendance = Attendance(
                    student=student_profile,
                    event=event,
                    timestamp=timezone.now(),
                    registered_by=assistant_profile,
                    registration_method='manual',
                    notes='Importado desde Excel - Agregado posteriormente',
                    is_valid=True
                )
                # Guardar omitiendo validaciones de tiempo
                attendance.save(skip_validation=True)
                print(f"    ✓ Asistencia registrada para: {event.title} (ID: {attendance.id})")
                created_attendances += 1

        # Actualizar estadísticas
        stats, created = AttendanceStats.objects.get_or_create(
            student=student_profile
        )
        stats.update_stats()
        print(f"    ✓ Estadísticas actualizadas: {stats.attended_events}/{stats.total_events} ({stats.attendance_percentage}%)")
        print()

    print("-" * 80)
    print()
    print("=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"  Estudiantes creados:       {created_students}")
    print(f"  Asistencias registradas:   {created_attendances}")
    print()
    print("✓ Proceso completado")
    print("=" * 80)

if __name__ == "__main__":
    add_missing_students_and_attendance()
