"""Pruebas de modelo que siguen siendo válidas tras RF-FLU-01/02."""

from django.test import TestCase

from servicios.estados import EstadoComponente, EstadoFaseComponente
from servicios.models import Cliente, Componente, Cotizacion, Servicio


class ModelosFlujoTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente, descripcion_solicitud='Solicitud'
        )

    def test_componente_nace_pendiente_y_recibido(self):
        pieza = Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        self.assertEqual(pieza.estado, EstadoComponente.PENDIENTE)
        self.assertEqual(pieza.fase, EstadoFaseComponente.RECIBIDO)
        self.assertFalse(pieza.trabajo_iniciado)

    def test_cotizacion_puede_pertenecer_a_un_componente(self):
        pieza = Componente.objects.create(servicio=self.servicio, tipo='Bomba')
        cotizacion = Cotizacion.objects.create(
            servicio=self.servicio, componente=pieza, descripcion='Repuesto',
            total=100, es_bloqueante=True,
        )
        self.assertEqual(cotizacion.componente, pieza)
