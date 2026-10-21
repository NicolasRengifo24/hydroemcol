# Spec 012 — Notificaciones de estado por WhatsApp (mensajes preparados)

**Especificación funcional · Hidroemcol**  
**Estado: aprobada completa**

> Las decisiones tomadas por el usuario están en §10 (y su revisión en §10.1) y no se reabren
> aquí. Las aclaraciones resueltas se resumen en §13.

## 1. Contexto y objetivo

Cuando el administrativo cambia el estado de un componente o de un servicio, hoy el cliente se
entera preguntando por WhatsApp o por teléfono, y la empresa repite por mensaje información que
el sistema ya tiene. `CONTEXTO_MAESTRO.md` §11 a §13 fija el marco: WhatsApp es un puente de
comunicación, el seguimiento web es la fuente oficial y, en el MVP, el sistema puede generar
mensajes preparados. La automatización completa (WhatsApp Business API) queda para una fase
posterior.

**Objetivo:** tras cada cambio de estado con texto aprobado en un servicio abierto, el administrativo dispone
de un mensaje preparado con el estado, el componente o servicio y el enlace de seguimiento. Lo
revisa, puede editarlo y lo envía él mismo desde su WhatsApp al número que el cliente registró.

**Por qué:** el cliente sabe lo que pasa sin tener que preguntar ni recargar la página, y la
empresa deja de redactar el mismo aviso a mano. Como no hay API, el sistema no garantiza que el
mensaje llegue: lo envía el administrativo, y el sistema no lo presenta como enviado.

## 2. Relación con especificaciones anteriores

Esta especificación añade un canal de comunicación sobre los eventos que ya existen. Hace una
excepción explícita a una cláusula de la 001 (ver el primer punto).

- **001 (solicitud):** el formulario pide teléfono o WhatsApp (al menos uno) (RF-2.1). **Esta
  spec supera esa regla para el número de WhatsApp: pasa a ser obligatorio en la solicitud**
  (decisión R6). El teléfono conserva su regla actual. Sigue vigente la normalización del
  teléfono para el aviso de duplicados (RF-8), que no se altera (ver §12).
- **002, 008 y 011 (estados y cotizaciones):** esta spec **consume** los cambios de estado tal
  como las transiciones de §4.1 y §4.2 de la 008 y la 011 los definen. No crea, ni altera,
  transiciones ni catálogos. Los textos aprobados usan los nombres de estado de 008 §4.4.
- **004, 005 y 006 (panel):** el botón de envío y la sección WhatsApp se añaden al panel
  administrativo. No cambia las acciones de estado ni sus reglas. Un servicio desactivado
  (`activo=False`, 006) no recibe mensaje (RF-WA-28).
- **007 (seguimiento):** el enlace de los mensajes es el enlace privado de seguimiento. Aplica la
  misma regla de privacidad: solo datos que el cliente puede ver (RF-SEG-03). Las respuestas del
  cliente desde el seguimiento no generan mensaje (RF-WA-27).
- **010 (registro de recepción):** registrar la recepción lleva el servicio de `SOLICITADO` a
  `EN_CURSO`; ese cambio, hecho por el administrativo, genera el texto de `EN_CURSO` (ver §4.1).
- **`CONTEXTO_MAESTRO.md` §43:** deja como pendiente el "formato definitivo de mensajes de
  WhatsApp". Esta spec lo fija con los textos aprobados. RF-WA-26 exige actualizar el contexto.
- **Constitución:** principios 1 (stack mínimo), 3 (el backend decide, la interfaz muestra), 4
  (tests con `django.test` y aprobación previa), 5 (datos del cliente solo los suyos) y 6
  (español en pantalla).

## 3. Usuarios

| Usuario | Descripción |
|---|---|
| **ADMINISTRATIVO** | Único rol del panel. Cambia estados, revisa el mensaje, lo edita y abre WhatsApp para enviarlo. |
| **Cliente** | Recibe el mensaje en su WhatsApp. No usa el panel, no obtiene textos y no responde por esta vía. |
| **Visitante sin datos** | No obtiene ningún mensaje ni número. |

## 4. Glosario

- **Número de WhatsApp:** celular colombiano de 10 dígitos que empieza por 3, guardado sin el
  prefijo +57 en `Cliente.whatsapp` (RF-WA-02, RF-WA-01).
- **Enlace de seguimiento:** dirección pública del servicio con su token privado (007, §5).
- **Evento de notificación:** cambio de estado de un componente o de un servicio que tiene un
  texto aprobado en §4.1, que hace el ADMINISTRATIVO desde el panel (incluida una aprobación registrada a mano), que queda guardado y que
  ocurre en un servicio abierto (no `FINALIZADO` ni `CANCELADO`, P4) (RF-WA-27).
- **Mensaje preparado:** texto generado para un evento de notificación. Se muestra al
  administrativo para revisarlo y editarlo. No se envía desde el sistema.
- **Abrir WhatsApp:** acción del administrativo que abre una pestaña nueva de WhatsApp con el
  número del cliente y el texto. **No implica envío** (decisión 1 original).
- **Servicio desactivado:** servicio con `activo=False` (006, glosario).
- **Cambio manual / automático:** definidos en 008 (§4). Un cambio automático no genera mensaje
  (RF-WA-27).

### 4.1 Textos aprobados

Se usan exactamente como están. Variables: `{codigo}`, `{componente}`, `{estado}`, `{fecha}`,
`{enlace}`, `{motivo}`. La variable `{estado}` no aparece en ningún texto aprobado y no se usa.

**Componente**

