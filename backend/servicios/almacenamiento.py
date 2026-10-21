"""Guardado de las fotografías de una solicitud pública (RF-5).

Es el **único** punto del proyecto que habla con el almacenamiento. Hoy usa el
almacenamiento local de Django (`default_storage` sobre `MEDIA_ROOT`) y guarda
en `Fotografia.url` una referencia `/media/...`.

En producción puede usar Cloudflare R2 privado. La base de datos conserva una
referencia `r2://...` y las URLs firmadas se generan al serializar.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from .models import Fotografia, TipoFotografia

logger = logging.getLogger('servicios.almacenamiento')


class ErrorDeAlmacenamiento(Exception):
    """El almacenamiento configurado no pudo guardar o borrar un archivo.

    El mensaje original del proveedor (S3/R2) se conserva en el log del
    servidor, nunca en la respuesta al cliente.
    """


def guardar_fotografias(servicio, archivos):
    """Guarda cada archivo y registra su `Fotografia` (RF-5).

    - `url` queda como `{MEDIA_URL}{nombre_guardado}` (p. ej. `/media/...`).
    - `tipo` = RECEPCION y `visible_cliente` = False: es evidencia interna de
      la recepción, no información para el cliente.

    Devuelve la lista de `Fotografia` creadas. Se llama dentro del
    `transaction.atomic()` de la vista: si algo falla, no queda archivo ni
    registro huérfano en la solicitud.
    """
    creadas = []
    for archivo in archivos or []:
        referencia = guardar_fotografia(archivo)
        creadas.append(
            Fotografia.objects.create(
                servicio=servicio,
                url=referencia,
                tipo=TipoFotografia.RECEPCION,
                visible_cliente=False,
            )
        )
    return creadas


def guardar_fotografia(archivo):
    """Guarda un archivo y devuelve su referencia, sin conocer el proveedor."""
    nombre = f'fotografias/{uuid.uuid4().hex}_{Path(archivo.name).name}'
    try:
        nombre_guardado = default_storage.save(nombre, archivo)
    except Exception as error:
        # El detalle del proveedor (por ejemplo `AccessDenied` o
        # `SignatureDoesNotMatch`) queda solo en el log del servidor.
        logger.error(
            'Fallo al guardar la fotografía en el almacenamiento: %s',
            error,
            exc_info=True,
        )
        raise ErrorDeAlmacenamiento(str(error)) from error
    if getattr(settings, 'R2_ENABLED', False):
        return f'{settings.R2_REFERENCE_PREFIX}{nombre_guardado}'
    return f'{settings.MEDIA_URL}{nombre_guardado}'


def url_fotografia(referencia):
    """Genera una URL temporal para una referencia privada de R2."""
    if not getattr(settings, 'R2_ENABLED', False):
        return referencia
    prefijo = getattr(settings, 'R2_REFERENCE_PREFIX', 'r2://')
    if not referencia or not referencia.startswith(prefijo):
        return referencia
    return default_storage.url(referencia[len(prefijo):])


def eliminar_referencia(referencia):
    """Elimina una referencia local o un objeto privado de R2."""
    if getattr(settings, 'R2_ENABLED', False):
        prefijo_r2 = getattr(settings, 'R2_REFERENCE_PREFIX', 'r2://')
        if referencia and referencia.startswith(prefijo_r2):
            default_storage.delete(referencia[len(prefijo_r2):])
            return True
    prefijo = str(settings.MEDIA_URL or '')
    nombre = referencia[len(prefijo):] if prefijo and referencia.startswith(prefijo) else referencia
    if not default_storage.exists(nombre):
        return False
    default_storage.delete(nombre)
    return True
