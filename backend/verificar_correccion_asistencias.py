#!/usr/bin/env python
"""
Script para verificar las correcciones de asistencia aplicadas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings.local')
django.setup()

from attendance.models import Attendance, AttendanceStats
from events.models import Event
from authentication.models import UserProfile

# Números de cuenta a verificar
ESTUDIANTES = [
    '42307052',
    '42306223',
    '32326922',
    '31904405',
    '42212521',
    '42110637'
]

# Días específicos para 42307052
DIAS_ESPECIFICOS = [20, 22, 24]

print("=" * 80)
print("VERIFICACIÓN DE CORRECCIONES DE ASISTENCIA")
print("=" * 80)

# Verificar que el estudiante 42307052 tenga asistencias en los días 20, 22, 24
print("\n1. Verificando asistencias del estudiante 42307052 en días específicos...")
print("-" * 80)

try:
    estudiante = UserProfile.objects.get(account_number='42307052')
    print(f"✓ Estudiante: {estudiante.full_name}")

    for dia in DIAS_ESPECIFICOS:
        eventos_dia = Event.objects.filter(
            is_active=True,
            date__day=dia
        ).order_by('start_time')

        if eventos_dia.exists():
            print(f"\n  Día {dia}:")
            for evento in eventos_dia:
                asistencia = Attendance.objects.filter(
                    student=estudiante,
                    event=evento,
                    is_valid=True
                ).exists()

                estado = "✓ SÍ" if asistencia else "✗ NO"
                print(f"    {estado} - {evento.title} ({evento.date} {evento.start_time})")
        else:
            print(f"\n  Día {dia}: No hay eventos en este día")

except UserProfile.DoesNotExist:
    print(f"❌ No se encontró el estudiante con cuenta 42307052")

# Verificar que todos los estudiantes cumplan con el 65%
print("\n\n2. Verificando que todos los estudiantes cumplan con el 65%...")
print("-" * 80)

cumple_requisito = 0
no_cumple_requisito = 0

for cuenta in ESTUDIANTES:
    try:
        estudiante = UserProfile.objects.get(account_number=cuenta)

        # Obtener estadísticas
        stats, created = AttendanceStats.objects.get_or_create(
            student=estudiante,
            defaults={
                'total_events': 0,
                'attended_events': 0,
                'attendance_percentage': 0.0
            }
        )

        # Actualizar estadísticas
        stats.update_stats()

        cumple = "✅ SÍ CUMPLE" if stats.attendance_percentage >= 65 else "❌ NO CUMPLE"

        print(f"\n{cumple} - {estudiante.full_name} ({cuenta})")
        print(f"  Eventos asistidos: {stats.attended_events}/{stats.total_events}")
        print(f"  Porcentaje: {stats.attendance_percentage}%")

        if stats.attendance_percentage >= 65:
            cumple_requisito += 1
        else:
            no_cumple_requisito += 1

        # Listar eventos asistidos
        asistencias = Attendance.objects.filter(
            student=estudiante,
            is_valid=True
        ).select_related('event').order_by('event__date', 'event__start_time')

        if asistencias.exists():
            print(f"  Asistencias registradas:")
            for asistencia in asistencias:
                print(f"    - {asistencia.event.title} ({asistencia.event.date})")

    except UserProfile.DoesNotExist:
        print(f"\n❌ No se encontró el estudiante con cuenta {cuenta}")
        no_cumple_requisito += 1

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)
print(f"Total de estudiantes verificados: {len(ESTUDIANTES)}")
print(f"✅ Cumplen con el 65%: {cumple_requisito}")
print(f"❌ No cumplen con el 65%: {no_cumple_requisito}")

if no_cumple_requisito == 0:
    print("\n🎉 ¡TODOS LOS ESTUDIANTES CUMPLEN CON EL REQUISITO DE ASISTENCIA!")
else:
    print(f"\n⚠️  Hay {no_cumple_requisito} estudiante(s) que aún no cumplen el requisito")
