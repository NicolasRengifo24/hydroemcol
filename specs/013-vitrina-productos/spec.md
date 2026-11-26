# Spec 013 — Vitrina digital de productos

**Especificación funcional · Hidroemcol**
**Estado: aprobada**
**Actualización (2026-11-20):** se retira la administración del carrusel, se documenta el carrusel editorial visible que existe hoy y se registra la carga de las siete imágenes iniciales, ya aprobadas y visibles.

## 1. Contexto y objetivos

Hidroemcol quiere dar visibilidad a repuestos y novedades mediante Facebook e Instagram y llevar
tráfico cualificado a su página. La sección actual de productos está incompleta. Se construirá una
vitrina digital sencilla, no un catálogo exhaustivo ni una tienda en línea.

Objetivos comerciales, en orden:

1. Solicitudes de cotización.
2. Consultas por WhatsApp.
3. Posicionamiento de marca.
4. Visitas a la página.

El público comprende personas y empresas relacionadas con hidráulica, maquinaria, mantenimiento,
industria, talleres y actividades afines, con alcance nacional en Colombia. Mostrar un producto no
significa que tenga precio, stock o disponibilidad comercial inmediata.

## 2. Alcance

Incluye:

- Ruta pública `/productos`, con capacidad objetivo de 20 a 50 productos.
- Novedades ordenadas por fecha de creación descendente y, en caso de empate, por identificador
  interno descendente; el identificador no se muestra públicamente.
- Productos disponibles y sobre pedido, sin publicar esa condición comercial.
- Categorías: **Bombas hidráulicas**, **Reparación y mantenimiento**, **Control hidráulico** y
  **Transmisión**.
- Entidad persistente **Producto**; **ImagenCarrusel** se conserva como contrato legado de solo
  lectura, sin administración.
- El modelo persistente ya incorpora **Producto** e **ImagenCarrusel**; este cambio no añade
  migración. La API administrativa y el panel se coordinan únicamente con Producto.
- CRUD administrativo de productos; “eliminar” significa ocultamiento recuperable, no borrado
  definitivo en esta fase.
- Carrusel visible editorial y estático en el frontend (`HeroProductos`): cinco piezas configuradas
  con sus imágenes, texto comercial por pieza, texto comercial del bloque, CTA de WhatsApp e
  indicadores visuales. Avanza automáticamente con transiciones suaves y se detiene ante
  interacción, pestaña oculta o preferencia de movimiento reducido. Su contenido no se administra
  desde el backend ni desde el panel.
- Contrato público legado `carrusel` derivado de **ImagenCarrusel**: solo lectura, sin gestión
  desde la aplicación y no renderizado por la página actual.
- WhatsApp únicamente dentro de `/productos`: mensaje aprobado en las tarjetas de Producto y
  mensaje del CTA del carrusel editorial, con UTM y medición mediante Meta Pixel.
- Orientación paso a paso de Meta Business, Meta Pixel y medición, sin solicitar credenciales.
- SEO de `/productos`, Open Graph, canonical, texto alternativo y sitemap.
- Enlace `Productos` en la navegación; CTA `Ver repuestos` en `/soluciones` y en el hero de inicio.
- Administración por una sola persona mediante la autenticación y las protecciones vigentes del
  panel; no se crea una entidad de auditoría ni un historial de operaciones para esta vitrina.

Las siete imágenes iniciales de productos ya están cargadas y visibles en la vitrina, con la
siguiente correspondencia aprobada. Los nombres, descripciones y textos alternativos salen de los
nombres de archivo aprobados; no se inventaron marcas, referencias, precios ni stock.

| Imagen | Producto | Categoría (`categoria`) | Descripción general y texto alternativo |
|---|---|---|---|
| `Bombas-de-piñones-piloto-y-de-pre-carga-para-todas-las-aplicaciones.jpeg` | Bombas de piñones piloto y de pre-carga para todas las aplicaciones | `bombas-hidraulicas` | Bombas de piñones piloto y de pre-carga para todas las aplicaciones |
| `Bombas-remanofacturadas.jpeg` | Bombas remanufacturadas | `bombas-hidraulicas` | Bombas remanufacturadas |
| `Retenedores-hidráulicos-de-alta-presión-para-bombas-y-motores.jpeg` | Retenedores hidráulicos de alta presión para bombas y motores | `reparacion-mantenimiento` | Retenedores hidráulicos de alta presión para bombas y motores |
| `Piezas-internas-para-reparación-de-bombas-y-motores.jpeg` | Piezas internas para reparación de bombas y motores | `reparacion-mantenimiento` | Piezas internas para reparación de bombas y motores |
| `Kit-de-empaquetadura-para-bombas-y-motores.jpeg` | Kit de empaquetadura para bombas y motores | `reparacion-mantenimiento` | Kit de empaquetadura para bombas y motores |
| `Controles-y-válvulas-de-regulación.jpeg` | Controles y válvulas de regulación | `control-hidraulico` | Controles y válvulas de regulación |
| `Cupling-y-ejes-de-conección.jpeg` | Cupling y ejes de conexión | `transmision` | Cupling y ejes de conexión |

