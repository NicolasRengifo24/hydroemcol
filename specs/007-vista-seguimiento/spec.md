# Spec 007 — Vista de seguimiento del cliente

**Estado: borrador**

Especificación funcional · Hidroemcol

## 1. Contexto y objetivo

Cuando un cliente solicita un servicio recibe un código (`SRV-…`) y un enlace privado de
seguimiento (spec 001, RF-7.1 y RF-9), pero la vista de seguimiento es hoy un marcador de
posición: no muestra nada. En la práctica, el cliente se entera del avance preguntando por
WhatsApp o teléfono, y la empresa repite información que ya está registrada en el sistema.

El backend ya expone una consulta pública por token con el estado del servicio, los
componentes con su estado y su fase, el historial y las fotografías visibles para el cliente,
las cotizaciones pendientes y una acción de aprobación web (specs 002, 005 y 006). Lo que
falta es la vista: la pantalla donde el cliente ve eso, se entiende de un vistazo y percibe
que el estado se renueva solo.

**Objetivo:** una vista de seguimiento donde el cliente, sin cuenta, vea en tiempo real el
estado de su servicio y el estado de cada componente que entregó, mediante una interfaz
animada que traduzca esos estados en una señal visual clara (avance del proceso, situación
de cada pieza), coherente con la identidad técnica e industrial de Hidroemcol.

**Por qué animada y no una lista estática:** el cliente no conoce el vocabulario del
proceso. Una animación de avance le dice "por aquí voy, esto ya está, esto falta" antes de
que lea una sola etiqueta; y al actualizarse sola le confirma que la información está viva,
sin que tenga que recargar ni preguntar.

## 2. Relación con especificaciones anteriores

- **001:** da el acceso (enlace privado + código) y deja el seguimiento fuera de alcance,
  marcando que la visibilidad se decide dato por dato, nunca por omisión.
- **002 (RF-COT-15):** el cliente ve `estado` y `fase` de cada componente en español; los
  campos de control interno quedan ocultos. Esta spec asume ese contrato público como
  punto de partida.
- **003 (RF-7.4):** el acceso "hacer seguimiento" del sitio conduce a consultar el avance
  con el código de servicio; el código no es el token.
- **005:** la API pública de seguimiento existe, filtra por visibilidad y excluye servicios
  desactivados; ningún campo del RegistroTecnico es visible al cliente.
- **006:** control administrativo de estados; `CANCELADO` sale del seguimiento público
  ordinario y `FINALIZADO`/`ENTREGADO` son estados de cierre.

Esta spec no modifica el modelo de datos ni la arquitectura. Los puntos que exigen una
decisión nueva (acceso por código, mecanismo de actualización, cancelación desde el enlace)
quedan en §10 con su supuesto explícito.

## 3. Usuarios

| Usuario | Descripción |
|---|---|
| **Cliente** | Persona o empresa que solicitó un servicio. No tiene cuenta ni la necesita. Llega con el enlace privado guardado o con su código `SRV-…`. Puede tener poca familiaridad con el proceso técnico: necesita entender la situación sin saber el nombre interno de cada estado. |
| **Administrativo** | No usa esta vista, pero sus cambios de estado (specs 002 y 006) son lo que la cliente ve moverse. |
| **Visitante sin datos** | Quien abre la ruta sin un enlace válido. No debe obtener información de ningún servicio. |

## 4. Historias de usuario

- **HU-1.** Como cliente, quiero ver en qué etapa está mi servicio sin escribir a la empresa,
  para saber si ya me van a cotizar o si mi pieza ya está en pruebas.
- **HU-2.** Como cliente, quiero ver el estado de cada componente que entregué, para saber
  qué está avanzando y qué está detenido.
- **HU-3.** Como cliente, quiero que la vista se actualice sola, para no depender de
  recargar la página ni de mensajes sueltos.
- **HU-4.** Como cliente, quiero entender de un vistazo cuánto falta del proceso, para no
  tener que interpretar etiquetas técnicas una por una.
