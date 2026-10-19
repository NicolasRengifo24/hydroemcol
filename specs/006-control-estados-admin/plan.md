# Plan técnico — Spec 006: Control de estados en el panel administrativo

**Plan de implementación · Hidroemcol**
**Spec origen:** `specs/006-control-estados-admin/spec.md` (Estado: aprobada, sin dudas abiertas)
**Autoridad normativa:** `docs/constitution.md` (6 principios) > `AGENTS.md` > `CONTEXTO_MAESTRO.md`
**Restricciones respetadas:** sin migraciones, sin campos nuevos, sin dependencias nuevas, sin Redis/WebSockets/Channels/roles nuevos; backend como autoridad; español en pantalla y mensajes; access token solo en memoria.

---

## 1. Resumen de la solución

Tres frentes, todos sobre piezas existentes:

1. **Componente:** una acción administrativa nueva `cambiar_estado_componente` que valida con reglas puras, ejecuta en transacción con bloqueo de filas y registra en `HistorialComponente`. Seleccionar `EN_PROCESO` es la operación canónica de inicio de trabajo.
2. **Servicio:** una acción administrativa nueva `cambiar_estado_servicio` para los estados normales, que delega en la operación protegida ya existente `finalizar_servicio` (para `FINALIZADO`) y en una nueva `cancelar_servicio` (para `CANCELADO`), con el mapeo de fechas aprobado y registro en `HistorialServicio`. Se excluye `CANCELADO` y los servicios desactivados de dashboard, listados y seguimiento público.
3. **Sesión:** `bootstrapSesion()` en el adaptador HTTP reutiliza el single-flight existente; el guard de ruta administrativa muestra carga mientras resuelve y solo redirige tras el intento.

No se crea ningún modelo ni migración. `HistorialComponente` y `HistorialServicio` ya admiten todo lo que la spec exige.

---

## 2. Archivos que se crean o modifican

### Se crean

| Archivo | Responsabilidad | RF que cubre |
|---|---|---|
| `backend/servicios/tests/test_estados_admin.py` | Pruebas de las reglas puras, las acciones de estado y los endpoints de RF-EST-01..13. | RF-EST-01..13, RNF-EST-02/03 |

### Se modifican

| Archivo | Responsabilidad | RF que cubre |
|---|---|---|
| `backend/servicios/reglas.py` | Añadir funciones puras de selección y resolución de transiciones de componente y servicio, y el predicado de bloqueo por cotización. Sin base de datos ni hora del sistema. | RF-EST-01, 02, 05, 07, 08, 09, 10, 11, 13 |
| `backend/servicios/serializers.py` | Ampliar `construir_hoy` con `estado`/`activo`; exponer `estados_seleccionables` en los serializers administrativos; añadir serializers de entrada del cambio de estado; ampliar `acciones_disponibles` del servicio. | RF-EST-01, 03, 09 (entrada), 12 |
| `backend/servicios/acciones.py` | Añadir `cambiar_estado_componente`, `cambiar_estado_servicio` y `cancelar_servicio`; extraer el helper del inicio canónico de trabajo. | RF-EST-03..13, RNF-EST-02/03 |
| `backend/servicios/views.py` | Añadir `CambiarEstadoComponenteView` y `CambiarEstadoServicioView`; excluir `CANCELADO` y desactivados de listado, dashboard y seguimiento público. | RF-EST-03, 04, 09, 12, 13 |
| `backend/servicios/urls.py` | Registrar las dos rutas nuevas. | RF-EST-03, 09 |
| `frontend/src/services/api.ts` | `bootstrapSesion()`; funciones `cambiarEstadoComponente`/`cambiarEstadoServicio`; tipos `CodigoEstadoComponente` y `estados_seleccionables`. | RF-EST-01..12, RF-EST-14/15 |
| `frontend/src/hooks/useAdministrativo.ts` | Mutaciones `cambiarEstadoComponente` y `cambiarEstadoServicio` con la invalidación existente. | RF-EST-03, 09, RNF-EST-05 |
| `frontend/src/components/RutaAdministrativaProtegida.tsx` | Disparar el bootstrap una vez, mostrar carga mientras resuelve y redirigir solo al terminar. | RF-EST-14, 15 |
| `frontend/src/pages/AdminServicioDetalle.tsx` | Selector de estado del componente y del servicio, comentario obligatorio al cancelar, confirmaciones y feedback. | RF-EST-01, 09, 11, RNF-EST-04/05 |
| `frontend/src/index.css` | Estilos del selector de estado, del campo de comentario y del estado de carga del guard, responsive. | RNF-EST-04 |

