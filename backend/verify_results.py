#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar los resultados del procesamiento de asistencias.
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

def verify_results():
    """Verificar los resultados del procesamiento"""
    print("=" * 80)
    print("VERIFICACIÓN DE RESULTADOS")
    print("=" * 80)
    print()

    # 1. Verificar evento
    event = Event.objects.get(id=46)
    print(f"=== EVENTO: {event.title} ===")
    print(f"Fecha: {event.date}")
    print(f"Total asistencias registradas: {Attendance.objects.filter(event=event).count()}")
    print()

    # 2. Asistencias por asistente
    print("Asistencias por asistente:")
    attendances_by_assistant = Attendance.objects.filter(event=event).values(
        'registered_by__full_name'
    ).annotate(count=Count('id'))

    for a in attendances_by_assistant:
        print(f"  - {a['registered_by__full_name']}: {a['count']} asistencias")
    print()

    # 3. Permisos de asistentes
    print("=== PERMISOS DE ASISTENTES ===")
    print(f"Total asistentes con permisos: {Asistente.objects.count()}")
    for asst in Asistente.objects.all():
        print(f"  - {asst.user_profile.full_name} ({asst.user_profile.account_number})")
    print()

    # 4. Estadísticas de algunos estudiantes
    print("=== ESTADÍSTICAS DE ASISTENCIA (Muestra) ===")
    stats_sample = AttendanceStats.objects.all().order_by('-attended_events')[:10]
    for stat in stats_sample:
        print(f"  {stat.student.full_name}: {stat.attended_events}/{stat.total_events} ({stat.attendance_percentage}%)")
    print()

    # 5. Estudiantes que asistieron a esta conferencia
    print("=== ESTUDIANTES QUE ASISTIERON A LA CONFERENCIA ===")
    attendees = Attendance.objects.filter(event=event).select_related('student')
    print(f"Total: {attendees.count()}")
    for att in attendees:
        print(f"  - {att.student.account_number}: {att.student.full_name}")
    print()

    print("=" * 80)
    print("✓ Verificación completada")
    print("=" * 80)

if __name__ == "__main__":
    verify_results()
