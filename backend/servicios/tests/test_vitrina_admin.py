"""Vitrina digital (spec 013) — categorías, modelo de Producto y API administrativa.

T1: catálogo de categorías, campos y restricciones de ``Producto``.
T4: CRUD administrativo de productos (autorización, CSRF, validación,
procesamiento de imagen y ocultamiento recuperable).
"""

import io
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from servicios.almacenamiento import ErrorDeAlmacenamiento
from servicios.models import CategoriaProducto, Producto
from servicios.serializers import ProductoAdminSerializer
from usuarios.models import Usuario


class CategoriaProductoTest(SimpleTestCase):
    def test_catalogo_exacto_con_slugs_del_query_string(self):
        self.assertEqual(
            list(CategoriaProducto.choices),
            [
                ('bombas-hidraulicas', 'Bombas hidráulicas'),
                ('reparacion-mantenimiento', 'Reparación y mantenimiento'),
                ('control-hidraulico', 'Control hidráulico'),
                ('transmision', 'Transmisión'),
            ],
        )


class ProductoModeloTest(TestCase):
    def test_campos_aprobados_sin_auditoria(self):
        nombres = {campo.name for campo in Producto._meta.fields}
        self.assertEqual(
            nombres,
            {
                'id',
                'nombre',
                'categoria',
                'descripcion',
                'imagen_referencia',
                'imagen_alt',
                'visible',
                'fecha_creacion',
                'fecha_actualizacion',
            },
        )

    def test_limites_tecnicos_de_campos(self):
        campos = {campo.name: campo for campo in Producto._meta.fields}
        self.assertEqual(campos['nombre'].max_length, 150)
        self.assertEqual(campos['categoria'].max_length, 32)
        self.assertEqual(campos['imagen_referencia'].max_length, 500)
        self.assertEqual(campos['imagen_alt'].max_length, 200)
        self.assertEqual(campos['categoria'].choices, CategoriaProducto.choices)

    def test_visible_es_falso_por_defecto(self):
        producto = Producto.objects.create(
            nombre='Bomba de prueba',
            categoria=CategoriaProducto.BOMBAS_HIDRAULICAS,
            descripcion='Descripción de prueba',
            imagen_referencia='r2://vitrina/productos/prueba.webp',
            imagen_alt='Bomba de prueba',
        )
        self.assertFalse(producto.visible)
        self.assertIsNotNone(producto.fecha_creacion)
        self.assertIsNotNone(producto.fecha_actualizacion)

    def test_orden_por_fecha_y_desempate_por_id_descendente(self):
        self.assertEqual(Producto._meta.ordering, ['-fecha_creacion', '-id'])
        momento = timezone.now()
        primero = Producto.objects.create(
            nombre='Primero', categoria=CategoriaProducto.TRANSMISION,
            descripcion='Descripción', imagen_referencia='r2://a',
            imagen_alt='Primero',
        )
        segundo = Producto.objects.create(
            nombre='Segundo', categoria=CategoriaProducto.TRANSMISION,
            descripcion='Descripción', imagen_referencia='r2://b',
            imagen_alt='Segundo',
        )
        Producto.objects.filter(pk__in=[primero.pk, segundo.pk]).update(fecha_creacion=momento)
        self.assertEqual(
            [p.pk for p in Producto.objects.all()],
            [segundo.pk, primero.pk],
        )

    def test_indice_de_vitrina_por_visibilidad_y_fecha(self):
        indices = {indice.name: indice for indice in Producto._meta.indexes}
        self.assertIn('producto_vitrina_idx', indices)
        self.assertEqual(
            list(indices['producto_vitrina_idx'].fields),
            ['visible', '-fecha_creacion', '-id'],
        )


def _imagen(lado=20, nombre='foto.png', formato='PNG'):
    """Archivo de imagen real para los multipart de la API."""
    buffer = io.BytesIO()
    Image.new('RGB', (lado, lado), 'red').save(buffer, format=formato)
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type='image/png')


def _archivo_corrupto(nombre='rota.png'):
    return SimpleUploadedFile(nombre, b'esto no es una imagen', content_type='image/png')