| Estado del componente | Texto aprobado | Disparador hoy |
|---|---|---|
| `PENDIENTE` | Hidroemcol: el componente {componente} del servicio {codigo} fue recibido. | Sin disparador: ningún cambio llega a `PENDIENTE` (DA-04). |
| `EN_REVISION` | Hidroemcol: el componente {componente} del servicio {codigo} está en revisión. | Manual, desde `PENDIENTE`. |
| `COTIZANDO` | Hidroemcol: estamos preparando la cotización de {componente} (servicio {codigo}). | Sin disparador: la cotización no pasa por este estado (DA-04). |
| `ESPERANDO_APROBACION` | Hidroemcol: {componente} (servicio {codigo}) espera su aprobación. Revise la cotización en: {enlace} | Manual: al crear una cotización (sí genera) y al reenviar un componente `RECHAZADO`. Editar y rechazar la cotización: no genera. Aprobar: solo si cambia el estado del componente (RF-WA-09). |
| `OPERARIO_TRABAJANDO` | Hidroemcol: iniciamos el trabajo en {componente} (servicio {codigo}). | Manual, desde `EN_REVISION`. Aprobación registrada a mano por el administrativo: genera si cambia el estado (RF-WA-09). Aprobación del cliente o automática: no genera (RF-WA-27). |
| `EN_PRUEBAS` | Hidroemcol: {componente} (servicio {codigo}) está en pruebas. | Manual, desde `OPERARIO_TRABAJANDO`; corrección desde `LISTO_PARA_ENTREGA`. |
| `LISTO_PARA_ENTREGA` | Hidroemcol: {componente} (servicio {codigo}) está listo para entregar. | Manual, finalización con motivo y fecha. |
| `RECHAZADO` | Hidroemcol: {componente} (servicio {codigo}) fue rechazado. Motivo: {motivo}. Detalle: {enlace} | Manual, finalización con motivo y fecha. |

**Servicio**

| Estado del servicio | Texto aprobado | Disparador hoy |
|---|---|---|
| `SOLICITADO` | Hidroemcol: recibimos su solicitud {codigo}. Siga el avance en: {enlace} | Sin disparador: ninguna transición llega a `SOLICITADO` (DA-04). |
| `EN_CURSO` | Hidroemcol: su servicio {codigo} está en curso. Siga el avance en: {enlace} | Manual: al registrar la recepción (010). Automático al salir el primer componente de `PENDIENTE`: no genera (RF-WA-27). |
| `FINALIZADO` | Hidroemcol: su servicio {codigo} fue finalizado el {fecha}. Detalle: {enlace} | Manual, finalizar servicio. Sin botón (P4). |
| `CANCELADO` | Hidroemcol: su servicio {codigo} fue cancelado. Consulte: {enlace} | Manual, cancelar servicio (con comentario obligatorio). Sin botón (P4). |

Los textos aprobados conservan su redacción. Resuelto (P2): se mantiene usted en los textos
aprobados y tú en la interfaz.

`FINALIZADO` y `CANCELADO` conservan su texto aprobado, pero no tienen botón de envío: mientras el
servicio esté cerrado no se prepara mensaje para ellos ni para sus componentes (P4).

### 4.2 Textos de interfaz aprobados

Definidos en tono de tú, para la interfaz (principio 6 y RNF-WA-06). Los RF citados usan estos
textos aprobados.

| Caso | Texto aprobado | Dónde aparece |
|---|---|---|
| Servicio cerrado sin botón (aviso al administrativo) | Este servicio está cerrado. No se preparan mensajes para él ni para sus componentes. | Sección WhatsApp del detalle (RF-WA-15, RF-WA-19) |
| Campo WhatsApp vacío en el registro | Indica tu número de WhatsApp. Lo usaremos para avisarte del avance de tu servicio. | Formulario de solicitud (RF-WA-03) |
| Número inválido en el registro | Escribe un celular colombiano de 10 dígitos que empiece por 3. | Formulario de solicitud (RF-WA-02) |
| Cliente sin número en el panel | Este cliente no tiene un número de WhatsApp registrado. No se preparó el mensaje. | Sección WhatsApp del detalle (RF-WA-21) |
| Falta `SEGUIMIENTO_BASE_URL` | No está configurado el dominio de los enlaces de seguimiento. Pide a quien administra el sistema que lo configure. No se preparó el mensaje. | Sección WhatsApp del detalle (RF-WA-29) |
| Sesión caducada | Tu sesión ha caducado. Vuelve a entrar: tu mensaje seguirá en el campo. | Pantalla de acceso (RF-WA-31) |
| Campo de texto del mensaje vacío | Escribe el mensaje antes de abrir WhatsApp. | Junto al campo de texto vacío (CL-09, RF-WA-16) |
| Aviso tras abrir WhatsApp | Se abrió WhatsApp con el mensaje. Envíalo desde WhatsApp: el sistema no confirma la entrega. | Después de abrir WhatsApp (RF-WA-18) |

## 5. Alcance

**Incluye**

- Captura y validación del número de WhatsApp en el formulario de solicitud, obligatorio.
- Preparación del mensaje para cada evento de notificación de componente y de servicio con texto
  aprobado, en servicios abiertos, cuando lo hace el administrativo desde el panel.
- Sección "WhatsApp" en el detalle del servicio, con una tarjeta por evento: texto preparado,
  edición y apertura de WhatsApp en pestaña nueva.
- Endpoint nuevo de solo lectura que devuelve el texto preparado.
- Tratamiento de los fallos: sin número, mensaje no preparable, ventana bloqueada, servicio
  desactivado, dominio no configurado y sesión caducada.

**No incluye:** ver §11.

## 6. Requisitos funcionales (EARS)

### Número de WhatsApp en la solicitud

#### RF-WA-01 — Captura del número

**WHEN** el cliente envía una solicitud con un número de WhatsApp **THEN** el sistema DEBE
guardarlo en el campo WhatsApp del cliente (`Cliente.whatsapp`, ya existente) solo si el cliente no tiene número guardado (RF-WA-04), sin prefijo +57 y
solo con dígitos. El número no se guarda en ningún otro campo ni se usa el teléfono para
mensajes. No requiere migración (decisión R6).

