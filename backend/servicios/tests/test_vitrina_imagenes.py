"""Vitrina digital (spec 013) — validación, procesamiento y almacenamiento.

Cubre T2: ``procesar_imagen`` (RF-VIT-13, RNF-VIT-02), el punto
único de almacenamiento y la URL pública configurable. No se hace red: en los
tests se fuerza el almacenamiento local con ``override_settings``.
"""

import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from PIL import Image

from servicios import almacenamiento
from servicios.imagenes import ErrorDeImagen, procesar_imagen


def _bytes_imagen(formato='PNG', tamano=(40, 30), modo='RGB', color='red', animada=False):
    buffer = BytesIO()
    if animada:
        fotogramas = [
            Image.new('RGB', tamano, 'red'),
            Image.new('RGB', tamano, 'blue'),
        ]
        fotogramas[0].save(
            buffer, format='WEBP', save_all=True,
            append_images=fotogramas[1:], duration=100, loop=0,
        )
    else:
        Image.new(modo, tamano, color).save(buffer, format=formato)
    return buffer.getvalue()


def _archivo(nombre='producto.png', contenido=None, **opciones):
    if contenido is None:
        contenido = _bytes_imagen(**opciones)
    return SimpleUploadedFile(nombre, contenido, content_type='image/png')


class ProcesarImagenTest(SimpleTestCase):
    def test_png_valido_devuelve_webp(self):
        contenido, nombre = procesar_imagen(_archivo())

        self.assertTrue(nombre.endswith('.webp'))
        self.assertTrue(contenido.name.endswith('.webp'))
        datos = contenido.read()
        self.assertEqual(datos[:4], b'RIFF')
        self.assertEqual(datos[8:12], b'WEBP')
        with Image.open(BytesIO(datos)) as resultado:
            self.assertEqual(resultado.format, 'WEBP')
            self.assertEqual(resultado.mode, 'RGB')
            self.assertEqual(resultado.size, (40, 30))

    def test_formatos_permitidos(self):
        casos = [
            ('foto.jpg', 'JPEG'),
            ('foto.jpeg', 'JPEG'),
            ('foto.png', 'PNG'),
            ('foto.webp', 'WEBP'),
        ]
        for nombre, formato in casos:
            with self.subTest(formato=formato):
                contenido, nombre_salida = procesar_imagen(
                    _archivo(nombre=nombre, formato=formato)
                )
                datos = contenido.read()
                self.assertTrue(nombre_salida.endswith('.webp'))
                with Image.open(BytesIO(datos)) as resultado:
                    self.assertEqual(resultado.format, 'WEBP')

    def test_reduce_el_lado_mayor_a_1600_px_sin_deformar(self):
        contenido, _ = procesar_imagen(_archivo(tamano=(2400, 1200)))
        with Image.open(BytesIO(contenido.read())) as resultado:
            self.assertEqual(resultado.size, (1600, 800))

        vertical, _ = procesar_imagen(_archivo(tamano=(800, 2000)))
        with Image.open(BytesIO(vertical.read())) as resultado:
            self.assertEqual(resultado.size, (640, 1600))

    def test_no_amplia_imagenes_pequenas(self):
        contenido, _ = procesar_imagen(_archivo(tamano=(40, 30)))
        with Image.open(BytesIO(contenido.read())) as resultado:
            self.assertEqual(resultado.size, (40, 30))

    def test_aplica_la_orientacion_exif(self):
        imagen = Image.new('RGB', (40, 20), 'red')
        exif = Image.Exif()
        exif[0x0112] = 6  # Rotar 90° en sentido horario al mostrar.
        buffer = BytesIO()
        imagen.save(buffer, format='JPEG', exif=exif)
        archivo = SimpleUploadedFile(
            'girada.jpg', buffer.getvalue(), content_type='image/jpeg',
        )

        contenido, _ = procesar_imagen(archivo)
        with Image.open(BytesIO(contenido.read())) as resultado:
            self.assertEqual(resultado.size, (20, 40))

    def test_extension_no_permitida(self):
        with self.assertRaises(ErrorDeImagen) as contexto:
            procesar_imagen(_archivo(nombre='producto.gif'))
        self.assertEqual(contexto.exception.campo, 'imagen')
        self.assertIn('formato', contexto.exception.detalle.lower())

    def test_contenido_corrupto(self):
        archivo = _archivo(
            contenido=b'\x89PNG\r\n\x1a\ncontenido-simulado',
        )
        with self.assertRaises(ErrorDeImagen):
            procesar_imagen(archivo)

    def test_formato_real_no_permitido_oculto_tras_extension_valida(self):
        buffer = BytesIO()
        Image.new('RGB', (10, 10), 'red').save(buffer, format='BMP')
        with self.assertRaises(ErrorDeImagen):
            procesar_imagen(
                _archivo(nombre='producto.jpg', contenido=buffer.getvalue())
            )

    def test_mime_real_manda_sobre_el_content_type(self):
        # Un JPEG real con nombre y content_type de PNG se procesa por su
        # formato real (JPEG), no por la extensión ni por `content_type`.
        contenido_real = _bytes_imagen(formato='JPEG')
        archivo = SimpleUploadedFile(
            'producto.png', contenido_real, content_type='image/png',
        )

        contenido, _ = procesar_imagen(archivo)
        with Image.open(BytesIO(contenido.read())) as resultado:
            self.assertEqual(resultado.format, 'WEBP')

    def test_supera_el_limite_de_5_mb(self):
        archivo = SimpleUploadedFile(
            'grande.png', b'0' * (5 * 1024 * 1024 + 1), content_type='image/png',
        )
        with self.assertRaises(ErrorDeImagen) as contexto:
            procesar_imagen(archivo)
        self.assertIn('5 MB', contexto.exception.detalle)

    def test_imagen_animada_rechazada(self):
        animada = _archivo(nombre='animada.webp', animada=True)
        with self.assertRaises(ErrorDeImagen) as contexto:
            procesar_imagen(animada)
        self.assertIn('animadas', contexto.exception.detalle.lower())

    def test_limite_de_pixeles(self):
        # 40 x 30 = 1200 px; con el límite reducido se rechaza sin descomprimir
        # una imagen gigante en memoria.
        with mock.patch('servicios.imagenes.PIXELES_MAXIMOS', 1000):
            with self.assertRaises(ErrorDeImagen) as contexto:
                procesar_imagen(_archivo())
        self.assertIn('píxeles', contexto.exception.detalle.lower())


