# Solicitud de servicio en banco de pruebas

Especificación funcional · Hidroemcol

## 1. Contexto y objetivo

Hoy la empresa recibe las solicitudes de prueba por WhatsApp. Eso significa que la
información queda en el teléfono del administrativo: se pierde, no se puede consultar con
orden y no hay forma de saber cuántos servicios están en curso ni qué se pidió exactamente.

El banco de pruebas es la capacidad técnica que distingue a la empresa, y es una de las
razones por las que un cliente la contacta. La vía de entrada, sin embargo, es la más débil
del proceso.

**Objetivo:** ofrecer una vía de solicitud donde el cliente describa su necesidad y sus
componentes, deje una huella verificable y reciba de inmediato un código y un enlace para
consultar el avance, sin necesidad de crear una cuenta.

**Por qué no es un formulario más:** centraliza en un solo lugar la información que hoy se
pierde en mensajería, y convierte el primer contacto en un servicio que ya puede seguirse
como cualquier otro.

## 2. Usuarios

| Usuario | Descripción |
|---|---|
| **Cliente solicitante** | Persona física o empresa que necesita probar un componente hidráulico o electrohidráulico. No tiene cuenta en el sistema y no la necesita. Desconoce el vocabulario técnico exacto: describe lo que observa, no el diagnóstico. |
| **Administrativo** | Usuario interno que revisa las solicitudes recibidas y continúa el proceso comercial y técnico. En esta versión solo es destinatario de la información, no interactúa con esta vista. |

## 3. Historias de usuario

**HU-1 — Solicitar sin fricción.**
Como cliente que necesita una prueba en banco, quiero enviar una solicitud describiendo
qué componente llevo y qué necesito, para que la empresa pueda cotizarme, sin tener que
registrarme ni aprender el proceso antes.

**HU-2 — Enviar evidencia visual.**
Como cliente, quiero adjuntar fotos del componente para que la empresa vea su estado y no
me devuelva peticiones de información que yo ya puedo responder con una imagen.

**HU-3 — No duplicar por error.**
Como cliente que ya tiene una solicitud en curso, quiero enterarme antes de enviar otra,
para no crear un duplicado por error, pero poder continuar si de verdad se trata de un
servicio nuevo.

**HU-4 — Salir con un comprobante.**
Como cliente, quiero recibir un código y un enlace de seguimiento al enviar, para poder
volver más adelante y ver el avance de mi servicio sin depender de mensajes sueltos.

## 4. Requisitos funcionales

### RF-1 — Presentar la solicitud

- **RF-1.1** Siempre que un cliente abra la vista de solicitud de banco de pruebas, el
  sistema muestra los campos de contacto, la descripción de la necesidad, el área para
  agregar componentes, el área para adjuntar fotografías y las casillas de preferencia de
  entrega.
- **RF-1.2** Siempre que se abra la vista, el sistema explica que no se requiere cuenta y
  que la empresa se pondrá en contacto para continuar el proceso.

### RF-2 — Capturar los datos de contacto

- **RF-2.1** Siempre que se abra el formulario, el sistema solicita nombre, correo y al
  menos un medio de contacto telefónico, así como un campo opcional de empresa.
- **RF-2.2** Si el cliente omite un campo obligatorio o envía un correo con formato
  inválido, entonces el sistema impide el envío e indica qué campo debe corregir.
- **RF-2.3** Donde se.capture un error de validación, el sistema no descarta lo que el
  cliente ya escribió.
- **RF-2.4** La descripción de la necesidad es obligatoria y admite hasta 500 caracteres. Si
  el cliente la deja vacía o escribe más de 500 caracteres, entonces el sistema impide el
  envío e indica cuál de los dos motivos lo bloquea.

### RF-3 — Indicar la preferencia de entrega

- **RF-3.1** La vista ofrece tres casillas: entregar el componente en el banco, necesitar que
  le avisen para coordinar la entrega, y preferir que recojan el componente.
- **RF-3.2** El cliente puede marcar ninguna, una o varias, y en todos los casos el envío es
  válido.
- **RF-3.3** El sistema guarda la preferencia únicamente como información para el
  administrativo, y no calcula ni gestiona ningún transporte.

### RF-4 — Capturar varios componentes

- **RF-4.1** Siempre que se abra la vista, el sistema permite agregar componentes a la
  solicitud, y cada uno acepta tipo, marca, referencia, descripción y cantidad; la
  descripción de cada componente admite hasta 500 caracteres.
- **RF-4.2** Si el cliente intenta enviar la solicitud sin ningún componente, entonces el
  sistema impide el envío e indica que se requiere al menos uno.
- **RF-4.3** Si el cliente no conoce la marca o la referencia de un componente, entonces el
  sistema le permite dejarlas vacías sin bloquear el envío.
- **RF-4.4** Donde exista más de un componente, el sistema permite quitar cualquiera de
  ellos antes del envío.
- **RF-4.5** Si un componente queda sin descripción, entonces el sistema permite enviar la
  solicitud igualmente, porque el cliente puede no saber cómo describirlo.

### RF-5 — Adjuntar fotografías

