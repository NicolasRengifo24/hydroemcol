"""Tests de los cambios de modelo de la especificación 002.

Cubren RF-COT-02, RF-COT-08, RF-COT-09 y RF-COT-14. Son `TestCase` porque
verifican valores por defecto y no regresión de datos existentes, que es lo
único que puede romper una migración.
"""

from django.test import TestCase

from servicios.estados import EstadoComponente, EstadoFaseComponente
from servicios.models import (
    Cliente,
    Componente,
    Cotizacion,
    HistorialComponente,
    Servicio,
)


class TestEstadoPorDefectoDelComponente(TestCase):
    """Un componente nuevo entra en el proceso sin trabajo hecho."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )

    def test_componente_nace_pendiente(self):
        componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro hidráulico',
        )
        self.assertEqual(componente.estado, EstadoComponente.PENDIENTE)
        self.assertFalse(componente.trabajo_iniciado)

    def test_componente_nace_recibido(self):
        componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Bomba',
        )
        self.assertEqual(componente.fase, EstadoFaseComponente.RECIBIDO)

    def test_componente_nace_sin_fechas_de_trabajo(self):
        componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Válvula',
        )
        self.assertIsNone(componente.fecha_inicio_trabajo)
        self.assertIsNone(componente.fecha_finalizacion)
        self.assertEqual(componente.motivo_finalizacion, '')

    def test_el_estado_usa_el_catalogo_de_estados(self):
        """T8: las choices vienen de `estados.py`, no se redeclaran aquí."""
        campo = Componente._meta.get_field('estado')
        valores = [valor for valor, _ in campo.choices]
        self.assertEqual(valores, [e.value for e in EstadoComponente])

    def test_el_motivo_usa_los_dos_estados_de_finalizacion(self):
        campo = Componente._meta.get_field('motivo_finalizacion')
        valores = [valor for valor, _ in campo.choices]
        self.assertEqual(
            valores,
            [
                EstadoComponente.FINALIZADO_POR_CLIENTE,
                EstadoComponente.FINALIZADO_POR_TECNICO,
            ],
        )


class TestTrabajoIniciadoEsExplicito(TestCase):
    """RF-COT-08 y CL-09: el booleano manda, no la fase."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Motor',
        )

    def test_trabajo_iniciado_es_explicito(self):
        self.componente.trabajo_iniciado = True
        self.componente.fase = EstadoFaseComponente.DESMONTAJE_INICIADO
        self.componente.save()

        self.componente.refresh_from_db()
        self.assertTrue(self.componente.trabajo_iniciado)
        self.assertEqual(
            self.componente.fase, EstadoFaseComponente.DESMONTAJE_INICIADO
        )

    def test_el_booleano_no_se_deduce_de_la_fase(self):
        """Una fase advanced no pone el booleano por su cuenta."""
        self.componente.fase = EstadoFaseComponente.EN_EJECUCION
        self.componente.save()

        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.fase, EstadoFaseComponente.EN_EJECUCION
        )
        self.assertFalse(self.componente.trabajo_iniciado)

    def test_fecha_inicio_queda_registrada(self):
        from django.utils import timezone

        momento = timezone.now()
        self.componente.trabajo_iniciado = True
        self.componente.fecha_inicio_trabajo = momento
        self.componente.save()

        self.componente.refresh_from_db()
        self.assertEqual(self.componente.fecha_inicio_trabajo, momento)


