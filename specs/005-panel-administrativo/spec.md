# Spec 005 — Panel administrativo completo

**Estado: aprobada**

## 1. Contexto y objetivo

El acceso administrativo de la especificación 004 ya proporciona la entrada segura al
panel, pero la ruta administrativa todavía es un placeholder. El negocio necesita una
vista operativa completa para revisar solicitudes, conducir el trabajo de los
componentes, documentar lo ocurrido y consultar el estado de cada servicio.

El objetivo de esta especificación es definir qué debe poder hacer el único rol
`ADMINISTRATIVO` desde un panel separado del sitio público, manteniendo al backend como
fuente de verdad para autorización, estados, cálculos y trazabilidad.

La especificación amplía la operación administrativa prevista en el contexto maestro y
reutiliza las reglas de cotización y de componentes aprobadas en la especificación 002.
No convierte la plataforma en un e-commerce ni crea una cuenta para el cliente final.

## 2. Usuarios

| Usuario | Necesidad |
|---|---|
| **Administrativo** | Consultar, documentar y operar cualquier servicio permitido por el panel, con una única sesión y un único rol administrativo. |
| **Cliente final** | No utiliza este panel. Consulta únicamente la información pública autorizada mediante su enlace privado de seguimiento. |

## 3. Historias de usuario

- **HU-ADM-01.** Como administrativo, quiero ver un resumen de la operación para saber
  qué servicios requieren atención.
- **HU-ADM-02.** Como administrativo, quiero buscar, filtrar, ordenar y paginar los
  servicios para encontrar rápidamente una solicitud.
- **HU-ADM-03.** Como administrativo, quiero consultar el detalle completo de un servicio
  para tomar decisiones con toda su información relacionada.
- **HU-ADM-04.** Como administrativo, quiero gestionar componentes y sus avances sin
  afectar indebidamente a los demás componentes del servicio.
- **HU-ADM-05.** Como administrativo, quiero crear y corregir cotizaciones conservando
  sus versiones y respuestas para no perder la historia comercial.
- **HU-ADM-06.** Como administrativo, quiero registrar aprobaciones recibidas por medios
  externos para que WhatsApp, llamadas o conversaciones presenciales no sustituyan el
  registro oficial.
- **HU-ADM-07.** Como administrativo, quiero documentar el historial, la información
  técnica y las fotografías para conservar evidencia del proceso.
- **HU-ADM-08.** Como administrativo, quiero ejecutar las acciones de proceso disponibles
  y recibir una explicación cuando una acción no sea válida.
- **HU-ADM-09.** Como cliente, no quiero que el panel ni los datos internos queden
  expuestos por una ruta pública o por una interfaz que oculte datos solamente con CSS.

## 4. Definiciones

- **Servicio activo:** servicio con `activo=True` que puede aparecer en la operación
  ordinaria. Desactivar un servicio no equivale a eliminarlo físicamente.
- **Componente:** pieza o conjunto atendido dentro de un servicio. Sus cotizaciones,
  estado, fase e historial pueden ser independientes de los demás componentes.
- **Cotización rechazada bloqueante:** cotización bloqueante en estado `RECHAZADA` que
  deja el componente detenido en `RECHAZADO_BLOQUEANTE`. En la interfaz se muestra como
  **“En espera por cotización rechazada”**; no se crea un estado de servicio o componente
  llamado `EN_ESPERA`.
- **Versión de cotización:** cotización nueva, con número propio, relacionada con una
  cotización anterior mediante la relación opcional `reemplaza_a` (o equivalente), que
  conserva la anterior, incluida una cotización rechazada. Una versión no sobrescribe ni
  elimina su antecedente.
- **Información administrativa interna:** datos destinados a la operación de la empresa,
  incluyendo observaciones internas, controles de proceso, trazabilidad, información
  técnica mientras no se autorice su publicación y datos de auditoría.
- **Información pública del cliente:** únicamente los datos que el contrato del
  seguimiento autoriza expresamente y que se filtran para ese servicio. La existencia en
  el panel no vuelve público ningún dato.
- **Cotización histórica sin componente:** cotización creada antes de la asociación de
  cotizaciones a componentes, conservada con `componente` vacío por compatibilidad. El panel
  la muestra como **“Cotización del servicio”**. Las cotizaciones nuevas se asocian a un
  componente cuando la operación corresponda a uno.
- **Registro técnico:** información interna de texto libre asociada uno-a-uno con un
  servicio, con diagnóstico, trabajo realizado, resultado de pruebas, recomendaciones,
  observaciones, autoría y fechas de creación y actualización. No representa parámetros
  rígidos de banco de pruebas.
- **Recientes:** los últimos 10 servicios activos ordenados por `fecha_solicitud`
  descendente.
- **Pendientes de atención:** servicios activos en `SOLICITADO`, `EN_REVISION`,
  `ESPERANDO_APROBACION` o con componentes detenidos por una cotización bloqueante,
  incluido `RECHAZADO_BLOQUEANTE`.
- **Componente conservado:** componente que tiene historial o cotizaciones. Se mantiene
  permanentemente para preservar la trazabilidad; sus datos descriptivos sí pueden corregirse.
  La conservación no introduce un campo `activo` nuevo.

## 5. Requisitos funcionales (EARS)

### Acceso, separación y autoridad

#### RF-ADM-01 — Acceso administrativo autenticado

**WHEN** una persona consulta cualquier dato u operación del panel
**THEN** el sistema DEBE exigir una sesión válida de la especificación 004 y el rol
`ADMINISTRATIVO`.

**IF** la petición no está autenticada, la sesión expiró, fue revocada o la cuenta dejó
de estar activa, **THEN** el backend DEBE rechazarla y la interfaz DEBE conducir a la
pantalla de acceso sin mostrar datos administrativos.

