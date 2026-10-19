# Plan técnico — Spec 008: Flujo de estados simplificado

**Plan de implementación · Hidroemcol**
**Spec origen:** `specs/008-flujo-estados-simplificado/spec.md` (Estado: aprobada)
**Autoridad normativa:** `docs/constitution.md` (6 principios) > `AGENTS.md` > `CONTEXTO_MAESTRO.md`
**Restricciones respetadas:** sin dependencias nuevas; backend como autoridad (principio 3); español en pantalla y mensajes; verificación backend con `django.test` vía `manage.py test` y frontend con Chrome DevTools MCP (RNF-FLU-06; disponibilidad del MCP confirmada por el usuario); responsive desde el inicio (RNF-FLU-07).

---

## 1. Contexto

La spec 006 ya está implementada: `reglas.py` calcula transiciones, `acciones.py` es el único punto de ejecución, la API expone `componentes/{id}/estado/` y `servicios/{id}/estado/`, y el panel pinta selectores de estado. La spec 008 **supersede** las cláusulas de la 006 (y de 001, 002, 005 y 007) que dependan de los catálogos antiguos, y reescribe el modelo de estados:

- **Servicio:** de 11 valores a 4 — `SOLICITADO`, `EN_CURSO`, `FINALIZADO`, `CANCELADO` (RF-FLU-01).
- **Componente:** de 7 a 8 — `PENDIENTE`, `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS`, `LISTO_PARA_ENTREGA`, `RECHAZADO` (RF-FLU-02). Desaparecen `APROBADO`, `RECHAZADO_BLOQUEANTE`, `EN_PROCESO`, `FINALIZADO_POR_CLIENTE`, `FINALIZADO_POR_TECNICO`.
- Cada cambio es **automático** (hecho registrado: primer componente fuera de `PENDIENTE`, cotización registrada, aprobación del cliente por token) o **manual y explícito** (acción del administrativo validada por la tabla de transiciones §4.1).
- El rechazo de cotización **no mueve** el componente; `RECHAZADO` solo lo decide el administrador al finalizar, con motivo (texto libre) y fecha.
- Se conservan sin tocar: `HistorialServicio` y `HistorialComponente` (ya admiten todo lo exigido, RF-FLU-12), la concurrencia con `select_for_update` + `409` (RF-FLU-13, heredada de la 006), la excepción de permiso del cliente por token (RF-FLU-14) y el catálogo de fases (DA-14).

El catálogo de fases (`RECIBIDO`, `DESMONTAJE_INICIADO`, `EN_EJECUCION`) no cambia. Los catálogos de cotización (`PENDIENTE`, `APROBADA`, `RECHAZADA`) tampoco.

## 2. Alcance

**Dentro:**

1. Actualización de las fuentes de negocio (RF-FLU-17): `CONTEXTO_MAESTRO.md` §14 y §30, y anotación en `MEMORY.md`. Es condición previa a escribir código.
2. Migración de esquema (choices) y migración de datos con la tabla de mapeo de RF-FLU-16:
   **creación y ejecución** de ambas contra la BD de desarrollo, con advertencia de respaldo
   previo si la BD no es de prueba (confirmado por el usuario: quiere probar el sistema).
3. Reescritura de catálogos, reglas puras, acciones, serializers, vistas, urls y Django Admin
   sobre los archivos existentes, incluidos los efectos automáticos de RF-FLU-05/06 sobre
   `OPERARIO_TRABAJANDO`, `EN_PRUEBAS` y `LISTO_PARA_ENTREGA` (cotización →
   `ESPERANDO_APROBACION` conservando fase y progreso) y la devolución a `EN_PRUEBAS` al aprobar
   la cotización registrada en `LISTO_PARA_ENTREGA` (DA-18 cerrada).
4. Simplificación del frontend administrativo (selectores → acciones explícitas) y alineación del
   seguimiento público.
5. **Suite nueva** de tests del flujo completo (`test_flujo_estados.py`) y **limpieza del legacy**:
   se conservan los tests que sigan válidos con el catálogo nuevo y se eliminan o ajustan
   mínimamente los que prueban estados retirados (decisión del usuario; sustituye a la
   reescritura integral de las ~390 pruebas existentes).
6. Verificación integral (tests + MCP + responsive) y bitácora.

**Fuera de alcance** (§9 de la spec): reapertura de servicios cerrados; corrección de estados a nivel de servicio; cancelación pública; roles o cuentas de cliente; notificaciones/tiempo real; cambio del catálogo de fases o de cotizaciones; diseño visual de la línea de tiempo pública de 4 pasos (lo define 007; aquí solo se garantizan los estados y etiquetas que esa línea consumirá).

## 3. Archivos que se crean o modifican

### Se crean

| Archivo | Responsabilidad | RF que cubre |
|---|---|---|
| `backend/servicios/migrations/0007_catalogo_estados_flujo.py` | Migración de **esquema**: nuevos `choices` de `EstadoServicio` y `EstadoComponente` (incluye los campos `choices` de `HistorialServicio.estado` y `HistorialComponente.estado_anterior/estado_nuevo`). | RF-FLU-01, 02, 16 |
| `backend/servicios/migrations/0008_mapeo_datos_flujo.py` | Migración de **datos**: RunPython con las tablas de mapeo de RF-FLU-16 (servicio y componente), con las marcas conservadas como comentarios. Ejecución vacía en BD nueva (tests). | RF-FLU-16, CL-18..20 |
| `backend/servicios/tests/test_flujo_estados.py` | Suite nueva de la spec 008: reglas puras del flujo, efectos automáticos, finalizaciones con motivo, correcciones, cierre/cancelación, permisos y concurrencia. | RF-FLU-03..14 |