class TestFinalizacionDelComponente(TestCase):
    """RF-COT-09: el cierre guarda motivo y fecha."""

    def setUp(self):
        from django.utils import timezone

        self.momento = timezone.now()
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro',
        )

    def test_finalizar_componente_guarda_motivo_y_fecha(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_TECNICO
        self.componente.motivo_finalizacion = (
            EstadoComponente.FINALIZADO_POR_TECNICO
        )
        self.componente.fecha_finalizacion = self.momento
        self.componente.save()

        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.estado, EstadoComponente.FINALIZADO_POR_TECNICO
        )
        self.assertEqual(
            self.componente.motivo_finalizacion,
            EstadoComponente.FINALIZADO_POR_TECNICO,
        )
        self.assertEqual(self.componente.fecha_finalizacion, self.momento)

    def test_se_puede_finalizar_por_cliente(self):
        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.motivo_finalizacion = (
            EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.componente.save()

        self.componente.refresh_from_db()
        self.assertEqual(
            self.componente.motivo_finalizacion,
            EstadoComponente.FINALIZADO_POR_CLIENTE,
        )


class TestCotizacionPorComponente(TestCase):
    """RF-COT-02 y RF-COT-14: la cotización baja al nivel del componente."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Orbitrol',
        )

    def test_cotizacion_existente_no_se_rompe(self):
        """RF-COT-14: las cotizaciones antigas siguen siendo válidas."""
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            descripcion='Cotización general del servicio',
            total=850000,
        )
        self.assertFalse(cotizacion.es_bloqueante)
        self.assertIsNone(cotizacion.componente)
        self.assertEqual(cotizacion.estado, 'PENDIENTE')

    def test_cotizacion_puede_apuntar_a_componente(self):
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto del orbitrol',
            total=250000,
            es_bloqueante=True,
        )
        self.assertEqual(cotizacion.componente, self.componente)
        self.assertTrue(cotizacion.es_bloqueante)

    def test_cotizacion_acepta_componente_nulo(self):
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            total=100000,
        )
        self.assertIsNone(cotizacion.componente)

    def test_la_cotizacion_del_componente_muere_con_este(self):
        """La cotización cuelga del componente, no al revés."""
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            total=250000,
        )
        self.componente.delete()
        self.assertFalse(Cotizacion.objects.filter(pk=cotizacion.pk).exists())

    def test_el_canal_usa_el_catalogo_de_estados(self):
        from servicios.estados import CanalRespuesta

        campo = Cotizacion._meta.get_field('canal')
        valores = [valor for valor, _ in campo.choices]
        self.assertEqual(valores, [c.value for c in CanalRespuesta])

    def test_el_canal_nace_vacio(self):
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            total=100000,
        )
        self.assertEqual(cotizacion.canal, '')


class TestHistorialComponente(TestCase):
    """T9: el historial guarda el estado anterior, para poder auditar."""

    def setUp(self):
        from usuarios.models import Usuario

        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Control',
        )
        self.usuario = Usuario.objects.create_user(
            username='tecnico', password='prueba12345',
        )

    def test_guarda_el_estado_anterior_y_el_nuevo(self):
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.FINALIZADO_POR_CLIENTE,
            estado_nuevo=EstadoComponente.EN_PROCESO,
            usuario=self.usuario,
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertEqual(
            registro.estado_anterior, EstadoComponente.FINALIZADO_POR_CLIENTE
        )
        self.assertEqual(registro.estado_nuevo, EstadoComponente.EN_PROCESO)
        self.assertEqual(registro.usuario, self.usuario)

    def test_registra_la_fase_del_desmontaje(self):
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.PENDIENTE,
            estado_nuevo=EstadoComponente.EN_PROCESO,
            fase_registrada=EstadoFaseComponente.DESMONTAJE_INICIADO,
            usuario=self.usuario,
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertEqual(
            registro.fase_registrada, EstadoFaseComponente.DESMONTAJE_INICIADO
        )

    def test_acepta_comentario(self):
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.FINALIZADO_POR_CLIENTE,
            estado_nuevo=EstadoComponente.FINALIZADO_POR_TECNICO,
            usuario=self.usuario,
            comentario='Corrección de un cierre mal registrado',
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertIn('Corrección', registro.comentario)

    def test_el_historial_se_borra_con_el_componente(self):
        """El historial es el rastro del ciclo de vida del componente (CASCADE).

        Si el componente desaparece, su rastro deja de tener sentido. El
        histórico que sobrevive a la vida del servicio es el de
        `HistorialServicio`, no este.
        """
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.PENDIENTE,
            estado_nuevo=EstadoComponente.EN_PROCESO,
            usuario=self.usuario,
        )
        self.componente.delete()
        self.assertEqual(HistorialComponente.objects.count(), 0)

    def test_el_historial_acepta_usuario_nulo(self):
        """Un cambio sin actor identificado no debe romper el registro."""
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.PENDIENTE,
            estado_nuevo=EstadoComponente.RECHAZADO_BLOQUEANTE,
        )
        registro = HistorialComponente.objects.get(componente=self.componente)
        self.assertIsNone(registro.usuario)