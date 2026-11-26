"""API pública de la vitrina (spec 013, T3).

Cubre RF-VIT-01..07/19/21 y RNF-VIT-01: endpoint público de solo lectura, sin
identificadores internos, con filtro exacto y carrusel visible.
"""

import hashlib
import re
from datetime import timedelta

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from ..models import CategoriaProducto, ImagenCarrusel, Producto
from ..vitrina_reglas import clave_publica_producto

RUTA = '/api/productos/'

CATALOGO = [
    {'slug': 'bombas-hidraulicas', 'nombre': 'Bombas hidráulicas'},
    {'slug': 'reparacion-mantenimiento', 'nombre': 'Reparación y mantenimiento'},
    {'slug': 'control-hidraulico', 'nombre': 'Control hidráulico'},
    {'slug': 'transmision', 'nombre': 'Transmisión'},
]

CAMPOS_PRODUCTO = {'clave', 'nombre', 'categoria', 'descripcion', 'imagen'}
CAMPOS_IMAGEN = {'url', 'alt'}
CAMPOS_CARRUSEL = {'url', 'alt'}


def crear_producto(**cambios):
    datos = {
        'nombre': 'Bomba de pistón',
        'categoria': CategoriaProducto.BOMBAS_HIDRAULICAS,
        'descripcion': 'Descripción general aprobada.',
        'imagen_referencia': '/media/vitrina/productos/foto.webp',
        'imagen_alt': 'Bomba hidráulica de pistón.',
        'visible': True,
    }
    datos.update(cambios)
    return Producto.objects.create(**datos)


def crear_imagen(**cambios):
    datos = {
        'imagen_referencia': '/media/vitrina/carrusel/foto.webp',
        'imagen_alt': 'Banco de pruebas hidráulico.',
        'orden': 1,
        'visible': True,
    }
    datos.update(cambios)
    return ImagenCarrusel.objects.create(**datos)


class ClavePublicaTest(SimpleTestCase):
    """La clave opaca se calcula con una única fórmula (plan §4.1)."""

    def test_formula_exacta(self):
        esperada = hashlib.sha256(b'vitrina:secreto:42').hexdigest()[:16]
        self.assertEqual(clave_publica_producto(42, 'secreto'), esperada)

    def test_formato_opaco_de_16_hex(self):
        clave = clave_publica_producto(42, 'secreto')
        self.assertRegex(clave, re.compile(r'^[0-9a-f]{16}$'))
        self.assertNotEqual(clave, '42')

    def test_es_estable_y_depende_del_producto(self):
        primera = clave_publica_producto(42, 'secreto')
        self.assertEqual(primera, clave_publica_producto(42, 'secreto'))
        self.assertNotEqual(primera, clave_publica_producto(43, 'secreto'))

    def test_depende_del_secreto(self):
        self.assertNotEqual(
            clave_publica_producto(42, 'secreto'),
            clave_publica_producto(42, 'otro-secreto'),
        )


