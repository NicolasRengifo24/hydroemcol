# Spec 011 — Coherencia del flujo y cotización por acción

**Especificación funcional · Hidroemcol**  
**Estado: aprobada**

## 1. Contexto y objetivo

La spec 008 definió el flujo simplificado de estados del componente. Su tabla §4.1 encadena
`PENDIENTE → EN_REVISION → COTIZANDO → ESPERANDO_APROBACION` como si `COTIZANDO` fuese un paso
manual que el administrativo elige. En la operación real esto obliga a "cotizar" un componente que
no necesita cotización, y confunde dos hechos distintos:

1. el avance normal del trabajo (revisión → operario → pruebas → listo); y
2. la creación de una cotización, que es una **acción separada** sobre un componente.

**Objetivo:** separar ambos hechos.

- `COTIZANDO` deja de ser un destino manual: la cotización se crea con el botón **Crear
  cotización** (acción ya existente), que mueve el componente a `ESPERANDO_APROBACION`.
- El avance normal del trabajo es lineal y no exige cotizar.
- Una cotización **bloqueante pendiente** impide avanzar: el backend rechaza el avance con aviso.
- Una cotización **no bloqueante pendiente** no impide avanzar.

**Por qué:** el administrativo registra el trabajo real tal como ocurre, y la cotización se
convierte en una acción explícita e independiente, coherente con el flujo público.

## 2. Relación con especificaciones anteriores

Esta especificación **supera parcialmente** la spec 008. Todo lo no listado permanece vigente.

### 2.1 Spec 008 §4.1 — Tabla de destinos manuales

**Superadas** las filas de `EN_REVISION` y `COTIZANDO`:

- `EN_REVISION`: de `[COTIZANDO]` pasa a `[OPERARIO_TRABAJANDO]`.
- `COTIZANDO`: permanece `[]` (ya no es alcanzable por acción manual; se conserva en el catálogo
  por compatibilidad de datos históricos, pero nunca se ofrece ni se asigna).

El resto de la tabla se mantiene:

| Origen | Destinos manuales |
|---|---|
| `PENDIENTE` | `EN_REVISION` |
| `EN_REVISION` | `OPERARIO_TRABAJANDO` |
| `OPERARIO_TRABAJANDO` | `EN_PRUEBAS` |
| `EN_PRUEBAS` | `LISTO_PARA_ENTREGA` |
| `LISTO_PARA_ENTREGA` | `EN_PRUEBAS` |
| `ESPERANDO_APROBACION` | `RECHAZADO` |
| `RECHAZADO` | `ESPERANDO_APROBACION` |
| `COTIZANDO` | — |

### 2.2 Spec 008 §4.3 — Mapeo público

Se **mantiene** el mapeo: `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION` y
`OPERARIO_TRABAJANDO` → paso público "Revisión y cotización". La creación de una cotización y su
estado de espera siguen siendo visibles al cliente en ese paso.

### 2.3 Spec 002 / RF-COT-04 — Continuar con cotización pendiente

Se **restituye** el principio de la 002 (parcialmente superado por la 008 §2.2): una cotización
bloqueante pendiente impide que el componente avance. Se concreta en RF-COH-03 de esta spec,
respetando el modelo de estados de la 008 (el estado de espera sigue siendo `ESPERANDO_APROBACION`,
no un estado "detenido" aparte).

## 3. Requisitos funcionales

- **RF-COH-01 — `COTIZANDO` no es manual.** `COTIZANDO` no aparece en
  `estados_componente_seleccionables` de ningún estado. Se conserva en el catálogo `EstadoComponente`
  para no invalidar datos históricos.

- **RF-COH-02 — `EN_REVISION` avanza a trabajo.** El único destino manual de `EN_REVISION` es
  `OPERARIO_TRABAJANDO`. Esta transición marca `trabajo_iniciado=True`, fija la fase
  `DESMONTAJE_INICIADO` y registra `fecha_inicio_trabajo` si aún es nula (mismo efecto que hoy tiene
  la aprobación de cotización).

- **RF-COH-03 — Bloqueo por cotización bloqueante pendiente.** Una cotización con
  `es_bloqueante=True` y `estado='PENDIENTE'` detiene el componente: en `ESPERANDO_APROBACION` el
  único destino manual disponible es `RECHAZADO` (previa cotización rechazada). Cualquier intento de
  avanzar se rechaza con `409` y un aviso claro. El componente permanece donde está.

