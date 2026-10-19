# Spec 006 — Control de estados en el panel administrativo

**Especificación funcional · Hidroemcol**  
**Estado: aprobada**

## 1. Contexto y objetivo

El panel administrativo permite iniciar trabajo, finalizar componentes o editarlos, pero
iniciar trabajo no cambia el estado visible del componente. Además, el administrativo no
tiene una operación general para corregir o conducir el estado operativo de un componente ni
un selector explícito para conducir el estado del servicio.

Esta especificación define el control administrativo de estados y corrige la recuperación de
sesión al recargar una ruta protegida. El backend continúa siendo la autoridad para permisos,
transiciones, cotizaciones, fechas, historial y cierres.

## 2. Relación con especificaciones anteriores

Esta especificación **supersede o modifica únicamente** las cláusulas siguientes:

- `002`:
  - glosario §4.3 y §4.4, para precisar qué estados del componente son seleccionables y cuáles
    son derivados, y qué significa que un componente sea activo;
  - §2 (usuarios afectados) y §5, únicamente donde atribuye a "técnico" la ejecución de
    acciones de estado; desde el panel esas acciones las ejecuta el rol `ADMINISTRATIVO`;
  - RF-COT-08, únicamente para que iniciar trabajo sincronice además el estado visible a
    `EN_PROCESO`;
  - RF-COT-09, para permitir la selección administrativa de los estados operativos confirmados
    y mantener la finalización de componentes `RECHAZADO_BLOQUEANTE` conforme a RF-COT-05;
  - RF-COT-10, para fijar los destinos válidos de una corrección de finalización.
- `005`:
  - RF-ADM-18, para que iniciar trabajo cambie el estado visible a `EN_PROCESO`;
  - RF-ADM-19, para incorporar el control autorizado de estados y conservar la corrección de
    finalizaciones;
  - RF-ADM-20, para incorporar el selector/acción de estado de servicio y la alternativa
    `CANCELADO`;
  - RF-ADM-21, CL-ADM-22, el criterio de finalización #14 y el §10, para reemplazar la
    prohibición de todo selector por un selector limitado por las reglas del backend;
  - RNF-ADM-02, RF-ADM-01 y los casos límite de sesión, únicamente para añadir el bootstrap de
    sesión al cargar la aplicación.
- `004`: RF-14, RF-15 y el caso límite de recarga, únicamente para especificar el bootstrap de
  renovación antes de resolver una ruta protegida.

Todas las demás reglas, catálogos, permisos, privacidad, cotizaciones, trazabilidad,
conservación de datos, historial, API pública, frontend, seguridad y fuera de alcance de esas
especificaciones permanecen intactos. Esta especificación no modifica la arquitectura ni
agrega dependencias.

## 3. Usuarios

- **ADMINISTRATIVO:** único rol autorizado a consultar y cambiar estados desde el panel.
  Reemplaza, para estas acciones, las menciones a "técnico" de `002`.
- **Cliente final:** no usa el panel y no puede cambiar estados.

## 4. Glosario

- **Estado:** condición operativa o de negocio que describe si un componente o servicio está
  pendiente, en ejecución, finalizado o cerrado. Es el dato visible de la situación actual y
  su cambio exige validación del backend.
- **Fase:** etapa del trabajo físico del componente. Conserva el catálogo y el significado de
  `RECIBIDO`, `DESMONTAJE_INICIADO` y `EN_EJECUCION` definidos en `002` §4.7. Una fase no
  reemplaza al estado.
- **Estado operativo seleccionable del componente:** estado que el ADMINISTRATIVO puede pedir
  mediante la acción de cambio, limitado a `PENDIENTE`, `EN_PROCESO`,
  `FINALIZADO_POR_TECNICO` y `FINALIZADO_POR_CLIENTE`.
- **Estado derivado del componente:** `APROBADO`, `RECHAZADO` o `RECHAZADO_BLOQUEANTE`, cuyo
  significado proviene de cotizaciones y respuestas. No puede ser asignado manualmente por el
  ADMINISTRATIVO ni por la interfaz.
