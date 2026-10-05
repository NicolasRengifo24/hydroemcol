"""Tests de las funciones puras de decisión de `reglas.py`.

Cada test corresponde a un requisito o a un caso límite de la
especificación 002. Son funciones puras: reciben el estado actual (`hoy`) y
devuelven una decisión, sin tocar la base de datos ni la hora del sistema.

T2 cubre `tiene_trabajo_iniciado` y `puede_continuar`. Las demás reglas se
verifican en las tareas T3, T4 y T5.
"""

from django.test import SimpleTestCase

from servicios.estados import EstadoComponente
from servicios.reglas import (
    componentes_no_finalizados,
    estado_por_rechazo_bloqueante,
    motivo_bloqueo,
    puede_continuar,
    puede_finalizar_servicio,
    resumen_cierre,
    tiene_trabajo_iniciado,
    todos_rechazan_bloqueantes,
)


def componente(id=1, estado=EstadoComponente.PENDIENTE, trabajo_iniciado=False):
    """Construye un componente mínimo para las pruebas."""
    return {
        'id': id,
        'estado': estado,
        'trabajo_iniciado': trabajo_iniciado,
    }


def cotizacion(es_bloqueante, estado, id=1):
    """Construye una cotización mínima para las pruebas."""
    return {
        'id': id,
        'es_bloqueante': es_bloqueante,
        'estado': estado,
    }


def hoy(componentes=None, cotizaciones_por_componente=None):
    """Construye el estado actual que consumen las reglas.

    `cotizaciones_por_componente` agrupa por id de componente, que es como las
    leerán las vistas y los serializers. `cotizaciones` es la misma lista en
    plano, que es como la lee la regla de cierre del servicio.
    """
    agrupadas = (
        cotizaciones_por_componente if cotizaciones_por_componente is not None else {}
    )
    return {
        'componentes': componentes if componentes is not None else [componente()],
        'cotizaciones_por_componente': agrupadas,
        'cotizaciones': [c for lista in agrupadas.values() for c in lista],
    }


class TestTieneTrabajoIniciado(SimpleTestCase):
    """RF-COT-08. El desmontaje es lo que marca el inicio de trabajo."""

    def test_sin_trabajo_iniciado_es_falso(self):
        estado = hoy(componentes=[componente(trabajo_iniciado=False)])
        self.assertFalse(tiene_trabajo_iniciado(estado, estado['componentes'][0]))

    def test_con_trabajo_iniciado_es_verdadero(self):
        estado = hoy(componentes=[componente(trabajo_iniciado=True)])
        self.assertTrue(tiene_trabajo_iniciado(estado, estado['componentes'][0]))


