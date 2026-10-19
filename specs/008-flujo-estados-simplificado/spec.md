# Spec 008 — Flujo de estados simplificado

**Especificación funcional · Hidroemcol**  
**Estado: aprobada**

> Convención: `[PROPUESTA]` marca una decisión que este borrador propone y que aún no está
> confirmada por el negocio. `[SUPUESTO]` marca una consecuencia deducida de las decisiones
> cerradas. Las decisiones cerradas no llevan marca.

## 1. Contexto y objetivo

El flujo de estados vigente tiene once estados de servicio y siete de componente. Varios de
ellos no corresponden a la operación real: `APROBADO`, `RECHAZADO_BLOQUEANTE`, `EN_PROCESO`,
`FINALIZADO_POR_CLIENTE` y `FINALIZADO_POR_TECNICO` en el componente, y `EN_REVISION`,
`COTIZANDO`, `ESPERANDO_APROBACION`, `EN_REPARACION`, `EN_PRUEBAS`, `LISTO_PARA_ENTREGA`,
`ENTREGADO` y `NO_APROBADO` en el servicio. El administrativo debe recordar cuál de los
estados casi equivalentes usar, y el cliente no entiende en qué punto está su servicio a partir
de esa lista.

**Objetivo:** reducir el flujo a un conjunto pequeño de estados con significado de negocio
claro, en el que cada cambio sea:

- **automático**, porque lo produce un hecho registrado (una cotización creada, una respuesta del
  cliente, el primer componente que sale de pendiente); o
- **manual y explícito**, porque lo decide el administrativo mediante una acción con reglas
  validadas en el backend.

**Por qué:** un flujo con menos estados y transiciones explícitas reduce errores de registro,
hace que el seguimiento público refleje el proceso real y deja un rastro legible de cada cambio.

## 2. Relación con especificaciones anteriores

Esta especificación **supersede** únicamente las cláusulas listadas en §2.1 a §2.5. Todo lo no
listado permanece vigente. Cuando una cláusula superada se mencione más abajo, se indica si
queda sustituida por una regla de esta spec o simplemente retirada.

### 2.1 Especificación 006 — Control de estados en el panel

**Superadas:**

- **RF-EST-01 a RF-EST-13**, en lo que dependan de los estados eliminados o de su catálogo:
  selector de estados del componente con `EN_PROCESO` como destino, `EN_PROCESO` como inicio
  canónico de trabajo, `RECHAZADO_BLOQUEANTE` como estado no activo, selector de estados del
  servicio con los nueve estados normales, y mapeo de fechas de `ENTREGADO` y `NO_APROBADO`.
  **No se superan** RF-EST-14 y RF-EST-15 (bootstrap de sesión), ni el mecanismo de
  concurrencia de RF-EST-04 y RNF-EST-02.
- **CL-02** (cotización bloqueante rechazada como detención finalizable conforme a RF-COT-05): el
  rechazo ya no mueve el componente y su cierre se rige por RF-FLU-08. **CL afectados:** CL-01,
  CL-02, CL-03, CL-04, CL-05, CL-06, CL-14, CL-16 y CL-17.
- **Criterios de aceptación 5 y 6** (selector de servicio y fechas/cierre), y los criterios 1 y 2
  en lo que nombran `EN_PROCESO`, `APROBADO`, `RECHAZADO` o `RECHAZADO_BLOQUEANTE`.
- **§10 (Decisiones preservadas)**, en lo que declara vigentes las cotizaciones bloqueantes que
  impiden `EN_PROCESO`, la finalización de `RECHAZADO_BLOQUEANTE` conforme a RF-COT-05 y el
  criterio de cierre anterior.
- **D-1 y D-6** del plan de la especificación 006 se retiran de la lista de cláusulas superadas:
  el plan de la 006 no contiene decisiones numeradas. **D-8 no se supera y sigue vigente**
  (corrección de cierres por error humano): se concreta en RF-FLU-07 (ver §11, duda DA-13).

### 2.2 Especificación 002 — Desarrollo del backend (cotización por componente)

**Superadas:**

- **Glosario §4.3** (estados de componente): sustituido por el catálogo de §4 de esta spec.
- **Glosario §4.4** (clasificación activo / no activo / finalizado): sustituido. Las categorías
  pasan a definirse en §4 de esta spec.
- **Glosario §4.5** (posibilidad de continuar): sustituido. Que un componente pueda o no avanzar lo
  define su estado y la tabla de §4.1, no el balance de cotizaciones bloqueantes.
- **Glosario §4.6** (trabajo iniciado): sustituido en lo que atribuye el inicio al técnico. El
  trabajo iniciado se produce al pasar a `OPERARIO_TRABAJANDO` (RF-FLU-06). `[SUPUESTO]` (duda DA-1).
- **Glosario §4.7** (fases): el catálogo de fases se conserva (§4 de esta spec), pero se supera en
  lo que cierra el componente con `finalizado_por_cliente` o `finalizado_por_tecnico` como etapa
  final: el cierre del componente es `LISTO_PARA_ENTREGA` o `RECHAZADO` (RF-FLU-07, RF-FLU-08).
- **Glosario §4.8** en cuanto a la definición de "componente finalizado". El principio de criterio
  único (el servicio sigue abierto mientras quede un componente sin cerrar) se **mantiene**.
- **Glosario §4.9** en cuanto a las condiciones de habilitación: sustituidas por RF-FLU-09.
- **RF-COT-04**: la regla de que una cotización bloqueante pendiente impide "continuar" queda
  sustituida por el modelo de estados: la detención del componente es su estado
  `ESPERANDO_APROBACION` (RF-FLU-05). Se mantiene el principio de que el backend valida toda
  operación (RNF-FLU-01).
- **RF-COT-05**: el estado resultante del rechazo bloqueante deja de ser `rechazado_bloqueante` y
  ya no cambia el estado del componente: la cotización queda `RECHAZADA` y el componente permanece
  en `ESPERANDO_APROBACION` (RF-FLU-06). Se mantienen "no puede continuar su trabajo" y "no afecta
  a los demás componentes".
- **RF-COT-08**: el registro de inicio de trabajo ya no lo ejecuta el técnico; lo produce el paso
  a `OPERARIO_TRABAJANDO` (RF-FLU-06). `[SUPUESTO]` la fase y la marca de trabajo iniciado se
  siguen registrando (duda DA-1).
- **RF-COT-09**: la finalización de componentes con `FINALIZADO_POR_CLIENTE` o
  `FINALIZADO_POR_TECNICO` deja de existir como estado. El cierre de un componente `RECHAZADO`
  se rige por RF-FLU-08.
- **RF-COT-10**: los destinos de la corrección de una finalización se sustituyen. Ver RF-FLU-07 y
  RF-FLU-11.
- **RF-COT-11**: se sustituye el caso 2 (todas las bloqueantes rechazadas y sin trabajo iniciado)
  y el criterio de habilitación. La habilitación es RF-FLU-09.
- **RF-COT-12 y RF-COT-13**: se mantienen. Una cotización pendiente no fuerza el cierre, y el
  rechazo de un componente no afecta a los demás.