Las URL/referencias de las siete imágenes quedan registradas en los Productos correspondientes.

## 3. Fuera de alcance

- Precios, stock, inventario o disponibilidad comercial pública.
- Carrito, pagos, checkout, e-commerce o cuentas de cliente.
- Páginas individuales de producto, variantes indexables, productos relacionados o fichas
  avanzadas.
- Video de productos.
- WhatsApp Business API.
- TikTok en la primera versión.
- Administración del carrusel: panel, ruta, menú, hooks, tipos, endpoints CRUD, serializer
  administrativo, tests administrativos y reglas de orden, posiciones libres, reactivación o
  límite de imágenes.
- Edición del carrusel visible desde backend o desde el panel: su contenido es editorial y estático
  en el frontend.
- Carrusel que seleccione productos o consuma el campo `carrusel` de la API pública: el carrusel
  visible muestra piezas configuradas y el campo legado no se renderiza.
- Borrado definitivo de productos en esta fase.
- Eventos de medición propios del carrusel; el CTA editorial usa el mensaje actual y no crea uno
  nuevo.
- Auditoría, versionado completo, historial de operaciones, eventos distribuidos o cualquier
  entidad adicional para registrar operaciones administrativas.
- Marcas, horarios, precios, disponibilidad o copy comercial no confirmados.

## 4. Actores

| Actor | Acciones |
|---|---|
| Visitante | Consulta productos, filtra por categoría y solicita información por WhatsApp. |
| Visitante de Facebook/Instagram | Entra por una campaña etiquetada y puede ser medido sin compartir datos sensibles. |
| ADMINISTRATIVO | Una sola persona administra productos con la autenticación del panel existente; no administra el carrusel. |
| Meta Pixel | Recibe únicamente los eventos y parámetros aprobados en esta spec. |

## 5. Modelo conceptual

### Producto

Entidad persistente con exactamente una categoría. Sus campos funcionales son: nombre, categoría,
descripción general, imagen, texto alternativo, visible, fecha de creación y fecha de actualización.
La imagen se representa en la base de datos mediante una URL o referencia al almacenamiento
Cloudflare; el binario no se guarda en la base de datos.

### ImagenCarrusel (contrato legado)

Entidad persistente independiente de Producto. Se conserva como contrato público de solo lectura:
la API pública expone el campo `carrusel` con las imágenes visibles, sin gestión desde la
aplicación. La página actual no renderiza ese campo. Sus campos persistidos son imagen,
descripción de la imagen, orden, visible y fecha de creación. No se crea, edita, oculta, reordena
ni elimina desde esta aplicación y no genera reglas de posiciones ni de límite.

### Carrusel editorial visible (`HeroProductos`)

Contenido editorial estático del frontend, independiente de Producto y del contrato legado. Muestra
cinco piezas configuradas en código — bombas remanufacturadas; bombas de piñones, piloto y
pre-carga; controles y válvulas de regulación; piezas internas para bombas y motores; y retenedores
de alta presión —, cada una con imagen, tipo, nombre y descripción, sin precio ni dato de stock.

El bloque incluye el texto comercial actual: etiqueta “REPUESTOS HIDRÁULICOS”, título “El repuesto
que necesita su equipo está a un mensaje.”, descripción “Compare opciones con nuestro equipo
técnico, identifique el repuesto y solicite su cotización. Importación sobre pedido y envíos
nacionales.” y CTA “PREGUNTAR POR MI REPUESTO”, que abre WhatsApp con el mensaje “Hola, quiero
preguntar por un repuesto hidráulico y solicitar una cotización.”. También muestra indicadores
visuales del carrusel. Este contenido es el que existe hoy y no se administra desde backend ni
desde el panel.

### Campaña y medición

Los parámetros UTM de una visita se conservan durante la sesión y se asocian a los eventos de la
vitrina cuando existan. La medición solo contempla `ViewContent` para la visita a `/productos` y
`Contact` para el clic de WhatsApp de un Producto. Un clic a `wa.me` representa un clic, no una
conversación confirmada. El carrusel editorial no emite eventos de medición y su CTA no añade un
evento distinto de los dos aprobados.

### Evolución del modelo persistente y decisión consciente sobre trazabilidad

El modelo persistente incorpora **Producto** e **ImagenCarrusel**; este cambio no añade migración.
La administración se refleja de forma coherente en la API administrativa y el panel solo para
Producto; ImagenCarrusel queda como contrato público de solo lectura y el carrusel visible es
contenido editorial estático. El backend es la autoridad para validar, autorizar, persistir y
publicar las operaciones de Producto.

Se adopta conscientemente la Opción A de trazabilidad: no se crea una entidad de auditoría ni un
historial de operaciones para Producto ni para la entidad legada ImagenCarrusel. Producto conserva
únicamente sus fechas de creación y actualización; ImagenCarrusel conserva su fecha de creación,
su estado visible y su orden guardado, sin que existan operaciones de gestión sobre ella. No se
registra operación por operación ni usuario histórico.