#### RF-WA-02 — Validación del número

**WHEN** se recibe un número de WhatsApp **THEN** el sistema DEBE aceptarlo solo si, tras quitar
espacios, guiones, paréntesis y el prefijo `+57` o `57`, quedan exactamente 10 dígitos y el
primero es 3.

**IF** el número no cumple **THEN** el sistema DEBE rechazar la solicitud con un mensaje en
español que indique el formato esperado (texto de §4.2, caso número inválido), sin crear cliente, servicio ni componentes.

#### RF-WA-03 — Solicitud sin número de WhatsApp válido

**IF** la solicitud llega sin número de WhatsApp o con uno que no cumple RF-WA-02 **THEN** el
sistema DEBE rechazarla con el texto de §4.2 (campo vacío o número inválido), sin crear cliente, servicio ni componentes.
El número es obligatorio (decisión R6). El teléfono no sustituye al WhatsApp.

#### RF-WA-04 — Número en clientes ya registrados

**WHEN** una solicitud trae un número de WhatsApp válido para un cliente que ya existe **THEN**
el sistema NO DEBE sobrescribir nunca el número ya guardado en `Cliente.whatsapp`, por ninguna
solicitud ni flujo (decisiones R2 y P5). La solicitud se registra según la 001. La corrección de
un número ya guardado se hace a mano en Django Admin (fuera del alcance del panel), sin
migraciones de datos.

**IF** el cliente existente no tiene número de WhatsApp registrado **THEN** el sistema DEBE
guardar en `Cliente.whatsapp` el número válido de la solicitud (decisión P5). Se considera que no
tiene número cuando el campo está vacío. Si ya tiene uno, aunque no cumpla RF-WA-02, no se
sobrescribe (CL-22, CL-24).

### Generación del mensaje

#### RF-WA-05 — Eventos de componente

**WHEN** el ADMINISTRATIVO cambia desde el panel el estado de un componente de un servicio abierto a un estado con
texto aprobado y el cambio queda guardado **THEN** el sistema DEBE preparar el mensaje de ese
estado para ese componente.

**AND** las cotizaciones se rigen por RF-WA-09.

#### RF-WA-06 — Eventos de servicio

**WHEN** el ADMINISTRATIVO cambia desde el panel el estado de un servicio abierto (no `FINALIZADO` ni `CANCELADO`, P4) a un estado con texto
aprobado y el cambio queda guardado **THEN** el sistema DEBE preparar el mensaje de ese estado
para el servicio. Los cambios automáticos no generan mensaje (RF-WA-27).

#### RF-WA-07 — Cobertura

**WHEN** se produce un evento de notificación **THEN** el sistema DEBE tratarlo igual sin importar
el tipo de servicio ni el número de componentes del servicio.

#### RF-WA-08 — Sin evento, sin mensaje

**IF** un cambio no queda guardado (validación, regla de negocio, conflicto `409`), o se pide el
mismo estado que ya tiene el recurso **THEN** el sistema NO DEBE preparar mensaje ni ofrecer el
botón de envío.

#### RF-WA-09 — Cotizaciones

**WHEN** el ADMINISTRATIVO crea una cotización **THEN** el sistema DEBE preparar el mensaje
`ESPERANDO_APROBACION` del componente (decisión R10).

**WHEN** el ADMINISTRATIVO edita o rechaza una cotización **THEN** el sistema NO DEBE preparar
mensaje.

**WHEN** el ADMINISTRATIVO registra desde el panel la aprobación de una cotización **THEN** el sistema DEBE preparar mensaje solo
si esa aprobación cambia el estado del componente, según RF-WA-05.

#### RF-WA-10 — Contenido fijo

**WHEN** el sistema prepara un mensaje **THEN** DEBE usar exactamente el texto aprobado de §4.1,
sustituyendo sus variables, en una sola línea, sin emojis ni texto adicional.

#### RF-WA-11 — Variables

**WHEN** el sistema sustituye las variables **THEN** DEBE usar:

- `{codigo}`: código humano del servicio (`SRV-…`).
- `{componente}`: tipo del componente y su referencia entre paréntesis (P1, opción b, resuelta). Si el componente no tiene referencia, solo el tipo (A3).
- `{enlace}`: enlace absoluto de seguimiento del servicio (`/seguimiento/:token`), con el token
  de ese servicio. La base del dominio viene de la variable de RF-WA-29.
- `{fecha}`: fecha de finalización del servicio en formato día/mes/año. Se guarda en UTC y se
  muestra en la zona America/Bogota **solo en este mensaje**; la zona de la aplicación no cambia
  (decisión R13). Mientras P4 esté vigente, ningún mensaje disponible usa `{fecha}`.
- `{motivo}`: el motivo que el ADMINISTRATIVO escribió al finalizar el componente como
  `RECHAZADO`. Se usa tal cual, sin cambios (decisión R1). Solo se usa en `RECHAZADO`; ningún otro texto lo incluye (P3).

#### RF-WA-12 — Privacidad del contenido

**WHEN** el sistema prepara un mensaje **THEN** DEBE incluir solo el código, el nombre del
componente, el enlace de seguimiento y, cuando el texto lo pida, la fecha o el motivo.

**AND** el mensaje NO DEBE incluir observaciones internas, motivos de bloqueo, detalle de
cotizaciones, nombres de usuarios administrativos, identificadores internos ni el token fuera del
enlace. Lo que el cliente puede ver es lo que ya autoriza el seguimiento público (007, RF-SEG-03).

**Excepción aprobada:** el `{motivo}` de `RECHAZADO` se incluye tal cual (decisión R1), aunque
el motivo se registra como campo interno. La excepción no amplía ningún otro dato y solo aplica a `RECHAZADO` (P3).

