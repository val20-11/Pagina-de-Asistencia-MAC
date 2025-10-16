from django.core.management.base import BaseCommand
from attendance.models import AttendanceStats
from authentication.models import UserProfile


class Command(BaseCommand):
    help = 'Recalcula las estadísticas de asistencia de todos los estudiantes usando bloques de horario'

    def handle(self, *args, **options):
        self.stdout.write('Recalculando estadísticas de asistencia...\n')

        # Obtener todos los estudiantes
        students = UserProfile.objects.filter(user_type='student')
        total_students = students.count()

        self.stdout.write(f'Se encontraron {total_students} estudiantes\n')

        updated = 0
        for student in students:
            # Obtener o crear las estadísticas
            stats, created = AttendanceStats.objects.get_or_create(student=student)

            # Actualizar con la nueva lógica
            stats.update_stats()

            updated += 1

            if updated % 10 == 0:
                self.stdout.write(f'Procesados {updated}/{total_students} estudiantes...')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nEstadisticas recalculadas exitosamente para {updated} estudiantes'
            )
        )
