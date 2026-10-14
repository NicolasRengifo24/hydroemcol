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
    MedioAprobacion,
    Fotografia,
    RegistroTecnico,
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


def _servicio_bloqueado(servicio_id):
    return Servicio.objects.select_for_update().get(pk=servicio_id)


def _historial_accion(servicio, comentario, usuario):
    HistorialServicio.objects.create(
        servicio=servicio, estado=servicio.estado, comentario=comentario,
        usuario=usuario, visible_cliente=False,
    )


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
        servicio = _servicio_bloqueado(servicio.pk)
        componente = Componente.objects.select_for_update().filter(
            pk=componente_id, servicio_id=servicio.pk,
        ).first()
        cotizacion = Cotizacion.objects.select_for_update().filter(
            pk=cotizacion_id, servicio_id=servicio.pk,
        ).first()
        if componente is None:
            raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)
        if cotizacion is None:
            raise ErrorDeAccion('La cotización no pertenece a ese servicio.', 404)
        if cotizacion.componente_id != componente.pk:
            raise ErrorDeAccion('La cotización no pertenece a ese componente.', 400)
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
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
        _historial_accion(
            servicio, f'Respuesta {resultado} registrada para la cotización {cotizacion.numero}.', usuario,
        )

    return aprobacion


# ─────────────────────────────────────────────────────────────
# T17 / T26 — Iniciar trabajo (RF-COT-04, RF-COT-08)
# ─────────────────────────────────────────────────────────────

def iniciar_trabajo(*, servicio, componente_id, usuario=None):
    """Registra el inicio del trabajo. Aplica RF-COT-04: lo bloquea la API."""
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        componente = Componente.objects.select_for_update().filter(
            pk=componente_id, servicio_id=servicio.pk,
        ).first()
        if componente is None:
            raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)
        hoy = construir_hoy(servicio)
        componente_hoy = next(c for c in hoy['componentes'] if c['id'] == componente.pk)
        if componente.trabajo_iniciado or not puede_continuar(hoy, componente_hoy):
            raise ErrorDeAccion(
                'El componente no puede iniciar trabajo: '
                f'{motivo_bloqueo(hoy, componente_hoy) or "el trabajo ya fue iniciado"}', 409,
            )
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
        _historial_accion(servicio, 'Inicio de trabajo registrado en el componente.', usuario)

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
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        componente = Componente.objects.select_for_update().filter(
            pk=componente_id, servicio_id=servicio.pk,
        ).first()
        if componente is None:
            raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)
        if componente.estado in ESTADOS_FINALIZACION:
            raise ErrorDeAccion('El componente ya está finalizado.', 409)
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
        _historial_accion(servicio, f'Componente finalizado: {motivo}.', usuario)

    return componente


# ─────────────────────────────────────────────────────────────
# T19 / T26 — Corregir una finalización (RF-COT-10)
# ─────────────────────────────────────────────────────────────

def corregir_finalizacion(
    *, servicio, componente_id, nuevo_estado, comentario='', usuario=None,
):
    """Corrige un cierre mal registrado, dejando rastro del estado anterior."""
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        componente = Componente.objects.select_for_update().filter(
            pk=componente_id, servicio_id=servicio.pk,
        ).first()
        if componente is None:
            raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)
        if componente.estado not in ESTADOS_FINALIZACION:
            raise ErrorDeAccion('Solo se pueden corregir estados de finalización.', 409)
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
        _historial_accion(servicio, 'Corrección de finalización registrada.', usuario)

    return componente


# ─────────────────────────────────────────────────────────────
# T20 / T27 — Finalizar el servicio (RF-COT-11)
# ─────────────────────────────────────────────────────────────

def finalizar_servicio(*, servicio, usuario=None):
    """Cierra el servicio. El cierre nunca es automático (glosario 4.9)."""
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if servicio.estado == EstadoServicio.FINALIZADO:
            raise ErrorDeAccion('El servicio ya está finalizado.', 409)
        hoy = construir_hoy(servicio)
        if not puede_finalizar_servicio(hoy):
            raise ErrorDeAccion(
                'El servicio no se puede finalizar todavía.', 409,
                {'resumen_cierre': resumen_cierre(hoy)},
            )
        detalle = resumen_cierre(hoy)['detalle']
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