- **HU-5.** Como cliente, quiero ver y responder a una cotización pendiente desde el mismo
  enlace, para desbloquear el trabajo sin cambiar de canal.
- **HU-6.** Como cliente, quiero ver las fotografías que la empresa marcó como visibles y el
  historial que puede ver, para tener constancia del avance.
- **HU-7.** Como cliente, quiero cancelar el servicio desde el enlace mientras todavía no se
  haya recibido mi componente, para no dejar un trámite abierto que ya no quiero.
- **HU-8.** Como cliente que solo conserva el código del servicio, quiero usarlo en el acceso
  de seguimiento del sitio para llegar a mi consulta.

## 5. Definiciones

- **Enlace privado:** URL con el token de seguimiento del servicio. Es la credencial de
  acceso; el código `SRV-…` es el identificador humano y no da acceso por sí mismo.
- **Estado del servicio:** catálogo cerrado vigente: `SOLICITADO`, `EN_REVISION`,
  `COTIZANDO`, `ESPERANDO_APROBACION`, `EN_REPARACION`, `EN_PRUEBAS`, `FINALIZADO`,
  `LISTO_PARA_ENTREGA`, `ENTREGADO`, `NO_APROBADO`, `CANCELADO`.
- **Estado del componente:** catálogo cerrado vigente: `PENDIENTE`, `APROBADO`,
  `RECHAZADO`, `RECHAZADO_BLOQUEANTE`, `EN_PROCESO`, `FINALIZADO_POR_CLIENTE`,
  `FINALIZADO_POR_TECNICO`.
- **Fase del componente:** `RECIBIDO`, `DESMONTAJE_INICIADO`, `EN_EJECUCION`.
- **Producto:** en esta vista, los componentes del servicio: las piezas que el cliente
  entregó. Su estado y su fase son el "estado del producto".
- **Línea de tiempo (stepper):** representación ordenada del proceso del servicio, con
  pasos completados, paso actual y pasos pendientes.
- **Tiempo real (en esta spec):** que la vista muestre un cambio de estado ocurrido en el
  sistema sin que el cliente recargue ni repita la consulta. No implica notificación push ni
  canales permanentes; el mecanismo concreto está en §10, supuesto S-2.
- **Datos autorizados:** solo los campos que el backend entrega para ese token: estado del
  servicio, fechas públicas, componentes con estado y fase, historial visible, fotografías
  visibles y cotizaciones pendientes.

## 6. Requisitos funcionales (EARS)

### Acceso y privacidad

#### RF-SEG-01 — Acceso por enlace privado

**WHEN** el cliente abre la ruta de seguimiento con un token válido de un servicio activo
**THEN** el sistema DEBE mostrar la vista de seguimiento de ese servicio.

**IF** el token no corresponde a ningún servicio, el servicio está desactivado o está en
estado `CANCELADO` **THEN** el sistema DEBE mostrar un mensaje genérico en español que
explique que la consulta no está disponible, con un medio de contacto (WhatsApp), sin
mostrar datos de ningún servicio y sin revelar si ese token existió.

#### RF-SEG-02 — Acceso con el código de servicio

**WHEN** el cliente llega al acceso de seguimiento del sitio e introduce su código de
servicio (`SRV-…`) **THEN** el sistema DEBE permitirle consultar el avance únicamente si el
código corresponde a un servicio y el cliente supera la verificación adicional que se
defina (§10, supuesto S-1).

**IF** la verificación no coincide o el código no existe **THEN** el sistema DEBE responder
con el mismo mensaje genérico en ambos casos, sin indicar cuál de los dos datos falló ni si
el código existe.

#### RF-SEG-03 — Solo los datos de ese servicio

**WHILE** la vista está abierta **THEN** el sistema DEBE presentar únicamente los datos que
el backend autoriza para ese token, filtrados por visibilidad.

**AND** el frontend NO DEBE mostrar ningún campo interno (observaciones internas, registro
técnico, motivos de bloqueo, fechas de control, usuarios administrativos, token completo ni
identificadores internos), ni deducir información que el backend no entrega.