#### RF-WA-13 — Enlace funcional

**WHEN** el mensaje incluye `{enlace}` **THEN** el enlace DEBE apuntar al seguimiento del mismo
servicio, con el token de ese servicio, y DEBE mostrar datos solo de ese servicio (007, RNF-SEG-04).

#### RF-WA-14 — Generar el mensaje no escribe datos

**WHEN** el sistema prepara o muestra un mensaje **THEN** NO DEBE modificar ningún dato del
servicio, del componente ni de la cotización, ni crear registros de historial.

### Panel administrativo

#### RF-WA-15 — Sección WhatsApp del detalle del servicio

**WHEN** el ADMINISTRATIVO abre el detalle de un servicio abierto con número de WhatsApp válido **THEN**
el panel DEBE mostrar una sección "WhatsApp" con una tarjeta por evento de notificación vigente
(un componente o el servicio, en su estado actual, si su estado tiene texto aprobado). Si el servicio está `FINALIZADO` o `CANCELADO`, la sección muestra solo el aviso de §4.2 y no muestra tarjetas ni botones (P4). Cada
tarjeta muestra el texto preparado y un botón para abrir WhatsApp con ese texto (decisión R11).

#### RF-WA-16 — Edición antes de abrir

**WHEN** el administrativo ve el mensaje preparado **THEN** DEBE poder editarlo en un campo de
una sola línea (decisión R13), y al pulsar el botón DEBE abrirse el texto tal como quedó editado.

**IF** el texto editado está vacío o solo tiene espacios **THEN** el panel NO DEBE abrir WhatsApp
y DEBE indicarlo junto al campo.

#### RF-WA-17 — Apertura en pestaña nueva

**WHEN** el administrativo pulsa el botón **THEN** el sistema DEBE abrir en una pestaña nueva un
enlace de WhatsApp con el número del cliente con prefijo 57 y el texto editado codificado para la
URL, de modo que los acentos, la ñ y los saltos de línea se vean bien al abrir. El enlace se
construye en el clic, no antes (decisión R11).

#### RF-WA-18 — Sin afirmar envío

**WHEN** se abre WhatsApp **THEN** el panel NO DEBE indicar que el mensaje fue enviado ni guardar
ningún estado de envío. DEBE indicar que el envío lo hace el administrativo desde WhatsApp y que
el sistema no confirma la entrega.

#### RF-WA-19 — Disponibilidad del botón

**WHEN** el estado vigente de un componente o de un servicio tiene texto aprobado y el servicio está
abierto (no `FINALIZADO` ni `CANCELADO`) **THEN** el botón DEBE estar siempre disponible para ese
estado, también al recargar el panel y con independencia del origen del cambio (decisiones R3 y A1). El texto corresponde siempre al estado vigente.

**AND** si el servicio está `FINALIZADO` o `CANCELADO`, ni el servicio ni sus componentes tienen
botón de mensaje (P4, revisado por el usuario), y la sección muestra solo el aviso de §4.2.

#### RF-WA-20 — Acceso

**WHEN** se pide un mensaje preparado **THEN** el backend DEBE exigir un ADMINISTRATIVO autenticado
y activo. Un cliente, un usuario no autenticado o una cuenta inactiva DEBE recibir rechazo sin
datos.

### Fallos y cómo se muestran

#### RF-WA-21 — Servicio sin número

**WHEN** el servicio no tiene número de WhatsApp válido **THEN** el cambio de estado queda
guardado, el panel NO DEBE mostrar el botón de abrir WhatsApp y DEBE mostrar el texto de §4.2 (caso cliente sin número).

#### RF-WA-22 — Mensaje no preparable

**IF** el mensaje no se puede preparar (el servidor no responde, hay un error interno, o no se
puede construir el enlace) **THEN** el panel DEBE mostrar: "No se pudo preparar el mensaje.
Inténtalo de nuevo.", con un botón de reintento, NO DEBE abrir WhatsApp, y el cambio de estado
DEBE quedar tal como se guardó.

#### RF-WA-23 — Ventana bloqueada por el navegador

**IF** el navegador impide abrir la pestaña de WhatsApp **THEN** el panel DEBE mostrar: "El
navegador bloqueó la ventana de WhatsApp. Permite las ventanas emergentes para este sitio y pulsa
de nuevo el botón.", y DEBE conservar el texto editado para que no se pierda.

El texto se prepara al mostrar el panel y la ventana se abre directamente en el clic, sin una
petición previa al servidor (decisión R11).

#### RF-WA-24 — Ningún fallo revierte el cambio

**WHEN** falla cualquier parte de la preparación o del envío del mensaje **THEN** el cambio de
estado del componente o del servicio NO DEBE revertirse ni quedar bloqueado (decisión 5 original).

#### RF-WA-25 — Mensajes accesibles

**WHEN** el panel muestra un aviso o un error de este flujo **THEN** DEBE anunciarlo de forma
accesible, con texto, sin depender del color (RNF-WA-05).

### Documentación

#### RF-WA-26 — Contexto actualizado antes de aprobar

**WHEN** esta spec quede aprobada para implementación **THEN** DEBEN actualizarse
`CONTEXTO_MAESTRO.md` §43 (formato de mensajes) con los textos de §4.1, y `MEMORY.md` debe registrar
la decisión. **IF** alguna de las dos no está hecha **THEN** la spec NO DEBE considerarse lista
para implementar (mismo criterio que RF-FLU-17 de la 008).

### Requisitos añadidos por la revisión (decisiones R4, R7, R9, R5, R13)

#### RF-WA-27 — Origen del cambio

**WHEN** el ADMINISTRATIVO cambia desde el panel React el estado de un componente o de un servicio,
o registra desde el panel una aprobación (RF-WA-09) **THEN** el sistema DEBE preparar el mensaje de
evento de ese estado, si cumple los demás requisitos (decisiones R4 y A2).