class VitrinaPublicaTest(TestCase):
    def setUp(self):
        self.api = APIClient()

    def get(self, params=None):
        return self.api.get(RUTA, params or {})

    # ── Sobre y catálogo ────────────────────────────────────────

    def test_endpoint_publico_sin_autenticacion(self):
        respuesta = self.get()
        self.assertEqual(respuesta.status_code, 200)

    def test_sobre_exacto(self):
        datos = self.get().json()
        self.assertEqual(
            set(datos), {'categorias', 'categoria', 'carrusel', 'resultados'},
        )

    def test_catalogo_exacto(self):
        self.assertEqual(self.get().json()['categorias'], CATALOGO)

    def test_sin_filtro_categoria_es_null(self):
        self.assertIsNone(self.get().json()['categoria'])

    def test_sin_paginacion(self):
        datos = self.get().json()
        self.assertIsInstance(datos['resultados'], list)
        self.assertNotIn('count', datos)
        self.assertNotIn('next', datos)
        self.assertNotIn('previous', datos)

    # ── Productos ──────────────────────────────────────────────

    def test_solo_devuelve_productos_visibles(self):
        visible = crear_producto(nombre='Visible')
        crear_producto(nombre='Oculto', visible=False)

        nombres = [item['nombre'] for item in self.get().json()['resultados']]
        self.assertEqual(nombres, ['Visible'])
        self.assertTrue(visible.visible)

    def test_oculta_productos_sin_imagen_o_sin_alt(self):
        crear_producto(nombre='Sin imagen', imagen_referencia='')
        crear_producto(nombre='Sin alt', imagen_alt='')
        crear_producto(nombre='Completo')

        nombres = [item['nombre'] for item in self.get().json()['resultados']]
        self.assertEqual(nombres, ['Completo'])

    def test_orden_por_fecha_descendente_y_desempate_por_id(self):
        antiguo = crear_producto(nombre='Antiguo')
        momento = timezone.now()
        primero = crear_producto(nombre='Primero')
        segundo = crear_producto(nombre='Segundo')
        Producto.objects.filter(pk__in=[primero.pk, segundo.pk]).update(
            fecha_creacion=momento,
        )
        Producto.objects.filter(pk=antiguo.pk).update(
            fecha_creacion=momento - timedelta(days=1),
        )

        nombres = [item['nombre'] for item in self.get().json()['resultados']]
        self.assertEqual(nombres, ['Segundo', 'Primero', 'Antiguo'])

    def test_producto_no_expone_campos_internos(self):
        crear_producto()
        item = self.get().json()['resultados'][0]

        self.assertEqual(set(item), CAMPOS_PRODUCTO)
        self.assertEqual(set(item['imagen']), CAMPOS_IMAGEN)
        self.assertEqual(set(item['categoria']), {'slug', 'nombre'})
        for prohibido in ('id', 'visible', 'fecha_creacion', 'fecha_actualizacion'):
            self.assertNotIn(prohibido, item)

    def test_item_tiene_los_valores_aprobados(self):
        producto = crear_producto()
        item = self.get().json()['resultados'][0]

        self.assertEqual(item['nombre'], producto.nombre)
        self.assertEqual(item['descripcion'], producto.descripcion)
        self.assertEqual(
            item['categoria'],
            {'slug': 'bombas-hidraulicas', 'nombre': 'Bombas hidráulicas'},
        )
        self.assertEqual(
            item['imagen'],
            {
                'url': '/media/vitrina/productos/foto.webp',
                'alt': producto.imagen_alt,
            },
        )

    def test_clave_estable_opaca_y_calculada_con_secret_key(self):
        producto = crear_producto()
        esperada = hashlib.sha256(
            f'vitrina:{settings.SECRET_KEY}:{producto.pk}'.encode('utf-8'),
        ).hexdigest()[:16]

        clave = self.get().json()['resultados'][0]['clave']
        self.assertEqual(clave, esperada)
        self.assertRegex(clave, re.compile(r'^[0-9a-f]{16}$'))
        self.assertNotEqual(clave, str(producto.pk))
        self.assertEqual(clave, self.get().json()['resultados'][0]['clave'])

    def test_claves_distintas_para_productos_distintos(self):
        crear_producto(nombre='Uno')
        crear_producto(nombre='Dos')

        claves = [item['clave'] for item in self.get().json()['resultados']]
        self.assertEqual(len(set(claves)), 2)

    @override_settings(VITRINA_IMAGENES_BASE_URL='https://cdn.ejemplo.test/')
    def test_imagen_usa_la_url_publica_de_la_vitrina(self):
        crear_producto(
            imagen_referencia='r2://vitrina/productos/bomba.webp',
            imagen_alt='Bomba en el banco de pruebas.',
        )
        crear_imagen(
            imagen_referencia='r2://vitrina/carrusel/banco.webp',
            imagen_alt='Banco de pruebas.',
        )

        datos = self.get().json()
        self.assertEqual(
            datos['resultados'][0]['imagen']['url'],
            'https://cdn.ejemplo.test/vitrina/productos/bomba.webp',
        )
        self.assertEqual(
            datos['carrusel'][0]['url'],
            'https://cdn.ejemplo.test/vitrina/carrusel/banco.webp',
        )

    # ── Filtro ─────────────────────────────────────────────────

    def test_filtro_valido_devuelve_solo_su_categoria(self):
        for indice, categoria in enumerate(CATALOGO):
            crear_producto(nombre=f'Producto {indice}', categoria=categoria['slug'])

        for indice, categoria in enumerate(CATALOGO):
            slug = categoria['slug']
            datos = self.get({'categoria': slug}).json()
            self.assertEqual(datos['categoria'], slug)
            self.assertIn(categoria, datos['categorias'])
            self.assertEqual(len(datos['resultados']), 1)
            self.assertEqual(datos['resultados'][0]['nombre'], f'Producto {indice}')

    def test_filtro_desconocido_responde_400_sin_productos(self):
        crear_producto()

        respuesta = self.get({'categoria': 'no-existe'})
        self.assertEqual(respuesta.status_code, 400)
        datos = respuesta.json()
        self.assertEqual(datos['detail'], 'La categoría indicada no existe.')
        self.assertEqual(datos['categorias'], CATALOGO)
        self.assertNotIn('resultados', datos)

    def test_filtro_vacio_responde_400(self):
        self.assertEqual(self.get({'categoria': ''}).status_code, 400)

    def test_filtro_repetido_responde_400(self):
        crear_producto()
        respuesta = self.api.get(f'{RUTA}?categoria=transmision&categoria=transmision')

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(
            respuesta.json()['detail'], 'La categoría indicada no existe.',
        )
        self.assertNotIn('resultados', respuesta.json())

    def test_filtros_validos_repetidos_responde_400(self):
        respuesta = self.api.get(
            f'{RUTA}?categoria=transmision&categoria=bombas-hidraulicas',
        )
        self.assertEqual(respuesta.status_code, 400)

    # ── Carrusel ───────────────────────────────────────────────

    def test_carrusel_solo_visibles_ordenadas_y_sin_campos_internos(self):
        crear_imagen(orden=3, imagen_alt='Tercera')
        crear_imagen(orden=1, imagen_alt='Primera')
        crear_imagen(orden=2, imagen_alt='Oculta', visible=False)

        carrusel = self.get().json()['carrusel']
        self.assertEqual([item['alt'] for item in carrusel], ['Primera', 'Tercera'])
        for item in carrusel:
            self.assertEqual(set(item), CAMPOS_CARRUSEL)

    def test_carrusel_vacio_devuelve_lista(self):
        self.assertEqual(self.get().json()['carrusel'], [])

    def test_carrusel_oculta_imagenes_sin_referencia_o_sin_alt(self):
        crear_imagen(orden=1, imagen_referencia='', imagen_alt='Sin imagen')
        crear_imagen(orden=2, imagen_alt='')
        self.assertEqual(self.get().json()['carrusel'], [])

    # ── Caché ──────────────────────────────────────────────────

    def test_cache_control_no_store_en_200(self):
        self.assertEqual(self.get()['Cache-Control'], 'no-store')

    def test_cache_control_no_store_en_400(self):
        respuesta = self.get({'categoria': 'no-existe'})
        self.assertEqual(respuesta['Cache-Control'], 'no-store')
