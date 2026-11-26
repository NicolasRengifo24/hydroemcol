"""Validación y procesamiento de las imágenes de la vitrina (spec 013).

Es el único punto que decodifica una imagen subida antes de guardarla: valida
el tamaño, la extensión y el **formato real** (no `content_type` ni el nombre),
rechaza animaciones y archivos dañados, aplica la orientación EXIF, reduce el
lado mayor a 1600 px y devuelve un WEBP recomprimido.

No toca base de datos ni almacenamiento: un error aquí no deja archivo ni
referencia (RNF-VIT-02, R6 del plan).
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

# Topes y formatos aprobados en el plan §3.2.
TAMANO_MAXIMO = 5 * 1024 * 1024  # 5 MB antes de abrir el archivo.
EXTENSIONES_PERMITIDAS = ('.jpg', '.jpeg', '.png', '.webp')
FORMATOS_REALES_PERMITIDOS = ('JPEG', 'PNG', 'WEBP')
PIXELES_MAXIMOS = 40_000_000  # Evita bombas de descompresión.
LADO_MAXIMO = 1600
CALIDAD_WEBP = 82
EXTENSION_SALIDA = '.webp'


class ErrorDeImagen(Exception):
    """La imagen no cumple las reglas; el mensaje es apto para el usuario.

    ``campo`` permite al serializer administrativo asociar el error al campo
    del formulario. El detalle del decodificador nunca se expone: se resume en
    un mensaje controlado.
    """

    def __init__(self, detalle, campo='imagen'):
        super().__init__(detalle)
        self.detalle = detalle
        self.campo = campo


def _validar_tamano(archivo):
    tamano = getattr(archivo, 'size', 0) or 0
    if tamano > TAMANO_MAXIMO:
        raise ErrorDeImagen('La imagen supera el límite de 5 MB.')
    if tamano <= 0:
        raise ErrorDeImagen('El archivo de imagen está vacío.')


def _validar_extension(archivo):
    extension = Path(getattr(archivo, 'name', '') or '').suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ErrorDeImagen(
            'Formato no admitido: usa JPG, JPEG, PNG o WEBP.'
        )


def _reabrir(archivo):
    """Vuelve al inicio; Pillow deja el flujo al final tras `verify()`."""
    try:
        archivo.seek(0)
    except (AttributeError, OSError):  # pragma: no cover - defensivo
        pass
    return archivo


def _abrir_verificada(archivo):
    """Decodifica la cabecera y comprueba la integridad antes de procesar."""
    _reabrir(archivo)
    try:
        with Image.open(archivo) as comprobacion:
            comprobacion.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ErrorDeImagen('El archivo no es una imagen válida o está dañado.')

    _reabrir(archivo)
    try:
        # `open` solo lee la cabecera: el tamaño en píxeles se valida antes de
        # descomprimir la imagen completa.
        return Image.open(archivo)
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ErrorDeImagen('El archivo no es una imagen válida o está dañado.')


def _validar_formato_real(imagen):
    formato = (imagen.format or '').upper()
    if formato not in FORMATOS_REALES_PERMITIDOS:
        raise ErrorDeImagen('Formato no admitido: usa JPG, JPEG, PNG o WEBP.')


def _validar_animacion(imagen):
    if getattr(imagen, 'is_animated', False) or getattr(imagen, 'n_frames', 1) > 1:
        raise ErrorDeImagen('No se admiten imágenes animadas.')


def _validar_pixeles(imagen):
    ancho, alto = imagen.size
    if ancho * alto > PIXELES_MAXIMOS:
        raise ErrorDeImagen(
            'La imagen tiene demasiados píxeles. Usa una imagen más pequeña.'
        )


def _nombre_salida(archivo):
    tallo = Path(getattr(archivo, 'name', '') or '').stem.strip()
    return f'{tallo or "imagen"}{EXTENSION_SALIDA}'


def procesar_imagen(archivo):
    """Valida y convierte una imagen en WEBP; no guarda nada.

    Devuelve ``(contenido, nombre_sugerido)``. Lanza `ErrorDeImagen` con un
    mensaje controlado si el archivo no cumple las reglas.
    """
    _validar_tamano(archivo)
    _validar_extension(archivo)

    original = _abrir_verificada(archivo)
    try:
        _validar_formato_real(original)
        _validar_animacion(original)
        _validar_pixeles(original)
        # A partir de aquí se descomprime: las dimensiones ya están acotadas.
        original.load()
        # Copia independiente con la orientación EXIF aplicada; el original se
        # libera en el `finally`.
        imagen = ImageOps.exif_transpose(original)
    finally:
        original.close()

    try:
        imagen.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.LANCZOS)
        if imagen.mode != 'RGB':
            convertida = imagen.convert('RGB')
            imagen.close()
            imagen = convertida

        salida = BytesIO()
        imagen.save(salida, format='WEBP', quality=CALIDAD_WEBP)
    except (OSError, ValueError) as error:
        raise ErrorDeImagen(
            'No se pudo procesar la imagen. Verifica que no esté dañada.'
        ) from error
    finally:
        imagen.close()

    nombre = _nombre_salida(archivo)
    return ContentFile(salida.getvalue(), name=nombre), nombre
