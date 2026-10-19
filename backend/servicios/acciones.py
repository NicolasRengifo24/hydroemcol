"""Acciones atómicas del flujo simplificado de estados (spec 008)."""

from django.db import transaction
from django.utils import timezone

from .estados import ESTADOS_FINALIZACION, EstadoComponente, EstadoFaseComponente
from .models import (AprobacionServicio, Componente, Cotizacion, EstadoCotizacion,
                     EstadoServicio, HistorialComponente, HistorialServicio,
                     MedioAprobacion, Fotografia, RegistroTecnico, Servicio)
from .reglas import (ESTADOS_SERVICIO_CERRADOS, es_cambio_fuera_de_pendiente,
                     puede_cancelar_servicio, puede_finalizar_servicio,
                     resolver_transicion_componente, resumen_cierre,
                     transicion_por_cotizacion, transicion_por_respuesta)
from .serializers import construir_hoy


class ErrorDeAccion(Exception):
    def __init__(self, detalle, codigo=400, extra=None):
        super().__init__(detalle)
        self.detalle, self.codigo, self.extra = detalle, codigo, extra or {}


def _servicio_bloqueado(servicio_id):
    return Servicio.objects.select_for_update().get(pk=servicio_id)


def _historial_accion(servicio, comentario, usuario):
    return HistorialServicio.objects.create(servicio=servicio, estado=servicio.estado,
                                            comentario=comentario, usuario=usuario,
                                            visible_cliente=False)


def _componente_bloqueado(servicio, componente_id):
    componente = Componente.objects.select_for_update().filter(
        pk=componente_id, servicio_id=servicio.pk).first()
    if componente is None:
        raise ErrorDeAccion('El componente no pertenece a ese servicio.', 404)
    return componente


def resumen_de_cierre(servicio):
    return resumen_cierre(construir_hoy(servicio))


def _aplicar_inicio_trabajo(componente):
    componente.estado = EstadoComponente.OPERARIO_TRABAJANDO
    componente.fase = EstadoFaseComponente.DESMONTAJE_INICIADO
    componente.trabajo_iniciado = True
    if componente.fecha_inicio_trabajo is None:
        componente.fecha_inicio_trabajo = timezone.now()
    return ['estado', 'fase', 'trabajo_iniciado', 'fecha_inicio_trabajo']


def _origen_espera(componente):
    historial = componente.historial.filter(
        estado_nuevo=EstadoComponente.ESPERANDO_APROBACION).order_by('-fecha').first()
    return historial.estado_anterior if historial else None


def _aplicar_respuesta(servicio, componente, cotizacion, resultado, usuario):
    destino = transicion_por_respuesta(construir_hoy(servicio),
                                       {'id': componente.pk, 'estado': componente.estado},
                                       resultado, _origen_espera(componente))
    if destino is None:
        return
    anterior = componente.estado
    if destino == EstadoComponente.OPERARIO_TRABAJANDO:
        campos = _aplicar_inicio_trabajo(componente)
    else:
        componente.estado = destino
        campos = ['estado']
    componente.save(update_fields=campos)
    HistorialComponente.objects.create(componente=componente, estado_anterior=anterior,
        estado_nuevo=destino, fase_registrada=componente.fase if destino == EstadoComponente.EN_PRUEBAS else '',
        comentario=f'Respuesta {resultado} de la cotización {cotizacion.numero}.', usuario=usuario)


def registrar_respuesta(*, servicio, componente_id, cotizacion_id, resultado, canal,
                        observacion='', usuario=None, ip=None):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if servicio.estado in ESTADOS_SERVICIO_CERRADOS:
            raise ErrorDeAccion('El servicio está cerrado y no admite respuestas.', 409)
        componente = _componente_bloqueado(servicio, componente_id)
        cotizacion = Cotizacion.objects.select_for_update().filter(
            pk=cotizacion_id, servicio_id=servicio.pk, componente_id=componente.pk).first()
        if cotizacion is None:
            raise ErrorDeAccion('La cotización no pertenece a ese componente.', 404)
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
            aprobacion = cotizacion.aprobaciones.order_by('fecha_registro').first()
            if aprobacion and aprobacion.resultado == resultado:
                return aprobacion
            raise ErrorDeAccion('La cotización ya tiene una respuesta contradictoria.', 409)
        aprobacion = AprobacionServicio.objects.create(cotizacion=cotizacion, resultado=resultado,
            medio=canal, usuario_registro=usuario, fecha=timezone.now(), observacion=observacion, ip=ip)
        cotizacion.estado, cotizacion.canal = resultado, canal
        cotizacion.save(update_fields=['estado', 'canal'])
        _aplicar_respuesta(servicio, componente, cotizacion, resultado, usuario)
        _historial_accion(servicio, f'Respuesta {resultado} registrada para {cotizacion.numero}.', usuario)
        return aprobacion