> No se toca `backend/servicios/admin.py`: ya mantiene los campos de estado en solo lectura y las acciones llaman a `acciones.py`; las funciones nuevas quedan disponibles para el admin sin cambiar su contrato.

---

## 3. Funciones puras de lógica (`reglas.py`)

Todas siguen el patrón del módulo: reciben `hoy` (estado ya leído), devuelven valores y no tocan base de datos ni reloj. `construir_hoy` se amplía con `'estado'` y `'activo'` del servicio para que las reglas de servicio no necesiten modelos.

```python
def tiene_bloqueo_cotizacion(hoy, componente):
    """Cotización bloqueante pendiente o rechazada. Extrae el criterio que hoy
    vive dentro de `puede_continuar`, para reutilizarlo también cuando el
    componente está finalizado (corrección)."""
    return any(
        cot['es_bloqueante'] and cot['estado'] in ESTADOS_COTIZACION_BLOQUEANTE
        for cot in _cotizaciones_de(hoy, componente)
    )
```

`puede_continuar` se reescribe como `estado not in ESTADOS_FINALIZACION and not tiene_bloqueo_cotizacion(...)`, preservando el comportamiento actual (tests de `test_reglas.py` deben seguir en verde).

```python
ESTADOS_SELECCIONABLES_COMPONENTE = (
    EstadoComponente.PENDIENTE, EstadoComponente.EN_PROCESO,
    EstadoComponente.FINALIZADO_POR_TECNICO, EstadoComponente.FINALIZADO_POR_CLIENTE,
)
ESTADOS_SERVICIO_NORMALES = (
    EstadoServicio.SOLICITADO, EstadoServicio.EN_REVISION, EstadoServicio.COTIZANDO,
    EstadoServicio.ESPERANDO_APROBACION, EstadoServicio.EN_REPARACION,
    EstadoServicio.EN_PRUEBAS, EstadoServicio.LISTO_PARA_ENTREGA,
    EstadoServicio.ENTREGADO, EstadoServicio.NO_APROBADO,
)
ESTADOS_SERVICIO_CERRADOS = (
    EstadoServicio.FINALIZADO, EstadoServicio.ENTREGADO, EstadoServicio.CANCELADO,
)
```

```python
def estados_componente_seleccionables(hoy, componente):
    """Destinos válidos según el estado actual y las reglas. Nunca incluye los
    estados derivados APROBADO/RECHAZADO/RECHAZADO_BLOQUEANTE."""
    actual = componente['estado']
    if actual == EstadoComponente.RECHAZADO_BLOQUEANTE:
        return [EstadoComponente.FINALIZADO_POR_TECNICO,
                EstadoComponente.FINALIZADO_POR_CLIENTE]
    destinos = []
    if actual not in ESTADOS_FINALIZACION and not componente['trabajo_iniciado']:
        destinos.append(EstadoComponente.PENDIENTE)
    if not tiene_bloqueo_cotizacion(hoy, componente):
        destinos.append(EstadoComponente.EN_PROCESO)
    destinos += [EstadoComponente.FINALIZADO_POR_TECNICO,
                 EstadoComponente.FINALIZADO_POR_CLIENTE]
    return destinos
```

```python
def resolver_transicion_componente(hoy, componente, destino):
    """Devuelve {'permitido', 'tipo', 'codigo', 'motivo'}.
    tipo ∈ {'noop','pendiente','iniciar','finalizar'}."""
    if destino not in ESTADOS_SELECCIONABLES_COMPONENTE:
        return {'permitido': False, 'codigo': 400,
                'motivo': 'Ese estado no puede asignarse manualmente.'}
    actual = componente['estado']
    if destino == actual:
        return {'permitido': True, 'tipo': 'noop', 'motivo': ''}
    if destino not in estados_componente_seleccionables(hoy, componente):
        return {'permitido': False, 'codigo': 409,
                'motivo': motivo_bloqueo(hoy, componente)
                          or 'La regla vigente no permite ese cambio de estado.'}
    if destino == EstadoComponente.PENDIENTE:
        return {'permitido': True, 'tipo': 'pendiente', 'motivo': ''}
    if destino == EstadoComponente.EN_PROCESO:
        return {'permitido': True, 'tipo': 'iniciar', 'motivo': ''}
    return {'permitido': True, 'tipo': 'finalizar', 'motivo': ''}
```

