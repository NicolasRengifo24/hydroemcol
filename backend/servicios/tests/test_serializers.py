"""Tests de los serializers de la especificación 002.

Cubren RF-COT-01, RF-COT-02, RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-06,
RF-COT-11 y RF-COT-13.

Dos cosas se verifican aquí:

1. que los campos nuevos aparezcan en la respuesta;
2. que los campos que decide el backend **no** se puedan escribir desde el
   cliente (constitución principio 3: el backend decide, la interfaz solo
   muestra).
"""

from django.test import TestCase

from servicios.estados import EstadoComponente, EstadoFaseComponente
from servicios.models import Cliente, Componente, Cotizacion, Servicio
from servicios.serializers import (
    ComponentePublicoSerializer,
    ComponenteSerializer,
    CotizacionSerializer,
    ServicioPublicoSerializer,
    ServicioSerializer,
)


class TestElPublicoVeElEstadoPeroNoLosCamposDeControl(TestCase):
    """El cliente ve el estado de su componente, no el control interno.

    `ServicioPublicoSerializer` reutiliza serializers anidados. Por eso
    `ComponentePublicoSerializer` existe aparte del administrativo: el cliente
    tiene derecho a saber en qué estado está lo que envió (RF-COT-15), pero no
    a ver los campos que describen reglas internas de la empresa. Estos tests
    existen para que una ampliación futura noAmplíe la pantalla del cliente sin
    querer.
    """

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro hidráulico',
        )

    def test_el_publico_ve_el_estado_y_la_fase(self):
        datos = ComponentePublicoSerializer(self.componente).data
        self.assertIn('estado', datos)
        self.assertIn('fase', datos)

    def test_el_estado_publico_es_etiqueta_en_espanol(self):
        """El cliente no debe leer el código interno del estado."""
        self.componente.estado = EstadoComponente.RECHAZADO_BLOQUEANTE
        self.componente.fase = EstadoFaseComponente.DESMONTAJE_INICIADO
        self.componente.save()

        datos = ComponentePublicoSerializer(self.componente).data
        self.assertEqual(
            datos['estado'],
            self.componente.get_estado_display(),
        )
        self.assertNotEqual(datos['estado'], EstadoComponente.RECHAZADO_BLOQUEANTE)
        self.assertNotEqual(
            datos['fase'], EstadoFaseComponente.DESMONTAJE_INICIADO,
        )

    def test_el_publico_refleja_el_cambio_de_estado(self):
        """El estado público sigue al guardado, sin caché."""
        antes = ComponentePublicoSerializer(self.componente).data['estado']

        self.componente.estado = EstadoComponente.FINALIZADO_POR_CLIENTE
        self.componente.save()

        despues = ComponentePublicoSerializer(self.componente).data['estado']
        self.assertNotEqual(antes, despues)
        self.assertEqual(despues, self.componente.get_estado_display())

    def test_el_componente_publico_no_expone_los_campos_de_control(self):
        datos = ComponentePublicoSerializer(self.componente).data
        for campo in (
            'trabajo_iniciado',
            'fecha_inicio_trabajo',
            'fecha_finalizacion',
            'motivo_finalizacion',
            'puede_continuar',
            'motivo_bloqueo',
        ):
            self.assertNotIn(campo, datos)

    def test_el_servicio_publico_no_arrastra_campos_de_control(self):
        datos = ServicioPublicoSerializer(self.servicio).data
        componente = datos['componentes'][0]
        for campo in (
            'puede_continuar', 'motivo_bloqueo', 'trabajo_iniciado',
            'motivo_finalizacion',
        ):
            self.assertNotIn(campo, componente)

    def test_el_servicio_publico_conserva_sus_campos_de_siempre(self):
        datos = ServicioPublicoSerializer(self.servicio).data
        for campo in (
            'codigo', 'tipo_servicio', 'estado', 'descripcion_solicitud',
            'componentes', 'historial', 'fotografias', 'cotizaciones_pendientes',
        ):
            self.assertIn(campo, datos)


