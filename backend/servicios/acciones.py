"""Acciones de proceso, en un solo lugar.

Cada acción de la especificación 002 vive aquí y la usan **las dos** capas que
la disparan: la API (`views.py`, T16 a T20) y el admin (`admin.py`, T25 a T27).

Por qué un módulo aparte y no la lógica dentro de las vistas: el admin necesita
iniciar trabajo, finalizar y corregir. Si cada capa reimplementara la regla, el
mismo requisito existiría en dos versiones y algún día divergirían. Aquí la regla
está escrita una vez, y las dos capas solo traducen peticiones.

`reglas.py` sigue siendo puro y sin base de datos. Este módulo es el que la usa,
traduciendo modelos a las llaves que las reglas esperan.

Ninguna función escribe directamente: todas validan con las reglas y, si algo
no cuadra, lanzan `ErrorDeAccion` con el mensaje que verá la persona.
"""

from django.db import transaction
from django.utils import timezone

from .estados import ESTADOS_FINALIZACION, EstadoComponente, EstadoFaseComponente
from .models import (
    AprobacionServicio,
    Componente,
    Cotizacion,
    EstadoCotizacion,
    EstadoServicio,
    HistorialComponente,
    HistorialServicio,
    Servicio,
)
from .reglas import (
    estado_por_rechazo_bloqueante,
    motivo_bloqueo,
    puede_continuar,
    puede_finalizar_servicio,
    resumen_cierre,
)
from .serializers import construir_hoy


class ErrorDeAccion(Exception):
    """Una acción no se puede ejecutar. El mensaje va en español, al usuario."""

    def __init__(self, detalle, codigo=400, extra=None):
        super().__init__(detalle)
        self.detalle = detalle
        self.codigo = codigo
        self.extra = extra or {}


def _componente_de_servicio(servicio, componente_id):
    """Devuelve el componente comprobando que pertenece al servicio.

    Sin esta comprobación, un id manipulado en la URL permitiría actuar sobre un
    componente de otra solicitud.
    """
    for componente in servicio.componentes.all():
        if componente.pk == componente_id:
            return componente
    raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)


def resumen_de_cierre(servicio):
    """Lo que la interfaz necesita saber del cierre, sin ejecutarlo."""
    return resumen_cierre(construir_hoy(servicio))


# ─────────────────────────────────────────────────────────────
# T16 / T25 — Registrar la respuesta del cliente (RF-COT-03)
# ─────────────────────────────────────────────────────────────

def registrar_respuesta(
    *, servicio, componente_id, cotizacion_id, resultado, canal,
    observacion='', usuario=None, ip=None,
):
    """Registra la respuesta del cliente y su efecto sobre el componente.

    Guarda el canal, quién la registra y cuándo (RF-COT-04). Si el componente
    tenía una cotización bloqueante y el cliente la rechaza, el componente
    queda `RECHAZADO_BLOQUEANTE` (RF-COT-05), sin tocar el estado del servicio
    (RF-COT-13).
    """
    componente = _componente_de_servicio(servicio, componente_id)

    cotizacion = next(
        (
            c for c in servicio.cotizaciones.all()
            if c.pk == cotizacion_id
        ),
        None,
    )
    if cotizacion is None:
        raise ErrorDeAccion('La cotización no pertenece a ese servicio.', 404)
    if cotizacion.componente_id != componente.pk:
        raise ErrorDeAccion('La cotización no pertenece a ese componente.', 400)
    if cotizacion.estado != EstadoCotizacion.PENDIENTE:
        raise ErrorDeAccion('Esa cotización ya tiene respuesta.', 400)

    with transaction.atomic():
        # Se relee filtrando por PENDIENTE para que una respuesta simultánea no
        # se pise: es la garantía real de que no se responde dos veces.
        cotizacion = Cotizacion.objects.filter(
            pk=cotizacion.pk, estado=EstadoCotizacion.PENDIENTE,
        ).first()
        if cotizacion is None:
            raise ErrorDeAccion('Esa cotización ya tiene respuesta.', 409)

        aprobacion = AprobacionServicio.objects.create(
            cotizacion=cotizacion,
            resultado=resultado,
            medio=canal,
            usuario_registro=usuario,
            fecha=timezone.now(),
            observacion=observacion,
            ip=ip,
        )
        cotizacion.estado = resultado
        cotizacion.canal = canal
        cotizacion.save(update_fields=['estado', 'canal'])

        # Las reglas ven la cotización ya actualizada, no la anterior.
        hoy = construir_hoy(servicio)
        estado_nuevo = estado_por_rechazo_bloqueante(
            hoy,
            next(c for c in hoy['componentes'] if c['id'] == componente.pk),
        )
        if estado_nuevo:
            estado_anterior = componente.estado
            componente.estado = estado_nuevo
            componente.save(update_fields=['estado'])
            HistorialComponente.objects.create(
                componente=componente,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                comentario='Cotización bloqueante rechazada por el cliente',
                usuario=usuario,
            )

    return aprobacion


