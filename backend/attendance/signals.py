"""
Señales para mantener las estadísticas de asistencia actualizadas.
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from events.models import Event
from attendance.models import Attendance, AttendanceStats


@receiver(post_delete, sender=Event)
def update_stats_on_event_delete(sender, instance, **kwargs):
    """
    Cuando se elimina un evento, actualizar las estadísticas de TODOS los estudiantes.
    Esto es necesario porque el total de eventos cambia para todos.
    """
    print(f"[SIGNAL] Evento '{instance.title}' eliminado. Actualizando estadísticas de todos los estudiantes...")

    # Actualizar todas las estadísticas existentes
    stats = AttendanceStats.objects.all()
    count = 0
    for stat in stats:
        stat.update_stats()
        count += 1

    print(f"[SIGNAL] Se actualizaron las estadísticas de {count} estudiantes.")


@receiver(post_delete, sender=Attendance)
def update_stats_on_attendance_delete(sender, instance, **kwargs):
    """
    Cuando se elimina una asistencia, actualizar las estadísticas del estudiante.
    """
    if instance.student:
        print(f"[SIGNAL] Asistencia eliminada para {instance.student.full_name}. Actualizando estadísticas...")

        # Verificar si existe el registro de estadísticas
        try:
            stats = AttendanceStats.objects.get(student=instance.student)
            stats.update_stats()
            print(f"[SIGNAL] Estadísticas actualizadas para {instance.student.full_name}")
        except AttendanceStats.DoesNotExist:
            print(f"[SIGNAL] No existen estadísticas para {instance.student.full_name}")


@receiver(post_save, sender=Event)
def update_stats_on_event_save(sender, instance, created, **kwargs):
    """
    Cuando se crea o modifica un evento, actualizar las estadísticas de TODOS los estudiantes
    si el evento es activo (ya que afecta el total de eventos).
    Solo actualizar si es un evento nuevo o si cambió el estado de is_active.
    """
    if created or (hasattr(instance, '_state') and instance._state.adding is False):
        # Verificar si es un evento nuevo o si cambió is_active
        if created:
            print(f"[SIGNAL] Nuevo evento '{instance.title}' creado. Actualizando estadísticas de todos los estudiantes...")

            # Actualizar todas las estadísticas existentes
            stats = AttendanceStats.objects.all()
            count = 0
            for stat in stats:
                stat.update_stats()
                count += 1

            print(f"[SIGNAL] Se actualizaron las estadísticas de {count} estudiantes.")