class TestCamposNuevosDelComponente(TestCase):
    """T13: el estado del componente viaja en la respuesta."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro hidráulico',
        )

    def test_expone_el_estado_y_la_fase(self):
        datos = ComponenteSerializer(self.componente).data
        self.assertEqual(datos['estado'], EstadoComponente.PENDIENTE)
        self.assertEqual(datos['fase'], EstadoFaseComponente.RECIBIDO)

    def test_expone_el_trabajo_iniciado(self):
        datos = ComponenteSerializer(self.componente).data
        self.assertFalse(datos['trabajo_iniciado'])

    def test_expone_las_fechas_de_trabajo(self):
        self.componente.trabajo_iniciado = True
        self.componente.save()
        datos = ComponenteSerializer(self.componente).data
        self.assertIn('fecha_inicio_trabajo', datos)
        self.assertIn('fecha_finalizacion', datos)

    def test_expone_el_motivo_de_finalizacion(self):
        datos = ComponenteSerializer(self.componente).data
        self.assertIn('motivo_finalizacion', datos)
        self.assertEqual(datos['motivo_finalizacion'], '')

    def test_no_acepta_escribir_el_estado(self):
        """El estado lo cambia el backend, no el cliente."""
        serializer = ComponenteSerializer(
            self.componente,
            data={'tipo': 'Cilindro hidráulico', 'estado': 'FINALIZADO_POR_TECNICO'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertNotEqual(instance.estado, EstadoComponente.FINALIZADO_POR_TECNICO)

    def test_no_acepta_escribir_el_trabajo_iniciado(self):
        serializer = ComponenteSerializer(
            self.componente,
            data={'tipo': 'Cilindro hidráulico', 'trabajo_iniciado': True},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertFalse(instance.trabajo_iniciado)

    def test_no_acepta_escribir_el_motivo_de_finalizacion(self):
        serializer = ComponenteSerializer(
            self.componente,
            data={
                'tipo': 'Cilindro hidráulico',
                'motivo_finalizacion': 'FINALIZADO_POR_CLIENTE',
            },
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.motivo_finalizacion, '')


class TestCamposCalculadosDelComponente(TestCase):
    """T14: `puede_continuar` y `motivo_bloqueo` los calcula el backend."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )
        self.componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Bomba',
        )

    def test_sin_cotizaciones_puede_continuar_y_sin_motivo(self):
        datos = ComponenteSerializer(self.componente).data
        self.assertTrue(datos['puede_continuar'])
        self.assertIsNone(datos['motivo_bloqueo'])

    def test_bloqueante_pendiente_no_puede_continuar(self):
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            es_bloqueante=True,
            total=100000,
        )
        datos = ComponenteSerializer(self.componente).data
        self.assertFalse(datos['puede_continuar'])
        self.assertIsNotNone(datos['motivo_bloqueo'])

    def test_bloqueante_rechazada_no_puede_continuar(self):
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            es_bloqueante=True,
            estado='RECHAZADA',
            total=100000,
        )
        datos = ComponenteSerializer(self.componente).data
        self.assertFalse(datos['puede_continuar'])

    def test_no_bloqueante_rechazada_puede_continuar(self):
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            es_bloqueante=False,
            estado='RECHAZADA',
            total=100000,
        )
        datos = ComponenteSerializer(self.componente).data
        self.assertTrue(datos['puede_continuar'])
        self.assertIsNone(datos['motivo_bloqueo'])

    def test_otro_componente_bloqueado_no_le_toca(self):
        """RF-COT-13: el cálculo es por componente."""
        otro = Componente.objects.create(servicio=self.servicio, tipo='Válvula')
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=otro,
            es_bloqueante=True,
            estado='RECHAZADA',
            total=100000,
        )
        datos = ComponenteSerializer(self.componente).data
        self.assertTrue(datos['puede_continuar'])

    def test_los_campos_calculados_no_se_pueden_escribir(self):
        serializer = ComponenteSerializer(
            self.componente,
            data={'tipo': 'Bomba', 'puede_continuar': False},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('puede_continuar', serializer.validated_data)


class TestCamposNuevosDeLaCotizacion(TestCase):
    """T13: la cotización baja al componente y declara su canal."""

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
        self.cotizacion = Cotizacion.objects.create(
            servicio=self.servicio,
            componente=self.componente,
            descripcion='Repuesto',
            total=250000,
            es_bloqueante=True,
            canal='WHATSAPP',
        )

    def test_expone_el_componente(self):
        datos = CotizacionSerializer(self.cotizacion).data
        self.assertEqual(datos['componente'], self.componente.pk)

    def test_expone_es_bloqueante(self):
        datos = CotizacionSerializer(self.cotizacion).data
        self.assertTrue(datos['es_bloqueante'])

    def test_expone_el_canal(self):
        datos = CotizacionSerializer(self.cotizacion).data
        self.assertEqual(datos['canal'], 'WHATSAPP')

    def test_no_acepta_escribir_es_bloqueante(self):
        serializer = CotizacionSerializer(
            self.cotizacion,
            data={'descripcion': 'Repuesto', 'total': '250000', 'es_bloqueante': False},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('es_bloqueante', serializer.validated_data)

    def test_no_acepta_escribir_el_canal(self):
        serializer = CotizacionSerializer(
            self.cotizacion,
            data={'descripcion': 'Repuesto', 'canal': 'WEB'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('canal', serializer.validated_data)


class TestResumenDeCierreEnElServicio(TestCase):
    """T15: el servicio expone si se puede cerrar y por qué."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre='Cliente de prueba')
        self.servicio = Servicio.objects.create(
            cliente=self.cliente,
            descripcion_solicitud='Solicitud de prueba',
        )

    def test_expone_el_resumen_de_cierre(self):
        datos = ServicioSerializer(self.servicio).data
        self.assertIn('resumen_cierre', datos)
        self.assertIn('puede_finalizar', datos['resumen_cierre'])
        self.assertIn('caso', datos['resumen_cierre'])
        self.assertIn('detalle', datos['resumen_cierre'])

    def test_sin_componentes_queda_nada_por_ejecutar(self):
        """Un servicio sin componentes no queda nada por ejecutar.

        El "por qué" de RF-COT-11 dice que el servicio se cierra cuando ya no
        queda nada que ejecutar. Con cero componentes eso se cumple, así que la
        acción queda habilitada. Un servicio sin componentes es una anomalía de
        datos, no un caso de negocio, y se detecta al crearlo sin componentes.
        """
        datos = ServicioSerializer(self.servicio).data
        self.assertTrue(datos['resumen_cierre']['puede_finalizar'])
        self.assertEqual(datos['resumen_cierre']['caso'], 'TODOS_FINALIZADOS')

    def test_componente_pendiente_no_puede_finalizar(self):
        Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro',
            estado=EstadoComponente.PENDIENTE,
        )
        datos = ServicioSerializer(self.servicio).data
        self.assertFalse(datos['resumen_cierre']['puede_finalizar'])

    def test_todos_finalizados_puede_finalizar(self):
        Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro',
            estado=EstadoComponente.FINALIZADO_POR_TECNICO,
        )
        datos = ServicioSerializer(self.servicio).data
        self.assertTrue(datos['resumen_cierre']['puede_finalizar'])
        self.assertEqual(datos['resumen_cierre']['caso'], 'TODOS_FINALIZADOS')

    def test_rechazado_bloqueante_sin_finalizar_no_puede_finalizar(self):
        componente = Componente.objects.create(
            servicio=self.servicio,
            tipo='Cilindro',
            estado=EstadoComponente.RECHAZADO_BLOQUEANTE,
        )
        Cotizacion.objects.create(
            servicio=self.servicio,
            componente=componente,
            es_bloqueante=True,
            estado='RECHAZADA',
            total=100000,
        )
        datos = ServicioSerializer(self.servicio).data
        self.assertFalse(datos['resumen_cierre']['puede_finalizar'])

    def test_el_resumen_no_se_puede_escribir(self):
        """T15: el serializer no añade ninguna acción de finalizar."""
        serializer = ServicioSerializer(
            self.servicio,
            data={'descripcion_solicitud': 'Otro', 'resumen_cierre': {'puede_finalizar': True}},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('resumen_cierre', serializer.validated_data)