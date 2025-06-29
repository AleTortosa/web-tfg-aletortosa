from django.contrib import admin
from .models import Ciudad, Etiqueta, Usuario, Evento, Resena, ResenaImagen, ReporteResena
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('ciudad_local', 'verificado', 'dni_foto_frontal', 'dni_foto_trasera'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('ciudad_local', 'verificado', 'dni_foto_frontal', 'dni_foto_trasera'),
        }),
    )
    list_display = UserAdmin.list_display + (
        'ciudad_local', 'verificado', 'mostrar_dni_foto_frontal', 'mostrar_dni_foto_trasera'
    )
    list_filter = UserAdmin.list_filter + ('verificado', 'ciudad_local')
    search_fields = UserAdmin.search_fields + ('username', 'email', 'ciudad_local__nombre')
    ordering = ('verificado', '-date_joined')

    def mostrar_dni_foto_frontal(self, obj):
        if obj.dni_foto_frontal:
            return format_html('<img src="{}" width="80" style="border-radius:6px;" />', obj.dni_foto_frontal.url)
        return "-"
    mostrar_dni_foto_frontal.short_description = "DNI Frontal"

    def mostrar_dni_foto_trasera(self, obj):
        if obj.dni_foto_trasera:
            return format_html('<img src="{}" width="80" style="border-radius:6px;" />', obj.dni_foto_trasera.url)
        return "-"
    mostrar_dni_foto_trasera.short_description = "DNI Trasera"

class EventoAdmin(admin.ModelAdmin):
    filter_horizontal = ('etiquetas',)

class ResenaImagenInline(admin.TabularInline):
    model = ResenaImagen
    extra = 1

class ResenaAdmin(admin.ModelAdmin):
    inlines = [ResenaImagenInline]

@admin.register(ReporteResena)
class ReporteResenaAdmin(admin.ModelAdmin):
    list_display = ('resena', 'reportado_por', 'fecha', 'revisado')
    list_filter = ('revisado',)
    search_fields = ('resena__descripcion', 'reportado_por__username', 'motivo')
    actions = ['marcar_como_revisado', 'eliminar_resena']

    def marcar_como_revisado(self, request, queryset):
        queryset.update(revisado=True)
    marcar_como_revisado.short_description = "Marcar reportes seleccionados como revisados"

    def eliminar_resena(self, request, queryset):
        for reporte in queryset:
            if reporte.resena:
                reporte.resena.delete()
    eliminar_resena.short_description = "Eliminar reseñas reportadas"

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Ciudad)
admin.site.register(Etiqueta)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Resena, ResenaAdmin)