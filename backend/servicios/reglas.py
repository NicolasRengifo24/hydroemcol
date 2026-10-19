"""Reglas puras del flujo simplificado de la spec 008.

Las funciones reciben el snapshot ``hoy`` construido por los serializers y no
leen reloj ni base de datos. ``token`` significa la credencial privada de
seguimiento; un rechazo de cliente es una respuesta no bloqueante para el
estado del componente: no lo mueve.
"""

from servicios.estados import ESTADOS_FINALIZACION, EstadoComponente
from servicios.models import EstadoServicio


ESTADOS_SERVICIO_NORMALES = (EstadoServicio.SOLICITADO, EstadoServicio.EN_CURSO)
ESTADOS_SERVICIO_CERRADOS = (EstadoServicio.FINALIZADO, EstadoServicio.CANCELADO)
ESTADOS_SELECCIONABLES_COMPONENTE = tuple(EstadoComponente.values)

# Tabla §4.1: solo destinos decididos manualmente por el administrativo.
TRANSICIONES_MANUALES_COMPONENTE = {
    EstadoComponente.PENDIENTE: [EstadoComponente.EN_REVISION],
    EstadoComponente.EN_REVISION: [EstadoComponente.COTIZANDO],
    EstadoComponente.COTIZANDO: [],
    EstadoComponente.ESPERANDO_APROBACION: [EstadoComponente.RECHAZADO],
    EstadoComponente.OPERARIO_TRABAJANDO: [EstadoComponente.EN_PRUEBAS],
    EstadoComponente.EN_PRUEBAS: [EstadoComponente.LISTO_PARA_ENTREGA],
    EstadoComponente.LISTO_PARA_ENTREGA: [EstadoComponente.EN_PRUEBAS],
    EstadoComponente.RECHAZADO: [EstadoComponente.ESPERANDO_APROBACION],
}


def _cotizaciones_de(hoy, componente):
    return hoy.get('cotizaciones_por_componente', {}).get(componente.get('id'), [])


def tiene_trabajo_iniciado(hoy, componente):
    """Dato informativo conservado para compatibilidad con acciones antiguas."""
    return bool(componente.get('trabajo_iniciado', False))


def requiere_motivo(destino):
    """Indica si el destino es una finalización; la corrección depende del origen."""
    return destino in ESTADOS_FINALIZACION


def estados_componente_seleccionables(hoy, componente):
    """Destinos manuales válidos; los automáticos nunca aparecen aquí."""
    return list(TRANSICIONES_MANUALES_COMPONENTE.get(componente.get('estado'), []))


def _decision(**cambios):
    resultado = {'permitido': False, 'tipo': None, 'codigo': None,
                 'motivo': '', 'extra': {}}
    resultado.update(cambios)
    return resultado


def resolver_transicion_componente(hoy, componente, destino, comentario=''):
    """Valida un destino manual, un noop o una transición no listada.

    Un destino de catálogo no listado devuelve 409; un código desconocido 400.
    ``RECHAZADO`` solo es posible si existe una cotización rechazada.
    """
    if destino not in ESTADOS_SELECCIONABLES_COMPONENTE:
        return _decision(codigo=400, motivo='Ese estado no puede asignarse manualmente.')
    if destino == componente.get('estado'):
        return _decision(permitido=True, tipo='noop', codigo=200)
    destinos = estados_componente_seleccionables(hoy, componente)
    if destino not in destinos:
        return _decision(codigo=409, motivo='La transición no está permitida.')
    requiere_comentario = (
        destino in ESTADOS_FINALIZACION
        or componente.get('estado') in ESTADOS_FINALIZACION
    )
    if requiere_comentario and not str(comentario or '').strip():
        return _decision(codigo=400, motivo='Este cambio requiere un motivo o comentario.')
    if destino == EstadoComponente.RECHAZADO:
        if not any(c.get('estado') == 'RECHAZADA' for c in _cotizaciones_de(hoy, componente)):
            return _decision(codigo=409, motivo='Se requiere una cotización rechazada.')
        return _decision(permitido=True, tipo='finalizar', codigo=200)
    tipo = 'correccion' if componente.get('estado') in ESTADOS_FINALIZACION else 'normal'
    if destino in ESTADOS_FINALIZACION:
        tipo = 'finalizar'
    return _decision(permitido=True, tipo=tipo, codigo=200)


def es_cambio_fuera_de_pendiente(componente_anterior, componente_hoy):
    return (componente_anterior.get('estado') == EstadoComponente.PENDIENTE
            and componente_hoy.get('estado') != EstadoComponente.PENDIENTE)