def desactivar_servicio(*, servicio_id, usuario=None):
    """Retira un servicio de la operación sin borrar su trazabilidad."""
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        if not servicio.activo:
            raise ErrorDeAccion('El servicio ya está desactivado.', 409)
        servicio.activo = False
        servicio.save(update_fields=['activo'])
        _historial_accion(servicio, 'Servicio desactivado de la operación ordinaria.', usuario)
    return servicio


def crear_cotizacion(*, datos, usuario):
    detalles = datos.pop('detalles', [])
    servicio = datos['servicio']
    componente = datos.get('componente')
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if componente is not None:
            componente = Componente.objects.select_for_update().filter(
                pk=componente.pk, servicio_id=servicio.pk,
            ).first()
            if componente is None:
                raise ErrorDeAccion('El componente no pertenece a ese servicio.', 400)
        datos.update(servicio=servicio, componente=componente, creada_por=usuario,
                     estado=EstadoCotizacion.PENDIENTE)
        cotizacion = Cotizacion.objects.create(**datos)
        for detalle in detalles:
            cotizacion.detalles.create(**detalle)
        cotizacion.total = sum(d['valor'] * d['cantidad'] for d in detalles)
        cotizacion.save(update_fields=['total'])
        _historial_accion(servicio, f'Cotización {cotizacion.numero} creada.', usuario)
    return cotizacion


def editar_cotizacion(*, cotizacion_id, datos, usuario):
    detalles = datos.pop('detalles', None)
    with transaction.atomic():
        cotizacion = Cotizacion.objects.select_for_update().select_related('servicio').get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(cotizacion.servicio_id)
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
            raise ErrorDeAccion('Solo se pueden editar cotizaciones pendientes.', 409)
        componente = datos.pop('componente', cotizacion.componente)
        if componente is not None and componente.servicio_id != servicio.pk:
            raise ErrorDeAccion('El componente no pertenece a ese servicio.', 400)
        for campo, valor in datos.items():
            setattr(cotizacion, campo, valor)
        cotizacion.componente = componente
        if detalles is not None:
            cotizacion.detalles.all().delete()
            for detalle in detalles:
                cotizacion.detalles.create(**detalle)
            cotizacion.total = sum(d['valor'] * d['cantidad'] for d in detalles)
        cotizacion.save()
        _historial_accion(servicio, f'Cotización {cotizacion.numero} editada.', usuario)
    return cotizacion


def reenviar_cotizacion(*, cotizacion_id, datos, usuario):
    detalles = datos.pop('detalles', [])
    with transaction.atomic():
        # PostgreSQL no permite combinar FOR UPDATE con el OUTER JOIN que
        # produce `select_related` sobre el componente opcional. Se bloquea
        # primero la cotización y después, de forma explícita, el servicio y
        # el componente: así se conserva el contrato de concurrencia sin
        # intentar bloquear el lado nullable del join.
        anterior = Cotizacion.objects.select_for_update().get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(anterior.servicio_id)
        componente = None
        if anterior.componente_id:
            componente = Componente.objects.select_for_update().get(
                pk=anterior.componente_id, servicio_id=servicio.pk,
            )
        if anterior.estado != EstadoCotizacion.RECHAZADA:
            raise ErrorDeAccion('Solo se pueden reenviar cotizaciones rechazadas.', 409)
        nueva = Cotizacion.objects.create(
            servicio=servicio, componente=componente, tipo=anterior.tipo,
            es_bloqueante=anterior.es_bloqueante,
            descripcion=datos.get('descripcion', anterior.descripcion),
            observaciones=datos.get('observaciones', anterior.observaciones),
            creada_por=usuario, estado=EstadoCotizacion.PENDIENTE,
            reemplaza_a=anterior,
        )
        for detalle in detalles:
            nueva.detalles.create(**detalle)
        nueva.total = sum(d['valor'] * d['cantidad'] for d in detalles)
        nueva.save(update_fields=['total'])
        _historial_accion(servicio, f'Cotización {anterior.numero} reenviada como {nueva.numero}.', usuario)
    return nueva