- **RF-5.1** Siempre que se abra la vista, el sistema permite adjuntar hasta cinco
  fotografías por solicitud.
- **RF-5.2** Si se alcanza el máximo de cinco, entonces el sistema impide agregar una sexta
  e informa que el límite fue alcanzado.
- **RF-5.3** Si una fotografía excede diez megabytes o no está en formato JPG o PNG,
  entonces el sistema rechaza esa fotografía, informa el límite y permite continuar
  con el resto.
- **RF-5.4** Si el cliente no adjunta ninguna fotografía, entonces el sistema permite enviar
  la solicitud igualmente.

### RF-6 — Clasificar la solicitud

- **RF-6.1** Siempre que se registre una solicitud desde esta vista, el sistema la
  clasifica como servicio de tipo prueba.

### RF-7 — Registrar la solicitud

- **RF-7.1** Cuando el cliente envía el formulario con todos los datos válidos y no debe
  confirmar ningún aviso, entonces el sistema registra la solicitud, la asocia a un cliente,
  y le asigna un código de servicio y un enlace privado de seguimiento.
- **RF-7.2** Si el cliente debe confirmar el aviso de segundo intento, entonces el sistema no
  registra nada hasta que el cliente confirma, y nunca antes de mostrar el aviso.
- **RF-7.3** Si la solicitud queda registrada, entonces todos sus componentes quedan
  asociados a esa misma solicitud.
- **RF-7.4** Si el cliente ya tenía solicitudes previas con el mismo correo o teléfono,
  entonces el sistema mantiene cada solicitud como independiente, y una solicitud enviada
  más tarde cuenta como una solicitud nueva.
- **RF-7.5** Si el cliente envía el mismo formulario más de una vez, incluso si recarga la
  página, se le corta la conexión o lo abre en otra pestaña, entonces el sistema registra una
  sola solicitud.
- **RF-7.6** Mientras la solicitud se está registrando, el sistema desactiva la acción de
  enviar y muestra que está en proceso, para que el cliente no pueda pulsarla de nuevo.

### RF-8 — Avisar de un segundo intento

- **RF-8.1** Si al enviar se detecta que ya existen solicitudes asociadas al mismo correo o
  al mismo teléfono, comparados sin distinguir mayúsculas, espacios sobrantes ni tildes, y
  al menos una de ellas sigue en curso, entonces el sistema muestra un mensaje que explica
  que puede tratarse de un servicio nuevo o de un envío repetido.
- **RF-8.2** Donde se muestre ese aviso, el sistema ofrece al cliente la posibilidad de
  continuar o de cancelar.
- **RF-8.3** Si el cliente cancela tras el aviso, entonces el sistema no registra nada y lo
  devuelve al formulario con lo escrito intacto.
- **RF-8.4** Si el cliente continúa tras el aviso, entonces el sistema registra la solicitud
  con normalidad, como si el aviso no se hubiera mostrado.
- **RF-8.5** Donde se detecte un segundo intento, el sistema nunca impide el envío por ese
  motivo.
- **RF-8.6** Una solicitud anterior sigue en curso mientras no esté en un estado cerrado. Se
  consideran cerrados los estados que terminan la relación con el cliente: finalizado,
  entregado y cancelado. Rechazar la cotización de un componente no cierra el servicio,
  porque los demás componentes de esa misma solicitud siguen avanzando.

### RF-9 — Confirmar al cliente

- **RF-9.1** Cuando la solicitud queda registrada, entonces el sistema muestra una
  confirmación que incluye el código del servicio y el enlace de seguimiento.
- **RF-9.2** Siempre que se muestre la confirmación, el sistema ofrece una forma de copiar
  el enlace, porque el cliente necesitará guardarlo.
- **RF-9.3** Donde se muestre la confirmación, el sistema indica que ese enlace da acceso
  únicamente a esa solicitud y que es su forma de consultar el avance.

### RF-10 — Avisar al administrativo

- **RF-10.1** Cuando se registre una solicitud, entonces el sistema la muestra en el panel del
  administrativo como pendiente de revisar, para que el administrativo sepa que hay una nueva
  sin tener que recargar la página.
- **RF-10.2** Si el administrativo no está mirando el panel, entonces la solicitud sigue
  esperando en la lista y no se pierde.

## 5. Requisitos no funcionales

- **RNF-1** La vista debe poder completarse íntegramente desde un teléfono móvil, que es
  el dispositivo con el que el cliente tiene el componente a la vista.
- **RNF-2** El sistema debe poder completarse en pocos minutos con la información que el
  cliente ya tiene, sin exigirle conocimiento del vocabulario técnico de la empresa.
- **RNF-3** Los textos que la empresa controla deben estar en español. Los mensajes
  generados automáticamente por la plataforma base pueden conservarse en su idioma original
  siempre que sigan siendo comprensibles, y el sitio debe indicar en español qué campo
  corregir cuando el cliente no pueda identificarlo por sí mismo.
- **RNF-4** Ninguna acción de esta vista debe requerir que el cliente tenga cuenta previa.
- **RNF-5** El sistema debe preservar lo capturado ante cualquier error o interrupción, para
  que el cliente no tenga que volver a escribir su solicitud.
