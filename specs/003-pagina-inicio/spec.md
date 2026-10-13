# Spec 003 — Página de inicio del sitio público

Estado: borrador

## Contexto y objetivo

Hidroemcol es una empresa técnica e industrial dedicada a sistemas hidráulicos y
electrohidráulicos: repuestos, importación sobre pedido, servicios técnicos con banco de
pruebas, diagnóstico y reparación de componentes, y soluciones de control a la medida.

Hoy la página de inicio del sitio público es un marcador de posición: solo muestra el
nombre de la empresa y un texto que anuncia que el contenido está por definir. No comunica
qué hace la empresa, no presenta sus servicios, no muestra su capacidad técnica y no le da
al visitante ninguna razón ni manera de avanzar.

**Objetivo:** convertir la página de inicio en la presentación pública de la empresa, de
modo que un visitante entienda en pocos segundos qué hace Hidroemcol, conozca sus servicios
y su capacidad técnica, reconozca la marca y tenga siempre a la vista una forma clara de
solicitar un servicio, hacer seguimiento o contactar.

**Por qué importa:** para una empresa del sector industrial, la página de inicio es la
primera prueba de credibilidad. Debe transmitir confianza, precisión técnica y capacidad
industrial, no parecer la plantilla genérica de una empresa tecnológica. La página no se
limita a informar: es también la puerta de entrada al flujo real de negocio, que empieza con
una solicitud de servicio y continúa con su seguimiento.

**Contexto de contenido:** el contenido textual de esta página proviene del folleto físico de
la empresa, transcrito por el usuario en `specs/003-pagina-inicio/contenido-folleto.md`, que es
la única fuente de contenido textual para la página de inicio. Para esta versión están disponibles
en `frontend/public/img` las imágenes `productos-1.jpeg`, `productos-2.jpeg` y
`productos-3.jpeg`; `reparacion-via.jpeg` y
`transporte-elicoportado-villa-garzon-putumayo.jpeg` se reservan para una futura vista de
Servicios y no se muestran en el inicio. Esta spec no inventa requisitos de negocio ni datos que
el folleto no contenga.

## Usuarios

| Usuario | Descripción |
|---|---|
| **Visitante (cliente potencial)** | Persona que llega a la página para saber qué hace Hidroemcol y si puede resolverle una necesidad técnica. Puede ser personal de mantenimiento, técnico mecánico/hidráulico/eléctrico, ingeniero, personal de compras o responsable de taller de una empresa industrial. Su nivel de conocimiento técnico es variable y navega mayoritariamente desde el teléfono. |
| **Cliente existente** | Persona que ya conoce la empresa y solo busca una vía directa para solicitar un servicio, hacer seguimiento de uno en curso o contactar sin recorrer todo el sitio. |

## Historias de usuario

**HU-1 — Entender la empresa de un vistazo.**
Como visitante que no conoce Hidroemcol, quiero comprender en la primera pantalla qué hace
la empresa y qué tipo de problemas técnicos resuelve, para decidir si es la empresa que
necesito antes de seguir navegando.

**HU-2 — Reconocer los servicios.**
Como visitante, quiero ver los servicios y componentes que la empresa atiende, para
identificar si alguno corresponde a mi necesidad sin tener que llamar para averiguarlo.

**HU-3 — Confiar en la capacidad técnica.**
Como visitante técnico, quiero ver qué componentes y qué capacidad técnica tiene la empresa
(como sus pruebas en banco), para confiar en que está calificada para el trabajo.

**HU-4 — Entender el proceso antes de comprometerme.**
Como visitante, quiero conocer cómo funciona el servicio paso a paso, para saber qué esperar
si decido solicitar un servicio.

**HU-5 — Actuar sin buscar.**
Como visitante, quiero tener siempre a la vista una forma clara de solicitar un servicio,
hacer seguimiento o contactar, para avanzar en el momento en que me decido, sin buscar
enlaces escondidos.

**HU-6 — Consultar mi servicio existente.**
Como cliente que ya tiene un servicio en curso, quiero llegar fácilmente al seguimiento
desde la página de inicio, para consultar el avance sin depender de mensajes o llamadas.