- **RF-COT-15**: se mantiene la regla de no exponer campos de control interno, pero los valores de
  `estado` y `fase` que ve el cliente son los de esta spec.
- **§2 y §5, donde atribuyen a "técnico" la ejecución de acciones de estado**: a partir de esta
  spec esas acciones las ejecuta el ADMINISTRATIVO, que es el único rol (decisión cerrada).
- **Decisiones D-3, D-7, D-8 y D-12**, en lo que dependan de los estados eliminados o de sus
  motivos. D-3 (estados propios del componente) y D-7 (bloqueante rechazada como no activo)
  quedan sustituidas por §4 y RF-FLU-02. D-8 (corrección de cierres por error humano) se conserva
  como principio y se concreta en RF-FLU-07; el cierre de un componente `RECHAZADO` se rige por
  RF-FLU-08. D-12 (motivo y fecha de cierre en el componente) se conserva como principio y es
  obligatorio también en `LISTO_PARA_ENTREGA` (RF-FLU-07).
- **CL-02, CL-03, CL-05, CL-07, CL-11 y CL-12**, en lo que usan los estados eliminados o el criterio
  de cierre anterior.
- **§8, criterios 1, 2, 3, 7 y 8**, en lo que nombran estados eliminados.

**Se mantienen** D-1, D-2, D-4, D-5, D-6, D-9, D-10, D-11, D-13 y D-14, y los puntos de
trazabilidad de cotizaciones y aprobaciones.

### 2.3 Especificación 001 — Solicitud en banco de pruebas

**Superada:**

- **RF-8.6 y §8, criterio 5**: los estados cerrados de una solicitud pasan a ser **`FINALIZADO` y
  `CANCELADO`**. `ENTREGADO` deja de ser un estado de servicio (§5, RF-FLU-01), por lo que la
  enumeración "finalizada, entregada ni cancelada" del criterio 5 se lee como `FINALIZADO` o
  `CANCELADO`. Se mantiene que rechazar la cotización de un componente no cierra el servicio.
- **Caso límite de §6** que menciona una solicitud "entregada" como cerrada: se lee como
  `FINALIZADO` o `CANCELADO`.

### 2.4 Especificación 005 — Panel administrativo

**Superadas:**

- **RF-ADM-05 y RF-ADM-06 y §4, definición de "pendientes de atención"**: la lista de estados
  pendientes y los indicadores por estado se reemplazan por los de esta spec. El criterio de
  "componente detenido por cotización" se mantiene con estado `ESPERANDO_APROBACION` (cotización
  pendiente o rechazada a la espera del administrador); `RECHAZADO` es ya una finalización del
  administrador y no un estado detenido.
- **RF-ADM-15 y CL-ADM-03**, en lo que nombran estados eliminados o la etiqueta "En espera por
  cotización rechazada" (interna y públicamente `RECHAZADO_BLOQUEANTE`).
- **RF-ADM-18**: iniciar trabajo deja de ser una acción manual que lleva a `EN_PROCESO`. El paso a
  `OPERARIO_TRABAJANDO` es automático al aprobar el cliente (RF-FLU-06).
- **RF-ADM-19**: los motivos oficiales `FINALIZADO_POR_CLIENTE` y `FINALIZADO_POR_TECNICO` dejan
  de existir. El cierre de componentes `RECHAZADO` se rige por RF-FLU-08.
- **RF-ADM-20**: la condición de cierre del servicio es la de RF-FLU-09.
- **RF-ADM-21**: las acciones disponibles en el panel son las de §5 de esta spec. Se mantiene que
  el panel no ofrece un selector libre.
- **CL-ADM-12**, en lo que describe la acción de finalizar servicio con el criterio anterior.

### 2.5 Especificación 007 — Vista de seguimiento

**Superadas:**

- **§2 (Relación con especificaciones anteriores)** en lo que da por buenos los catálogos de
  estado y los estados de cierre anteriores (incluido `ENTREGADO` como cierre), y
  **§5 (Definiciones)**: los catálogos de estado del servicio y del componente se sustituyen por
  los de §4 de esta spec. La definición de fase de §5 se conserva.
- **S-3** (pasos de la línea de tiempo) y los pasos de la línea de tiempo que propone la spec. La
  línea de tiempo pública se construye con cuatro pasos: **Recibido, Revisión y cotización,
  Pruebas y Finalizado** (§5, RF-FLU-15). `[PROPUESTA]` (duda DA-15).
- **RF-SEG-07** (aviso diferenciado para `NO_APROBADO`), **RF-SEG-08** (servicio `ENTREGADO` y
  pasos futuros), **CL-11** y **CL-12**, en lo que nombran `NO_APROBADO` o `ENTREGADO`.
- **S-7** (etiqueta "Rechazado (bloqueante)" del componente): el estado es `RECHAZADO`.

## 3. Usuarios

- **ADMINISTRATIVO:** único rol. Opera el flujo, registra cotizaciones y avances, ejecuta el
  cierre y la cancelación. Sustituye a "técnico" en todas las especificaciones anteriores
  (decisión cerrada).
- **Cliente final:** no usa el panel. Responde cotizaciones desde el seguimiento con su token o por
  WhatsApp (registrado por el administrativo). Esa respuesta a su cotización es la única acción suya
  que el backend autoriza (RF-FLU-14) y los estados derivados cambian de forma automática
  (RF-FLU-06). No cambia ningún otro estado de forma directa.
- **Visitante sin datos:** no obtiene información de ningún servicio.

## 4. Glosario

- **Estado del servicio:** condición de negocio de la solicitud completa. Catálogo cerrado:
  `SOLICITADO`, `EN_CURSO`, `FINALIZADO`, `CANCELADO`.