### Se modifican

| Archivo | Responsabilidad | RF que cubre |
|---|---|---|
| `backend/servicios/estados.py` | Nuevo catálogo de `EstadoComponente` (8 valores) y `ESTADOS_FINALIZACION = (LISTO_PARA_ENTREGA, RECHAZADO)`. | RF-FLU-02 |
| `backend/servicios/models.py` | `EstadoServicio` reduce a 4 valores. Sin campos nuevos: `motivo_finalizacion` y `fecha_finalizacion` ya existen en `Componente`. | RF-FLU-01 |
| `backend/servicios/reglas.py` | Reescritura de las funciones de transición sobre la tabla §4.1; nuevas reglas de efectos automáticos; retiro de `tiene_bloqueo_cotizacion`, `puede_continuar`, `estado_por_rechazo_bloqueante`, `todos_rechazan_bloqueantes`; `estados_cerrados()` pasa a `(FINALIZADO, CANCELADO)`. | RF-FLU-03..13 |
| `backend/servicios/acciones.py` | `cambiar_estado_componente` con las ramas nuevas; efectos automáticos en la misma transacción del hecho (`crear_cotizacion`, `registrar_respuesta`, `registrar_aprobacion_externa`); retiro de `iniciar_trabajo`, `finalizar_componente` y `estado_por_rechazo_bloqueante`; `corregir_finalizacion` por RF-FLU-07; `finalizar_servicio` con el criterio nuevo; `cancelar_servicio` sin cambios de comportamiento. | RF-FLU-03..13 |
| `backend/servicios/serializers.py` | `construir_hoy` se conserva; entradas de cambio de estado adaptadas; `estados_seleccionables` del componente sobre el catálogo nuevo; `acciones_disponibles` del servicio pasa a ser la única superficie de decisión (`finalizar_servicio`, `cancelar_servicio`); `motivo_bloqueo` → `motivo_espera` informativo. | RF-FLU-05, 06, 09, 14 |
| `backend/servicios/views.py` | `CambiarEstadoComponenteView` se mantiene; se retira `IniciarTrabajoView`, `FinalizarComponenteView`, `CorregirFinalizacionView` y `CambiarEstadoServicioView` (unificadas en `/estado/` de componente y en `/finalizar/` + `/cancelar/` de servicio); `DashboardAdministrativoView` con pendientes del flujo nuevo; `SeguimientoView` excluye `CANCELADO`. | RF-FLU-09, 10, 14, 15 |
| `backend/servicios/urls.py` | Retiro de rutas obsoletas; registro de `servicios/<pk>/cancelar/`. | RF-FLU-10 |
| `backend/servicios/admin.py` | `ComponenteAdmin`: acciones sobre el catálogo nuevo (avanzar, finalizar con motivo libre, corregir), sin "iniciar desmontaje"; `ResumenDeCierre` con `resumen_cierre` simplificado; `ServicioAdmin` sin referencias a estados retirados. | RF-FLU-04, 07..10 |
| `frontend/src/services/api.ts` | `CodigoEstadoServicio` (4) y `CodigoEstadoComponente` (8); retiro de `MotivoFinalizacion`; contratos de detalle y dashboard alineados. | RF-FLU-01, 02 |
| `frontend/src/hooks/useAdministrativo.ts` | Mutaciones alineadas: `cambiarEstadoComponente`, `finalizarServicio`, `cancelarServicio`; retiro de `iniciarTrabajo`, `finalizarComponente`, `corregirFinalizacion`. | RF-FLU-04, 07..10 |
| `frontend/src/pages/AdminServicioDetalle.tsx` | Selector de servicio → acciones **Finalizar** (con `resumen_cierre`) y **Cancelar** (textarea obligatorio); selector de componente desde `estados_seleccionables` con textarea de motivo obligatorio donde la regla lo exige; etiquetas nuevas; feedback `409` con recarga. | RF-FLU-01..12, RNF-FLU-04/05 |
| `frontend/src/pages/AdminServicios.tsx` | Filtro de estado a los 4 valores. | RF-FLU-01 |
| `frontend/src/pages/AdminIndicadores.tsx` | Contadores del dashboard a los 4 estados. | RF-FLU-01 |
| `frontend/src/pages/Seguimiento.tsx` | Alineación: sin códigos de estado eliminados; el detalle y las etiquetas llegan del backend. La línea de tiempo de 4 pasos queda para 007. | RF-FLU-15 |
| `frontend/src/index.css` | Ajustes de los controles nuevos (acciones del servicio, textarea de motivo), responsive. | RNF-FLU-04/07 |
| `backend/servicios/tests/` (existentes) | Limpieza mínima del legacy: se conservan los tests que siguen válidos con el catálogo nuevo y se eliminan o ajustan los que prueban estados retirados del catálogo viejo (sin reescribir suites enteras). | RF-FLU-01..16 |
| `CONTEXTO_MAESTRO.md` §14 y §30; `MEMORY.md` | Fuentes de negocio (RF-FLU-17). | RF-FLU-17 |

## 4. Fases y dependencias

