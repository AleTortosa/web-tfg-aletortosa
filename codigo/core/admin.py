from django.contrib import admin
from .models import Ciudad, Etiqueta, Usuario, Evento, Resena, ResenaImagen
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

admin.site.register(Ciudad)
admin.site.register(Etiqueta)
admin.site.register(Evento, EventoAdmin)
admin.site.register(Resena, ResenaAdmin)