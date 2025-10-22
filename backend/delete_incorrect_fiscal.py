#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para eliminar las asistencias incorrectas del evento fiscal que agregué.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from attendance.models import Attendance, AttendanceStats
from events.models import Event

def delete_incorrect_fiscal():
    """Eliminar asistencias incorrectas del evento fiscal"""
    print("=" * 80)
    print("ELIMINANDO ASISTENCIAS INCORRECTAS DEL EVENTO FISCAL")
    print("=" * 80)
    print()

    # Evento fiscal
    event_fiscal = Event.objects.get(id=47)

    print(f"Evento: {event_fiscal.title}")
    print(f"Asistencias actuales: {Attendance.objects.filter(event=event_fiscal).count()}")
    print()

    # Obtener estudiantes afectados antes de eliminar
    affected_students = set()
    attendances = Attendance.objects.filter(event=event_fiscal)

    for att in attendances:
        affected_students.add(att.student)

    print(f"Eliminando {attendances.count()} asistencias...")
    attendances.delete()

    print(f"✓ Asistencias eliminadas")
    print()

    # Actualizar estadísticas
    print(f"Actualizando estadísticas de {len(affected_students)} estudiantes...")
    for student in affected_students:
        try:
            stats = AttendanceStats.objects.get(student=student)
            stats.update_stats()
        except AttendanceStats.DoesNotExist:
            pass

    print(f"✓ Estadísticas actualizadas")
    print()

    print(f"Asistencias restantes en evento fiscal: {Attendance.objects.filter(event=event_fiscal).count()}")
    print()

    print("=" * 80)
    print("✓ Proceso completado")
    print("=" * 80)

if __name__ == "__main__":
    delete_incorrect_fiscal()