**WHEN** un cambio de estado llega desde la respuesta del cliente en el seguimiento, desde el
Django Admin, o es automático **THEN** el sistema NO DEBE preparar mensaje de evento para él.

**AND** en todos los casos, mientras el servicio esté abierto, el panel DEBE mostrar el botón del
texto del estado vigente (RF-WA-19). Ese botón solo reabre el texto preparado: no genera un mensaje
nuevo ni registra un envío (decisión A1).

#### RF-WA-28 — Servicio desactivado

**IF** el servicio tiene `activo=False` **THEN** el sistema NO DEBE preparar mensaje ni ofrecer
el botón, y el panel DEBE mostrar: "Este servicio está desactivado. No se preparó el mensaje."
(decisión R9).

#### RF-WA-29 — Dominio del enlace

**WHEN** se prepara un texto con `{enlace}` **THEN** la base del dominio DEBE leerse de una
variable de entorno en la configuración del backend. El valor de producción no se fija en el
código ni en esta spec (decisión R7).

**IF** la variable no está definida **THEN** el sistema NO DEBE preparar los textos con
`{enlace}` ni generar un enlace parcial, y el panel DEBE avisar al ADMINISTRATIVO con el texto de §4.2 (caso falta el dominio de seguimiento). Los textos sin
`{enlace}` se preparan igual.

#### RF-WA-30 — Lectura del texto preparado

**WHEN** el panel muestra un recurso de un servicio abierto cuyo estado vigente tiene texto aprobado **THEN** el texto
se obtiene de un endpoint nuevo de solo lectura (decisión R5), que lo prepara en ese momento
(decisión R11).

**AND** el endpoint DEBE responder solo a un ADMINISTRATIVO autenticado y activo (RF-WA-20), NO
DEBE escribir datos (RF-WA-14) y, si no puede preparar el texto, DEBE indicar la causa (RF-WA-21,
RF-WA-22, RF-WA-28 o RF-WA-29).

#### RF-WA-31 — Sesión caducada

**WHEN** la sesión del ADMINISTRATIVO caduca mientras edita un mensaje **THEN** el panel DEBE
redirigir a la pantalla de acceso con el texto de §4.2 y, tras volver a entrar, DEBE conservar el texto editado
(decisión R13).

## 7. Requisitos no funcionales (EARS)

- **RNF-WA-01 — Sin integraciones ni dependencias.** La solución NO DEBE usar la API de WhatsApp,
  credenciales, envío automático ni dependencias nuevas (constitución, principio 1; decisión 1
  original).
- **RNF-WA-02 — Sin modelo nuevo de datos y sin migraciones.** La solución NO DEBE crear tablas,
  historial de mensajes ni migraciones (decisiones 8 original y R2). Cualquier cambio de esquema
  requiere aprobación previa y su migración.
- **RNF-WA-03 — El backend decide.** El texto, la validez del número y la elegibilidad de un
  evento se resuelven en el backend. La interfaz muestra y abre; no decide qué texto ni qué número
  corresponden (constitución, principio 3).
- **RNF-WA-04 — Privacidad.** El token aparece en los mensajes solo como parte del enlace y en la
  URL de WhatsApp al hacer clic. Ese riesgo está aceptado y documentado en §12 (decisión R8). Los
  textos preparados NO DEBEN quedar registrados en logs del servidor.
- **RNF-WA-05 — Accesibilidad y responsive.** El botón, el editor del mensaje y los avisos DEBEN
  tener nombre accesible, foco visible, anuncio de error y objetivos táctiles de al menos 44 px. El
  flujo DEBE funcionar sin desplazamiento horizontal en 375 px, 768 px y 1280 px.
- **RNF-WA-06 — Idioma y tratamiento.** Los textos visibles y los avisos DEBEN estar en español
  (principio 6). Los avisos y mensajes del panel usan el tratamiento de tú (decisión R13). El
  tratamiento de los textos aprobados se mantiene de usted (P2, confirmado).
- **RNF-WA-07 — Verificación.** Solo se escriben con `django.test` las pruebas aprobadas en la
  decisión R12: CA-02 (validación del número), CA-15 (no escritura), CA-14 (permisos), CA-12
  (contenido del mensaje) y CA-06 (409 y mismo estado). El resto se verifica en el navegador con
  el número de prueba del usuario, nunca con un cliente real.

## 8. Casos límite

- **CL-01 — Número con formato libre.** Entrada `+57 300 123 4567` o `57-300-123-4567`: se acepta
  y se guarda como `3001234567` si el cliente no tiene número guardado (RF-WA-04).
- **CL-02 — Número no válido.** Fijo (`6011234567`), 9 dígitos, 11 dígitos o empezado por otro
  dígito: se rechaza con mensaje y no se crea nada.
- **CL-03 — Servicio sin número.** Solo en clientes sin número guardado (clientes antiguos que no han vuelto a solicitar, RF-WA-04, P5) o cuyo número guardado no cumple RF-WA-02, que nunca se sobrescribe (CL-24). El cambio queda
  guardado, el panel muestra el aviso de RF-WA-21 y no hay botón.
- **CL-04 — Cambios seguidos.** El administrativo cambia tres componentes seguidos: cada cambio
  tiene su propio mensaje; no se combinan en uno.
- **CL-05 — Mismo estado.** Se pide el estado que el recurso ya tiene: no hay mensaje (RF-WA-08).
- **CL-06 — Cambio rechazado.** Una transición no permitida o un `409` no genera mensaje (RF-WA-08).
- **CL-07 — Falla al preparar.** El cambio se queda guardado y el panel muestra el error de RF-WA-22
  con reintento.
