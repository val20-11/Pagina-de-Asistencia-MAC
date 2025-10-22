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

    # Obtener un estudiante de prueba
    student = UserProfile.objects.filter(user_type='student').first()
    assistant = UserProfile.objects.filter(user_type='assistant').first()

    # Buscar dos eventos que sean simultáneos
    event_iiot = Event.objects.get(id=46)  # 12:00-13:00
    event_math = Event.objects.get(id=48)  # 12:00-13:00

    print(f"Estudiante de prueba: {student.account_number} - {student.full_name}")
    print()
    print(f"Evento 1: {event_iiot.title}")
    print(f"  Horario: {event_iiot.start_time} - {event_iiot.end_time}")
    print()
    print(f"Evento 2: {event_math.title}")
    print(f"  Horario: {event_math.start_time} - {event_math.end_time}")
    print()
    print("-" * 80)
    print()

    # Verificar si el estudiante ya tiene asistencia en alguno
    att1 = Attendance.objects.filter(student=student, event=event_iiot).first()
    att2 = Attendance.objects.filter(student=student, event=event_math).first()

    if att1:
        print(f"✓ El estudiante ya tiene asistencia en: {event_iiot.title}")
        print(f"  ID de asistencia: {att1.id}")
        print()

        # Intentar crear asistencia en evento simultáneo
        print("Intentando crear asistencia en evento simultáneo...")
        try:
            new_attendance = Attendance(
                student=student,
                event=event_math,
                timestamp=timezone.now(),
                registered_by=assistant,
                registration_method='manual',
                notes='Prueba de validación',
                is_valid=True
            )
            new_attendance.save(skip_validation=True)  # Usar skip_validation para probar
            print("✗ ERROR: Se permitió crear asistencia simultánea (LA VALIDACIÓN FALLÓ)")
        except ValidationError as e:
            print(f"✓ CORRECTO: Se bloqueó la asistencia simultánea")
            print(f"  Mensaje: {e}")
    elif att2:
        print(f"✓ El estudiante ya tiene asistencia en: {event_math.title}")
        print(f"  ID de asistencia: {att2.id}")
        print()

        # Intentar crear asistencia en evento simultáneo
        print("Intentando crear asistencia en evento simultáneo...")
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
            print("✗ ERROR: Se permitió crear asistencia simultánea (LA VALIDACIÓN FALLÓ)")
        except ValidationError as e:
            print(f"✓ CORRECTO: Se bloqueó la asistencia simultánea")
            print(f"  Mensaje: {e}")
    else:
        print("⚠ El estudiante no tiene asistencia en ninguno de estos eventos")
        print("  No se puede probar la validación con este estudiante")

    print()
    print("=" * 80)
    print("✓ Prueba completada")
    print("=" * 80)

if __name__ == "__main__":
    test_validation()
