# MEMORY.md — Estado y bitácora del proyecto

Complementa dos capas que ya existen:

- `AGENTS.md` → cómo trabajar en el repo (comandos, arquitectura, convenciones).
- `CONTEXTO_MAESTRO.md` → contexto de negocio aprobado (§1–49).

Este archivo guarda **dónde está el proyecto realmente** y **qué sigue sin decidirse**, para
que una sesión nueva no repita discusiones ni adivine lo ya hecho.

Mantenerlo corto. Actualizarlo al cerrar cada tarea relevante (regla en `AGENTS.md`).

---

## 1. Estado por fases

Roadmap aprobado en `CONTEXTO_MAESTRO.md` §42.

| Fase | Contenido | Estado |
|---|---|---|
| 1 — Backend base | Apps `usuarios` y `servicios`, `AUTH_USER_MODEL`, 8 modelos, migraciones, Django Admin | **Completada** |
| 2 — API | Serializers, JWT, permisos, API pública de seguimiento y de aprobación | **Avanzada** — falta probarla |
| 3 — Frontend público | Landing, Nosotros, Servicios, Soluciones, Contacto, Solicitar, Seguimiento | **Solo andamiaje** — las 8 páginas son placeholders |
| 4 — Panel administrativo | Login, dashboard, servicios, detalle, cotizaciones | **Placeholder** (`/admin`) |
| 5 — Pruebas del flujo completo | Solicitud → entrega | **No iniciada** |
| 002 — Cotización por componente | Estados en el componente, reglas de proceso, acciones de API y admin | **Completada** — 201 tests |

**Gaps transversales:**

- **El frontend no tiene capa de API.** No existe cliente HTTP, ni `import.meta.env`, ni
  manejo/guardado del token JWT. `src/services/` y `src/hooks/` solo tienen README de marcador.
  Esta es la brecha que bloquea las fases 3 y 4. Tampoco hay forma de consumir el estado del
  componente en el seguimiento (ver §2, "Tiempo real del cliente").
- **Tests: solo backend.** 201 tests con `manage.py test` (`usuarios`, `servicios`, modelos,
  reglas, serializers, API, admin y recorridos). El frontend no tiene runner instalado, así
  que sigue sin cobertura.
- **Despliegue sin configurar.** `settings.py:39` fija `ALLOWED_HOSTS` a `localhost/127.0.0.1`
  y `settings.py:145` fija `CORS_ALLOWED_ORIGINS` a `:5173`. Render + Neon + Cloudflare están
  definidos como destino pero no implementados.
- **Sin git.** La rama `master` no tiene ningún commit todavía.

---

## 2. Decisiones pendientes

### Bloquean implementación

| Tema | Qué bloquea | Referencia |
|---|---|---|
| Campos de información técnica | Dónde se guardan diagnóstico, trabajo, pruebas, observaciones | §16, §43 |
| Política al rechazar un costo adicional | Flujo de cotización `ADICIONAL`: hoy comparte reglas con la inicial | §38 |
| Si una cotización rechazada puede reenviarse | Endpoint de cotizaciones: no existe reenvío | §43 |

**Resuelto en la spec 002** (estaba en esta lista y ya no bloquea):

- *Reglas de transición entre estados.* Antes: "el estado se puede cambiar a cualquier valor sin
  validación". Ahora todo cambio de estado pasa por una acción de
  `backend/servicios/acciones.py`, que consulta `reglas.py`.
- *Política al rechazar una cotización.* El rechazo es **por componente**: no frena a los demás
  componentes ni cierra el servicio (RF-COT-05, RF-COT-13).
- *Hueco de modelado del rechazo por componente.* Cerrado con `Cotizacion.componente`, que hace
  posible representar el rechazo granular.

### Tomadas provisionalmente en el código — falta confirmación formal

Marcadas con comentarios `# DECISIÓN PENDIENTE:` en `backend/servicios/models.py`:

- **Formato del código de servicio** (línea 93) → `SRV-<año>-<consecutivo 5 dígitos>`,
  generado en `Servicio.save()`.
- **Formato y longitud del token de seguimiento** (línea 114) →
  `secrets.token_urlsafe(24)` (~32 caracteres), generado en `Servicio.save()`.