- **RNF-6** El cliente no debe quedar bloqueado ante un error del sistema: siempre debe
  existir una salida comprensible, y si no es posible continuar, debe poder comunicarse por
  otros medios con una referencia clara.

## 6. Casos límite

- El cliente cierra el navegador o pierde la conexión **antes** de confirmar el envío: no
  debe quedar ninguna solicitud a medias.
- El cliente pulsa enviar dos veces por impaciencia: debe registrarse **una sola**
  solicitud, nunca dos.
- El cliente es una persona natural y deja el campo de empresa vacío.
- El cliente conoce el tipo de componente pero no la marca ni la referencia.
- El cliente tiene dos componentes del mismo tipo y quiere describirlos por separado.
- El cliente tiene componentes que va a entregar en momentos distintos: la vista solo
  contempla un envío, no varias entregas programadas.
- El cliente adjunta exactamente cinco fotografías: es un caso válido, no un error.
- El archivo tiene extensión de imagen pero su contenido está dañado.
- El cliente adjunta una fotografía que no corresponde al componente: el sistema no valida
  el contenido de la imagen, es responsabilidad de la empresa descartarla.
- El mismo correo corresponde a dos personas distintas que trabajan para el mismo cliente
  comercial: como el correo identifica a una sola persona, el aviso se muestra.
- La solicitud previa del mismo cliente está cancelada, entregada o finalizada: ninguna cuenta
  como servicio en curso, así que el aviso no aparece.
- La solicitud previa del mismo cliente está en cualquiera de los estados en curso, sin
  importar en qué punto del proceso vaya: el aviso aparece.
- El cliente escribe más de 500 caracteres en la descripción o en un componente: el sistema
  no le deja continuar hasta que lo ajuste.

## 7. Fuera de alcance

Esta versión **no** incluye:

- La vista de seguimiento del servicio, que es una funcionalidad propia y se consulta desde
  el enlace recibido. Incluye decidir qué información de la solicitud es visible para el
  cliente y qué información interna queda oculta; esa visibilidad se determina de forma
  explícita por cada dato, nunca por omisión.
- La revisión, asignación, respuesta o cambio de estado de la solicitud por parte del
  administrativo.
- La generación de cotizaciones, su envío al cliente y la aprobación en línea.
- La cuenta de cliente, el registro y el acceso con contraseña.
- La validación del contenido de las fotografías por parte del sistema.
- El aviso al administrativo por canales distintos del panel, como una conversación interna
  o un mensaje por WhatsApp. Queda abierto para una fase posterior, no descartado.
- La eliminación, a solicitud del cliente, de los datos personales ya registrados.
- El transporte, la recepción física y la entrega del componente en el banco. El administrativo
  gestiona la recogida por sus propios medios y cambia el estado cuando recibe el componente.
- El registro de historial técnico, resultados de prueba y documentación del trabajo.
- Cualquier modificación del catálogo de servicios o de los tipos de servicio existentes.

## 8. Criterios de finalización

La funcionalidad está completa cuando:

1. Un cliente sin cuenta puede enviar una solicitud con sus datos de contacto, una
   descripción y al menos un componente, y recibe de inmediato un código y un enlace.
2. Una solicitud con varios componentes queda registrada como **una sola** solicitud que
   contiene todos ellos.
3. El sistema rechaza el envío e indica qué campo debe corregir cuando falta un campo
   obligatorio, el correo es inválido o no hay ningún componente.
4. Se aceptan hasta cinco fotografías por solicitud, y una sexta, una imagen de más de
   diez megabytes o un formato no admitido producen un mensaje que explica el límite sin
   perder lo ya capturado.
5. El aviso de segundo intento aparece solo si hay alguna solicitud previa en curso, es decir,
   que no esté finalizada, entregada ni cancelada; y aparece **antes de registrar nada**. El
   cliente puede continuar o cancelar, cancelar no deja ninguna solicitud registrada, y en
   ningún caso el envío queda bloqueado por esa condición.
6. Un doble envío del mismo formulario produce una sola solicitud, incluso si el cliente
   recarga la página, se le corta la conexión o abre el formulario en otra pestaña; un envío
   posterior con datos distintos sí cuenta como una solicitud nueva.
7. El cliente puede enviar la solicitud sin marcar ninguna casilla de preferencia de entrega,
   y las que marque se guardan solo como información para el administrativo.
8. Un error o interrupción del sistema no hace perder lo que el cliente ya escribió.
9. El recorrido completo se verifica manualmente en un teléfono móvil real.

## 9. Dudas abiertas

- **[NECESITA ACLARACIÓN]** ¿Cuánto tiempo se conservan las fotografías después de la solicitud
  y a quién corresponden los derechos de uso de esas imágenes?
- **[NECESITA ACLARACIÓN]** El rechazo de una cotización es por componente y no cierra el
  servicio, pero el modelo de datos actual no tiene dónde registrarlo: la cotización es del
  servicio, sus líneas no saben a qué componente pertenecen, y el componente no tiene estado.
  Hace falta definir cómo se guarda esa información antes de poder aplicarla.