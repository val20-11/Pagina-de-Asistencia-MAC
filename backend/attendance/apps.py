from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = 'Gestión de Asistencias'

    def ready(self):
        """
        Importar señales cuando la aplicación esté lista.
        """
        import attendance.signals  # noqa