#### RF-ADM-02 — Separación del sitio público

**WHILE** el usuario navega por el panel **THEN** el sistema DEBE presentar un layout
administrativo separado del sitio público, sin mezclar su navegación ni sus datos.

#### RF-ADM-03 — Backend como autoridad

**WHEN** el administrativo consulta o ejecuta una operación
**THEN** el backend DEBE ser la autoridad para permisos, estados, totales, indicadores,
visibilidad y validación de reglas.

**IF** la interfaz muestra una acción como disponible pero el backend la considera
inválida, **THEN** el backend DEBE rechazarla sin modificar datos.

#### RF-ADM-04 — No exposición innecesaria del seguimiento

**WHEN** el panel muestra o prepara un enlace de seguimiento
**THEN** el sistema DEBE tratar el token privado como una credencial y no DEBE exponerlo
en listados, búsquedas, indicadores, logs visibles ni respuestas donde no sea necesario.

**AND** el ID interno del servicio NO DEBE sustituir al token como mecanismo de acceso
público.

**AND** el token de seguimiento NUNCA DEBE mostrarse completo como texto; el panel solo
DEBE ofrecer acciones explícitas para copiarlo o abrir el enlace privado.

**AND** en esta versión el panel NO DEBE ofrecer acciones para regenerar ni revocar el
enlace privado.

### Dashboard

#### RF-ADM-05 — Indicadores operativos

**WHEN** el administrativo abre el dashboard **THEN** el sistema DEBE mostrar indicadores
separados para el total de servicios activos y para los estados de servicio:

- solicitados;
- en revisión;
- cotizando;
- esperando aprobación;
- en reparación;
- en pruebas;
- finalizados;
- listos para entrega;
- entregados;
- cancelados;
- no aprobados.

**AND** cada indicador DEBE representar los datos calculados por el backend y DEBE poder
llevar al listado correspondiente sin inventar una cifra en el frontend.

**AND** todos los contadores operativos, incluido el total, DEBEN contar únicamente
servicios con `activo=True`.

#### RF-ADM-06 — Recientes y pendientes de atención

**WHEN** el administrativo abre el dashboard **THEN** el sistema DEBE mostrar una
sección de servicios recientes y otra de pendientes de atención.

**AND** el backend DEBE entregar los elementos y la definición aplicada a cada sección,
para que la interfaz no duplique la política de fechas o prioridad.

**AND** “recientes” DEBE contener exactamente los últimos 10 servicios activos ordenados
por `fecha_solicitud` descendente.

**AND** “pendientes de atención” DEBE incluir servicios activos en `SOLICITADO`,
`EN_REVISION` o `ESPERANDO_APROBACION`, y servicios activos con componentes detenidos
por una cotización bloqueante, incluido un componente en `RECHAZADO_BLOQUEANTE`.

**AND** un servicio activo en `NO_APROBADO` DEBE contar en el indicador correspondiente.

#### RF-ADM-07 — Coherencia de indicadores

**WHEN** una operación modifica un servicio o una relación que afecte los indicadores
**THEN** una consulta posterior DEBE reflejar el resultado persistido por el backend.

**AND** un servicio desactivado no DEBE contarse como activo en los indicadores de
operación ordinaria, aunque su información histórica siga conservada.

**AND** ningún servicio desactivado DEBE aparecer en el dashboard operativo.

### Listado de servicios

#### RF-ADM-08 — Consulta del listado

**WHEN** el administrativo abre la sección de servicios **THEN** el sistema DEBE mostrar
un listado de servicios administrativos con, como mínimo, código, cliente o empresa,
tipo de servicio, estado y fecha relevante para la operación.

#### RF-ADM-09 — Búsqueda

**WHEN** el administrativo busca un texto **THEN** el sistema DEBE permitir buscar por
código de servicio, nombre o datos identificables del cliente y empresa.

**AND** la búsqueda DEBE resolverse sobre los datos autorizados por el backend y no solo
sobre las filas ya cargadas en la interfaz.

**AND** la comparación DEBE ser insensible a mayúsculas y tildes, y DEBE abarcar código,
nombre del cliente y empresa.

#### RF-ADM-10 — Filtros

**WHEN** el administrativo aplica un filtro de estado **THEN** el sistema DEBE devolver
solo los servicios que correspondan al estado seleccionado, usando los estados oficiales
del servicio de la especificación 002 y del modelo vigente.

**AND** el filtro DEBE permitir consultar como mínimo los estados mostrados por RF-ADM-05.

**AND** la búsqueda DEBE poder combinarse con el filtro de estado en una misma consulta.

#### RF-ADM-11 — Paginación y ordenamiento

**WHEN** el resultado excede una página **THEN** el sistema DEBE permitir paginarlo y
mostrar el contexto de la página actual.

**AND** cada página DEBE contener 20 elementos y el orden predeterminado DEBE ser
`fecha_solicitud` descendente.

**WHEN** el administrativo selecciona un criterio de ordenamiento **THEN** el sistema
DEBE devolver el resultado ordenado por el backend y conservar el criterio mientras se
consulta la lista.

#### RF-ADM-12 — Presentación adaptable

**WHEN** el ancho disponible es de escritorio **THEN** el sistema DEBE ofrecer una vista
de tabla legible.

**WHEN** el ancho disponible es móvil **THEN** el sistema DEBE ofrecer una vista de
tarjetas que conserve las acciones y datos esenciales sin exigir desplazamiento
horizontal para leer cada servicio.

### Detalle del servicio

#### RF-ADM-13 — Detalle consolidado