## Definiciones

- **Hero (encabezado principal):** la primera sección de la página, visible sin desplazarse.
  Presenta el mensaje principal, el botón de acción principal y las tres tarjetas de servicio.
  La marca se identifica mediante el encabezado compartido; el hero no repite el logo grande.
- **Tarjeta de servicio:** bloque visual reutilizable que resume una categoría de servicio o
  componente, con un título y una descripción breve. Es contenido informativo y no navegable
  mientras no se le asigne un destino; si en el futuro se le asigna uno, pasará a ser un
  elemento interactivo con foco de teclado visible.
- **Servicios destacados:** sección que presenta las cuatro áreas de productos y servicios de
  la empresa según el folleto —suministro de repuestos, importación sobre pedido, servicio
  técnico electrohidráulico e implementación de sistemas—, en formato informativo (título y
  descripción, sin enlace). El bloque de Importación Sobre Pedido incluye la presentación de las
  tres imágenes de productos mediante un carrusel accesible.
- **Carrusel de Importación Sobre Pedido:** presentación de las imágenes
  `productos-1.jpeg`, `productos-2.jpeg` y `productos-3.jpeg` dentro del bloque de Importación
  Sobre Pedido de servicios destacados. Incluye controles visibles y operación por teclado, y no
  es una galería genérica de la sección de componentes y capacidad técnica.
- **Capacidad técnica / componentes:** sección que comunica qué componentes atiende la
  empresa, los nombres de las marcas con las que trabaja y con qué medios técnicos cuenta (por
  ejemplo, pruebas en banco).
- **Cómo funciona el servicio:** sección que describe, como una secuencia ordenada de pasos,
  el recorrido que sigue una solicitud desde que llega hasta que se entrega.
- **Llamado a la acción (CTA):** elemento que invita al visitante a realizar una acción
  concreta. Se distingue una acción principal (solicitar servicio) de las secundarias
  (seguimiento y contacto).
- **Seguimiento:** consulta del avance de un servicio ya solicitado, mediante el código de
  servicio (identificador humano del servicio) que el cliente usa para acceder a su consulta.
  El token privado de seguimiento es un mecanismo de acceso distinto y no es lo que el cliente
  introduce como código.
- **Único punto del número de contacto:** una única fuente o valor del número de contacto de la
  empresa, de la que dependen todos los accesos visibles (WhatsApp y llamada); cambiar el valor
  en esa única fuente actualiza todos los accesos a la vez.
- **Contenido provisional:** texto o imagen de borrador que aún no proviene del folleto
  transcrito ni de los recursos de marca confirmados, y que debe reemplazarse o validarse antes
  de dar la página por terminada. El texto de servicios y componentes proviene del folleto; las
  imágenes del folleto y los logotipos de las marcas aún pueden estar pendientes.

## Requisitos funcionales

### RF-1 — Estructura y orden de la página

- **RF-1.1** CUANDO un visitante abre la página de inicio, EL SISTEMA muestra las secciones
  en este orden exacto: (1) hero o encabezado principal con el mensaje, el botón de acción
  principal y las tres tarjetas, (2) servicios destacados, (3) componentes y
  capacidad técnica, (4) cómo funciona el servicio, (5) llamado a la acción final.
- **RF-1.2** EL SISTEMA no muestra en la página de inicio ninguna sección de contenido
  distinta de las cinco enumeradas en RF-1.1. El encabezado y el pie compartidos del sitio
  (RF-10) y el acceso a contacto (RF-9) son elementos estructurales permitidos y no cuentan
  como secciones de contenido.
- **RF-1.3** EL SISTEMA mantiene cada sección identificable mediante un encabezado propio y
  visible, de modo que el visitante pueda reconocer dónde empieza cada una al desplazarse.

### RF-2 — Encabezado principal (hero)

- **RF-2.1** CUANDO un visitante abre la página de inicio, EL SISTEMA muestra primero el hero
  con tres elementos: un mensaje que explica qué hace la empresa, un botón de acción principal
  ("solicitar un servicio") y las tres tarjetas de servicio.