**AND** la existencia de un dato en el panel administrativo NO DEBE volverlo visible aquí.

### Estado del servicio y línea de tiempo

#### RF-SEG-04 — Resumen del servicio

**WHEN** la vista carga un servicio **THEN** el sistema DEBE mostrar como mínimo: código del
servicio, tipo de servicio, estado actual con su etiqueta en español, fecha de solicitud y
las fechas públicas que el backend entregue (recepción, finalización, entrega cuando
existan), y la descripción de la solicitud.

#### RF-SEG-05 — Línea de tiempo del proceso

**WHEN** la vista muestra un servicio **THEN** el sistema DEBE presentar una línea de tiempo
con los pasos del proceso aprobado, en orden fijo, marcando cada paso como completado, actual
o pendiente según el estado que informe el backend (§10, supuesto S-3 para el mapeo exacto).

**AND** la línea de tiempo DEBE ser comprensible sin leer todas las etiquetas: el cliente
debe poder distinguir, de un vistazo, qué ya pasó, en qué punto va y qué falta.

**AND** la vista DEBE ser legible sin horizontal scroll en móvil; el orden de los pasos no
puede perderse por el formato de la pantalla.

#### RF-SEG-06 — El avance solo lo mueve el backend

**WHEN** el estado del servicio no cambia **THEN** la línea de tiempo NO DEBE avanzar ni
retroceder por cuenta propia.

**AND** ningún paso DEBE presentarse como completado sin que el estado recibido lo respalde;
el frontend solo interpreta para presentar, nunca decide el progreso.

#### RF-SEG-07 — Estados fuera del recorrido lineal

**WHEN** el estado recibido es `NO_APROBADO` **THEN** el sistema DEBE mostrar un aviso
diferenciado que explique en español que el servicio no continuó, en lugar de forzar ese
estado dentro de los pasos del recorrido, y DEBE ofrecer el medio de contacto.

**AND** un servicio `CANCELADO` no es consultable por esta vista (RF-SEG-01).

#### RF-SEG-08 — Servicio en recorrido terminado

**WHEN** el estado es `FINALIZADO`, `LISTO_PARA_ENTREGA` o `ENTREGADO` **THEN** el sistema
DEBE presentar el proceso como avanzado hasta el punto que corresponda, sin animar pasos
futuros como si faltaran trabajo que la empresa va a ejecutar, y DEBE mostrar las fechas de
finalización o entrega cuando el backend las entregue.

### Estado del producto (componentes)

#### RF-SEG-09 — Ficha por componente

**WHEN** el servicio tiene componentes **THEN** el sistema DEBE mostrar una ficha por
componente con tipo, marca, referencia, descripción, cantidad, estado y fase, tal como los
entregue el backend en español.

**WHEN** el servicio no tiene componentes **THEN** el sistema DEBE mostrar el resto de la
vista con normalidad y una nota breve de que aún no hay componentes registrados, sin
presentarlo como un error.

#### RF-SEG-10 — Indicación animada del estado del componente

**WHEN** se muestra cada ficha de componente **THEN** el sistema DEBE reflejar su estado con
una señal visual animada diferenciada: componente en proceso con indicador activo,
componente finalizado con señal de completado, componente detenido por cotización con
señal de espera.

**AND** la distinción NO DEBE depender solo del color: cada estado DEBE llevar además
etiqueta de texto y una señal de forma (icono, trazo o marcador) reconocible.

**AND** la animación DEBE ser decorativa de apoyo: la información debe leerse igual si no se
ejecuta.

#### RF-SEG-11 — Estado del producto se actualiza solo

**WHEN** una consulta automática entrega un estado de componente distinto al mostrado
**THEN** el sistema DEBE reemplazar el valor y ejecutar la animación de cambio de esa ficha
sin recargar la página (RF-SEG-18).

### Cotización pendiente

#### RF-SEG-12 — Bloque de cotización pendiente

