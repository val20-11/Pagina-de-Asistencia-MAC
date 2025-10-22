#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar los resultados finales de ambas conferencias.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from django.db.models import Count
from attendance.models import Attendance, AttendanceStats
from events.models import Event
from authentication.models import Asistente, UserProfile

def verify_final_results():
    """Verificar los resultados finales"""
    print("=" * 80)
    print("VERIFICACIÓN FINAL DE RESULTADOS")
    print("=" * 80)
    print()

    # Eventos procesados
    event1 = Event.objects.get(id=46)
    event2 = Event.objects.get(id=48)

    print("=== CONFERENCIA 1 ===")
    print(f"Título: {event1.title}")
    print(f"Fecha: {event1.date}")
    print(f"Total asistencias: {Attendance.objects.filter(event=event1).count()}")
    print()

    print("=== CONFERENCIA 2 ===")
    print(f"Título: {event2.title}")
    print(f"Fecha: {event2.date}")
    print(f"Total asistencias: {Attendance.objects.filter(event=event2).count()}")
    print()

    # Total de asistencias registradas
    print("=== RESUMEN GLOBAL ===")
    total_attendances = Attendance.objects.count()
    print(f"Total de asistencias en el sistema: {total_attendances}")
    print(f"Asistencias registradas hoy: {Attendance.objects.filter(event__in=[event1, event2]).count()}")
    print()

    # Asistencias por asistente
    print("=== ASISTENCIAS POR ASISTENTE ===")
    attendances_by_assistant = Attendance.objects.all().values(
        'registered_by__full_name'
    ).annotate(count=Count('id')).order_by('-count')

    for a in attendances_by_assistant:
        print(f"  {a['registered_by__full_name']}: {a['count']} asistencias")
    print()

    # Permisos de asistentes
    print("=== PERMISOS DE ASISTENTES ===")
    print(f"Total asistentes con permisos: {Asistente.objects.count()}")
    for asst in Asistente.objects.all():
        print(f"  - {asst.user_profile.full_name} ({asst.user_profile.account_number})")
        print(f"    Puede gestionar eventos: {asst.can_manage_events}")
    print()

    # Top 10 estudiantes con más asistencias
    print("=== TOP 10 ESTUDIANTES CON MÁS ASISTENCIAS ===")
    top_students = AttendanceStats.objects.all().order_by('-attended_events', '-attendance_percentage')[:10]
    for i, stat in enumerate(top_students, 1):
        print(f"  {i}. {stat.student.full_name}")
        print(f"     {stat.attended_events}/{stat.total_events} eventos ({stat.attendance_percentage}%)")
    print()

    # Estudiantes que asistieron a ambas conferencias
    print("=== ESTUDIANTES QUE ASISTIERON A AMBAS CONFERENCIAS ===")
    students_event1 = set(Attendance.objects.filter(event=event1).values_list('student_id', flat=True))
    students_event2 = set(Attendance.objects.filter(event=event2).values_list('student_id', flat=True))
    both_events = students_event1.intersection(students_event2)

    print(f"Total estudiantes en ambas: {len(both_events)}")
    for student_id in both_events:
        student = UserProfile.objects.get(id=student_id)
        print(f"  - {student.account_number}: {student.full_name}")
    print()

    print("=" * 80)
    print("✓ Verificación final completada")
    print("=" * 80)

if __name__ == "__main__":
    verify_final_results()
