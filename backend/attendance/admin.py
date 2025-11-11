from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from import_export import resources, fields, widgets
from import_export.admin import ImportExportMixin, ExportMixin
from .models import Attendance, AttendanceStats
from django.core.exceptions import ValidationError
import pandas as pd
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils import timezone as tz


class FlexibleDateTimeWidget(widgets.DateTimeWidget):
    """
    Widget personalizado que acepta múltiples formatos de fecha/hora.
    """
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None

        # Si ya es un objeto datetime, devolverlo
        if isinstance(value, datetime):
            return value

        # Convertir a string si es necesario
        val = str(value).strip()
        if not val:
            return None

        # Formatos aceptados
        date_formats = [
            '%d/%m/%Y %H:%M',      # 24/10/2025 11:44
            '%d/%m/%Y %H:%M:%S',   # 24/10/2025 11:44:00
            '%Y-%m-%d %H:%M:%S',   # 2025-10-24 11:44:00
            '%Y-%m-%d %H:%M',      # 2025-10-24 11:44
            '%d-%m-%Y %H:%M',      # 24-10-2025 11:44
            '%d-%m-%Y %H:%M:%S',   # 24-10-2025 11:44:00
        ]

        # Intentar parsear con cada formato
        for fmt in date_formats:
            try:
                dt = datetime.strptime(val, fmt)
                # Hacer timezone-aware si es necesario
                if tz.is_naive(dt):
                    dt = tz.make_aware(dt)
                return dt
            except (ValueError, TypeError):
                continue

        # Si ningún formato funciona, intentar con el parser por defecto
        try:
            dt = parse_datetime(val)
            if dt and tz.is_naive(dt):
                dt = tz.make_aware(dt)
            if dt:
                return dt
        except (ValueError, TypeError):
            pass

        # Si nada funciona, lanzar error
        raise ValueError(f"No se pudo parsear la fecha: '{value}'. Formatos aceptados: DD/MM/YYYY HH:MM o YYYY-MM-DD HH:MM:SS")


class StudentWidget(widgets.ForeignKeyWidget):
    """
    Widget para convertir account_number en objeto Student.
    """
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None

        from authentication.models import UserProfile

        # Normalizar número de cuenta
        account_number = str(value).strip().replace(' ', '').replace('-', '')[:8]

        try:
            student = UserProfile.objects.get(account_number=account_number, user_type='student')
            return student
        except UserProfile.DoesNotExist:
            raise ValueError(f"Estudiante con cuenta {account_number} no encontrado")


class EventWidget(widgets.ForeignKeyWidget):
    """
    Widget para convertir event_title en objeto Event.
    """
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None

        from events.models import Event

        # Buscar evento por título
        event_title = str(value).strip()

        try:
            event = Event.objects.get(title=event_title)
            return event
        except Event.DoesNotExist:
            raise ValueError(f"Evento '{event_title}' no encontrado")


class AssistantWidget(widgets.ForeignKeyWidget):
    """
    Widget para convertir registered_by_account en objeto Assistant.
    """
    def clean(self, value, row=None, **kwargs):
        from authentication.models import UserProfile, Asistente

        # Si no hay valor, usar por defecto
        if not value:
            value = '11111111'

        # Normalizar número de cuenta
        account_number = str(value).strip().replace(' ', '').replace('-', '')[:8]

        try:
            assistant = UserProfile.objects.get(account_number=account_number, user_type='assistant')

            # Verificar/crear permisos de asistente
            Asistente.objects.get_or_create(
                user_profile=assistant,
                defaults={'can_manage_events': True}
            )

            return assistant
        except UserProfile.DoesNotExist:
            # Usar asistente por defecto
            return UserProfile.objects.get(account_number='11111111', user_type='assistant')


