#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para eliminar asistencias a la conferencia fiscal y actualizar estadísticas.
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

def delete_fiscal_attendances():
    """Eliminar asistencias a la conferencia fiscal"""
    print("=" * 80)
    print("ELIMINANDO ASISTENCIAS A CONFERENCIA FISCAL")
    print("=" * 80)
    print()

    # Buscar el evento
    try:
        fiscal_event = Event.objects.get(title="La presión fiscal como oportunidad en el entorno profesional")
        print(f"✓ Evento encontrado: {fiscal_event.title}")
        print(f"  ID: {fiscal_event.id}")
        print(f"  Fecha: {fiscal_event.date}")
        print(f"  Horario: {fiscal_event.start_time} - {fiscal_event.end_time}")
        print()

        # Obtener todas las asistencias
        fiscal_attendances = Attendance.objects.filter(event=fiscal_event)
        total_attendances = fiscal_attendances.count()

        print(f"Total de asistencias a eliminar: {total_attendances}")
        print()

        if total_attendances > 0:
            # Guardar los estudiantes afectados para actualizar sus estadísticas
            affected_students = set()

            print("Eliminando asistencias:")
            for att in fiscal_attendances:
                student = att.student
                affected_students.add(student)
                print(f"  - {student.account_number}: {student.full_name} (ID: {att.id})")
                att.delete()

            print()
            print(f"✓ {total_attendances} asistencias eliminadas")
            print()

            # Actualizar estadísticas de los estudiantes afectados
            print("Actualizando estadísticas de estudiantes afectados...")
            print()

            for student in affected_students:
                try:
                    stats = AttendanceStats.objects.get(student=student)
                    old_attended = stats.attended_events
                    old_percentage = stats.attendance_percentage

                    stats.update_stats()

                    print(f"  ✓ {student.full_name}")
                    print(f"    Antes: {old_attended}/{stats.total_events} ({old_percentage}%)")
                    print(f"    Ahora: {stats.attended_events}/{stats.total_events} ({stats.attendance_percentage}%)")
                except AttendanceStats.DoesNotExist:
                    print(f"  ⚠ {student.full_name} - No tiene estadísticas")

            print()
            print(f"✓ Estadísticas actualizadas para {len(affected_students)} estudiantes")
        else:
            print("✓ No hay asistencias que eliminar")

    except Event.DoesNotExist:
        print("✗ No se encontró el evento 'La presión fiscal como oportunidad en el entorno profesional'")
        return

    print()
    print("=" * 80)
    print("✓ Proceso completado")
    print("=" * 80)

if __name__ == "__main__":
    delete_fiscal_attendances()
