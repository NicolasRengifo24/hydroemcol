"""Crea (o habilita) el usuario administrativo de la aplicación.

Está pensado para el despliegue: el plan gratuito de Render no ofrece shell,
así que el comando se ejecuta durante el build. Es idempotente, de modo que
puede permanecer en el comando de build sin crear efectos secundarios.

Variables de entorno:
    HIDROEMCOL_ADMIN_USERNAME  nombre de usuario (por defecto `user`).
    HIDROEMCOL_ADMIN_PASSWORD  contraseña; obligatoria al crear el usuario.
    HIDROEMCOL_ADMIN_EMAIL     correo (por defecto `admin@hydroemcol.com`).

Opciones:
    --actualizar-clave  vuelve a fijar la contraseña de un usuario existente.
"""

import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea o habilita el usuario administrativo definido por entorno.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--actualizar-clave',
            action='store_true',
            help='Vuelve a fijar la contraseña si el usuario ya existe.',
        )

    def handle(self, *args, **opciones):
        username = os.getenv('HIDROEMCOL_ADMIN_USERNAME', 'user').strip()
        password = os.getenv('HIDROEMCOL_ADMIN_PASSWORD', '')
        email = os.getenv('HIDROEMCOL_ADMIN_EMAIL', 'admin@hydroemcol.com').strip()
        actualizar_clave = opciones['actualizar_clave']

        if not username:
            raise CommandError('HIDROEMCOL_ADMIN_USERNAME no puede estar vacío.')

        with transaction.atomic():
            usuario = Usuario.objects.filter(username=username).first()
            if usuario is None:
                if not password:
                    raise CommandError(
                        'HIDROEMCOL_ADMIN_PASSWORD es obligatoria para crear el usuario.'
                    )
                usuario = Usuario(
                    username=username,
                    email=email,
                    rol=Usuario.Roles.ADMINISTRATIVO,
                    is_active=True,
                    is_staff=True,
                )
                usuario.set_password(password)
                usuario.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Usuario administrativo "{username}" creado.')
                )
                return

            cambios = []
            if usuario.rol != Usuario.Roles.ADMINISTRATIVO:
                usuario.rol = Usuario.Roles.ADMINISTRATIVO
                cambios.append('rol')
            if not usuario.is_active:
                usuario.is_active = True
                cambios.append('is_active')
            if not usuario.is_staff:
                usuario.is_staff = True
                cambios.append('is_staff')
            if not usuario.email:
                usuario.email = email
                cambios.append('email')
            if actualizar_clave:
                if not password:
                    raise CommandError(
                        'HIDROEMCOL_ADMIN_PASSWORD es obligatoria para actualizar la clave.'
                    )
                usuario.set_password(password)
                cambios.append('password')
            if cambios:
                usuario.save(update_fields=cambios)

        self.stdout.write(
            self.style.SUCCESS(f'Usuario administrativo "{username}" disponible.')
        )