**WHEN** el backend entrega una o más cotizaciones pendientes para ese servicio **THEN** el
sistema DEBE mostrar un bloque visible con número, tipo, descripción, total y sus detalles,
con la indicación de que requiere respuesta del cliente.

**AND** el bloque DEBE destacarse como la acción pendiente principal de la vista mientras
exista.

#### RF-SEG-13 — Responder la cotización desde el enlace

**WHEN** el cliente pulsa "Aprobar" o "No aprobar" **THEN** el sistema DEBE enviar la
respuesta al endpoint público de aprobación y DEBE reflejar el resultado devuelto por el
backend.

**IF** el backend rechaza la operación (por ejemplo, porque otra vía ya respondió esa
cotización) **THEN** el sistema DEBE mostrar el mensaje del backend, desaparecer el bloque si
ya no hay cotización pendiente y actualizar la vista, sin fingir éxito.

**WHILE** la respuesta se está registrando **THEN** el sistema DEBE impedir el envío
duplicado por doble pulsación y mostrar que está en proceso.

#### RF-SEG-14 — Sin cotización pendiente

**WHEN** no hay cotizaciones pendientes **THEN** el sistema NO DEBE mostrar el bloque de
aprobación ni un espacio vacío que sugiera que falta algo.

### Evidencia visible

#### RF-SEG-15 — Historial visible

**WHEN** el backend entrega entradas de historial visibles para el cliente **THEN** el
sistema DEBE mostrarlas en orden cronológico con su estado, comentario y fecha.

**WHEN** no hay entradas visibles **THEN** el sistema DEBE omitir la sección sin presentarlo
como error, porque la línea de tiempo (RF-SEG-05) ya informa el avance (§10, supuesto S-4).

#### RF-SEG-16 — Fotografías visibles

**WHEN** el backend entrega fotografías visibles **THEN** el sistema DEBE mostrarlas con su
descripción y tipo, con texto alternativo, carga diferida y sin mostrar ninguna fotografía
que el backend no entregue.

### Tiempo real

#### RF-SEG-17 — Actualización automática

**WHILE** la vista de seguimiento está abierta **THEN** el sistema DEBE actualizar los datos
periódicamente por su cuenta, sin que el cliente tenga que recargar ni pulsar un botón.

**AND** la actualización NO DEBE requerir que el cliente tenga sesión ni introduce de nuevo
el enlace.

#### RF-SEG-18 — Cambio detectado: animación y aviso

**WHEN** una actualización trae un estado del servicio o de un componente distinto al
mostrado **THEN** el sistema DEBE aplicar el cambio en pantalla y ejecutar la animación de
transición correspondiente (la línea de tiempo avanza y la ficha afectada cambia de señal).

**AND** el cambio DEBE anunciarse también en texto accesible, para que no dependa de la
animación ni del color.

**AND** el sistema NO DEBE recargar la página ni perder el lugar de lectura del cliente.

#### RF-SEG-19 — Fallo de la actualización

**IF** una actualización automática falla por red, timeout o error del servidor **THEN** el
sistema DEBE conservar el último dato mostrado, indicar de forma discreta y comprensible
que la información podría no estar actualizada y reintentar en la siguiente oportunidad.

**AND** un fallo transitorio NO DEBE borrar la pantalla ni presentarse como error técnico.

#### RF-SEG-20 — Indicador de actualización en vivo

**WHILE** la actualización automática está activa **THEN** la vista DEBE mostrar un indicador
discreto de que la información se renueva sola; con movimiento reducido, ese indicador DEBE
ser estático y de texto.

### Cancelación desde el enlace

#### RF-SEG-21 — Cancelación mientras no se ha recibido

**WHEN** el servicio cumple la condición de "aún no recibido" (§10, supuesto S-5) **THEN**
la vista DEBE ofrecer al cliente cancelar el servicio, pidiendo confirmación y un motivo
obligatorio antes de enviarlo.

**WHEN** el servicio ya superó esa condición **THEN** la vista NO DEBE ofrecer la
cancelación; solo el administrativo puede cancelar (spec 006, RF-EST-11).