- **CL-08 — Ventana bloqueada.** Se muestra el aviso de RF-WA-23 y el texto editado se conserva.
- **CL-09 — Texto editado vacío.** No se abre WhatsApp y se indica junto al campo (RF-WA-16).
- **CL-10 — Caracteres especiales en el texto editado.** Acentos, ñ, emojis y saltos de línea se
  codifican bien al abrir.
- **CL-11 — Reabrir con el estado actual.** Al recargar el panel, el botón sigue disponible para el
  estado vigente de un servicio abierto y el texto corresponde a ese estado (RF-WA-19, P4).
- **CL-12 — Motivo largo.** El motivo es texto libre sin tope y se usa tal cual (decisión R1). El
  mensaje puede quedar largo y no se corta.
- **CL-13 — Cierre de un componente con motivo vacío.** No es posible: la finalización exige
  motivo. Si el motivo llega vacío por otra vía, el mensaje no se prepara (RF-WA-22).
- **CL-14 — Cancelación de un servicio.** El cambio queda guardado y no hay botón de mensaje para
  `CANCELADO` ni para sus componentes (RF-WA-19, P4).
- **CL-15 — Respuesta del cliente a una cotización.** Aprobar o rechazar desde el enlace de
  seguimiento no genera mensaje (RF-WA-27).
- **CL-16 — Usuario sin permiso.** Un cliente o una cuenta inactiva que pide un texto recibe rechazo
  sin datos (RF-WA-20).
- **CL-17 — Cotización creada.** Genera `ESPERANDO_APROBACION` (RF-WA-09).
- **CL-18 — Cotización editada o rechazada.** No genera mensaje (RF-WA-09).
- **CL-19 — Cambio automático.** `EN_CURSO` automático o `OPERARIO_TRABAJANDO` por aprobación del
  cliente no generan mensaje (RF-WA-27).
- **CL-20 — Servicio desactivado.** No hay mensaje ni botón; el panel muestra el aviso de RF-WA-28.
- **CL-21 — Dominio sin configurar.** Los textos con `{enlace}` no se preparan y el panel avisa
  (RF-WA-29).
- **CL-22 — Cliente existente con otro número.** Una solicitud con un número válido distinto no
  sobrescribe el número guardado (RF-WA-04).
- **CL-23 — Sesión caducada.** Al volver a entrar, el texto editado sigue en el campo (RF-WA-31).
- **CL-24 — Cliente con número guardado distinto.** El cliente tiene el número A guardado y llega una
  solicitud nueva con el número B válido: se conserva A y el mensaje se envía a A (RF-WA-04, P5). Si A
  no cumple RF-WA-02 (cliente antiguo), tampoco se sobrescribe; si A no es válido, aplica RF-WA-21.

## 9. Criterios de aceptación

Se verifican en el navegador con datos reales y el número de prueba del usuario, salvo CA-02,
CA-06, CA-12, CA-14 y CA-15, que se verifican con `django.test` (decisión R12), y CA-18.

- **CA-01.** Los formatos `3001234567`, `+57 300 123 4567` y `57-300-123-4567` se guardan como
  `3001234567` en `Cliente.whatsapp` si el cliente no tenía número (RF-WA-01, RF-WA-02, RF-WA-04).
- **CA-02.** `6011234567`, un número de 9 u 11 dígitos y uno que no empieza por 3 se rechazan con
  mensaje claro, sin crear cliente, servicio ni componentes (RF-WA-02, RF-WA-03). *[django.test]*
- **CA-03.** Cada cambio de componente que tiene texto aprobado (ver §4.1) hecho desde el panel en un servicio abierto
  produce el texto exacto con sus variables (RF-WA-05, RF-WA-10, RF-WA-11).
- **CA-04.** Cada cambio de servicio que tiene texto aprobado produce el texto exacto en servicios abiertos:
  `EN_CURSO` al registrar recepción. `FINALIZADO` y `CANCELADO` no muestran botón (P4). El `EN_CURSO`
  automático no genera mensaje (RF-WA-06, RF-WA-19, RF-WA-27).
- **CA-05.** Crear una cotización produce `ESPERANDO_APROBACION`. Editar o rechazar no produce
  mensaje. Aprobar, registrada a mano por el administrativo, solo produce mensaje si cambia el estado del componente (RF-WA-09).
- **CA-06.** Un cambio rechazado, un `409` o pedir el mismo estado no muestran mensaje
  (RF-WA-08). *[django.test]*
- **CA-07.** El botón abre una pestaña nueva con WhatsApp dirigido a `57` más el número, y el texto
  se lee correctamente con acentos (RF-WA-17).
- **CA-08.** Si el administrativo edita el texto antes de abrir, se abre el texto editado
  (RF-WA-16).
- **CA-09.** Con un servicio sin número, el cambio queda guardado, aparece el aviso y no hay botón
  (RF-WA-21).
- **CA-10.** Si la preparación del mensaje falla, aparece el error con reintento, no se abre
  WhatsApp y el cambio sigue guardado (RF-WA-22, RF-WA-24).
- **CA-11.** Con la ventana bloqueada, aparece el aviso y el texto editado se conserva (RF-WA-23).
- **CA-12.** Los textos generados contienen solo los datos permitidos: no aparecen observaciones
  internas, motivos de bloqueo, usuarios ni identificadores (RF-WA-12). *[django.test]*
- **CA-13.** El enlace del mensaje abre el seguimiento del mismo servicio y no muestra datos de otro
  (RF-WA-13).
- **CA-14.** Un cliente o un usuario no autenticado no obtiene textos preparados (RF-WA-20).
  *[django.test]*
- **CA-15.** Preparar o abrir un mensaje no crea ni modifica filas en la base de datos (RF-WA-14,
  RNF-WA-02). *[django.test]*
- **CA-16.** El flujo funciona sin desplazamiento horizontal en 375, 768 y 1280 px, sin errores de
  consola, con foco visible y avisos accesibles (RNF-WA-05).