- **Tipo de componente** (línea 156) → texto libre, no lista cerrada.
- **Formato del número de cotización** (línea 180) → `COT-<año>-<consecutivo 5 dígitos>`,
  generado en `Cotizacion.save()`.
- **`usuario_registro` en aprobaciones** (línea 260) → queda en `null` cuando
  `medio=WEB`, porque una aprobación del cliente no tiene administrativo detrás.

Resuelto sin marca, pero conviene dejarlo escrito: la **autenticación de la API es
SimpleJWT** (`/api/token/` y `/api/token/refresh/`, `config/urls.py:24`). Lo que sigue
abierto es dónde guarda el frontend ese token.

### Configuración y operación — sin definir

- Cloudflare: bucket, nombres, estructura de URLs, credenciales (§17, §43).
- Formato definitivo de los mensajes de WhatsApp (§43).
- Qué información técnica ve el cliente en el seguimiento (§43). Principio ya fijado en
  `specs/001`: la visibilidad se decide dato por dato, nunca por omisión.
- Diseño visual definitivo (§43). Base actual: variables CSS en
  `frontend/src/index.css`.
- Conservación y derechos de uso de las fotografías. Sin esto las imágenes se acumulan para
  siempre y es la única variable que realmente pesa en almacenamiento.

### Decisiones tomadas, pendientes de implementar

Salen de `specs/001-solicitud-banco-pruebas/spec.md`.

- **Preferencias de entrega en el formulario** (RF-3): tres casillas, todas opcionales, sin
  lógica de transporte. **Implica campo nuevo en el modelo y migración** (constitución,
  principio 2). El administrativo coordina por sus propios medios y cambia el estado cuando
  recibe el componente.
- **Prevención del doble envío** (RF-7.5 y 7.6): token de idempotencia, no una ventana de
  tiempo. Cubre recarga, corte de conexión y doble pestaña. Mientras se registra, la acción de
  enviar se desactiva. No requiere dependencias nuevas.
- **Aviso de segundo intento** (RF-8): se dispara por coincidencia de correo **o** teléfono,
  normalizados sin distinguir mayúsculas, espacios sobrantes ni tildes, y **solo si hay alguna
  solicitud previa en curso**. Una solicitud cuenta como en curso mientras no esté en un
  estado cerrado; los estados cerrados son **finalizado, entregado y cancelado** (RF-8.6).
  Rechazar la cotización de un componente **no** cierra el servicio. El aviso aparece antes de
  registrar; cancelar no deja nada registrado; nunca bloquea el envío.
  - Nota: `CONTEXTO_MAESTRO.md` §14 solo lista los once estados y no dice cuáles son
    cerrados. La clasificación salió de esta decisión del usuario, no del contexto maestro.
    Conviene promoverla a §14 cuando se defina la política de transiciones.
- **Textos libres con tope**: 500 caracteres para la descripción de la necesidad y 500 para la
  de cada componente. El peso en base de datos es irrelevante; lo que pesa son las fotos.
- **Límites de fotografías**: hasta 5 por solicitud, 10 MB cada una, JPG o PNG. Definido
  **solo** para esta vista; sigue sin definirse para el resto del sistema (§17).
- **Eliminación de datos personales**: no habrá botón de borrado. Válido porque la Ley 1581 de
  2012 no exige un botón, sino un canal para ejercer el derecho. **Pendiente para el final del
  proyecto**: publicar ese canal (correo o teléfono). Mientras no exista, el derecho existe pero
  no se puede ejercer.

### Dependencias que bloquean

- **RF-10, el aviso al administrativo, no es implementable todavía.** El panel es un
  placeholder (fase 4) y el frontend no tiene capa de API, que es el hueco que bloquea las
  fases 3 y 4. Es el mayor riesgo de secuencia de esta spec:RF-10 depende de resolver primero
  el cliente HTTP del frontend.
- **Cancelación desde el seguimiento**: el cliente puede cancelar desde el enlace mientras el
  componente no haya sido recibido; a partir de ahí solo el administrativo. Condición que ya se
  puede leer del estado, porque el administrativo cambia el estado cuando recibe el componente.
  **No pertenece a esta spec** (§7 deja el seguimiento fuera de alcance); se implementa al
  escribir la spec de seguimiento.

### ~~Hueco de modelo~~ — cerrado: el rechazo de cotización es por componente

