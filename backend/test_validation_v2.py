#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar que la validación de eventos simultáneos funciona correctamente.
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
from django.utils import timezone
from django.core.exceptions import ValidationError

def test_validation():
    """Probar validación de eventos simultáneos"""
    print("=" * 80)
    print("PROBANDO VALIDACIÓN DE EVENTOS SIMULTÁNEOS")
    print("=" * 80)
    print()

    # Buscar estudiante que tenga asistencia en la conferencia de Matemáticas
    event_math = Event.objects.get(id=48)
    attendance_math = Attendance.objects.filter(event=event_math).first()

    if not attendance_math:
        print("✗ No se encontró ninguna asistencia en la conferencia de Matemáticas")
        return

    student = attendance_math.student
    assistant = UserProfile.objects.filter(user_type='assistant').first()

    # Buscar eventos simultáneos
    event_iiot = Event.objects.get(id=46)

    print(f"Estudiante de prueba: {student.account_number} - {student.full_name}")
    print()
    print(f"Evento donde YA tiene asistencia: {event_math.title}")
    print(f"  Horario: {event_math.start_time} - {event_math.end_time}")
    print(f"  ID de asistencia existente: {attendance_math.id}")
    print()
    print(f"Evento simultáneo (intentaremos crear asistencia aquí): {event_iiot.title}")
    print(f"  Horario: {event_iiot.start_time} - {event_iiot.end_time}")
    print()
    print("-" * 80)
    print()

    # Verificar si los eventos son simultáneos
    if event_math.date == event_iiot.date:
        if event_math.start_time < event_iiot.end_time and event_math.end_time > event_iiot.start_time:
            print("✓ Los eventos son simultáneos")
        else:
            print("⚠ Los eventos NO son simultáneos")
            print(f"  Evento 1: {event_math.start_time} - {event_math.end_time}")
            print(f"  Evento 2: {event_iiot.start_time} - {event_iiot.end_time}")
    else:
        print("⚠ Los eventos son en fechas diferentes")

    print()

    # Verificar si ya tiene asistencia en el otro evento
    existing_att = Attendance.objects.filter(student=student, event=event_iiot).first()
    if existing_att:
        print(f"⚠ El estudiante YA tiene asistencia en {event_iiot.title}")
        print(f"  No se puede probar con este estudiante")
        return

    # Intentar crear asistencia en evento simultáneo CON skip_validation=True
    print("TEST 1: Intentando crear asistencia con skip_validation=True...")
    try:
        new_attendance = Attendance(
            student=student,
            event=event_iiot,
            timestamp=timezone.now(),
            registered_by=assistant,
            registration_method='manual',
            notes='Prueba de validación',
            is_valid=True
        )
        new_attendance.save(skip_validation=True)
        print("✗ ERROR: Se permitió crear asistencia simultánea")
        print("  LA VALIDACIÓN FALLÓ - skip_validation no está validando eventos simultáneos")
        # Eliminar la asistencia creada
        new_attendance.delete()
    except ValidationError as e:
        print(f"✓ CORRECTO: Se bloqueó la asistencia simultánea incluso con skip_validation=True")
        print(f"  Mensaje: {e}")

    print()

    # Intentar crear asistencia en evento simultáneo SIN skip_validation
    print("TEST 2: Intentando crear asistencia con skip_validation=False (validación completa)...")
    try:
        new_attendance = Attendance(
            student=student,
            event=event_iiot,
            timestamp=timezone.now(),
            registered_by=assistant,
            registration_method='manual',
            notes='Prueba de validación',
            is_valid=True
        )
        new_attendance.save(skip_validation=False)
        print("✗ ERROR: Se permitió crear asistencia simultánea")
        print("  LA VALIDACIÓN FALLÓ - No está validando eventos simultáneos")
        # Eliminar la asistencia creada
        new_attendance.delete()
    except ValidationError as e:
        print(f"✓ CORRECTO: Se bloqueó la asistencia simultánea")
        print(f"  Mensaje: {e}")

    print()
    print("=" * 80)
    print("✓ Prueba completada")
    print("=" * 80)

if __name__ == "__main__":
    test_validation()