def cambiar_estado_componente(*, servicio, componente_id, nuevo_estado, comentario='', usuario=None):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if servicio.estado in ESTADOS_SERVICIO_CERRADOS:
            raise ErrorDeAccion('El servicio está cerrado y no admite cambios de estado.', 409)
        componente = _componente_bloqueado(servicio, componente_id)
        hoy = construir_hoy(servicio)
        dato = next(c for c in hoy['componentes'] if c['id'] == componente.pk)
        decision = resolver_transicion_componente(hoy, dato, nuevo_estado, comentario)
        if not decision['permitido']:
            raise ErrorDeAccion(decision['motivo'], decision['codigo'], decision['extra'])
        if decision['tipo'] == 'noop':
            return componente
        anterior = componente.estado
        if decision['tipo'] == 'finalizar':
            componente.estado = nuevo_estado
            componente.motivo_finalizacion = comentario.strip()
            componente.fecha_finalizacion = timezone.now()
            campos = ['estado', 'motivo_finalizacion', 'fecha_finalizacion']
        elif decision['tipo'] == 'correccion':
            componente.estado = nuevo_estado
            componente.motivo_finalizacion = ''
            componente.fecha_finalizacion = None
            campos = ['estado', 'motivo_finalizacion', 'fecha_finalizacion']
        else:
            componente.estado = nuevo_estado
            campos = ['estado']
        componente.save(update_fields=campos)
        HistorialComponente.objects.create(componente=componente, estado_anterior=anterior,
            estado_nuevo=nuevo_estado, fase_registrada=componente.fase if decision['tipo'] == 'normal' else '',
            comentario=comentario, usuario=usuario)
        nuevo_hoy = dict(hoy, componentes=[dict(dato, estado=nuevo_estado)])
        if es_cambio_fuera_de_pendiente(dato, nuevo_hoy) and servicio.estado == EstadoServicio.SOLICITADO:
            servicio.estado = EstadoServicio.EN_CURSO
            servicio.save(update_fields=['estado'])
            _historial_accion(servicio, 'El primer componente salió de pendiente.', usuario)
        return componente


def finalizar_servicio(*, servicio, comentario='', usuario=None):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if servicio.estado in ESTADOS_SERVICIO_CERRADOS:
            raise ErrorDeAccion('El servicio está cerrado y no admite cambios.', 409)
        hoy = construir_hoy(servicio)
        if not puede_finalizar_servicio(hoy):
            resumen = resumen_cierre(hoy)
            raise ErrorDeAccion(resumen['detalle'], 409, {'resumen_cierre': resumen})
        servicio.estado = EstadoServicio.FINALIZADO
        servicio.fecha_finalizacion = timezone.now()
        servicio.save(update_fields=['estado', 'fecha_finalizacion'])
        HistorialServicio.objects.create(servicio=servicio, estado=servicio.estado,
            comentario=comentario, usuario=usuario, visible_cliente=False)
        return servicio


def cancelar_servicio(*, servicio, comentario, usuario=None):
    if not (comentario or '').strip():
        raise ErrorDeAccion('La cancelación requiere un comentario.', 400)
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if not puede_cancelar_servicio(construir_hoy(servicio)):
            raise ErrorDeAccion('El servicio no admite cancelación en su estado actual.', 409)
        servicio.estado = EstadoServicio.CANCELADO
        servicio.save(update_fields=['estado'])
        HistorialServicio.objects.create(servicio=servicio, estado=servicio.estado,
            comentario=comentario, usuario=usuario, visible_cliente=False)
        return servicio