- **Estado del componente:** condición de una pieza dentro de un servicio. Catálogo cerrado:
  `PENDIENTE`, `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `OPERARIO_TRABAJANDO`,
  `EN_PRUEBAS`, `LISTO_PARA_ENTREGA`, `RECHAZADO`.
- **Fase del componente:** etapa del trabajo físico (`RECIBIDO`, `DESMONTAJE_INICIADO`,
  `EN_EJECUCION`), según 002 §4.7. Una fase no reemplaza al estado. `[SUPUESTO]` el catálogo de
  fases no cambia (duda DA-14).
- **Servicio en curso:** servicio en `SOLICITADO` o `EN_CURSO`.
- **Servicio cerrado:** servicio en `FINALIZADO` o `CANCELADO`. Es el criterio de estados cerrados
  de 001 (RF-8.6) y no admite cambios de estado.
- **Componente detenido por cotización:** componente en `ESPERANDO_APROBACION`, con la cotización
  pendiente o rechazada a la espera de la decisión del administrador (reenviar o finalizar).
- **Componente listo para cierre:** componente en `LISTO_PARA_ENTREGA` o `RECHAZADO`, ambos ya
  finalizados con motivo y fecha. Es el criterio que habilita el cierre del servicio (RF-FLU-09).
- **Cotización:** presupuesto asociado a un componente, con tipo bloqueante o no bloqueante. Sus
  estados (`PENDIENTE`, `APROBADA`, `RECHAZADA`) no cambian en esta spec.
- **Transición automática:** cambio de estado que produce un hecho registrado, sin una acción
  manual adicional.
- **Transición manual:** cambio de estado que decide el administrativo mediante una acción
  explícita.
- **Operación idempotente:** operación que, pedida con el estado que el recurso ya tiene, no
  produce cambio ni registro en el historial.

### 4.1 Tabla de transiciones del componente

| Desde | Hacia | Tipo | Disparador |
|---|---|---|---|
| `PENDIENTE` | `EN_REVISION` | Manual (administrativo) | Llega el repuesto del componente. |
| `EN_REVISION` | `COTIZANDO` | Manual (administrativo) | El administrativo prepara la cotización. |
| `COTIZANDO` | `ESPERANDO_APROBACION` | Automática | Se registra una cotización del componente. |
| `ESPERANDO_APROBACION` | `OPERARIO_TRABAJANDO` | Automática | El cliente aprueba la cotización. |
| `ESPERANDO_APROBACION` | `RECHAZADO` | Manual (administrativo) | El administrativo finaliza el componente tras el rechazo de la cotización (motivo y fecha, RF-FLU-08). El rechazo del cliente no cambia el estado. |
| `OPERARIO_TRABAJANDO` | `EN_PRUEBAS` | Manual (administrativo) `[PROPUESTA]` | El trabajo termina y pasa a pruebas. |
| `OPERARIO_TRABAJANDO` | `ESPERANDO_APROBACION` | Automática | Se registra una cotización adicional para el componente; el trabajo queda detenido a la espera de la respuesta del cliente (RF-FLU-05). |
| `EN_PRUEBAS` | `ESPERANDO_APROBACION` | Automática | Se registra una cotización del componente; las pruebas quedan detenidas a la espera de la respuesta del cliente (RF-FLU-05). |
| `EN_PRUEBAS` | `LISTO_PARA_ENTREGA` | Manual (administrativo) | Las pruebas se aprueban; finalización con motivo y fecha (RF-FLU-07). |
| `LISTO_PARA_ENTREGA` | `ESPERANDO_APROBACION` | Automática | Se registra una cotización del componente; conserva su fase y su progreso ("se queda en pruebas": no reinicia el trabajo) y, al aprobar esa cotización, el componente vuelve a `EN_PRUEBAS`, no a `OPERARIO_TRABAJANDO` (RF-FLU-05, RF-FLU-06; duda DA-18 cerrada). |
| `LISTO_PARA_ENTREGA` | `EN_PRUEBAS` | Manual (administrativo) | Corrección por error humano con comentario obligatorio (RF-FLU-07). |
| `RECHAZADO` | `ESPERANDO_APROBACION` | Manual (administrativo) | Corrección por error humano del cierre, con comentario obligatorio (RF-FLU-07). |

Cualquier otra transición entre estados de componente queda **no permitida**. En particular, un
rechazo de cotización no mueve el componente, no existe transición de `RECHAZADO` a un estado de
trabajo (salvo la corrección por error humano de RF-FLU-07, que lo devuelve a
`ESPERANDO_APROBACION`) y no hay transición de vuelta a `PENDIENTE`. La única excepción en el
destino de una aprobación es la del componente detenido desde `LISTO_PARA_ENTREGA`: al aprobar su
cotización vuelve a `EN_PRUEBAS`, no a `OPERARIO_TRABAJANDO` (RF-FLU-06, duda DA-18).

### 4.2 Tabla de transiciones del servicio

| Desde | Hacia | Tipo | Disparador |
|---|---|---|---|
| `SOLICITADO` | `EN_CURSO` | Automática | El primer componente sale de `PENDIENTE`. |
| `EN_CURSO` | `FINALIZADO` | Manual (administrativo) | Todos los componentes finalizados con motivo y fecha: `LISTO_PARA_ENTREGA` o `RECHAZADO`. |
| `SOLICITADO` o `EN_CURSO` | `CANCELADO` | Manual (administrativo) | Comentario obligatorio; no cambia el campo de activo ni los componentes. |

### 4.3 Mapeo componente → paso público

Los estados del componente se agrupan en los cuatro pasos de la línea de tiempo pública
(**Recibido, Revisión y cotización, Pruebas, Finalizado**):

| Estado del componente | Paso público |
|---|---|
| `PENDIENTE` | Recibido |
| `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `OPERARIO_TRABAJANDO` | Revisión y cotización |
| `EN_PRUEBAS` | Pruebas |
| `LISTO_PARA_ENTREGA`, `RECHAZADO` (finalizado) | Finalizado |

### 4.4 Etiquetas en español

**Componente:**

| Estado del componente | Etiqueta |
|---|---|
| `PENDIENTE` | Pendiente |
| `EN_REVISION` | En revisión |
| `COTIZANDO` | Cotizando |
| `ESPERANDO_APROBACION` | Esperando aprobación |
| `OPERARIO_TRABAJANDO` | Operario trabajando |
| `EN_PRUEBAS` | En pruebas |
| `LISTO_PARA_ENTREGA` | Listo para entregar |
| `RECHAZADO` | Rechazado |

**Servicio:**

| Estado del servicio | Etiqueta |
|---|---|
| `SOLICITADO` | Solicitado |
| `EN_CURSO` | En curso |
| `FINALIZADO` | Finalizado |
| `CANCELADO` | Cancelado |

## 5. Requisitos funcionales (EARS)

### Catálogos

#### RF-FLU-01 — Estados del servicio

**WHEN** se consulta o se registra un servicio **THEN** el sistema DEBE clasificarlo en uno de
cuatro estados: `SOLICITADO` (Solicitado), `EN_CURSO` (En curso), `FINALIZADO` (Finalizado) o
`CANCELADO` (Cancelado).

**AND** los estados `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `EN_REPARACION`,
`EN_PRUEBAS`, `LISTO_PARA_ENTREGA`, `ENTREGADO` y `NO_APROBADO` DEJAN de ser estados del servicio.
El avance detallado se lee en los estados de los componentes (RF-FLU-02).

#### RF-FLU-02 — Estados del componente

**WHEN** se consulta un componente **THEN** el sistema DEBE clasificarlo en uno de ocho estados:
`PENDIENTE`, `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `OPERARIO_TRABAJANDO`,
`EN_PRUEBAS`, `LISTO_PARA_ENTREGA` o `RECHAZADO`.

**AND** los estados `APROBADO`, `RECHAZADO_BLOQUEANTE`, `EN_PROCESO`, `FINALIZADO_POR_CLIENTE` y
`FINALIZADO_POR_TECNICO` DEJAN de existir.

**AND** `RECHAZADO` es un estado final que solo alcanza el administrativo mediante una
finalización manual con motivo (texto libre) y fecha (RF-FLU-08). El rechazo de la cotización por
el cliente NO lleva el componente a `RECHAZADO`: lo deja en `ESPERANDO_APROBACION` (RF-FLU-06).
`RECHAZADO` no es una fase ni un estado de trabajo.