| Fase | Contenido | Depende de |
|---|---|---|
| **f0 — Fuentes de negocio** | `CONTEXTO_MAESTRO.md` §14 (catálogos) y §30 (pasos de ejemplo y línea de tiempo) al nuevo modelo; anotación del cambio en `MEMORY.md` (RF-FLU-17). | — |
| **f1 — Catálogos y migración** | `estados.py`, `models.py`, migración de esquema (0007) y de datos (0008) con la tabla de mapeo; **creación y ejecución** de ambas contra la BD de desarrollo (advertencia de respaldo si la BD no es de prueba). | f0 |
| **f2 — Reglas y acciones** | `reglas.py` (puras sobre `hoy`) y `acciones.py` (efectos automáticos en la transacción del hecho, ramas manuales, cierre y cancelación); efectos de RF-FLU-05 sobre `COTIZANDO`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS` y `LISTO_PARA_ENTREGA` (conservando fase y progreso) y destino de la aprobación según el origen de la espera: `OPERARIO_TRABAJANDO` o `EN_PRUEBAS` (DA-18). | f1 |
| **f3 — API, serializers y admin** | Contratos de entrada/salida, `estados_seleccionables`, `acciones_disponibles`, vistas/urls simplificadas, dashboard, `admin.py`; la respuesta de aprobación por token refleja el destino que la regla devuelve (`EN_PRUEBAS` cuando la espera vino de `LISTO_PARA_ENTREGA`, DA-18). | f2 |
| **f4 — Frontend admin** | `api.ts`, hooks, `AdminServicioDetalle.tsx`, `AdminServicios.tsx`, `AdminIndicadores.tsx`, `index.css`; responsive móvil/tablet/escritorio. | f3 |
| **f5 — Frontend seguimiento** | Alineación de `Seguimiento.tsx` con los estados nuevos; sin códigos eliminados; etiquetas desde el backend. | f3 |
| **f6 — Tests y verificación** | Suite nueva `test_flujo_estados.py` (el flujo completo, escrita en rojo durante f2/f3) y limpieza del legacy inválido (conservar los tests válidos, eliminar o ajustar los que prueban estados retirados); verificación integral (check, tests, build, lint, MCP visual y responsive) y bitácora. | f2 (reglas), f4, f5 |

> Nota de orden: las pruebas se escriben en rojo junto a cada fase de backend (convención del repo), no al final. f6 es la fase de cierre que unifica y certifica, no la primera vez que se escriben tests.

## 5. Funciones puras de `reglas.py`

Mismo patrón que el módulo actual: reciben `hoy` (estado ya leído, forma la que `construir_hoy` devuelve), devuelven valores, no tocan base de datos ni reloj. `construir_hoy` **no cambia de forma**.

```python
# Tabla §4.1 como fuente única: estado actual → destinos manuales.
TRANSICIONES_MANUALES_COMPONENTE = {
    'PENDIENTE':             ['EN_REVISION'],
    'EN_REVISION':           ['COTIZANDO'],
    'COTIZANDO':             [],                       # su salida es automática
    'ESPERANDO_APROBACION':  ['RECHAZADO'],            # el rechazo del cliente no mueve
    'OPERARIO_TRABAJANDO':   ['EN_PRUEBAS'],
    'EN_PRUEBAS':            ['LISTO_PARA_ENTREGA'],
    'LISTO_PARA_ENTREGA':    ['EN_PRUEBAS'],           # corrección por error humano; su
                                                       # salida automática es
                                                       # ESPERANDO_APROBACION (RF-FLU-05,
                                                       # DA-18)
    'RECHAZADO':             ['ESPERANDO_APROBACION'], # corrección por error humano
}

# Estados cuyas finalizaciones exigen motivo (texto libre) y fecha (RF-FLU-07/08).
ESTADOS_FINALIZACION = ('LISTO_PARA_ENTREGA', 'RECHAZADO')
ESTADOS_SERVICIO_CERRADOS = ('FINALIZADO', 'CANCELADO')

def estados_componente_seleccionables(hoy, componente):
    """Destinos manuales válidos según §4.1. Nunca incluye destinos
    automáticos (ESPERANDO_APROBACION desde COTIZANDO /
    OPERARIO_TRABAJANDO / EN_PRUEBAS / LISTO_PARA_ENTREGA, ni
    OPERARIO_TRABAJANDO / EN_PRUEBAS por aprobación): los produce
    el hecho, no el selector."""

def requiere_motivo(destino):
    """Todo destino finalizado y toda corrección exigen motivo libre."""

def resolver_transicion_componente(hoy, componente, destino, comentario=''):
    """{'permitido','tipo','codigo','motivo','extra'} con
    tipo ∈ {'noop','normal','finalizar','correccion'}.
    - destino inexistente en el catálogo → 400;
    - destino ≠ actual pero no listado en §4.1 → 409 (CL-03);
    - destino final (LISTO_PARA_ENTREGA/RECHAZADO) sin motivo → 400;
    - corrección sin comentario → 400 (CL-22);
    - RECHAZADO exige que exista una cotización RECHAZADA del componente → 409;
    - mismo estado → noop (CL-16)."""

def es_cambio_fuera_de_pendiente(componente_anterior, componente_hoy):
    """Primer componente que sale de PENDIENTE (RF-FLU-03, CL-01/02)."""

def transicion_por_respuesta(hoy, componente, resultado, origen_espera):
    """Efecto automático de la respuesta del cliente (RF-FLU-06):
    APROBADA + ESPERANDO_APROBACION → 'OPERARIO_TRABAJANDO', salvo
    cuando la espera vino de LISTO_PARA_ENTREGA → 'EN_PRUEBAS'
    (DA-18: conserva fase y progreso); RECHAZADA → None (no mueve
    el componente, CL-06). El origen de la espera se pasa como
    dato (última transición a ESPERANDO_APROBACION en
    HistorialComponente), sin campo nuevo."""

def transicion_por_cotizacion(hoy, componente):
    """Efecto automático de registrar una cotización (RF-FLU-05):
    COTIZANDO, OPERARIO_TRABAJANDO, EN_PRUEBAS o LISTO_PARA_ENTREGA
    → 'ESPERANDO_APROBACION' conservando fase y progreso (no
    reinicia el trabajo); en ESPERANDO_APROBACION u otro estado →
    None (DA-17 y DA-18 cerradas)."""

