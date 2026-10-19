"""Catálogos vigentes del flujo simplificado (RF-FLU-01/02)."""

from django.test import SimpleTestCase

from servicios.estados import ESTADOS_FINALIZACION, EstadoComponente
from servicios.models import EstadoServicio


class CatalogosFlujoTest(SimpleTestCase):
    def test_catalogo_servicio_tiene_cuatro_estados(self):
        self.assertEqual(
            list(EstadoServicio.values),
            ['SOLICITADO', 'EN_CURSO', 'FINALIZADO', 'CANCELADO'],
        )

    def test_catalogo_componente_tiene_ocho_estados(self):
        self.assertEqual(len(EstadoComponente), 8)
        self.assertEqual(
            list(EstadoComponente.values),
            ['PENDIENTE', 'EN_REVISION', 'COTIZANDO',
             'ESPERANDO_APROBACION', 'OPERARIO_TRABAJANDO',
             'EN_PRUEBAS', 'LISTO_PARA_ENTREGA', 'RECHAZADO'],
        )

    def test_finalizaciones_son_los_dos_cierres_de_componente(self):
        self.assertEqual(
            tuple(ESTADOS_FINALIZACION),
            (EstadoComponente.LISTO_PARA_ENTREGA, EstadoComponente.RECHAZADO),
        )
