"""Mapeo de datos del flujo de estados simplificado (spec 008, RF-FLU-16).

Aplica a la BD existente las tablas de mapeo propuestas en RF-FLU-16, con las
marcas `[PROPUESTA]`/`[SUPUESTO]` de la spec conservadas en los comentarios.
En una BD nueva (tests) la migración corre vacío: no hay filas que mapear.

Advertencia de respaldo documentada (RF-FLU-16): la ejecución sobre una BD de
desarrollo con datos reales requiere respaldo previo (`pg_dump`); varias filas
pierden distinciones (DA-11). El usuario confirmó que los datos de la BD de
desarrollo son de prueba.

CL-18 — `NO_APROBADO` → `CANCELADO`: el servicio queda fuera del seguimiento
público y su comentario de cierre queda vacío. La cancelación real exige
comentario (RF-FLU-10) pero la migración NO DEBE inventarlo: no se escribe
ningún registro de historial ni comentario.

CL-19 — `FINALIZADO_POR_CLIENTE`/`FINALIZADO_POR_TECNICO` →
`LISTO_PARA_ENTREGA`: `motivo_finalizacion` y `fecha_finalizacion` se
conservan como historial en el propio componente y en sus
`HistorialComponente` (duda DA-9); la migración no los toca ni los reescribe
al nuevo catálogo.

CL-20 — `ENTREGADO` → `FINALIZADO`: se conserva `fecha_entrega` y NO se
inventa `fecha_finalizacion` (duda DA-8); el cierre administrativo posterior
ya no existe, el servicio queda cerrado.
"""

from django.db import migrations


# Tabla de mapeo propuesta — servicio (RF-FLU-16).
#
# | Estado actual                                 | Estado nuevo                  | Fecha que se conserva   | Nota                                        |
# |-----------------------------------------------|-------------------------------|-------------------------|---------------------------------------------|
# | `SOLICITADO`                                  | `SOLICITADO`                  | —                       |                                             |
# | `EN_REVISION`, `COTIZANDO`,                   | `EN_CURSO`                    | —                       |                                             |
# | `ESPERANDO_APROBACION`, `EN_REPARACION`,      |                               |                         |                                             |
# | `EN_PRUEBAS`                                  |                               |                         |                                             |
# | `LISTO_PARA_ENTREGA`                          | `EN_CURSO` `[PROPUESTA]`      | —                       | El cierre es manual (duda DA-8).            |
# | `ENTREGADO`                                   | `FINALIZADO` `[PROPUESTA]`    | `fecha_entrega` se      | No se inventa `fecha_finalizacion`          |
# |                                               |                               | conserva                | (duda DA-8).                                |
# | `FINALIZADO`                                  | `FINALIZADO`                  | `fecha_finalizacion`    |                                             |
# | `NO_APROBADO`                                 | `CANCELADO` `[PROPUESTA]`     | —                       | Deja de ser consultable por el enlace       |
# |                                               |                               |                         | (duda DA-7); comentario de cierre vacío     |
# |                                               |                               |                         | (CL-18).                                    |
# | `CANCELADO`                                   | `CANCELADO`                   | —                       |                                             |
MAPEO_ESTADO_SERVICIO = {
    'SOLICITADO': 'SOLICITADO',
    'EN_REVISION': 'EN_CURSO',
    'COTIZANDO': 'EN_CURSO',
    'ESPERANDO_APROBACION': 'EN_CURSO',
    'EN_REPARACION': 'EN_CURSO',
    'EN_PRUEBAS': 'EN_CURSO',
    'LISTO_PARA_ENTREGA': 'EN_CURSO',      # [PROPUESTA] duda DA-8
    'ENTREGADO': 'FINALIZADO',             # [PROPUESTA] duda DA-8; conserva fecha_entrega (CL-20)
    'FINALIZADO': 'FINALIZADO',            # conserva fecha_finalizacion
    'NO_APROBADO': 'CANCELADO',            # [PROPUESTA] duda DA-7; comentario vacío (CL-18)
    'CANCELADO': 'CANCELADO',
}