**IF** la cancelación se confirma **THEN** el sistema DEBE reflejar que el servicio quedó
cancelado y dejar de ofrecer acciones, sin fingir éxito si el backend la rechaza.

**IF** el backend no tiene todavía una operación pública de cancelación **THEN** esta vista
NO DEBE simularla: el requisito queda condicionado a la aprobación descrita en §10.

### Interfaz, estados y animación

#### RF-SEG-22 — Estados de la interfaz

**WHEN** la consulta está en curso **THEN** el sistema DEBE mostrar un estado de carga que
conserve la maqueta de la página, para que el contenido no salte al llegar.

**WHEN** la consulta termina sin datos esperados **THEN** DEBE distinguir error de vacío y
ofrecer un reintento o el medio de contacto, sin dejar una pantalla en blanco.

**WHEN** el cliente pulsa un reintento **THEN** el sistema DEBE volver a consultar sin
duplicar ninguna acción ya confirmada.

#### RF-SEG-23 — Animación con movimiento reducido

**WHEN** el sistema operativo del cliente indica movimiento reducido **THEN** toda la
animación de entrada, de progreso y de transición DEBE desactivarse y el contenido DEBE
mostrarse completo e inmediatamente.

**AND** ninguna información DEBE depender de que una animación se ejecute.

#### RF-SEG-24 — Entrada y progreso con intención industrial

**WHEN** la vista termina de cargar **THEN** las secciones DEBEN aparecer de forma escalonada
y el trazo de la línea de tiempo DEBE dibujarse hasta el paso actual, con una duración
acotada que no retrase la lectura.

**AND** el lenguaje visual DEBE conservar la identidad técnica de Hidroemcol (precisión,
ordén, sobriedad industrial) y NO DEBE parecer una plantilla genérica ni de entretenimiento.

#### RF-SEG-25 — Enlace y contacto

**WHEN** la vista muestra un servicio **THEN** el sistema DEBE permitir copiar el enlace de
seguimiento (para guardarlo) y DEBE ofrecer el contacto con la empresa desde la misma
vista, usando el único punto de configuración del contacto del sitio.

## 7. Requisitos no funcionales

- **RNF-SEG-01 — Responsive.** La vista DEBE funcionar en móvil, tablet y escritorio con
  enfoque móvil primero, sin desplazamiento horizontal para leer el estado, sin texto
  microscópico y con objetivos táctiles utilizables; la línea de tiempo DEBE seguir siendo
  interpretable en 375 px.
- **RNF-SEG-02 — Accesibilidad.** HTML semántico, jerarquía de encabezados, foco visible,
  contraste suficiente, operación por teclado, texto alternativo en fotografías, y anuncio
  accesible de los cambios de estado. El color NUNCA puede ser la única vía para comunicar
  estado, error o progreso.
- **RNF-SEG-03 — Rendimiento.** Las animaciones DEBEN ser ligeras y no impedir la lectura ni
  el desplazamiento; las fotografías con carga diferida; la actualización automática NO DEBE
  mantenerse activa de forma intensa cuando la pestaña no está visible (§10, supuesto S-2);
  la vista DEBE mostrar contenido útil sin esperar a que todo termine de animarse.
- **RNF-SEG-04 — Seguridad y privacidad.** El token se trata como credencial; el backend es
  la autoridad para entregar datos; ocultar algo en la interfaz NO es una medida de
  seguridad; ningún dato de otro servicio ni campo interno puede aparecer aunque se
  manipule la URL.
- **RNF-SEG-05 — Idioma.** Los textos visibles en español, con etiquetas comprensibles para
  un cliente que no domina el vocabulario técnico; los valores internos de estado pueden
  llegar como código mientras se muestren como etiqueta legible.
- **RNF-SEG-06 — Sin arquitectura nueva.** La vista DEBE operar con la arquitectura,
  dependencias y API aprobadas: sin WebSockets, SSE, Redis, Channels, cuentas de cliente ni
  dependencias nuevas, salvo aprobación explícita (constitución, principio 1).