- **RF-2.2** EL SISTEMA no muestra el logotipo grande dentro del hero, porque la marca ya está
  identificada por el logotipo del encabezado compartido; el hero conserva el h1 provisional
  actual, el CTA y las tres tarjetas.
- **RF-2.3** EL SISTEMA muestra en el hero exactamente tres tarjetas de servicio, ni más ni
  menos.
- **RF-2.4** EL SISTEMA muestra la primera tarjeta del hero con el título "Servicio técnico
  hidráulico y electrohidráulico" y la descripción "diagnóstico, reparación y pruebas en
  banco".
- **RF-2.5** EL SISTEMA muestra la segunda tarjeta del hero con el título "Suministro de
  repuestos e importación sobre pedido" y la descripción "bombas, motores, cilindros,
  válvulas, orbitroles".
- **RF-2.6** EL SISTEMA muestra la tercera tarjeta del hero con el título "Implementación de
  sistemas electrohidráulicos a medida" y la descripción "control proporcional, control de
  marcha y velocidades, asesoría e implementación".
- **RF-2.7** EL SISTEMA hace visible el mensaje principal y las tres tarjetas sin exigir
  desplazamiento horizontal en ninguna anchura soportada.

### RF-3 — Animación de las tarjetas del hero

- **RF-3.1** EL SISTEMA reproduce la animación de las tres tarjetas del hero al aparecer la
  página y la termina en un tiempo acotado; durante toda la animación el título y la
  descripción de cada tarjeta permanecen legibles y sin recorte.
- **RF-3.2** MIENTRAS el dispositivo del visitante tenga activada la preferencia de reducir
  movimiento, EL SISTEMA muestra las tres tarjetas sin animación, con todo su contenido
  visible y legible de forma estática.
- **RF-3.3** EL SISTEMA mantiene visible en todo momento la respuesta de cada tarjeta a la
  interacción del visitante (señalización al pasar el puntero y pulsación táctil), de modo que
  la animación no la oculte ni la atenúe. Las tarjetas del hero son contenido informativo y no
  navegable en esta versión; SI en una versión futura una tarjeta pasa a ser interactiva (por
  ejemplo, un enlace), ENTONCES EL SISTEMA le añade un estado de foco de teclado visible.
- **RF-3.4** SI el contenido definitivo de una tarjeta aún no está disponible, ENTONCES EL
  SISTEMA mantiene visible el texto provisional o el título confirmado de esa tarjeta, sin
  dejar el espacio vacío.

### RF-4 — Servicios destacados

- **RF-4.1** CUANDO un visitante abre la página de inicio, EL SISTEMA presenta una sección de
  servicios destacados con los cuatro bloques de productos y servicios del folleto, cada uno
  con un título y una descripción breve tomada del folleto:
  - "Suministro de Repuestos" — repuestos de excelente calidad para bombas y motores
    hidráulicos.
  - "Importación Sobre Pedido" — solución para equipos cuyos repuestos no son comunes o son de
    referencias especiales.
  - "Servicio técnico electrohidráulico" — servicio en sistemas eléctricos de mando ligados a
    la hidráulica: control proporcional, control de marcha y velocidades, combinaciones
    valvulares y sistemas sensorizados.
  - "Implementación de sistemas" — asesoría y ejecución de sistemas electrohidráulicos a la
    medida, por sustitución de un sistema obsoleto o por creación desde cero.
- **RF-4.2** EL SISTEMA presenta cada servicio destacado como contenido informativo (título y
  descripción), sin enlace ni acción de navegación.
- **RF-4.3** SI el contenido de un servicio destacado aún no está confirmado con el folleto,
  ENTONCES EL SISTEMA muestra el texto provisional sin afirmar datos de negocio no
  verificados (precios, disponibilidad o capacidades numéricas).
- **RF-4.4** EL SISTEMA presenta los servicios destacados en el mismo orden en cada carga de
  la página.
- **RF-4.5** EL SISTEMA incorpora dentro del bloque "Importación Sobre Pedido" las imágenes
  `productos-1.jpeg`, `productos-2.jpeg` y `productos-3.jpeg`, ubicadas en
  `frontend/public/img`, mediante un carrusel visualmente integrado al bloque. No las presenta
  como una galería genérica dentro de Componentes y capacidad técnica.