# Tabla de mapeo propuesta — componente (RF-FLU-16).
#
# | Estado actual                                              | Estado nuevo                   | Nota                                      |
# |------------------------------------------------------------|--------------------------------|-------------------------------------------|
# | `PENDIENTE`                                                | `PENDIENTE`                    |                                           |
# | `APROBADO`                                                 | `OPERARIO_TRABAJANDO`          | Cliente ya aprobó (duda DA-10).           |
# |                                                            | `[SUPUESTO]`                   |                                           |
# | `EN_PROCESO`                                               | `OPERARIO_TRABAJANDO` `[SUPUESTO]` |                                       |
# | `RECHAZADO`                                                | `RECHAZADO`                    |                                           |
# | `RECHAZADO_BLOQUEANTE`                                     | `RECHAZADO` `[SUPUESTO]`       |                                           |
# | `FINALIZADO_POR_CLIENTE`, `FINALIZADO_POR_TECNICO`         | `LISTO_PARA_ENTREGA`           | `motivo_finalizacion` y                  |
# |                                                            | `[PROPUESTA]`                  | `fecha_finalizacion` se conservan como    |
# |                                                            |                                | historial (duda DA-9, CL-19).             |
MAPEO_ESTADO_COMPONENTE = {
    'PENDIENTE': 'PENDIENTE',
    'APROBADO': 'OPERARIO_TRABAJANDO',                    # [SUPUESTO] duda DA-10
    'EN_PROCESO': 'OPERARIO_TRABAJANDO',                  # [SUPUESTO]
    'RECHAZADO': 'RECHAZADO',
    'RECHAZADO_BLOQUEANTE': 'RECHAZADO',                  # [SUPUESTO]
    'FINALIZADO_POR_CLIENTE': 'LISTO_PARA_ENTREGA',       # [PROPUESTA] duda DA-9; conserva datos de cierre (CL-19)
    'FINALIZADO_POR_TECNICO': 'LISTO_PARA_ENTREGA',       # [PROPUESTA] duda DA-9; conserva datos de cierre (CL-19)
}


def mapear_estados(apps, schema_editor):
    """Aplica las tablas de mapeo a los datos existentes.

    Solo se actualiza el campo `estado`. No se tocan `fecha_entrega`,
    `fecha_finalizacion`, `motivo_finalizacion`, `activo`, componentes,
    cotizaciones ni historiales; tampoco se crean registros de historial
    (la migración no inventa comentarios ni trazas: RF-FLU-16, CL-18).
    """
    Servicio = apps.get_model('servicios', 'Servicio')
    Componente = apps.get_model('servicios', 'Componente')

    for estado_actual, estado_nuevo in MAPEO_ESTADO_SERVICIO.items():
        if estado_actual == estado_nuevo:
            continue
        Servicio.objects.filter(estado=estado_actual).update(estado=estado_nuevo)

    for estado_actual, estado_nuevo in MAPEO_ESTADO_COMPONENTE.items():
        if estado_actual == estado_nuevo:
            continue
        Componente.objects.filter(estado=estado_actual).update(estado=estado_nuevo)


def revertir_mapeo(apps, schema_editor):
    """La migración de datos es irreversible sin backup.

    Varias filas del mapeo son `[PROPUESTA]`/`[SUPUESTO]` con pérdida de
    distinciones (DA-7 a DA-11): `NO_APROBADO`, `ENTREGADO`,
    `LISTO_PARA_ENTREGA` de servicio, `APROBADO`, `EN_PROCESO`,
    `RECHAZADO_BLOQUEANTE` y `FINALIZADO_POR_*` de componente no tienen
    destino de vuelta único. La reversión de las filas identidad no hace
    nada. Restaurar el catálogo anterior en una BD con datos requiere el
    respaldo previo documentado.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0007_catalogo_estados_flujo'),
    ]

    operations = [
        migrations.RunPython(mapear_estados, revertir_mapeo),
    ]