> **Resuelto en la spec 002.** Se conserva el análisis original como registro de por qué hizo
> falta una migración. La opción elegida fue la **1 con el matiz de la 3**: `Cotizacion.componente`
> es la clave, y el componente pasó a tener estados propios.

**Regla de negocio:** en un servicio con varios componentes y varias cotizaciones, el cliente
puede rechazar la cotización de un componente. Eso **no** impide que los demás componentes
continúen y **no** finaliza el servicio. El resultado del rechazo aplica solo a ese componente.

**Lo que se verificó en su momento (2026-10-02) y motivó la migración:**

- `Cotizacion.servicio` apuntaba al **servicio**, no al componente. Una cotización cubría el
  servicio entero.
- `DetalleCotizacion` no sabía a qué componente pertenecía cada línea.
- `Componente` **no tenía campo de estado**.
- `NO_APROBADO` era un estado del **servicio**, no del componente, así que a nivel de servicio no
  tenía un significado claro.

**Cómo quedó resuelto** (migración `servicios.0003_componente_por_cotizacion`):

- `Cotizacion.componente` es la clave del rechazo granular. Nulable a propósito: las cotizaciones
  anteriores a la spec 002 eran del servicio entero y siguen siendo válidas (RF-COT-14).
- `Componente` tiene estados propios y `trabajo_iniciado` explícito (D-3, D-4).
- El rechazo marca el componente como `RECHAZADO_BLOQUEANTE` y **no toca el servicio**
  (RF-COT-05, RF-COT-13).
- La cotización sigue siendo del servicio y se puede consultar desde el admin o el seguimiento.

### Tiempo real del cliente — sin decidir

El usuario pidió que el cliente **vea cómo cambia el estado de su componente**. Lo entregado es
RF-COT-15: `ComponentePublicoSerializer` expone `estado` y `fase` en español, y refleja el estado
guardado en cada consulta al enlace de seguimiento.

**Lo que NO está hecho:** que el cambio llegue solo. No hay WebSockets, ni SSE, ni polling. El
cliente ve el estado nuevo al recargar. Elijir el mecanismo es una decisión pendiente:

- *Polling* en el frontend: no añade dependencias, pero son peticiones periódicas.
- *WebSockets / Django Channels*: empuja el cambio, pero **Channels está en la lista de "No
  hacer"** (§3) y sería una dependencia nueva, o sea que exige aprobación explícita.

Mientras no se decida, RF-COT-15 está satisfecha en su forma más simple: el dato está expuesto y
es correcto.

---

## 3. No hacer (fuera del MVP)

No proponer ni implementar sin que el usuario lo pida explícitamente. Detalle completo en
`CONTEXTO_MAESTRO.md` §29 y §40.

- **Arquitectura:** microservicios, Redis, WebSockets, Django Channels, event sourcing, CQRS.
- **Negocio:** carrito, pagos, e-commerce, inventario público, cuenta de cliente para el
  cliente final, app móvil, chat interno, múltiples roles administrativos.
- **Modelo de datos:** `numero_serie`, `subtotal`, impuestos, `fecha_vencimiento`, entidad
  `Entrega`, parámetros rígidos de banco de pruebas.
- **Fuera del MVP pero previsto a futuro** (no descartado, solo aplazado): WhatsApp Business
  API, Google Calendar, envío de correo, PDF de cotizaciones, firma digital.

Regla general: si una de estas hace falta técnicamente, explicar por qué y pedir autorización.

---

## 4. Bitácora

Formato de entrada: fecha, qué se hizo, archivos tocados, decisiones que implicó.

### 2026-10-02 — Línea base documentada

- **No hay historial previo recuperable:** la rama `master` no tiene commits, así que esta
  entrada registra el estado verificado del código, no una reconstrucción de cambios.
- **Backend verificado:** 8 modelos en `servicios/models.py` (Cliente, Servicio, Componente,
  Cotizacion, DetalleCotizacion, AprobacionServicio, HistorialServicio, Fotografia) con sus
  catálogos cerrados como `TextChoices`; `Usuario(AbstractUser)` en `usuarios/models.py`
  añadiendo solo `rol` y `fecha_creacion`.
- **Migraciones:** `servicios` tiene `0001_initial.py` y un `0002_initial.py` que también
  declara `initial = True` y añade las FKs a `Usuario` y entre modelos — resultado de dos
  `makemigrations` seguidos el 2026-09-28. Funciona, pero si hay que revertir conviene
  saber que son dos archivos, no uno.