- **Componente activo:** componente no finalizado sobre el que aún puede ejecutarse trabajo,
  conforme a `002` §4.4 (`PENDIENTE` sin cotización bloqueante pendiente, `APROBADO`,
  `RECHAZADO` o `EN_PROCESO`).
- **Componente finalizado:** componente en `FINALIZADO_POR_TECNICO` o
  `FINALIZADO_POR_CLIENTE`, conforme a `002`.
- **Servicio desactivado:** servicio con `activo=False`. Se conserva para consulta histórica
  autorizada, pero queda fuera del operativo y del seguimiento público conforme a `005`.
- **Servicio cancelado:** servicio en estado `CANCELADO` sin modificar `activo`. Se conserva
  para consulta histórica autorizada, pero queda fuera de la operación ordinaria y del
  seguimiento público.
- **Operación canónica de inicio de trabajo:** acción única que registra la fase
  `DESMONTAJE_INICIADO`, marca `trabajo_iniciado=True`, registra fecha y usuario y deja el
  estado en `EN_PROCESO`.
- **Bootstrap de sesión:** intento inicial de renovar la sesión usando la cookie `refresh_token`
  antes de decidir si una ruta administrativa debe mostrarse o redirigir al login.
- **Single-flight:** propiedad por la cual, si hay varias renovaciones solicitadas a la vez,
  solo se ejecuta una y las demás comparten su resultado.

## 5. Requisitos funcionales (EARS)

### Estados de componentes

#### RF-EST-01 — Catálogo seleccionable

**WHEN** el ADMINISTRATIVO consulta un componente **THEN** el backend DEBE indicar, según el
estado actual y las reglas vigentes, las opciones seleccionables entre `PENDIENTE`,
`EN_PROCESO`, `FINALIZADO_POR_TECNICO` y `FINALIZADO_POR_CLIENTE`.

**AND** la interfaz DEBE mostrar etiquetas legibles en español y NO DEBE presentar como
opciones manuales `APROBADO`, `RECHAZADO` ni `RECHAZADO_BLOQUEANTE`.

**AND** las opciones DEBEN provenir del backend; la interfaz NO DEBE decidir por su cuenta qué
transición es válida.

**AND** para un componente `RECHAZADO_BLOQUEANTE` (no activo) el backend DEBE ofrecer
únicamente su finalización como `FINALIZADO_POR_TECNICO` o `FINALIZADO_POR_CLIENTE`.

#### RF-EST-02 — Estados derivados

**WHEN** una cotización o aprobación produzca `APROBADO`, `RECHAZADO` o
`RECHAZADO_BLOQUEANTE` **THEN** el backend DEBE conservar esas reglas derivadas y NO DEBE
permitir que el selector administrativo las escriba directamente.

**AND** cambiar el estado operativo NO DEBE sobrescribir, borrar, editar ni crear
retroactivamente cotizaciones o aprobaciones.

#### RF-EST-03 — Acción autorizada para componente

**WHEN** un ADMINISTRATIVO solicita cambiar el estado de un componente mediante la acción o
endpoint administrativo autorizado **THEN** el backend DEBE verificar autenticación, rol,
pertenencia del componente al servicio indicado y existencia del componente antes de cambiarlo.

**AND** DEBE validar el estado solicitado contra el catálogo seleccionable y las reglas de
`002` antes de persistirlo.

**AND** la acción DEBE ejecutarse dentro de una transacción que bloquee la fila del servicio y
la del componente, vuelva a consultar el estado persistido y confirme el cambio de forma
atómica.

**AND** DEBE registrar la trazabilidad en el modelo vigente `HistorialComponente`, guardando el
componente afectado, estado anterior, estado nuevo, fase registrada cuando aplique, usuario
ADMINISTRATIVO, fecha/hora y comentario suministrado, sin crear un modelo ni una migración
nuevos.

#### RF-EST-04 — Rechazo y conflicto

