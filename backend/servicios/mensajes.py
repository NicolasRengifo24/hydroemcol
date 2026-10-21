"""Construcción pura de los mensajes preparados de WhatsApp."""


PLANTILLAS_SERVICIO = {
    'SOLICITADO': 'Hidroemcol: recibimos su solicitud {codigo}. Siga el avance en: {enlace}',
    'EN_CURSO': 'Hidroemcol: su servicio {codigo} está en curso. Siga el avance en: {enlace}',
}

PLANTILLAS_COMPONENTE = {
    'PENDIENTE': 'Hidroemcol: el componente {componente} del servicio {codigo} fue recibido.',
    'EN_REVISION': 'Hidroemcol: el componente {componente} del servicio {codigo} está en revisión.',
    'COTIZANDO': 'Hidroemcol: estamos preparando la cotización de {componente} (servicio {codigo}).',
    'ESPERANDO_APROBACION': 'Hidroemcol: {componente} (servicio {codigo}) espera su aprobación. Revise la cotización en: {enlace}',
    'OPERARIO_TRABAJANDO': 'Hidroemcol: iniciamos el trabajo en {componente} (servicio {codigo}).',
    'EN_PRUEBAS': 'Hidroemcol: {componente} (servicio {codigo}) está en pruebas.',
    'LISTO_PARA_ENTREGA': 'Hidroemcol: {componente} (servicio {codigo}) está listo para entregar.',
    'RECHAZADO': 'Hidroemcol: {componente} (servicio {codigo}) fue rechazado. Motivo: {motivo}. Detalle: {enlace}',
}

ESTADOS_SERVICIO_CERRADOS = frozenset({'FINALIZADO', 'CANCELADO'})

ETIQUETAS_ESTADO_SERVICIO = {
    'SOLICITADO': 'Solicitado',
    'EN_CURSO': 'En curso',
}

ETIQUETAS_ESTADO_COMPONENTE = {
    'PENDIENTE': 'Pendiente',
    'EN_REVISION': 'En revisión',
    'COTIZANDO': 'Cotizando',
    'ESPERANDO_APROBACION': 'Esperando aprobación',
    'OPERARIO_TRABAJANDO': 'Operario trabajando',
    'EN_PRUEBAS': 'En pruebas',
    'LISTO_PARA_ENTREGA': 'Listo para entregar',
    'RECHAZADO': 'Rechazado',
}

AVISO_SERVICIO_CERRADO = (
    'Este servicio está cerrado. No se preparan mensajes para él ni para sus componentes.'
)
AVISO_SERVICIO_DESACTIVADO = 'Este servicio está desactivado. No se preparó el mensaje.'
AVISO_SIN_NUMERO = (
    'Este cliente no tiene un número de WhatsApp registrado. No se preparó el mensaje.'
)
AVISO_DOMINIO = (
    'No está configurado el dominio de los enlaces de seguimiento. '
    'Pide a quien administra el sistema que lo configure. No se preparó el mensaje.'
)
AVISO_NO_PREPARADO = 'No se pudo preparar el mensaje. Inténtalo de nuevo.'


def enlace_seguimiento(base, token):
    """Devuelve el enlace absoluto de seguimiento o ``None`` si no es válido."""
    if not base or not isinstance(base, str):
        return None
    if not base.startswith(('http://', 'https://')):
        return None
    return f'{base.rstrip("/")}/seguimiento/{token}'


def etiqueta_componente(tipo, referencia):
    """Combina tipo y referencia sin añadir paréntesis para referencias vacías."""
    if referencia:
        return f'{tipo} ({referencia})'
    return tipo


def texto_servicio(estado, codigo, enlace):
    """Construye el texto aprobado del estado vigente del servicio."""
    plantilla = PLANTILLAS_SERVICIO.get(estado)
    if plantilla is None:
        return None
    if '{enlace}' in plantilla and not enlace:
        return None
    return plantilla.format(codigo=codigo, enlace=enlace)