- **RNF-SEG-07 — Verificabilidad.** Cada RF DEBE poder comprobarse en el navegador con datos
  reales (servicio en varios estados), y las garantías de autorización del backend DEBEN
  seguir cubiertas por las pruebas `django.test` existentes.

## 8. Casos límite

- **CL-01.** Token inventado, truncado o de servicio desactivado/cancelado: mensaje
  genérico, contacto, cero datos; el mensaje es idéntico al de un token que nunca existió.
- **CL-02.** Código correcto pero datos de verificación erróneos (y viceversa): mismo
  mensaje genérico, sin revelar cuál falló.
- **CL-03.** Servicio sin componentes: se ve el resumen y la línea de tiempo; nota breve;
  no es un error.
- **CL-04.** Componente con cotización bloqueante pendiente o rechazada: ficha en espera con
  su señal; los demás componentes se muestran con sus propios estados.
- **CL-05.** Historial visible vacío (caso habitual hoy): la vista funciona igual, sin sección
  de historial y sin error.
- **CL-06.** Ninguna fotografía visible: la vista funciona sin galería.
- **CL-07.** Cotización pendiente aprobada por WhatsApp mientras el cliente tenía la vista
  abierta: al responder o al refrescar, el bloque desaparece y se muestra el mensaje
  correspondiente sin dar por buena una operación rechazada.
- **CL-08.** Doble pulsación en "Aprobar": se registra una sola respuesta.
- **CL-09.** Red caída durante varias actualizaciones: se conserva el último dato con aviso
  discreto y reintento; no se borra la pantalla ni se acumulan errores técnicos visibles.
- **CL-10.** El cliente cambia de pestaña y vuelve: ve el estado actual (el más reciente),
  no el que había al irse.
- **CL-11.** Estado `NO_APROBADO`: aviso diferenciado con contacto, fuera de los pasos del
  recorrido.
- **CL-12.** Estado `ENTREGADO`: proceso presentado como terminado, con fecha de entrega;
  sin pasos pendientes animados.
- **CL-13.** Servicio con historial adelantado o atrasado respecto del estado: manda el
  estado actual; la línea de tiempo no puede contradecirlo.
- **CL-14.** Movimiento reducido activado: sin animaciones, contenido completo de inmediato,
  indicador de actualización estático.
- **CL-15.** Pantalla de 375 px: la línea de tiempo se lee completa sin scroll horizontal y
  los botones de cotización son tocables.
- **CL-16.** Cliente con dos servicios distintos: el enlace de cada uno lleva solo a su
  servicio; nada del otro aparece aunque se comparta la pestaña.
- **CL-17.** Cambio de estado justo al momento de enviar una respuesta de cotización: la
  respuesta se juzga con la respuesta del backend; la vista se refresca y muestra el estado
  persistido, nunca uno supuesto.
- **CL-18.** La cancelación pública no está disponible (supuesto S-5 no aprobado o backend
  sin operación): la vista no ofrece el botón y no simula la acción.

## 9. Fuera de alcance

- WebSockets, SSE, Redis, Django Channels, notificaciones push, correo automático y WhatsApp
  Business API (el seguimiento web sigue siendo la fuente oficial).
- Cuenta, registro o login de cliente; el acceso sigue siendo por enlace o por código con
  verificación.
- Mostrar el RegistroTecnico o cualquier campo de información técnica (spec 005, RF-ADM-28:
  nada visible al cliente en esta versión).
- Mostrar observaciones internas, motivos de bloqueo, usuarios administrativos, el token
  completo o identificadores internos.
- Historial de cotizaciones ya respondidas y de aprobaciones, salvo que se apruebe (§10,
  supuesto S-6): hoy solo se exponen las pendientes.
- Aprobar cotizaciones desde el panel o cambiar estados: es tarea del administrativo (specs
  002 y 006).
- Reapertura de servicios cancelados, edición de solicitudes, generación de PDF o facturas.
- Cambiar el modelo de datos, los catálogos de estado o el contrato público existente, salvo
  los puntos nuevos que este documento somete a aprobación en §10.

