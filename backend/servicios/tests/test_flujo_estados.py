"""Pruebas puras del flujo de estados de la spec 008 (T3).

RF-FLU-04/05/06/07/08/09/10/11/13 y CL-03/06/09/10/11/16/22.
Estas pruebas no crean modelos: ``hoy`` es el snapshot que consume reglas.py.
"""

from django.apps import apps
from django.contrib.admin import site as admin_site
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from importlib import import_module

from servicios import reglas
from servicios.estados import EstadoComponente
from servicios.models import EstadoServicio
from servicios.models import Cliente, Componente, Cotizacion, EstadoCotizacion, HistorialComponente, HistorialServicio, MedioAprobacion, ResultadoAprobacion, Servicio
from servicios.acciones import ErrorDeAccion, cambiar_estado_componente, cancelar_servicio, crear_cotizacion, finalizar_servicio, registrar_aprobacion_externa, registrar_respuesta
from servicios.serializers import (
    CambiarEstadoComponenteInputSerializer,
    ComponenteAdministrativoSerializer,
    ServicioAdministrativoSerializer,
)
from servicios.admin import ComponenteInline, ServicioAdmin
from usuarios.models import Usuario

mapeo_flujo = import_module('servicios.migrations.0008_mapeo_datos_flujo')


def componente(id=1, estado=EstadoComponente.PENDIENTE):
    return {'id': id, 'estado': estado, 'trabajo_iniciado': False}


def cotizacion(estado='PENDIENTE', id=1):
    return {'id': id, 'es_bloqueante': True, 'estado': estado}


def snapshot(componentes=None, cotizaciones=None, estado=EstadoServicio.EN_CURSO,
             activo=True):
    componentes = componentes if componentes is not None else [componente()]
    cotizaciones = cotizaciones or {}
    return {
        'componentes': componentes,
        'cotizaciones_por_componente': cotizaciones,
        'cotizaciones': [c for lista in cotizaciones.values() for c in lista],
        'estado': estado,
        'activo': activo,
    }