**IF** el componente no pertenece al servicio solicitado, el usuario no es ADMINISTRATIVO,
el estado no es seleccionable o la regla de negocio no permite el cambio **THEN** el backend
DEBE rechazar la operación sin modificar datos.

**IF** otra operación cambia el recurso antes de que se confirme la acción y el estado
persistido más reciente ya no permite el cambio **THEN** el backend DEBE responder `409
Conflict`, sin sobrescribir la modificación concurrente ni producir cambios parciales, y la
interfaz DEBE pedir recargar antes de reintentar.

#### RF-EST-05 — Bloqueo por cotización

**WHEN** un componente tiene una cotización bloqueante `PENDIENTE` o `RECHAZADA` **THEN** el
backend NO DEBE permitir que pase a `EN_PROCESO`, incluso si la petición se envía fuera de la
interfaz.

**AND** la interfaz DEBE mostrar el motivo devuelto por el backend y no ocultar el componente.

**WHEN** el componente está `RECHAZADO_BLOQUEANTE` **THEN** el ADMINISTRATIVO DEBE poder
finalizarlo como `FINALIZADO_POR_TECNICO` o `FINALIZADO_POR_CLIENTE` según RF-COT-05,
registrando el motivo y la trazabilidad correspondiente, y NO DEBE poder llevarlo a
`EN_PROCESO`.

#### RF-EST-06 — Inicio de trabajo visible

**WHEN** el ADMINISTRATIVO inicia trabajo y ninguna cotización bloqueante impide continuar
**THEN** el backend DEBE ejecutar la operación canónica de inicio de trabajo, conservar el
registro de inicio de desmontaje, marcar `trabajo_iniciado=True`, registrar la fecha y el
usuario, y dejar visible el estado `EN_PROCESO`.

**AND** seleccionar `EN_PROCESO` en la acción de cambio DEBE ser equivalente a la operación
canónica de inicio de trabajo: DEBE registrar la fase `DESMONTAJE_INICIADO`, la fecha,
`trabajo_iniciado=True` y el usuario.

**AND** los demás componentes del servicio DEBEN conservar sus propios estados y reglas.

#### RF-EST-07 — Finalización y corrección

**WHEN** el ADMINISTRATIVO selecciona `FINALIZADO_POR_TECNICO` o
`FINALIZADO_POR_CLIENTE` **THEN** el backend DEBE aplicar las reglas de finalización de `002`,
registrar fecha, usuario, motivo y comentario, y conservar los datos de cierre vigentes.

**WHEN** se corrige una finalización por error humano **THEN** el backend DEBE conservar el
estado anterior, el estado nuevo, usuario, fecha/hora y comentario de corrección en
`HistorialComponente`.

**AND** una corrección desde un estado final DEBE permitir únicamente estos destinos:
`EN_PROCESO`, `FINALIZADO_POR_TECNICO` o `FINALIZADO_POR_CLIENTE`, validando primero las reglas
de cotización y trabajo.

#### RF-EST-08 — Coherencia entre estado, fase y trabajo

**WHEN** el estado se cambia mediante una acción administrativa **THEN** el backend DEBE
mantener la siguiente correspondencia, sin borrar evidencia de trabajo iniciado:

- `PENDIENTE` → fase `RECIBIDO`; se permite únicamente antes de iniciar trabajo.
- `EN_PROCESO` → fase `DESMONTAJE_INICIADO`, `trabajo_iniciado=True` y `fecha_inicio_trabajo`.
- `FINALIZADO_POR_TECNICO` / `FINALIZADO_POR_CLIENTE` → conserva fase y fechas; registra
  `fecha_finalizacion` y `motivo_finalizacion`.

**AND** seleccionar el mismo estado que ya tiene el componente DEBE aceptarse como operación
idempotente sin cambios ni historial.

**AND** una transición hacia `PENDIENTE` DEBE rechazarse si el componente ya tiene trabajo
iniciado o un estado final; nunca DEBEN borrarse fechas, fase ni evidencias.

### Estado del servicio

#### RF-EST-09 — Selector de estado del servicio

