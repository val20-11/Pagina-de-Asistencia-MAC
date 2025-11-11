import os
import sys
import django
from datetime import datetime
import math

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mac_attendance.settings.local')
django.setup()

from attendance.models import Attendance, AttendanceStats
from events.models import Event
from authentication.models import UserProfile
from django.db import transaction

# Números de cuenta a corregir
ESTUDIANTES_DIA_ESPECIFICO = {
    '42307052': [20, 22, 24]  # Este estudiante necesita asistencias en días específicos
}

# Estudiantes que necesitan cumplir el 65%
ESTUDIANTES_65_PORCIENTO = [
    '42306223',
    '42307052',  # Este también está en la lista
    '32326922',
    '31904405',
    '42212521',
    '42110637'
]

def main():
    print("=" * 80)
    print("CORRECCIÓN DE ASISTENCIAS")
    print("=" * 80)

    # 1. Buscar eventos activos
    print("\n1. Buscando eventos activos...")
    eventos = Event.objects.filter(is_active=True).order_by('date')

    if not eventos.exists():
        print("❌ No se encontraron eventos activos")
        return

    print(f"✓ Se encontraron {eventos.count()} eventos activos")

    # Agrupar eventos por día
    eventos_por_dia = {}
    for evento in eventos:
        dia = evento.date.day
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        eventos_por_dia[dia].append(evento)

    print(f"\nDías con eventos: {sorted(eventos_por_dia.keys())}")

    # 2. Verificar que existan eventos en los días 20, 22, 24
    dias_requeridos = [20, 22, 24]
    eventos_a_registrar = {}

    for dia in dias_requeridos:
        if dia in eventos_por_dia:
            eventos_a_registrar[dia] = eventos_por_dia[dia]
            print(f"\nDía {dia}:")
            for evento in eventos_por_dia[dia]:
                print(f"  - {evento.title} ({evento.date} {evento.start_time})")
        else:
            print(f"\n⚠️  No hay eventos registrados para el día {dia}")

    if not eventos_a_registrar:
        print("\n❌ No hay eventos en los días especificados (20, 22, 24)")
        return

    # 3. Buscar un asistente para usar como 'registered_by'
    print("\n2. Buscando asistente para registrar asistencias...")
    asistente = UserProfile.objects.filter(user_type='assistant').first()

    if not asistente:
        print("❌ No se encontró ningún asistente en el sistema")
        return

    print(f"✓ Usando asistente: {asistente.full_name}")

    # 4. Procesar estudiante 42307052 (días específicos)
    print("\n3. Procesando asistencias para días específicos...")
    print("-" * 80)

    cuenta = '42307052'
    dias = ESTUDIANTES_DIA_ESPECIFICO[cuenta]

    try:
        estudiante = UserProfile.objects.get(account_number=cuenta)
        print(f"\n✓ Estudiante encontrado: {estudiante.full_name} ({cuenta})")

        asistencias_creadas = 0
        asistencias_existentes = 0

        for dia in dias:
            if dia in eventos_a_registrar:
                for evento in eventos_a_registrar[dia]:
                    # Verificar si ya existe asistencia
                    existe = Attendance.objects.filter(
                        student=estudiante,
                        event=evento,
                        is_valid=True
                    ).exists()

                    if existe:
                        print(f"  ⊙ Ya existe asistencia: {evento.title} ({evento.date})")
                        asistencias_existentes += 1
                    else:
                        # Crear asistencia con skip_validation
                        with transaction.atomic():
                            asistencia = Attendance(
                                student=estudiante,
                                event=evento,
                                registered_by=asistente,
                                registration_method='manual',
                                notes='Corrección de asistencia - registrado manualmente'
                            )
                            asistencia.save(skip_validation=True)
                            print(f"  ✓ Asistencia creada: {evento.title} ({evento.date})")
                            asistencias_creadas += 1

        print(f"\nResumen para {cuenta}:")
        print(f"  - Asistencias creadas: {asistencias_creadas}")
        print(f"  - Asistencias ya existentes: {asistencias_existentes}")

    except UserProfile.DoesNotExist:
        print(f"❌ No se encontró estudiante con cuenta {cuenta}")
    except Exception as e:
        print(f"❌ Error procesando estudiante {cuenta}: {str(e)}")

    # 5. Procesar estudiantes que necesitan cumplir el 65%
    print("\n4. Procesando estudiantes para cumplir 65% de asistencia...")
    print("-" * 80)

    for cuenta in ESTUDIANTES_65_PORCIENTO:
        try:
            estudiante = UserProfile.objects.get(account_number=cuenta)
            print(f"\n📊 Estudiante: {estudiante.full_name} ({cuenta})")

            # Obtener o crear estadísticas
            stats, created = AttendanceStats.objects.get_or_create(
                student=estudiante,
                defaults={
                    'total_events': 0,
                    'attended_events': 0,
                    'attendance_percentage': 0.0
                }
            )

            # Actualizar estadísticas actuales
            stats.update_stats()

            print(f"  Estado actual: {stats.attended_events}/{stats.total_events} eventos ({stats.attendance_percentage}%)")

            if stats.attendance_percentage >= 65:
                print(f"  ✓ Ya cumple con el 65% requerido")
                continue

            # Calcular cuántos eventos más necesita (redondear hacia arriba)
            eventos_minimos_65 = math.ceil(stats.total_events * 0.65)
            eventos_necesarios = eventos_minimos_65 - stats.attended_events
            if eventos_necesarios < 0:
                eventos_necesarios = 0

            print(f"  Necesita asistir a {eventos_necesarios} eventos más para cumplir el 65%")

            if eventos_necesarios == 0:
                print(f"  ✓ Ya cumple con el requisito")
                continue

            # Buscar eventos a los que no ha asistido
            eventos_asistidos = Attendance.objects.filter(
                student=estudiante,
                is_valid=True
            ).values_list('event_id', flat=True)

            eventos_disponibles = Event.objects.filter(
                is_active=True
            ).exclude(id__in=eventos_asistidos).order_by('date', 'start_time')

            print(f"  Eventos disponibles para registrar: {eventos_disponibles.count()}")

            # Registrar asistencias hasta cumplir el 65%, evitando conflictos
            asistencias_agregadas = 0
            intentos_fallidos = 0
            max_intentos_fallidos = 10  # Evitar bucle infinito

            for evento in eventos_disponibles:
                # Si ya alcanzamos el número necesario, salir
                if asistencias_agregadas >= eventos_necesarios:
                    break

                # Si hay muchos fallos consecutivos, probablemente no hay más eventos disponibles
                if intentos_fallidos >= max_intentos_fallidos:
                    print(f"  ⚠️  Se alcanzó el límite de intentos fallidos. No hay más eventos compatibles.")
                    break

                try:
                    with transaction.atomic():
                        asistencia = Attendance(
                            student=estudiante,
                            event=evento,
                            registered_by=asistente,
                            registration_method='manual',
                            notes='Corrección de asistencia - registrado manualmente'
                        )
                        asistencia.save(skip_validation=True)
                        print(f"  ✓ Asistencia agregada: {evento.title} ({evento.date})")
                        asistencias_agregadas += 1
                        intentos_fallidos = 0  # Resetear contador de fallos
                except Exception as e:
                    print(f"  ⚠️  No se pudo agregar: {evento.title} - {str(e)}")
                    intentos_fallidos += 1

            # Actualizar estadísticas finales
            stats.update_stats()
            print(f"\n  Estado final: {stats.attended_events}/{stats.total_events} eventos ({stats.attendance_percentage}%)")

            if stats.attendance_percentage >= 65:
                print(f"  ✅ Ahora cumple con el 65% requerido")
            else:
                print(f"  ⚠️  Aún no cumple el 65% - se agregaron {asistencias_agregadas} asistencias")

        except UserProfile.DoesNotExist:
            print(f"\n❌ No se encontró estudiante con cuenta {cuenta}")
        except Exception as e:
            print(f"\n❌ Error procesando estudiante {cuenta}: {str(e)}")

    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)

if __name__ == '__main__':
    main()