class FlujoComponentePuroTest(SimpleTestCase):
    # RF-FLU-04/07/08; la tabla §4.1 es la fuente única de destinos manuales.
    def test_tabla_de_destinos_manuales_por_estado(self):
        esperados = {
            'PENDIENTE': ['EN_REVISION'],
            'EN_REVISION': ['COTIZANDO'],
            'COTIZANDO': [],
            'ESPERANDO_APROBACION': ['RECHAZADO'],
            'OPERARIO_TRABAJANDO': ['EN_PRUEBAS'],
            'EN_PRUEBAS': ['LISTO_PARA_ENTREGA'],
            'LISTO_PARA_ENTREGA': ['EN_PRUEBAS'],
            'RECHAZADO': ['ESPERANDO_APROBACION'],
        }
        for origen, destinos in esperados.items():
            actual = reglas.estados_componente_seleccionables(
                snapshot(componentes=[componente(estado=origen)]),
                componente(estado=origen),
            )
            self.assertEqual(actual, destinos)

    def test_no_ofrece_destinos_automaticos(self):
        for estado in ('COTIZANDO', 'OPERARIO_TRABAJANDO', 'EN_PRUEBAS',
                       'LISTO_PARA_ENTREGA'):
            destinos = reglas.estados_componente_seleccionables(
                snapshot(componentes=[componente(estado=estado)]),
                componente(estado=estado),
            )
            self.assertNotIn('ESPERANDO_APROBACION', destinos)
            self.assertNotIn('OPERARIO_TRABAJANDO', destinos)

    def test_motivo_vacio_en_finalizacion_y_comentario_en_correccion(self):
        self.assertTrue(reglas.requiere_motivo('LISTO_PARA_ENTREGA'))
        self.assertTrue(reglas.requiere_motivo('RECHAZADO'))
        self.assertFalse(reglas.requiere_motivo('EN_PRUEBAS'))
        dato = componente(estado='EN_PRUEBAS')
        estado = snapshot(componentes=[dato])
        for destino in ('LISTO_PARA_ENTREGA',):
            self.assertEqual(reglas.resolver_transicion_componente(
                estado, dato, destino, '   '
            )['codigo'], 400)
        corregido = componente(estado='LISTO_PARA_ENTREGA')
        self.assertEqual(reglas.resolver_transicion_componente(
            snapshot(componentes=[corregido]), corregido, 'EN_PRUEBAS', ''
        )['codigo'], 400)

    def test_rechazado_exige_cotizacion_rechazada(self):
        dato = componente(estado='ESPERANDO_APROBACION')
        decision = reglas.resolver_transicion_componente(
            snapshot(componentes=[dato]), dato, 'RECHAZADO', 'cliente no aprobó'
        )
        self.assertEqual(decision['codigo'], 409)
        estado = snapshot(
            componentes=[dato],
            cotizaciones={1: [cotizacion('RECHAZADA')]},
        )
        self.assertTrue(reglas.resolver_transicion_componente(
            estado, dato, 'RECHAZADO', 'sin aprobación'
        )['permitido'])

    def test_noop_e_invalida(self):
        dato = componente(estado='EN_REVISION')
        noop = reglas.resolver_transicion_componente(
            snapshot(componentes=[dato]), dato, 'EN_REVISION'
        )
        self.assertEqual((noop['permitido'], noop['tipo']), (True, 'noop'))
        invalida = reglas.resolver_transicion_componente(
            snapshot(componentes=[dato]), dato, 'OPERARIO_TRABAJANDO'
        )
        self.assertEqual(invalida['codigo'], 409)  # CL-03

    # RF-FLU-06 / CL-06: rechazo no mueve el componente.
    def test_respuesta_aprobada_y_rechazada(self):
        dato = componente(estado='ESPERANDO_APROBACION')
        estado = snapshot(componentes=[dato])
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'OPERARIO_TRABAJANDO'
        ), 'OPERARIO_TRABAJANDO')
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'LISTO_PARA_ENTREGA'
        ), 'EN_PRUEBAS')
        self.assertIsNone(reglas.transicion_por_respuesta(
            estado, dato, 'RECHAZADA', 'OPERARIO_TRABAJANDO'
        ))

    def test_cotizacion_desde_los_cuatro_origenes(self):
        for origen in ('COTIZANDO', 'OPERARIO_TRABAJANDO', 'EN_PRUEBAS',
                       'LISTO_PARA_ENTREGA'):
            dato = componente(estado=origen)
            self.assertEqual(reglas.transicion_por_cotizacion(
                snapshot(componentes=[dato]), dato
            ), 'ESPERANDO_APROBACION')
        dato = componente(estado='PENDIENTE')
        self.assertIsNone(reglas.transicion_por_cotizacion(
            snapshot(componentes=[dato]), dato
        ))


