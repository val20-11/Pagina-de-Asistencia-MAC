from django.contrib import admin
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Event


class EventResource(resources.ModelResource):
    """Recurso para importar/exportar eventos"""

    class Meta:
        model = Event
        fields = ('title', 'speaker', 'date', 'start_time', 'end_time', 'event_type',
                  'modality', 'location', 'description', 'is_active')
        import_id_fields = ['title', 'date', 'start_time']
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Limpiar datos antes de importar"""
        row['title'] = str(row.get('title', '')).strip()
        row['speaker'] = str(row.get('speaker', '')).strip()
        row['location'] = str(row.get('location', '')).strip()



@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource
    list_display = ['title', 'speaker', 'date', 'start_time', 'modality', 'location', 'is_active']
    list_filter = ['event_type', 'modality', 'date', 'is_active']
    search_fields = ['title', 'speaker', 'location']
    date_hierarchy = 'date'
    ordering = ['date', 'start_time']
    readonly_fields = ['created_at']
    actions = ['export_selected_events']

    def get_import_formats(self):
        """Formatos permitidos para importar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def get_export_formats(self):
        """Formatos permitidos para exportar"""
        from import_export.formats.base_formats import XLSX, CSV
        return [XLSX, CSV]

    def export_selected_events(self, request, queryset):
        """Acción para exportar eventos seleccionados"""
        from django.http import HttpResponse
        resource = EventResource()
        dataset = resource.export(queryset)

        from import_export.formats.base_formats import XLSX
        xlsx_format = XLSX()
        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(
            export_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="eventos.xlsx"'

        self.message_user(request, f'Se exportaron {queryset.count()} eventos.')
        return response

    export_selected_events.short_description = "📊 Exportar eventos seleccionados"