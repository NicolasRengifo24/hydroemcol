from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario administrativo del sistema.

    Reutiliza los campos que ya trae AbstractUser para no duplicar
    conceptos (regla del CONTEXTO_MAESTRO):
      - nombre  -> first_name
      - apellido -> last_name
      - activo  -> is_active
      - ultimo_acceso -> last_login
      - fecha_creacion -> campo propio (no existe equivalente directo)

    Se agrega únicamente `rol` (por ahora solo ADMINISTRATIVO).
    """

    class Roles(models.TextChoices):
        ADMINISTRATIVO = 'ADMINISTRATIVO', 'Administrativo'

    rol = models.CharField(
        max_length=30,
        choices=Roles.choices,
        default=Roles.ADMINISTRATIVO,
        verbose_name='Rol',
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        name = self.get_full_name() or self.username
        return f'{name} ({self.rol})'