class FlujoServicioPuroTest(SimpleTestCase):
    # RF-FLU-03: salir de pendiente es cualquier primer estado distinto.
    def test_es_cambio_fuera_de_pendiente(self):
        self.assertTrue(reglas.es_cambio_fuera_de_pendiente(
            componente(estado='PENDIENTE'), componente(estado='EN_REVISION')
        ))
        self.assertFalse(reglas.es_cambio_fuera_de_pendiente(
            componente(estado='PENDIENTE'), componente(estado='PENDIENTE')
        ))

    # RF-FLU-09 / CL-10/11: únicamente componentes cerrados permiten cierre.
    def test_cierre_con_en_pruebas_y_sin_componentes(self):
        en_pruebas = snapshot(componentes=[componente(estado='EN_PRUEBAS')])
        self.assertFalse(reglas.puede_finalizar_servicio(en_pruebas))
        self.assertEqual(reglas.resumen_cierre(en_pruebas)['impeditivos'], [1])
        vacio = snapshot(componentes=[])
        self.assertFalse(reglas.puede_finalizar_servicio(vacio))
        self.assertEqual(reglas.resumen_cierre(vacio)['caso'], 'SIN_COMPONENTES')

    def test_cierre_con_todos_finalizados_y_selector_servicio_vacio(self):
        estado = snapshot(componentes=[
            componente(1, 'LISTO_PARA_ENTREGA'), componente(2, 'RECHAZADO')
        ])
        self.assertEqual(reglas.componentes_no_finalizados(estado), [])
        self.assertTrue(reglas.puede_finalizar_servicio(estado))
        self.assertEqual(reglas.estados_servicio_seleccionables(estado), [])

    def test_cancelacion_y_estados_cerrados(self):
        self.assertTrue(reglas.puede_cancelar_servicio(
            snapshot(estado=EstadoServicio.SOLICITADO)
        ))
        self.assertFalse(reglas.puede_cancelar_servicio(
            snapshot(estado=EstadoServicio.FINALIZADO)
        ))
        self.assertEqual(reglas.estados_cerrados(), (
            EstadoServicio.FINALIZADO, EstadoServicio.CANCELADO
        ))