def registrar_aprobacion_externa(*, cotizacion_id, resultado, medio, usuario, observacion='', fecha=None, ip=None):
    """Registra una respuesta administrativa sin confundir medio con canal."""
    with transaction.atomic():
        cotizacion = Cotizacion.objects.select_for_update().select_related('servicio').get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(cotizacion.servicio_id)
        componente = None
        if cotizacion.componente_id:
            componente = Componente.objects.select_for_update().get(pk=cotizacion.componente_id)
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
            raise ErrorDeAccion('Esa cotización ya tiene respuesta.', 409)
        aprobacion = AprobacionServicio.objects.create(
            cotizacion=cotizacion, resultado=resultado, medio=medio,
            fecha=fecha or timezone.now(), usuario_registro=usuario,
            observacion=observacion, ip=ip,
        )
        cotizacion.estado = resultado
        if medio in (MedioAprobacion.WEB, MedioAprobacion.WHATSAPP):
            cotizacion.canal = medio
            cotizacion.save(update_fields=['estado', 'canal'])
        else:
            cotizacion.save(update_fields=['estado'])
        if componente is not None:
            hoy = construir_hoy(servicio)
            dato = next(c for c in hoy['componentes'] if c['id'] == componente.pk)
            estado_nuevo = estado_por_rechazo_bloqueante(hoy, dato)
            if estado_nuevo and componente.estado != estado_nuevo:
                anterior = componente.estado
                componente.estado = estado_nuevo
                componente.save(update_fields=['estado'])
                HistorialComponente.objects.create(
                    componente=componente, estado_anterior=anterior,
                    estado_nuevo=estado_nuevo,
                    comentario='Cotización bloqueante rechazada.', usuario=usuario,
                )
        _historial_accion(servicio, f'Respuesta externa registrada para {cotizacion.numero}.', usuario)
    return aprobacion


def guardar_registro_tecnico(*, servicio_id, datos, usuario):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        registro = RegistroTecnico.objects.select_for_update().filter(servicio_id=servicio.pk).first()
        if registro is None:
            registro = RegistroTecnico.objects.create(
                servicio=servicio, creado_por=usuario, actualizado_por=usuario, **datos,
            )
        else:
            for campo, valor in datos.items():
                setattr(registro, campo, valor)
            registro.actualizado_por = usuario
            registro.save()
        _historial_accion(servicio, 'Registro técnico actualizado.', usuario)
    return registro


def crear_fotografia(*, servicio_id, datos, usuario, archivo=None):
    from .almacenamiento import guardar_fotografia, eliminar_referencia
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        if Fotografia.objects.filter(servicio_id=servicio.pk).count() >= 10:
            raise ErrorDeAccion('El servicio ya tiene el máximo de 10 fotografías.', 409)
        if archivo is not None:
            datos['url'] = guardar_fotografia(archivo)
        try:
            fotografia = Fotografia.objects.create(servicio=servicio, subida_por=usuario, **datos)
        except Exception:
            if archivo is not None and datos.get('url'):
                eliminar_referencia(datos['url'])
            raise
        _historial_accion(servicio, 'Fotografía agregada.', usuario)
    return fotografia


def actualizar_fotografia(*, servicio_id, fotografia_id, datos, usuario):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        fotografia = Fotografia.objects.select_for_update().filter(
            pk=fotografia_id, servicio_id=servicio.pk,
        ).first()
        if fotografia is None:
            raise ErrorDeAccion('La fotografía no pertenece a ese servicio.', 404)
        for campo, valor in datos.items():
            setattr(fotografia, campo, valor)
        fotografia.save()
        _historial_accion(servicio, 'Fotografía actualizada.', usuario)
    return fotografia


def eliminar_fotografia(*, servicio_id, fotografia_id, usuario):
    from .almacenamiento import eliminar_referencia
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        fotografia = Fotografia.objects.select_for_update().filter(
            pk=fotografia_id, servicio_id=servicio.pk,
        ).first()
        if fotografia is None:
            raise ErrorDeAccion('La fotografía no pertenece a ese servicio.', 404)
        try:
            eliminar_referencia(fotografia.url)
        except Exception as error:
            raise ErrorDeAccion(f'No se pudo eliminar el archivo: {error}', 409)
        fotografia.delete()
    return None