- **API verificada:** `ClienteViewSet`, `ServicioViewSet` y `CotizacionViewSet` (DefaultRouter)
  más vistas anidadas para componentes, historial, fotografías y aprobaciones. API pública
  en `seguimiento/<token>/` y `seguimiento/<token>/aprobar/`.
- **Django Admin completo** con inlines anidados en Servicio y Cotización.
- **Frontend verificado:** Vite + React 19 + React Router 7 + TanStack Query. `QueryClient`
  ya montado en `main.tsx`, pero sin usar. Rutas en `src/router.tsx`, todo el CSS en un único
  `src/index.css`. Las 8 páginas son placeholders que dicen "contenido por definir".
- **Correcciones de documentación:** `AGENTS.md` apuntaba a `contexto-proyecto.md`, que no
  existía (el archivo real es `CONTEXTO_MAESTRO.md`), y a `.opencode/skills/`, que no
  contiene skills (están en `.agents/skills/`). Ambas corregidas. La misma referencia rota
  estaba en `.agents/skills/hidroemcol-frontend/SKILL.md`.
- **Nota:** `docs/constitution.md` y `specs/` estaban vacíos al momento de escribir esto.
  Ninguno era fuente de verdad.

### 2026-10-02 — Constitución del proyecto

- **`docs/constitution.md` creado** con 6 principios innegociables: stack mínimo, la spec
  manda, el backend decide y la interfaz muestra, tests sin dependencias nuevas, datos del
  cliente solo los suyos, y español en código y pantalla. Pasa a ser el documento de mayor
  jerarquía del repo.
- **Decisión sobre tests:** el agente **propone y pregunta** antes de escribir un test, en
  lugar de hacerlo por iniciativa propia. Si se escriben, solo con `django.test` vía
  `manage.py test`; no se instalan pytest ni dependencias de test. Registrado como regla en
  `AGENTS.md` §5 y como principio 4 de la constitución.
- **Decisión sobre idioma:** se mantiene `LANGUAGE_CODE = 'en-us'` a propósito. Los
  identificadores, comentarios y textos visibles quedan en español; los mensajes que genera
  el framework (errores de validación de DRF, Django Admin) quedan en inglés y eso se
  considera normal, no deuda. No se cambió `settings.py`.
- **`AGENTS.md` actualizado:** la constitución se añadió a la tabla de referencias, se
  corrigió la nota que decía que `docs/constitution.md` estaba vacío, y se añadió la regla
  de tests a la sección de decisiones.

### 2026-10-02 — Especificación de la solicitud en banco de pruebas

- **Spec creada** en `specs/001-solicitud-banco-pruebas/spec.md`: vista pública para registrar
  una solicitud de prueba sin cuenta. 29 RF y 6 RNF en notación EARS, casos límite, fuera de
  alcance, criterios de finalización y 9 dudas abiertas. **No se escribió código.**
- **Nombre de la carpeta:** se pidió `001-heat-map`, que no corresponde a esta funcionalidad.
  Se usa `001-solicitud-banco-pruebas` y el usuario confirmó explícitamente que **no** se
  renombre. No volver a proponer el cambio de nombre.
- **Revisión QA de la spec:** 34 hallazgos detectados, priorizados en bloqueantes, altos,
  medios y bajos. Los 8 bloqueantes eran 4 defectos documentales y 4 decisiones de negocio.
- **Defectos corregidos sin necesidad de preguntar:** RF-5.2 eliminado por no implementable
  (pedía distinguir tipos de prueba sin poder modificar el catálogo); los requisitos de
  privacidad del cliente se movieron a "Fuera de alcance" porque describían la vista de
  seguimiento, conservando allí el criterio de que la visibilidad del cliente se decide dato
  por dato y nunca por omisión; RNF-3 y el criterio 3 ya no exigen español a los errores que
  genera el framework.