**WHEN** el ADMINISTRATIVO consulta un servicio activo **THEN** el panel DEBE ofrecer un
selector o acción de cambio cuyas opciones entregue el backend, con etiquetas en español.

**AND** los estados seleccionables DEBEN ser los estados normales del catálogo `EstadoServicio`:
`SOLICITADO`, `EN_REVISION`, `COTIZANDO`, `ESPERANDO_APROBACION`, `EN_REPARACION`, `EN_PRUEBAS`,
`LISTO_PARA_ENTREGA`, `ENTREGADO` y `NO_APROBADO`.

**AND** `FINALIZADO` y `CANCELADO` NO DEBEN ofrecerse como escritura libre: `FINALIZADO` DEBE
invocar la operación protegida de cierre (RF-EST-10) y `CANCELADO` la acción protegida
alternativa (RF-EST-11).

#### RF-EST-10 — Finalización del servicio

**WHEN** el ADMINISTRATIVO solicita `FINALIZADO` **THEN** el backend DEBE permitirlo solo si
todos los componentes están en `FINALIZADO_POR_TECNICO` o `FINALIZADO_POR_CLIENTE`, conforme a
la regla vinculante de `002`.

**AND** DEBE registrar el estado, la fecha de finalización, el usuario y el comentario en el
historial del servicio.

**IF** queda un componente sin finalizar, o el servicio no tiene componentes **THEN** el
backend DEBE rechazar el cierre con el motivo y no modificar el servicio.

#### RF-EST-11 — Cancelación alternativa

**WHEN** el ADMINISTRATIVO necesita cerrar administrativamente un servicio sin que todos sus
componentes estén finalizados **THEN** DEBE poder solicitar `CANCELADO` mediante una acción
explícita, con autorización del backend, sin ejecutar la lógica de `FINALIZADO`.

**AND** la cancelación DEBE registrar usuario, fecha, estado alcanzado y comentario; NO DEBE
marcar componentes como finalizados ni eliminar sus cotizaciones, aprobaciones, historial o
datos técnicos.

**AND** la cancelación DEBE requerir comentario y NO DEBE modificar `activo`; el servicio queda
fuera de la operación ordinaria y deja de ser consultable por su token de seguimiento público.

**AND** un servicio `CANCELADO` no DEBE volver a aparecer como operativo ni permitir cambios de
estado; esta especificación no crea ninguna reapertura.

#### RF-EST-12 — Fechas, historial y permisos del servicio

**WHEN** un cambio de estado del servicio se confirma **THEN** el backend DEBE aplicar este
mapeo de fechas y conservar el resto:

- `FINALIZADO` → escribe `fecha_finalizacion`.
- `ENTREGADO` → escribe `fecha_entrega`.
- los demás estados → no escriben fecha.
- ninguna transición DEBE borrar una fecha histórica existente.
- `CANCELADO` no dispone de campo de fecha y por tanto no escribe ninguna.

**AND** DEBE crear un registro en `HistorialServicio` con el estado alcanzado, comentario,
fecha/hora y usuario.

**AND** solo un ADMINISTRATIVO autenticado y activo puede ejecutar el cambio; un cliente,
usuario no autenticado o cuenta inactiva DEBE recibir rechazo sin modificar datos.

#### RF-EST-13 — Servicios desactivados y cancelados

**WHEN** un servicio tiene `activo=False` o está en estado `CANCELADO` **THEN** DEBE quedar
excluido del dashboard, listados operativos, indicadores y seguimiento público ordinario,
conforme a `005`.

**AND** el backend DEBE rechazar cambios operativos de estado sobre un servicio desactivado o
cancelado, salvo una consulta histórica autorizada; sus datos DEBEN conservarse.

### Persistencia de sesión al recargar

#### RF-EST-14 — Bootstrap con refresh

**WHEN** la aplicación frontend inicia o se recarga mientras la URL pertenece a una ruta
administrativa protegida **THEN** DEBE intentar renovar la sesión con la cookie `refresh_token`
existente antes de redirigir al login.

**AND** el bootstrap NO DEBE ejecutarse por el hecho de cargar una ruta pública.