Esta es una simplificación consciente y una excepción al principio general de trazabilidad. Se
justifica por el bajo riesgo de la vitrina y porque la administración de Producto está a cargo de
una sola persona. La seguridad administrativa, la autenticación, CSRF, la autoridad del backend, la
visibilidad y las validaciones continúan siendo obligatorias para Producto.

### Impacto aprobado de la evolución

- **Base de datos:** el modelo persistente incluye Producto e ImagenCarrusel; este cambio no añade
  migración. Se conservan referencias a Cloudflare y no binarios en PostgreSQL.
- **API pública:** exponer únicamente productos visibles, aplicando filtros, orden y textos
  alternativos desde el backend, y mantener el campo `carrusel` como contrato legado de solo
  lectura. La regla constitucional `visible_cliente=True` sigue aplicando a serializers públicos de
  servicios y datos de clientes; Producto e ImagenCarrusel no son datos de clientes ni servicios y
  usan su propio campo `visible`.
- **API administrativa:** permitir las operaciones aprobadas sobre productos con autenticación,
  validación y protección vigente del panel. No existen operaciones administrativas del carrusel.
- **Panel:** ofrecer la gestión editorial de productos y categorías, además de mostrar el resultado
  de las operaciones sin convertirse en la autoridad de las reglas. No incluye gestión del carrusel.
- **Frontend:** consumir el contrato público de productos y las operaciones administrativas,
  representar estados y aplicar la experiencia visual y accesible; mostrar el carrusel editorial
  estático, sin decidir visibilidad, autorización ni orden de los productos.

### Bloqueos y dependencias de implementación

- La persistencia de Producto e ImagenCarrusel es un requisito previo ya cubierto; este cambio no
  introduce migración ni dependencias nuevas.
- La API pública, la API administrativa de productos, el panel de productos y el frontend deben
  coordinarse con el contrato resultante; el frontend no puede sustituir una regla del backend con
  estado local. El carrusel editorial es la excepción documentada: es contenido estático y no
  depende del backend.
- La carga inicial de las siete imágenes ya está resuelta: los siete productos están cargados y
  visibles con la correspondencia aprobada en §2. No se inventaron descripciones ni textos
  alternativos; no queda ninguna tabla pendiente de aprobación.
- La publicación en producción queda bloqueada hasta resolver la decisión legal sobre consentimiento
  y privacidad de Meta Pixel. Esta decisión no bloquea la especificación ni la implementación local.
- La conservación de binarios sustituidos u ocultados y el lugar de publicación de la guía siguen
  siendo decisiones operativas pendientes; no autorizan borrar referencias ni pedir credenciales.

## 6. Requisitos funcionales (EARS)

### Fuente de datos y vitrina

#### RF-VIT-01 — Fuente pública

**WHEN** una persona visita `/productos` **THEN** el sistema DEBE obtener la lista desde la fuente
de datos pública y mostrar únicamente productos cuyo estado `visible` haya sido autorizado por el
servidor, sin exigir autenticación.

#### RF-VIT-02 — Datos visibles

**WHEN** se muestra un producto **THEN** DEBE presentar nombre, categoría, descripción general,
imagen con texto alternativo y botón de WhatsApp, sin precio, stock ni disponibilidad comercial.

#### RF-VIT-03 — Orden de productos

**WHEN** se carga la lista sin filtro **THEN** el sistema DEBE ordenar los productos visibles por
fecha de creación descendente y, en caso de empate, por identificador interno descendente. El
identificador interno NO DEBE mostrarse públicamente.

#### RF-VIT-04 — Categorías y query string

**WHEN** la persona selecciona una categoría **THEN** el sistema DEBE reflejarla en el query string
con el valor exacto aprobado y la fuente pública DEBE devolver solo productos visibles de esa
categoría:

| Categoría | Valor de `categoria` |
|---|---|
| Bombas hidráulicas | `bombas-hidraulicas` |
| Reparación y mantenimiento | `reparacion-mantenimiento` |
| Control hidráulico | `control-hidraulico` |
| Transmisión | `transmision` |

Por ejemplo: `/productos?categoria=bombas-hidraulicas`.

**IF** la categoría no pertenece al catálogo aprobado **THEN** el sistema DEBE mostrar un estado
vacío o filtro inválido sin revelar otros productos ni inventar categorías.

#### RF-VIT-05 — Visibilidad completa

**IF** un producto está `oculto` **THEN** NO DEBE aparecer en la respuesta pública, filtros,
sitemap, Open Graph, resultados indexables ni metadatos.

#### RF-VIT-06 — Estados de consulta

**WHEN** la fuente pública está cargando **THEN** la vitrina DEBE mostrar un estado de carga.

**IF** la respuesta no contiene productos para el filtro vigente **THEN** DEBE mostrar un estado
vacío claro sin revelar ocultos.

**IF** la fuente responde con error **THEN** DEBE mostrar un estado de error comprensible y un
control para reintentar, sin presentar datos parciales como completos.

#### RF-VIT-07 — Variantes

**WHEN** un producto agrupa variantes o referencias **THEN** DEBE conservar una descripción
general en la misma vitrina; NO DEBE crear una página individual ni una URL indexable por variante.

### Producto y administración

#### RF-VIT-08 — Entidad Producto

