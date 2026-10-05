"""Reglas de negocio puras de los componentes de un servicio.

Todas las funciones de este archivo:

- reciben `hoy` como primer parámetro, que es el estado actual del servicio ya
  leído y serializado;
- devuelven un valor (o `None`);
- no escriben nada, no guardan objetos y no preguntan la hora del sistema.

`hoy` tiene esta forma:

    {
        'componentes': [
            {'id': 1, 'estado': 'PENDIENTE', 'trabajo_iniciado': False},
            ...
        ],
        'cotizaciones_por_componente': {
            1: [
                {'id': 10, 'es_bloqueante': True, 'estado': 'PENDIENTE'},
                ...
            ],
            ...
        },
    }

El criterio de la especificación 002 es único: un componente tiene posibilidad de
continuar cuando **ninguna** de sus cotizaciones `bloqueantes` está `pendiente`
o `rechazada`. Las cotizaciones `no_bloqueantes` nunca detienen el componente, ni
siquiera cuando están rechazadas.
"""

from servicios.estados import ESTADOS_FINALIZACION, EstadoComponente

# Estados de cotización que detienen un componente mientras siga vigente su
# cotización bloqueante.
ESTADOS_COTIZACION_BLOQUEANTE = ('PENDIENTE', 'RECHAZADA')


def _cotizaciones_de(hoy, componente):
    """Devuelve las cotizaciones del componente, o lista vacía si no tiene."""
    return hoy.get('cotizaciones_por_componente', {}).get(componente['id'], [])


def _bloqueantes(hoy, componente):
    """Devuelve solo las cotizaciones bloqueantes del componente."""
    return [
        cotizacion
        for cotizacion in _cotizaciones_de(hoy, componente)
        if cotizacion['es_bloqueante']
    ]


def _tiene_bloqueante_en(hoy, componente, estado):
    """Indica si alguna cotización bloqueante del componente está en `estado`."""
    return any(
        cotizacion['estado'] == estado
        for cotizacion in _bloqueantes(hoy, componente)
    )


def tiene_trabajo_iniciado(hoy, componente):
    """Indica si la empresa ya empezó a trabajar sobre el componente.

    El inicio de trabajo se registra al iniciar el desmontaje (RF-COT-08). Lo
    usa la regla de cierre del servicio, que exige que no haya trabajo en curso.
    """
    return bool(componente.get('trabajo_iniciado', False))


def puede_continuar(hoy, componente):
    """Indica si el componente puede pasar a la siguiente fase de trabajo.

    Falso si el componente ya está finalizado, o si tiene alguna cotización
    `bloqueante` en estado `pendiente` o `rechazada`. En cualquier otro caso,
    verdadero.
    """
    if componente.get('estado') in ESTADOS_FINALIZACION:
        return False

    hay_bloqueo = any(
        cotizacion['es_bloqueante']
        and cotizacion['estado'] in ESTADOS_COTIZACION_BLOQUEANTE
        for cotizacion in _cotizaciones_de(hoy, componente)
    )
    return not hay_bloqueo


def estado_por_rechazo_bloqueante(hoy, componente):
    """Devuelve el estado que impone un rechazo bloqueante, o `None`.

    Solo el rechazo de una cotización `bloqueante` fija el estado del
    componente a `rechazado_bloqueante` (RF-COT-05). Una cotización pendiente
    deja el componente como está, y una cotización `no_bloqueante` rechazada no
    cambia nada (RF-COT-06, RF-COT-07).

    El rechazo bloqueante tiene prioridad sobre una pendiente: si conviven, el
    componente está en la situación más restrictiva.
    """
    if _tiene_bloqueante_en(hoy, componente, 'RECHAZADA'):
        return EstadoComponente.RECHAZADO_BLOQUEANTE
    return None


def motivo_bloqueo(hoy, componente):
    """Explica en español por qué el componente está detenido, o `None`.

    Distingue los dos motivos posibles: el cliente rechazó una cotización
    bloqueante (RF-COT-05) o todavía no respondió una pendiente (RF-COT-04). Si
    hay ambos, manda el rechazo, que es el motivo más restrictivo.
    """
    if _tiene_bloqueante_en(hoy, componente, 'RECHAZADA'):
        return (
            'El cliente rechazó una cotización bloqueante. '
            'El componente queda detenido hasta redefinir el alcance.'
        )
    if _tiene_bloqueante_en(hoy, componente, 'PENDIENTE'):
        return (
            'Hay una cotización bloqueante pendiente de respuesta del cliente. '
            'El componente queda detenido hasta recibir su respuesta.'
        )
    return None