@override_settings(
    R2_ENABLED=False,
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class GuardarImagenVitrinaTest(SimpleTestCase):
    def setUp(self):
        # Un MEDIA_ROOT por test: las aserciones de "sin archivos residuales"
        # no dependen de lo que hayan escrito otros tests.
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)

    def _ruta(self, referencia):
        return Path(self.media) / referencia[len('/media/'):]

    def test_guarda_webp_bajo_vitrina(self):
        referencia = almacenamiento.guardar_imagen_vitrina(_archivo())

        self.assertTrue(referencia.startswith('/media/vitrina/'))
        self.assertTrue(referencia.endswith('.webp'))
        ruta = self._ruta(referencia)
        self.assertTrue(ruta.is_file())
        with Image.open(ruta) as imagen:
            self.assertEqual(imagen.format, 'WEBP')

    def test_permite_separar_productos_y_carrusel(self):
        productos = almacenamiento.guardar_imagen_vitrina(
            _archivo(), 'vitrina/productos',
        )
        carrusel = almacenamiento.guardar_imagen_vitrina(
            _archivo(), 'vitrina/carrusel',
        )

        self.assertTrue(productos.startswith('/media/vitrina/productos/'))
        self.assertTrue(carrusel.startswith('/media/vitrina/carrusel/'))

    def test_guardar_fotografia_conserva_su_contrato(self):
        archivo = SimpleUploadedFile(
            'bomba.png',
            b'\x89PNG\r\n\x1a\ncontenido-simulado',
            content_type='image/png',
        )

        referencia = almacenamiento.guardar_fotografia(archivo)

        self.assertRegex(
            referencia, r'^/media/fotografias/[0-9a-f]{32}_bomba\.png$',
        )
        self.assertTrue(self._ruta(referencia).is_file())

    def test_fallo_de_almacenamiento_no_deja_referencia_ni_archivo(self):
        almacen = mock.Mock()
        almacen.save.side_effect = OSError('R2 caído')

        with self.assertLogs('servicios.almacenamiento', level='ERROR'):
            with mock.patch.object(almacenamiento, 'default_storage', almacen):
                with self.assertRaises(almacenamiento.ErrorDeAlmacenamiento):
                    almacenamiento.guardar_imagen_vitrina(_archivo())

        almacen.save.assert_called_once()
        self.assertEqual(list(Path(self.media).rglob('*')), [])

    def test_imagen_invalida_no_llega_al_almacenamiento(self):
        almacen = mock.Mock()

        with mock.patch.object(almacenamiento, 'default_storage', almacen):
            with self.assertRaises(ErrorDeImagen):
                almacenamiento.guardar_imagen_vitrina(
                    SimpleUploadedFile('rota.png', b'no es una imagen')
                )

        almacen.save.assert_not_called()
        self.assertEqual(list(Path(self.media).rglob('*')), [])