def transicion_por_respuesta(hoy, componente, resultado, origen_espera):
    """Aprobación automática; rechazo deja el componente donde estaba."""
    if componente.get('estado') != EstadoComponente.ESPERANDO_APROBACION:
        return None
    if resultado != 'APROBADA':
        return None
    if origen_espera == EstadoComponente.LISTO_PARA_ENTREGA:
        return EstadoComponente.EN_PRUEBAS
    return EstadoComponente.OPERARIO_TRABAJANDO


def transicion_por_cotizacion(hoy, componente):
    if componente.get('estado') in (
        EstadoComponente.COTIZANDO, EstadoComponente.OPERARIO_TRABAJANDO,
        EstadoComponente.EN_PRUEBAS, EstadoComponente.LISTO_PARA_ENTREGA,
    ):
        return EstadoComponente.ESPERANDO_APROBACION
    return None


def componentes_no_finalizados(hoy):
    return [c for c in hoy.get('componentes', [])
            if c.get('estado') not in ESTADOS_FINALIZACION]


def puede_finalizar_servicio(hoy):
    return bool(hoy.get('componentes')) and not componentes_no_finalizados(hoy)


def resumen_cierre(hoy):
    impeditivos = [c.get('id') for c in componentes_no_finalizados(hoy)]
    if not hoy.get('componentes'):
        return {'puede_finalizar': False, 'caso': 'SIN_COMPONENTES',
                'detalle': 'El servicio no tiene componentes que cerrar',
                'impeditivos': []}
    if impeditivos:
        return {'puede_finalizar': False, 'caso': 'COMPONENTES_PENDIENTES',
                'detalle': 'Quedan componentes sin finalizar: ' + ', '.join(map(str, impeditivos)),
                'impeditivos': impeditivos}
    return {'puede_finalizar': True, 'caso': 'TODOS_FINALIZADOS',
            'detalle': 'Todos los componentes están finalizados', 'impeditivos': []}


def estados_servicio_seleccionables(hoy):
    return []


def puede_cancelar_servicio(hoy):
    return bool(hoy.get('activo', False)) and hoy.get('estado') not in ESTADOS_SERVICIO_CERRADOS


def estados_cerrados():
    return ESTADOS_SERVICIO_CERRADOS


# Compatibilidad temporal para imports de acciones.py/serializers.py (T4 los
# retirará). No son usadas por las reglas nuevas.
def tiene_bloqueo_cotizacion(hoy, componente):
    return any(c.get('es_bloqueante') and c.get('estado') in ('PENDIENTE', 'RECHAZADA')
               for c in _cotizaciones_de(hoy, componente))


def puede_continuar(hoy, componente):
    return componente.get('estado') not in ESTADOS_FINALIZACION and not tiene_bloqueo_cotizacion(hoy, componente)


def estado_por_rechazo_bloqueante(hoy, componente):
    return None


def todos_rechazan_bloqueantes(hoy):
    return False


def motivo_bloqueo(hoy, componente):
    return None


def fecha_para_estado_servicio(destino):
    return 'fecha_finalizacion' if destino == EstadoServicio.FINALIZADO else None


def resolver_transicion_servicio(hoy, destino, comentario=''):
    """Compatibilidad hasta T4; el selector libre de servicio sigue vacío."""
    if destino not in ESTADOS_SERVICIO_NORMALES + ESTADOS_SERVICIO_CERRADOS:
        return _decision(codigo=400, motivo='Estado de servicio inválido.')
    if destino == hoy.get('estado'):
        return _decision(permitido=True, tipo='noop', codigo=200)
    if not hoy.get('activo') or hoy.get('estado') in ESTADOS_SERVICIO_CERRADOS:
        return _decision(codigo=409, motivo='El servicio está cerrado o desactivado.')
    if destino == EstadoServicio.CANCELADO and not str(comentario or '').strip():
        return _decision(codigo=400, motivo='La cancelación requiere un comentario.')
    if destino == EstadoServicio.FINALIZADO and not puede_finalizar_servicio(hoy):
        return _decision(codigo=409, motivo=resumen_cierre(hoy)['detalle'],
                        extra={'resumen_cierre': resumen_cierre(hoy)})
    return _decision(permitido=True, tipo='cancelar' if destino == EstadoServicio.CANCELADO else 'normal', codigo=200)


def tiene_solicitud_en_curso(hoy, *, correo_norm=None, telefono_norm=None, whatsapp_norm=None):
    from django.db.models import Q
    from servicios.models import Servicio
    q = Q()
    if correo_norm:
        q |= Q(cliente__email=correo_norm)
    if telefono_norm:
        q |= Q(cliente__telefono=telefono_norm)
    if whatsapp_norm:
        q |= Q(cliente__whatsapp=whatsapp_norm)
    return bool(q) and Servicio.objects.filter(q).exclude(estado__in=estados_cerrados()).exists()