**WHEN** el administrativo abre un servicio **THEN** el sistema DEBE mostrar su código,
estado, tipo, fechas disponibles, descripción de la solicitud, observaciones internas,
cliente, componentes, cotizaciones, aprobaciones, historial, fotografías, información
técnica y datos necesarios para el seguimiento.

**AND** las relaciones mostradas DEBEN corresponder al servicio consultado, sin permitir
actuar sobre componentes o cotizaciones de otro servicio mediante identificadores
manipulados.

#### RF-ADM-14 — Cliente y datos administrativos

**WHEN** el administrativo consulta el cliente desde el detalle **THEN** el sistema
DEBE permitir consultar sus datos de contacto y relación con el servicio.

**AND** los campos internos DEBEN distinguirse visualmente de la información que podría
ser visible al cliente; la interfaz no DEBE insinuar que todo lo administrativo es
público.

#### RF-ADM-15 — Estado y seguimiento

**WHEN** el administrativo consulta el estado de un servicio o componente **THEN** el
sistema DEBE mostrar la etiqueta legible, la fase del componente cuando corresponda, el
motivo de bloqueo y el resumen de cierre que entregue el backend.

**AND** el componente con cotización bloqueante rechazada DEBE mostrarse como “En espera
por cotización rechazada”, conservando internamente `RECHAZADO_BLOQUEANTE`.

#### RF-ADM-15A — Edición limitada del servicio

**WHEN** el administrativo modifica un servicio desde el panel **THEN** el sistema DEBE
permitir únicamente actualizar `observaciones_internas`.

**AND** el administrativo NO DEBE poder modificar mediante esta funcionalidad los demás
datos del servicio ni ningún dato del cliente.

**IF** se intenta modificar un campo no permitido, **THEN** el backend DEBE rechazar la
operación sin alterar el servicio ni el cliente.

### Componentes y acciones de proceso

#### RF-ADM-16 — Gestión de componentes

**WHEN** el administrativo agrega o edita un componente **THEN** el sistema DEBE permitir
gestionar tipo, marca, referencia, descripción y cantidad, manteniendo la relación con
su servicio.

**AND** el administrativo DEBE poder eliminar un componente únicamente conforme a la
política de conservación y trazabilidad de RF-ADM-17.

**AND** el sistema NO DEBE crear ni exigir un número de serie ni parámetros rígidos de
banco de pruebas.

#### RF-ADM-17 — Conservación de componentes con trazabilidad

**WHEN** un componente tiene historial o cotizaciones **THEN** el sistema NO DEBE
permitir eliminarlo físicamente y DEBE conservarlo permanentemente.

**AND** el administrativo DEBE poder corregir sus datos descriptivos permitidos sin borrar ni
desvincular sus cotizaciones, aprobaciones o historial.

**WHEN** un componente no tiene historial ni cotizaciones **THEN** el sistema DEBE
permitir su eliminación física.

**AND** si tiene historial o cotizaciones, el backend DEBE rechazar la eliminación y
conservar el componente sin crear un campo `activo` nuevo.

#### RF-ADM-18 — Inicio de trabajo

**WHEN** el administrativo ejecuta iniciar trabajo sobre un componente
**THEN** el backend DEBE aplicar las reglas de la especificación 002, registrar el inicio
del desmontaje, la fase, la fecha y el administrativo responsable.

**IF** existe una cotización bloqueante pendiente o rechazada, **THEN** el sistema DEBE
rechazar la acción y explicar el bloqueo; los demás componentes DEBEN permanecer
operables según sus propias reglas.

#### RF-ADM-19 — Finalización y corrección de componente

**WHEN** el administrativo ejecuta finalizar componente **THEN** el sistema DEBE usar
únicamente los motivos oficiales `FINALIZADO_POR_CLIENTE` o
`FINALIZADO_POR_TECNICO`, registrar fecha, usuario y trazabilidad.

**WHEN** se corrige una finalización por error humano **THEN** el sistema DEBE conservar
el estado anterior, registrar quién corrigió, cuándo y el comentario de corrección.

#### RF-ADM-20 — Finalización del servicio

**WHEN** el administrativo solicita finalizar un servicio **THEN** el backend DEBE
permitirlo solo cuando se cumpla el criterio de cierre de la especificación 002 y la
acción sea explícita.

**AND** el sistema DEBE registrar el cambio, el administrativo y la fecha.

**IF** queda un componente sin finalizar **THEN** el sistema DEBE rechazar el cierre y
mostrar el motivo entregado por las reglas del backend.

#### RF-ADM-21 — Acciones permitidas de proceso

**WHEN** el administrativo consulta un componente o servicio **THEN** el panel DEBE
ofrecer, según la respuesta del backend, las acciones existentes de iniciar trabajo,
responder cotización, finalizar componente, corregir finalización y finalizar servicio.

**AND** el panel NO DEBE fabricar una transición directa de estado para sustituir esas
acciones ni ejecutar reglas distintas en el navegador.

**AND** el panel NO DEBE ofrecer un selector libre para asignar estados de servicio o de
componente; cada acción DEBE producir el estado que determine el backend según las reglas
vigentes.

### Cotizaciones y aprobaciones

#### RF-ADM-22 — Crear cotización

**WHEN** el administrativo crea una cotización **THEN** el sistema DEBE asociarla al
servicio y, cuando corresponda, a un componente específico; DEBE permitir múltiples
detalles, descripción, tipo oficial, total neto, observaciones y clasificación
bloqueante/no bloqueante.

**AND** el total oficial DEBE ser el resultado validado por el backend y NO DEBE incluir
subtotal, impuestos ni fecha de vencimiento no aprobados.