class UrlImagenVitrinaTest(SimpleTestCase):
    def test_setting_definido_por_entorno(self):
        self.assertIsInstance(settings.VITRINA_IMAGENES_BASE_URL, str)
        self.assertFalse(settings.VITRINA_IMAGENES_BASE_URL.endswith('/'))

    def test_base_publica_para_referencias_r2(self):
        with override_settings(
            VITRINA_IMAGENES_BASE_URL='https://cdn.ejemplo.com',
            R2_REFERENCE_PREFIX='r2://',
        ):
            self.assertEqual(
                almacenamiento.url_imagen_vitrina(
                    'r2://vitrina/productos/a.webp'
                ),
                'https://cdn.ejemplo.com/vitrina/productos/a.webp',
            )

    def test_base_con_barra_final_no_duplica_separador(self):
        with override_settings(
            VITRINA_IMAGENES_BASE_URL='https://cdn.ejemplo.com/',
            R2_REFERENCE_PREFIX='r2://',
        ):
            self.assertEqual(
                almacenamiento.url_imagen_vitrina('r2://vitrina/a.webp'),
                'https://cdn.ejemplo.com/vitrina/a.webp',
            )

    def test_sin_base_cae_a_la_url_firmada(self):
        with mock.patch(
            'servicios.almacenamiento.url_fotografia',
            return_value='https://firmada',
        ) as firmada:
            with override_settings(VITRINA_IMAGENES_BASE_URL=''):
                self.assertEqual(
                    almacenamiento.url_imagen_vitrina('r2://vitrina/a.webp'),
                    'https://firmada',
                )
            firmada.assert_called_once_with('r2://vitrina/a.webp')

    def test_referencia_local_se_devuelve_tal_cual(self):
        with override_settings(
            VITRINA_IMAGENES_BASE_URL='https://cdn.ejemplo.com',
            R2_ENABLED=False,
        ):
            self.assertEqual(
                almacenamiento.url_imagen_vitrina('/media/vitrina/a.webp'),
                '/media/vitrina/a.webp',
            )

    def test_referencia_vacia(self):
        self.assertEqual(almacenamiento.url_imagen_vitrina(''), '')
        self.assertEqual(almacenamiento.url_imagen_vitrina(None), '')
