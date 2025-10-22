#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para encontrar estudiantes con asistencias en conferencias simultáneas.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from attendance.models import Attendance
from events.models import Event
from authentication.models import UserProfile

def find_duplicate_attendances():
    """Encontrar estudiantes con asistencias en eventos simultáneos"""
    print("=" * 80)
    print("BUSCANDO ASISTENCIAS EN CONFERENCIAS SIMULTÁNEAS")
    print("=" * 80)
    print()

    # Obtener todos los eventos activos
    all_events = Event.objects.filter(is_active=True).order_by('date', 'start_time')

    conflicts = []

    # Revisar cada estudiante que tenga asistencias
    students_with_attendance = UserProfile.objects.filter(
        user_type='student',
        attendance__isnull=False
    ).distinct()

    print(f"Revisando {students_with_attendance.count()} estudiantes con asistencias...")
    print()

    for student in students_with_attendance:
        # Obtener todas las asistencias del estudiante
        student_attendances = Attendance.objects.filter(
            student=student,
            is_valid=True
        ).select_related('event')

        # Comparar cada par de asistencias
        attendances_list = list(student_attendances)
        for i in range(len(attendances_list)):
            for j in range(i + 1, len(attendances_list)):
                event1 = attendances_list[i].event
                event2 = attendances_list[j].event

                # Verificar si son en la misma fecha y horarios se solapan
                if event1.date == event2.date:
                    # Hay solapamiento si el inicio de uno es menor al fin del otro
                    if (event1.start_time < event2.end_time and event1.end_time > event2.start_time):
                        conflicts.append({
                            'student': student,
                            'attendance1': attendances_list[i],
                            'attendance2': attendances_list[j],
                            'event1': event1,
                            'event2': event2
                        })

    print(f"✓ Búsqueda completada")
    print()
    print("-" * 80)
    print()

    if conflicts:
        print(f"⚠ SE ENCONTRARON {len(conflicts)} CONFLICTOS:")
        print()

        for idx, conflict in enumerate(conflicts, 1):
            student = conflict['student']
            event1 = conflict['event1']
            event2 = conflict['event2']
            att1 = conflict['attendance1']
            att2 = conflict['attendance2']

            print(f"[CONFLICTO {idx}]")
            print(f"  Estudiante: {student.account_number} - {student.full_name}")
            print(f"  Fecha: {event1.date}")
            print()
            print(f"  Evento 1 (ID: {att1.id}):")
            print(f"    - {event1.title}")
            print(f"    - Horario: {event1.start_time} - {event1.end_time}")
            print()
            print(f"  Evento 2 (ID: {att2.id}):")
            print(f"    - {event2.title}")
            print(f"    - Horario: {event2.start_time} - {event2.end_time}")
            print()
            print("-" * 80)
            print()
    else:
        print("✓ No se encontraron conflictos de asistencias simultáneas")
        print()

    # También buscar la conferencia específica a eliminar
    print("=" * 80)
    print("BUSCANDO CONFERENCIA: 'La presión fiscal como oportunidad en el entorno profesional'")
    print("=" * 80)
    print()

    try:
        fiscal_event = Event.objects.get(title="La presión fiscal como oportunidad en el entorno profesional")
        fiscal_attendances = Attendance.objects.filter(event=fiscal_event)

        print(f"✓ Evento encontrado (ID: {fiscal_event.id})")
        print(f"  Fecha: {fiscal_event.date}")
        print(f"  Horario: {fiscal_event.start_time} - {fiscal_event.end_time}")
        print(f"  Total de asistencias: {fiscal_attendances.count()}")
        print()

        if fiscal_attendances.exists():
            print("  Estudiantes con asistencia a esta conferencia:")
            for att in fiscal_attendances:
                print(f"    - {att.student.account_number}: {att.student.full_name} (Asistencia ID: {att.id})")
            print()
    except Event.DoesNotExist:
        print("✗ No se encontró el evento")
        print()

    print("=" * 80)
    print("✓ Análisis completado")
    print("=" * 80)

    return conflicts

if __name__ == "__main__":
    find_duplicate_attendances()