- **Cuatro decisiones de negocio tomadas por el usuario:**
  - Obligatorios: descripción de la necesidad y al menos un componente. Opcionales: descripción
    del componente, empresa y fotografías.
  - El aviso de segundo intento se dispara por coincidencia de correo **o** teléfono,
    normalizados sin distinguir mayúsculas, espacios sobrantes ni tildes.
  - El aviso aparece **antes** de registrar; cancelar no deja ninguna solicitud registrada.
  - Solo se fusionan envíos del mismo formulario dentro de un intervalo muy breve; un segundo
    envío posterior cuenta como solicitud nueva. **Superado en la segunda ronda:** esto se
    cambió por un token de idempotencia. La línea de arriba se conserva como registro de lo que
    se decidió entonces, no como lo vigente.
- **Sigue pendiente:** las 9 dudas abiertas de la spec (§9). Las que bloquean la
  implementación son el intervalo de simultaneidad, a qué solicitudes aplica el aviso,
  longitudes máximas de los textos de texto libre, y si el aviso debe ofrecer el enlace de la
  solicitud previa.
- **No se propusieron tests.** Todavía no hay un cambio de código que los justifique; cuando
  lo haya, se propone antes de escribirlo (constitución, principio 4).

### 2026-10-02 — Segunda ronda de decisiones sobre la spec 001

- **Ocho dudas de §9 cerradas y dos abiertas.** Se decidió: el aviso de segundo intento solo
  muestra el mensaje, nunca el enlace previo; se dispara si hay alguna solicitud previa que no
  esté finalizada; 500 caracteres por texto; correo único equivale a misma persona; el aviso al
  administrativo es por panel, y WhatsApp queda para una fase posterior sin descartarse; no hay
  borrado de datos personales; y el doble envío se previene con token de idempotencia en lugar
  de una ventana de tiempo.
- **RF-3 nuevo: preferencia de entrega por casillas.** Tres casillas opcionales, sin lógica de
  transporte. Es el único cambio de esta ronda que **añade un campo al modelo**, así que
  requiere migración y queda anotado aquí según el principio 2 de la constitución.
- **Renumeración de §4:** RF-3 pasa a ser la preferencia de entrega y los antiguos 3 a 9 se
  desplazan a 4 a 10. Verificado que no quedan referencias cruzadas rotas: 35 requisitos,
  numeración contigua.
- **Se corrigieron dos casos límite** que contradecían decisiones ya tomadas (solicitud previa
  cancelada, y texto largo sin tope).
- **§9 quedó con 1 duda:** conservación y derechos de uso de las fotos. La duda sobre si una
  solicitud previa cancelada o entregada debía disparar el aviso se cerró: el aviso solo
  aparece cuando hay algo realmente en curso.
- **Sin cambios en código.** Todo este trabajo es documentación.

### 2026-10-02 — El rechazo de cotización es por componente

- **Nueva regla de negocio:** rechazar la cotización de un componente no impide la continuación
  de los demás componentes ni finaliza el servicio. El resultado aplica solo a ese componente.
- **Verificado en `backend/servicios/models.py` que el modelo actual no puede representarlo:**
  la cotización es del servicio y no del componente, las líneas de la cotización no saben a qué
  componente pertenecen, el componente no tiene campo de estado, y `NO_APROBADO` es un estado
  del servicio.
- **Consecuencia sobre la spec 001:** `NO_APROBADO` salió de la lista de estados cerrados de
  RF-8.6, porque rechazar un componente deja el servicio en marcha. Los estados cerrados quedan
  en tres: finalizado, entregado y cancelado.
- **Queda abierto y sin código:** cómo guardar el resultado por componente. Se documentaron
  tres opciones de modelado en §2. Depende de la decisión del usuario y exige migración.
- **Alerta de proceso:** al insertar esa sección en `MEMORY.md` se destruyó por error el
  encabezado de la sección 3 ("No hacer"); se restauró y se verificó la estructura completa.

### 2026-10-04 — Especificación 002: cotización por componente (cerrada)

Cierra el hueco de modelo que la entrada anterior dejó abierto. **Backend completo, frontend sin
tocar.** 29 tareas, 201 tests en verde, `manage.py check` sin incidencias.

**Migración nueva** (`servicios.0003_componente_por_cotizacion`, principio 2 de la constitución):

- `Cotizacion.componente` (FK nulable a propósito, para no romper las cotizaciones anteriores,
  RF-COT-14).
- `Componente`: `estado` (D-3), `fase`, `trabajo_iniciado` y `fecha_inicio_trabajo` (D-4),
  `fecha_finalizacion` y `motivo_finalizacion` (D-12).