def cambiar_estado_servicio(*, servicio, destino, comentario='', usuario=None):
    """Compatibilidad con la vista antigua; el servicio ya no tiene selector."""
    if destino == EstadoServicio.FINALIZADO:
        return finalizar_servicio(servicio=servicio, comentario=comentario, usuario=usuario)
    if destino == EstadoServicio.CANCELADO:
        return cancelar_servicio(servicio=servicio, comentario=comentario, usuario=usuario)
    if destino == servicio.estado:
        return servicio
    raise ErrorDeAccion('El servicio solo admite finalizar o cancelar.', 409)


def crear_cotizacion(*, datos, usuario):
    datos = dict(datos)
    detalles = datos.pop('detalles', [])
    servicio = datos.pop('servicio')
    componente = datos.pop('componente', None)
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio.pk)
        if componente is None:
            raise ErrorDeAccion('La cotización debe pertenecer a un componente.', 400)
        componente = _componente_bloqueado(servicio, componente.pk)
        if servicio.estado in ESTADOS_SERVICIO_CERRADOS:
            raise ErrorDeAccion('El servicio está cerrado y no admite cotizaciones.', 409)
        datos.update(servicio=servicio, componente=componente, creada_por=usuario,
                     estado=EstadoCotizacion.PENDIENTE)
        cotizacion = Cotizacion.objects.create(**datos)
        for detalle in detalles:
            cotizacion.detalles.create(**detalle)
        cotizacion.total = sum(d['valor'] * d['cantidad'] for d in detalles)
        cotizacion.save(update_fields=['total'])
        destino = transicion_por_cotizacion(construir_hoy(servicio),
                                            {'id': componente.pk, 'estado': componente.estado})
        if destino:
            anterior = componente.estado
            componente.estado = destino
            componente.save(update_fields=['estado'])
            HistorialComponente.objects.create(componente=componente, estado_anterior=anterior,
                estado_nuevo=destino, comentario=f'Cotización {cotizacion.numero} registrada.', usuario=usuario)
        _historial_accion(servicio, f'Cotización {cotizacion.numero} creada.', usuario)
        return cotizacion


def registrar_aprobacion_externa(*, cotizacion_id, resultado, medio, usuario, observacion='', fecha=None, ip=None):
    with transaction.atomic():
        cotizacion = Cotizacion.objects.select_for_update().get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(cotizacion.servicio_id)
        componente = _componente_bloqueado(servicio, cotizacion.componente_id) if cotizacion.componente_id else None
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
            aprobacion = cotizacion.aprobaciones.order_by('fecha_registro').first()
            if aprobacion and aprobacion.resultado == resultado:
                return aprobacion
            raise ErrorDeAccion('La cotización ya tiene una respuesta contradictoria.', 409)
        aprobacion = AprobacionServicio.objects.create(cotizacion=cotizacion, resultado=resultado,
            medio=medio, fecha=fecha or timezone.now(), usuario_registro=usuario,
            observacion=observacion, ip=ip)
        cotizacion.estado = resultado
        cotizacion.save(update_fields=['estado'])
        if componente:
            _aplicar_respuesta(servicio, componente, cotizacion, resultado, usuario)
        _historial_accion(servicio, f'Respuesta externa registrada para {cotizacion.numero}.', usuario)
        return aprobacion


# Compatibilidad temporal para callers de T5; la API nueva usa la rama unificada.
def iniciar_trabajo(*, servicio, componente_id, usuario=None):
    return cambiar_estado_componente(servicio=servicio, componente_id=componente_id,
                                      nuevo_estado=EstadoComponente.OPERARIO_TRABAJANDO, usuario=usuario)


def finalizar_componente(*, servicio, componente_id, motivo, usuario=None):
    return cambiar_estado_componente(servicio=servicio, componente_id=componente_id,
                                      nuevo_estado=motivo, comentario=motivo, usuario=usuario)


def corregir_finalizacion(*, servicio, componente_id, nuevo_estado, comentario='', usuario=None):
    return cambiar_estado_componente(servicio=servicio, componente_id=componente_id,
                                      nuevo_estado=nuevo_estado, comentario=comentario, usuario=usuario)