**AND** una cotización histórica sin componente DEBE conservarse y mostrarse como
**“Cotización del servicio”**; una cotización nueva DEBE asociarse al componente cuando
corresponda, sin alterar retroactivamente las cotizaciones históricas.

#### RF-ADM-23 — Editar cotización

**WHEN** el administrativo edita una cotización **THEN** el backend DEBE validar si la
edición es compatible con su estado, respuestas y trazabilidad.

**AND** el sistema NO DEBE borrar aprobaciones ni alterar silenciosamente una cotización
que ya tenga una respuesta oficial.

**AND** únicamente una cotización en estado `PENDIENTE` DEBE poder editarse.

**AND** una cotización `APROBADA` o `RECHAZADA` DEBE ser inmutable; cualquier cambio
posterior DEBE realizarse mediante una nueva versión relacionada.

#### RF-ADM-24 — Reenviar cotización rechazada

**WHEN** el administrativo reenvía una cotización rechazada **THEN** el sistema DEBE
crear una nueva versión relacionada con la anterior, conservar la rechazada y mostrar la
relación entre ambas.

**AND** la nueva versión DEBE poder tener sus propios detalles, total y observaciones,
DEBE conservar el tipo de cotización y DEBE iniciar en estado `PENDIENTE` por no tener
aprobaciones.

**AND** el sistema NO DEBE sobrescribir, eliminar ni cambiar retroactivamente la
cotización rechazada.

**AND** las aprobaciones de la cotización anterior DEBEN permanecer asociadas a esa
versión y la nueva versión DEBE comenzar sin aprobaciones.

**AND** el estado de cada versión DEBE determinarse únicamente por las aprobaciones
registradas para esa versión; reenviar una cotización NO DEBE copiar aprobaciones ni
cambiar el estado de la anterior.

**AND** la nueva versión DEBE conservar explícitamente la relación de versionado con la
rechazada, asociarse al mismo componente, conservar el tipo de cotización, generar un
número nuevo y mantener consultables las aprobaciones y el historial de la cotización
anterior.

**AND** la relación DEBE ser opcional en `Cotizacion`, apuntar a la cotización anterior
(`reemplaza_a` o equivalente) y permitir consultar la cadena de versiones sin
sobrescribir ni eliminar ninguna cotización previa.

#### RF-ADM-25 — Aprobaciones externas

**WHEN** el administrativo registra una aprobación o rechazo recibido por WhatsApp,
llamada, presencialmente u otro medio permitido **THEN** el sistema DEBE asociarlo a la
cotización correcta y registrar resultado, medio, fecha, usuario que lo registró,
observación e IP cuando aplique.

**AND** `AprobacionServicio.medio` DEBE admitir únicamente `WEB`, `WHATSAPP`, `LLAMADA`,
`PRESENCIAL` u `OTRO`.

**AND** `Cotizacion.canal` DEBE admitir únicamente `WEB` o `WHATSAPP` como canal de la
cotización, conforme a la especificación 002; el medio de una aprobación externa NO DEBE
ampliar los valores permitidos para el canal de la cotización.

**AND** la cotización DEBE reflejar el resultado registrado y el componente DEBE cambiar
solo según las reglas de la especificación 002.

#### RF-ADM-26 — Historial de cotizaciones

**WHEN** el administrativo consulta cotizaciones **THEN** el sistema DEBE mostrar las
versiones, estados, detalles, aprobaciones y relaciones sin ocultar una cotización
rechazada por existir una versión posterior.

**AND** ninguna cotización DEBE poder eliminarse físicamente desde el panel.

**AND** las cotizaciones sin componente DEBEN identificarse como **“Cotización del servicio”**
en lugar de presentarse como si pertenecieran a un componente.

### Historial y registro técnico

#### RF-ADM-27 — Historial del servicio

**WHEN** el administrativo registra un evento o cambio de estado del servicio **THEN**
el sistema DEBE conservarlo con estado alcanzado, comentario, fecha, usuario y bandera
de visibilidad para el cliente.

**AND** el historial DEBE poder consultarse en orden temporal y no DEBE poder eliminarse
desde el panel.

**AND** los cambios de estado y las acciones importantes DEBEN generar este historial
automáticamente, conservando actor, fecha, estado o acción y el contexto disponible;
la eliminación física de fotografías es la excepción definida en RF-ADM-32.

#### RF-ADM-28 — Registro técnico uno-a-uno

**WHEN** un servicio requiere información técnica **THEN** el sistema DEBE permitir un
único RegistroTecnico opcional asociado uno-a-uno con ese servicio, mediante una
migración de esquema nueva, sin migrar datos históricos.

**AND** el RegistroTecnico DEBE crearse bajo demanda cuando se necesite; no se DEBE crear
automáticamente para todos los servicios existentes o nuevos.

**AND** el registro DEBE contemplar diagnóstico, trabajo realizado, resultado de
pruebas, recomendaciones, observaciones, creado por, actualizado por, fecha de creación
y fecha de actualización.

**AND** esos campos DEBEN mantenerse como información libre y flexible; el sistema NO
DEBE imponer parámetros como RPM, presión, caudal o temperatura en esta versión.

**AND** mientras el servicio exista en el sistema, el administrativo DEBE poder editar
libremente los campos del RegistroTecnico sin crear una versión por cada edición.

**AND** ningún campo del RegistroTecnico DEBE ser visible al cliente en esta versión.

#### RF-ADM-29 — Trazabilidad técnica

**WHEN** se crea o actualiza el registro técnico **THEN** el sistema DEBE conservar qué
administrativo lo creó o actualizó y las fechas correspondientes.