```python
def estados_servicio_seleccionables(hoy):
    if not hoy['activo'] or hoy['estado'] in ESTADOS_SERVICIO_CERRADOS:
        return []
    return list(ESTADOS_SERVICIO_NORMALES)

def fecha_para_estado_servicio(destino):
    return {'FINALIZADO': 'fecha_finalizacion', 'ENTREGADO': 'fecha_entrega'}.get(destino)

def puede_cancelar_servicio(hoy):
    return bool(hoy['activo']) and hoy['estado'] not in ESTADOS_SERVICIO_CERRADOS

def resolver_transicion_servicio(hoy, destino, comentario=''):
    """Mismo contrato que la de componente; tipo ∈ {'noop','normal','finalizar','cancelar'}."""
    todos = set(ESTADOS_SERVICIO_NORMALES) | {
        EstadoServicio.FINALIZADO, EstadoServicio.CANCELADO}
    if destino not in todos:
        return {'permitido': False, 'codigo': 400, 'motivo': 'Estado de servicio inválido.'}
    if not hoy['activo']:
        return {'permitido': False, 'codigo': 409, 'motivo': 'El servicio está desactivado.'}
    if hoy['estado'] in ESTADOS_SERVICIO_CERRADOS:
        return {'permitido': False, 'codigo': 409,
                'motivo': 'El servicio ya está cerrado y no admite más cambios de estado.'}
    if destino == hoy['estado']:
        return {'permitido': True, 'tipo': 'noop', 'motivo': ''}
    if destino == EstadoServicio.CANCELADO:
        if not comentario.strip():
            return {'permitido': False, 'codigo': 400,
                    'motivo': 'La cancelación requiere un comentario.'}
        return {'permitido': True, 'tipo': 'cancelar', 'motivo': ''}
    if destino == EstadoServicio.FINALIZADO:
        if not puede_finalizar_servicio(hoy):
            return {'permitido': False, 'codigo': 409,
                    'motivo': resumen_cierre(hoy)['detalle'],
                    'extra': {'resumen_cierre': resumen_cierre(hoy)}}
        return {'permitido': True, 'tipo': 'finalizar', 'motivo': ''}
    return {'permitido': True, 'tipo': 'normal', 'motivo': ''}
```

---

## 4. Algoritmo en pseudocódigo (`acciones.py`)

### 4.1 Reutilizar el inicio canónico de trabajo (RF-EST-06)

```
función _aplicar_inicio_trabajo(componente):
    componente.estado = EN_PROCESO
    componente.fase = DESMONTAJE_INICIADO
    componente.trabajo_iniciado = True
    si componente.fecha_inicio_trabajo es None:
        componente.fecha_inicio_trabajo = ahora
    componente.motivo_finalizacion = ''
    componente.fecha_finalizacion = None
    devolver ['estado','fase','trabajo_iniciado','fecha_inicio_trabajo',
              'motivo_finalizacion','fecha_finalizacion']
```

`iniciar_trabajo` se refactoriza para asignar esos campos con el helper (mantiene su validación previa de `puede_continuar` y su historial), de modo que "iniciar trabajo" y "seleccionar EN_PROCESO" sean la misma operación (RF-EST-06).

### 4.2 Cambio de estado del componente (RF-EST-03, 04, 05, 07, 08, 17)