def desactivar_servicio(*, servicio_id, usuario=None):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        if not servicio.activo:
            raise ErrorDeAccion('El servicio ya está desactivado.', 409)
        servicio.activo = False
        servicio.save(update_fields=['activo'])
        _historial_accion(servicio, 'Servicio desactivado de la operación ordinaria.', usuario)
        return servicio


def editar_cotizacion(*, cotizacion_id, datos, usuario):
    with transaction.atomic():
        cotizacion = Cotizacion.objects.select_for_update().get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(cotizacion.servicio_id)
        if cotizacion.estado != EstadoCotizacion.PENDIENTE:
            raise ErrorDeAccion('Solo se pueden editar cotizaciones pendientes.', 409)
        for campo, valor in datos.items():
            if campo != 'detalles':
                setattr(cotizacion, campo, valor)
        cotizacion.save()
        _historial_accion(servicio, f'Cotización {cotizacion.numero} editada.', usuario)
        return cotizacion


def reenviar_cotizacion(*, cotizacion_id, datos, usuario):
    with transaction.atomic():
        anterior = Cotizacion.objects.select_for_update().get(pk=cotizacion_id)
        servicio = _servicio_bloqueado(anterior.servicio_id)
        componente = _componente_bloqueado(servicio, anterior.componente_id) if anterior.componente_id else None
        if anterior.estado != EstadoCotizacion.RECHAZADA:
            raise ErrorDeAccion('Solo se pueden reenviar cotizaciones rechazadas.', 409)
        nueva = Cotizacion.objects.create(servicio=servicio, componente=componente, tipo=anterior.tipo,
            es_bloqueante=anterior.es_bloqueante, descripcion=datos.get('descripcion', anterior.descripcion),
            observaciones=datos.get('observaciones', anterior.observaciones), creada_por=usuario,
            estado=EstadoCotizacion.PENDIENTE, reemplaza_a=anterior)
        _historial_accion(servicio, f'Cotización {anterior.numero} reenviada como {nueva.numero}.', usuario)
        return nueva


def guardar_registro_tecnico(*, servicio_id, datos, usuario):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        registro, creado = RegistroTecnico.objects.get_or_create(servicio=servicio, defaults={**datos, 'creado_por': usuario, 'actualizado_por': usuario})
        if not creado:
            for campo, valor in datos.items(): setattr(registro, campo, valor)
            registro.actualizado_por = usuario
            registro.save()
        _historial_accion(servicio, 'Registro técnico actualizado.', usuario)
        return registro


def crear_fotografia(*, servicio_id, datos, usuario, archivo=None):
    from .almacenamiento import guardar_fotografia
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        if Fotografia.objects.filter(servicio_id=servicio.pk).count() >= 10:
            raise ErrorDeAccion('El servicio ya tiene el máximo de 10 fotografías.', 409)
        if archivo is not None: datos['url'] = guardar_fotografia(archivo)
        fotografia = Fotografia.objects.create(servicio=servicio, subida_por=usuario, **datos)
        _historial_accion(servicio, 'Fotografía agregada.', usuario)
        return fotografia


def actualizar_fotografia(*, servicio_id, fotografia_id, datos, usuario):
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        fotografia = Fotografia.objects.select_for_update().filter(pk=fotografia_id, servicio_id=servicio.pk).first()
        if fotografia is None: raise ErrorDeAccion('La fotografía no pertenece a ese servicio.', 404)
        for campo, valor in datos.items(): setattr(fotografia, campo, valor)
        fotografia.save()
        _historial_accion(servicio, 'Fotografía actualizada.', usuario)
        return fotografia


def eliminar_fotografia(*, servicio_id, fotografia_id, usuario):
    from .almacenamiento import eliminar_referencia
    with transaction.atomic():
        servicio = _servicio_bloqueado(servicio_id)
        fotografia = Fotografia.objects.select_for_update().filter(pk=fotografia_id, servicio_id=servicio.pk).first()
        if fotografia is None: raise ErrorDeAccion('La fotografía no pertenece a ese servicio.', 404)
        eliminar_referencia(fotografia.url)
        fotografia.delete()
        return None