class FlujoAccionesTest(TestCase):
    """RF-FLU-03/05/06/07/08/09/10/12/13: efectos persistentes."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente')
        self.servicio = Servicio.objects.create(cliente=self.cliente, descripcion_solicitud='Prueba')
        self.componente = Componente.objects.create(servicio=self.servicio, tipo='Bomba')

    def cotizar(self, estado=EstadoComponente.COTIZANDO):
        self.componente.estado = estado
        self.componente.save(update_fields=['estado'])
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, estado)
        return crear_cotizacion(datos={'servicio': self.servicio, 'componente': self.componente,
                                       'descripcion': 'Trabajo', 'total': 100}, usuario=None)

    def test_primer_cambio_arrastra_servicio_y_deja_dos_historiales(self):
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.EN_REVISION)
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.EN_CURSO)
        self.assertEqual(HistorialComponente.objects.count(), 1)
        self.assertEqual(HistorialServicio.objects.filter(estado=EstadoServicio.EN_CURSO).count(), 1)

    def test_cotizacion_mueve_los_cuatro_origenes_y_conserva_datos(self):
        for estado in ('COTIZANDO', 'OPERARIO_TRABAJANDO', 'EN_PRUEBAS', 'LISTO_PARA_ENTREGA'):
            componente = self.componente if estado == 'COTIZANDO' else Componente.objects.create(servicio=self.servicio, tipo=estado, estado=estado, fase='EN_EJECUCION')
            if estado == 'COTIZANDO':
                componente.estado = estado
                componente.save(update_fields=['estado'])
            fase = componente.fase
            cotizacion = crear_cotizacion(datos={'servicio': self.servicio, 'componente': componente,
                                                  'descripcion': 'Adicional', 'total': 1}, usuario=None)
            componente.refresh_from_db()
            self.assertEqual(componente.estado, EstadoComponente.ESPERANDO_APROBACION, estado)
            self.assertEqual(componente.fase, fase)
            self.assertEqual(cotizacion.componente_id, componente.pk)

    def test_aprobacion_y_rechazo_no_mueven_rechazo(self):
        cotizacion = self.cotizar()
        registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                            cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                            canal=MedioAprobacion.WEB)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.OPERARIO_TRABAJANDO)
        cotizacion = self.cotizar(EstadoComponente.EN_PRUEBAS)
        registrar_aprobacion_externa(cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.RECHAZADA,
                                     medio=MedioAprobacion.WHATSAPP, usuario=None)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.ESPERANDO_APROBACION)
        self.assertEqual(Cotizacion.objects.get(pk=cotizacion.pk).estado, EstadoCotizacion.RECHAZADA)

    def test_finalizacion_correccion_y_cierre(self):
        self.componente.estado = EstadoComponente.EN_PRUEBAS
        self.componente.save(update_fields=['estado'])
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.LISTO_PARA_ENTREGA, comentario='Pruebas OK')
        self.componente.refresh_from_db()
        self.assertTrue(self.componente.fecha_finalizacion)
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.EN_PRUEBAS, comentario='Error de registro')
        self.componente.refresh_from_db()
        self.assertIsNone(self.componente.fecha_finalizacion)
        self.assertEqual(HistorialComponente.objects.count(), 2)
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.LISTO_PARA_ENTREGA, comentario='OK')
        finalizar_servicio(servicio=self.servicio, comentario='Servicio terminado')
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.FINALIZADO)
        self.assertEqual(HistorialServicio.objects.filter(estado=EstadoServicio.FINALIZADO).count(), 1)

    def test_rechazado_exige_cotizacion_rechazada_y_cancelar_no_toca_componente(self):
        cotizacion = self.cotizar()
        registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                            cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.RECHAZADA,
                            canal=MedioAprobacion.WEB)
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.RECHAZADO, comentario='No aprobado')
        cancelar_servicio(servicio=self.servicio, comentario='Cancelación administrativa')
        self.componente.refresh_from_db()
        self.servicio.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.RECHAZADO)
        self.assertEqual(self.servicio.estado, EstadoServicio.CANCELADO)

    def test_respuesta_repetida_igual_es_noop_y_contradictoria_es_409(self):
        cotizacion = self.cotizar()
        primera = registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                                      cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                                      canal=MedioAprobacion.WEB)
        segunda = registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                                      cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                                      canal=MedioAprobacion.WEB)
        self.assertEqual(primera.pk, segunda.pk)
        with self.assertRaises(ErrorDeAccion) as error:
            registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                                cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.RECHAZADA,
                                canal=MedioAprobacion.WEB)
        self.assertEqual(error.exception.codigo, 409)


class FlujoContratosApiTest(TestCase):
    """RF-FLU-01/02/09/10/14/15: contratos de la superficie nueva."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de contratos')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente, descripcion_solicitud='Contrato',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio, tipo='Bomba',
        )

    def test_detalle_administrativo_expone_solo_acciones_nuevas(self):
        datos_componente = ComponenteAdministrativoSerializer(self.componente).data
        self.assertEqual(datos_componente['estados_seleccionables'], ['EN_REVISION'])
        self.assertNotIn('motivo_bloqueo', datos_componente)
        self.assertNotIn('iniciar_trabajo', datos_componente['acciones_disponibles'])
        datos_servicio = ServicioAdministrativoSerializer(self.servicio).data
        self.assertNotIn('estados_seleccionables', datos_servicio)
        self.assertEqual(datos_servicio['acciones_disponibles'], ['cancelar_servicio'])

    def test_entrada_componente_usa_catalogo_nuevo_y_comentario(self):
        serializer = CambiarEstadoComponenteInputSerializer(data={
            'estado': 'EN_REVISION', 'comentario': 'Llegó el repuesto',
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        invalido = CambiarEstadoComponenteInputSerializer(data={'estado': 'INVENTADO'})
        self.assertFalse(invalido.is_valid())


class FlujoEndpointsYPermisosTest(TestCase):
    """Contrato HTTP, permisos y seguimiento.

    RF-FLU-06 / CL-05/06/07: ``test_aprobacion_publica_por_token...`` cubre
    aprobación pública, rechazo no bloqueante e idempotencia en las acciones.
    RF-FLU-09 / CL-10/11/12: el cierre se valida en la suite de acciones y en
    el contrato de la vista; RF-FLU-14 / CL-21: este módulo prueba la única
    excepción de permiso (respuesta con token) y el rechazo sin autenticación.
    RF-FLU-15: la consulta de un servicio cancelado devuelve 404.
    """

    def setUp(self):
        self.usuario = Usuario.objects.create_user(username='admin-flujo')
        self.cliente = Cliente.objects.create(nombre='Cliente API')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente, descripcion_solicitud='Solicitud API'
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio, tipo='Bomba'
        )
        self.api = APIClient()
        self.api.force_authenticate(self.usuario)

    def test_cambiar_componente_y_arrastre_via_http(self):
        respuesta = self.api.post(
            reverse('componente-cambiar-estado', kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': self.componente.pk,
            }),
            {'estado': EstadoComponente.EN_REVISION}, format='json',
        )
        self.assertEqual(respuesta.status_code, 200)
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.EN_CURSO)

    def test_cancelacion_exige_comentario_y_excluye_seguimiento(self):
        url = reverse('servicio-cancelar', kwargs={'servicio_pk': self.servicio.pk})
        self.assertEqual(self.api.post(url, {}, format='json').status_code, 400)
        respuesta = self.api.post(url, {'comentario': 'No continúa'}, format='json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            self.api.get(reverse('seguimiento', kwargs={
                'token': self.servicio.token_seguimiento,
            })).status_code,
            404,
        )

    def test_permisos_y_dashboard_solo_muestran_catalogo_nuevo(self):
        self.api.force_authenticate(user=None)
        self.assertIn(
            self.api.get(reverse('admin-dashboard')).status_code, (401, 403)
        )
        self.api.force_authenticate(self.usuario)
        respuesta = self.api.get(reverse('admin-dashboard'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            set(respuesta.data['contadores']),
            set(EstadoServicio.values),
        )

    def test_aprobacion_publica_por_token_es_la_excepcion_de_permiso(self):
        self.componente.estado = EstadoComponente.COTIZANDO
        self.componente.save(update_fields=['estado'])
        cotizacion = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': self.componente,
            'descripcion': 'Trabajo', 'total': 100,
        }, usuario=None)
        self.api.force_authenticate(user=None)
        respuesta = self.api.post(
            reverse('seguimiento-aprobar', kwargs={
                'token': self.servicio.token_seguimiento,
            }),
            {'resultado': ResultadoAprobacion.APROBADA}, format='json',
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['cotizacion'], cotizacion.pk)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.OPERARIO_TRABAJANDO)