**WHEN** se crea o actualiza un Producto **THEN** DEBE conservar nombre, una sola categoría válida,
descripción general, imagen, texto alternativo, visible y sus fechas de creación y actualización.

#### RF-VIT-09 — Crear y editar

**WHEN** un ADMINISTRATIVO autenticado guarda un producto válido **THEN** el sistema DEBE crearlo
o actualizarlo y DEBE reflejarlo públicamente solo si `visible` es verdadero.

#### RF-VIT-10 — Ocultar y mostrar

**WHEN** el ADMINISTRATIVO oculta o muestra un producto **THEN** el sistema DEBE cambiar `visible`
en el servidor y publicar el resultado inmediatamente.

#### RF-VIT-11 — Eliminar recuperable

**WHEN** el ADMINISTRATIVO pulsa “Eliminar” sobre un producto **THEN** el sistema DEBE ocultarlo de
forma recuperable, conservar sus datos y permitir mostrarlo nuevamente desde el panel. NO DEBE
ejecutar borrado definitivo en esta fase. Esta operación NO EXISTE para el carrusel.

#### RF-VIT-12 — Validación de producto

**IF** falta nombre, categoría, descripción general, imagen o texto alternativo **THEN** el
sistema DEBE rechazar el guardado y explicar el campo faltante.

#### RF-VIT-13 — Imagen de producto

**WHEN** se carga o reemplaza la imagen de un Producto **THEN** el sistema DEBE aceptar únicamente
JPG, JPEG, PNG o WEBP de máximo 5 MB, una imagen por producto, y DEBE validar el MIME real y
redimensionarla o comprimirla para evitar archivos pesados antes de publicarla.

**IF** el MIME real, formato, tamaño o procesamiento no es válido **THEN** NO DEBE guardar la
referencia ni publicar una imagen rota.

#### RF-VIT-14 — Carga inicial de las siete imágenes

**WHEN** se publica la vitrina **THEN** los siete productos iniciales DEBEN estar cargados y
visibles con la correspondencia aprobada de imagen, Producto, categoría, descripción y texto
alternativo indicada en §2.

**AND** las descripciones y los textos alternativos DEBEN salir de los nombres de archivo aprobados,
sin inventar marcas, referencias, precios ni stock.

**WHEN** se verifica la carga inicial **THEN** las URL/referencias de las siete imágenes DEBEN quedar
registradas en los Productos correspondientes y NO DEBE quedar ninguna tabla pendiente de
aprobación.

### Carrusel editorial y contrato legado

#### RF-VIT-15 — Contrato legado de solo lectura

**WHEN** la API pública expone el campo `carrusel` derivado de ImagenCarrusel **THEN** DEBE hacerlo
como contenido de solo lectura, sin operaciones de creación, edición, ocultamiento, reordenamiento
ni eliminación desde esta aplicación.

**AND** la página `/productos` NO DEBE renderizar ese campo: el carrusel visible es el contenido
editorial estático descrito en §5. El contrato se conserva sin ser gestionado ni eliminado.

#### RF-VIT-19 — Contenido editorial del carrusel visible

**WHEN** se muestra `/productos` **THEN** el carrusel editorial DEBE presentar las cinco piezas
configuradas con sus imágenes, tipo, nombre y descripción, además del texto comercial actual del
bloque y sus indicadores visuales.

**AND** el bloque DEBE incluir el CTA “PREGUNTAR POR MI REPUESTO” hacia WhatsApp con el mensaje
“Hola, quiero preguntar por un repuesto hidráulico y solicitar una cotización.”, sin inventar
marcas, referencias, precios ni datos de stock.

**AND** el contenido del carrusel NO DEBE depender de la base de datos, de la API pública ni del
panel: no existe gestión administrativa del carrusel.

#### RF-VIT-20 — Autoplay, pausa y navegación del carrusel editorial

**WHEN** el carrusel editorial tiene dos o más imágenes configuradas **THEN** DEBE avanzar
automáticamente con una transición suave, sin controles visibles de reproducción.

**AND** el movimiento automático DEBE detenerse cuando la pestaña esté oculta, al pasar el puntero,
al recibir foco, tras una interacción manual de navegación y cuando `prefers-reduced-motion` lo
solicite. La navegación manual DEBE seguir disponible por teclado y gestos táctiles.

**IF** existe una sola imagen configurada **THEN** NO DEBE simular movimiento ni controles
innecesarios. **IF** no hay imágenes configuradas **THEN** el carrusel NO DEBE renderizarse.

**AND** el carrusel DEBE conservar su presentación legible y sin desplazamiento horizontal propio en
móvil, tablet y escritorio.

### Navegación y WhatsApp

#### RF-VIT-22 — Navegación

**WHEN** se muestra la navegación pública **THEN** DEBE incluir `Productos` hacia `/productos`.

**WHEN** se muestra el CTA de repuestos en `/soluciones` **THEN** DEBE decir `Ver repuestos` y
dirigir a `/productos`.

**WHEN** se muestra el hero de inicio **THEN** DEBE incluir `Ver repuestos` junto a `Solicitar
servicio`, con destino `/productos`.

#### RF-VIT-23 — Mensaje aprobado de producto