def componentes_no_finalizados(hoy):
    """Servicio sigue abierto mientras quede algo fuera de
    LISTO_PARA_ENTREGA/RECHAZADO (RF-FLU-09)."""

def puede_finalizar_servicio(hoy):
    """≥ 1 componente y todos en LISTO_PARA_ENTREGA o RECHAZADO.
    Por definición ambos ya llevan motivo y fecha (DA-6 cerrada)."""

def resumen_cierre(hoy):
    """'puede_finalizar' + 'detalle' en español, listando los componentes
    que impiden el cierre o el caso SIN_COMPONENTES (CL-10/11)."""

def estados_servicio_seleccionables(hoy):
    """Siempre []. El servicio no tiene selector libre: sus dos operaciones
    manuales son finalizar y cancelar (§4.1 solo define transiciones de
    componente; el servicio cambia por hecho o por esas dos acciones)."""

def puede_cancelar_servicio(hoy):
    """Servicio activo y no cerrado (RF-FLU-10)."""

def estados_cerrados():
    """(FINALIZADO, CANCELADO) —RF-8.6 de 001 supersede por §2.3;
    lo consume `tiene_solicitud_en_curso` del aviso de duplicado."""
```

**Se retiran** (sin sustituto): `tiene_bloqueo_cotizacion`, `puede_continuar`, `estado_por_rechazo_bloqueante`, `todos_rechazan_bloqueantes`, `motivo_bloqueo`, `fecha_para_estado_servicio` (solo `FINALIZADO` escribe fecha de servicio; `ENTREGADO` ya no existe). `tiene_trabajo_iniciado` se conserva como dato informativo (DA-1 supuesto).

## 6. Acciones en pseudocódigo (`acciones.py`)

### 6.1 Efectos automáticos (en la misma transacción del hecho, RF-FLU-13)

```
crear_cotizacion(...):
    en transacción (ya bloquea servicio y componente):
        ...registro actual...
        si componente.estado in (COTIZANDO, OPERARIO_TRABAJANDO,
                                 EN_PRUEBAS, LISTO_PARA_ENTREGA):
            componente.estado = ESPERANDO_APROBACION     # RF-FLU-05
            # fase, progreso y trabajo_iniciado intactos     # DA-17/DA-18
            componente.save; HistorialComponente (sin usuario)

registrar_respuesta(...) / registrar_aprobacion_externa(...):
    en transacción (ya bloquea servicio, componente y cotización):
        ...registro de AprobacionServicio y cotizacion.estado...
        origen = ultima_transicion_a_espera(HistorialComponente)
        efecto = transicion_por_respuesta(hoy, componente, resultado, origen)
        si efecto == 'EN_PRUEBAS':                        # RF-FLU-06, DA-18
            componente.estado = EN_PRUEBAS                # origen LISTO_PARA_ENTREGA:
                                                          # conserva fase y progreso
            HistorialComponente (usuario=None si llegó por token)
        si efecto == 'OPERARIO_TRABAJANDO':               # RF-FLU-06, CL-05
            campos = _aplicar_inicio_trabajo(componente)  # estado, fase DESMONTAJE_INICIADO,
                                                          # trabajo_iniciado, fecha (DA-1)
            HistorialComponente (usuario=None si la respuesta llegó por token)
        si resultado == RECHAZADA:                        # RF-FLU-06, CL-06
            NO se toca el componente; solo historial de servicio
```

### 6.2 Cambio manual del componente (RF-FLU-04, 07, 08)

```
cambiar_estado_componente(*, servicio, componente_id, nuevo_estado, comentario, usuario):
    en transacción:
        servicio = bloquear(Servicio); si cerrado → 409 (CL-15)
        componente = bloquear(Componente, pk, servicio) o 404
        hoy = construir_hoy(servicio)
        decisión = resolver_transicion_componente(hoy, dato, nuevo_estado, comentario)
        si no permitido → ErrorDeAccion(codigo, motivo, extra)
        si noop → devolver sin historial (CL-16)
        anterior = componente.estado
        según decisión.tipo:
            'normal':      componente.estado = destino            # EN_REVISION / COTIZANDO / EN_PRUEBAS
            'finalizar':   estado + motivo_finalizacion = comentario (texto libre)
                           + fecha_finalizacion = ahora           # LISTO_PARA_ENTREGA / RECHAZADO
            'correccion':  estado = destino + limpiar
                           motivo_finalizacion/fecha_finalizacion  # historial conserva el previo
        componente.save
        HistorialComponente(estado_anterior, estado_nuevo, comentario, usuario)
        si es_cambio_fuera_de_pendiente(...) y servicio.estado == SOLICITADO:
            servicio.estado = EN_CURSO                            # RF-FLU-03, CL-01
            servicio.save; HistorialServicio(EN_CURSO, usuario)
```

### 6.3 Servicio: cierre y cancelación (RF-FLU-09, 10)

```
finalizar_servicio(*, servicio, comentario='', usuario):
    en transacción:
        bloquear; si cerrado → 409
        hoy = construir_hoy; si no puede_finalizar_servicio(hoy):
            409 con resumen_cierre (lista los componentes que impiden, CL-10/11)
        servicio.estado = FINALIZADO; fecha_finalizacion = ahora
        HistorialServicio(FINALIZADO, comentario, usuario)        # componentes no cambian (CL-12)

cancelar_servicio(*, servicio, comentario, usuario):
    sin cambios de comportamiento respecto a la 006 (RF-FLU-10, CL-13/14):
    exige comentario; no toca activo, componentes, cotizaciones ni historial previo.