class AttendanceResource(resources.ModelResource):
    """Recurso para importar/exportar asistencias"""
    # Campos con widgets personalizados para importación
    account_number = fields.Field(
        column_name='account_number',
        attribute='student',
        widget=StudentWidget(model='authentication.UserProfile', field='account_number')
    )
    student_name = fields.Field(
        column_name='student_name',
        readonly=True  # Solo para vista previa/exportación
    )
    event_title = fields.Field(
        column_name='event_title',
        attribute='event',
        widget=EventWidget(model='events.Event', field='title')
    )
    registered_by_account = fields.Field(
        column_name='registered_by_account',
        attribute='registered_by',
        widget=AssistantWidget(model='authentication.UserProfile', field='account_number')
    )
    timestamp = fields.Field(
        column_name='timestamp',
        attribute='timestamp',
        widget=FlexibleDateTimeWidget()
    )

    class Meta:
        model = Attendance
        # Campos para importar/exportar
        fields = ('account_number', 'student_name', 'event_title', 'timestamp',
                 'registered_by_account', 'registration_method', 'notes', 'is_valid')
        export_order = ('id',) + fields
        import_id_fields = []  # No usar ID para importación
        skip_unchanged = True
        exclude = ('id',)  # Excluir explícitamente el ID de la importación

    def dehydrate_account_number(self, attendance):
        """Obtener número de cuenta del estudiante para exportación"""
        return attendance.student.account_number

    def dehydrate_student_name(self, attendance):
        """Obtener nombre del estudiante para exportación"""
        return attendance.student.full_name

    def dehydrate_event_title(self, attendance):
        """Obtener título del evento para exportación"""
        return attendance.event.title

    def dehydrate_registered_by_account(self, attendance):
        """Obtener cuenta del asistente que registró para exportación"""
        return attendance.registered_by.account_number if attendance.registered_by else ''

    def before_import_row(self, row, **kwargs):
        """
        Procesar fila antes de importar.
        Los widgets se encargan de convertir los valores, aquí solo validamos.
        """
        # Los widgets personalizados (StudentWidget, EventWidget, AssistantWidget)
        # se encargan de toda la conversión automáticamente.
        # Este método se deja para validaciones adicionales si se necesitan en el futuro.
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.students_to_update = set()  # Conjunto de estudiantes para actualizar al final

    def save_instance(self, instance, *args, **kwargs):
        """
        Guardar la instancia usando skip_validation=True para permitir
        importaciones de asistencias pasadas (fuera de ventana de tiempo)
        """
        # Extraer dry_run de kwargs
        dry_run = kwargs.get('dry_run', False)

        if not dry_run:
            # Guardar sin actualizar estadísticas (se hará en batch al final)
            # Temporalmente desactivar la actualización automática
            if hasattr(instance, '_importing'):
                instance._importing = True
            else:
                # Marcar la instancia como en importación
                instance._skip_stats_update = True

            # Usar skip_validation=True para permitir importar asistencias históricas
            # Esto omite la validación de tiempo pero mantiene validación de duplicados
            instance.save(skip_validation=True)

            # Registrar estudiante para actualización posterior
            if instance.student:
                self.students_to_update.add(instance.student.id)

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """
        Después de importar todas las asistencias, actualizar estadísticas
        de los estudiantes afectados en batch (más eficiente)
        """
        if not dry_run and self.students_to_update:
            from attendance.models import AttendanceStats

            count = len(self.students_to_update)
            print(f'\n[IMPORTACIÓN] Actualizando estadísticas de {count} estudiante(s) afectado(s)...')

            updated = 0
            for student_id in self.students_to_update:
                try:
                    stats, created = AttendanceStats.objects.get_or_create(
                        student_id=student_id
                    )
                    stats.update_stats()
                    updated += 1
                except Exception as e:
                    print(f'Error actualizando estadísticas del estudiante {student_id}: {e}')

            print(f'[IMPORTACIÓN] ✓ Estadísticas actualizadas para {updated} estudiante(s)')

            # Limpiar el conjunto
            self.students_to_update.clear()


class AttendanceStatsResource(resources.ModelResource):
    """Recurso para exportar estadísticas de asistencia"""
    account_number = fields.Field()
    full_name = fields.Field()
    cumple_requisito = fields.Field()

    class Meta:
        model = AttendanceStats
        fields = ('account_number', 'full_name', 'attended_events', 'total_events',
                  'attendance_percentage', 'cumple_requisito')
        export_order = fields

    def dehydrate_account_number(self, stats):
        """Obtener número de cuenta del estudiante"""
        return stats.student.account_number

    def dehydrate_full_name(self, stats):
        """Obtener nombre completo del estudiante"""
        return stats.student.full_name

    def dehydrate_cumple_requisito(self, stats):
        """Verificar si cumple el requisito mínimo"""
        return 'SÍ' if stats.meets_minimum_requirement() else 'NO'