- **RF-4.6** EL SISTEMA permite operar el carrusel con controles visibles y teclado, sin depender
  únicamente de gestos táctiles. Cada imagen conserva un texto alternativo significativo
  confirmado para su contenido.
- **RF-4.7** MIENTRAS el visitante tenga activada la preferencia de reducir movimiento, EL
  SISTEMA evita la transición animada del carrusel y mantiene accesibles sus controles y la
  imagen activa.
- **RF-4.8** SI una imagen del carrusel no carga, EL SISTEMA mantiene el bloque de Importación
  Sobre Pedido comprensible, sin mostrar un espacio roto ni generar desplazamiento horizontal.

### RF-5 — Componentes y capacidad técnica

- **RF-5.1** CUANDO un visitante abre la página de inicio, EL SISTEMA presenta una sección que
  comunica qué componentes atiende la empresa, incluyendo al menos cilindros, bombas, motores,
  orbitroles, controles, válvulas y otros componentes hidráulicos y electrohidráulicos.
- **RF-5.2** EL SISTEMA presenta en esa sección la capacidad técnica de la empresa,
  mencionando explícitamente las pruebas en banco.
- **RF-5.3** SI una categoría de componente o una capacidad técnica no está confirmada,
  ENTONCES EL SISTEMA la muestra como contenido provisional y no como hecho comercial
  definitivo.
- **RF-5.4** EL SISTEMA expone los componentes y capacidades en formato de lista o conjunto de
  bloques escaneables, no en un párrafo de texto continuo.
- **RF-5.5** EL SISTEMA muestra dentro de esa sección los nombres de las marcas que atiende
  como texto —Komatsu, Bobcat, Ingersoll Rand, Genie, Soilmeca, Link-Belt, Eaton, Bosch
  Rexroth, Sauer Danfoss, Kawasaki Hydraulics, Caterpillar, Kayaba, Linde y Denison—, sin usar
  imágenes o logotipos de esas marcas ni afirmar que existan.
- **RF-5.6** EL SISTEMA incluye dentro de esa sección un video que muestra una pieza montada en
  el banco de pruebas; el contenido de referencia es el archivo disponible en
  `frontend/public/vid/video-banco-prueba.mp4`. El video refuerza el POR QUÉ de la sección:
  demostrar la capacidad técnica real de la empresa.
- **RF-5.7** EL SISTEMA no reproduce el sonido del video sin que el visitante lo active;
  cuando el video se reproduce automáticamente, lo hace en silencio.
- **RF-5.8** EL SISTEMA ofrece un control visible para reproducir y pausar el video.
- **RF-5.9** MIENTRAS el dispositivo del visitante tenga activada la preferencia de reducir
  movimiento, EL SISTEMA no reproduce el video de forma automática.
- **RF-5.10** SI el archivo del video no está disponible o falla su carga, ENTONCES EL SISTEMA
  mantiene la sección comprensible y no deja un espacio roto ni vacío.
- **RF-5.11** EL SISTEMA no muestra en esta sección las imágenes `productos-1.jpeg`,
  `productos-2.jpeg` ni `productos-3.jpeg`; esas imágenes pertenecen al bloque de Importación
  Sobre Pedido de RF-4.

### RF-6 — Cómo funciona el servicio

- **RF-6.1** CUANDO un visitante abre la página de inicio, EL SISTEMA presenta una sección que
  describe el proceso del servicio como una secuencia ordenada de pasos numerados.
- **RF-6.2** EL SISTEMA muestra los pasos en orden ascendente y con una numeración visible.
- **RF-6.3** EL SISTEMA redacta la sección como contenido provisional hasta que la secuencia
  definitiva de pasos se valide con el folleto y con el proceso de negocio aprobado.
- **RF-6.4** EL SISTEMA permite comprender cada paso leyendo solo su título, sin depender de
  un párrafo largo.

### RF-7 — Llamado a la acción final