**AND** el nuevo token de acceso DEBE permanecer únicamente en memoria.

**AND** el frontend NO DEBE guardar el access token ni el refresh token en `localStorage`,
`sessionStorage` ni otro almacenamiento legible por JavaScript; el refresh DEBE seguir siendo
cookie `httpOnly` con las protecciones de `004`.

**AND** el bootstrap DEBE ser single-flight: las renovaciones solicitadas a la vez DEBEN
compartir una sola petición; si el refresh falla por rotación concurrente entre pestañas, DEBE
reintentarse una vez y, si persiste, conducir al login.

#### RF-EST-15 — Estados de bootstrap y expiración

**WHILE** el bootstrap está pendiente **THEN** la ruta protegida DEBE mostrar un estado de
carga y NO DEBE redirigir prematuramente ni mostrar datos administrativos.

**IF** el refresh está ausente, expirado, revocado, falla por cuenta inactiva o el intento
falla por red, timeout o error del servidor **THEN** el frontend DEBE limpiar el access token
en memoria, conducir a `/admin/login` y no mostrar datos administrativos ni errores técnicos.

**IF** el bootstrap es válido **THEN** el frontend DEBE resolver la ruta protegida sin pedir
credenciales nuevamente y DEBE continuar usando el mecanismo reactivo de renovación ante `401`.

## 6. Requisitos no funcionales (EARS)

#### RNF-EST-01 — Seguridad y autorización

Todos los endpoints o acciones de cambio DEBEN exigir autenticación válida, rol
`ADMINISTRATIVO` activo, pertenencia de la entidad al servicio y validación en backend. Ocultar
una opción en el frontend NO es una medida de seguridad.

#### RNF-EST-02 — Integridad y concurrencia

Las mutaciones de estado de componente y servicio DEBEN ser atómicas, usar transacción y
bloqueo de filas del servicio y de la entidad específica antes de reevaluar reglas. Un
conflicto debe devolver `409 Conflict` sin pérdida ni sobrescritura silenciosa y sin requerir
Redis, WebSockets, Channels, una dependencia nueva o un campo de versión nuevo.

#### RNF-EST-03 — Trazabilidad

Los cambios de componente DEBEN registrarse en `HistorialComponente` y los cambios de servicio
en `HistorialServicio`, usando la información que cada modelo vigente admite (el historial de
servicio conserva el estado alcanzado, el comentario, el usuario y la fecha). El historial NO
DEBE poder eliminarse desde esta funcionalidad.

#### RNF-EST-04 — Accesibilidad y responsive

Los selectores, acciones, errores, bloqueos y estados de carga DEBEN tener nombres accesibles,
foco visible, contraste suficiente, objetivos táctiles utilizables y una alternativa textual
al color. El flujo DEBE funcionar en móvil, tablet y escritorio sin desplazamiento horizontal
para operar un componente o servicio.

#### RNF-EST-05 — Feedback y consistencia

**WHEN** una mutación termina **THEN** el panel DEBE confirmar el resultado y reflejar el
estado devuelto por el servidor.

**IF** falla por regla, autorización, conflicto o sesión **THEN** DEBE mostrar un mensaje
comprensible, no fingir éxito y ofrecer recarga o reintento cuando corresponda.

#### RNF-EST-06 — Sesión segura

La solución DEBE conservar las garantías de `004`: access token solo en memoria, refresh en
cookie `httpOnly`, CSRF, rotación, revocación, logout efectivo y sin secretos en logs o
almacenamiento del navegador.

#### RNF-EST-07 — Verificación

La lógica del backend DEBE verificarse con `django.test` mediante `manage.py test`, sin
dependencias nuevas. El frontend DEBE verificarse de forma manual en el navegador.

## 7. Casos límite

- **CL-01 — Cotización bloqueante pendiente:** se solicita `EN_PROCESO`; el backend responde
  rechazo con el bloqueo, no cambia fase ni estado y los demás componentes siguen operables.