### Transiciones automáticas

#### RF-FLU-03 — Inicio automático del servicio

**WHEN** el primer componente de un servicio `SOLICITADO` sale de `PENDIENTE` **THEN** el
servicio DEBE pasar a `EN_CURSO` de forma automática, sin acción del administrativo.

**AND** un servicio que ya está `EN_CURSO`, `FINALIZADO` o `CANCELADO` NO DEBE cambiar por este
motivo.

**AND** ninguna acción vuelve un servicio de `EN_CURSO` a `SOLICITADO`.

#### RF-FLU-04 — Avance manual de revisión y cotización

**WHEN** el administrativo registra que llegó el repuesto de un componente `PENDIENTE` **THEN**
el componente DEBE pasar a `EN_REVISION`.

**WHEN** el administrativo registra que un componente `EN_REVISION` está siendo cotizado
**THEN** el componente DEBE pasar a `COTIZANDO`.

**AND** toda transición manual que no aparezca en la tabla de §4.1 DEBE rechazarse sin cambios.

#### RF-FLU-05 — Cotización lleva a esperar aprobación

**WHEN** se registra una cotización para un componente en `COTIZANDO` **THEN** el componente DEBE
pasar a `ESPERANDO_APROBACION` de forma automática.

**AND** **WHEN** se registra una cotización para un componente en `OPERARIO_TRABAJANDO` **THEN**
el componente DEBE volver a `ESPERANDO_APROBACION` de forma automática: el trabajo queda detenido
a la espera de la respuesta del cliente a la nueva cotización.

**AND** **WHEN** se registra una cotización para un componente en `EN_PRUEBAS` **THEN** el
componente DEBE volver a `ESPERANDO_APROBACION` de forma automática: las pruebas quedan detenidas
a la espera de la respuesta del cliente a la nueva cotización (decisión cerrada, duda DA-17).

**AND** **WHEN** se registra una cotización para un componente en `LISTO_PARA_ENTREGA` **THEN**
el componente DEBE pasar a `ESPERANDO_APROBACION` de forma automática, conservando su fase y su
progreso: "se queda en pruebas" y NO DEBE reiniciar el trabajo (decisión cerrada, duda DA-18).
Al aprobar esa cotización el componente vuelve a `EN_PRUEBAS`, no a `OPERARIO_TRABAJANDO`
(RF-FLU-06).

**AND** registrar una cotización adicional mientras el componente ya está en
`ESPERANDO_APROBACION` NO DEBE cambiar su estado. `[SUPUESTO]`

**AND** esta regla cubre `COTIZANDO`, `OPERARIO_TRABAJANDO`, `EN_PRUEBAS` y `LISTO_PARA_ENTREGA`
(duda DA-18 cerrada): registrar una cotización en cualquier otro estado NO DEBE cambiar el estado
del componente. `[SUPUESTO]`

#### RF-FLU-06 — Respuesta del cliente

**WHEN** el cliente aprueba la cotización de un componente en `ESPERANDO_APROBACION` **THEN** el
componente DEBE pasar a `OPERARIO_TRABAJANDO` de forma automática, sin ninguna acción adicional
del administrativo.

**AND** **WHEN** ese componente llegó a `ESPERANDO_APROBACION` desde `LISTO_PARA_ENTREGA`
(RF-FLU-05) **THEN** la aprobación DEBE devolverlo a `EN_PRUEBAS`, no a `OPERARIO_TRABAJANDO`
(decisión cerrada, duda DA-18): conserva su fase y su progreso porque el trabajo no se reinició.

**WHEN** el cliente rechaza la cotización de un componente **THEN** la cotización DEBE quedar
`RECHAZADA` y el componente DEBE permanecer en `ESPERANDO_APROBACION`: el rechazo NO DEBE cambiar
el estado del componente.

**AND** después del rechazo decide el administrativo: reenviar la cotización o finalizar el
componente como `RECHAZADO` (RF-FLU-08).

**AND** el rechazo NO DEBE cambiar el estado de los demás componentes del servicio, ni el estado
del servicio (RF-COT-13).

**AND** el canal de la respuesta, quién la registró y la fecha se conservan (RF-COT-03).

**AND** la respuesta del cliente llega solo por la vía de respuesta registrada (seguimiento web con
token o WhatsApp registrado por el administrativo) y es la única acción del cliente que el backend
autoriza (RF-FLU-14). Para todo lo demás el cliente no cambia estados de forma directa.

**AND** la primera aprobación de la cotización pendiente es la que lleva el componente a
`OPERARIO_TRABAJANDO` (o a `EN_PRUEBAS` si la espera vino de `LISTO_PARA_ENTREGA`, RF-FLU-05 y
duda DA-18); si después se registra una cotización adicional, el componente vuelve a
`ESPERANDO_APROBACION` (RF-FLU-05). La vista de aprobación pública usa la cotización pendiente
más reciente del componente, como hasta ahora (dudas DA-3 y DA-4 cerradas).

### Transiciones manuales de trabajo

#### RF-FLU-07 — Trabajo, pruebas y entrega del componente

**WHEN** el administrativo registra que un componente en `OPERARIO_TRABAJANDO` pasa a pruebas
**THEN** el componente DEBE pasar a `EN_PRUEBAS`. `[PROPUESTA]`

**WHEN** el administrativo registra que un componente en `EN_PRUEBAS` tiene las pruebas aprobadas
**THEN** el componente DEBE pasar a `LISTO_PARA_ENTREGA` y la finalización DEBE registrar el motivo
escrito por el administrativo (texto libre) y la fecha.

**AND** `LISTO_PARA_ENTREGA` es el último estado del recorrido normal del componente y no tiene
transición a otro estado del recorrido, salvo la corrección por error humano indicada más abajo.

**AND** un componente devuelto a `EN_PRUEBAS` por la aprobación de una cotización registrada en
`LISTO_PARA_ENTREGA` (RF-FLU-06, duda DA-18) se rige por esta misma regla: conserva su fase y su
progreso, y el administrativo puede finalizarlo a `LISTO_PARA_ENTREGA` cuando las pruebas se
apruben, con motivo y fecha.

**WHEN** el administrativo corrige por error humano un componente finalizado en
`LISTO_PARA_ENTREGA` o en `RECHAZADO`, de un servicio no cerrado **THEN** el sistema DEBE
permitirlo, devolviendo el componente al estado que tenía antes de la finalización, DEBE exigir un
comentario obligatorio y DEBE registrarlo en `HistorialComponente`.

**AND** esta corrección DEBE estar reservada al administrativo y el sistema NUNCA DEBE aplicarla
por sí solo.

**AND** `[SUPUESTO]` el paso a `OPERARIO_TRABAJANDO` deja marcado el trabajo iniciado y la fase
`DESMONTAJE_INICIADO` con su fecha, sin borrar evidencias previas (duda DA-1).

#### RF-FLU-08 — Finalización de componente rechazado