**AND** cada actualización DEBE mantener quién y cuándo realizó la última actualización;
no se DEBE exigir ni crear un historial de versiones de cada edición.

**AND** la interfaz DEBE diferenciar el registro técnico de los datos públicos del
seguimiento mientras su visibilidad pública no esté aprobada.

**AND** el RegistroTecnico DEBE conservarse al desactivar el servicio y NO DEBE poder
eliminarse físicamente desde el panel.

### Fotografías

#### RF-ADM-30 — Gestión de fotografías

**WHEN** el administrativo carga una fotografía **THEN** el sistema DEBE asociarla al
servicio, conservar su referencia de almacenamiento, registrar quién la subió y
permitir describirla, clasificarla y definir `visible_cliente`.

**AND** el servicio DEBE tener como máximo 10 fotografías almacenadas en total;
la cantidad no es obligatoria.

**AND** el formulario público DEBE rechazar una solicitud que incluya más de 5
fotografías, conforme a la especificación 001.

**AND** las fotografías aceptadas por el formulario público DEBEN contar dentro del
límite de 10 fotografías almacenadas del servicio; el panel DEBE rechazar una carga
que haga superar ese límite.

**AND** el sistema NO DEBE guardar ni exigir un dato de origen que distinga fotografías
provenientes del formulario público de las cargadas desde el panel.

**IF** el servicio ya tiene 10 fotografías y se intenta cargar la número 11, **THEN**
el backend DEBE rechazar la carga, no asociar una nueva fotografía y el panel DEBE
informar que se alcanzó el máximo permitido.

**AND** la validación vigente de tamaño y formato DEBE conservarse cuando aplique.

**AND** la solución DEBE poder operar con el mecanismo de almacenamiento vigente sin
acoplar el panel a un proveedor concreto.

#### RF-ADM-31 — Visibilidad fotográfica

**WHEN** el administrativo cambia `visible_cliente` **THEN** el backend DEBE aplicar ese
valor al serializer o representación pública correspondiente.

**AND** una fotografía no visible al cliente NO DEBE aparecer en el seguimiento público,
aunque sí sea consultable por el administrativo autenticado.

#### RF-ADM-32 — Eliminación física de fotografías

**WHEN** el administrativo elimina una fotografía por error o mala calidad **THEN** el
sistema DEBE eliminar la entidad administrativa y la referencia o archivo físico que le
corresponda según el almacenamiento actual, sin dejar una imagen accesible por una
referencia huérfana.

**AND** la eliminación DEBE requerir una acción explícita e informar el resultado, sin
impedir que la fotografía sea eliminada físicamente.

**IF** falla la eliminación del archivo físico **THEN** el sistema DEBE conservar el
registro de la fotografía e informar el error.

**IF** el archivo físico ya no existe **THEN** el sistema DEBE eliminar el registro de
la fotografía.

**AND** nunca DEBEN eliminarse físicamente por esta operación el historial, las
aprobaciones ni las cotizaciones.

### Eliminación, errores y experiencia operativa

#### RF-ADM-33 — Desactivación del servicio

**WHEN** el administrativo solicita retirar un servicio de la operación ordinaria
**THEN** el sistema DEBE desactivarlo mediante `activo=False`, conservar sus datos y no
DEBE eliminarlo físicamente.

**AND** un cliente no DEBE poder consultar mediante seguimiento un servicio desactivado.

#### RF-ADM-34 — Conservación de clientes, aprobaciones e historial

**WHEN** el administrativo intenta eliminar un cliente, una aprobación o un registro de
historial **THEN** el sistema NO DEBE eliminarlos físicamente.

**AND** las relaciones históricas DEBEN seguir siendo consultables por el administrativo
autenticado.

#### RF-ADM-35 — Estados de interfaz

**WHEN** una consulta está en curso **THEN** el panel DEBE mostrar un estado de carga
comprensible y no presentar datos como definitivos.

**WHEN** una consulta no devuelve resultados **THEN** el panel DEBE mostrar un estado
vacío contextual y una forma clara de volver a buscar o quitar filtros.

**WHEN** el backend devuelve un error **THEN** el panel DEBE mostrar un mensaje
comprensible, conservar la sesión si sigue siendo válida y no ocultar el error como si
la operación hubiera sido exitosa.

#### RF-ADM-36 — Feedback de operaciones

**WHEN** una mutación termina correctamente **THEN** el panel DEBE confirmar el resultado
y reflejar los datos actualizados del servidor.

**WHEN** una mutación falla por una regla de negocio, conflicto o falta de autorización
**THEN** el panel DEBE explicar el motivo devuelto por el backend y no asumir que el
cambio se realizó.

**IF** una operación concurre con otra modificación incompatible del mismo recurso
**THEN**, después de bloquear el registro y consultar el estado persistido más reciente,
si la acción ya no cumple las reglas el backend DEBE rechazarla con `409 Conflict`, sin
sobrescribir datos, y el panel DEBE solicitar recargar la información antes de reintentar.

**AND** la operación DEBE ejecutarse dentro de una transacción y DEBE bloquear la fila
del servicio y la fila de la entidad específica que modifica antes de volver a validar
la regla. Esta protección DEBE aplicarse, como mínimo, a observaciones del servicio,
componentes, cotizaciones y reenvíos, aprobaciones, RegistroTecnico, fotografías y
acciones de proceso.

## 6. Requisitos no funcionales

#### RNF-ADM-01 — Seguridad de endpoints

Todos los endpoints administrativos DEBEN requerir autenticación válida y el rol
`ADMINISTRATIVO`; ocultar una opción en la interfaz NO se considera una medida de
seguridad.

#### RNF-ADM-02 — Sesión segura