- **CL-02 — Cotización bloqueante rechazada:** el componente permanece detenido, pero puede
  finalizarse según RF-COT-05; el cierre del servicio sigue exigiendo que todos los
  componentes estén finalizados.
- **CL-03 — Estado derivado solicitado manualmente:** se solicita `APROBADO`, `RECHAZADO` o
  `RECHAZADO_BLOQUEANTE`; el backend rechaza la escritura y no toca cotizaciones ni
  aprobaciones.
- **CL-04 — Reversión a `PENDIENTE`:** se rechaza si el componente ya tiene trabajo iniciado o
  un estado final; nunca se borran fechas, fase ni evidencias.
- **CL-05 — Corrección desde finalizado:** la corrección por error humano conserva estado
  anterior, estado nuevo, usuario, fecha y comentario en `HistorialComponente`, y solo admite
  `EN_PROCESO`, `FINALIZADO_POR_TECNICO` o `FINALIZADO_POR_CLIENTE`, revalidando cotizaciones y
  trabajo.
- **CL-06 — Finalizar frente a cancelar:** `FINALIZADO` se rechaza si falta un componente por
  finalizar; `CANCELADO` usa la acción alternativa explícita y no convierte componentes en
  finalizados.
- **CL-07 — Conflicto concurrente:** dos administrativos actúan sobre el mismo servicio o
  componente; la operación que pierde la validación tras el bloqueo recibe `409`, sin cambios
  parciales, y el panel pide recargar.
- **CL-08 — Identificador ajeno:** se intenta cambiar un componente que pertenece a otro
  servicio; el backend rechaza la operación sin revelar ni modificar el recurso ajeno.
- **CL-09 — Servicio desactivado:** se intenta cambiar su estado; se rechaza y el servicio
  permanece fuera del operativo, aunque su historial siga consultable por un ADMINISTRATIVO.
- **CL-10 — Refresh ausente o expirado:** al recargar una ruta protegida no hay refresh válido;
  se muestra carga durante el intento y luego `/admin/login`, sin datos administrativos ni
  error técnico expuesto.
- **CL-11 — Recarga durante ruta protegida:** el access token en memoria desaparece; el
  bootstrap restaura la sesión mediante la cookie o redirige solo después de que el intento
  termine.
- **CL-12 — Cierre concurrente del servicio:** un administrativo intenta `FINALIZADO` mientras
  otro deja un componente sin finalizar; el primero recibe `409` o el rechazo equivalente de
  la regla y el servicio no queda parcialmente actualizado.
- **CL-13 — Mismo estado:** se selecciona el estado que el componente ya tiene; se acepta como
  operación sin efecto y sin historial.
- **CL-14 — Servicio ya cerrado:** se intenta cambiar el estado de un componente de un servicio
  en `FINALIZADO`, `ENTREGADO` o `CANCELADO`; el backend lo rechaza.
- **CL-15 — Servicio sin componentes:** se intenta `FINALIZADO`; se rechaza y se indica que no
  hay componentes que cerrar.
- **CL-16 — Corrección a nivel de servicio:** se intenta revertir un servicio `FINALIZADO`,
  `ENTREGADO` o `CANCELADO`; esta versión no lo permite.
- **CL-17 — Transición desde derivado:** un componente en `APROBADO` o `RECHAZADO` sin
  cotización bloqueante pendiente o rechazada puede pasar a `EN_PROCESO`; uno en
  `RECHAZADO_BLOQUEANTE` no.
- **CL-18 — Bootstrap en ruta pública:** cargar una ruta del sitio público no dispara el
  bootstrap de sesión.
- **CL-19 — Fallo no autenticable del bootstrap:** red caída, timeout, `5xx` o `429` durante el
  bootstrap conducen a `/admin/login` sin mostrar datos ni errores técnicos.
- **CL-20 — Varias pestañas:** dos pestañas renuevan a la vez; el single-flight evita peticiones
  duplicadas y un fallo por rotación se reintenta una vez antes de llevar al login.
- **CL-21 — Comentario obligatorio ausente:** se intenta cancelar o corregir sin comentario; el
  backend rechaza la operación sin modificar datos.