- **RF-7.1** CUANDO un visitante llega al final de la página de inicio, EL SISTEMA muestra una
  sección final con tres acciones: solicitar un servicio, hacer seguimiento y contactar.
- **RF-7.2** EL SISTEMA distingue visualmente la acción "solicitar un servicio" como acción
  principal, y trata "seguimiento" y "contactar" como acciones secundarias.
- **RF-7.3** CUANDO el visitante activa "solicitar un servicio", EL SISTEMA lo conduce a la
  vía de solicitud de servicio del sitio.
- **RF-7.4** CUANDO el visitante activa "hacer seguimiento", EL SISTEMA lo conduce al acceso de
  seguimiento del sitio, donde el cliente consulta el avance de un servicio con su código de
  servicio.
- **RF-7.5** CUANDO el visitante activa "contactar", EL SISTEMA le ofrece el medio de contacto
  directo definido en RF-9.

### RF-8 — Identidad visual de la marca

- **RF-8.1** EL SISTEMA usa el azul corporativo #2E3192 como color principal de la página de
  inicio.
- **RF-8.2** EL SISTEMA usa el color #FFC908 como color de acento de la página de inicio.
- **RF-8.3** EL SISTEMA usa el logotipo completo de la marca de forma consistente en el
  encabezado compartido de la página de inicio, sin duplicarlo como logo grande en el hero, sin
  deformarlo ni recolorearlo fuera de la paleta corporativa.
- **RF-8.4** EL SISTEMA no comunica información importante únicamente por medio del color.

### RF-9 — Contacto directo (WhatsApp)

- **RF-9.1** EL SISTEMA ofrece en la página de inicio un acceso directo a WhatsApp con el
  número de desarrollo +57 312 5967913, que también sirve como número de teléfono de contacto.
- **RF-9.2** MIENTRAS el sitio esté en fase de desarrollo, EL SISTEMA permite sustituir el
  número de contacto +57 312 5967913 desde un único punto sin tener que buscarlo en varios
  lugares, y no lo presenta como dato definitivo de producción.
- **RF-9.3** CUANDO el visitante activa el contacto por WhatsApp, EL SISTEMA abre una
  conversación dirigida al número +57 312 5967913 configurado en el único punto de contacto.
- **RF-9.4** SI el canal de contacto por WhatsApp no está disponible o el número configurado es
  inválido, ENTONCES EL SISTEMA ofrece como alternativa de contacto el mismo número por
  llamada telefónica, de forma comprensible y funcional en la misma página.

### RF-10 — Encabezado y pie compartidos

- **RF-10.1** EL SISTEMA mantiene en la página de inicio el encabezado y el pie compartidos
  del sitio, de modo que el visitante pueda identificar la marca y acceder a las secciones
  principales.
- **RF-10.2** SI se modifica el encabezado o el pie para atender la página de inicio, ENTONCES
  EL SISTEMA conserva su funcionamiento y su aspecto en el resto de páginas del sitio.
- **RF-10.3** EL SISTEMA muestra en el pie compartido un acceso a la página de Facebook de la
  empresa, que es la única red social incluida.

### RF-11 — Contenido y validación

- **RF-11.1** EL SISTEMA presenta en la página de inicio el texto proveniente del folleto
  transcrito en `specs/003-pagina-inicio/contenido-folleto.md` y no publica cifras,
  capacidades, disponibilidad ni otros datos de negocio que el folleto no contenga.
- **RF-11.2** MIENTRAS los logotipos de las marcas no estén disponibles, EL SISTEMA mantiene
  esos elementos como pendientes, sin dejar espacios vacíos ni inventar recursos, y muestra los
  nombres de las marcas como texto. Las tres imágenes de productos definidas en RF-4.5 sí se
  incorporan en el carrusel de Importación Sobre Pedido.
- **RF-11.3** CUANDO el usuario aporte otras imágenes del folleto o los logotipos de las marcas,
  EL SISTEMA permite incorporarlos sin alterar la estructura ni el orden de las secciones; las
  tres imágenes definidas en RF-4.5 mantienen su ubicación dentro de Importación Sobre Pedido.