```
función cambiar_estado_componente(servicio, componente_id, nuevo_estado, comentario, usuario):
    en transacción:
        servicio = bloquear(Servicio, pk)                      # fila de servicio
        componente = bloquear(Componente, pk, servicio=servicio) o ErrorDeAccion 404
        si servicio.estado en ESTADOS_SERVICIO_CERRADOS:        # CL-14
            ErrorDeAccion 409 'El servicio está cerrado...'
        hoy = construir_hoy(servicio)
        dato = el componente de hoy con id == componente.pk
        decisión = resolver_transicion_componente(hoy, dato, nuevo_estado)
        si no decisión.permitido:
            ErrorDeAccion(decisión.codigo, decisión.motivo, decisión.extra)
        si decisión.tipo == 'noop':                            # CL-13
            devolver componente                                # sin historial
        estado_anterior = componente.estado
        fase_registrada = ''
        según decisión.tipo:
            'pendiente':                                           # RF-EST-08
                componente.estado = PENDIENTE
                componente.fase = RECIBIDO
                campos = ['estado','fase']
            'iniciar':                                             # RF-EST-06
                campos = _aplicar_inicio_trabajo(componente)
                fase_registrada = DESMONTAJE_INICIADO
            'finalizar':                                           # RF-EST-07
                componente.estado = nuevo_estado
                componente.motivo_finalizacion = nuevo_estado
                componente.fecha_finalizacion = ahora
                campos = ['estado','motivo_finalizacion','fecha_finalizacion']
        componente.save(update_fields=campos)
        HistorialComponente.crear(
            componente, estado_anterior, estado_nuevo=nuevo_estado,
            fase_registrada, comentario, usuario)
        _historial_accion(servicio, 'Estado del componente actualizado...', usuario)
    devolver componente
```

### 4.3 Cambio de estado del servicio (RF-EST-09, 10, 11, 12)

```
función cambiar_estado_servicio(servicio, destino, comentario, usuario):
    en transacción:
        servicio = bloquear(Servicio, pk)
        hoy = construir_hoy(servicio)
        decisión = resolver_transicion_servicio(hoy, destino, comentario)
        si no decisión.permitido:
            ErrorDeAccion(decisión.codigo, decisión.motivo, decisión.extra)
        si decisión.tipo == 'noop':
            devolver servicio
        si decisión.tipo == 'cancelar':
            devolver _cancelar_servicio_bloqueado(servicio, comentario, usuario)
        si decisión.tipo == 'finalizar':
            devolver _finalizar_servicio_bloqueado(servicio, usuario)   # código actual
        # tipo 'normal'
        servicio.estado = destino
        campos = ['estado']
        campo_fecha = fecha_para_estado_servicio(destino)
        si campo_fecha:                                        # ENTREGADO -> fecha_entrega
            setattr(servicio, campo_fecha, ahora)
            campos.append(campo_fecha)
        servicio.save(update_fields=campos)                    # nunca borra fechas
        HistorialServicio.crear(servicio, estado=destino, comentario, usuario,
                                visible_cliente=False)
    devolver servicio

función cancelar_servicio(servicio, comentario, usuario):      # RF-EST-11
    en transacción:
        servicio = bloquear(Servicio, pk)
        si not servicio.activo o estado en ESTADOS_SERVICIO_CERRADOS: ErrorDeAccion 409
        si no comentario.strip(): ErrorDeAccion 400               # CL-21
        servicio.estado = CANCELADO                               # no toca activo
        servicio.save(update_fields=['estado'])
        HistorialServicio.crear(servicio, CANCELADO, comentario, usuario)
        # ningún componente se marca finalizado; no se borra nada
    devolver servicio
```

`finalizar_servicio` (existente) se reutiliza como bloque interno; el endpoint de estado lo invoca para `FINALIZADO` en lugar de duplicar la regla.

---

## 5. Cómo se pinta en la interfaz

### 5.1 Guard de sesión (RF-EST-14, 15)

- `bootstrapSesion()` cambia el estado a `'autenticando'`, llama a `refrescarSesion()` (single-flight ya existente). Si obtiene token → `'autenticada'`. Si el refresh responde 401 → reintenta una vez (rotación entre pestañas); si vuelve a fallar o el error es de red/`5xx`/`429` → limpia la sesión y deja `'anonima'`.
- `RutaAdministrativaProtegida` dispara `bootstrapSesion()` una sola vez (`useEffect` + bandera) cuando el estado es `'anonima'`; mientras es `'autenticando'` o el bootstrap está en curso muestra un bloque de carga con `role="status"` ("Restaurando sesión…") y **no** redirige. Solo cuando el intento terminó y no hay sesión, redirige a `/admin/login` conservando `from`.
- No se dispara en rutas públicas: el guard solo envuelve el árbol `/admin`.

### 5.2 Detalle del servicio (`AdminServicioDetalle.tsx`)

