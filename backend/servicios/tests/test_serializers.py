"""Contratos públicos y campos calculados del flujo vigente."""

from django.test import TestCase

from servicios.estados import EstadoComponente
from servicios.models import Cliente, Componente, Servicio
from servicios.serializers import ComponentePublicoSerializer, ServicioPublicoSerializer


class SerializersFlujoTest(TestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nombre='Cliente')
        self.servicio = Servicio.objects.create(
            cliente=cliente, descripcion_solicitud='Solicitud'
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio, tipo='Bomba'
        )

    def test_publico_expone_etiquetas_y_no_campos_internos(self):
        datos = ComponentePublicoSerializer(self.componente).data
        self.assertEqual(datos['estado'], 'Pendiente')
        self.assertNotIn('motivo_finalizacion', datos)
        self.assertNotIn('trabajo_iniciado', datos)

    def test_servicio_publico_incluye_componentes(self):
        datos = ServicioPublicoSerializer(self.servicio).data
        self.assertEqual(datos['estado'], 'Solicitado')
        self.assertEqual(datos['componentes'][0]['estado'], 'Pendiente')

    def test_catalogo_publico_refleja_estado_nuevo(self):
        self.componente.estado = EstadoComponente.RECHAZADO
        self.componente.save(update_fields=['estado'])
        self.assertEqual(
            ComponentePublicoSerializer(self.componente).data['estado'],
            'Rechazado',
        )