- **RF-11.4** EL SISTEMA muestra en el inicio únicamente `productos-1.jpeg`,
  `productos-2.jpeg` y `productos-3.jpeg`, dentro del bloque de Importación Sobre Pedido. No
  muestra todavía `reparacion-via.jpeg` ni
  `transporte-elicoportado-villa-garzon-putumayo.jpeg`; estos recursos quedan reservados para
  una futura vista o sección de Servicios y permanecen en `frontend/public/img`.

## Requisitos no funcionales

- **RNF-1** La página debe diseñarse con enfoque móvil primero y ser totalmente usable en
  móvil, tablet y escritorio, sin desplazamiento horizontal en ninguna de esas anchuras.
- **RNF-2** En pantallas pequeñas, los elementos interactivos deben tener un área táctil de al
  menos 44×44 px y los textos deben conservar un cuerpo de al menos 16 px; el diseño no debe
  ser una simple reducción de la versión de escritorio.
- **RNF-3** La página debe tener una estructura y una jerarquía de contenido comprensibles, de
  modo que el visitante y las ayudas técnicas identifiquen claramente las partes principales
  de la página.
- **RNF-4** La página debe tener una jerarquía de encabezados lógica: un solo encabezado de
  nivel principal por página y niveles subsiguientes sin saltos.
- **RNF-5** Toda imagen que aporte información o marca debe tener un texto alternativo
  significativo; toda imagen decorativa debe quedar fuera del árbol de accesibilidad.
- **RNF-6** Todos los elementos interactivos deben ser alcanzables y operables con teclado, y
  deben mostrar un estado de foco visible.
- **RNF-7** La página debe mantener un contraste mínimo de 4.5:1 para texto normal y de 3:1
  para texto grande e iconos relevantes, incluida la combinación del acento sobre el azul y
  del texto sobre fondos claros.
- **RNF-8** MIENTRAS el dispositivo tenga activada la preferencia de reducir movimiento, la
  página no debe reproducir animaciones de las tarjetas del hero ni otras animaciones no
  esenciales.
- **RNF-9** Si alguna sección de la página carga datos de forma remota, debe mostrar estados de
  carga, de resultado vacío y de error, y ofrecer reintento cuando corresponda; si toda la
  página es estática, este requisito no aplica y la página nunca debe quedar en blanco.
- **RNF-10** Si una imagen de marca o de contenido no carga, la página debe seguir siendo
  comprensible y usable, sin depender de esa imagen para transmitir la información.
- **RNF-11** La carga de las imágenes no debe provocar que el contenido salte de posición ni
  mermar la fluidez de la página. El carrusel no debe generar overflow horizontal.
- **RNF-12** Los textos visibles de la página deben estar en español y usar la terminología de
  la empresa de forma consistente.
- **RNF-13** La página debe ser visual y funcionalmente consistente con el resto del sitio, de
  modo que el visitante reconozca una misma identidad y un mismo comportamiento.
- **RNF-14** Los controles del carrusel deben tener foco visible, ser alcanzables y operables con
  teclado, y contar con un área táctil mínima de 44×44 px. El carrusel no puede depender solo de
  gestos.
- **RNF-15** Las imágenes del carrusel deben usar textos alternativos significativos y
  confirmados, no limitarse a repetir el nombre del archivo. Las imágenes que no aporten
  información deben declararse decorativas según RNF-5.

## Casos límite

- El visitante abre la página en un teléfono de 320 píxeles de ancho: no debe aparecer
  desplazamiento horizontal ni recortes de texto.
- El visitante tiene activada la preferencia de reducir movimiento: las tres tarjetas del hero
  se muestran completas y estáticas, y ninguna información queda solo en la animación.
- El visitante usa el carrusel de Importación Sobre Pedido solo con teclado: puede moverlo con
  controles visibles, alcanzar cada control con foco visible y no necesita un gesto táctil.
- El visitante tiene activada la preferencia de reducir movimiento: el carrusel no ejecuta
  transiciones animadas y la imagen activa sigue siendo comprensible.
- El sistema operativo o el navegador bloquea la apertura de WhatsApp: el visitante encuentra
  una alternativa de contacto comprensible en la misma página.
