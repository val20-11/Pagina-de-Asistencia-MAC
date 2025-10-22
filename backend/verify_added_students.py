#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar que los estudiantes agregados están correctamente registrados.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from authentication.models import UserProfile
from attendance.models import Attendance, AttendanceStats
from events.models import Event

def verify_added_students():
    """Verificar los estudiantes recién agregados"""
    print("=" * 80)
    print("VERIFICACIÓN DE ESTUDIANTES AGREGADOS")
    print("=" * 80)
    print()

    # IDs de los estudiantes agregados
    student_accounts = ['32030968', '34220729', '32119639']

    event_iiot = Event.objects.get(id=46)
    event_math = Event.objects.get(id=48)

    for account in student_accounts:
        print(f"[{account}]")

        # Buscar el estudiante
        try:
            student = UserProfile.objects.get(account_number=account, user_type='student')
            print(f"  ✓ Estudiante en BD: {student.full_name}")

            # Verificar asistencias
            attendances = Attendance.objects.filter(student=student)
            print(f"  ✓ Total asistencias: {attendances.count()}")

            for att in attendances:
                print(f"    - {att.event.title}")
                print(f"      Fecha: {att.timestamp}")
                print(f"      Registrado por: {att.registered_by.full_name}")

            # Verificar estadísticas
            try:
                stats = AttendanceStats.objects.get(student=student)
                print(f"  ✓ Estadísticas: {stats.attended_events}/{stats.total_events} ({stats.attendance_percentage}%)")
            except AttendanceStats.DoesNotExist:
                print(f"  ⚠ No tiene estadísticas aún")

        except UserProfile.DoesNotExist:
            print(f"  ✗ ERROR: No se encontró el estudiante")

        print()

    print("-" * 80)
    print()

    # Resumen final de TODAS las asistencias
    print("=== RESUMEN FINAL DE ASISTENCIAS ===")
    print(f"Conferencia IIoT: {Attendance.objects.filter(event=event_iiot).count()} asistencias")
    print(f"Conferencia Matemáticas: {Attendance.objects.filter(event=event_math).count()} asistencias")
    print(f"Total en el sistema: {Attendance.objects.count()} asistencias")
    print()

    print("=" * 80)
    print("✓ Verificación completada")
    print("=" * 80)

if __name__ == "__main__":
    verify_added_students()
