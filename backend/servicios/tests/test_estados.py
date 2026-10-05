"""Tests de los catálogos de estado del componente.

Cubre T1 de tasks.md. Los catálogos son la base de las reglas puras de
`reglas.py`, así que se verifican de forma aislada, sin base de datos.
"""

from django.test import SimpleTestCase

from servicios.estados import (
    CanalRespuesta,
    ESTADOS_FINALIZACION,
    EstadoComponente,
    EstadoFaseComponente,
)


class TestEstadoComponente(SimpleTestCase):
    def test_tiene_los_siete_estados(self):
        self.assertEqual(len(EstadoComponente), 7)

    def test_incluye_rechazado_bloqueante(self):
        self.assertIn(
            EstadoComponente.RECHAZADO_BLOQUEANTE,
            [e.value for e in EstadoComponente],
        )

    def test_incluye_los_dos_estados_de_finalizacion(self):
        valores = [e.value for e in EstadoComponente]
        self.assertIn('FINALIZADO_POR_CLIENTE', valores)
        self.assertIn('FINALIZADO_POR_TECNICO', valores)


class TestEstadoFaseComponente(SimpleTestCase):
    def test_tiene_las_tres_fases(self):
        self.assertEqual(len(EstadoFaseComponente), 3)

    def test_el_desmontaje_es_una_fase(self):
        valores = [e.value for e in EstadoFaseComponente]
        self.assertIn('DESMONTAJE_INICIADO', valores)


class TestCanalRespuesta(SimpleTestCase):
    def test_tiene_web_y_whatsapp(self):
        valores = [e.value for e in CanalRespuesta]
        self.assertEqual(valores, ['WEB', 'WHATSAPP'])


class TestEstadosFinalizacion(SimpleTestCase):
    def test_contiene_exactamente_dos_estados(self):
        self.assertEqual(len(ESTADOS_FINALIZACION), 2)

    def test_los_dos_estados_son_de_finalizacion_del_componente(self):
        self.assertEqual(
            set(ESTADOS_FINALIZACION),
            {
                EstadoComponente.FINALIZADO_POR_CLIENTE,
                EstadoComponente.FINALIZADO_POR_TECNICO,
            },
        )

    def test_no_incluye_estados_no_finalizados(self):
        for estado in (
            EstadoComponente.PENDIENTE,
            EstadoComponente.RECHAZADO_BLOQUEANTE,
            EstadoComponente.EN_PROCESO,
        ):
            self.assertNotIn(estado, ESTADOS_FINALIZACION)
