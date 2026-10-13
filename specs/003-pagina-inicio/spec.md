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

**Contexto de contenido:** el contenido textual e imágenes definitivos provienen de un
folleto físico de la empresa que el usuario transcribirá. El agente no puede leer ni
interpretar imágenes, por lo que el contenido de esta página se redacta como borrador y debe
validarse con el folleto real antes de considerar la página terminada. Esta spec no inventa
requisitos de negocio ni datos que el folleto aún no ha entregado.

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
  Presenta la marca, el mensaje principal, el botón de acción principal y las tres tarjetas de
  servicio.
- **Tarjeta de servicio:** bloque visual reutilizable que resume una categoría de servicio o
  componente, con un título y una descripción breve.
- **Servicios destacados:** sección que presenta las áreas de servicio de la empresa: las
  mismas tres del hero y otras categorías adicionales, en formato informativo (título y
  descripción, sin enlace).
- **Capacidad técnica / componentes:** sección que comunica qué componentes atiende la
  empresa y con qué medios técnicos cuenta (por ejemplo, pruebas en banco).
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
- **Contenido provisional:** texto o imagen de borrador, no proveniente del folleto
  definitivo, que debe reemplazarse antes de dar la página por terminada.

## Requisitos funcionales

### RF-1 — Estructura y orden de la página

- **RF-1.1** CUANDO un visitante abre la página de inicio, EL SISTEMA muestra las secciones
  en este orden exacto: (1) hero o encabezado principal con el logotipo, el mensaje, el botón
  de acción principal y las tres tarjetas, (2) servicios destacados, (3) componentes y
  capacidad técnica, (4) cómo funciona el servicio, (5) llamado a la acción final.
- **RF-1.2** EL SISTEMA no muestra en la página de inicio ninguna sección de contenido
  distinta de las cinco enumeradas en RF-1.1. El encabezado y el pie compartidos del sitio
  (RF-10) y el acceso a contacto (RF-9) son elementos estructurales permitidos y no cuentan
  como secciones de contenido.
- **RF-1.3** EL SISTEMA mantiene cada sección identificable mediante un encabezado propio y
  visible, de modo que el visitante pueda reconocer dónde empieza cada una al desplazarse.

### RF-2 — Encabezado principal (hero)

- **RF-2.1** CUANDO un visitante abre la página de inicio, EL SISTEMA muestra primero el hero
  con cuatro elementos: el logotipo de la marca, un mensaje que explica qué hace la empresa,
  un botón de acción principal ("solicitar un servicio") y las tres tarjetas de servicio.
- **RF-2.2** EL SISTEMA muestra en el hero el logotipo completo de la marca —la tuerca junto
  con el nombre "HYDROEMCOL SERVICE AND PARTS S.A.S"—, que es la versión confirmada de la
  marca.
- **RF-2.3** EL SISTEMA muestra en el hero exactamente tres tarjetas de servicio, ni más ni
  menos.
- **RF-2.4** EL SISTEMA muestra la primera tarjeta del hero con el título "Servicios técnicos
  hidráulicos" y la descripción "diagnóstico, reparación y pruebas en banco".
- **RF-2.5** EL SISTEMA muestra la segunda tarjeta del hero con el título "Repuestos e
  importación sobre pedido" y la descripción "cilindros, bombas, motores, válvulas,
  orbitroles".
- **RF-2.6** EL SISTEMA muestra la tercera tarjeta del hero con el título "Sistemas
  electrohidráulicos a medida" y la descripción "control proporcional, marcha y velocidad,
  asesoría e implementación".
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
  interacción del visitante (señalización al pasar el puntero, foco de teclado y pulsación
  táctil), de modo que la animación no la oculte ni la atenúe.
- **RF-3.4** SI el contenido definitivo de una tarjeta aún no está disponible, ENTONCES EL
  SISTEMA mantiene visible el texto provisional o el título confirmado de esa tarjeta, sin
  dejar el espacio vacío.