```

**Se retiran** de `acciones.py`: `iniciar_trabajo` (el inicio es el paso automático a `OPERARIO_TRABAJANDO`, RF-ADM-18 supersede), `finalizar_componente` (sus destinos pasan por `cambiar_estado_componente`) y el uso de `estado_por_rechazo_bloqueante` en `registrar_respuesta`/`registrar_aprobacion_externa`. `corregir_finalizacion` queda absorbida por la rama `correccion` de `cambiar_estado_componente` (un solo punto de decisión).

## 7. API, serializers y admin

- **Entrada de componente:** se conserva `POST servicios/{s}/componentes/{c}/estado/` con `{estado, comentario}` (D-1 de la 006 preservada en espíritu: un solo punto de decisión). `comentario` pasa a ser obligatorio cuando la regla lo exige (la acción revalida; el serializer no decide).
- **Servicio:** se retira `POST servicios/{s}/estado/` (selector libre). Quedan dos operaciones explícitas: `POST servicios/{s}/finalizar/` (comentario opcional) y la nueva `POST servicios/{s}/cancelar/` (comentario obligatorio). Coherente con "el panel no ofrece un selector libre" (RF-ADM-21 de 005, mantenido por §2.4).
- **`ServicioAdministrativoSerializer`:** se retira `estados_seleccionables` (o se fija a `[]` durante una iteración y se elimina); `acciones_disponibles` expone `finalizar_servicio` y `cancelar_servicio` según las reglas. `resumen_cierre` conserva su forma.
- **`ComponenteAdministrativoSerializer`:** `estados_seleccionables` desde la tabla nueva; `acciones_disponibles` pasa a `['responder_cotizacion']` si hay cotización pendiente y `['corregir_finalizacion']` si está finalizado (sin `iniciar_trabajo` ni `finalizar_componente` como acciones sueltas); `motivo_bloqueo` se sustituye por `motivo_espera` (informativo en `ESPERANDO_APROBACION`: "Cotización pendiente de respuesta" / "Cotización rechazada: reenviar o finalizar como RECHAZADO").
- **Públicos:** `ServicioPublicoSerializer` y `ComponentePublicoSerializer` ya exponen etiquetas vía `get_estado_display`; con los catálogos nuevos muestran automáticamente los 4 y 8 estados en español, sin exponer campos internos (RF-COT-15 mantenido, RF-FLU-15). `SeguimientoView` y `SeguimientoAprobarView` siguen excluyendo `CANCELADO`.
- **Dashboard:** `pendientes_atencion` = servicios `SOLICITADO` o con algún componente en `ESPERANDO_APROBACION` (§2.4 de la spec); `contadores` se calculan sobre las 4 opciones del `TextChoices`.
- **Django Admin:** `ComponenteAdmin` ofrece las acciones válidas del catálogo nuevo (avanzar según §4.1, finalizar con motivo libre, corregir con comentario); se retiran "Iniciar desmontaje" y los motivos `FINALIZADO_POR_*`. `ResumenDeCierre` muestra el `resumen_cierre` nuevo y el botón de cierre solo habilitado con la regla vigente.

## 8. Frontend

- **`api.ts`:** `CodigoEstadoServicio = 'SOLICITADO' | 'EN_CURSO' | 'FINALIZADO' | 'CANCELADO'`; `CodigoEstadoComponente` con los 8 códigos nuevos; se retira `MotivoFinalizacion`; `estados_seleccionables` solo en el componente; `acciones_disponibles` del servicio guía los botones.
- **`AdminServicioDetalle.tsx`:** desaparece `SelectorEstadoServicio`; la sección "Acciones del servicio" pinta **Finalizar servicio** (con el `detalle` de `resumen_cierre`, habilitado solo cuando la regla lo permite) y **Cancelar servicio** (textarea de comentario obligatorio antes de confirmar). `SelectorEstadoComponente` sigue pintando las opciones que el backend entrega; al elegir `LISTO_PARA_ENTREGA`, `RECHAZADO` o una corrección aparece un textarea de motivo obligatorio (deshabilita el botón hasta escribir, como ya hacía la cancelación). Feedback: éxito `role="status"`, error `role="alert"`, `409` con mensaje del backend y botón "Recargar detalle" (invalidación existente en `opcionesMutacion`).
- **`AdminServicios.tsx` / `AdminIndicadores.tsx`:** filtros y contadores a los 4 estados.
- **`Seguimiento.tsx`:** hoy es placeholder; se alinea para no nombrar códigos eliminados y para consumir `estado`/etiquetas tal como el backend los sirve. La línea de tiempo de 4 pasos (Recibido, Revisión y cotización, Pruebas, Finalizado — DA-15) **no se implementa aquí**: su diseño pertenece a 007.
- **Responsive (RNF-FLU-07):** controles apilados en móvil y en fila desde ~640 px, sin scroll horizontal a 375/768/1280; foco visible; labels con `htmlFor`; estados comunicados con texto, no solo color.

## 9. Decisiones de diseño

| # | Decisión | Alternativa descartada | Motivo |
|---|---|---|---|
| PD-1 | Catálogos como `TextChoices` en `estados.py`/`models.py` con migración de esquema de `choices`. | Constantes Python fuera de la BD, sin migración. | Es el patrón ya adoptado por la 002/006; los campos del historial también llevan `choices` y deben coherentes. Constitución principio 2: cambio de modelo ⇒ migración anotada. |
| PD-2 | Migración de datos con `RunPython` + tablas de mapeo de RF-FLU-16, conservando fechas señaladas. | Borrar y recrear servicios/componentes de prueba. | El mapeo preserva relaciones, historial y trazabilidad; borrar destruiría el rastro que la spec exige conservar. |
| PD-3 | Servicio con dos endpoints explícitos (`/finalizar/`, `/cancelar/`) y sin `estados_seleccionables`. | Conservar `POST /estado/` del servicio con los 4 estados. | El servicio solo tiene dos operaciones manuales; un endpoint genérico invita al selector libre que 005 y 008 prohíben. Menos superficie de API que probar y documentar. |
| PD-4 | Efectos automáticos ejecutados dentro de la transacción del hecho que los produce. | Programar la transición como paso posterior (cola, cron o segunda llamada). | RF-FLU-13 lo exige explícitamente; evita estados intermedios imposibles ("cotización registrada pero componente sin esperar"). |
| PD-5 | `TRANSICIONES_MANUALES_COMPONENTE` como tabla diccionario que alimenta `estados_componente_seleccionables` y `resolver_transicion_componente`. | Listas de destinos calculadas a mano en cada función. | Una sola fuente = la tabla §4.1; imposible que selección y validación diverjan. |
| PD-6 | El inicio de trabajo es únicamente el paso automático a `OPERARIO_TRABAJANDO` (fase `DESMONTAJE_INICIADO`, `trabajo_iniciado=True`, su fecha una sola vez — supuesto DA-1). | Conservar la acción manual "iniciar trabajo" además del paso automático. | Dos caminos para el mismo hecho = dos comportamientos que divergen. RF-ADM-18 supersede; la spec retira la acción manual. |
| PD-7 | El motivo de finalización es texto libre escrito en el campo existente `motivo_finalizacion` (ya `TextField`). | Crear un catálogo de motivos o un campo nuevo. | DA-6 cerrada: texto libre; el modelo ya tiene el campo y el historial, sin migración de estructura. |
| PD-8 | La corrección por error humano es una rama dentro de `cambiar_estado_componente` (destinos únicos: `LISTO_PARA_ENTREGA→EN_PRUEBAS`, `RECHAZADO→ESPERANDO_APROBACION`; comentario obligatorio). | Endpoint/acción aparte `corregir_estado`. | Un solo punto de decisión para toda transición de componente; D-8 de la 002 preservada y concretada en RF-FLU-07. Al corregir se limpian `motivo_finalizacion` y `fecha_finalizacion` (coherencia, como la D-5 de la 006); el dato previo queda en `HistorialComponente`. |
| PD-9 | `motivo_bloqueo` se sustituye por `motivo_espera`, informativo (no bloqueante), activo en `ESPERANDO_APROBACION`. | Conservar `motivo_bloqueo` y `puede_continuar` como bloqueadores del backend. | El nuevo modelo no tiene bloqueos que imponga el backend: la detención es el estado `ESPERANDO_APROBACION` y la decisión posterior es del administrador (RF-FLU-06). El texto guía, no valida. |
| PD-10 | Los cambios provocados por el cliente (aprobación por token) se registran en el historial **sin usuario administrativo** (supuesto DA-16, coherente con `usuario_registro=None` de `004`). | Marcarlos con una identidad sintética "cliente". | No existe cuenta de cliente (fuera de alcance); inventar una identidad crearía un dato falso en la auditoría. |
| PD-11 | **Suite nueva** `test_flujo_estados.py` que cubre el flujo completo (reglas, acciones, endpoints, migración de datos) + **limpieza mínima del legacy**: conservar los tests que sigan válidos y eliminar o ajustar los que prueban estados retirados (decisión del usuario). | (a) Reescribir las ~390 pruebas existentes por completo; (b) parchear assertions sueltas en las suites viejas. | Reescribir todo destruye fixtures y patrones aún válidos y multiplica el esfuerzo; parchear a medias mantiene escenarios muertos. La suite nueva da cobertura verificable del flujo y la limpieza retira solo lo que el catálogo viejo invalida. |
| PD-12 | `SeguimientoAprobarView` conserva el comportamiento actual (responde la cotización pendiente más reciente del componente, ahora con el destino según el origen de la espera, PD-13). | Elegir "todas las pendientes" o "por componente" sin decisión del negocio. | DA-3 y DA-4 quedaron **cerradas** en la spec (el cliente responde la pendiente más reciente y la aprobación mueve el componente). No inventar requisitos (AGENTS.md §4). |
| PD-13 | El destino de la aprobación se decide con el **origen de la espera**: `acciones.py` lee la última transición a `ESPERANDO_APROBACION` en `HistorialComponente` (RF-FLU-12) dentro de la transacción y se lo pasa a la función pura `transicion_por_respuesta`. | (a) Campo nuevo `estado_previo_espera` en `Componente`; (b) no distinguir el origen (aprobar siempre a `OPERARIO_TRABAJANDO`). | DA-18: el estado actual por sí solo no distingue si la espera vino de `LISTO_PARA_ENTREGA` (→ `EN_PRUEBAS`) o de otro estado (→ `OPERARIO_TRABAJANDO`). Una migración de estructura solo para esto es desproporcionada; el historial ya guarda el dato y se lee en la misma transacción. |

## 10. Estrategia de tests

`manage.py test` con `django.test`, sin dependencias nuevas (principio 4, RNF-FLU-06). `node --test` se ejecuta como comprobación de toolchain (0 tests JS, como en 004/005/006). El frontend se verifica con Chrome DevTools MCP (RNF-FLU-06/07; disponibilidad confirmada por el usuario). La cobertura principal vive en la **suite nueva** `test_flujo_estados.py` (PD-11); los tests legacy se conservan si siguen válidos y se eliminan o ajustan si prueban estados retirados.

**A. Reglas puras (`SimpleTestCase`, sin BD) — suite nueva `test_flujo_estados.py`**

- Tabla §4.1 por estado: selección de destinos; destinos automáticos nunca ofrecidos; `RECHAZADO` exige cotización rechazada; motivo obligatorio en finales y correcciones; `noop` (CL-16); transición no listada → 409 (CL-03).
- Efectos automáticos: `es_cambio_fuera_de_pendiente` (CL-01/02), `transicion_por_respuesta` (CL-05, CL-06: rechazo → `None`; origen `LISTO_PARA_ENTREGA` → `EN_PRUEBAS`, DA-18), `transicion_por_cotizacion` (los cuatro orígenes: `COTIZANDO`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS`, `LISTO_PARA_ENTREGA` → `ESPERANDO_APROBACION`; en `ESPERANDO_APROBACION` u otro estado → `None`).
- Servicio: `puede_finalizar_servicio` con todos finalizados, con uno en `EN_PRUEBAS` (CL-10) y sin componentes (CL-11); `puede_cancelar_servicio`; cerrados → sin acciones (CL-15); `estados_cerrados()` para el aviso de duplicado de 001.