- El número de contacto aún es el de desarrollo (312 5967913): la página debe seguir siendo
  funcional y no debe presentarlo como dato definitivo de producción.
- Las imágenes de marca o de producto no cargan o tardan: la página conserva su estructura y
  su mensaje principal.
- El visitante abre la página en una anchura pequeña mientras usa el carrusel: las imágenes y
  controles se mantienen dentro del contenedor, sin overflow horizontal ni recortes de acciones.
- El video del banco de pruebas no está disponible o falla su carga: la sección de componentes
  y capacidad técnica sigue siendo comprensible y no queda un espacio roto.
- El visitante navega solo con teclado: puede recorrer las secciones y las acciones, y ver
  siempre el foco. Las tarjetas del hero son contenido informativo y no reciben foco de teclado
  en esta versión.
- El visitante amplía la página al 200 %: el contenido sigue siendo legible y no se pierde
  ninguna acción.
- Las imágenes del folleto o los logotipos de las marcas todavía no llegaron: la página conserva
  su estructura, muestra los nombres de las marcas como texto y no inventa recursos ni datos de
  negocio.
- El visitante llega desde un enlace directo al final de la página: las acciones principales
  siguen siendo alcanzables.
- El script de la página tarda en cargar: el contenido principal no queda vacío.
- `reparacion-via.jpeg` o `transporte-elicoportado-villa-garzon-putumayo.jpeg` existen en
  `frontend/public/img`: no se muestran todavía en el inicio y no se eliminan del directorio.

## Fuera de alcance

Esta versión **no** incluye:

- La ubicación o el mapa de Google Maps. El usuario decidió que irá en la página "Nosotros" y
  se implementará aparte.
- La página "Nosotros" y cualquier otra página del sitio: Servicios, Soluciones, Contacto,
  Solicitar servicio, Seguimiento y el panel administrativo. Esta spec solo cubre la página de
  inicio.
- La misión, la visión y los valores de la empresa: pertenecen a la página "Quiénes somos"
  (Nosotros) y no a la página de inicio.
- Cambios en el backend, en la API o en la lógica de negocio.
- Catálogo comercial, e-commerce, carrito, pagos, precios, inventario público o disponibilidad
  de productos.
- La recolección de los recursos gráficos del folleto físico y de los logotipos de las marcas:
  es una dependencia externa que aporta el usuario; lo que está pendiente se lista en Dudas
  abiertas.
- Una galería genérica de imágenes en Componentes y capacidad técnica, y la incorporación de
  `reparacion-via.jpeg` o `transporte-elicoportado-villa-garzon-putumayo.jpeg` en la página de
  inicio. Esos recursos quedan reservados para una futura vista o sección de Servicios.
- La creación de cuentas de cliente o cualquier autenticación en el sitio público.
- Integración con WhatsApp Business API o cualquier automatización de mensajería.
- Redes sociales distintas de Facebook (única red confirmada).
- Versiones del sitio en idiomas distintos del español.
- Cualquier modificación del flujo de negocio o del modelo de datos.

## Criterios de finalización

La página de inicio está terminada cuando:

1. Un visitante que abre la página entiende qué hace la empresa sin desplazarse más allá de la
   primera sección.
2. Las cinco secciones aparecen en el orden definido en RF-1.1 y no se muestra ninguna otra
   sección de contenido; el encabezado, el pie y el acceso a contacto son elementos
   estructurales permitidos.
3. El encabezado compartido muestra el logotipo de la marca y el hero, sin repetirlo como logo
   grande, conserva el h1 provisional actual, el botón de acción principal y exactamente tres
   tarjetas con los tres títulos y descripciones definidos en esta spec (RF-2.4 a RF-2.6),
   tomados del folleto.
4. Las tres tarjetas del hero reproducen su animación al aparecer la página y la terminan en
   un tiempo acotado, conservan siempre visible su contenido y, con la preferencia de reducir
   movimiento activada, se muestran sin animación y completas.
5. La página usa el azul #2E3192 como color principal y el #FFC908 como acento, y el logotipo
   del encabezado se muestra sin deformar ni duplicarse en el hero.
