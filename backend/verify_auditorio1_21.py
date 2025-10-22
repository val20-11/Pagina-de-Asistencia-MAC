#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el procesamiento del auditorio1_21.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings')
django.setup()

from attendance.models import Attendance, AttendanceStats
from events.models import Event
from authentication.models import UserProfile

def verify_processing():
    """Verificar procesamiento de auditorio1_21"""
    print("=" * 80)
    print("VERIFICACIÓN - PROCESAMIENTO AUDITORIO1_21")
    print("=" * 80)
    print()

    # Evento procesado
    event = Event.objects.get(id=45)

    print(f"Conferencia: {event.title}")
    print(f"Fecha: {event.date}")
    print(f"Horario: {event.start_time} - {event.end_time}")
    print()

    # Contar asistencias
    total_attendances = Attendance.objects.filter(event=event).count()
    print(f"Total de asistencias registradas: {total_attendances}")
    print()

    # Resumen general
    print("=" * 80)
    print("RESUMEN GENERAL DEL SISTEMA")
    print("=" * 80)
    print()

    # Todas las conferencias procesadas hasta ahora
    conferences = [
        ("Tecnologías IIoT al servicio de la Industria", 46),
        ("Matemáticas Aplicadas y Computación: Una fábrica mexicana de conocimiento y soluciones", 48),
        ("Matemáticas Aplicadas a Medicina a través del Procesamiento Digital de Imágenes", 45),
    ]

    total_system = 0
    for title, event_id in conferences:
        count = Attendance.objects.filter(event_id=event_id).count()
        total_system += count
        print(f"[Evento {event_id}] {count} asistencias")
        print(f"  {title}")
        print()

    print(f"TOTAL DE ASISTENCIAS EN EL SISTEMA: {Attendance.objects.count()}")
    print(f"TOTAL DE ESTUDIANTES CON ASISTENCIAS: {UserProfile.objects.filter(user_type='student', attendance__isnull=False).distinct().count()}")
    print()

    # Top estudiantes
    print("=" * 80)
    print("TOP 10 ESTUDIANTES CON MÁS ASISTENCIAS")
    print("=" * 80)
    top_students = AttendanceStats.objects.all().order_by('-attended_events', '-attendance_percentage')[:10]
    for i, stat in enumerate(top_students, 1):
        print(f"{i}. {stat.student.full_name}")
        print(f"   {stat.attended_events}/{stat.total_events} eventos ({stat.attendance_percentage}%)")
        print()

    print("=" * 80)
    print("✓ Verificación completada")
    print("=" * 80)

if __name__ == "__main__":
    verify_processing()