- `Cotizacion.canal` para el medio de la respuesta del cliente.

**Decisiones aplicadas:** D-1 a D-10 del spec y D-11, D-12 del plan.

- D-1 a D-4: la cotización cuelga del componente, declara si bloquea, el componente tiene
  estados propios y el trabajo se inicia con el desmontaje.
- D-5, D-6: criterio **único** de cierre (ningún componente sin finalizar) y cierre manual.
- D-7: un componente con bloqueante rechazada no está finalizado, así que no habilita el cierre.
- D-8: los cierres mal registrados se corrigen con rastro en el historial.
- D-9: la respuesta registra canal, responsable y fecha. **El canal no tiene valor por defecto**
  (RF-COT-03): es un dato de lo que ocurrió, no un valor que se pueda suponer.
- D-10: el sistema no calcula la mano de obra.
- D-11: se reutiliza `AprobacionServicio` en vez de crear un modelo de respuesta paralelo.
- D-12: `fecha_finalizacion` y `motivo_finalizacion` viven en el componente, no se deducen del
  historial.

**Beneficio de la lógica pura en `reglas.py`:** las reglas no dependen de Django ni de la base de
datos, así que la **misma** función decide en la API, en el Django Admin y en los tests. No hay
dos copias de la verdad. Consecuencia práctica de este diseño: cuando se encontró un criterio mal
redactado en `tasks.md` (que pedía que una bloqueante *pendiente* ocultara el botón de cierre),
la corrección estuvo en un test y en un `tasks.md`, **no** en dos implementaciones.

**Interfaz entregada por Django Admin**, sin panel propio:

- `admin.py` con inlines de solo lectura para componentes, cotizaciones, aprobaciones e
  historial. Los estados se muestran calculados y **no se pueden escribir**.
- Acciones de proceso (responder, iniciar desmontaje, finalizar, corregir cierre) que llaman a
  `acciones.py`, o sea, exactamente las mismas reglas que la API.
- Panel de cierre en el servicio: siempre muestra el motivo; el botón solo aparece cuando
  `puede_finalizar` es verdadero. El botón es una cortesía: la garantía está en el backend, que
  vuelve a validar aunque el botón se envíe a mano.
- `FINALIZADO` se quitó del desplegable de estado del servicio: solo la acción de cierre lo
  escribe.

**RF-COT-15** (decisión del usuario durante esta spec): el seguimiento público expone `estado` y
`fase` del componente en español, y oculta los campos de control interno. Lo pendiente de este
requisito está anotado en §2, "Tiempo real del cliente".

**Tests creados** (todos con `manage.py test`, sin dependencias nuevas, principio 4):

- `servicios/tests/test_modelos.py`, `test_reglas.py`, `test_serializers.py`, `test_api.py`,
  `test_admin.py` y `test_recorridos.py`, más `usuarios/tests.py`.

**Un hallazgo sobre el plan:** §6.4 los llama "verificación manual (no automatizable)". No era
cierto: los cuatro recorridos se escribieron como `test_recorridos.py` y se vuelven a pasar solos.
La parte visual sí se comprobó aparte, levantando el servidor contra datos sembrados. **No se
pudo usar el navegador del MCP** porque no encuentra Chrome en la ruta que espera (solo hay
"Chrome Dev" y Edge instalados), así que el HTML del admin se verificó con peticiones reales
contra `runserver`.

**Corrección de alcance en `tasks.md`:** T27 pedía que una cotización bloqueante *pendiente*
ocultara el botón de cierre. Contradecía RF-COT-12 ya decidido (lo pendiente es neutro; lo que
bloquea es que quede un componente sin finalizar). Se corrigió el criterio de la tarea y se
documentó el cambio. El comportamiento implementado y el de RF-COT-12 coinciden.

**La especificación 001 sigue intacta.** No se tocó ningún archivo de `specs/001`, ni sus RF, ni
los tres estados cerrados que se definieron allí (finalizado, entregado, cancelado). `NO_APROBADO`
sigue fuera de esa lista, porque rechazar un componente deja el servicio en marcha.

**La sección "No hacer" sigue intacta.** No se añadió nada a §3. Se deja constancia de que
Channels sigue en esa lista, y por eso el "tiempo real" se pospuso a una decisión explícita.
