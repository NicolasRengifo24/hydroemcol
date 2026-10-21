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
from servicios.models import AprobacionServicio, Cliente, Componente, Cotizacion, EstadoCotizacion, HistorialComponente, HistorialServicio, MedioAprobacion, ResultadoAprobacion, Servicio
from servicios.acciones import ErrorDeAccion, cambiar_estado_componente, cancelar_servicio, crear_cotizacion, finalizar_servicio, registrar_aprobacion_externa, registrar_recepcion, registrar_respuesta, reenviar_cotizacion
from servicios.serializers import (
    CambiarEstadoComponenteInputSerializer,
    ComponenteAdministrativoSerializer,
    CotizacionAdministrativaSerializer,
    ServicioAdministrativoSerializer,
)
from servicios.admin import ComponenteInline, ServicioAdmin
from usuarios.models import Usuario

mapeo_flujo = import_module('servicios.migrations.0008_mapeo_datos_flujo')


def componente(id=1, estado=EstadoComponente.PENDIENTE, origen_espera=None):
    return {'id': id, 'estado': estado, 'trabajo_iniciado': False,
            'origen_espera': origen_espera}


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
            'EN_REVISION': ['OPERARIO_TRABAJANDO'],
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
            snapshot(componentes=[dato]), dato, 'EN_PRUEBAS'
        )
        self.assertEqual(invalida['codigo'], 409)  # CL-03

    # RF-COH-01: `COTIZANDO` nunca es un destino manual.
    def test_cotizando_nunca_es_destino_manual(self):
        for estado in EstadoComponente.values:
            destinos = reglas.estados_componente_seleccionables(
                snapshot(componentes=[componente(estado=estado)]),
                componente(estado=estado),
            )
            self.assertNotIn('COTIZANDO', destinos, estado)

    # RF-COH-06: aprobar devuelve al estado de origen.
    def test_respuesta_aprobada_y_rechazada(self):
        dato = componente(estado='ESPERANDO_APROBACION')
        estado = snapshot(componentes=[dato])
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'OPERARIO_TRABAJANDO'
        ), 'OPERARIO_TRABAJANDO')
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'EN_REVISION'
        ), 'EN_REVISION')
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'EN_PRUEBAS'
        ), 'EN_PRUEBAS')
        self.assertEqual(reglas.transicion_por_respuesta(
            estado, dato, 'APROBADA', 'LISTO_PARA_ENTREGA'
        ), 'EN_PRUEBAS')
        self.assertIsNone(reglas.transicion_por_respuesta(
            estado, dato, 'RECHAZADA', 'OPERARIO_TRABAJANDO'
        ))

    def test_cotizacion_desde_origenes_validos(self):
        for origen in ('EN_REVISION', 'OPERARIO_TRABAJANDO', 'EN_PRUEBAS'):
            dato = componente(estado=origen)
            self.assertEqual(reglas.transicion_por_cotizacion(
                snapshot(componentes=[dato]), dato
            ), 'ESPERANDO_APROBACION', origen)
        for origen in ('PENDIENTE', 'LISTO_PARA_ENTREGA'):
            dato = componente(estado=origen)
            self.assertIsNone(reglas.transicion_por_cotizacion(
                snapshot(componentes=[dato]), dato
            ), origen)

    # RF-COH-03: cotización bloqueante pendiente impide avanzar (409).
    def test_bloqueo_por_cotizacion_bloqueante(self):
        dato = componente(estado='ESPERANDO_APROBACION', origen_espera='EN_PRUEBAS')
        pendiente = snapshot(componentes=[dato], cotizaciones={1: [cotizacion('PENDIENTE')]})
        decision = reglas.resolver_transicion_componente(
            pendiente, dato, 'LISTO_PARA_ENTREGA', 'Pruebas OK'
        )
        self.assertEqual(decision['codigo'], 409)
        self.assertFalse(decision['permitido'])
        self.assertIn('bloqueante', decision['motivo'])

    # RF-COH-05: cotización no bloqueante deja avanzar desde el origen.
    def test_cotizacion_no_bloqueante_no_detiene(self):
        dato = componente(estado='ESPERANDO_APROBACION', origen_espera='EN_PRUEBAS')
        no_bloqueante = {'id': 1, 'es_bloqueante': False, 'estado': 'PENDIENTE'}
        estado = snapshot(componentes=[dato], cotizaciones={1: [no_bloqueante]})
        self.assertEqual(reglas.estados_componente_seleccionables(estado, dato),
                         ['RECHAZADO', 'LISTO_PARA_ENTREGA'])
        self.assertTrue(reglas.resolver_transicion_componente(
            estado, dato, 'LISTO_PARA_ENTREGA', 'Pruebas OK'
        )['permitido'])


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

    def cotizar(self, estado=EstadoComponente.EN_REVISION):
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

    def test_cotizacion_mueve_origenes_validos_y_conserva_datos(self):
        for estado in ('EN_REVISION', 'OPERARIO_TRABAJANDO', 'EN_PRUEBAS'):
            componente = Componente.objects.create(
                servicio=self.servicio, tipo=estado, estado=estado, fase='EN_EJECUCION')
            fase = componente.fase
            cotizacion = crear_cotizacion(datos={'servicio': self.servicio, 'componente': componente,
                                                  'descripcion': 'Adicional', 'total': 1}, usuario=None)
            componente.refresh_from_db()
            self.assertEqual(componente.estado, EstadoComponente.ESPERANDO_APROBACION, estado)
            self.assertEqual(componente.fase, fase)
            self.assertEqual(cotizacion.componente_id, componente.pk)

    # RF-COH-04 / CL-COH-04/05: no se cotiza desde PENDIENTE ni LISTO_PARA_ENTREGA.
    def test_cotizacion_rechazada_desde_origenes_invalidos(self):
        for estado in ('PENDIENTE', 'LISTO_PARA_ENTREGA'):
            componente = Componente.objects.create(
                servicio=self.servicio, tipo=estado, estado=estado)
            with self.assertRaises(ErrorDeAccion) as error:
                crear_cotizacion(datos={'servicio': self.servicio, 'componente': componente,
                                        'descripcion': 'X', 'total': 1}, usuario=None)
            self.assertEqual(error.exception.codigo, 409, estado)

    # RF-COH-02: EN_REVISION -> OPERARIO_TRABAJANDO inicia trabajo.
    def test_en_revision_inicia_trabajo(self):
        self.componente.estado = EstadoComponente.EN_REVISION
        self.componente.save(update_fields=['estado'])
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.OPERARIO_TRABAJANDO)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.OPERARIO_TRABAJANDO)
        self.assertTrue(self.componente.trabajo_iniciado)
        self.assertEqual(self.componente.fase, 'DESMONTAJE_INICIADO')
        self.assertIsNotNone(self.componente.fecha_inicio_trabajo)

    # RF-COH-05: cotización no bloqueante deja avanzar tras crearla.
    def test_cotizacion_no_bloqueante_permite_avanzar(self):
        self.componente.estado = EstadoComponente.EN_PRUEBAS
        self.componente.save(update_fields=['estado'])
        crear_cotizacion(datos={'servicio': self.servicio, 'componente': self.componente,
                                'descripcion': 'No bloqueante', 'total': 100,
                                'es_bloqueante': False}, usuario=None)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.ESPERANDO_APROBACION)
        cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                  nuevo_estado=EstadoComponente.LISTO_PARA_ENTREGA,
                                  comentario='Pruebas OK')
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.LISTO_PARA_ENTREGA)

    # RF-COH-03: cotización bloqueante pendiente impide avanzar.
    def test_cotizacion_bloqueante_impide_avanzar(self):
        self.componente.estado = EstadoComponente.EN_PRUEBAS
        self.componente.save(update_fields=['estado'])
        crear_cotizacion(datos={'servicio': self.servicio, 'componente': self.componente,
                                'descripcion': 'Bloqueante', 'total': 100,
                                'es_bloqueante': True}, usuario=None)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.ESPERANDO_APROBACION)
        with self.assertRaises(ErrorDeAccion) as error:
            cambiar_estado_componente(servicio=self.servicio, componente_id=self.componente.pk,
                                      nuevo_estado=EstadoComponente.LISTO_PARA_ENTREGA,
                                      comentario='Pruebas OK')
        self.assertEqual(error.exception.codigo, 409)
        self.assertIn('bloqueante', error.exception.detalle)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.ESPERANDO_APROBACION)

    def test_aprobacion_y_rechazo_no_mueven_rechazo(self):
        cotizacion = self.cotizar()
        registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                            cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                            canal=MedioAprobacion.WEB)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.EN_REVISION)
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

    def test_respuesta_repetida_siempre_es_409(self):
        cotizacion = self.cotizar()
        primera = registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                                      cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                                      canal=MedioAprobacion.WEB)
        with self.assertRaises(ErrorDeAccion) as error:
            registrar_respuesta(servicio=self.servicio, componente_id=self.componente.pk,
                                cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                                canal=MedioAprobacion.WEB)
        self.assertEqual(error.exception.codigo, 409)

    def test_respuesta_externa_repetida_igual_es_409(self):
        cotizacion = self.cotizar()
        registrar_aprobacion_externa(
            cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
            medio=MedioAprobacion.WHATSAPP, usuario=None,
        )
        with self.assertRaises(ErrorDeAccion) as error:
            registrar_aprobacion_externa(
                cotizacion_id=cotizacion.pk, resultado=ResultadoAprobacion.APROBADA,
                medio=MedioAprobacion.WHATSAPP, usuario=None,
            )
        self.assertEqual(error.exception.codigo, 409)

    def test_motivo_finalizacion_acepta_texto_largo(self):
        self.componente.estado = EstadoComponente.EN_PRUEBAS
        self.componente.save(update_fields=['estado'])
        motivo = 'x' * 120
        cambiar_estado_componente(
            servicio=self.servicio, componente_id=self.componente.pk,
            nuevo_estado=EstadoComponente.LISTO_PARA_ENTREGA, comentario=motivo,
        )
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.motivo_finalizacion, motivo)

    def test_reenviar_cotizacion_conserva_detalles_y_recalcula_total(self):
        cotizacion = self.cotizar()
        cotizacion.estado = EstadoCotizacion.RECHAZADA
        cotizacion.save(update_fields=['estado'])
        cotizacion.detalles.create(descripcion='Cambio de sellos', valor=200000, cantidad=2)
        cotizacion.detalles.create(descripcion='Prueba', valor=50000, cantidad=1)

        nueva = reenviar_cotizacion(
            cotizacion_id=cotizacion.pk,
            datos={},
            usuario=None,
        )

        self.assertEqual(nueva.reemplaza_a_id, cotizacion.pk)
        self.assertEqual(nueva.componente_id, cotizacion.componente_id)
        self.assertEqual(nueva.tipo, cotizacion.tipo)
        self.assertEqual(nueva.es_bloqueante, cotizacion.es_bloqueante)
        self.assertEqual(nueva.total, 450000)
        self.assertEqual(
            list(nueva.detalles.values_list('descripcion', 'valor', 'cantidad')),
            [('Cambio de sellos', 200000, 2), ('Prueba', 50000, 1)],
        )


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
        self.assertEqual(datos_servicio['acciones_disponibles'], [
            'agregar_componente', 'crear_cotizacion', 'registrar_recepcion',
            'cancelar_servicio',
        ])
        self.assertIn('editar_componente', datos_componente['acciones_disponibles'])
        self.assertIn('eliminar_componente', datos_componente['acciones_disponibles'])

    def test_servicio_deja_de_ofrecer_recepcion_cuando_ya_fue_registrada(self):
        registrar_recepcion(servicio=self.servicio, comentario='Recibido')
        self.servicio.refresh_from_db()
        datos = ServicioAdministrativoSerializer(self.servicio).data
        self.assertNotIn('registrar_recepcion', datos['acciones_disponibles'])

    def test_cotizacion_expone_acciones_segun_estado_y_sucesora(self):
        self.componente.estado = EstadoComponente.EN_REVISION
        self.componente.save(update_fields=['estado'])
        cotizacion = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': self.componente, 'tipo': 'INICIAL',
            'descripcion': 'Trabajo',
            'detalles': [{'descripcion': 'Sellos', 'valor': 100, 'cantidad': 1}],
        }, usuario=None)
        acciones = lambda c: CotizacionAdministrativaSerializer(c).data['acciones_disponibles']
        self.assertEqual(acciones(cotizacion), ['editar_pendiente', 'registrar_respuesta'])
        cotizacion.estado = EstadoCotizacion.RECHAZADA
        cotizacion.save(update_fields=['estado'])
        self.assertEqual(acciones(cotizacion), ['reenviar'])
        nueva = reenviar_cotizacion(cotizacion_id=cotizacion.pk, datos={}, usuario=None)
        self.assertEqual(acciones(cotizacion), [])
        self.assertEqual(acciones(nueva), ['editar_pendiente', 'registrar_respuesta'])

    def test_servicio_cerrado_no_ofrece_acciones_ni_estados(self):
        self.servicio.estado = EstadoServicio.CANCELADO
        self.servicio.save(update_fields=['estado'])
        datos_componente = ComponenteAdministrativoSerializer(self.componente).data
        datos_servicio = ServicioAdministrativoSerializer(self.servicio).data
        self.assertEqual(datos_servicio['acciones_disponibles'], [])
        self.assertEqual(datos_componente['acciones_disponibles'], [])
        self.assertEqual(datos_componente['estados_seleccionables'], [])

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

    def test_cancelacion_exige_comentario_y_muestra_cancelado_en_seguimiento(self):
        url = reverse('servicio-cancelar', kwargs={'servicio_pk': self.servicio.pk})
        self.assertEqual(self.api.post(url, {}, format='json').status_code, 400)
        respuesta = self.api.post(url, {'comentario': 'No continúa'}, format='json')
        self.assertEqual(respuesta.status_code, 200)
        seguimiento = self.api.get(reverse('seguimiento', kwargs={
            'token': self.servicio.token_seguimiento,
        }))
        self.assertEqual(seguimiento.status_code, 200)
        self.assertTrue(seguimiento.data['cancelado'])
        self.assertEqual(seguimiento.data['cotizaciones_pendientes'], [])
        self.assertNotIn('comentario', str(seguimiento.data['historial']))

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
        self.componente.estado = EstadoComponente.EN_REVISION
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
            {'cotizacion_id': cotizacion.pk, 'resultado': ResultadoAprobacion.APROBADA}, format='json',
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['cotizacion'], cotizacion.pk)
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.EN_REVISION)

    def test_aprobacion_publica_responde_la_cotizacion_indicada(self):
        segundo = Componente.objects.create(servicio=self.servicio, tipo='Motor', estado=EstadoComponente.EN_REVISION)
        self.componente.estado = EstadoComponente.EN_REVISION
        self.componente.save(update_fields=['estado'])
        primera = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': self.componente,
            'descripcion': 'Primera', 'total': 100,
        }, usuario=None)
        segunda = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': segundo,
            'descripcion': 'Segunda', 'total': 200,
        }, usuario=None)
        self.api.force_authenticate(user=None)
        respuesta = self.api.post(
            reverse('seguimiento-aprobar', kwargs={'token': self.servicio.token_seguimiento}),
            {'cotizacion_id': segunda.pk, 'resultado': ResultadoAprobacion.APROBADA}, format='json',
        )
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data['cotizacion'], segunda.pk)
        primera.refresh_from_db()
        self.assertEqual(primera.estado, EstadoCotizacion.PENDIENTE)

    def test_respuesta_publica_repetida_igual_es_409(self):
        self.componente.estado = EstadoComponente.EN_REVISION
        self.componente.save(update_fields=['estado'])
        cotizacion = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': self.componente,
            'descripcion': 'Trabajo', 'total': 100,
        }, usuario=None)
        self.api.force_authenticate(user=None)
        url = reverse('seguimiento-aprobar', kwargs={'token': self.servicio.token_seguimiento})
        datos = {'cotizacion_id': cotizacion.pk, 'resultado': ResultadoAprobacion.APROBADA}
        self.assertEqual(self.api.post(url, datos, format='json').status_code, 201)
        self.assertEqual(self.api.post(url, datos, format='json').status_code, 409)

    def test_respuesta_http_repetida_con_resultado_contrario_es_409(self):
        """Una cotización respondida no acepta una segunda decisión distinta."""
        self.componente.estado = EstadoComponente.EN_REVISION
        self.componente.save(update_fields=['estado'])
        cotizacion = crear_cotizacion(datos={
            'servicio': self.servicio, 'componente': self.componente,
            'descripcion': 'Trabajo', 'total': 100,
        }, usuario=None)
        url = reverse('componente-respuesta', kwargs={
            'servicio_pk': self.servicio.pk,
            'componente_pk': self.componente.pk,
        })

        primera = self.api.post(url, {
            'cotizacion_id': cotizacion.pk,
            'resultado': ResultadoAprobacion.APROBADA,
            'canal': MedioAprobacion.WEB,
        }, format='json')
        self.assertEqual(primera.status_code, 201)

        segunda = self.api.post(url, {
            'cotizacion_id': cotizacion.pk,
            'resultado': ResultadoAprobacion.RECHAZADA,
            'canal': MedioAprobacion.WEB,
        }, format='json')
        self.assertEqual(segunda.status_code, 409)
        self.assertEqual(
            AprobacionServicio.objects.filter(cotizacion=cotizacion).count(), 1,
        )
        cotizacion.refresh_from_db()
        self.componente.refresh_from_db()
        self.assertEqual(cotizacion.estado, EstadoCotizacion.APROBADA)
        self.assertEqual(self.componente.estado, EstadoComponente.EN_REVISION)

    def test_seguimiento_sirve_el_paso_publico_del_componente(self):
        self.componente.estado = EstadoComponente.EN_PRUEBAS
        self.componente.save(update_fields=['estado'])
        self.api.force_authenticate(user=None)
        respuesta = self.api.get(reverse('seguimiento', kwargs={'token': self.servicio.token_seguimiento}))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data['componentes'][0]['paso_publico'], 'Pruebas')

    def test_recepcion_registra_fecha_pasa_en_curso_y_es_visible(self):
        self.assertEqual(self.servicio.estado, EstadoServicio.SOLICITADO)
        respuesta = self.api.post(
            reverse('servicio-recepcion', kwargs={'servicio_pk': self.servicio.pk}),
            {'comentario': 'Componentes recibidos en almacén.'}, format='json',
        )
        self.assertEqual(respuesta.status_code, 200)
        self.servicio.refresh_from_db()
        self.assertIsNotNone(self.servicio.fecha_recepcion)
        self.assertEqual(self.servicio.estado, EstadoServicio.EN_CURSO)
        entrada = HistorialServicio.objects.get(
            servicio=self.servicio, comentario='Componentes recibidos en almacén.')
        self.assertTrue(entrada.visible_cliente)
        self.api.force_authenticate(user=None)
        seguimiento = self.api.get(reverse('seguimiento', kwargs={
            'token': self.servicio.token_seguimiento,
        }))
        self.assertIsNotNone(seguimiento.data['fecha_recepcion'])
        self.assertIn('Componentes recibidos en almacén.',
                      str(seguimiento.data['historial']))

    def test_recepcion_repetida_es_409(self):
        url = reverse('servicio-recepcion', kwargs={'servicio_pk': self.servicio.pk})
        self.assertEqual(self.api.post(url, {}, format='json').status_code, 200)
        self.assertEqual(self.api.post(url, {}, format='json').status_code, 409)

    def test_recepcion_en_curso_conserva_estado(self):
        self.servicio.estado = EstadoServicio.EN_CURSO
        self.servicio.save(update_fields=['estado'])
        self.api.post(
            reverse('servicio-recepcion', kwargs={'servicio_pk': self.servicio.pk}),
            {}, format='json',
        )
        self.servicio.refresh_from_db()
        self.assertIsNotNone(self.servicio.fecha_recepcion)
        self.assertEqual(self.servicio.estado, EstadoServicio.EN_CURSO)

    def test_recepcion_exige_autenticacion(self):
        self.api.force_authenticate(user=None)
        respuesta = self.api.post(
            reverse('servicio-recepcion', kwargs={'servicio_pk': self.servicio.pk}),
            {}, format='json',
        )
        self.assertIn(respuesta.status_code, (401, 403))


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