**WHEN** la persona pulsa WhatsApp en un Producto **THEN** el sistema DEBE usar exactamente este
mensaje, sustituyendo únicamente el nombre:

`Hola, quiero información sobre el producto “[NOMBRE DEL PRODUCTO]” que vi en la página de Hydroemcol.`

DEBE usar el número y la utilidad de WhatsApp existentes; el número NO es configurable por
producto. WhatsApp se usa únicamente dentro de `/productos`: con el mensaje aprobado en las
tarjetas de Producto y con el mensaje del CTA del carrusel editorial definido en RF-VIT-19. No se
crea un número ni una utilidad distinta para el carrusel.

#### RF-VIT-24 — Clic no confirmado

**WHEN** se abre `wa.me` **THEN** el sistema DEBE indicar que WhatsApp se abrió y NO DEBE afirmar
que se envió, inició o respondió una conversación.

### UTM y Meta Pixel

#### RF-VIT-25 — UTM durante la sesión

**WHEN** una visita llega con `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` o
`utm_term` **THEN** el sistema DEBE conservar los valores disponibles durante la sesión y
asociarlos a los eventos posteriores de la vitrina, sin inventar valores ausentes.

#### RF-VIT-26 — Pixel configurable

**WHEN** existe un identificador de Meta Pixel en la configuración de despliegue **THEN** el
sistema DEBE habilitar la medición con ese identificador y NO DEBE exigir credenciales en la
interfaz pública.

**IF** el identificador no existe o el Pixel no carga **THEN** la vitrina y sus CTA DEBEN seguir
funcionando sin errores bloqueantes.

#### RF-VIT-27 — Eventos y parámetros aprobados

**WHEN** Meta Pixel está habilitado **THEN** DEBE enviar únicamente estos dos eventos:

| Evento | Disparador | Parámetros permitidos |
|---|---|---|
| `ViewContent` | Visita a `/productos` | URL canónica y UTM disponibles |
| `Contact` | Clic en WhatsApp de un Producto | Tipo de origen `producto`, categoría si aplica, identificador técnico no sensible y UTM disponibles |

Solo se DEBEN enviar estos dos eventos y sus parámetros permitidos. El identificador de `Contact`
DEBE ser técnico y no sensible; la categoría puede incluirse cuando corresponda. El carrusel
editorial no emite eventos de medición: su navegación manual ni su CTA añaden eventos nuevos.

#### RF-VIT-28 — Privacidad de eventos

**WHEN** se envía cualquier evento **THEN** NO DEBE incluir nombre, teléfono, correo, mensaje de
WhatsApp, conversación privada, token, precio, stock u otro dato sensible.

#### RF-VIT-29 — Orientación paso a paso

**WHEN** se entrega la orientación aprobada **THEN** DEBE explicar, sin pedir credenciales: Meta
Business, creación o localización del Pixel, ubicación del Pixel ID, configuración mediante variable
de entorno, prueba de eventos, UTM, lectura de resultados, campañas de mensajes y tráfico, y la
diferencia entre clic a `wa.me` y conversación confirmada.

La recomendación inicial DEBE priorizar mensajes a WhatsApp, usar tráfico como campaña secundaria
y partir de aproximadamente 100.000 COP, ampliable según resultados. TikTok queda aplazado.

### SEO

#### RF-VIT-30 — Canonical y filtros

**WHEN** se visita `/productos` con o sin `categoria` **THEN** la canonical DEBE ser siempre
`/productos`.

**AND** las URLs filtradas y las variantes NO DEBEN indexarse como páginas independientes.

#### RF-VIT-31 — Metadatos y sitemap

**WHEN** se publica la vitrina **THEN** `/productos` DEBE tener metadatos propios y Open Graph,
DEBE aparecer en el sitemap y NO DEBE incluir Productos ocultos.

#### RF-VIT-32 — Texto alternativo

**WHEN** se muestra una imagen de Producto **THEN** DEBE usar el texto alternativo guardado, que es
obligatorio en el formulario administrativo. **WHEN** se muestra una imagen del carrusel editorial
**THEN** DEBE usar el texto alternativo configurado con el contenido; no existe formulario
administrativo para el carrusel.

### Seguridad administrativa

#### RF-VIT-33 — Autorización administrativa

**WHEN** se crea, edita, oculta, muestra, elimina de forma recuperable o carga la imagen de un
Producto **THEN** el servidor DEBE exigir una cuenta administrativa autenticada y activa, validar la
operación y rechazar cualquier acceso no autorizado. NO EXISTEN operaciones administrativas sobre
el carrusel.

#### RF-VIT-34 — Protección de solicitudes

**WHEN** una operación administrativa modifica datos **THEN** DEBE cumplir las protecciones de
sesión y CSRF vigentes del panel. La interfaz no puede ser la única barrera.

#### RF-VIT-35 — Fechas y estado actual

**WHEN** se crea o actualiza un Producto **THEN** el backend DEBE conservar su fecha de creación y
su fecha de actualización.

**WHEN** se expone el contrato legado de ImagenCarrusel **THEN** el backend DEBE conservar su fecha
de creación, su estado visible y su orden guardado, sin que exista operación de escritura ni regla
de posición pública asociada.