- **Servicio — sección "Acciones del servicio":** si `servicio.estados_seleccionables` no está vacío, un `<select>` "Estado del servicio" con esas opciones (etiquetas en español ya legibles) + botón "Guardar estado" y confirmación. `FINALIZADO` no aparece en el selector: se ofrece el botón existente "Finalizar servicio" con su `resumen_cierre.motivo`. `CANCELADO` se activa desde el selector y despliega un `<textarea>` "Comentario de cancelación" obligatorio antes de confirmar. El botón "Desactivar servicio" se conserva.
- **Componente — cada tarjeta:** si `componente.estados_seleccionables` tiene opciones, un `<select>` "Cambiar estado" con confirmación; al elegir `CANCELADO`/corrección NO aplica (solo componente); para el componente el comentario es opcional y se envía si el usuario lo escribe en un campo corto. Las opciones ya excluyen los estados derivados y, en `RECHAZADO_BLOQUEANTE`, solo muestran finalizar (RF-EST-01). El mensaje de `motivo_bloqueo` se muestra junto al selector cuando `puede_continuar` es falso.
- **Feedback (RNF-EST-05):** éxito con `role="status"`; error con `role="alert"`; si el backend responde `409`, se muestra el mensaje *y* el botón "Recargar detalle" (la mutación ya invalida en `409`, `opcionesMutacion` en `useAdministrativo.ts`). Nunca se finge éxito.
- **Accesibilidad y responsive (RNF-EST-04):** `<label htmlFor>` + `id`, foco visible, `aria-describedby` para el motivo del bloqueo, controles apilados en móvil y en fila a partir de 640–680 px, sin scroll horizontal para operar.

### 5.3 Historial

- El historial del servicio ya se pinta en la sección "Historial del servicio" (`HistorialServicio`). El historial del componente ya viaja en `componente.historial`; el plan no añade un panel nuevo para no inflar la tarjeta, y deja visible el último cambio en la etiqueta de estado. (Ampliar el panel de historial del componente queda **fuera** de este plan salvo que el usuario lo pida.)

---

## 6. Decisiones técnicas justificadas

| # | Decisión | Alternativa descartada | Motivo |
|---|---|---|---|
| D-1 | Un endpoint por acción: `POST .../componentes/{id}/estado/` y `POST .../servicios/{id}/estado/` con `{estado, comentario}`. | Reutilizar `iniciar-trabajo`/`finalizar` y añadir `PATCH` de estado en el `ViewSet`. | Un solo punto de decisión para el cambio de estado, sin dispersar la validación ni exponer `estado` como campo editable (principio 3). `FINALIZADO`/`CANCELADO` se rutean internamente a las operaciones protegidas, así que el selector no es una puerta trasera (RF-EST-10/11). |
| D-2 | `estados_seleccionables` calculado en backend y expuesto en el serializer. | Calcular la lista en el frontend. | RF-EST-01/09: las opciones vienen del backend; el frontend no decide transiciones (principio 3). |
| D-3 | Ampliar `construir_hoy` con `estado` y `activo` en lugar de crear un `hoy_servicio`. | Crear una segunda función constructora. | Una sola traducción modelo→reglas; las funciones puras de servicio y componente comparten el mismo diccionario. |
| D-4 | Extraer `tiene_bloqueo_cotizacion` y reescribir `puede_continuar` sobre ella. | Duplicar el criterio dentro de la regla de corrección. | Evita dos definiciones de "bloqueo"; permite reutilizarlo cuando el componente está finalizado (corrección a `EN_PROCESO`). |
| D-5 | Al reabrir a `EN_PROCESO` desde un estado final se limpian `motivo_finalizacion` y `fecha_finalizacion`. | Conservarlos mientras el componente vuelve a estar en proceso. | Un componente `EN_PROCESO` con motivo/fecha de finalización es incoherente; el estado anterior queda auditado en `HistorialComponente`. No afecta `fecha_inicio_trabajo` (no se borra evidencia de inicio). |
| D-6 | `FINALIZADO`/`ENTREGADO`/`CANCELADO` bloquean cambios posteriores de estado; `ENTREGADO` sí aparece como destino normal. | Permitir `FINALIZADO → ENTREGADO`. | Criterio de aceptación 6 lo exige; el plan no inventa reapertura (fuera de alcance). |
| D-7 | Mismo estado en componente/servicio = no-op idempotente sin historial. | Responder `409`. | CL-13 lo exige para el componente; se mantiene la coherencia en el servicio y se evita ruido en el historial. |
| D-8 | `CANCELADO` se excluye del listado, dashboard y seguimiento público con `.exclude(estado=CANCELADO)`. | Añadir un booleano nuevo al modelo. | RF-EST-13/RF-EST-11: no cambia `activo` y no requiere migración; se reutiliza el estado. |
| D-9 | El bootstrap reutiliza `refrescarSesion()` (single-flight) y reintenta una vez solo ante `401`. | Un `fetch` de refresh aparte en el guard. | Reutiliza el mecanismo probado de `004`, conserva single-flight y disipa la rotación concurrente (CL-20) sin almacenar tokens. |
| D-10 | El guard resuelve el bootstrap; `SesionContext` no cambia de forma. | Mover el bootstrap al `SesionProvider` global. | Evita pedir refresh en rutas públicas (RF-EST-14) y mantiene el árbol público intacto. |

