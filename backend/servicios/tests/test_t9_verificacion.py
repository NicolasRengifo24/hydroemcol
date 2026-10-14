"""Verificación de cierre de la Spec 005 (T9).

La suite usa únicamente TestCase de Django y el cliente de pruebas de DRF para
ejercitar los contratos HTTP existentes; no añade dependencias de test.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from servicios.acciones import ErrorDeAccion, crear_fotografia, guardar_registro_tecnico
from servicios.estados import CanalRespuesta, EstadoComponente
from servicios.models import (
    AprobacionServicio, Cliente, Componente, Cotizacion, EstadoCotizacion,
    EstadoServicio, Fotografia, RegistroTecnico, Servicio,
)
from usuarios.models import Usuario


class BaseT9(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create_user(username='admin-t9', password='x')
        self.otro_rol = Usuario.objects.create_user(
            username='otro-t9', password='x', rol='OTRO'
        )
        self.cliente = Cliente.objects.create(
            nombre='José Álvarez', empresa='Bombas Únicas', email='jose@example.com'
        )
        self.servicio = Servicio.objects.create(
            cliente=self.cliente, descripcion_solicitud='Diagnóstico'
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio, tipo='Bomba'
        )

    def autenticar(self, usuario=None):
        self.client.force_authenticate(user=usuario or self.admin)

    def cotizacion(self, estado=EstadoCotizacion.PENDIENTE, bloqueante=True):
        return Cotizacion.objects.create(
            servicio=self.servicio, componente=self.componente,
            estado=estado, es_bloqueante=bloqueante, descripcion='Trabajo',
        )


class PermisosYConsultasT9(BaseT9):
    def test_rutas_administrativas_exigen_rol_activo(self):
        for usuario in (None, self.otro_rol):
            self.client.force_authenticate(user=usuario)
            respuesta = self.client.get('/api/admin/dashboard/')
            self.assertIn(respuesta.status_code, (401, 403))
        self.admin.is_active = False
        self.admin.save(update_fields=['is_active'])
        self.autenticar(self.admin)
        self.assertIn(self.client.get('/api/admin/dashboard/').status_code, (401, 403))

    def test_dashboard_solo_activos_recientes_y_pendientes(self):
        self.autenticar()
        Servicio.objects.filter(pk=self.servicio.pk).update(activo=False)
        for indice in range(11):
            cliente = Cliente.objects.create(nombre=f'Cliente {indice}')
            Servicio.objects.create(
                cliente=cliente, descripcion_solicitud='Solicitud',
                estado=EstadoServicio.SOLICITADO if indice == 0 else EstadoServicio.COTIZANDO,
            )
        respuesta = self.client.get('/api/admin/dashboard/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['total_activos'], 11)
        self.assertEqual(len(respuesta.data['recientes']), 10)
        self.assertEqual(len(respuesta.data['pendientes_atencion']), 1)
        self.assertNotIn(self.servicio.codigo, str(respuesta.data))

    def test_busqueda_sin_tildes_filtro_orden_y_paginacion_de_20(self):
        self.autenticar()
        for indice in range(21):
            cliente = Cliente.objects.create(nombre=f'Cliente {indice}')
            Servicio.objects.create(
                cliente=cliente, descripcion_solicitud='Solicitud',
                estado=EstadoServicio.EN_REVISION,
            )
        respuesta = self.client.get(
            '/api/servicios/?search=jose&estado=SOLICITADO&ordering=-codigo&page=1'
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['count'], 1)
        self.assertEqual(respuesta.data['results'][0]['cliente']['nombre'], 'José Álvarez')
        respuesta = self.client.get('/api/servicios/?estado=EN_REVISION&page=1')
        self.assertEqual(respuesta.data['page_size'], 20)
        self.assertEqual(len(respuesta.data['results']), 20)

    def test_detalle_no_mezcla_relaciones_de_otro_servicio(self):
        self.autenticar()
        otro = Servicio.objects.create(
            cliente=Cliente.objects.create(nombre='Otro'), descripcion_solicitud='Otro'
        )
        Componente.objects.create(servicio=otro, tipo='Válvula')
        respuesta = self.client.get(f'/api/servicios/{self.servicio.pk}/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual([c['id'] for c in respuesta.data['componentes']], [self.componente.pk])
        self.assertNotIn(otro.pk, [c['servicio'] for c in respuesta.data['componentes']])
        self.assertNotIn('token_seguimiento', respuesta.data)

    def test_desactivar_servicio_requiere_rol_y_conserva_datos_fuera_de_operacion(self):
        self.client.force_authenticate(user=None)
        respuesta = self.client.post(f'/api/servicios/{self.servicio.pk}/desactivar/')
        self.assertIn(respuesta.status_code, (401, 403))

        self.autenticar(self.otro_rol)
        self.assertIn(
            self.client.post(f'/api/servicios/{self.servicio.pk}/desactivar/').status_code,
            (401, 403),
        )

        self.autenticar()
        self.servicio.observaciones_internas = 'Conservar evidencia'
        self.servicio.save(update_fields=['observaciones_internas'])
        respuesta = self.client.post(f'/api/servicios/{self.servicio.pk}/desactivar/')
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.servicio.refresh_from_db()
        self.assertFalse(self.servicio.activo)
        self.assertEqual(self.servicio.observaciones_internas, 'Conservar evidencia')
        self.assertTrue(self.servicio.componentes.exists())
        self.assertTrue(self.servicio.historial.exists())
        self.assertNotIn(self.servicio.codigo, str(self.client.get('/api/admin/dashboard/').data))
        self.assertNotIn(self.servicio.codigo, str(self.client.get('/api/servicios/').data))
        self.assertEqual(
            self.client.get(f'/api/seguimiento/{self.servicio.token_seguimiento}/').status_code,
            404,
        )


class CotizacionesYAccionesT9(BaseT9):
    def test_modelos_versionado_y_edicion_solo_pendiente(self):
        self.autenticar()
        pendiente = self.cotizacion()
        respuesta = self.client.patch(
            f'/api/cotizaciones/{pendiente.pk}/', {'descripcion': 'Editada'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 200)
        aprobada = self.cotizacion(EstadoCotizacion.APROBADA)
        respuesta = self.client.patch(
            f'/api/cotizaciones/{aprobada.pk}/', {'descripcion': 'No'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(Cotizacion._meta.get_field('reemplaza_a').remote_field.model, Cotizacion)

    def test_reenvio_nueva_version_sin_copiar_aprobaciones(self):
        self.autenticar()
        anterior = self.cotizacion(EstadoCotizacion.RECHAZADA)
        AprobacionServicio.objects.create(
            cotizacion=anterior, resultado=EstadoCotizacion.RECHAZADA,
            medio=CanalRespuesta.WHATSAPP, fecha=timezone.now(), usuario_registro=self.admin,
        )
        respuesta = self.client.post(
            f'/api/cotizaciones/{anterior.pk}/reenviar/',
            {'descripcion': 'Nueva versión', 'detalles': []}, format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        nueva = Cotizacion.objects.get(pk=respuesta.data['id'])
        self.assertEqual(nueva.reemplaza_a_id, anterior.pk)
        self.assertEqual(nueva.estado, EstadoCotizacion.PENDIENTE)
        self.assertEqual(nueva.aprobaciones.count(), 0)
        anterior.refresh_from_db()
        self.assertEqual(anterior.estado, EstadoCotizacion.RECHAZADA)

    def test_acciones_bloqueantes_y_no_bloqueantes(self):
        self.autenticar()
        bloqueante = self.cotizacion(bloqueante=True)
        respuesta = self.client.post(
            f'/api/servicios/{self.servicio.pk}/componentes/{self.componente.pk}/iniciar-trabajo/'
        )
        self.assertEqual(respuesta.status_code, 409, respuesta.data)
        bloqueante.delete()
        self.cotizacion(bloqueante=False)
        respuesta = self.client.post(
            f'/api/servicios/{self.servicio.pk}/componentes/{self.componente.pk}/iniciar-trabajo/'
        )
        self.assertEqual(respuesta.status_code, 200)

    def test_conflicto_no_sobrescribe_cotizacion_respondida(self):
        self.autenticar()
        cotizacion = self.cotizacion()
        self.client.post(
            f'/api/cotizaciones/{cotizacion.pk}/aprobaciones/',
            {'resultado': 'RECHAZADA', 'medio': 'WHATSAPP'}, format='json'
        )
        respuesta = self.client.patch(
            f'/api/cotizaciones/{cotizacion.pk}/', {'descripcion': 'Sobrescrita'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 409)
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.descripcion, 'Trabajo')
        self.assertEqual(cotizacion.aprobaciones.count(), 1)


class TecnicoYFotografiasT9(BaseT9):
    def test_registro_tecnico_opcional_autoria_actualizacion_y_privacidad(self):
        self.autenticar()
        self.assertFalse(RegistroTecnico.objects.exists())
        respuesta = self.client.post(
            f'/api/servicios/{self.servicio.pk}/registro-tecnico/',
            {'diagnostico': 'Fuga'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 201)
        registro = RegistroTecnico.objects.get(servicio=self.servicio)
        self.assertEqual(registro.creado_por, self.admin)
        self.client.patch(
            f'/api/servicios/{self.servicio.pk}/registro-tecnico/',
            {'resultado_pruebas': 'Correcto'}, format='json'
        )
        registro.refresh_from_db()
        self.assertEqual(registro.actualizado_por, self.admin)
        publica = self.client.get(f'/api/seguimiento/{self.servicio.token_seguimiento}/')
        self.assertEqual(publica.status_code, 200)
        self.assertNotIn('diagnostico', publica.data)

    def test_maximo_diez_fotos_visibilidad_borrado_y_fallo_de_almacenamiento(self):
        self.autenticar()
        for indice in range(10):
            Fotografia.objects.create(
                servicio=self.servicio, url=f'https://files.example.com/{indice}.jpg',
                tipo='OTRO', visible_cliente=(indice == 0), subida_por=self.admin,
            )
        respuesta = self.client.post(
            f'/api/servicios/{self.servicio.pk}/fotografias/',
            {'url': 'https://files.example.com/11.jpg', 'tipo': 'OTRO'}, format='json'
        )
        self.assertEqual(respuesta.status_code, 409, respuesta.data)
        self.assertEqual(self.servicio.fotografias.count(), 10)
        publica = self.client.get(f'/api/seguimiento/{self.servicio.token_seguimiento}/')
        self.assertEqual(len(publica.data['fotografias']), 1)
        foto = self.servicio.fotografias.first()
        with patch('servicios.almacenamiento.eliminar_referencia', side_effect=OSError('fallo')):
            respuesta = self.client.delete(
                f'/api/servicios/{self.servicio.pk}/fotografias/{foto.pk}/'
            )
        self.assertEqual(respuesta.status_code, 409)
        self.assertTrue(Fotografia.objects.filter(pk=foto.pk).exists())