@override_settings(
    R2_ENABLED=False,
    VITRINA_IMAGENES_BASE_URL='',
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)
class ProductoAdminApiTest(TestCase):
    """Contrato de `/api/admin/productos/` (plan §4.2)."""

    def setUp(self):
        # Almacenamiento local aislado: no se escribe en el R2 configurado.
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)

        self.usuario = Usuario.objects.create_user(
            username='admin-vitrina', password='clave-segura',
        )
        self.api = APIClient()
        self.api.force_authenticate(self.usuario)
        self.url = reverse('admin-producto-list')

    def _detalle(self, producto):
        return reverse('admin-producto-detail', kwargs={'pk': producto.pk})

    def _archivos(self):
        return sorted(
            str(ruta) for ruta in Path(self.media).rglob('*') if ruta.is_file()
        )

    def _datos_post(self, **cambios):
        datos = {
            'nombre': 'Bomba de pistón',
            'categoria': 'bombas-hidraulicas',
            'descripcion': 'Descripción general aprobada.',
            'visible': 'true',
            'imagen': _imagen(),
            'imagen_alt': 'Bomba hidráulica de pistón.',
        }
        datos.update(cambios)
        return {clave: valor for clave, valor in datos.items() if valor is not None}

    def _producto(self, **cambios):
        datos = {
            'nombre': 'Bomba de prueba',
            'categoria': CategoriaProducto.BOMBAS_HIDRAULICAS,
            'descripcion': 'Descripción de prueba.',
            'imagen_referencia': '/media/vitrina/productos/vieja.webp',
            'imagen_alt': 'Bomba de prueba.',
            'visible': True,
        }
        datos.update(cambios)
        return Producto.objects.create(**datos)

    def _crear_por_api(self, **cambios):
        respuesta = self.api.post(
            self.url, self._datos_post(**cambios), format='multipart',
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        return respuesta

    # ── Autorización y CSRF ────────────────────────────────────

    def test_anonimo_es_rechazado_sin_crear_nada(self):
        anonimo = APIClient()
        self.assertEqual(anonimo.get(self.url).status_code, 401)
        respuesta = anonimo.post(self.url, self._datos_post(), format='multipart')
        self.assertEqual(respuesta.status_code, 401)
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])

    def test_inactivo_es_rechazado(self):
        self.usuario.is_active = False
        self.usuario.save(update_fields=['is_active'])
        self.assertEqual(self.api.get(self.url).status_code, 403)

    def test_no_administrativo_es_rechazado(self):
        self.usuario.rol = 'TECNICO'
        self.usuario.save(update_fields=['rol'])
        self.assertEqual(self.api.get(self.url).status_code, 403)

    def test_mutacion_sin_csrf_es_rechazada(self):
        cliente = APIClient(enforce_csrf_checks=True)
        cliente.force_authenticate(self.usuario)

        respuesta = cliente.post(
            self.url, self._datos_post(), format='multipart',
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(Producto.objects.count(), 0)

    def test_mutacion_con_csrf_es_aceptada(self):
        cliente = APIClient(enforce_csrf_checks=True)
        cliente.force_authenticate(self.usuario)
        token = cliente.get(reverse('csrf')).json()['csrfToken']

        respuesta = cliente.post(
            self.url, self._datos_post(),
            format='multipart', HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.assertEqual(Producto.objects.count(), 1)

    def test_borrado_sin_csrf_es_rechazado(self):
        producto = self._producto()
        cliente = APIClient(enforce_csrf_checks=True)
        cliente.force_authenticate(self.usuario)

        respuesta = cliente.delete(self._detalle(producto))
        self.assertEqual(respuesta.status_code, 403)
        producto.refresh_from_db()
        self.assertTrue(producto.visible)

    # ── GET ────────────────────────────────────────────────────

    def test_get_lista_visibles_y_ocultos_con_orden_administrativo(self):
        self._producto(nombre='Oculto', visible=False)
        antiguo = self._producto(nombre='Antiguo')
        momento = timezone.now()
        primero = self._producto(nombre='Primero')
        segundo = self._producto(nombre='Segundo')
        Producto.objects.filter(pk__in=[primero.pk, segundo.pk]).update(
            fecha_creacion=momento,
        )
        Producto.objects.filter(pk=antiguo.pk).update(
            fecha_creacion=momento - timezone.timedelta(days=1),
        )

        respuesta = self.api.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(set(datos), {'resultados'})
        self.assertEqual(
            [item['nombre'] for item in datos['resultados']],
            ['Segundo', 'Primero', 'Oculto', 'Antiguo'],
        )

    def test_get_devuelve_contrato_administrativo(self):
        producto = self._producto()

        item = self.api.get(self.url).json()['resultados'][0]
        self.assertEqual(
            set(item),
            {
                'id', 'nombre', 'categoria', 'descripcion', 'imagen',
                'visible', 'fecha_creacion', 'fecha_actualizacion',
            },
        )
        self.assertEqual(item['id'], producto.pk)
        self.assertEqual(
            item['categoria'],
            {'slug': 'bombas-hidraulicas', 'nombre': 'Bombas hidráulicas'},
        )
        self.assertEqual(
            item['imagen'],
            {
                'url': '/media/vitrina/productos/vieja.webp',
                'alt': 'Bomba de prueba.',
            },
        )
        self.assertTrue(item['visible'])
        self.assertIn('fecha_creacion', item)
        self.assertIn('fecha_actualizacion', item)

    # ── POST ───────────────────────────────────────────────────

    def test_post_crea_producto_y_procesa_la_imagen(self):
        respuesta = self._crear_por_api(imagen=_imagen(lado=2000))

        producto = Producto.objects.get()
        self.assertEqual(producto.nombre, 'Bomba de pistón')
        self.assertEqual(producto.categoria, 'bombas-hidraulicas')
        self.assertTrue(producto.visible)
        self.assertTrue(
            producto.imagen_referencia.startswith('/media/vitrina/productos/'),
        )
        self.assertTrue(producto.imagen_referencia.endswith('.webp'))
        self.assertEqual(respuesta.json()['id'], producto.pk)
        self.assertEqual(respuesta.json()['imagen']['alt'], producto.imagen_alt)

        ruta = Path(self.media) / producto.imagen_referencia[len('/media/'):]
        self.assertTrue(ruta.is_file())
        with Image.open(ruta) as guardada:
            self.assertEqual(guardada.format, 'WEBP')
            self.assertLessEqual(guardada.width, 1600)
            self.assertLessEqual(guardada.height, 1600)

    def test_post_exige_imagen_y_alt(self):
        respuesta = self.api.post(
            self.url, self._datos_post(imagen=None), format='multipart',
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('imagen', respuesta.json())
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])

    def test_post_con_imagen_invalida_no_guarda_nada(self):
        respuesta = self.api.post(
            self.url, self._datos_post(imagen=_archivo_corrupto()),
            format='multipart',
        )
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('imagen', respuesta.json())
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])

    def test_post_valida_campos_obligatorios_y_catalogo(self):
        casos = {
            'nombre': '',
            'nombre_solo_espacios': None,
            'descripcion': '',
            'imagen_alt': '',
            'categoria': 'no-existe',
        }
        for caso, valor in casos.items():
            with self.subTest(caso=caso):
                cambios = {
                    'nombre_solo_espacios': {'nombre': '   '},
                }.get(caso, {caso: valor})
                respuesta = self.api.post(
                    self.url, self._datos_post(**cambios), format='multipart',
                )
                self.assertEqual(respuesta.status_code, 400, respuesta.data)
                self.assertIn(caso.replace('_solo_espacios', ''), respuesta.json())
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])
    def test_post_ignora_fechas_y_referencias_del_cliente(self):
        respuesta = self.api.post(
            self.url,
            self._datos_post(
                imagen_referencia='https://malicioso.ejemplo/foto.webp',
                fecha_creacion='2000-01-01T00:00:00Z',
                fecha_actualizacion='2000-01-01T00:00:00Z',
            ),
            format='multipart',
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.data)

        producto = Producto.objects.get()
        self.assertTrue(
            producto.imagen_referencia.startswith('/media/vitrina/productos/'),
        )
        self.assertNotIn('malicioso', producto.imagen_referencia)
        self.assertEqual(producto.fecha_creacion.year, timezone.now().year)

    # ── PATCH ──────────────────────────────────────────────────

    def test_patch_campos_conserva_la_imagen_actual(self):
        producto = self._producto()
        referencia = producto.imagen_referencia

        respuesta = self.api.patch(
            self._detalle(producto),
            {'nombre': 'Nombre nuevo', 'visible': False},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 200)
        producto.refresh_from_db()
        self.assertEqual(producto.nombre, 'Nombre nuevo')
        self.assertFalse(producto.visible)
        self.assertEqual(producto.imagen_referencia, referencia)
        self.assertEqual(respuesta.json()['imagen']['url'], referencia)

    def test_patch_reemplaza_la_imagen_sin_borrar_la_anterior(self):
        creado = self._crear_por_api().json()
        producto = Producto.objects.get()
        referencia_anterior = producto.imagen_referencia

        respuesta = self.api.patch(
            self._detalle(producto),
            {
                'imagen': _imagen(lado=30, nombre='nueva.png'),
                'imagen_alt': 'Imagen nueva.',
            },
            format='multipart',
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        producto.refresh_from_db()
        self.assertNotEqual(producto.imagen_referencia, referencia_anterior)
        self.assertEqual(producto.imagen_alt, 'Imagen nueva.')
        self.assertEqual(respuesta.json()['id'], creado['id'])

        anterior = Path(self.media) / referencia_anterior[len('/media/'):]
        nueva = Path(self.media) / producto.imagen_referencia[len('/media/'):]
        self.assertTrue(anterior.is_file())
        self.assertTrue(nueva.is_file())

    def test_patch_con_imagen_invalida_conserva_la_actual(self):
        self._crear_por_api()
        producto = Producto.objects.get()
        referencia = producto.imagen_referencia

        respuesta = self.api.patch(
            self._detalle(producto),
            {'imagen': _archivo_corrupto()},
            format='multipart',
        )
        self.assertEqual(respuesta.status_code, 400)
        producto.refresh_from_db()
        self.assertEqual(producto.imagen_referencia, referencia)
        self.assertEqual(len(self._archivos()), 1)

    # ── DELETE ─────────────────────────────────────────────────

    def test_delete_oculta_y_conserva_fila_e_imagen(self):
        self._crear_por_api()
        producto = Producto.objects.get()
        referencia = producto.imagen_referencia

        respuesta = self.api.delete(self._detalle(producto))
        self.assertEqual(respuesta.status_code, 204)

        producto.refresh_from_db()
        self.assertFalse(producto.visible)
        self.assertTrue((Path(self.media) / referencia[len('/media/'):]).is_file())

        listado = self.api.get(self.url).json()['resultados']
        self.assertEqual([item['id'] for item in listado], [producto.pk])
        self.assertFalse(listado[0]['visible'])

    # ── Atomicidad ─────────────────────────────────────────────

    def test_fallo_de_almacenamiento_en_post_no_deja_fila_ni_archivo(self):
        with mock.patch(
            'servicios.views.guardar_imagen_vitrina',
            side_effect=ErrorDeAlmacenamiento('fallo del proveedor'),
        ):
            respuesta = self.api.post(
                self.url, self._datos_post(), format='multipart',
            )

        self.assertEqual(respuesta.status_code, 503)
        self.assertNotIn('proveedor', str(respuesta.json()))
        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])

    def test_fallo_de_almacenamiento_en_patch_conserva_la_imagen_actual(self):
        self._crear_por_api()
        producto = Producto.objects.get()
        referencia = producto.imagen_referencia

        with mock.patch(
            'servicios.views.guardar_imagen_vitrina',
            side_effect=ErrorDeAlmacenamiento('fallo del proveedor'),
        ):
            respuesta = self.api.patch(
                self._detalle(producto),
                {'imagen': _imagen(nombre='nueva.png')},
                format='multipart',
            )

        self.assertEqual(respuesta.status_code, 503)
        producto.refresh_from_db()
        self.assertEqual(producto.imagen_referencia, referencia)
        self.assertEqual(len(self._archivos()), 1)

    def test_fallo_de_base_de_datos_elimina_la_referencia_nueva(self):
        with mock.patch.object(
            ProductoAdminSerializer, 'create', side_effect=RuntimeError('db caída'),
        ):
            with self.assertRaises(RuntimeError):
                self.api.post(
                    self.url, self._datos_post(), format='multipart',
                )

        self.assertEqual(Producto.objects.count(), 0)
        self.assertEqual(self._archivos(), [])