**AND** el sistema NO DEBE crear una entidad de auditoría ni registrar operación por operación o
usuario histórico para Producto ni para ImagenCarrusel.

#### RF-VIT-36 — Evolución coordinada del modelo

**WHEN** se implementa la vitrina **THEN** el sistema DEBE conservar Producto e ImagenCarrusel en el
modelo persistente y DEBE exponer únicamente los datos autorizados: administración de productos en
la API administrativa y el panel, campo `carrusel` de solo lectura en la API pública y carrusel
editorial estático en el frontend. Este cambio NO AÑADE migración.

**AND** las reglas de visibilidad, validación y orden de Producto DEBEN resolverse en el
backend; el frontend NO DEBE ser la autoridad para ocultar, publicar ni autorizar productos. El
carrusel editorial no aplica reglas de negocio del backend.

## 7. Requisitos no funcionales

- **RNF-VIT-01 — Fuente, autorización y orden.** La API pública DEBE filtrar en servidor por el
  campo `visible` propio de Producto; nunca se debe confiar en filtros del cliente para ocultar
  contenido. `visible_cliente=True` continúa reservado a serializers públicos de servicios y datos
  de clientes. También DEBE aplicar el orden público de Producto por fecha de creación descendente
  y, en empate, por identificador interno descendente, sin exponerlo. El campo `carrusel` legado se
  expone solo lectura, sin reglas de gestión en esta spec.
- **RNF-VIT-02 — Imágenes.** Solo JPG/JPEG/PNG/WEBP de máximo 5 MB, una imagen por registro; el
  procesamiento DEBE validar el MIME real y redimensionar o comprimir para evitar archivos pesados.
  Estas reglas aplican a la imagen de Producto, incluido su texto alternativo obligatorio. La base
  de datos DEBE conservar solo referencias/URL. El carrusel editorial no carga imágenes desde el
  panel: sus cinco imágenes y su texto alternativo son contenido configurado.
- **RNF-VIT-03 — Responsive.** Vitrina, filtros, carrusel editorial, CTA y administración de
  productos DEBEN funcionar en móvil, tablet y escritorio sin desplazamiento horizontal propio.
- **RNF-VIT-04 — Accesibilidad.** Controles con nombre accesible, foco visible, contraste,
  teclado, objetivos táctiles adecuados y avisos que no dependan solo del color. El autoplay debe
  cumplir RF-VIT-20.
- **RNF-VIT-05 — Estados de interfaz.** La vitrina y el panel de productos DEBEN contemplar carga,
  error, vacío, reintento y confirmación o rechazo de mutaciones. El carrusel editorial, al ser
  contenido estático, no tiene estados de consulta.
- **RNF-VIT-06 — Seguridad.** Las operaciones administrativas DEBEN validar autenticación, rol,
  cuenta activa y CSRF en el servidor.
- **RNF-VIT-07 — Privacidad y medición.** La medición DEBE limitarse a `ViewContent` para la visita
   a `/productos` y `Contact` para el clic de WhatsApp de Producto, usando solo parámetros no
   sensibles permitidos. No debe registrar datos personales sensibles, el contenido de WhatsApp ni
   interacciones del carrusel editorial.
- **RNF-VIT-08 — Idioma.** Textos visibles, validaciones, errores y guía DEBEN estar en español y
  no inventar copy comercial.
- **RNF-VIT-09 — Evolución y autoridad del backend.** El modelo persistente ya incluye Producto e
  ImagenCarrusel; este cambio no requiere migración. La API, el panel de productos y el frontend
  DEBEN consumir el contrato resultante sin duplicar reglas de negocio; el backend DEBE ser la
  autoridad para autorización, el campo `visible` de Producto, su orden, la validación de archivos
  y la conservación de fechas y estado actual. El carrusel editorial no duplica reglas del backend
  porque no las gestiona.
- **RNF-VIT-10 — Simplificación consciente de trazabilidad.** La vitrina NO DEBE crear una entidad
  de auditoría ni un historial de operaciones para Producto o ImagenCarrusel. Esta excepción al
  principio general de trazabilidad se justifica por el bajo riesgo y la administración por una sola
  persona. El modelo DEBE conservar únicamente las fechas y el estado actual definidos en RF-VIT-35.

## 8. Reglas de negocio

1. La vitrina presenta; no promete precio, stock ni compra inmediata.
2. Cada Producto tiene exactamente una categoría de las cuatro aprobadas, con los valores de query
   string definidos en RF-VIT-04.
3. Los Productos visibles se ordenan por fecha de creación descendente y, en caso de empate, por
   identificador interno descendente; el identificador no se muestra públicamente.
4. Ocultar es recuperable; no hay borrado definitivo en esta fase.
5. El carrusel visible es contenido editorial estático del frontend: cinco piezas configuradas, con
   texto comercial, CTA de WhatsApp e indicadores visuales; no se administra desde el panel ni
   desde el backend.
6. El carrusel editorial avanza automáticamente y detiene el movimiento ante interacción manual,
   puntero, foco, pestaña oculta o preferencia de movimiento reducido; no emite eventos de medición.