**B. Acciones y endpoints (`APITestCase`/`TestCase`) — suite nueva `test_flujo_estados.py` (legacy adaptado solo si sigue válido)**

- Primer componente fuera de `PENDIENTE` → servicio `EN_CURSO` en la misma transacción, con ambos historiales (CL-01); segundo componente no cambia el servicio (CL-02).
- Registrar cotización desde `COTIZANDO`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS` o `LISTO_PARA_ENTREGA` → `ESPERANDO_APROBACION` conservando fase y progreso (RF-FLU-05, DA-17/DA-18); cotización adicional ya en `ESPERANDO_APROBACION` no mueve.
- Aprobación por token → `OPERARIO_TRABAJANDO` automático + fase/trabajo iniciado, sin usuario admin (CL-05), **o `EN_PRUEBAS` conservando fase y progreso cuando la espera vino de `LISTO_PARA_ENTREGA` (DA-18)**; rechazo → componente intacto, sin cambio en servicio ni demás componentes (CL-06); respuesta repetida → 409 (CL-07).
- `RECHAZADO` solo con finalización manual + motivo libre + fecha (CL-09); `RECHAZADO` no avanza salvo corrección (CL-08).
- Cierre: con todos finalizados → `FINALIZADO` + fecha + historial (CL-12); con componente en curso → 409 que lo lista (CL-10); sin componentes → 409 (CL-11).
- Cancelación: sin comentario → 400 (CL-13); con componentes en curso → `CANCELADO` sin tocar nada más y fuera del seguimiento (CL-14).
- Cerrados no cambian (CL-15); mismo estado sin historial (CL-16); concurrencia best-effort → 409 sin cambios parciales (CL-17).
- Permisos: solo ADMINISTRATIVO; cliente solo responde cotización por token; sin token u otra acción → rechazo sin modificar datos (CL-21, RF-FLU-14).
- Corrección: sin comentario → 400; con comentario → estado anterior y registro en `HistorialComponente` (CL-22).

**C. Migración de datos — caso en `test_flujo_estados.py`**

- Servicios sembrados con los estados antiguos → ejecutar el `RunPython` de 0008 → comprobar mapeo de CL-18 (`NO_APROBADO→CANCELADO`, comentario vacío), CL-19 (`FINALIZADO_POR_*→LISTO_PARA_ENTREGA`, datos de cierre conservados como historial) y CL-20 (`ENTREGADO→FINALIZADO`, sin inventar `fecha_finalizacion`).

**D. Frontend (manual en navegador con MCP, RNF-FLU-05/07)**

Detalle con sesión administrativa: acciones de servicio (finalizar habilitado/deshabilitado según `resumen_cierre`; cancelar exige comentario); selector de componente con las opciones del backend y textarea obligatorio en finales/correcciones; `409` con recarga; dashboard y filtro con 4 estados; seguimiento público sin códigos eliminados; layout a 375/768/1280 sin scroll horizontal.

## 11. Matriz de cobertura RF → partes

| RF / RNF | Partes del plan |
|---|---|
| RF-FLU-01 | `models.py`, migración 0007, `api.ts`, `AdminServicios.tsx`, `AdminIndicadores.tsx` |
| RF-FLU-02 | `estados.py`, migración 0007, `api.ts`, etiquetas del detalle |
| RF-FLU-03 | `es_cambio_fuera_de_pendiente`, rama en `cambiar_estado_componente`, CL-01/02 |
| RF-FLU-04 | tabla §4.1 en `reglas.py`, ramas `normal`, CL-03 |
| RF-FLU-05 | `transicion_por_cotizacion` en `crear_cotizacion`, sobre `COTIZANDO`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS` y `LISTO_PARA_ENTREGA` (conservando fase y progreso; DA-17/DA-18) |
| RF-FLU-06 | `transicion_por_respuesta` (con origen de la espera desde `HistorialComponente`, PD-13: `LISTO_PARA_ENTREGA` → `EN_PRUEBAS`, DA-18) en `registrar_respuesta`/`registrar_aprobacion_externa`, `_aplicar_inicio_trabajo` (DA-1), `SeguimientoAprobarView` |
| RF-FLU-07 | ramas `finalizar`/`correccion` de `cambiar_estado_componente`, textarea de motivo en UI |
| RF-FLU-08 | rama `finalizar` a `RECHAZADO` con cotización rechazada exigida |
| RF-FLU-09 | `puede_finalizar_servicio`, `resumen_cierre`, `finalizar_servicio`, botón Finalizar |
| RF-FLU-10 | `cancelar_servicio`, endpoint `/cancelar/`, textarea de cancelación |
| RF-FLU-11 | guard de cerrados en acciones y vistas; exclusión del seguimiento |
| RF-FLU-12 | `HistorialComponente`/`HistorialServicio` en todas las ramas |
| RF-FLU-13 | `transaction.atomic` + `select_for_update` + `409`; efectos en la transacción del hecho |
| RF-FLU-14 | `EsAdministrativo` + token en `SeguimientoAprobarView`; tests CL-21 |
| RF-FLU-15 | serializers públicos (etiquetas por `get_estado_display`), exclusión de `CANCELADO`, alineación de `Seguimiento.tsx` |
| RF-FLU-16 | migraciones 0007 y 0008 con tablas de mapeo, creadas **y ejecutadas** en la BD de desarrollo (con advertencia de respaldo si la BD no es de prueba; confirmado por el usuario) |
| RF-FLU-17 | T1 del `tasks.md`: `CONTEXTO_MAESTRO.md` §14/§30 + `MEMORY.md` |
| RNF-FLU-01..03 | autoridad en `reglas.py`/`acciones.py`; bloqueo de filas; historiales |
| RNF-FLU-04/05 | etiquetas en español, texto no solo color, feedback y recarga en 409 |
| RNF-FLU-06 | `django.test` + `node --test` (0 tests) + MCP; sin dependencias nuevas |
| RNF-FLU-07 | responsive en `index.css`/detalle y verificación a 375/768/1280 |