- **CA-17.** `CONTEXTO_MAESTRO.md` §43 y `MEMORY.md` están actualizados (RF-WA-26).
- **CA-18.** Las pruebas `django.test` de CA-02, CA-06, CA-12, CA-14 y CA-15 pasan con
  `manage.py test`, junto con las pruebas de backend existentes (constitución, principio 4).
- **CA-19.** Una respuesta del cliente desde el seguimiento, un cambio desde el Django Admin o un
  cambio automático no producen mensaje de evento; el botón del estado vigente sí aparece (RF-WA-19, RF-WA-27).
- **CA-20.** Un servicio con `activo=False` no muestra mensaje ni botón y el panel muestra el aviso
  de RF-WA-28.
- **CA-21.** Sin la variable de dominio, los textos con `{enlace}` no se preparan y el panel avisa
  al administrativo (RF-WA-29).
- **CA-22.** Con la sesión caducada, el panel lleva a la pantalla de acceso y, al volver a entrar,
  el texto editado sigue en el campo (RF-WA-31).
- **CA-23.** Una solicitud sin número de WhatsApp válido se rechaza, y una solicitud con número
  válido para un cliente existente no cambia el número guardado, y si el cliente no tenía número se guarda el de la solicitud; el mensaje va al número guardado (RF-WA-03, RF-WA-04, CL-24).

## 10. Decisiones tomadas por el usuario (preservadas)

1. **Opción C.** Sin API de WhatsApp, sin librerías nuevas, sin credenciales y sin modelo nuevo.
   El backend genera el texto; el panel abre el enlace de WhatsApp en pestaña nueva. El
   administrativo revisa y envía. No hay envío automático ni confirmación de entrega.
2. **Disparo manual.** El envío se dispara con un botón del panel tras el cambio de estado; no es
   automático.
3. **Alcance de eventos.** Se notifican los cambios de estado de componente (8) y de servicio (4)
   que hace el administrativo desde el panel (ver R4). Las cotizaciones no generan mensaje, salvo
   la creación (ver R10).
4. **Contenido.** Cada mensaje incluye el enlace de seguimiento web (`/seguimiento/:token`) y es
   de una línea, corto.
5. **Número.** Se captura y valida en el registro de la solicitud. Solo celulares colombianos de 10
   dígitos que empiezan por 3, guardados sin +57. Ya no es opcional: ver R6. Sin número en un
   cliente existente, se omite el mensaje y el cambio de estado NO se bloquea.
6. **Edición.** El administrativo puede editar el texto antes de enviarlo.
7. **Fallos.** Se muestran al administrativo: sin número, texto no preparable y ventana bloqueada
   (RF-WA-21 a RF-WA-23).
8. **Sin historial.** No se guarda historial de mensajes en la base de datos.
9. **Pruebas.** Solo las pruebas `django.test` de R12. El resto es verificación manual con el MCP
   de navegador y el número de prueba del usuario.

Textos de §4.1 aprobados tal cual.

### 10.1 Decisiones de la revisión (2026-10-20)

- **R1.** `{motivo}` de `RECHAZADO` se usa tal cual; el cliente sí puede verlo (decisión de negocio).
  El texto de `LISTO_PARA_ENTREGA` no contiene `{motivo}` (P3, confirmado).
- **R2.** Nunca se sobrescribe el número guardado de un cliente existente, por ninguna vía (P5); se corrige a mano en Django Admin.
  Sin migraciones.
- **R3.** El botón de mensaje está siempre disponible para el estado vigente de los estados con
  texto, para reabrir. No está disponible en servicios `FINALIZADO` ni `CANCELADO` (P4, revisado por el usuario). Esto limita la decisión 3 de §10.
- **R4.** Solo generan mensaje los cambios de estado que hace el administrativo en el panel React.
  No las respuestas del cliente desde el seguimiento ni el Django Admin. Los cambios automáticos
  quedan excluidos por el mismo criterio (RF-WA-27).
- **R5.** Endpoint nuevo de solo lectura que devuelve el texto preparado (RF-WA-30).
- **R6.** Número solo desde `Cliente.whatsapp`, obligatorio en la solicitud. Supera la regla
  "teléfono o WhatsApp" de la 001 (§2). Cliente existente sin número guardado: se guarda el número de la solicitud; con número guardado no se sobrescribe (P5, confirmado).
- **R7.** Dominio pendiente de compra: variable de entorno en la configuración, sin valor de
  producción. Sin variable no hay enlace y se avisa al administrativo (RF-WA-29).
- **R8.** Riesgo del token en la URL de wa.me: aceptado y documentado (§12).
- **R9.** Servicio desactivado: no se prepara mensaje y se muestra un aviso (RF-WA-28).
- **R10.** Crear una cotización genera `ESPERANDO_APROBACION`. Editar y rechazar no generan.
  Aprobar genera solo si cambia el estado del componente (RF-WA-09).
- **R11.** El texto se prepara al mostrar el panel; la URL de wa.me se construye al clic. Una
  tarjeta por evento en la sección WhatsApp del detalle del servicio (RF-WA-15, RF-WA-17).
- **R12.** Pruebas `django.test` solo para CA-02, CA-15, CA-14, CA-12 y CA-06 (RNF-WA-07).
- **R13.** Editor de una línea. Tratamiento de tú en los avisos del panel. Sesión caducada: login
  conservando el texto editado. Zona America/Bogota solo en la fecha del mensaje (RF-WA-31).
- **R14.** Aplicar R-1 a R-8 del informe QA: **pendiente**, el informe no está en el repositorio
  (ver §13).

### 10.2 Decisiones de la aprobación (A1 a A7)

