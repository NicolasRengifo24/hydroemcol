from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Panel de administración del usuario. Hereda UserAdmin de Django para
    que el manejo de password (hash, cambio de clave) quede correcto."""

    fieldsets = UserAdmin.fieldsets + (
        ('Información del proyecto', {'fields': ('rol', 'fecha_creacion')}),
    )
    readonly_fields = ('fecha_creacion',)
    list_display = ('username', 'first_name', 'last_name', 'rol', 'is_active', 'fecha_creacion')
    list_filter = UserAdmin.list_filter + ('rol',)
    search_fields = ('username', 'first_name', 'last_name', 'email')