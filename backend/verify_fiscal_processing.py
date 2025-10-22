#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el procesamiento de asistencias fiscales.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from attendance.models import Attendance, AttendanceStats
from events.models import Event

def verify_fiscal():
    """Verificar procesamiento de evento fiscal"""
    print("=" * 80)
    print("VERIFICACIÓN - PROCESAMIENTO EVENTO FISCAL")
    print("=" * 80)
    print()

    # Evento
    event = Event.objects.get(id=47)
    print(f"Conferencia: {event.title}")
    print(f"Fecha: {event.date}")
    print(f"Horario: {event.start_time} - {event.end_time}")
    print()

    # Total de asistencias
    total = Attendance.objects.filter(event=event).count()
    print(f"✓ Total de asistencias registradas: {total}")
    print()

    # Verificar que no hay conflictos
    print("Verificando conflictos con eventos simultáneos...")
    event_math = Event.objects.get(id=48)

    students_fiscal = set(Attendance.objects.filter(event=event).values_list('student_id', flat=True))
    students_math = set(Attendance.objects.filter(event=event_math).values_list('student_id', flat=True))

    conflicts = students_fiscal.intersection(students_math)

    if conflicts:
        print(f"⚠ ADVERTENCIA: {len(conflicts)} estudiantes con asistencia en ambos eventos")
        print("  Esto NO debería ocurrir por la validación de eventos simultáneos")
    else:
        print(f"✓ No hay conflictos: 0 estudiantes con asistencia en ambos eventos")
    print()

    # Resumen general
    print("=" * 80)
    print("RESUMEN GENERAL DEL SISTEMA")
    print("=" * 80)
    print()

    conferences = [
        ("Tecnologías IIoT", 46),
        ("Matemáticas Aplicadas a Medicina", 45),
        ("Matemáticas Aplicadas y Computación", 48),
        ("La presión fiscal", 47),
    ]

    total_system = 0
    for title, event_id in conferences:
        count = Attendance.objects.filter(event_id=event_id).count()
        total_system += count
        print(f"[Evento {event_id}] {count:3d} asistencias - {title}")

    print()
    print(f"TOTAL DE ASISTENCIAS EN EL SISTEMA: {Attendance.objects.count()}")
    print()

    print("=" * 80)
    print("✓ Verificación completada")
    print("=" * 80)

if __name__ == "__main__":
    verify_fiscal()