7. El contrato legado `ImagenCarrusel` / campo `carrusel` es de solo lectura: no se gestiona desde
   la aplicación y no es renderizado por la página actual.
8. WhatsApp se usa únicamente dentro de `/productos`: mensaje aprobado en las tarjetas y mensaje
   del CTA del carrusel editorial, con el número central del sitio.
9. Un clic a `wa.me` no confirma una conversación.
10. Facebook e Instagram son los canales iniciales; TikTok se posterga.
11. El presupuesto inicial de referencia es aproximadamente 100.000 COP y no es un precio de
    producto.
12. Producto e ImagenCarrusel forman parte del modelo persistente aprobado; la coordinación con API
    administrativa y panel aplica solo a Producto. Este cambio no exige migración.
13. El backend es la autoridad para validar y persistir las operaciones administrativas de
    productos; el frontend no puede convertir una operación fallida en una publicación exitosa. No
    hay operaciones administrativas del carrusel.
14. Producto conserva sus fechas de creación y actualización; ImagenCarrusel conserva su fecha de
    creación, su estado visible y su orden guardado, sin administración. No existe historial de
    operaciones ni usuario histórico para estas entidades.

## 9. Casos límite

- Categoría desconocida o filtro manipulado: respuesta vacía o inválida, sin revelar datos.
- Producto oculto con URL de campaña: permanece ausente de API, SEO y vitrina.
- Producto sin algún dato obligatorio o con dos categorías: se rechaza.
- Imagen de producto mayor de 5 MB, MIME real distinto de la extensión o formato no permitido: se
  rechaza.
- Error de Cloudflare al guardar o reemplazar una imagen de producto: no se conserva referencia
  rota ni se publica el cambio.
- Las siete imágenes iniciales están aprobadas, cargadas y visibles según §2: no se publican imágenes
  fuera de esa correspondencia ni se inventan descripciones ni textos alternativos.
- El carrusel editorial no tiene imágenes configuradas: no se renderiza ni produce error.
- Una sola imagen configurada en el carrusel: se muestra sin autoplay ni controles innecesarios.
- Varias imágenes configuradas: avanzan automáticamente con transición suave; el movimiento se
  detiene con puntero, foco, pestaña oculta, interacción manual o `prefers-reduced-motion`, y la
  navegación manual permanece disponible.
- Se pulsa el CTA del carrusel: abre WhatsApp con el mensaje del bloque y no afirma envío; no añade
  eventos de medición.
- El campo legado `carrusel` está vacío o cambia: la página actual no lo consume, por lo que no
  afecta al carrusel visible.
- UTM ausentes o incompletos: solo se conservan los disponibles, sin valores inventados.
- Pixel ausente, bloqueado o rechazado: la vitrina sigue operativa.
- Se pulsa WhatsApp varias veces en un Producto: cada acción es solo un clic y no una confirmación
  de envío.
- Un usuario no autenticado, cuenta inactiva o petición sin CSRF intenta modificar datos: se
  rechaza sin alterar la entidad.
- Una operación rechazada por autorización, validación o almacenamiento no modifica Producto ni
  publica un estado inválido. No existen operaciones administrativas del carrusel que puedan
  rechazarse.
- El contrato público deja de exponer Producto: la iniciativa no se considera completa y no se
  compensa con estado local del frontend. El carrusel editorial es contenido estático documentado y
  no depende de ese contrato.

## 10. Criterios de aceptación

1. `/productos` consume la fuente pública, muestra carga/error/vacío/reintento y solo devuelve
   Productos visibles ordenados por fecha de creación descendente y, en empate, por identificador
   interno descendente, sin exponer ese identificador.
2. Los filtros `?categoria=bombas-hidraulicas`, `?categoria=reparacion-mantenimiento`,
   `?categoria=control-hidraulico` y `?categoria=transmision` funcionan con sus categorías
   exactas; la canonical continúa siendo `/productos` y las variantes no se indexan.
3. Producto conserva exactamente los campos aprobados, una sola categoría y fechas de creación y
   actualización.
4. El panel permite crear, editar, ocultar, mostrar y “eliminar” recuperablemente un Producto;
   ocultos no aparecen en API, vitrina, sitemap ni metadatos.
5. Para las siete imágenes iniciales existe la tabla aprobada de correspondencia
   imagen/producto/categoría/descripción/texto alternativo de §2; están cargadas y visibles en
   Cloudflare con URL/referencia registrada, sin marcas, referencias, precios ni stock inventados, y
   se rechazan formatos no permitidos, MIME inválido y archivos mayores de 5 MB.
6. ImagenCarrusel permanece como contrato legado de solo lectura en la API pública; no existe
   panel, ruta, menú, endpoint, serializer ni test administrativo del carrusel, y la página actual
   no renderiza el campo `carrusel`.
7. El carrusel visible muestra las cinco piezas configuradas con sus imágenes, tipo, nombre y
   descripción, el texto comercial actual, el CTA “PREGUNTAR POR MI REPUESTO” y sus indicadores
   visuales; su contenido no depende de backend ni de panel.