class FlujoAdminYMigracionTest(TestCase):
    """Admin alineado y migración segura en BD nueva.

    RF-FLU-08 / CL-09: la suite de acciones cubre la finalización manual como
    ``RECHAZADO`` con motivo, fecha y cotización rechazada; este bloque verifica
    que el admin expone el catálogo nuevo sin abrir una vía paralela.
    RF-FLU-12: los cambios y sus actores se comprueban en ``FlujoAccionesTest``.
    RF-FLU-16 / CL-18/19/20: se ejecuta el RunPython sobre una BD de pruebas
    vacía y se comprueban sus tablas de mapeo sin modificar datos reales.
    """

    def test_admin_no_ofrece_estado_editable_y_muestra_motivo_espera(self):
        self.assertIn('estado', ComponenteInline.readonly_fields)
        self.assertIn('motivo_espera', ComponenteInline.fields)
        admin_servicio = admin_site._registry[Servicio]
        self.assertIsInstance(admin_servicio, ServicioAdmin)
        self.assertIn('estado', admin_servicio.readonly_fields)

    def test_mapeo_de_datos_se_ejecuta_sin_inventar_datos_en_bd_nueva(self):
        # RF-FLU-16 / CL-18/19/20: la prueba usa la BD de test recién creada.
        # Ejecutar el RunPython aquí es seguro: no hay filas legacy que mutar.
        mapeo_flujo.mapear_estados(apps, None)
        self.assertEqual(mapeo_flujo.MAPEO_ESTADO_SERVICIO['NO_APROBADO'], 'CANCELADO')
        self.assertEqual(
            mapeo_flujo.MAPEO_ESTADO_COMPONENTE['FINALIZADO_POR_TECNICO'],
            'LISTO_PARA_ENTREGA',
        )