**WHEN** el administrativo finaliza un componente en `ESPERANDO_APROBACION` cuya cotización está
`RECHAZADA` **THEN** el componente DEBE pasar a `RECHAZADO` de forma manual, registrando el motivo
escrito por el administrativo (texto libre) y la fecha de finalización.

**AND** el rechazo de la cotización por el cliente NO DEBE producir este cambio por sí solo
(RF-FLU-06): `RECHAZADO` solo se alcanza con esta finalización manual del administrativo.

**AND** el sistema NUNCA DEBE llevar un componente a `RECHAZADO` por sí solo.

**AND** la finalización NO DEBE cambiar el estado del componente después; la única corrección
posible es la de RF-FLU-07.

### Cierre y cancelación del servicio

#### RF-FLU-09 — Finalización manual del servicio

**WHEN** el administrativo solicita finalizar un servicio **THEN** el sistema DEBE permitirlo
únicamente si el servicio tiene al menos un componente y todos sus componentes están en
`LISTO_PARA_ENTREGA` o `RECHAZADO`, ambos alcanzados por una finalización que ya registró motivo
y fecha (RF-FLU-07 y RF-FLU-08).

**AND** el sistema NUNCA DEBE finalizar un servicio por sí solo.

**AND** la finalización DEBE registrar la fecha de finalización, el administrativo y el comentario
en el historial del servicio.

**IF** no se cumple la condición **THEN** el sistema DEBE rechazar la finalización sin modificar
datos e indicar qué componentes impiden el cierre, o que el servicio no tiene componentes.

#### RF-FLU-10 — Cancelación administrativa

**WHEN** el administrativo solicita cancelar un servicio que no está `FINALIZADO` ni `CANCELADO`
**THEN** el sistema DEBE cancelarlo, solo con comentario obligatorio.

**AND** la cancelación NO DEBE modificar el campo de activo, los estados de los componentes, sus
cotizaciones, aprobaciones, historial ni fechas existentes.

**AND** la cancelación NO DEBE exigir que los componentes estén cerrados, ni marcarlos como
cerrados.

**AND** la cancelación DEBE registrarse en el historial del servicio con usuario, fecha, estado
alcanzado y comentario.

#### RF-FLU-11 — Estados cerrados

**WHEN** un servicio está en `FINALIZADO` o `CANCELADO` **THEN** ninguna acción DEBE cambiar su
estado ni el de sus componentes.

**AND** esta spec no crea ninguna reapertura de un servicio cerrado.

**AND** esta regla aplica también a un componente de un servicio cerrado: no admite cambio de
estado.

### Trazabilidad, validación y concurrencia

#### RF-FLU-12 — Trazabilidad de cada cambio

**WHEN** cambia el estado de un componente, sea automático o manual **THEN** el sistema DEBE
registrarlo en `HistorialComponente` con estado anterior, estado nuevo, usuario (si lo hay), fecha
y comentario cuando aplique.

**AND** **WHEN** cambia el estado del servicio, sea automático o manual, **THEN** el sistema DEBE
registrarlo en `HistorialServicio` con estado alcanzado, usuario (si lo hay), fecha y comentario.

**AND** `[SUPUESTO]` un cambio automático provocado por el cliente se registra sin usuario
administrativo (duda DA-16).

**AND** ningún registro de historial puede eliminarse desde esta funcionalidad.

#### RF-FLU-13 — Validación, idempotencia y concurrencia en el backend

**WHEN** se solicita un cambio de estado **THEN** el backend DEBE validar la transición contra las
tablas de esta spec, sin confiar en lo que muestra la interfaz.

**WHEN** se solicita el mismo estado que el recurso ya tiene **THEN** la operación DEBE aceptarse
sin efecto y sin registro en el historial.

**WHEN** dos operaciones afectan al mismo servicio o al mismo componente **THEN** cada una DEBE
ejecutarse en una transacción que bloquee el servicio y la entidad afectada, consulte de nuevo el
estado persistido y decida con ese estado.

**IF** el estado persistido ya no permite la operación **THEN** el backend DEBE responder con
`409 Conflict`, sin sobrescribir la operación confirmada y sin cambios parciales.

**AND** una transición automática (RF-FLU-03, RF-FLU-05, RF-FLU-06) DEBE aplicarse en la misma
transacción que el hecho que la produce.

#### RF-FLU-14 — Permisos

**WHEN** se solicita un cambio de estado de servicio o de componente **THEN** el backend DEBE
exigir un ADMINISTRATIVO autenticado y activo.

**AND** `WHEN` el cliente responde una cotización (aprobación o rechazo) desde el seguimiento
público con el token de acceso de ese servicio **THEN** el backend DEBE autorizarla como única
excepción a la regla anterior, limitada a esa respuesta de cotización; los estados derivados de la
respuesta cambian de forma automática (RF-FLU-06).

**IF** la petición proviene de un cliente sin token válido, de un usuario no autenticado o de una
cuenta inactiva, o pide cualquier cambio distinto de la respuesta a su cotización **THEN** el
backend DEBE rechazarla sin modificar datos.

### Presentación pública

#### RF-FLU-15 — Estados en el seguimiento público

**WHEN** el seguimiento público muestra un servicio **THEN** DEBE usar únicamente los estados de
esta spec, con etiquetas en español, y NO DEBE mostrar estados eliminados.

**AND** la línea de tiempo pública usa cuatro pasos: **Recibido, Revisión y cotización, Pruebas y
Finalizado**. `[PROPUESTA]` (duda DA-15).

**AND** un servicio `CANCELADO` NO DEBE ser consultable por su enlace de seguimiento público.

**AND** la regla de no exponer campos de control interno de RF-COT-15 se mantiene.

### Migración de datos

#### RF-FLU-16 — Cambio de catálogo y migración de datos

**WHEN** se implemente este flujo **THEN** el cambio de catálogo requiere dos entregables
explícitos: (1) la **migración de esquema**, que actualiza las opciones (`choices`) de los campos
de estado a los catálogos de §4, y (2) la **migración de datos**, con la tabla de mapeo propuesta
más abajo. Esta spec DEBE crear ambas migraciones y ejecutarlas contra la base de datos de
desarrollo, con advertencia previa de respaldo antes de ejecutar.

**AND** la ejecución sobre una base de datos que no sea de prueba DEBE quedar sujeta a la
confirmación de las dudas de pérdida de información (DA-11): hasta esa confirmación NO DEBE
ejecutarse la migración de datos sobre esa base.

**AND** la migración de datos DEBE aplicar la tabla de mapeo propuesta a continuación, con las
marcas indicadas.

**AND** los servicios migrados de `NO_APROBADO` a `CANCELADO` DEBEN quedar con el comentario de
cierre vacío: la cancelación real exige comentario (RF-FLU-10) pero la migración NO DEBE
inventarlo. Cualquier comentario añadido durante la migración DEBE quedar documentado como
excepción.

**Tabla de mapeo propuesta — servicio**

