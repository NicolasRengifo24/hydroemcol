"""Punto único de acceso al almacenamiento de archivos.

Hoy lo usan las fotografías de la solicitud pública (RF-5) y las imágenes de
la vitrina (spec 013). Guarda en `Fotografia.url` o `imagen_referencia` una
referencia, nunca un binario: `/media/...` con el almacenamiento local de
Django o `r2://...` con Cloudflare R2.

En producción se usa R2 privado: las URLs se generan al serializar. Para las
imágenes de la vitrina existe además una base pública opcional
(`VITRINA_IMAGENES_BASE_URL`) que evita firmar cada URL.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from .imagenes import procesar_imagen
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


def guardar_archivo(archivo, carpeta):
    """Guarda `archivo` bajo `carpeta` y devuelve su referencia, sin conocer
    el proveedor (local o R2).

    Es el único punto que llama a `default_storage.save`. Si el proveedor
    falla se lanza `ErrorDeAlmacenamiento`; el detalle queda solo en el log.
    """
    nombre = f'{carpeta}/{uuid.uuid4().hex}_{Path(archivo.name).name}'
    try:
        nombre_guardado = default_storage.save(nombre, archivo)
    except Exception as error:
        # El detalle del proveedor (por ejemplo `AccessDenied` o
        # `SignatureDoesNotMatch`) queda solo en el log del servidor.
        logger.error(
            'Fallo al guardar un archivo en el almacenamiento: %s',
            error,
            exc_info=True,
        )
        raise ErrorDeAlmacenamiento(str(error)) from error
    if getattr(settings, 'R2_ENABLED', False):
        return f'{settings.R2_REFERENCE_PREFIX}{nombre_guardado}'
    return f'{settings.MEDIA_URL}{nombre_guardado}'


def guardar_fotografia(archivo):
    """Guarda un archivo y devuelve su referencia, sin conocer el proveedor."""
    return guardar_archivo(archivo, 'fotografias')


def guardar_imagen_vitrina(archivo, carpeta='vitrina'):
    """Procesa (valida, reduce y recomprime a WEBP) y guarda una imagen.

    No guarda nada si `procesar_imagen` rechaza el archivo. `carpeta` permite
    separar los objetos del catálogo (`vitrina/productos`) de los del carrusel
    (`vitrina/carrusel`). Devuelve la referencia persistible.
    """
    contenido, _ = procesar_imagen(archivo)
    return guardar_archivo(contenido, carpeta)


def url_fotografia(referencia):
    """Genera una URL temporal para una referencia privada de R2."""
    if not getattr(settings, 'R2_ENABLED', False):
        return referencia
    prefijo = getattr(settings, 'R2_REFERENCE_PREFIX', 'r2://')
    if not referencia or not referencia.startswith(prefijo):
        return referencia
    return default_storage.url(referencia[len(prefijo):])


def url_imagen_vitrina(referencia):
    """Construye la URL pública de una imagen de la vitrina.

    - Referencia `r2://...` y `VITRINA_IMAGENES_BASE_URL` configurada: base
      pública + clave, sin firmar (apta para caché).
    - R2 sin base pública: cae a la URL firmada existente.
    - Referencia local `/media/...`: se devuelve tal cual (Vite la proxya en
      desarrollo).
    """
    if not referencia:
        return ''
    prefijo = getattr(settings, 'R2_REFERENCE_PREFIX', 'r2://')
    base = str(getattr(settings, 'VITRINA_IMAGENES_BASE_URL', '') or '').rstrip('/')
    if base and referencia.startswith(prefijo):
        clave = referencia[len(prefijo):].lstrip('/')
        return f'{base}/{clave}'
    return url_fotografia(referencia)


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