## 12. Riesgos

1. **Ejecución de las migraciones (RF-FLU-16).** La spec manda que esquema y datos sean entregables "pedidos por separado"; el usuario confirmó que **crear y ejecutar ambas forma parte de este encargo** (quiere probar el sistema). El plan las crea en f1 y las ejecuta contra la BD de desarrollo. Riesgo residual: si la BD no es de prueba, el mapeo puede perder distinciones (DA-11) — se advierte que conviene respaldar la BD antes de ejecutar.
2. **Filas de mapeo con supuestos (DA-7 a DA-11).** Varias filas de RF-FLU-16 llevan `[PROPUESTA]`/`[SUPUESTO]` (`NO_APROBADO→CANCELADO`, `LISTO_PARA_ENTREGA→EN_CURSO`, `ENTREGADO→FINALIZADO`, `FINALIZADO_POR_*→LISTO_PARA_ENTREGA`, `APROBADO/EN_PROCESO/RECHAZADO_BLOQUEANTE→OPERARIO_TRABAJANDO/RECHAZADO`). La migración de datos se ejecuta sobre la BD de desarrollo: si esa BD contiene datos que no son de prueba, el mapeo con pérdida debe confirmarse (DA-11) y respaldarse antes.
3. **DA-3 y DA-4 cerradas en la spec; comportamiento vigente a vigilar.** El cliente responde la cotización pendiente más reciente y una aprobación mueve el componente aunque tenga otras cotizaciones pendientes. Si el negocio lo reconsidera, tocará `registrar_respuesta` y su test.
4. **Origen de la espera (DA-18).** Distinguir `OPERARIO_TRABAJANDO` de `EN_PRUEBAS` al aprobar exige leer el `HistorialComponente` dentro de la transacción (PD-13). Si la traza viniera incompleta (dato migrado o histórico sin historial), el destino se decidiría con un origen desconocido: la implementación debe degradar de forma documentada (por defecto `OPERARIO_TRABAJANDO`) y la suite nueva cubre ambos orígenes.
5. **Alcance de la limpieza de tests.** Entre los ~390 tests actuales, una fracción describe escenarios del catálogo viejo. La suite nueva cubre el flujo completo; el legacy se limpia en T6 (conservar los válidos, eliminar o ajustar mínimamente los inválidos — PD-11). Riesgo de regresión cubierto por f6 completa (suite íntegra en verde).
6. **Disponibilidad de Chrome DevTools MCP.** El usuario confirma que está disponible y la verificación visual de T9 se hace con él. Si en la sesión de verificación el navegador no respondiera, la verificación queda pendiente y no se declara cumplida (regla de no inventar validación).
7. **El seguimiento público es placeholder.** `Seguimiento.tsx` no está construido; f5 solo alinea estados/códigos. La línea de tiempo de 4 pasos (DA-15) depende de la 007: no duplicar ese trabajo aquí.