class TestPuedeContinuar(SimpleTestCase):
    """RF-COT-04, RF-COT-05, RF-COT-06 y RF-COT-07."""

    def test_sin_cotizaciones_puede_continuar(self):
        estado = hoy()
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_bloqueante_pendiente_no_puede_continuar(self):
        """RF-COT-04: se está esperando al cliente."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'PENDIENTE')],
        })
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_bloqueante_rechazada_no_puede_continuar(self):
        """RF-COT-05: el cliente no aprobó lo que cuesta."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'RECHAZADA')],
        })
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_bloqueante_aprobada_puede_continuar(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'APROBADA')],
        })
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_no_bloqueante_pendiente_puede_continuar(self):
        """RF-COT-06: lo no bloqueante nunca detiene."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'PENDIENTE')],
        })
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_no_bloqueante_rechazada_puede_continuar(self):
        """RF-COT-06: se puede dejar el tornillo tal cual."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'RECHAZADA')],
        })
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_no_bloqueante_aprobada_puede_continuar(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'APROBADA')],
        })
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_bloqueante_pendiente_manda_sobre_no_bloqueante_aprobada(self):
        """RF-COT-07 y CL-10: manda la bloqueante."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'PENDIENTE', id=1),
                cotizacion(False, 'APROBADA', id=2),
            ],
        })
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_bloqueante_rechazada_manda_sobre_no_bloqueante_aprobada(self):
        """RF-COT-07: una bloqueante rechazada tampoco se compensa."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'RECHAZADA', id=1),
                cotizacion(False, 'APROBADA', id=2),
            ],
        })
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_una_bloqueante_rechazada_con_otra_aprobada_no_puede_continuar(self):
        """RF-COT-07: basta una bloqueante que no esté aprobada."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'APROBADA', id=1),
                cotizacion(True, 'RECHAZADA', id=2),
            ],
        })
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_componente_finalizado_por_cliente_no_puede_continuar(self):
        estado = hoy(componentes=[
            componente(estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
        ])
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_componente_finalizado_por_tecnico_no_puede_continuar(self):
        estado = hoy(componentes=[
            componente(estado=EstadoComponente.FINALIZADO_POR_TECNICO),
        ])
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_rechazado_bloqueante_no_puede_continuar(self):
        """RF-COT-05: el estado detenido por un rechazo sigue sin poder continuar.

        El estado `rechazado_bloqueante` siempre viene acompañado de la
        cotización bloqueante en estado `rechazada`, que es la que sigue
        bloqueando. La regla decide sobre las cotizaciones, no sobre el estado
        derivado.
        """
        estado = hoy(
            componentes=[
                componente(estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
            ],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertFalse(puede_continuar(estado, estado['componentes'][0]))

    def test_rechazo_bloqueante_revertido_puede_continuar(self):
        """RF-COT-05: la condición deja de aplicar si el rechazo se revierte."""
        estado = hoy(
            componentes=[
                componente(estado=EstadoComponente.APROBADO),
            ],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'APROBADA')],
            },
        )
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))

    def test_otro_componente_bloqueado_no_afecta_a_este(self):
        """RF-COT-13: el bloqueo es por componente."""
        estado = hoy(
            componentes=[componente(id=1), componente(id=2)],
            cotizaciones_por_componente={
                1: [],
                2: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertTrue(puede_continuar(estado, estado['componentes'][0]))
        self.assertFalse(puede_continuar(estado, estado['componentes'][1]))

    def test_cl01_solo_se_detiene_el_componente_bloqueante(self):
        """CL-01: bloqueante, no bloqueante y sin cotización conviven."""
        estado = hoy(
            componentes=[
                componente(id=1),
                componente(id=2),
                componente(id=3),
            ],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'PENDIENTE', id=1)],
                2: [cotizacion(False, 'RECHAZADA', id=2)],
                3: [],
            },
        )
        decisiones = [
            puede_continuar(estado, componente) for componente in estado['componentes']
        ]
        self.assertEqual(decisiones, [False, True, True])

    def test_cl04_rechazado_bloqueante_no_detiene_a_los_demas(self):
        """CL-04: los que pueden avanzar continúan y el servicio sigue abierto."""
        estado = hoy(
            componentes=[
                componente(id=1, estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
                componente(id=2, estado=EstadoComponente.EN_PROCESO),
                componente(id=3, estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
            ],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA', id=1)],
                2: [cotizacion(False, 'RECHAZADA', id=2)],
                3: [],
            },
        )
        decisiones = [
            puede_continuar(estado, componente) for componente in estado['componentes']
        ]
        self.assertEqual(decisiones, [False, True, False])
        self.assertFalse(puede_finalizar_servicio(estado))


class TestEstadoPorRechazoBloqueante(SimpleTestCase):
    """RF-COT-05: un rechazo bloqueante fija el estado del componente."""

    def test_sin_cotizaciones_devuelve_none(self):
        estado = hoy()
        self.assertIsNone(estado_por_rechazo_bloqueante(estado, estado['componentes'][0]))

    def test_bloqueante_pendiente_devuelve_none(self):
        """Una cotización pendiente no fija estado: el componente sigue PENDIENTE."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'PENDIENTE')],
        })
        self.assertIsNone(estado_por_rechazo_bloqueante(estado, estado['componentes'][0]))

    def test_bloqueante_aprobada_devuelve_none(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'APROBADA')],
        })
        self.assertIsNone(estado_por_rechazo_bloqueante(estado, estado['componentes'][0]))

    def test_bloqueante_rechazada_devuelve_rechazado_bloqueante(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'RECHAZADA')],
        })
        self.assertEqual(
            EstadoComponente.RECHAZADO_BLOQUEANTE,
            estado_por_rechazo_bloqueante(estado, estado['componentes'][0]),
        )

    def test_no_bloqueante_rechazada_devuelve_none(self):
        """RF-COT-06: un rechazo no bloqueante no cambia el estado."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'RECHAZADA')],
        })
        self.assertIsNone(estado_por_rechazo_bloqueante(estado, estado['componentes'][0]))

    def test_rechazo_no_bloqueante_no_compensa_una_bloqueante_pendiente(self):
        """RF-COT-07: manda la bloqueante pendiente."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'PENDIENTE', id=1),
                cotizacion(False, 'RECHAZADA', id=2),
            ],
        })
        self.assertIsNone(estado_por_rechazo_bloqueante(estado, estado['componentes'][0]))

    def test_una_bloqueante_rechazada_fija_el_estado_entre_varias(self):
        """CL-10: basta una bloqueante rechazada."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'APROBADA', id=1),
                cotizacion(True, 'RECHAZADA', id=2),
                cotizacion(True, 'PENDIENTE', id=3),
            ],
        })
        self.assertEqual(
            EstadoComponente.RECHAZADO_BLOQUEANTE,
            estado_por_rechazo_bloqueante(estado, estado['componentes'][0]),
        )


class TestMotivoBloqueo(SimpleTestCase):
    """RF-COT-04 y RF-COT-05: el sistema explica por qué el componente está detenido."""

    def test_sin_cotizaciones_devuelve_none(self):
        estado = hoy()
        self.assertIsNone(motivo_bloqueo(estado, estado['componentes'][0]))

    def test_bloqueante_aprobada_devuelve_none(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'APROBADA')],
        })
        self.assertIsNone(motivo_bloqueo(estado, estado['componentes'][0]))

    def test_bloqueante_pendiente_explica_la_espera(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'PENDIENTE')],
        })
        motivo = motivo_bloqueo(estado, estado['componentes'][0])
        self.assertIsNotNone(motivo)
        self.assertIn('cotización', motivo.lower())

    def test_bloqueante_rechazada_explica_el_rechazo(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'RECHAZADA')],
        })
        motivo = motivo_bloqueo(estado, estado['componentes'][0])
        self.assertIsNotNone(motivo)
        self.assertIn('rechaz', motivo.lower())

    def test_no_bloqueante_rechazada_devuelve_none(self):
        """RF-COT-06: un rechazo no bloqueante no bloquea ni explica nada."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'RECHAZADA')],
        })
        self.assertIsNone(motivo_bloqueo(estado, estado['componentes'][0]))

    def test_el_rechazo_bloqueante_tiene_prioridad_sobre_la_espera(self):
        """Si hay una rechazada y otra pendiente, manda el rechazo."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'PENDIENTE', id=1),
                cotizacion(True, 'RECHAZADA', id=2),
            ],
        })
        motivo = motivo_bloqueo(estado, estado['componentes'][0])
        self.assertIn('rechaz', motivo.lower())


class TestComponentesNoFinalizados(SimpleTestCase):
    """Criterio único del glosario 4.8: servicio abierto con componentes sin cerrar."""

    def test_sin_componentes_devuelve_lista_vacia(self):
        self.assertEqual(componentes_no_finalizados(hoy(componentes=[])), [])

    def test_todos_finalizados_devuelve_lista_vacia(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
            componente(id=2, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
        ])
        self.assertEqual(componentes_no_finalizados(estado), [])

    def test_pendiente_cuenta_como_no_finalizado(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.PENDIENTE),
        ])
        self.assertEqual(len(componentes_no_finalizados(estado)), 1)

    def test_rechazado_bloqueante_cuenta_como_no_finalizado(self):
        """Un componente detenido por rechazo sigue sin cerrar: hay que cerrarlo."""
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
        ])
        self.assertEqual(len(componentes_no_finalizados(estado)), 1)

    def test_en_proceso_cuenta_como_no_finalizado(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.EN_PROCESO),
        ])
        self.assertEqual(len(componentes_no_finalizados(estado)), 1)

    def test_solo_devuelve_los_que_faltan_por_cerrar(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
            componente(id=2, estado=EstadoComponente.EN_PROCESO),
            componente(id=3, estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
            componente(id=4, estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
        ])
        pendientes = componentes_no_finalizados(estado)
        self.assertEqual([c['id'] for c in pendientes], [2, 3])


class TestTodosRechazanBloqueantes(SimpleTestCase):
    """RF-COT-11 caso 2 y RF-COT-12."""

    def test_sin_cotizaciones_es_falso(self):
        """Sin cotizaciones bloqueantes no hay nada que habilitar."""
        self.assertFalse(todos_rechazan_bloqueantes({'cotizaciones': []}))

    def test_lista_vacia_es_falsa(self):
        self.assertFalse(todos_rechazan_bloqueantes({'cotizaciones': []}))

    def test_solo_no_bloqueantes_es_falso(self):
        """RF-COT-06: sin bloqueantes, el caso 2 no aplica."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(False, 'RECHAZADA')],
        })
        self.assertFalse(todos_rechazan_bloqueantes(estado))

    def test_bloqueante_pendiente_es_falso(self):
        """RF-COT-12: pendiente no habilita el cierre."""
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'PENDIENTE')],
        })
        self.assertFalse(todos_rechazan_bloqueantes(estado))

    def test_todas_bloqueantes_rechazadas_es_verdadero(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'RECHAZADA')],
        })
        self.assertTrue(todos_rechazan_bloqueantes(estado))

    def test_todas_bloqueantes_rechazadas_entre_varios_componentes_es_verdadero(self):
        estado = hoy(
            componentes=[componente(id=1), componente(id=2)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA', id=1)],
                2: [cotizacion(True, 'RECHAZADA', id=2)],
            },
        )
        self.assertTrue(todos_rechazan_bloqueantes(estado))

    def test_una_bloqueante_aprobada_es_falso(self):
        estado = hoy(cotizaciones_por_componente={
            1: [cotizacion(True, 'APROBADA')],
        })
        self.assertFalse(todos_rechazan_bloqueantes(estado))

    def test_no_bloqueante_rechazada_no_compensa_a_la_bloqueante_aprobada(self):
        """CL-03: una bloqueante no rechazada impide el caso 2."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'APROBADA', id=1),
                cotizacion(False, 'RECHAZADA', id=2),
            ],
        })
        self.assertFalse(todos_rechazan_bloqueantes(estado))

    def test_no_bloqueante_pendiente_no_afecta_el_caso_2(self):
        """Las no bloqueantes son indiferentes para esta regla."""
        estado = hoy(cotizaciones_por_componente={
            1: [
                cotizacion(True, 'RECHAZADA', id=1),
                cotizacion(False, 'PENDIENTE', id=2),
            ],
        })
        self.assertTrue(todos_rechazan_bloqueantes(estado))


class TestPuedeFinalizarServicio(SimpleTestCase):
    """RF-COT-11, RF-COT-12, RF-COT-13 y el glosario 4.8.

    Criterio único de habilitación: todos los componentes finalizados. El
    caso 2 de RF-COT-11 es el motivo del cierre, no una condición aparte.
    """

    def test_sin_componentes_puede_finalizar(self):
        self.assertTrue(puede_finalizar_servicio(hoy(componentes=[])))

    def test_todos_finalizados_puede_finalizar(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
            componente(id=2, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
        ])
        self.assertTrue(puede_finalizar_servicio(estado))

    def test_un_componente_pendiente_no_puede_finalizar(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
            componente(id=2, estado=EstadoComponente.PENDIENTE),
        ])
        self.assertFalse(puede_finalizar_servicio(estado))

    def test_bloqueante_pendiente_no_habilita_por_si_solo(self):
        """RF-COT-12: una pendiente no habilita el cierre por sí sola.

        El componente con la cotización pendiente sigue sin finalizar, así que
        el servicio no se cierra. Lo que impide el cierre es que falte cerrar ese
        componente, no la pendiente en sí.
        """
        estado = hoy(
            componentes=[
                componente(id=1, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
                componente(id=2, estado=EstadoComponente.EN_PROCESO),
            ],
            cotizaciones_por_componente={
                2: [cotizacion(True, 'PENDIENTE')],
            },
        )
        self.assertFalse(puede_finalizar_servicio(estado))
        self.assertFalse(todos_rechazan_bloqueantes(estado))

    def test_rechazado_bloqueante_sin_finalizar_no_puede_finalizar(self):
        """Glosario 4.8: un componente detenido por rechazo sigue sin cerrar."""
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
            componente(id=2, estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
        ])
        self.assertFalse(puede_finalizar_servicio(estado))

    def test_bloqueantes_rechazadas_sin_finalizar_no_puede_finalizar(self):
        """RF-COT-11 (AND final) y RF-COT-13: el caso 2 no habilita solo."""
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.RECHAZADO_BLOQUEANTE)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertFalse(puede_finalizar_servicio(estado))

    def test_bloqueantes_rechazadas_sin_trabajo_ya_finalizado_puede_finalizar(self):
        """CL-02: ya finalizado, el motivo es 'rechazadas y nada trabajado'."""
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.FINALIZADO_POR_TECNICO)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertTrue(puede_finalizar_servicio(estado))

    def test_bloqueantes_rechazadas_con_trabajo_y_finalizado_puede_finalizar(self):
        """CL-03 no bloquea el cierre si el componente ya se cerró."""
        estado = hoy(
            componentes=[componente(
                estado=EstadoComponente.FINALIZADO_POR_TECNICO,
                trabajo_iniciado=True,
            )],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertTrue(puede_finalizar_servicio(estado))

    def test_cierre_bloqueantes_rechazadas_con_trabajo_no_habilita(self):
        """CL-03: hay trabajo y además falta cerrar ese componente."""
        estado = hoy(
            componentes=[componente(
                id=1,
                estado=EstadoComponente.RECHAZADO_BLOQUEANTE,
                trabajo_iniciado=True,
            )],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertTrue(tiene_trabajo_iniciado(estado, estado['componentes'][0]))
        self.assertFalse(puede_finalizar_servicio(estado))

    def test_cierre_sin_bloqueantes_rechazadas_no_habilita(self):
        """Sin ninguna bloqueante rechazada, el motivo es trabajo en curso."""
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.EN_PROCESO)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'APROBADA')],
            },
        )
        self.assertFalse(puede_finalizar_servicio(estado))
        self.assertEqual(resumen_cierre(estado)['caso'], 'SERVICIO_EN_CURSO')

    def test_un_solo_componente_rechazado_requiere_finalizarlo_primero(self):
        """CL-07: un solo componente aplica la misma regla."""
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.RECHAZADO_BLOQUEANTE)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        self.assertFalse(puede_finalizar_servicio(estado))
        estado['componentes'][0]['estado'] = EstadoComponente.FINALIZADO_POR_TECNICO
        self.assertTrue(puede_finalizar_servicio(estado))


class TestResumenCierre(SimpleTestCase):
    """El resumen es lo que ve el administrativo: habilitación más motivo."""

    def test_todos_finalizados(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.FINALIZADO_POR_CLIENTE),
        ])
        resumen = resumen_cierre(estado)
        self.assertTrue(resumen['puede_finalizar'])
        self.assertEqual(resumen['caso'], 'TODOS_FINALIZADOS')
        self.assertIn('finalizados', resumen['detalle'])

    def test_todos_finalizados_motivo_rechazo_sin_trabajo(self):
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.FINALIZADO_POR_TECNICO)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        resumen = resumen_cierre(estado)
        self.assertTrue(resumen['puede_finalizar'])
        self.assertEqual(resumen['caso'], 'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO')

    def test_servicio_en_curso(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.EN_PROCESO),
            componente(id=2, estado=EstadoComponente.FINALIZADO_POR_TECNICO),
        ])
        resumen = resumen_cierre(estado)
        self.assertFalse(resumen['puede_finalizar'])
        self.assertEqual(resumen['caso'], 'SERVICIO_EN_CURSO')
        self.assertIn('1', resumen['detalle'])

    def test_bloqueantes_rechazadas_con_componente_sin_finalizar(self):
        """Debe decir que falta cerrar el componente, no que hay trabajo."""
        estado = hoy(
            componentes=[componente(estado=EstadoComponente.RECHAZADO_BLOQUEANTE)],
            cotizaciones_por_componente={
                1: [cotizacion(True, 'RECHAZADA')],
            },
        )
        resumen = resumen_cierre(estado)
        self.assertFalse(resumen['puede_finalizar'])
        self.assertEqual(resumen['caso'], 'BLOQUEANTES_RECHAZADAS_CON_TRABAJO_INICIADO')
        self.assertIn('sin finalizar', resumen['detalle'])

    def test_el_resumen_devuelve_las_tres_claves(self):
        """T5: resumen_cierre devuelve puede_finalizar, caso y detalle."""
        estado = hoy(componentes=[componente(estado=EstadoComponente.PENDIENTE)])
        resumen = resumen_cierre(estado)
        self.assertEqual(sorted(resumen), ['caso', 'detalle', 'puede_finalizar'])

    def test_el_detalle_esta_en_espanol(self):
        estado = hoy(componentes=[
            componente(id=1, estado=EstadoComponente.RECHAZADO_BLOQUEANTE),
            componente(id=2, estado=EstadoComponente.PENDIENTE),
        ])
        resumen = resumen_cierre(estado)
        self.assertEqual(resumen['caso'], 'SERVICIO_EN_CURSO')
        self.assertIn('componente', resumen['detalle'])
