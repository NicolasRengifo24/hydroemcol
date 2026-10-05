"""Tests de las vistas de la especificación 002.

Cubren RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-08, RF-COT-09,
RF-COT-10, RF-COT-11, RF-COT-12 y RF-COT-13.

Cada test comprueba que la **API** rechaza lo que la especificación prohíbe,
no solo que el botón de la interfaz esté deshabilitado. Esa es la garantía real
(constitución principio 3).
"""

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from servicios.estados import CanalRespuesta, EstadoComponente, EstadoFaseComponente
from servicios.models import (
    AprobacionServicio,
    Cliente,
    Componente,
    Cotizacion,
    EstadoCotizacion,
    EstadoServicio,
    HistorialComponente,
    HistorialServicio,
    MedioAprobacion,
    Servicio,
)
from usuarios.models import Usuario


class BaseApiTest(APITestCase):
    """Datos mínimos y autenticación para las vistas administrativas."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='admin', password='prueba12345',
        )
        self.client.force_authenticate(self.usuario)

        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro hidráulico',
        )

    def url_respuesta(self, componente=None):
        return reverse(
            'componente-respuesta',
            kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': (componente or self.componente).pk,
            },
        )

    def url_iniciar_trabajo(self, componente=None):
        return reverse(
            'componente-iniciar-trabajo',
            kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': (componente or self.componente).pk,
            },
        )

    def url_finalizar_componente(self, componente=None):
        return reverse(
            'componente-finalizar',
            kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': (componente or self.componente).pk,
            },
        )

    def url_corregir_finalizacion(self, componente=None):
        return reverse(
            'componente-corregir-finalizacion',
            kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': (componente or self.componente).pk,
            },
        )

    def url_finalizar_servicio(self):
        return reverse('servicio-finalizar', kwargs={'servicio_pk': self.servicio.pk})

    def crear_cotizacion(self, componente=None, es_bloqueante=True, estado=None):
        return Cotizacion.objects.create(
            servicio=self.servicio,
            componente=componente or self.componente,
            descripcion='Repuesto del cilindro',
            total=250000,
            es_bloqueante=es_bloqueante,
            estado=estado or EstadoCotizacion.PENDIENTE,
        )


# ─────────────────────────────────────────────────────────────
# T16 — Registrar la respuesta del cliente (RF-COT-03)
# ─────────────────────────────────────────────────────────────

class TestRegistrarRespuesta(BaseApiTest):
    """RF-COT-03: canal, responsable y fecha de cada respuesta."""

    def test_registrar_respuesta_por_whatsapp(self):
        cotizacion = self.crear_cotizacion()
        respuesta = self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        aprobacion = AprobacionServicio.objects.get(cotizacion=cotizacion)
        self.assertEqual(aprobacion.medio, MedioAprobacion.WHATSAPP)
        self.assertEqual(aprobacion.usuario_registro, self.usuario)
        self.assertIsNotNone(aprobacion.fecha)

    def test_registrar_respuesta_por_web(self):
        cotizacion = self.crear_cotizacion()
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WEB,
            },
            format='json',
        )
        aprobacion = AprobacionServicio.objects.get(cotizacion=cotizacion)
        self.assertEqual(aprobacion.medio, MedioAprobacion.WEB)
        self.assertEqual(aprobacion.usuario_registro, self.usuario)

    def test_respuesta_deja_registro_consultable(self):
        cotizacion = self.crear_cotizacion()
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
                'observacion': 'El cliente lo considera muy caro',
            },
            format='json',
        )
        aprobacion = AprobacionServicio.objects.get(cotizacion=cotizacion)
        self.assertEqual(aprobacion.resultado, EstadoCotizacion.RECHAZADA)
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.estado, EstadoCotizacion.RECHAZADA)
        self.assertEqual(cotizacion.canal, CanalRespuesta.WHATSAPP)

    def test_cotizacion_ajena_al_componente_responde_400(self):
        otro = Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        cotizacion = self.crear_cotizacion(componente=otro)
        respuesta = self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WEB,
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cotizacion_ya_respondida_responde_400(self):
        cotizacion = self.crear_cotizacion(estado=EstadoCotizacion.RECHAZADA)
        respuesta = self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WEB,
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_canal_obligatorio(self):
        cotizacion = self.crear_cotizacion()
        respuesta = self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_respuesta_exige_autenticacion(self):
        self.client.force_authenticate(user=None)
        respuesta = self.client.post(self.url_respuesta(), {}, format='json')
        self.assertIn(
            respuesta.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


# ─────────────────────────────────────────────────────────────
# T16 — Efecto sobre el componente (RF-COT-05, RF-COT-06, RF-COT-13)
# ─────────────────────────────────────────────────────────────

class TestEfectoSobreElComponente(BaseApiTest):
    """El rechazo bloqueante detiene solo a su propio componente."""

    def test_rechazar_bloqueante_marca_componente(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE
        )

    def test_rechazar_bloqueante_registra_historial(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertEqual(registro.estado_anterior, EstadoComponente.PENDIENTE)
        self.assertEqual(
            registro.estado_nuevo, EstadoComponente.RECHAZADO_BLOQUEANTE
        )
        self.assertEqual(registro.usuario, self.usuario)

    def test_aprobar_bloqueante_no_marca_componente(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WEB,
            },
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.PENDIENTE)

    def test_rechazar_bloqueante_no_toca_otros_componentes(self):
        otro = Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        otro.refresh_from_db()
        self.assertEqual(otro.estado, EstadoComponente.PENDIENTE)

    def test_rechazar_bloqueante_no_cierra_el_servicio(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.SOLICITADO)
        self.assertIsNone(self.servicio.fecha_finalizacion)

    def test_rechazar_no_bloqueante_no_marca_componente(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=False)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertNotEqual(
            self.componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE
        )

    def test_servicio_no_se_finaliza_solo(self):
        """Glosario 4.9: ninguna vista finalize el servicio por su cuenta."""
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.servicio.refresh_from_db()
        self.assertNotEqual(self.servicio.estado, EstadoServicio.FINALIZADO)


# ─────────────────────────────────────────────────────────────
# T17 — Iniciar trabajo (RF-COT-04, RF-COT-08)
# ─────────────────────────────────────────────────────────────

class TestIniciarTrabajo(BaseApiTest):
    def test_iniciar_trabajo_permitido_registra_fase(self):
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.componente.refresh_from_db()
        self.assertTrue(self.componente.trabajo_iniciado)
        self.assertEqual(
            self.componente.fase, EstadoFaseComponente.DESMONTAJE_INICIADO
        )
        self.assertIsNotNone(self.componente.fecha_inicio_trabajo)

    def test_iniciar_trabajo_registra_historial(self):
        self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertEqual(
            registro.fase_registrada, EstadoFaseComponente.DESMONTAJE_INICIADO
        )
        self.assertEqual(registro.usuario, self.usuario)

    def test_iniciar_trabajo_bloqueado_responde_409(self):
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('detail', respuesta.data)

        self.componente.refresh_from_db()
        self.assertFalse(self.componente.trabajo_iniciado)

    def test_iniciar_trabajo_bloqueado_explica_el_motivo(self):
        self.crear_cotizacion(es_bloqueante=True)
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        # El mensaje dice por qué está bloqueado, en español (RF-COT-04).
        self.assertIn('bloqueante', respuesta.data['detail'])

    def test_bloqueante_pendiente_tambien_bloquea(self):
        self.crear_cotizacion(es_bloqueante=True)
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_no_bloqueante_pendiente_no_bloquea(self):
        self.crear_cotizacion(es_bloqueante=False)
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_otro_componente_bloqueado_no_impide_este(self):
        otro = Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        self.crear_cotizacion(componente=otro, es_bloqueante=True)
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_componente_finalizado_no_puede_iniciar_trabajo(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_TECNICO
        self.componente.save()
        respuesta = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)


# ─────────────────────────────────────────────────────────────
# T18 — Finalizar un componente (RF-COT-09, RF-COT-05, D-7)
# ─────────────────────────────────────────────────────────────

class TestFinalizarComponente(BaseApiTest):
    def test_finalizar_componente_por_tecnico(self):
        respuesta = self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.FINALIZADO_POR_TECNICO
        )
        self.assertEqual(
            self.componente.motivo_finalizacion,
            EstadoComponente.FINALIZADO_POR_TECNICO,
        )
        self.assertIsNotNone(self.componente.fecha_finalizacion)

    def test_finalizar_componente_por_cliente(self):
        self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_CLIENTE},
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.motivo_finalizacion,
            EstadoComponente.FINALIZADO_POR_CLIENTE,
        )

    def test_finalizar_componente_registra_historial(self):
        self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertEqual(registro.estado_anterior, EstadoComponente.PENDIENTE)
        self.assertEqual(
            registro.estado_nuevo, EstadoComponente.FINALIZADO_POR_TECNICO
        )

    def test_finalizar_componente_detenido_por_bloqueante(self):
        """D-7: un componente detenido por rechazo también se puede cerrar."""
        cotizacion = self.crear_cotizacion(es_bloqueante=True)
        self.client.post(
            self.url_respuesta(),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE
        )

        respuesta = self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.FINALIZADO_POR_TECNICO
        )

    def test_finalizar_componente_ya_finalizado_responde_409(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.save()
        respuesta = self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_motivo_invalido_responde_400(self):
        respuesta = self.client.post(
            self.url_finalizar_componente(),
            {'motivo': 'CERRADO'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finalizar_componente_no_cierra_el_servicio(self):
        """Finalizar un componente no finaliza el servicio."""
        self.client.post(
            self.url_finalizar_componente(),
            {'motivo': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.servicio.refresh_from_db()
        self.assertNotEqual(self.servicio.estado, EstadoServicio.FINALIZADO)


# ─────────────────────────────────────────────────────────────
# T19 — Corregir una finalización (RF-COT-10)
# ─────────────────────────────────────────────────────────────

class TestCorregirFinalizacion(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.motivo_finalizacion = (
            EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.componente.fecha_finalizacion = timezone.now()
        self.componente.save()

    def test_corregir_finalizacion_registra_anterior(self):
        respuesta = self.client.post(
            self.url_corregir_finalizacion(),
            {
                'nuevo_estado': EstadoComponente.EN_PROCESO,
                'comentario': 'Se cerró por error',
            },
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        registro = HistorialComponente.objects.latest('fecha')
        self.assertEqual(
            registro.estado_anterior, EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.assertEqual(registro.estado_nuevo, EstadoComponente.EN_PROCESO)
        self.assertEqual(registro.usuario, self.usuario)

    def test_corregir_finalizacion_actualiza_el_componente(self):
        self.client.post(
            self.url_corregir_finalizacion(),
            {'nuevo_estado': EstadoComponente.EN_PROCESO},
            format='json',
        )
        self.componente.refresh_from_db()
        self.assertEqual(self.componente.estado, EstadoComponente.EN_PROCESO)

    def test_corregir_a_otro_cierre_tambien_se_puede(self):
        respuesta = self.client.post(
            self.url_corregir_finalizacion(),
            {'nuevo_estado': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.FINALIZADO_POR_TECNICO
        )

    def test_corregir_estado_no_finalizado_responde_409(self):
        """Solo se corrigen estados de finalización."""
        self.componente.estado = EstadoComponente.EN_PROCESO
        self.componente.save()
        respuesta = self.client.post(
            self.url_corregir_finalizacion(),
            {'nuevo_estado': EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_nuevo_estado_invalido_responde_400(self):
        respuesta = self.client.post(
            self.url_corregir_finalizacion(),
            {'nuevo_estado': 'CERRADO'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# T20 — Finalizar el servicio (RF-COT-11, RF-COT-12, CL-03)
# ─────────────────────────────────────────────────────────────

class TestFinalizarServicio(BaseApiTest):
    def finalizar_componente(self, componente, estado=None):
        componente.estado = estado or EstadoComponente.FINALIZADO_POR_TECNICO
        componente.motivo_finalizacion = componente.estado
        componente.fecha_finalizacion = timezone.now()
        componente.save()

    def test_finalizar_servicio_caso_todos_finalizados(self):
        self.finalizar_componente(self.componente)
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.estado, EstadoServicio.FINALIZADO)
        self.assertIsNotNone(self.servicio.fecha_finalizacion)

    def test_finalizar_servicio_registra_historial_interno(self):
        self.finalizar_componente(self.componente)
        self.client.post(self.url_finalizar_servicio(), {}, format='json')
        registro = HistorialServicio.objects.filter(
            servicio=self.servicio, estado=EstadoServicio.FINALIZADO
        ).latest('fecha')
        self.assertFalse(registro.visible_cliente)
        self.assertEqual(registro.usuario, self.usuario)

    def test_finalizar_servicio_caso_bloqueantes_rechazadas(self):
        """RF-COT-11: motivo del caso 2, con todos los componentes ya cerrados."""
        self.crear_cotizacion(es_bloqueante=True)
        cotizacion = Cotizacion.objects.filter(componente=self.componente).first()
        cotizacion.estado = EstadoCotizacion.RECHAZADA
        cotizacion.save()
        self.finalizar_componente(self.componente)

        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(
            respuesta.data['resumen_cierre']['caso'],
            'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO',
        )

    def test_finalizar_servicio_pendiente_no_habilita_ni_bloquea(self):
        """RF-COT-12: lo pendiente es neutro para el cierre.

        RF-COT-12 dice que lo pendiente NO habilita "por sí solo" el cierre; no
        dice que lo bloquee. El único criterio es que todos los componentes
        estén finalizados (criterio único 4.8), así que un componente ya
        finalizado con una cotización pendiente no impide cerrar.
        """
        self.crear_cotizacion(es_bloqueante=True)
        self.finalizar_componente(self.componente)
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_pendiente_deja_el_componente_detenido(self):
        """Segunda mitad de RF-COT-12: sigue visible como detenido.

        La cotización pendiente no habilita el cierre, pero tampoco deja pasar
        al cliente como si no existiera: el componente queda detenido.
        """
        self.crear_cotizacion(es_bloqueante=True)

        inicio = self.client.post(self.url_iniciar_trabajo(), {}, format='json')
        self.assertEqual(inicio.status_code, status.HTTP_409_CONFLICT)

        cierre = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(cierre.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('resumen_cierre', cierre.data)

    def test_finalizar_servicio_con_componente_sin_finalizar_responde_409(self):
        """Criterio único 4.8: basta un componente sin cerrar para bloquear."""
        self.finalizar_componente(self.componente)
        Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_finalizar_servicio_bloqueada_con_trabajo_responde_409(self):
        """CL-03: hay trabajo iniciado y el componente sigue sin cerrarse."""
        self.componente.trabajo_iniciado = True
        self.componente.fase = EstadoFaseComponente.DESMONTAJE_INICIADO
        self.componente.save()
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

    def test_el_409_explica_el_motivo(self):
        Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('resumen_cierre', respuesta.data)

    def test_accion_de_finalizar_exige_administrativo(self):
        self.finalizar_componente(self.componente)
        self.client.force_authenticate(user=None)
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertIn(
            respuesta.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
        self.servicio.refresh_from_db()
        self.assertNotEqual(self.servicio.estado, EstadoServicio.FINALIZADO)

    def test_no_se_puede_finalizar_un_servicio_ajeno(self):
        """El servicio se toma de la ruta, no del cuerpo."""
        otro_servicio = Servicio.objects.create(
            cliente=self.cliente, descripcion_solicitud='Otro',
        )
        self.finalizar_componente(self.componente)
        respuesta = self.client.post(self.url_finalizar_servicio(), {}, format='json')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        otro_servicio.refresh_from_db()
        self.assertNotEqual(otro_servicio.estado, EstadoServicio.FINALIZADO)