- **RF-COH-04 — Crear cotización es una acción, no un estado.** El endpoint de creación de
  cotización mueve el componente a `ESPERANDO_APROBACION` desde cualquier estado de trabajo
  **excepto** `LISTO_PARA_ENTREGA` y los estados cerrados del servicio. Orígenes válidos:
  `EN_REVISION`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS`. Desde `PENDIENTE` no se permite cotizar
  (el repuesto aún no está disponible y no se conoce el trabajo).

- **RF-COH-05 — Cotización no bloqueante deja avanzar.** Una cotización con `es_bloqueante=False`
  mueve el componente a `ESPERANDO_APROBACION` (visible al cliente en "Revisión y cotización"),
  pero **no lo detiene**: en `ESPERANDO_APROBACION` el selector ofrece además el avance normal
  desde el origen de la espera (`EN_REVISION → OPERARIO_TRABAJANDO`,
  `OPERARIO_TRABAJANDO → EN_PRUEBAS`, `EN_PRUEBAS → LISTO_PARA_ENTREGA`), de modo que el
  administrativo puede seguir el flujo mientras el cliente responde.

- **RF-COH-06 — Aprobación devuelve al origen.** Al aprobar una cotización, el componente vuelve
  al estado desde el que se creó la espera (`_origen_espera`): `EN_REVISION` vuelve a
  `EN_REVISION`, `EN_PRUEBAS` a `EN_PRUEBAS`, `OPERARIO_TRABAJANDO` a `OPERARIO_TRABAJANDO`. El
  fallback histórico (`OPERARIO_TRABAJANDO`) se mantiene solo si no hay historial de origen.

- **RF-COH-07 — Rechazo no mueve.** Responder "rechazada" a una cotización no mueve el componente
  (se mantiene el comportamiento de la 008).

## 4. Casos límite

- **CL-COH-01:** intento de asignar `COTIZANDO` manualmente → `409` (no está en destinos).
- **CL-COH-02:** componente en `ESPERANDO_APROBACION` (origen `EN_PRUEBAS`) con cotización
  bloqueante pendiente → el selector solo ofrece `RECHAZADO`; intento de pasar a
  `LISTO_PARA_ENTREGA` → `409` con aviso de cotización bloqueante.
- **CL-COH-03:** componente en `ESPERANDO_APROBACION` (origen `EN_PRUEBAS`) con cotización **no**
  bloqueante pendiente → el selector ofrece `RECHAZADO` y `LISTO_PARA_ENTREGA`; puede avanzar.
- **CL-COH-04:** crear cotización con componente en `PENDIENTE` → `409`.
- **CL-COH-05:** crear cotización con componente en `LISTO_PARA_ENTREGA` → `409`.
- **CL-COH-06:** aprobar cotización creada en `EN_REVISION` → vuelve a `EN_REVISION`.
- **CL-COH-07:** aprobar cotización creada en `EN_PRUEBAS` → vuelve a `EN_PRUEBAS`.
- **CL-COH-08:** `EN_REVISION → OPERARIO_TRABAJANDO` deja `trabajo_iniciado=True` y fase
  `DESMONTAJE_INICIADO` (registro equivalente al de la aprobación de cotización).

## 5. Criterios de aceptación

1. `estados_componente_seleccionables` devuelve `EN_REVISION: ['OPERARIO_TRABAJANDO']` y
   `COTIZANDO: []`.
2. `EN_REVISION → OPERARIO_TRABAJANDO` inicia trabajo (fase y fecha).
3. Avanzar con cotización bloqueante pendiente devuelve `409`; con no bloqueante, procede.
4. Crear cotización desde `EN_REVISION`/`OPERARIO_TRABAJANDO`/`EN_PRUEBAS` mueve a
   `ESPERANDO_APROBACION`; desde `PENDIENTE` o `LISTO_PARA_ENTREGA` devuelve `409`.
5. Aprobar una cotización devuelve el componente a su estado de origen.
6. La suite `python manage.py test servicios` pasa.

## 6. Trazabilidad

| Requisito | Implementación | Prueba |
|---|---|---|
| RF-COH-01 | `reglas.TRANSICIONES_MANUALES_COMPONENTE` | `test_tabla_de_destinos_manuales_por_estado` |
| RF-COH-02 | `acciones.cambiar_estado_componente` + `_aplicar_inicio_trabajo` | `test_en_revision_inicia_trabajo` |
| RF-COH-03 | `reglas.resolver_transicion_componente` | `test_bloqueo_por_cotizacion_bloqueante` |
| RF-COH-04 | `reglas.transicion_por_cotizacion` | `test_cotizacion_desde_origenes_validos` |
| RF-COH-05 | `reglas.tiene_bloqueo_cotizacion` | `test_cotizacion_no_bloqueante_no_detiene` |
| RF-COH-06 | `reglas.transicion_por_respuesta` | `test_aprobacion_vuelve_al_origen` |
| RF-COH-07 | `reglas.transicion_por_respuesta` | `test_respuesta_aprobada_y_rechazada` |

## 7. Decisiones tomadas con el usuario

1. No existe botón/estado "Cotizando": la cotización se crea con el botón **Crear cotización**.
2. `ESPERANDO_APROBACION` es el estado de espera (visible al cliente en "Revisión y cotización").
4. Cotización **no bloqueante** pendiente **deja avanzar** (el componente queda en
   `ESPERANDO_APROBACION` pero el selector ofrece el avance normal desde el origen).
5. Cotización bloqueante pendiente **detiene**: solo `RECHAZADO` y aviso `409` al intentar avanzar.
5. Selección manual en `EN_REVISION`: solo `OPERARIO_TRABAJANDO`.
6. `EN_REVISION → OPERARIO_TRABAJANDO` marca trabajo iniciado y fase `DESMONTAJE_INICIADO`.