### RF-4 — Servicios destacados

- **RF-4.1** CUANDO un visitante abre la página de inicio, EL SISTEMA presenta una sección de
  servicios destacados que incluye las mismas tres áreas de servicio del hero y, además, otras
  categorías (orientativas: banco de pruebas, importación sobre pedido, asesoría e
  implementación, y servicios ya realizados), cada una con un título y una descripción breve.
  El contenido concreto de todas las categorías queda provisional a la espera del folleto.
- **RF-4.2** EL SISTEMA presenta cada servicio destacado como contenido informativo (título y
  descripción), sin enlace ni acción de navegación.
- **RF-4.3** SI el contenido de un servicio destacado aún no está confirmado con el folleto,
  ENTONCES EL SISTEMA muestra el texto provisional sin afirmar datos de negocio no
  verificados (precios, disponibilidad, capacidades numéricas o marcas).
- **RF-4.4** EL SISTEMA presenta los servicios destacados en el mismo orden en cada carga de
  la página.

### RF-5 — Componentes y capacidad técnica

- **RF-5.1** CUANDO un visitante abre la página de inicio, EL SISTEMA presenta una sección que
  comunica qué componentes atiende la empresa, incluyendo al menos cilindros, bombas, motores,
  orbitroles, controles y válvulas.
- **RF-5.2** EL SISTEMA presenta en esa sección la capacidad técnica de la empresa,
  mencionando explícitamente las pruebas en banco.
- **RF-5.3** SI una categoría de componente o una capacidad técnica no está confirmada con el
  folleto, ENTONCES EL SISTEMA la muestra como contenido provisional y no como hecho
  comercial definitivo.
- **RF-5.4** EL SISTEMA expone los componentes y capacidades en formato de lista o conjunto de
  bloques escaneables, no en un párrafo de texto continuo.

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
- **RF-8.3** EL SISTEMA usa el logotipo completo de la marca de forma consistente en la página
  de inicio, sin deformarlo ni recolorearlo fuera de la paleta corporativa.
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

### RF-11 — Contenido provisional y validación

- **RF-11.1** MIENTRAS el contenido del folleto no se haya incorporado, EL SISTEMA presenta el
  texto de la página de inicio como borrador y no publica cifras, capacidades, marcas ni
  disponibilidad no confirmadas.
- **RF-11.2** CUANDO el contenido definitivo del folleto esté disponible, EL SISTEMA permite
  reemplazar el texto provisional sin alterar la estructura ni el orden de las secciones.

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
  mermar la fluidez de la página.
- **RNF-12** Los textos visibles de la página deben estar en español y usar la terminología de
  la empresa de forma consistente.
- **RNF-13** La página debe ser visual y funcionalmente consistente con el resto del sitio, de
  modo que el visitante reconozca una misma identidad y un mismo comportamiento.

## Casos límite

- El visitante abre la página en un teléfono de 320 píxeles de ancho: no debe aparecer
  desplazamiento horizontal ni recortes de texto.
- El visitante tiene activada la preferencia de reducir movimiento: las tres tarjetas del hero
  se muestran completas y estáticas, y ninguna información queda solo en la animación.
- El sistema operativo o el navegador bloquea la apertura de WhatsApp: el visitante encuentra
  una alternativa de contacto comprensible en la misma página.
- El número de contacto aún es el de desarrollo (312 5967913): la página debe seguir siendo
  funcional y no debe presentarlo como dato definitivo de producción.
- Las imágenes de marca o de producto no cargan o tardan: la página conserva su estructura y
  su mensaje principal.
- El visitante navega solo con teclado: puede recorrer las secciones, las tarjetas y las
  acciones, y ver siempre el foco.
- El visitante amplía la página al 200 %: el contenido sigue siendo legible y no se pierde
  ninguna acción.
- El contenido definitivo del folleto todavía no llegó: la página muestra texto provisional y
  no inventa datos de negocio ni de productos.