- **CL-22 — Reintento tras `409`:** el panel solicita recargar; no reintenta a ciegas la
  transición con datos obsoletos.

## 8. Criterios de aceptación

1. El inicio de trabajo deja visible `EN_PROCESO`, conserva fase, `trabajo_iniciado`, fecha y
   usuario, y respeta bloqueos de cotizaciones; seleccionar `EN_PROCESO` equivale a iniciar
   trabajo.
2. El ADMINISTRATIVO puede solicitar únicamente los cuatro estados operativos confirmados del
   componente según las opciones del backend; los tres estados derivados nunca son opciones de
   escritura manual; `RECHAZADO_BLOQUEANTE` solo permite finalizar.
3. La acción de componente valida pertenencia, permisos, reglas, transacción, bloqueo,
   conflicto `409`, comentario, usuario, fecha y trazabilidad en `HistorialComponente`.
4. Una transición a `PENDIENTE` se rechaza tras iniciar o finalizar; seleccionar el mismo estado
   es una operación sin efecto.
5. El servicio ofrece control de estados normales desde el panel; `FINALIZADO` solo se confirma
   con todos los componentes finalizados y `CANCELADO` es la alternativa administrativa
   explícita que no cambia `activo` ni altera componentes.
6. Las fechas del servicio siguen el mapeo aprobado y no se borra ninguna fecha histórica; el
   servicio en `FINALIZADO`/`ENTREGADO`/`CANCELADO` no acepta más cambios de estado.
7. Los servicios desactivados y cancelados no aparecen en operación ni seguimiento ordinarios y
   no aceptan cambios operativos.
8. La recarga de una ruta protegida intenta bootstrap con la cookie refresh, muestra carga
   mientras tanto, es single-flight, conserva el access solo en memoria y lleva a `/admin/login`
   si la sesión expiró o el intento falla.
9. El flujo comunica éxitos, bloqueos, errores, conflictos y sesión expirada, y es accesible y
   usable en móvil, tablet y escritorio.
10. La verificación se realiza con `django.test` en el backend y de forma manual en el
    navegador, sin dependencias nuevas.

## 9. Fuera de alcance

- Crear roles adicionales, permisos diferenciados o cuentas de cliente.
- Cambiar los catálogos aprobados, las reglas de cotización, las aprobaciones o el modelo de
  seguimiento público fuera de las modificaciones expresas de esta spec.
- Crear un campo de fecha de cancelación u otro cambio de esquema; se reutilizan
  `HistorialComponente`, `HistorialServicio` y las fechas existentes. Cualquier migración que
  resultara imprescindible debería justificarse y aprobarse antes.
- Reapertura automática o manual de un servicio `CANCELADO`, o conversión de cancelado a
  finalizado sin una nueva decisión de negocio.
- Corrección de estados a nivel de servicio.
- WebSockets, SSE, polling nuevo, Redis, Channels, dependencias nuevas, tiempo real, WhatsApp
  Business API, notificaciones automáticas, pagos, entrega, inventario o e-commerce.
- Cambiar fases o borrar evidencias de trabajo como efecto implícito de seleccionar un estado.

## 10. Decisiones preservadas

- El backend es la autoridad y la interfaz solo presenta opciones y respuestas validadas.
- Las cotizaciones bloqueantes pendientes o rechazadas impiden `EN_PROCESO`; las no bloqueantes
  no lo impiden.
- `RECHAZADO_BLOQUEANTE` puede finalizarse conforme a RF-COT-05.
- El cierre ordinario del servicio es manual y exige todos los componentes finalizados.
- El rechazo o cambio de un componente no afecta indebidamente a los demás.
- La autenticación mantiene access en memoria y refresh en cookie `httpOnly`, con rotación,
  revocación y protección CSRF.
- El frontend no decide transiciones; solo presenta las opciones que entrega el backend.

## 11. Dudas abiertas

Ninguna. Las decisiones de la clarificación quedaron incorporadas en esta especificación.