## 13. Criterios de finalización

- Las migraciones 0007 (esquema) y 0008 (datos) están creadas **y aplicadas en la BD de desarrollo**, tras la advertencia de respaldo si la BD no es de prueba (RF-FLU-16; confirmado por el usuario).
- `manage.py check` y `manage.py makemigrations --check` sin incidencias; suite completa con `manage.py test --noinput` en verde —incluida la suite nueva `test_flujo_estados.py` y sin legacy que pruebe estados retirados— y cada RF-FLU con al menos una prueba que lo cubra.
- El servicio solo admite `SOLICITADO`/`EN_CURSO`/`FINALIZADO`/`CANCELADO` y el componente los 8 estados; no queda ninguna referencia a los estados eliminados en backend ni frontend (búsqueda de códigos viejos sin resultados en `backend/` y `frontend/src/`).
- Todo cambio de estado queda en el historial correspondiente; los efectos automáticos ocurren en la transacción del hecho; los `409` no dejan cambios parciales.
- `CONTEXTO_MAESTRO.md` §14 y §30 reflejan el modelo nuevo y `MEMORY.md` anota el cambio (RF-FLU-17) antes del cierre.
- `npm run build` y `npm run lint` en verde; verificación MCP del panel y del seguimiento sin errores de consola, con flujos probados y layout correcto a 375/768/1280.
- Sin dependencias nuevas, sin campos nuevos en los modelos y con la arquitectura existente intacta.
