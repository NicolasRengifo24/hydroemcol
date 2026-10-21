"""Contratos públicos y campos calculados del flujo vigente."""

from django.test import TestCase

from servicios.estados import EstadoComponente
from servicios.models import Cliente, Componente, HistorialComponente, Servicio
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

    def test_publico_expone_comentarios_del_historial(self):
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.PENDIENTE,
            estado_nuevo=EstadoComponente.EN_PRUEBAS,
            comentario='Pruebas de presión realizadas.',
        )
        datos = ComponentePublicoSerializer(self.componente).data
        self.assertEqual(len(datos['historial']), 1)
        registro = datos['historial'][0]
        self.assertEqual(registro['estado'], 'En pruebas')
        self.assertEqual(registro['paso_publico'], 'Pruebas')
        self.assertEqual(registro['comentario'], 'Pruebas de presión realizadas.')
        self.assertNotIn('usuario', registro)

    def test_publico_omite_historial_sin_comentario(self):
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior=EstadoComponente.PENDIENTE,
            estado_nuevo=EstadoComponente.EN_REVISION,
            comentario='',
        )
        datos = ComponentePublicoSerializer(self.componente).data
        self.assertEqual(datos['historial'], [])

    def test_historial_con_estado_legado_no_rompe_el_seguimiento(self):
        """Un estado antiguo en el historial no debe tumbar el seguimiento.

        La migración 0008 remapeó el estado vigente, no las filas de historial
        ya escritas, así que pueden aparecer valores como
        ``FINALIZADO_POR_TECNICO`` o ``EN_PROCESO``.
        """
        HistorialComponente.objects.create(
            componente=self.componente,
            estado_anterior='EN_PROCESO',
            estado_nuevo='FINALIZADO_POR_TECNICO',
            comentario='Cierre con el catálogo anterior.',
        )
        datos = ComponentePublicoSerializer(self.componente).data
        registro = datos['historial'][0]
        self.assertEqual(registro['paso_publico'], 'Finalizado')

    def test_paso_publico_catalogo_legado_y_desconocido(self):
        from servicios.estados import paso_publico_componente
        self.assertEqual(paso_publico_componente('EN_PROCESO'), 'Revisión y cotización')
        self.assertEqual(paso_publico_componente('FINALIZADO_POR_TECNICO'), 'Finalizado')
        self.assertEqual(paso_publico_componente('ESTADO_INEXISTENTE'), 'Revisión y cotización')