@admin.register(Attendance)
class AttendanceAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ['attendee_name', 'attendee_identifier', 'event', 'timestamp', 'registration_method', 'get_registered_by', 'is_valid']
    list_filter = ['registration_method', 'registered_by', 'event__date', 'is_valid', 'event']
    search_fields = ['student__full_name', 'student__account_number', 'event__title',
                     'registered_by__full_name', 'registered_by__account_number']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp', 'attendee_name', 'attendee_identifier']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Información del Asistente', {
            'fields': ('student', 'attendee_name', 'attendee_identifier')
        }),
        ('Información del Evento', {
            'fields': ('event',)
        }),
        ('Registro', {
            'fields': ('registered_by', 'registration_method', 'timestamp', 'is_valid', 'notes')
        }),
    )

    def get_registered_by(self, obj):
        """Muestra el asistente que registró con formato mejorado"""
        if obj.registered_by:
            return format_html(
                '<span style="color: #0066cc;">👤 {}</span><br><small>Cuenta: {}</small>',
                obj.registered_by.full_name,
                obj.registered_by.account_number
            )
        return '-'
    get_registered_by.short_description = 'Registrado por'

    def get_import_formats(self):
        """Formatos permitidos para importar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def has_add_permission(self, request):
        # Permitir importación pero no creación manual individual
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Solo superusuarios pueden editar asistencias (para correcciones excepcionales)
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar asistencias
        return request.user.is_superuser

@admin.register(AttendanceStats)
class AttendanceStatsAdmin(ExportMixin, admin.ModelAdmin):
    """
    Admin para estadísticas de asistencia.
    NOTA: Solo permite EXPORTAR, NO importar. Las estadísticas se calculan automáticamente.
    """
    resource_class = AttendanceStatsResource
    list_display = ['student', 'attended_events', 'total_events', 'attendance_percentage', 'get_cumple_requisito']
    ordering = ['-attendance_percentage']
    list_filter = ['attendance_percentage']
    search_fields = ['student__account_number', 'student__full_name']
    actions = ['export_selected_stats', 'export_students_with_certificate', 'update_all_stats']

    def get_cumple_requisito(self, obj):
        """Mostrar si cumple el requisito mínimo"""
        cumple = obj.meets_minimum_requirement()
        color = '#28a745' if cumple else '#dc3545'
        text = '✅ SÍ' if cumple else '❌ NO'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    get_cumple_requisito.short_description = 'Cumple requisito'

    def export_selected_stats(self, request, queryset):
        """Acción para exportar estadísticas seleccionadas"""
        resource = AttendanceStatsResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="estadisticas_asistencia.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} estadísticas.')
        return response

    export_selected_stats.short_description = "📊 Exportar estadísticas seleccionadas"

    def export_students_with_certificate(self, request, queryset):
        """Acción para exportar solo estudiantes que cumplen el requisito mínimo"""
        from authentication.models import SystemConfiguration
        config = SystemConfiguration.get_config()

        # Filtrar solo los que cumplen el requisito
        qualified_students = queryset.filter(
            attendance_percentage__gte=config.minimum_attendance_percentage
        )

        # Crear el recurso y exportar
        resource = AttendanceStatsResource()
        dataset = resource.export(qualified_students)

        # Generar archivo Excel
        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="estudiantes_con_constancia.xlsx"'

        self.message_user(
            request,
            f'Se exportaron {qualified_students.count()} estudiantes que cumplen con el {config.minimum_attendance_percentage}% de asistencia mínima.'
        )

        return response

    export_students_with_certificate.short_description = "📊 Exportar estudiantes que cumplen requisito para constancia"

    def update_all_stats(self, request, queryset):
        """Acción para actualizar estadísticas de los estudiantes seleccionados"""
        count = 0
        for stats in queryset:
            stats.update_stats()
            count += 1

        self.message_user(
            request,
            f'Se actualizaron las estadísticas de {count} estudiantes.'
        )

    update_all_stats.short_description = "🔄 Actualizar estadísticas seleccionadas"

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def has_add_permission(self, request):
        # Las estadísticas se generan automáticamente
        return False

    def has_change_permission(self, request, obj=None):
        # Las estadísticas son de solo lectura
        return False

    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar estadísticas
        return request.user.is_superuser