| Estado actual | Estado nuevo | Fecha que se conserva | Nota |
|---|---|---|---|
| `SOLICITADO` | `SOLICITADO` | — | |
| `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `EN_REPARACION`, `EN_PRUEBAS` | `EN_CURSO` | — | |
| `LISTO_PARA_ENTREGA` | `EN_CURSO` `[PROPUESTA]` | — | El cierre es manual (duda DA-8). |
| `ENTREGADO` | `FINALIZADO` `[PROPUESTA]` | `fecha_entrega` se conserva | No se inventa `fecha_finalizacion` (duda DA-8). |
| `FINALIZADO` | `FINALIZADO` | `fecha_finalizacion` | |
| `NO_APROBADO` | `CANCELADO` `[PROPUESTA]` | — | Deja de ser consultable por el enlace (duda DA-7). |
| `CANCELADO` | `CANCELADO` | — | |

**Tabla de mapeo propuesta — componente**

| Estado actual | Estado nuevo | Nota |
|---|---|---|
| `PENDIENTE` | `PENDIENTE` | |
| `APROBADO` | `OPERARIO_TRABAJANDO` `[SUPUESTO]` | Cliente ya aprobó (duda DA-10). |
| `EN_PROCESO` | `OPERARIO_TRABAJANDO` `[SUPUESTO]` | |
| `RECHAZADO` | `RECHAZADO` | |
| `RECHAZADO_BLOQUEANTE` | `RECHAZADO` `[SUPUESTO]` | |
| `FINALIZADO_POR_CLIENTE`, `FINALIZADO_POR_TECNICO` | `LISTO_PARA_ENTREGA` `[PROPUESTA]` | `motivo_finalizacion` y `fecha_finalizacion` se conservan como historial (duda DA-9). |

**AND** según la petición, los datos actuales son de prueba. Esta condición debe confirmarse antes
de ejecutar el mapeo con pérdida de información (duda DA-11).

### Fuentes de contexto del negocio

#### RF-FLU-17 — Actualización de las fuentes de negocio como condición de aprobación

**WHEN** esta spec quede aprobada para su implementación **THEN** el proceso de aprobación DEBE
exigir, antes de escribir código, la actualización de las fuentes de contexto del negocio.

**AND** `CONTEXTO_MAESTRO.md` §14 (catálogos de estado) DEBE actualizarse para reflejar los
catálogos de servicio y de componente de §4 de esta spec.

**AND** `CONTEXTO_MAESTRO.md` §30 (ejemplo de pasos) DEBE actualizarse para reflejar los pasos del
nuevo flujo y la línea de tiempo pública (RF-FLU-15).

**AND** el cambio de modelo de estados DEBE anotarse en `MEMORY.md`.

**IF** alguna de las tres actualizaciones no está hecha **THEN** la spec NO DEBE considerarse lista
para implementación.

## 6. Requisitos no funcionales (EARS)

#### RNF-FLU-01 — Autoridad del backend

Las transiciones, la validación de permisos, el cálculo de las opciones válidas y la decisión de
cierre DEBEN resolverse en el backend. La interfaz muestra opciones y resultados; no decide
transiciones.

#### RNF-FLU-02 — Integridad y concurrencia

Toda transición DEBE ser atómica. Las transiciones automáticas y manuales DEBEN bloquear el
servicio y la entidad afectada antes de evaluar la regla. Un conflicto DEBE devolver `409 Conflict`
sin pérdida ni sobrescritura silenciosa. Esta protección NO DEBE requerir Redis, WebSockets, una
dependencia nueva ni un campo de versión nuevo.

#### RNF-FLU-03 — Trazabilidad

Cada cambio de estado DEBE dejar rastro en el historial que corresponda (RF-FLU-12). El rastro
DEBE permitir reconstruir la secuencia de estados de un servicio y de sus componentes.

#### RNF-FLU-04 — Idioma y etiquetas

Las etiquetas visibles de estado DEBEN estar en español y ser comprensibles para un cliente que no
domina el vocabulario técnico. Los códigos internos pueden conservarse en el backend.

#### RNF-FLU-05 — Accesibilidad y feedback

Los estados DEBEN comunicarse con texto, no solo con color, en el panel y en el seguimiento. Las
acciones de cambio DEBEN confirmar su resultado, mostrar el motivo cuando una regla las rechaza y
ofrecer recarga ante `409`.

#### RNF-FLU-06 — Sin dependencias ni arquitectura nueva

La implementación DEBE operar con la arquitectura, las dependencias y la sesión aprobadas. La
verificación del backend DEBE hacerse con `django.test` mediante `manage.py test`, sin
dependencias nuevas. La verificación del frontend DEBE hacerse con Chrome DevTools MCP.

#### RNF-FLU-07 — Responsive

El panel administrativo y el seguimiento público DEBEN funcionar correctamente en móvil, tablet y
escritorio, con diseño responsive desde el inicio. NO DEBE diseñarse únicamente para escritorio
y adaptarse después.

## 7. Casos límite

- **CL-01 — Primer componente sale de pendiente:** el componente pasa a `EN_REVISION` y el servicio
  pasa de `SOLICITADO` a `EN_CURSO` en la misma operación.
- **CL-02 — Segundo componente sale de pendiente:** el servicio ya está `EN_CURSO`; no cambia.
- **CL-03 — Transición no listada:** se pide pasar de `PENDIENTE` a `COTIZANDO`, o de `COTIZANDO` a
  `EN_REVISION`; el backend rechaza sin modificar datos.
- **CL-04 — Cotización adicional durante el trabajo:** se registra una cotización para un componente
  en `OPERARIO_TRABAJANDO`; el componente vuelve automáticamente a `ESPERANDO_APROBACION` y la vista
  de aprobación pública muestra la cotización pendiente más reciente (RF-FLU-05; dudas DA-3 y DA-4
  cerradas).
- **CL-05 — Cliente aprueba:** con el token del seguimiento, el componente pasa automáticamente a
  `OPERARIO_TRABAJANDO`; el servicio y los demás componentes no cambian.
- **CL-06 — Cliente rechaza:** la cotización queda `RECHAZADA` y el componente permanece en
  `ESPERANDO_APROBACION`; los demás componentes y el servicio no cambian. Después el administrador
  decide reenviar la cotización o finalizar el componente como `RECHAZADO` (CL-09).
- **CL-07 — Respuesta repetida:** se intenta responder una cotización que ya tiene respuesta
  (por ejemplo, por dos canales); el backend responde `409` y no sobrescribe la respuesta
  confirmada.
- **CL-08 — Componente rechazado no avanza:** se intenta llevar un `RECHAZADO` a `OPERARIO_TRABAJANDO`
  o a `EN_PRUEBAS`; el backend rechaza el cambio. Solo sale de `RECHAZADO` por la corrección por
  error humano de RF-FLU-07.
- **CL-09 — Finalización como rechazado:** el administrativo finaliza un componente en
  `ESPERANDO_APROBACION` con la cotización rechazada; se registran motivo (texto libre) y fecha, el
  componente queda en `RECHAZADO` y la finalización consta en `HistorialComponente`.
- **CL-10 — Finalizar con componentes en curso:** se pide finalizar el servicio con un componente en
  `EN_PRUEBAS`; el backend rechaza e indica qué componente impide el cierre.
- **CL-11 — Finalizar sin componentes:** se pide finalizar un servicio sin componentes; el backend
  rechaza.
- **CL-12 — Finalizar con todos listos o rechazados:** todos los componentes están en
  `LISTO_PARA_ENTREGA` o `RECHAZADO`, ambos finalizados con motivo y fecha; el servicio pasa a
  `FINALIZADO`, con fecha y registro en el historial; los componentes no cambian.
- **CL-13 — Cancelar sin comentario:** el backend rechaza la cancelación sin modificar datos.
- **CL-14 — Cancelar con componentes en curso:** el servicio pasa a `CANCELADO`, con comentario; los
  componentes conservan su estado, el campo de activo no cambia y el enlace público deja de ser
  consultable.
- **CL-15 — Cambio sobre servicio cerrado:** se intenta cambiar el estado de un servicio
  `FINALIZADO` o `CANCELADO`, o de un componente de uno de ellos; el backend rechaza.
- **CL-16 — Mismo estado:** se pide el estado que el recurso ya tiene; la operación se acepta sin
  efecto y sin historial.
- **CL-17 — Concurrencia en el cierre:** un administrativo finaliza el servicio mientras otro pasa
  un componente a `EN_PRUEBAS`; la operación que pierde la validación recibe `409` y el servicio no
  queda parcialmente actualizado.
- **CL-18 — Servicio migrado como `NO_APROBADO`:** tras el mapeo queda `CANCELADO`, su enlace de
  seguimiento deja de estar disponible (duda DA-7) y su comentario de cierre queda vacío salvo
  excepción documentada (RF-FLU-16).
- **CL-19 — Componente migrado como finalizado:** tras el mapeo queda `LISTO_PARA_ENTREGA`, y sus
  datos de cierre anteriores se conservan como historial (duda DA-9).
- **CL-20 — Servicio migrado como `ENTREGADO`:** tras el mapeo queda `FINALIZADO`, sin inventar una
  fecha de finalización, y conserva su fecha de entrega (duda DA-8).
- **CL-21 — Cliente sin acceso directo:** el cliente intenta cambiar un estado distinto de la
  respuesta a su cotización, o responde sin token válido; el backend lo rechaza sin modificar datos.
  La respuesta a la cotización con token es la única excepción (RF-FLU-14).
- **CL-22 — Corrección por error humano:** el administrativo corrige un componente en
  `LISTO_PARA_ENTREGA` o un cierre `RECHAZADO` sin comentario; el backend rechaza. Con comentario
  obligatorio, el componente vuelve al estado anterior a la finalización y el cambio queda registrado
  en `HistorialComponente`.

## 8. Criterios de aceptación

1. El servicio solo puede estar en `SOLICITADO`, `EN_CURSO`, `FINALIZADO` o `CANCELADO`, y el
   componente solo en los ocho estados de RF-FLU-02.
2. El primer componente que sale de pendiente lleva el servicio a `EN_CURSO` automáticamente, y
   ninguna acción lo devuelve a `SOLICITADO`.
3. Las transiciones del componente siguen la tabla de §4.1: las manuales requieren acción del
   administrativo, las automáticas se producen con el hecho que las causa, y cualquier otra
   transición se rechaza.
4. La aprobación del cliente lleva automáticamente el componente a `OPERARIO_TRABAJANDO`, salvo
   cuando la cotización se registró estando el componente en `LISTO_PARA_ENTREGA`, en cuyo caso
   vuelve a `EN_PRUEBAS` conservando su fase y su progreso (duda DA-18); el rechazo deja la
   cotización `RECHAZADA` y el componente en `ESPERANDO_APROBACION`, sin afectar a los demás
   componentes ni al servicio, y después decide el administrador.
5. `RECHAZADO` solo se alcanza con la finalización manual del administrador, con motivo (texto
   libre) y fecha; el componente no avanza y solo admite la corrección por error humano del
   criterio 15.
6. El servicio se finaliza manualmente, nunca automáticamente, solo cuando tiene al menos un
   componente y todos están en `LISTO_PARA_ENTREGA` o `RECHAZADO`, ambos finalizados con motivo y
   fecha; de lo contrario el backend rechaza y explica el motivo.
7. La cancelación exige comentario, no modifica `activo`, no cambia componentes y deja el servicio
   fuera del seguimiento público.
8. `FINALIZADO` y `CANCELADO` no admiten cambios de estado, y ninguna reapertura queda creada.
9. Cada cambio de estado queda en el historial que corresponde, con usuario (si lo hay), fecha y
   comentario, sin borrar historial.
10. Un cambio que ya no es válido con el estado persistido responde `409` sin cambios parciales, y el
    mismo estado solicitado no genera efecto ni historial.
11. El seguimiento público usa solo los estados nuevos, en español, con la línea de tiempo de cuatro
    pasos (duda DA-15).
12. Se crean y ejecutan la migración de esquema y la migración de datos contra la base de datos de
    desarrollo, con advertencia previa de respaldo, y la tabla de mapeo queda aplicada; la
    ejecución sobre una base de datos que no sea de prueba queda sujeta a la confirmación de DA-11.
13. La verificación del backend se hace con `django.test` y la del frontend con Chrome DevTools
    MCP, sin dependencias nuevas.
14. Solo el ADMINISTRATIVO cambia estados, con la única excepción de la respuesta del cliente a su
    cotización autorizada por el token de seguimiento; cualquier otra petición de cliente o no
    autenticada se rechaza sin modificar datos.
15. La corrección por error humano de un `LISTO_PARA_ENTREGA` o de un cierre `RECHAZADO` está
    permitida solo al administrador, exige comentario obligatorio y queda registrada en
    `HistorialComponente`.
16. Antes de aprobar la implementación, `CONTEXTO_MAESTRO.md` §14 y §30 quedan actualizados al
    nuevo modelo y el cambio queda anotado en `MEMORY.md` (RF-FLU-17).

## 9. Fuera de alcance

- Crear roles adicionales o cuentas para el cliente, o ampliar la excepción de RF-FLU-14 más allá
  de la respuesta a la cotización con el token de seguimiento.
- Reapertura de servicios `FINALIZADO` o `CANCELADO`, y corrección de estados a nivel de servicio.
- Cancelación pública desde el enlace del cliente (decisión pendiente en 007, S-5).
- Transporte, recogida, entrega física, facturación o pagos.
- Notificaciones automáticas, WhatsApp Business API, correo, tiempo real, WebSockets, Redis o
  Channels.
- Cambiar el catálogo de fases, los catálogos de cotización o el contrato de cotizaciones
  aprobados en 002.
- Modificar datos existentes al margen de las migraciones previstas en RF-FLU-16.
- Diseño visual definitivo de la línea de tiempo pública (lo define 007).

## 10. Decisiones preservadas

- ADMINISTRATIVO es el único rol y el técnico es el administrativo (decisión cerrada); la única
  excepción es la respuesta del cliente a su cotización con token de seguimiento (RF-FLU-14).
- La cotización se asocia a un componente; el rechazo de un componente no afecta a los demás
  (RF-COT-01, RF-COT-13).
- El rechazo de una cotización no cambia el estado del componente; `RECHAZADO` solo lo decide el
  administrador al finalizar, con motivo (texto libre) y fecha (RF-FLU-06, RF-FLU-08).
- El criterio de cierre del servicio es único, el cierre es manual y exige todos los componentes
  finalizados con motivo y fecha (002, criterio único y D-6, RF-FLU-09).
- El backend decide las transiciones y la interfaz solo presenta lo que el backend entrega.
- La cancelación exige comentario y no modifica `activo`.
- Los estados cerrados no admiten cambios.
- La autenticación y la sesión de 004 y 006 no cambian.
- El cliente no ve campos internos (RF-COT-15, 005 RF-ADM-28).

## 11. Dudas abiertas

Estas dudas no bloquean la redacción de esta spec, pero sí bloquean su aprobación y la migración.

- **DA-1 — Trabajo iniciado.** ¿`OPERARIO_TRABAJANDO` equivale a trabajo iniciado (fase
  `DESMONTAJE_INICIADO` y `trabajo_iniciado=True`)? ¿Sigue existiendo una acción manual de "iniciar
  trabajo", o queda solo la transición automática al aprobar?
- **DA-5 — Quién registra el paso a pruebas.** ¿El paso a `EN_PRUEBAS` lo registra siempre el
  administrativo? (La corrección por error humano de un `LISTO_PARA_ENTREGA` o de un cierre
  `RECHAZADO` queda **cerrada** por la decisión sobre corrección: permitida solo al administrador,
  con comentario obligatorio y registro en `HistorialComponente` — RF-FLU-07.)
- **DA-7 — `NO_APROBADO` a `CANCELADO`.** `[PROPUESTA]`. Tiene el efecto de que el enlace de
  seguimiento deja de estar disponible. ¿Es correcto, o debe migrar a `FINALIZADO`?
- **DA-8 — Servicios `LISTO_PARA_ENTREGA` y `ENTREGADO`.** ¿`LISTO_PARA_ENTREGA` pasa a `EN_CURSO`
  (`[PROPUESTA]`), dejando el cierre al administrativo? ¿`ENTREGADO` pasa a `FINALIZADO`
  (`[PROPUESTA]`) sin inventar fecha de finalización? ¿Se conserva `fecha_entrega` como dato de
  consulta?
- **DA-9 — Componentes finalizados antiguos.** ¿Su `motivo_finalizacion` se reescribe al nuevo
  catálogo o se conserva como historial? El mapeo a `LISTO_PARA_ENTREGA` es `[PROPUESTA]`.
- **DA-10 — Estados antiguos de componente.** `APROBADO`, `EN_PROCESO` y `RECHAZADO_BLOQUEANTE` tienen
  mapeo `[SUPUESTO]`. Confirmar.
- **DA-11 — Naturaleza de los datos.** La petición indica que los datos actuales son de prueba.
  Confirmarlo antes de aceptar un mapeo que pierde distinciones.
- **DA-12 — Cancelación desde cualquier estado.** Se supone que el administrativo puede cancelar en
  cualquier estado no cerrado, incluso con componentes en pruebas. Confirmar.
- **DA-13 — Referencias de decisiones anteriores.** Las referencias D-3 a D-12 de la 002 se toman
  de la petición. El plan de la 006 no contiene decisiones numeradas: D-1, D-6 y D-8 se retiraron
  de la lista de cláusulas superadas de esa spec, y D-8 (corrección de cierres por error humano)
  sigue vigente. Conviene verificar el texto exacto de las decisiones de la 002 antes de aprobar
  esta spec.
- **DA-14 — Fases.** Se supone que el catálogo de fases (`RECIBIDO`, `DESMONTAJE_INICIADO`,
  `EN_EJECUCION`) no cambia. Confirmar.
- **DA-15 — Línea de tiempo pública.** Los cuatro pasos son `[PROPUESTA]`. ¿Dónde cae
  `OPERARIO_TRABAJANDO`? ¿`LISTO_PARA_ENTREGA` es "Pruebas" o "Finalizado"?
- **DA-16 — Usuario en cambios provocados por el cliente.** ¿El historial de un cambio automático
  causado por el cliente queda sin usuario, o se marca con una identidad propia?

### Cerradas en esta revisión

- **DA-2 — Cotización no bloqueante rechazada (cerrada).** Cerrada por la decisión sobre el
  rechazo: ningún rechazo de cotización cambia el estado del componente, bloqueante o no; el
  componente permanece en `ESPERANDO_APROBACION` con la cotización `RECHAZADA` y decide el
  administrador (RF-FLU-06).
- **DA-6 — Motivo del cierre de un componente rechazado (cerrada).** Cerrada por la decisión sobre
  `RECHAZADO`: el motivo es texto libre escrito por el administrador (no hay catálogo propio) y la
  finalización exige motivo y fecha (RF-FLU-08). Como todo componente en `RECHAZADO` está por
  definición ya finalizado con motivo y fecha, basta con estar en `RECHAZADO` para cumplir la
  condición de RF-FLU-09.
- **DA-3 — Varias cotizaciones del mismo componente (cerrada).** Cerrada por la decisión sobre
  cotizaciones adicionales: la primera aprobación de la cotización pendiente lleva el componente a
  `OPERARIO_TRABAJANDO`; si durante el trabajo se registra una cotización adicional, el componente
  vuelve a `ESPERANDO_APROBACION` (RF-FLU-05) y el cliente responde la cotización pendiente más
  reciente.
- **DA-4 — Cotización adicional durante el trabajo (cerrada).** Cerrada por la decisión sobre la
  vista de aprobación pública: su comportamiento se conserva como hoy, usando la cotización
  pendiente más reciente del componente. El componente en `OPERARIO_TRABAJANDO` vuelve a
  `ESPERANDO_APROBACION` al registrar una cotización adicional (RF-FLU-05).
- **DA-17 — Cotización adicional durante `EN_PRUEBAS` (cerrada).** Cerrada por la decisión del
  usuario: si un componente está en `EN_PRUEBAS` y se registra una cotización para él, el
  componente vuelve a `ESPERANDO_APROBACION` de forma automática, con las pruebas detenidas a la
  espera de la respuesta del cliente (RF-FLU-05, §4.1).
- **DA-18 — Cotización registrada en `LISTO_PARA_ENTREGA` (cerrada).** Cerrada por la decisión
  del usuario: el componente pasa a `ESPERANDO_APROBACION` de forma automática, conservando su
  fase y su progreso ("se queda en pruebas": no reinicia el trabajo); al aprobar esa cotización
  el componente vuelve a `EN_PRUEBAS`, no a `OPERARIO_TRABAJANDO` (RF-FLU-05, RF-FLU-06,
  RF-FLU-07 y la fila `LISTO_PARA_ENTREGA` → `ESPERANDO_APROBACION` de §4.1).