---

## 7. Estrategia de tests

`manage.py test` con `django.test` (principio 4, sin dependencias nuevas). Nuevo `backend/servicios/tests/test_estados_admin.py`; se amplía `test_reglas.py` con las funciones puras nuevas.

**A. Reglas puras (`SimpleTestCase`, sin BD)**

- `estados_componente_seleccionables` por estado: `PENDIENTE`, `APROBADO`, `RECHAZADO`, `EN_PROCESO`, `RECHAZADO_BLOQUEANTE` (solo finalizar), finales; con/sin cotización bloqueante pendiente y rechazada; con/sin `trabajo_iniciado`. (RF-EST-01, 02, 05, 08)
- `resolver_transicion_componente`: destino derivado → `400`; bloqueo → `409`; `PENDIENTE` con trabajo iniciado → rechazo; mismo estado → `noop`; final→`EN_PROCESO`/final. (RF-EST-04, 07, 08; CL-03/04/05/13)
- `estados_servicio_seleccionables`, `fecha_para_estado_servicio`, `puede_cancelar_servicio`, `resolver_transicion_servicio`: cerrado → `[]`; cancelar sin comentario → `400`; `FINALIZADO` con componente pendiente → `409`. (RF-EST-09, 10, 11, 12; CL-15, 16, 21)

**B. Acciones y endpoints (`APITestCase`/`TestCase`)**

- `cambiar_estado_componente` a `EN_PROCESO` desde `PENDIENTE`: deja fase `DESMONTAJE_INICIADO`, `trabajo_iniciado=True`, fecha y `HistorialComponente` con estado anterior/nuevo. (RF-EST-06)
- Bloqueo por cotización bloqueante `PENDIENTE`/`RECHAZADA`: `409`, sin cambios de estado/fase (CL-01/02, RF-EST-05).
- `RECHAZADO_BLOQUEANTE` finaliza pero no pasa a `EN_PROCESO` (RF-EST-05).
- Estado derivado solicitado → `400` y sin tocar cotizaciones (CL-03).
- `PENDIENTE` tras iniciar/finalizar → `409` (CL-04); mismo estado → `200` sin historial (CL-13).
- Corrección desde final a destinos válidos y rechazo de inválidos (CL-05, RF-EST-07).
- Componente de otro servicio → `404` (CL-08); servicio en `FINALIZADO`/`ENTREGADO`/`CANCELADO` → `409` (CL-14).
- Servicio: cambio a estado normal sin fecha; `ENTREGADO` escribe `fecha_entrega`; ninguna transición borra `fecha_finalizacion`/`fecha_entrega` previas; `HistorialServicio` creado (RF-EST-12).
- `FINALIZADO` con todos los componentes finalizados → cierra y escribe `fecha_finalizacion`; con un componente pendiente o sin componentes → `409` (RF-EST-10, CL-15; reutiliza el criterio ya probado en `test_recorridos.py`).
- `CANCELADO`: exige comentario (CL-21), no cambia `activo`, no finaliza componentes; queda excluido de listado, dashboard, `SeguimientoView` y `SeguimientoAprobarView` (RF-EST-11/13).
- Servicio desactivado: cambio rechazado y sigue fuera del operativo (CL-09).
- Permisos: sin JWT y con rol no administrativo → `401`/`403` (RNF-EST-01).
- Concurrencia: segunda finalización del mismo componente/servicio → `409` sin cambios parciales (CL-07/12, RNF-EST-02) — verificación best-effort con dos llamadas secuenciales sobre estado recargado, ya que el bloqueo real es de fila de BD.