## 10. Dudas abiertas y supuestos a confirmar

- **S-1 [NECESITA ACLARACIÓN] — Acceso por código.** El backend hoy solo consulta por token:
  no existe ninguna operación de búsqueda por código, y los códigos son consecutivos
  (`SRV-2026-00125`), así que exponer el servicio solo con el código permitiría adivinar
  otros. **Supuesto:** el acceso por código exige código + un dato de verificación (recomendado:
  el correo registrado en la solicitud, comparado igual que en el aviso de duplicados de la
  spec 001). **Preguntas:** ¿qué dato se exige (correo, teléfono, ambos)? ¿se crea la
  operación pública de búsqueda en esta spec o el acceso por código queda solo con el enlace
  hasta una fase posterior?
- **S-2 [NECESITA ACLARACIÓN] — Mecanismo de tiempo real.** El contexto maestro §33 descarta
  WebSockets inicialmente y habla de consulta periódica. **Supuesto:** actualización
  periódica (polling) sin dependencias nuevas, con la vista dejando de consultar cuando la
  pestaña no está visible. **Preguntas:** ¿se aprueba el sondeo? ¿cada cuánto (por ejemplo 15
  o 30 segundos)? ¿se pausa con la pestaña oculta o se mantiene siempre?
- **S-3 [NECESITA ACLARACIÓN] — Pasos de la línea de tiempo.** Hay 11 estados de servicio y
  el ejemplo del contexto (§30) muestra 6 pasos. **Supuesto:** los pasos siguen el flujo
  aprobado (§9): solicitud recibida → revisión/cotización → aprobación → trabajo → pruebas →
  finalización y entrega, con `NO_APROBADO` como aviso aparte (RF-SEG-07). **Preguntas:**
  ¿cuántos pasos exactos y cómo se agrupan `COTIZANDO` con `ESPERANDO_APROBACION`?
  ¿`LISTO_PARA_ENTREGA` es un paso propio o parte de "entrega"?
- **S-4 [SUPUESTO] — Historial casi siempre vacío.** Hoy todos los registros de historial se
  crean con `visible_cliente=False` y en el administrativo ese campo es de solo lectura, así
  que el bloque de historial llegaría vacío en la práctica. **Supuesto:** la línea de tiempo
  se construye desde el estado actual (RF-SEG-05) y el historial se muestra solo si el
  backend devuelve entradas. **Pregunta:** ¿conviene que algún cambio de estado se registre
  visible para el cliente de forma automática, o se marca caso por caso desde el panel?
- **S-5 [NECESITA ACLARACIÓN] — Cancelación desde el enlace.** Está anotada en `MEMORY.md`
  como decisión tomada pendiente de implementar en esta spec, pero hoy no existe operación
  pública de cancelación y la condición exacta no está cerrada. **Supuesto:** el cliente
  puede cancelar mientras el componente aún no haya sido recibido (legible del estado o de
  `fecha_recepcion`), con motivo obligatorio, reutilizando la regla de cancelación de la
  spec 006. **Preguntas:** ¿se aprueba la operación pública de cancelación (endpoint nuevo)?
  ¿cuál es la condición técnica exacta de "no recibido"? ¿se exige confirmación doble además
  del motivo?
- **S-6 [SUPUESTO] — Cotizaciones visibles.** **Supuesto:** el cliente solo ve la cotización
  pendiente (es lo que expone el backend hoy), no el histórico de cotizaciones ni las
  aprobaciones registradas. **Pregunta:** ¿se quiere mostrar el histórico de cotizaciones y
  sus resultados en esta versión? Expondría un contrato público nuevo.
- **S-7 [SUPUESTO] — Etiqueta del componente detenido.** El backend entrega "Rechazado
  (bloqueante)" como etiqueta. **Supuesto:** se muestra tal cual en esta versión. **Pregunta:**
  ¿se pide al backend una etiqueta amigable para el cliente (por ejemplo "En espera por
  cotización rechazada", como en el panel)? Eso modificaría el serializer público.
