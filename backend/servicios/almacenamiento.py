"""Guardado de las fotografías de una solicitud pública (RF-5).

Es el **único** punto del proyecto que habla con el almacenamiento. Hoy usa el
almacenamiento local de Django (`default_storage` sobre `MEDIA_ROOT`) y guarda
en `Fotografia.url` una referencia `/media/...`.

La migración futura a Cloudflare (plan D-1) es un cambio de este módulo: la
vista, el serializer y el contrato (`Fotografia.url` sigue siendo `URLField`)
no se tocan.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from .models import Fotografia, TipoFotografia


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
        nombre = f'fotografias/{uuid.uuid4().hex}_{Path(archivo.name).name}'
        nombre_guardado = default_storage.save(nombre, archivo)
        creadas.append(
            Fotografia.objects.create(
                servicio=servicio,
                url=f'{settings.MEDIA_URL}{nombre_guardado}',
                tipo=TipoFotografia.RECEPCION,
                visible_cliente=False,
            )
        )
    return creadas