# ─────────────────────────────────────────────────────────────
# T17 / T26 — Iniciar trabajo (RF-COT-04, RF-COT-08)
# ─────────────────────────────────────────────────────────────

def iniciar_trabajo(*, servicio, componente_id, usuario=None):
    """Registra el inicio del trabajo. Aplica RF-COT-04: lo bloquea la API."""
    componente = _componente_de_servicio(servicio, componente_id)

    hoy = construir_hoy(servicio)
    componente_hoy = next(
        c for c in hoy['componentes'] if c['id'] == componente.pk
    )
    if not puede_continuar(hoy, componente_hoy):
        raise ErrorDeAccion(
            'El componente no puede iniciar trabajo: '
            f'{motivo_bloqueo(hoy, componente_hoy)}',
            409,
        )

    with transaction.atomic():
        estado_anterior = componente.estado
        componente.fase = EstadoFaseComponente.DESMONTAJE_INICIADO
        componente.trabajo_iniciado = True
        componente.fecha_inicio_trabajo = timezone.now()
        componente.save(
            update_fields=['fase', 'trabajo_iniciado', 'fecha_inicio_trabajo'],
        )
        HistorialComponente.objects.create(
            componente=componente,
            estado_anterior=estado_anterior,
            estado_nuevo=componente.estado,
            fase_registrada=EstadoFaseComponente.DESMONTAJE_INICIADO,
            comentario='Inicio de trabajo registrado',
            usuario=usuario,
        )

    return componente


# ─────────────────────────────────────────────────────────────
# T18 / T26 — Finalizar un componente (RF-COT-09)
# ─────────────────────────────────────────────────────────────

def finalizar_componente(*, servicio, componente_id, motivo, usuario=None):
    """Finaliza un componente con su motivo.

    No exige `puede_continuar`: un componente detenido por una bloqueante
    rechazada también se cierra (RF-COT-05 y decisión D-7). Lo que no se
    permite es cerrar dos veces (RF-COT-09).
    """
    componente = _componente_de_servicio(servicio, componente_id)

    if componente.estado in ESTADOS_FINALIZACION:
        raise ErrorDeAccion('El componente ya está finalizado.', 409)

    with transaction.atomic():
        estado_anterior = componente.estado
        componente.estado = motivo
        componente.motivo_finalizacion = motivo
        componente.fecha_finalizacion = timezone.now()
        componente.save(
            update_fields=['estado', 'motivo_finalizacion', 'fecha_finalizacion'],
        )
        HistorialComponente.objects.create(
            componente=componente,
            estado_anterior=estado_anterior,
            estado_nuevo=motivo,
            comentario=f'Componente finalizado: {componente.get_estado_display()}',
            usuario=usuario,
        )

    return componente


# ─────────────────────────────────────────────────────────────
# T19 / T26 — Corregir una finalización (RF-COT-10)
# ─────────────────────────────────────────────────────────────

def corregir_finalizacion(
    *, servicio, componente_id, nuevo_estado, comentario='', usuario=None,
):
    """Corrige un cierre mal registrado, dejando rastro del estado anterior."""
    componente = _componente_de_servicio(servicio, componente_id)

    if componente.estado not in ESTADOS_FINALIZACION:
        raise ErrorDeAccion(
            'Solo se pueden corregir estados de finalización.', 409,
        )

    with transaction.atomic():
        estado_anterior = componente.estado
        componente.estado = nuevo_estado
        componente.save(update_fields=['estado'])
        HistorialComponente.objects.create(
            componente=componente,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            comentario=comentario or 'Corrección de finalización',
            usuario=usuario,
        )

    return componente


# ─────────────────────────────────────────────────────────────
# T20 / T27 — Finalizar el servicio (RF-COT-11)
# ─────────────────────────────────────────────────────────────

def finalizar_servicio(*, servicio, usuario=None):
    """Cierra el servicio. El cierre nunca es automático (glosario 4.9)."""
    if servicio.estado == EstadoServicio.FINALIZADO:
        raise ErrorDeAccion('El servicio ya está finalizado.', 409)

    hoy = construir_hoy(servicio)
    if not puede_finalizar_servicio(hoy):
        raise ErrorDeAccion(
            'El servicio no se puede finalizar todavía.', 409,
            {'resumen_cierre': resumen_cierre(hoy)},
        )

    detalle = resumen_cierre(hoy)['detalle']
    with transaction.atomic():
        servicio.estado = EstadoServicio.FINALIZADO
        servicio.fecha_finalizacion = timezone.now()
        servicio.save(update_fields=['estado', 'fecha_finalizacion'])
        HistorialServicio.objects.create(
            servicio=servicio,
            estado=EstadoServicio.FINALIZADO,
            comentario=detalle,
            usuario=usuario,
            visible_cliente=False,
        )

    return servicio