def componentes_no_finalizados(hoy):
    """Devuelve los componentes que aún no están cerrados.

    Es el criterio único del glosario 4.8: el servicio sigue abierto mientras
    exista un solo componente sin finalizar, sin importar si ese componente
    está activo o detenido por un rechazo.
    """
    return [
        componente
        for componente in hoy.get('componentes', [])
        if componente['estado'] not in ESTADOS_FINALIZACION
    ]


def todos_rechazan_bloqueantes(hoy):
    """Indica si todas las cotizaciones bloqueantes del servicio están rechazadas.

    Devuelve `True` solo si existe al menos una cotización `bloqueante` y todas
    están en estado `rechazada`:

    - sin cotizaciones bloqueantes → `False`, porque no hay nada que rechazar;
    - alguna `bloqueante` `pendiente` → `False` (RF-COT-12: se está esperando
      al cliente, no es que el trabajo se haya descartado);
    - alguna `bloqueante` `aprobada` → `False`;
    - todas `bloqueante` `rechazada` → `True`.

    Las cotizaciones `no_bloqueantes` son indiferentes para esta regla.
    """
    bloqueantes = [
        cotizacion
        for cotizacion in hoy.get('cotizaciones', [])
        if cotizacion['es_bloqueante']
    ]
    if not bloqueantes:
        return False
    return all(cotizacion['estado'] == 'RECHAZADA' for cotizacion in bloqueantes)


def puede_finalizar_servicio(hoy):
    """Indica si está habilitada la acción manual de finalizar el servicio.

    El criterio de habilitación es único: todos los componentes deben estar en
    estado de finalización (glosario 4.8 y RF-COT-13).

    El "caso 2" de RF-COT-11 (todas las cotizaciones bloqueantes rechazadas y
    ningún componente con trabajo iniciado) no habilita el cierre por sí solo:
    describe el motivo por el que se cierra, que es lo que
    `resumen_cierre` le muestra al administrativo.

    Ninguna función de este archivo finaliza un servicio: solo habilitan. La
    ejecución es siempre una acción manual del administrativo (glosario 4.9).
    """
    return componentes_no_finalizados(hoy) == []


def resumen_cierre(hoy):
    """Devuelve si la acción está habilitada y por qué, para la interfaz.

    Devuelve tres claves: `puede_finalizar`, `caso` y `detalle` (en español).
    Los casos describen el motivo, no condiciones independientes: solo se
    habilita cuando todos los componentes están finalizados.
    """
    pendientes = componentes_no_finalizados(hoy)

    if not pendientes:
        con_trabajo = [
            componente
            for componente in hoy.get('componentes', [])
            if tiene_trabajo_iniciado(hoy, componente)
        ]
        if todos_rechazan_bloqueantes(hoy) and not con_trabajo:
            return {
                'puede_finalizar': True,
                'caso': 'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO',
                'detalle': (
                    'Todos los componentes están finalizados. Las cotizaciones '
                    'bloqueantes fueron rechazadas y no se inició trabajo en '
                    'ningún componente'
                ),
            }
        return {
            'puede_finalizar': True,
            'caso': 'TODOS_FINALIZADOS',
            'detalle': 'Todos los componentes están finalizados',
        }

    # Queda al menos un componente sin finalizar: la acción nunca se habilita.
    if todos_rechazan_bloqueantes(hoy):
        return {
            'puede_finalizar': False,
            'caso': 'BLOQUEANTES_RECHAZADAS_CON_TRABAJO_INICIADO',
            'detalle': (
                f'Quedan {len(pendientes)} componente(s) sin finalizar. '
                'Debe finalizarlos uno a uno antes de cerrar el servicio'
            ),
        }

    return {
        'puede_finalizar': False,
        'caso': 'SERVICIO_EN_CURSO',
        'detalle': f'Quedan {len(pendientes)} componente(s) sin finalizar',
    }