**C. Frontend (manual en navegador, RNF-EST-07)**

Levantar frontend y `manage.py runserver`; con MCP verificar: recarga de `/admin/servicios/:id` mantiene la sesión (carga → panel, sin parpadeo a login); el selector de componente ofrece solo los 4 estados operativos y bloquea con el motivo; `EN_PROCESO` refleja el inicio de trabajo; el selector de servicio aplica el mapeo de fechas y `CANCELADO` exige comentario; `409` pide recargar; layout móvil/tablet sin scroll horizontal.

---

## 8. Matriz de cobertura RF → partes

| RF / RNF | Partes del plan |
|---|---|
| RF-EST-01 | `reglas.estados_componente_seleccionables`, `serializers` (`estados_seleccionables`), UI selector componente |
| RF-EST-02 | `reglas.estados_componente_seleccionables` (no derivados), validación de acción |
| RF-EST-03 | `acciones.cambiar_estado_componente`, vistas, transacción/bloqueo, `HistorialComponente` |
| RF-EST-04 | `resolver_transicion_*`, `409`, handle de conflicto en UI/hooks |
| RF-EST-05 | `tiene_bloqueo_cotizacion`, `resolver_transicion_componente`, motivo en UI |
| RF-EST-06 | `_aplicar_inicio_trabajo`, rama `iniciar`, `iniciar_trabajo` refactor |
| RF-EST-07 | rama `finalizar` + corrección, `HistorialComponente` |
| RF-EST-08 | ramas `pendiente`/`iniciar`/`finalizar`, no-op, no borrar fechas |
| RF-EST-09 | `estados_servicio_seleccionables`, serializer + UI selector servicio |
| RF-EST-10 | `resolver_transicion_servicio` → `finalizar_servicio`, `puede_finalizar_servicio` |
| RF-EST-11 | `cancelar_servicio`, comentario obligatorio, UI textarea de cancelación |
| RF-EST-12 | `fecha_para_estado_servicio`, `cambiar_estado_servicio`, `HistorialServicio`, permisos |
| RF-EST-13 | `.exclude(estado=CANCELADO)` en listado/dashboard/seguimiento; guard de servicio desactivado |
| RF-EST-14 | `bootstrapSesion()` single-flight, guard dispara solo en rutas admin |
| RF-EST-15 | guard muestra carga y redirige solo al terminar; limpieza ante fallo |
| RNF-EST-01 | `EsAdministrativo` en las vistas nuevas |
| RNF-EST-02 | `transaction.atomic` + `select_for_update`, `409` |
| RNF-EST-03 | `HistorialComponente` / `HistorialServicio`, historial no eliminable |
| RNF-EST-04 | estilos de selector/foco/contraste, responsive en `index.css` y detalle |
| RNF-EST-05 | invalidación en hooks + feedback en la página |
| RNF-EST-06 | bootstrap conserva memoria + cookie `httpOnly` de `004` |
| RNF-EST-07 | `django.test` + verificación manual |

---

## 9. Orden de implementación sugerido (para `tasks.md`)

1. `reglas.py` (puras) + ampliación de `construir_hoy` + pruebas puras.
2. `acciones.py`: helper de inicio, `cambiar_estado_componente`, `cambiar_estado_servicio`, `cancelar_servicio`.
3. `serializers.py`: entradas, `estados_seleccionables`, `acciones_disponibles`.
4. `views.py` + `urls.py`: dos vistas/rutas + exclusiones de `CANCELADO`.
5. Pruebas de acciones/endpoints (`test_estados_admin.py`).
6. `api.ts` + `useAdministrativo.ts`: bootstrap y mutaciones.
7. `RutaAdministrativaProtegida.tsx`: bootstrap + carga.
8. `AdminServicioDetalle.tsx` + `index.css`: selectores y feedback.
9. Verificación manual con MCP y actualización de `MEMORY.md`.

---

## 10. Fuera de alcance confirmado

Migraciones o campos nuevos; reapertura de servicios cancelados; corrección de estado a nivel de servicio; notificaciones, tiempo real, Redis/Channels/WebSockets; paneles nuevos de historial de componente más allá de lo ya expuesto; cambios en catálogos, cotizaciones o seguimiento público distintos de excluir `CANCELADO`.