- **A1 (opción a).** El botón del texto del estado vigente aparece siempre en servicios abiertos,
  también si el cambio fue automático o del cliente (RF-WA-19). Solo los cambios que el ADMINISTRATIVO
  hace desde el panel generan mensaje de evento (RF-WA-27). El botón solo reabre el texto preparado.
- **A2.** Una aprobación registrada a mano por el ADMINISTRATIVO genera el mensaje del estado de
  destino solo si cambia el estado del componente (RF-WA-09).
- **A3.** Si el componente no tiene referencia, `{componente}` muestra solo el tipo (RF-WA-11).
- **A4.** La variable de dominio del enlace se llama `SEGUIMIENTO_BASE_URL` (RF-WA-29).
- **A5.** El texto editado se conserva en la pestaña del navegador y se borra al cerrarla (RF-WA-31).
  El mecanismo está en `plan.md` §4 (D9).
- **A6.** Se aprueban los dos textos de interfaz de §4.2: "Escribe el mensaje antes de abrir
  WhatsApp." para CL-09 y "Se abrió WhatsApp con el mensaje. Envíalo desde WhatsApp: el sistema
  no confirma la entrega." para RF-WA-18. Las tareas que los usan quedan desbloqueadas.
- **A7.** No se modifica la comparación de duplicados por WhatsApp (§12). Queda como pendiente futuro.

## 11. Fuera de alcance

- Integración con WhatsApp Business API, envío automático, confirmación de entrega o de lectura.
- Historial o bitácora de mensajes en la base de datos.
- Mensajes para costos adicionales como eventos propios.
- Notificaciones de cotización distintas de la creación (ver R10).
- Correo electrónico u otros canales distintos de WhatsApp.
- Plantillas editables desde el panel o textos configurables por el administrativo.
- Aviso de nueva solicitud al administrativo (RF-10 de la 001): es otro flujo.
- Cancelación pública desde el enlace (007, supuesto S-5).
- Números fijos, envío a varios números o al número de la empresa.
- Cambios en el catálogo de estados o en las transiciones.
- Mensajes por cambios automáticos o por respuestas del cliente (RF-WA-27).

## 12. Riesgos y notas

- **Sin constancia de envío.** No queda registro de que el cliente recibió el mensaje. Es coherente
  con la decisión 8 original, pero `CONTEXTO_MAESTRO.md` §4 pide trazabilidad de operaciones
  importantes. Se deja constancia para que el usuario confirme que la decisión 8 original lo cubre.
- **Token en la URL de wa.me.** El token viaja en el texto y en la URL de WhatsApp al hacer clic.
  Quien tenga acceso al historial del navegador o a la conversación puede abrir ese seguimiento.
  **Riesgo aceptado y documentado** por el usuario (decisión R8).
- **Normalización compartida.** La normalización del teléfono también alimenta el aviso de
  duplicados (001, RF-8). Un cambio en la validación de WhatsApp no debe alterar esa comparación. Pendiente futuro (A7): la comparación de duplicados por WhatsApp no se cambia en esta spec; ahora el número es obligatorio, así que siempre se compara. El usuario decidirá después si se mantiene.
- **Enlace en desarrollo.** Con un dominio local, el enlace no abre desde el teléfono del cliente.
  La variable de RF-WA-29 permite configurarlo, pero la prueba final necesita el dominio público,
  que aún no existe (decisión R7).
- **Clientes antiguos.** Los números guardados antes de esta spec pueden no cumplir RF-WA-02. Si el
  cliente vuelve a solicitar, su número se guarda solo si no tenía ninguno (RF-WA-04, P5). Un número
  guardado que no cumple RF-WA-02 no se sobrescribe y aplica RF-WA-21 (CL-24).
- **Corrección manual del número.** R2 y P5 dejan la corrección de `Cliente.whatsapp` en Django
  Admin, fuera del alcance del panel. Riesgo: un número mal escrito solo se corrige a mano en Django
  Admin. El usuario decidirá después si quiere edición desde el panel; sería una función nueva con su
  propia aprobación.
- **Ventana emergente.** Mitigado por R11: la ventana se abre en el clic, sin petición previa.
- **Motivo largo.** Al usarse tal cual (R1), el mensaje de `RECHAZADO` puede quedar extenso.

## 13. Resumen de aclaraciones pendientes

**Resueltas por las decisiones del usuario** (sin marcador en el texto): DA-01 (solo
`Cliente.whatsapp`), DA-02 (obligatorio), DA-03 (no sobrescribir, R2), DA-05 (cambios del cliente y
automáticos excluidos, R4), DA-06 (P1, opción b), DA-07 (variable de entorno, R7), DA-08 (zona solo en el mensaje, R13),
DA-09 (`{motivo}` tal cual, R1), DA-10 (sección WhatsApp, R11), DA-11 (siempre disponible, R3),
DA-12 (texto al mostrar, wa.me al clic, R11), DA-13 (endpoint de lectura, R5). Resueltas por el usuario: P1 (opción b, tipo y referencia), P2 (se mantiene usted en los textos
aprobados y tú en la interfaz), P3 (texto de `LISTO_PARA_ENTREGA` sin `{motivo}`), P4 (revisado: sin botón en
`FINALIZADO` ni `CANCELADO`; los componentes de servicios abiertos sí lo tienen), P5 (se guarda el número de la solicitud solo si el cliente no tiene
ninguno; corrección en Django Admin, riesgo en §12) y P6 (textos de estados sin disparador
conservados sin usar).

**Pendientes no relacionados con la aprobación de textos**

| ID | Tema | Opciones | Recomendación del planificador |
|---|---|---|---|
| **R14** | Informe QA con R-1 a R-8 | No localizado en el repositorio | Pasar el informe para aplicarlo. |
| **A7** | Comparación de duplicados por WhatsApp | Mantener, o cambiar en una spec futura | Pendiente futuro; no se toca en la 012. |
