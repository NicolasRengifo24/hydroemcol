"""Los cuatro recorridos de §6.4 del plan, de principio a fin (T28).

El plan los llama "verificación manual (no automatizable)". No es del todo
cierto: los cuatro son recorridos de proceso sobre las mismas reglas que ya
están en `reglas.py`, así que se pueden escribir como tests y obtener algo
mejor que una comprobación puntual, namely que se vuelvan a pasar solos.

Cada test camina la historia completa: registra la respuesta del cliente,
inicia y finaliza componentes e intenta cerrar el servicio, y comprueba el
estado en cada paso. Se recorre por la **API** y no por el admin a propósito:
la garantía que importa (constitución principio 3) es que el backend rechaza
lo prohibido, no que el botón esté oculto. La parte visual de los recorridos se
verifica aparte en el navegador.

Cubren RF-COT-05, RF-COT-11, RF-COT-13 y los casos límite CL-03 y CL-07.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from servicios.estados import CanalRespuesta, EstadoComponente, EstadoFaseComponente
from servicios.models import (
    Cliente,
    Componente,
    Cotizacion,
    EstadoCotizacion,
    EstadoServicio,
    Servicio,
)
from usuarios.models import Usuario


class BaseRecorrido(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='tecnico', password='prueba12345',
        )
        self.client.force_authenticate(self.usuario)

        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )

    # ── Utilidades ────────────────────────────────────────────

    def nuevo_componente(self, tipo='Cilindro hidráulico'):
        return Componente.objects.create(servicio=self.servicio, tipo=tipo)

    def nueva_cotizacion(self, componente, es_bloqueante=True):
        return Cotizacion.objects.create(
            servicio=self.servicio,
            componente=componente,
            descripcion='Repuesto del cilindro',
            total=250000,
            es_bloqueante=es_bloqueante,
            estado=EstadoCotizacion.PENDIENTE,
        )

    def url(self, nombre, componente=None):
        return reverse(
            nombre,
            kwargs={
                'servicio_pk': self.servicio.pk,
                'componente_pk': componente.pk,
            },
        )

    def rechazar(self, componente, cotizacion):
        """El cliente rechaza una cotización por WhatsApp."""
        return self.client.post(
            self.url('componente-respuesta', componente),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.RECHAZADA,
                'canal': CanalRespuesta.WHATSAPP,
            },
            format='json',
        )

    def aprobar(self, componente, cotizacion):
        return self.client.post(
            self.url('componente-respuesta', componente),
            {
                'cotizacion_id': cotizacion.pk,
                'resultado': EstadoCotizacion.APROBADA,
                'canal': CanalRespuesta.WEB,
            },
            format='json',
        )

    def iniciar_trabajo(self, componente):
        return self.client.post(
            self.url('componente-iniciar-trabajo', componente),
            {},
            format='json',
        )

    def finalizar_componente(self, componente, motivo=None):
        return self.client.post(
            self.url('componente-finalizar', componente),
            {'motivo': motivo or EstadoComponente.FINALIZADO_POR_TECNICO},
            format='json',
        )

    def finalizar_servicio(self):
        return self.client.post(
            reverse('servicio-finalizar', kwargs={'servicio_pk': self.servicio.pk}),
            {},
            format='json',
        )

    def estado_del_servicio(self):
        self.servicio.refresh_from_db()
        return self.servicio.estado


# ─────────────────────────────────────────────────────────────
# Recorrido 1 — El rechazo de uno no frena al otro
# ─────────────────────────────────────────────────────────────

class RecorridoUno(BaseRecorrido):
    """§6.4, fila 1: RF-COT-05 y RF-COT-13.

    Un servicio con dos componentes. El cliente rechaza la cotización
    bloqueante del primero. Ese componente queda detenido, el otro sigue
    avanzando y el servicio permanece abierto.
    """

    def test_el_rechazo_de_uno_no_toca_al_otro(self):
        primero = self.nuevo_componente('Cilindro hidráulico')
        segundo = self.nuevo_componente('Bomba de engrane')
        cotizacion = self.nueva_cotizacion(primero, es_bloqueante=True)

        # El segundo componente avanza: se registra su desmontaje.
        respuesta = self.iniciar_trabajo(segundo)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        # El cliente rechaza la bloqueante del primero.
        respuesta = self.rechazar(primero, cotizacion)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        primero.refresh_from_db()
        segundo.refresh_from_db()

        # El rechazado queda detenido por la bloqueante.
        self.assertEqual(primero.estado, EstadoComponente.RECHAZADO_BLOQUEANTE)
        self.assertFalse(primero.trabajo_iniciado)

        # El otro sigue avanzando: el rechazo no lo ha tocado. Que avance
        # significa trabajo registrado (RF-COT-08), no cambio de estado: iniciar
        # el desmontaje marca `trabajo_iniciado` y la fase, y `estado` sigue
        # `PENDIENTE` hasta que alguien lo finalice.
        self.assertTrue(segundo.trabajo_iniciado)
        self.assertEqual(
            segundo.fase, EstadoFaseComponente.DESMONTAJE_INICIADO,
        )
        self.assertIsNotNone(segundo.fecha_inicio_trabajo)
        self.assertEqual(segundo.estado, EstadoComponente.PENDIENTE)

        # El servicio sigue abierto (RF-COT-13).
        self.assertNotEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)

    def test_el_servicio_aun_no_puede_cerrarse(self):
        primero = self.nuevo_componente('Cilindro hidráulico')
        segundo = self.nuevo_componente('Bomba de engrane')
        cotizacion = self.nueva_cotizacion(primero, es_bloqueante=True)

        self.iniciar_trabajo(segundo)
        self.rechazar(primero, cotizacion)
        self.finalizar_componente(segundo)

        # Queda el primero sin finalizar, así que el cierre se rechaza.
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertNotEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)


# ─────────────────────────────────────────────────────────────
# Recorrido 2 — Desmontaje y después rechazo (CL-03)
# ─────────────────────────────────────────────────────────────

class RecorridoDos(BaseRecorrido):
    """§6.4, fila 2: CL-03.

    Se registra el desmontaje de un componente y después se rechaza su
    cotización bloqueante. El trabajo ya no se puede deshacer, así que el
    servicio no puede cerrarse hasta que ese componente se finalice.
    """

    def test_el_cierre_queda_bloqueado_hasta_finalizar_el_componente(self):
        componente = self.nuevo_componente('Cilindro hidráulico')
        cotizacion = self.nueva_cotizacion(componente, es_bloqueante=True)

        # Primero se aprueba para poder empezar a trabajar.
        self.aprobar(componente, cotizacion)
        respuesta = self.iniciar_trabajo(componente)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        # Después se rechaza otra cotización bloqueante del mismo componente.
        otra = self.nueva_cotizacion(componente, es_bloqueante=True)
        respuesta = self.rechazar(componente, otra)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        componente.refresh_from_db()
        self.assertTrue(componente.trabajo_iniciado)
        self.assertEqual(componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE)

        # El servicio no se puede cerrar con ese componente abierto.
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)
        self.assertNotEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)

        # Al finalizarlo, el cierre se habilita y explica el motivo del caso 2.
        respuesta = self.finalizar_componente(componente)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)

        # El motivo dice que hubo trabajo, no el caso de "sin trabajo".
        resumen = respuesta.data['resumen_cierre']
        self.assertNotEqual(
            resumen['caso'], 'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO',
        )


# ─────────────────────────────────────────────────────────────
# Recorrido 3 — Todas las bloqueantes rechazadas sin trabajo
# ─────────────────────────────────────────────────────────────

class RecorridoTres(BaseRecorrido):
    """§6.4, fila 3: RF-COT-11.

    Se rechazan todas las cotizaciones bloqueantes sin haber iniciado trabajo
    en ningún componente. El cierre no se habilita hasta finalizar el
    componente detenido; después aparece con el motivo del caso 2.
    """

    def test_el_cierre_no_se_habilita_hasta_finalizar_el_componente_detenido(self):
        primero = self.nuevo_componente('Cilindro hidráulico')
        segundo = self.nuevo_componente('Bomba de engrane')

        cotizacion_primero = self.nueva_cotizacion(primero, es_bloqueante=True)
        cotizacion_segundo = self.nueva_cotizacion(segundo, es_bloqueante=True)

        respuesta = self.rechazar(primero, cotizacion_primero)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        respuesta = self.rechazar(segundo, cotizacion_segundo)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        # Nadie ha iniciado trabajo todavía.
        primero.refresh_from_db()
        segundo.refresh_from_db()
        self.assertFalse(primero.trabajo_iniciado)
        self.assertFalse(segundo.trabajo_iniciado)

        # Mientras queden componentes sin finalizar, no hay cierre.
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

        # Finalizar uno tampoco basta: el otro sigue abierto.
        self.finalizar_componente(primero)
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

        # Al finalizar el último, el cierre se habilita con el caso 2.
        self.finalizar_componente(segundo)
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)
        self.assertEqual(
            respuesta.data['resumen_cierre']['caso'],
            'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO',
        )

    def test_el_motivo_del_caso_2_explica_que_no_hay_trabajo(self):
        componente = self.nuevo_componente()
        cotizacion = self.nueva_cotizacion(componente, es_bloqueante=True)
        self.rechazar(componente, cotizacion)
        self.finalizar_componente(componente)

        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        detalle = respuesta.data['resumen_cierre']['detalle']
        # El detalle está en español y menciona el rechazo y la ausencia de
        # trabajo, que es lo que un técnico necesita leer para entender el caso.
        self.assertIn('rechaz', detalle.lower())
        self.assertIn('trabajo', detalle.lower())


# ─────────────────────────────────────────────────────────────
# Recorrido 4 — Un solo componente rechazado (CL-07)
# ─────────────────────────────────────────────────────────────

class RecorridoCuatro(BaseRecorrido):
    """§6.4, fila 4: CL-07.

    Servicio de un único componente con la bloqueante rechazada y sin trabajo.
    El cierre se habilita en cuanto ese componente queda finalizado.
    """

    def test_el_cierre_se_habilita_al_finalizar_el_unico_componente(self):
        componente = self.nuevo_componente()
        cotizacion = self.nueva_cotizacion(componente, es_bloqueante=True)

        respuesta = self.rechazar(componente, cotizacion)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

        componente.refresh_from_db()
        self.assertEqual(componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE)

        # Rechazado y sin finalizar: todavía no.
        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_409_CONFLICT)

        # Finalizado: sí.
        respuesta = self.finalizar_componente(componente)
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        respuesta = self.finalizar_servicio()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(self.estado_del_servicio(), EstadoServicio.FINALIZADO)

    def test_el_cliente_ve_el_estado_del_componente_que_rechazo(self):
        """El componente rechazado sigue siendo visible y explicado."""
        componente = self.nuevo_componente()
        cotizacion = self.nueva_cotizacion(componente, es_bloqueante=True)
        self.rechazar(componente, cotizacion)

        componente.refresh_from_db()
        # No se borra ni se oculta: el cliente tiene que ver qué pasó.
        self.assertTrue(Componente.objects.filter(pk=componente.pk).exists())
        self.assertEqual(componente.estado, EstadoComponente.RECHAZADO_BLOQUEANTE)
        self.assertEqual(
            componente.get_estado_display(), 'Rechazado (bloqueante)',
        )