6. La página ofrece acceso directo a WhatsApp con el número 312 5967913, definido en un único
   lugar y marcado como temporal.
7. La sección final presenta las tres acciones (solicitar servicio, seguimiento, contacto),
   con "solicitar un servicio" diferenciada como acción principal, y cada una conduce a su
   destino.
8. La página funciona sin desplazamiento horizontal y con contenido legible en móvil, tablet y
   escritorio, verificada manualmente en un teléfono móvil real.
9. La página cumple la verificación de accesibilidad: estructura y jerarquía de contenido
   comprensibles, jerarquía de encabezados correcta, texto alternativo significativo en
   imágenes de marca y contenido, foco visible y navegación por teclado, y contraste según los
   umbrales de RNF-7.
10. La página no reproduce animaciones de tarjetas cuando la preferencia de reducir movimiento
    está activa.
11. Los estados de carga, vacío y error se comportan según RNF-9 donde existan datos
    cargados, y la página nunca queda en blanco.
12. El texto de servicios, componentes y capacidad técnica proviene del folleto; las imágenes
    del folleto y los logotipos de las marcas han sido incorporados y validados por el usuario
    cuando estén disponibles, y mientras tanto la página muestra los nombres de las marcas como
    texto, sin dejar contenido vacío ni inventado.
13. La sección de servicios destacados presenta los cuatro bloques del folleto y la sección de
    componentes muestra los nombres de las marcas como texto, sin depender de logotipos de
    marca.
14. La sección de componentes y capacidad técnica incluye el video del banco de pruebas, que no
     reproduce sonido sin que el visitante lo active, ofrece control de reproducir y pausar, no
     se reproduce solo con la preferencia de reducir movimiento activa y, si no carga, deja la
     sección comprensible sin espacio roto.
15. El bloque de Importación Sobre Pedido contiene un carrusel con `productos-1.jpeg`,
    `productos-2.jpeg` y `productos-3.jpeg`, con controles visibles y operables por teclado,
    foco visible, áreas táctiles de al menos 44×44 px, textos alternativos significativos
    confirmados, reducción de movimiento y sin overflow horizontal.
16. La página de inicio no muestra `reparacion-via.jpeg` ni
    `transporte-elicoportado-villa-garzon-putumayo.jpeg`; ambos recursos permanecen disponibles
    en `frontend/public/img` para una futura vista o sección de Servicios.

## Dudas abiertas

- [NECESITA ACLARACIÓN] Texto alternativo exacto y validado para cada una de las tres imágenes
  `productos-1.jpeg`, `productos-2.jpeg` y `productos-3.jpeg`; debe describir su contenido real
  y no puede inferirse únicamente desde el nombre del archivo.
- [NECESITA ACLARACIÓN] Logotipos de las marcas: pendientes de aportar por el usuario (no se
  generan); mientras tanto la página muestra los nombres de las marcas como texto; cuando
  existan irán en `frontend/public/img/marcas/`.
- [NECESITA ACLARACIÓN] Número de contacto definitivo de producción; el +57 312 5967913 es
  temporal, solo para desarrollo.
- [NECESITA ACLARACIÓN] Mensaje inicial de la conversación de WhatsApp: no se ha definido su
  contenido.
- [NECESITA ACLARACIÓN] Variantes del logotipo para fondos oscuros: los recursos de marca
  disponibles en `frontend/public/` son `logo-completo.jpg` y `logo-solo-tuerca.jpg` (imágenes
  con fondo blanco) y `favicon.svg` (icono vectorial); no existe una versión vectorial del
  logotipo completo ni de la tuerca apta para fondos oscuros, y debe definirse cómo se resuelve.
- [NECESITA ACLARACIÓN] Contenido exacto de la sección "Cómo funciona el servicio": los pasos
  deben definirse con el flujo de negocio aprobado y el folleto.
- [NECESITA ACLARACIÓN] Denominación de componentes: el usuario y `CONTEXTO_MAESTRO.md` usan
  "orbitroles" (plural) y el backend usa "orbitrol" en algunos tests; confirmar cuál mostrar.