El panel DEBE reutilizar la sesión segura de la especificación 004: token de acceso solo
en memoria, token de refresco fuera del alcance de JavaScript, renovación, revocación,
CSRF y logout efectivo conforme a esa especificación.

#### RNF-ADM-03 — Privacidad por representación

Las respuestas destinadas al cliente DEBEN filtrar por visibilidad autorizada y por el
servicio asociado al token. Las respuestas administrativas pueden mostrar información
interna solo a una petición autenticada y autorizada.

#### RNF-ADM-04 — Responsive y accesible

El panel DEBE funcionar en móvil, tablet y escritorio; sus controles DEBEN tener nombres
accesibles, foco visible, contraste suficiente, objetivos táctiles utilizables y no
depender solo del color para comunicar estado o error.

#### RNF-ADM-05 — Consistencia del idioma y del dominio

Los textos visibles del panel DEBEN estar en español, usar etiquetas comprensibles para
una empresa técnica e industrial y distinguir los conceptos administrativos de los
públicos. Los valores internos de estados pueden conservarse como códigos mientras se
muestran sus etiquetas en español.

#### RNF-ADM-06 — Integridad y trazabilidad

Las operaciones relevantes DEBEN ser atómicas desde la perspectiva del usuario: no se
debe confirmar parcialmente una cotización, aprobación, acción de proceso o fotografía.
Los cambios relevantes DEBEN conservar usuario y fecha cuando el modelo lo requiera.

Los cambios de estado y las acciones importantes DEBEN generar historial automático con
el actor, fecha, estado o acción y contexto suficiente para reconstruir lo ocurrido.

Las operaciones concurrentes DEBEN resolverse explícitamente mediante transacciones y bloqueo
de fila en el backend para las mutaciones críticas, sin pérdida silenciosa de datos ni
sobrescritura de una versión más reciente. Después de bloquear el registro, si la acción ya
no cumple las reglas con el estado persistido más reciente, la operación DEBE devolverse con
`409 Conflict` y no modificar los datos confirmados por la otra operación. Esta protección NO
DEBE requerir Redis ni campos de versión nuevos.

Para observaciones del servicio, componentes, cotizaciones y reenvíos, aprobaciones,
RegistroTecnico, fotografías y acciones de proceso, la transacción DEBE bloquear primero
la fila del servicio y también la fila de la entidad específica afectada; luego DEBE
consultar nuevamente el estado persistido y evaluar la regla. Si la regla falla con ese
estado, DEBE devolver `409 Conflict` y no debe confirmar ningún cambio parcial.

Las actualizaciones del RegistroTecnico DEBEN conservar como mínimo el usuario y la fecha
de su última actualización, sin requerir versionado de cada edición.

La eliminación física de una fotografía es una excepción a la generación de historial
automático: no DEBE registrarse en el historial del servicio.

#### RNF-ADM-07 — Sin arquitectura adicional

La funcionalidad DEBE operar con la arquitectura, dependencias y sesión aprobadas. No
DEBE requerir Redis, WebSockets, Channels, nuevas dependencias ni una cuenta del cliente.

## 7. Modelo y migraciones

1. `Cotizacion` DEBE incorporar una relación opcional consigo misma (`reemplaza_a` o
   equivalente), conservar su número propio y mantener intacta la cotización anterior.
   La relación DEBE permitir consultar la cadena completa de versiones. Esto requiere una
   migración de esquema explícita.
2. `Cotizacion.canal` ya existe en el modelo vigente y DEBE reutilizarse sin una nueva
   migración para ese campo. DEBE conservar el catálogo cerrado `WEB`/`WHATSAPP` de la
   especificación 002. `AprobacionServicio.medio` DEBE conservar el catálogo cerrado
   `WEB`/`WHATSAPP`/`LLAMADA`/`PRESENCIAL`/`OTRO`; ambos conceptos DEBEN permanecer
   separados.
3. `RegistroTecnico` DEBE añadirse como relación opcional uno-a-uno con `Servicio` en una
   migración de esquema explícita. La migración no DEBE crear ni transformar registros
   históricos; el registro se crea bajo demanda.
4. El formulario público DEBE validar máximo 5 fotografías por solicitud. El sistema DEBE
   almacenar como máximo 10 fotografías por servicio, contando las aceptadas por el
   formulario público y las cargadas desde el panel. No se DEBE guardar el origen de la
   fotografía ni mantener contadores separados por origen.
5. La concurrencia crítica DEBE resolverse con una transacción que bloquee la fila del
   servicio y la fila de la entidad específica afectada para observaciones del servicio,
   componentes, cotizaciones y reenvíos, aprobaciones, RegistroTecnico, fotografías y
   acciones de proceso. Si la regla falla tras leer el estado bloqueado, DEBE devolver
   `409 Conflict`. No se añade Redis ni un campo de versión.

## 8. Casos límite

- **CL-ADM-01.** No existen servicios activos: el dashboard muestra ceros y el listado
  muestra un estado vacío, sin error.
- **CL-ADM-02.** La búsqueda o combinación de filtros no encuentra resultados: se
  muestran los filtros aplicados y una forma de limpiarlos.
- **CL-ADM-03.** Un servicio tiene varios componentes y solo uno tiene una cotización
  bloqueante rechazada: ese componente se muestra “En espera por cotización rechazada”;
  los demás conservan sus propias acciones y el servicio no se elimina ni se cierra
  automáticamente.
- **CL-ADM-04.** Una cotización bloqueante está pendiente: iniciar trabajo se rechaza
  por backend aunque el usuario intente invocar la operación fuera de la interfaz.