- El visitante llega desde un enlace directo al final de la página: las acciones principales
  siguen siendo alcanzables.
- El script de la página tarda en cargar: el contenido principal no queda vacío.

## Fuera de alcance

Esta versión **no** incluye:

- La ubicación o el mapa de Google Maps. El usuario decidió que irá en la página "Nosotros" y
  se implementará aparte.
- La página "Nosotros" y cualquier otra página del sitio: Servicios, Soluciones, Contacto,
  Solicitar servicio, Seguimiento y el panel administrativo. Esta spec solo cubre la página de
  inicio.
- Cambios en el backend, en la API o en la lógica de negocio.
- Catálogo comercial, e-commerce, carrito, pagos, precios, inventario público o disponibilidad
  de productos.
- La recolección y transcripción del contenido del folleto físico: es una dependencia externa
  que aporta el usuario.
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
3. El hero muestra el logotipo completo de la marca, el mensaje principal, el botón de acción
   principal y exactamente tres tarjetas con los tres títulos y descripciones definidos en
   esta spec (RF-2.4 a RF-2.6), pendientes de validar con el folleto.
4. Las tres tarjetas del hero reproducen su animación al aparecer la página y la terminan en
   un tiempo acotado, conservan siempre visible su contenido y, con la preferencia de reducir
   movimiento activada, se muestran sin animación y completas.
5. La página usa el azul #2E3192 como color principal y el #FFC908 como acento, y el logotipo
   se muestra sin deformar.
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
12. Si el contenido definitivo del folleto está disponible, su texto e imágenes han sido
    incorporados y validados por el usuario y ya no queda contenido provisional; mientras no
    esté disponible, la página funciona con el contenido provisional como borrador válido.

## Dudas abiertas

- [NECESITA ACLARACIÓN] Contenido real del folleto físico (textos e imágenes definitivos de
  servicios, componentes y capacidad técnica). El agente no puede leer imágenes; el usuario
  transcribirá el texto. Todo el contenido de la página es un borrador a validar contra el
  folleto.
- [NECESITA ACLARACIÓN] Número de contacto definitivo de producción; el +57 312 5967913 es
  temporal, solo para desarrollo.
- [NECESITA ACLARACIÓN] Mensaje inicial de la conversación de WhatsApp: no se ha definido su
  contenido.
- [NECESITA ACLARACIÓN] Número de accesos visibles a WhatsApp en la página de inicio: si debe
  haber uno solo o varios que compartan el mismo valor de contacto.
- [NECESITA ACLARACIÓN] Alcance del seguimiento en esta spec: si debe incluirse aquí la página
  donde el cliente ingresa o pega su código de servicio, o si la página de inicio solo enlaza
  al acceso de seguimiento ya existente.
- [NECESITA ACLARACIÓN] Variantes del logotipo para fondos oscuros: los recursos de marca
  disponibles son `frontend/public/logo-completo.jpg` y `frontend/public/logo-solo-tuerca.jpg`
  (imágenes con fondo blanco) y `frontend/public/favicon.svg` (icono vectorial); no existe una
  versión vectorial del logotipo completo ni de la tuerca apta para fondos oscuros, y debe
  definirse cómo se resuelve.
- [NECESITA ACLARACIÓN] Contenido exacto de la sección "Cómo funciona el servicio": los pasos
  deben validarse con el folleto y con el flujo de negocio aprobado.
- [NECESITA ACLARACIÓN] Categorías de componentes definitivas que se mostrarán y su
  denominación correcta (por ejemplo, confirmar si la denominación es "orbitrol" u
  "orbitroles").
- [NECESITA ACLARACIÓN] Alcance de "servicios ya realizados" en Servicios destacados: si
  implica una galería de trabajos hechos (lo que sería una sección nueva y cambiaría la
  estructura de cinco secciones) o solo más categorías informativas.
