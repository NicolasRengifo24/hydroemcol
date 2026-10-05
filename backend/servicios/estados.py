"""Catálogos de estado del componente y del canal de respuesta.

Este archivo es la fuente única de verdad de los estados. Lo importan los
modelos, los serializers, las vistas y el admin, para que el mismo nombre de
estado no se escriba en varios sitios.

Los estados de cierre de un componente son `FINALIZADO_POR_CLIENTE` y
`FINALIZADO_POR_TECNICO`. Cualquier otro estado significa que al componente le
falta trabajo por ejecutar, y por tanto el servicio sigue abierto.
"""

from django.db import models


class EstadoComponente(models.TextChoices):
    """Estados por los que atraviesa un componente dentro de un servicio."""

    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADO = 'APROBADO', 'Aprobado'
    RECHAZADO = 'RECHAZADO', 'Rechazado'
    RECHAZADO_BLOQUEANTE = 'RECHAZADO_BLOQUEANTE', 'Rechazado (bloqueante)'
    EN_PROCESO = 'EN_PROCESO', 'En proceso'
    FINALIZADO_POR_CLIENTE = 'FINALIZADO_POR_CLIENTE', 'Finalizado por cliente'
    FINALIZADO_POR_TECNICO = 'FINALIZADO_POR_TECNICO', 'Finalizado por técnico'


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
# estos dos, el servicio sigue abierto (criterio único de la especificación).
ESTADOS_FINALIZACION = (
    EstadoComponente.FINALIZADO_POR_CLIENTE,
    EstadoComponente.FINALIZADO_POR_TECNICO,
)
