from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from import_export import resources, fields
from import_export.admin import ImportExportMixin
from .models import Attendance, AttendanceStats
from django.core.exceptions import ValidationError
import pandas as pd
from datetime import datetime


class AttendanceResource(resources.ModelResource):
    """Recurso para importar/exportar asistencias"""
    student_account_number = fields.Field(column_name='account_number')
    student_name = fields.Field(column_name='student_name')
    event_title = fields.Field(column_name='event_title')
    registered_by_account = fields.Field(column_name='registered_by_account')

    class Meta:
        model = Attendance
        fields = ('id', 'student_account_number', 'student_name', 'event_title',
                  'timestamp', 'registered_by_account', 'registration_method', 'notes', 'is_valid')
        export_order = fields
        import_id_fields = []  # No usar ID para importación
        skip_unchanged = True

    def dehydrate_student_account_number(self, attendance):
        """Obtener número de cuenta del estudiante"""
        return attendance.student.account_number

    def dehydrate_student_name(self, attendance):
        """Obtener nombre del estudiante"""
        return attendance.student.full_name

    def dehydrate_event_title(self, attendance):
        """Obtener título del evento"""
        return attendance.event.title

    def dehydrate_registered_by_account(self, attendance):
        """Obtener cuenta del asistente que registró"""
        return attendance.registered_by.account_number if attendance.registered_by else ''

    def before_import_row(self, row, **kwargs):
        """Procesar fila antes de importar"""
        from authentication.models import UserProfile
        from events.models import Event
        from django.utils import timezone

        # Normalizar número de cuenta del estudiante
        account_number = str(row.get('account_number', '')).strip()
        account_number = account_number.replace(' ', '').replace('-', '')[:8]

        # Buscar estudiante
        try:
            student = UserProfile.objects.get(account_number=account_number, user_type='student')
        except UserProfile.DoesNotExist:
            raise ValidationError(f"Estudiante con cuenta {account_number} no encontrado")

        # Buscar evento
        event_title = str(row.get('event_title', '')).strip()
        try:
            event = Event.objects.get(title=event_title)
        except Event.DoesNotExist:
            raise ValidationError(f"Evento '{event_title}' no encontrado")

        # Buscar o crear asistente que registra
        registered_by_account = str(row.get('registered_by_account', '11111111')).strip()[:8]
        try:
            registered_by = UserProfile.objects.get(account_number=registered_by_account, user_type='assistant')

            # Verificar/crear permisos de asistente
            from authentication.models import Asistente
            Asistente.objects.get_or_create(
                user_profile=registered_by,
                defaults={'can_manage_events': True}
            )
        except UserProfile.DoesNotExist:
            # Usar asistente por defecto
            registered_by = UserProfile.objects.get(account_number='11111111', user_type='assistant')

        # Preparar datos para el modelo
        row['student'] = student.id
        row['event'] = event.id
        row['registered_by'] = registered_by.id

        # Timestamp
        if 'timestamp' not in row or not row['timestamp']:
            row['timestamp'] = timezone.now()

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Guardar la instancia usando skip_validation=True para permitir
        importaciones de asistencias pasadas (fuera de ventana de tiempo)
        """
        if not dry_run:
            # Usar skip_validation=True para permitir importar asistencias históricas
            # Esto omite la validación de tiempo pero mantiene validación de duplicados
            instance.save(skip_validation=True)


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
class AttendanceStatsAdmin(ImportExportMixin, admin.ModelAdmin):
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

    def get_import_formats(self):
        """Formatos permitidos para importar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

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