- **CL-ADM-05.** Una cotización rechazada se reenvía varias veces: cada reenvío crea una
  versión relacionada con la anterior, conserva componente, tipo e historial de la
  anterior, genera un número nuevo, comienza sin aprobaciones y queda sujeta únicamente
  a sus propias aprobaciones; todas las versiones siguen consultables.
- **CL-ADM-06.** Se intenta editar o borrar una cotización con aprobación: no se pierde
  la aprobación ni se altera la evidencia histórica; las cotizaciones aprobadas y
  rechazadas son inmutables.
- **CL-ADM-07.** Se intenta eliminar un componente con historial o cotizaciones: el
  sistema lo rechaza y conserva permanentemente el componente y su trazabilidad; los datos
  descriptivos permitidos siguen siendo corregibles y no se crea un campo `activo` nuevo.
- **CL-ADM-08.** Se elimina una fotografía subida por error: se elimina su referencia y
  archivo físico según el almacenamiento vigente; si falla el borrado físico se conserva
  el registro y se informa el error, y si el archivo ya no existe se elimina el registro.
- **CL-ADM-09.** Un registro técnico no existe todavía: el detalle ofrece su creación;
  si existe, ofrece su consulta y edición libre mientras el servicio exista; la edición
  actualiza el responsable y la fecha de última actualización sin crear una versión nueva.
- **CL-ADM-10.** La sesión expira durante una carga o una operación: el backend rechaza
  la petición, no se muestra como exitosa y la interfaz conduce al login según la spec
  004.
- **CL-ADM-11.** Un usuario manipula un identificador de componente, cotización o
  fotografía de otro servicio: el backend rechaza la operación y no modifica el objeto
  ajeno.
- **CL-ADM-12.** Todos los componentes están finalizados pero el servicio no se ha
  cerrado: el panel muestra la acción manual de finalizar servicio; no lo finaliza por
  sí solo.
- **CL-ADM-13.** Un servicio desactivado conserva historial, cotizaciones y fotografías:
  queda fuera de la operación ordinaria y de la consulta pública, pero permanece
  disponible para el administrativo autorizado.
- **CL-ADM-14.** Una fotografía está marcada como no visible: aparece al administrativo
  pero no al cliente, aun cuando el cliente conozca el código del servicio.
- **CL-ADM-15.** Una solicitud o detalle falla temporalmente: el panel distingue error
  de estado vacío y permite reintentar sin duplicar una operación ya confirmada.
- **CL-ADM-16.** Dos administrativos intentan modificar el mismo recurso: después de
  bloquear el registro, si la segunda operación ya no cumple las reglas con el estado
  persistido más reciente, pierde con `409 Conflict`; no sobrescribe la modificación
  confirmada y el panel solicita recargar antes de reintentar. Se usa transacción y
  bloqueo de fila del servicio y de la entidad específica, sin Redis ni campo de versión.
- **CL-ADM-17.** El dashboard contiene servicios desactivados y activos: solo los activos
  cuentan o aparecen en la operación; los desactivados permanecen fuera del dashboard.
- **CL-ADM-18.** El token de seguimiento se ofrece desde el detalle: nunca se muestra
  completo como texto y solo están disponibles las acciones de copiar o abrir enlace.
- **CL-ADM-19.** Un servicio tiene exactamente 10 fotografías y se intenta cargar otra:
  el backend rechaza la número 11, no crea ni asocia una fotografía adicional y el panel
  informa el límite; las validaciones vigentes de tamaño y formato siguen aplicándose
  cuando corresponda.
- **CL-ADM-20.** Se intenta editar un dato del cliente o un dato del servicio distinto de
  `observaciones_internas`: el backend rechaza la operación y conserva los datos sin
  cambios.
- **CL-ADM-21.** El panel consulta una cotización histórica sin componente: la muestra como
  “Cotización del servicio”, conserva sus relaciones históricas y no intenta asignarle un
  componente retroactivamente.
- **CL-ADM-22.** El administrativo intenta cambiar directamente un estado desde un selector:
  la interfaz no ofrece esa operación y, si se invoca manualmente, el backend la rechaza; el
  estado solo cambia mediante una acción de proceso válida.
- **CL-ADM-23.** Una cotización solo puede registrar `WEB` o `WHATSAPP` en `canal`, aunque
  una aprobación externa registre `LLAMADA`, `PRESENCIAL` u `OTRO` en `medio`; los dos
  catálogos se validan por separado y `canal` se reutiliza sin migración nueva.
- **CL-ADM-24.** Se reenvía una cotización rechazada varias veces: cada nueva cotización
  recibe un número nuevo, apunta a su antecedente mediante `reemplaza_a` o equivalente y
  comienza sin aprobaciones; cada versión conserva sus propias aprobaciones y estado,
  ninguna anterior se sobrescribe ni se elimina y toda la cadena sigue consultable.
- **CL-ADM-25.** Un servicio existente no tiene RegistroTecnico: el panel lo crea bajo
  demanda; la migración solo modifica el esquema y no genera registros a partir de datos
  históricos.
- **CL-ADM-26.** Una solicitud pública intenta superar 5 fotografías: se rechaza el
  archivo que excede el máximo de la solicitud. Las fotografías aceptadas cuentan en el
  máximo almacenado de 10 del servicio; una carga que supere ese total se rechaza. No se
  registra el origen de ninguna fotografía ni se usan contadores separados.
- **CL-ADM-27.** Dos operaciones concurrentes afectan observaciones, componentes,
  cotizaciones o reenvíos, aprobaciones, RegistroTecnico, fotografías o una acción de
  proceso: cada una bloquea el servicio y la entidad específica dentro de una transacción;
  la que ya no cumpla la regla con el estado persistido devuelve `409 Conflict` sin cambios
  parciales.

## 9. Fuera de alcance