8. El carrusel avanza automáticamente con transición suave y sin controles visibles de reproducción;
   se detiene con puntero, foco, pestaña oculta, interacción manual o `prefers-reduced-motion`, con
   navegación manual por teclado y gestos; con una sola imagen es estático y sin imágenes no se
   renderiza.
9. El CTA del carrusel abre WhatsApp con el mensaje “Hola, quiero preguntar por un repuesto
   hidráulico y solicitar una cotización.” y no afirma envío de conversación; no se añaden marcas,
   referencias, precios ni datos de stock.
10. El carrusel mantiene su presentación legible y sin desplazamiento horizontal propio en móvil,
    tablet y escritorio, con texto alternativo configurado para cada imagen.
11. El CTA de WhatsApp de Producto usa exactamente el mensaje aprobado, el número configurado y no
    afirma envío de conversación; ambos usos de WhatsApp en la vitrina reutilizan el número central.
12. Solo se envían `ViewContent` en la visita a `/productos` y `Contact` en el clic de WhatsApp de
    un Producto; conservan UTM durante la sesión y usan únicamente parámetros no sensibles
    permitidos. El carrusel editorial no emite eventos de medición: su navegación manual ni su CTA
    añaden eventos nuevos.
13. El Pixel ID se obtiene de configuración; sin Pixel la vitrina continúa funcionando. La guía de
    Meta explica el flujo paso a paso sin solicitar credenciales.
14. `/productos` está en sitemap, tiene Open Graph y canonical `/productos`; no hay URLs
    individuales indexables ni entradas de Productos ocultos.
15. Navegación, hero y `/soluciones` contienen los accesos aprobados a `/productos`.
16. Las operaciones administrativas de productos exigen autenticación, cuenta activa, rol
    autorizado y CSRF; los errores no dejan cambios parciales y el backend conserva las fechas y el
    estado actual definidos para Producto, sin crear historial de operaciones. La Opción A es una
    excepción consciente: la autenticación, CSRF y seguridad administrativa vigente son suficientes
    para este alcance de un solo administrador. No hay operaciones administrativas del carrusel.
17. La experiencia funciona en móvil, tablet y escritorio, con teclado, foco visible y estados
    accesibles de carga, error, vacío y mutación.
18. El modelo persistente (Producto e ImagenCarrusel) queda expuesto de forma coherente sin nueva
    migración: administración y panel solo para Producto, campo `carrusel` de solo lectura en la API
    pública y carrusel editorial estático en el frontend; el backend conserva la autoridad sobre las
    reglas de productos.

## 11. Decisiones pendientes

1. **Consentimiento y privacidad de Meta Pixel:** validar antes de producción si se requiere aviso,
   consentimiento explícito o gestión de cookies. Es una decisión pendiente no bloqueante para la
   spec; no se inventa una política legal.
2. **Política de conservación del binario sustituido:** confirmar cuándo se eliminan del
   almacenamiento las imágenes de producto reemplazadas u ocultadas, sin borrar la referencia
   histórica en esta fase.
3. **Lugar de publicación de la guía:** confirmar si se entrega como documentación interna,
   sección del panel o material separado. No se compartirán credenciales.

## 12. Notas de alineación

- La autenticación reutiliza las credenciales del panel existente.
- La incorporación de Producto e ImagenCarrusel al modelo persistente es una decisión aprobada y ya
  registrada. Este cambio no añade migración y coordina API pública, API administrativa, panel y
  frontend solo para Producto.
- El carrusel visible y el contrato legado son dos cosas distintas: el primero es contenido
  editorial estático del frontend, con cinco piezas, texto comercial, CTA de WhatsApp e
  indicadores; el segundo es el campo `carrusel` de la API pública, de solo lectura, no gestionado
  desde la aplicación y no renderizado por la página actual. No se elimina ninguno de los dos.
- Se retira toda administración del carrusel: no hay panel, ruta, menú, hooks, tipos, endpoints
  CRUD, serializer administrativo, reglas de posiciones ni tests administrativos del carrusel. No
  se modifica el contrato público ni el modelo de datos.
- La Opción A de trazabilidad está adoptada: no se crea entidad de auditoría ni historial de
  operaciones. Producto conserva fechas de creación/actualización e ImagenCarrusel conserva fecha
  de creación, estado visible y orden guardado, sin administración; esta simplificación consciente
  es una excepción al principio general de trazabilidad, justificada por el bajo riesgo y el único
  administrador. La seguridad administrativa vigente se mantiene como control suficiente para este
  alcance.
- El número y la utilidad de WhatsApp existentes son la única fuente para construir los enlaces de
  Producto y del CTA del carrusel editorial.
- Cloudflare almacena las imágenes; la base de datos conserva URL o referencia, nunca binarios.
- La carga inicial de las siete imágenes quedó resuelta con la tabla editorial aprobada de §2:
  están cargadas y visibles, con descripción y texto alternativo derivados de los nombres aprobados;
  no se inventan marcas, referencias, precios ni stock.
- Esta spec no autoriza credenciales de Meta, una política legal no confirmada, dependencias nuevas,
  precios, stock, e-commerce, páginas individuales, WhatsApp API ni TikTok inicial.