def texto_componente(estado, etiqueta, codigo, enlace, motivo):
    """Construye el texto aprobado del estado vigente del componente."""
    plantilla = PLANTILLAS_COMPONENTE.get(estado)
    if plantilla is None:
        return None
    if '{enlace}' in plantilla and not enlace:
        return None
    if estado == 'RECHAZADO' and not motivo:
        return None
    return plantilla.format(
        componente=etiqueta,
        codigo=codigo,
        enlace=enlace,
        motivo=motivo,
    )


def _numero_destino(numero):
    if not isinstance(numero, str) or len(numero) != 10:
        return None
    if not numero.isdigit() or not numero.startswith('3'):
        return None
    return f'57{numero}'


def _mensaje_servicio(servicio, enlace):
    estado = servicio.get('estado')
    codigo = servicio.get('codigo')
    texto = texto_servicio(estado, codigo, enlace)
    return {
        'clave': 'servicio',
        'ambito': 'SERVICIO',
        'etiqueta': f'Servicio {codigo}',
        'estado': estado,
        'etiqueta_estado': ETIQUETAS_ESTADO_SERVICIO.get(estado, estado),
        'texto': texto,
        'aviso': None,
    }


def _mensaje_componente(componente, codigo, enlace, posicion):
    estado = componente.get('estado')
    etiqueta = etiqueta_componente(
        componente.get('tipo', ''), componente.get('referencia', '')
    )
    texto = texto_componente(
        estado,
        etiqueta,
        codigo,
        enlace,
        componente.get('motivo_finalizacion', ''),
    )
    return {
        'clave': f'componente-{estado.lower()}-{posicion}',
        'ambito': 'COMPONENTE',
        'etiqueta': etiqueta,
        'estado': estado,
        'etiqueta_estado': ETIQUETAS_ESTADO_COMPONENTE.get(estado, estado),
        'texto': texto,
        'aviso': AVISO_NO_PREPARADO if estado == 'RECHAZADO' and not texto else None,
    }


def construir_bloque_whatsapp(servicio, componentes, base_url, numero_destino):
    """Construye el contrato de lectura de mensajes definido en el plan §2."""
    codigo = servicio.get('codigo')
    if not servicio.get('activo', True):
        return {
            'codigo': codigo,
            'abierto': False,
            'numero_destino': None,
            'aviso': AVISO_SERVICIO_DESACTIVADO,
            'mensajes': [],
        }

    numero = _numero_destino(numero_destino)
    if numero is None:
        return {
            'codigo': codigo,
            'abierto': True,
            'numero_destino': None,
            'aviso': AVISO_SIN_NUMERO,
            'mensajes': [],
        }

    estado_servicio = servicio.get('estado')
    if estado_servicio in ESTADOS_SERVICIO_CERRADOS:
        return {
            'codigo': codigo,
            'abierto': False,
            'numero_destino': numero,
            'aviso': AVISO_SERVICIO_CERRADO,
            'mensajes': [],
        }

    enlace = enlace_seguimiento(base_url, servicio.get('token_seguimiento'))
    mensajes = []
    if estado_servicio in PLANTILLAS_SERVICIO:
        mensajes.append(_mensaje_servicio(servicio, enlace))
    for posicion, componente in enumerate(componentes):
        if componente.get('estado') in PLANTILLAS_COMPONENTE:
            mensajes.append(_mensaje_componente(componente, codigo, enlace, posicion))

    necesita_enlace = (
        estado_servicio in PLANTILLAS_SERVICIO
        or any(
            componente.get('estado') in {'ESPERANDO_APROBACION', 'RECHAZADO'}
            for componente in componentes
        )
    )
    return {
        'codigo': codigo,
        'abierto': True,
        'numero_destino': numero,
        'aviso': AVISO_DOMINIO if necesita_enlace and enlace is None else None,
        'mensajes': mensajes,
    }
