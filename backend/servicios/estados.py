"""Catálogos de estado del componente y del canal de respuesta.

Este archivo es la fuente única de verdad de los estados. Lo importan los
modelos, los serializers, las vistas y el admin, para que el mismo nombre de
estado no se escriba en varios sitios.

Catálogo de la spec 008 (§4, RF-FLU-02): ocho estados de componente. Los
estados de cierre de un componente son `LISTO_PARA_ENTREGA` y `RECHAZADO`,
ambos alcanzados solo con finalización manual del administrativo que registra
motivo (texto libre) y fecha (RF-FLU-07 y RF-FLU-08). Cualquier otro estado
significa que al componente le falta trabajo por ejecutar, y por tanto el
servicio sigue abierto.
"""

from django.db import models


class EstadoComponente(models.TextChoices):
    """Estados por los que atraviesa un componente dentro de un servicio."""

    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EN_REVISION = 'EN_REVISION', 'En revisión'
    COTIZANDO = 'COTIZANDO', 'Cotizando'
    ESPERANDO_APROBACION = 'ESPERANDO_APROBACION', 'Esperando aprobación'
    OPERARIO_TRABAJANDO = 'OPERARIO_TRABAJANDO', 'Operario trabajando'
    EN_PRUEBAS = 'EN_PRUEBAS', 'En pruebas'
    LISTO_PARA_ENTREGA = 'LISTO_PARA_ENTREGA', 'Listo para entregar'
    RECHAZADO = 'RECHAZADO', 'Rechazado'


class EstadoFaseComponente(models.TextChoices):
    """Fases del ciclo normal de trabajo sobre un componente.

    `DESMONTAJE_INICIADO` es la fase que marca el inicio de trabajo: desde ese
    momento el componente ya está en manos de la empresa.
    """

    RECIBIDO = 'RECIBIDO', 'Recibido'
    DESMONTAJE_INICIADO = 'DESMONTAJE_INICIADO', 'Desmontaje iniciado'
    EN_EJECUCION = 'EN_EJECUCION', 'En ejecución'


class CanalRespuesta(models.TextChoices):
    """Canal por el que el cliente respondió una cotización.

    Se separa de `MedioAprobacion` porque este es el canal de la respuesta a la
    cotización de un componente, no el medio de una aprobación del servicio.
    """

    WEB = 'WEB', 'Web'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'


# Estados que cierran un componente. Mientras un componente no esté en uno de
# estos dos, el servicio sigue abierto (criterio único de la especificación,
# RF-FLU-09). Ambos se alcanzan solo con finalización manual que registra
# motivo y fecha (RF-FLU-07/08).
ESTADOS_FINALIZACION = (
    EstadoComponente.LISTO_PARA_ENTREGA,
    EstadoComponente.RECHAZADO,
)


PASOS_PUBLICOS_COMPONENTE = {
    EstadoComponente.PENDIENTE: 'Recibido',
    EstadoComponente.EN_REVISION: 'Revisión y cotización',
    EstadoComponente.COTIZANDO: 'Revisión y cotización',
    EstadoComponente.ESPERANDO_APROBACION: 'Revisión y cotización',
    EstadoComponente.OPERARIO_TRABAJANDO: 'Revisión y cotización',
    EstadoComponente.EN_PRUEBAS: 'Pruebas',
    EstadoComponente.LISTO_PARA_ENTREGA: 'Finalizado',
    EstadoComponente.RECHAZADO: 'Finalizado',
}


# Estados de catálogos anteriores que pueden aparecer en el historial de
# componentes (la migración 0008 remapeó el estado vigente, no las filas de
# historial ya escritas). Se traducen a su equivalente del catálogo actual para
# que el seguimiento público muestre el paso correcto.
ESTADOS_COMPONENTE_HISTORICOS = {
    'EN_PROCESO': EstadoComponente.OPERARIO_TRABAJANDO,
    'RECHAZADO_BLOQUEANTE': EstadoComponente.RECHAZADO,
    'APROBADO': EstadoComponente.OPERARIO_TRABAJANDO,
    'FINALIZADO_POR_CLIENTE': EstadoComponente.LISTO_PARA_ENTREGA,
    'FINALIZADO_POR_TECNICO': EstadoComponente.LISTO_PARA_ENTREGA,
}


def paso_publico_componente(estado):
    """Devuelve el paso público definido en la tabla §4.3 de la spec 008.

    Tolera estados fuera del catálogo vigente: el historial de componentes
    conserva valores de catálogos anteriores (p. ej. ``EN_PROCESO`` o
    ``FINALIZADO_POR_TECNICO``). Un estado histórico se traduce a su
    equivalente; un estado totalmente desconocido no debe tumbar el
    seguimiento público y cae en "Revisión y cotización".
    """
    estado = ESTADOS_COMPONENTE_HISTORICOS.get(estado, estado)
    return PASOS_PUBLICOS_COMPONENTE.get(estado, 'Revisión y cotización')