- Crear o administrar usuarios administrativos, nuevos roles, permisos diferenciados o
  una cuenta para el cliente.
- Crear una vista pública nueva o decidir qué información técnica se publicará al cliente.
- Regenerar o revocar el enlace privado de seguimiento; en esta versión el enlace solo
  puede copiarse o abrirse desde el panel.
- WhatsApp Business API, envío automático de mensajes, correo automático, PDF, firma
  digital, pagos, facturación, inventario, e-commerce o entidad `Entrega`.
- Chat interno, tiempo real mediante WebSockets, Redis, Channels, SSE o arquitectura de
  microservicios.
- Parámetros estructurados de banco de pruebas como RPM, presión, caudal o temperatura.
- Eliminación física de servicios, clientes, cotizaciones, aprobaciones, historial o
  componentes que deban conservar trazabilidad.
- Cálculo de impuestos, subtotal, vencimientos o valores de mano de obra no definidos
  por el negocio.
- Definir políticas no confirmadas sobre transporte, devolución de piezas o rechazo de
  costos adicionales más allá de las reglas ya aprobadas en la especificación 002.

## 10. Criterios de finalización

1. Un administrativo autenticado puede abrir dashboard, listado, detalle y operaciones;
   una petición no autenticada o de una cuenta inactiva no obtiene datos.
2. El dashboard muestra todos los indicadores aprobados y sus cifras provienen del
   backend; todos cuentan solo servicios activos, “recientes” son los últimos 10 por
   `fecha_solicitud` descendente y “pendientes” aplican exactamente sus estados y
   bloqueos aprobados, incluido `RECHAZADO_BLOQUEANTE`; `NO_APROBADO` cuenta si sigue
   activo y ningún desactivado aparece.
3. El listado permite búsqueda case-insensitive y sin tildes por código, nombre del
   cliente y empresa, combinable con estado; usa 20 elementos por página y orden
   predeterminado por `fecha_solicitud` descendente, además de tabla o tarjetas según
   el dispositivo.
4. El detalle consolida cliente, componentes, cotizaciones, aprobaciones, historial,
   fotografías, seguimiento, estado y registro técnico.
5. Las acciones de iniciar trabajo, responder cotización, finalizar componente,
   corregir finalización y finalizar servicio respetan las reglas de la especificación
   002 y dejan trazabilidad.
   6. Las cotizaciones admiten múltiples detalles; solo las `PENDIENTE` se editan,
     `APROBADA` y `RECHAZADA` son inmutables, y una rechazada se reenvía como nueva
     versión relacionada mediante `reemplaza_a` o equivalente, con componente, tipo,
     historial y número nuevo, sin sobrescritura ni eliminación; la versión anterior
     conserva sus aprobaciones, la nueva comienza sin aprobaciones y cada estado depende
     solo de las aprobaciones de su propia versión.
  7. Las aprobaciones externas conservan resultado, medio, fecha, usuario, observación e
    IP cuando aplique; `Cotizacion.canal` solo admite `WEB`/`WHATSAPP` y
    `AprobacionServicio.medio` solo admite `WEB`/`WHATSAPP`/`LLAMADA`/`PRESENCIAL`/`OTRO`.
  8. Existe un RegistroTecnico opcional uno-a-uno por servicio, creado bajo demanda sobre
     un esquema incorporado mediante migración sin datos históricos, con los cinco textos libres,
     autoría y fechas; puede editarse libremente
    mientras el servicio exista, sin versionar cada edición; conserva quién y cuándo lo
    actualizó por última vez, se conserva al desactivar, no se elimina físicamente y
    ningún campo es visible al cliente.
 9. El administrativo solo puede editar `observaciones_internas` del servicio; no puede
    editar los demás datos del servicio ni los datos del cliente. Puede gestionar,
     agregar, editar y eliminar componentes conforme a la política de trazabilidad; un
     componente con historial o cotizaciones se conserva permanentemente, aunque sus datos
     descriptivos permitidos puedan corregirse, sin añadir un campo `activo`.
  10. Las fotografías permiten cargar, describir, clasificar, marcar visibilidad y borrar
     físicamente archivo y referencia según el almacenamiento vigente; el formulario
     público valida como máximo 5 por solicitud y el servicio conserva como máximo 10
     almacenadas en total, sin guardar el origen; la número 11 se rechaza sin crear asociación, se conservan las
    validaciones vigentes de tamaño/formato cuando apliquen, un fallo conserva el registro
    e informa, y un archivo inexistente permite eliminarlo.
 11. Servicios, clientes, cotizaciones, aprobaciones, historial y componentes se
     conservan conforme a las reglas de eliminación; un servicio solo se desactiva.
 12. El panel tiene estados de carga, vacío, error y confirmación de mutaciones, y es
     usable y accesible en móvil, tablet y escritorio.
 13. Los datos internos y tokens privados no se exponen al cliente ni se protegen solo
     mediante la interfaz; el token nunca se muestra completo y solo se copia o abre
     mediante acciones explícitas.
  14. Los cambios de estado y acciones importantes dejan historial automático, excepto la
       eliminación física de fotografías según RF-ADM-32. Las mutaciones de observaciones,
       componentes, cotizaciones y reenvíos, aprobaciones, RegistroTecnico, fotografías y
       acciones de proceso usan una transacción que bloquea la fila del servicio y la
       entidad específica; si el estado persistido más reciente invalida la acción el
       backend responde `409 Conflict`, sin sobrescritura ni cambios parciales, y el panel
       solicita recargar. No se usa Redis ni campo de versión. El panel no permite
       seleccionar libremente un estado: las acciones válidas determinan el resultado en
       el backend.
