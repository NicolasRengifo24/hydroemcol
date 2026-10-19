# Spec 009 — Vista "Nosotros" (Quiénes somos)

Estado: borrador

## Contexto y objetivo

La página `/nosotros` es hoy un marcador de posición: un `h1` "Quiénes somos" y un texto que
anuncia contenido por definir. La spec 003 reservó para esta vista la misión, la visión, los
valores y la ubicación/mapa, y aprobó el contenido textual del folleto en
`specs/003-pagina-inicio/contenido-folleto.md`.

**Objetivo:** convertir la página Nosotros en la presentación institucional de la empresa: quién
es Hidroemcol, cuál es su misión, visión y valores, qué capacidades técnicas tiene, dónde está
ubicada, con un llamado a la acción claro de contacto. La sección de marcas fue eliminada de
esta página por decisión de diseño del usuario (18/10/2026); ver RF-6.

**Por qué importa:** después del hero de Inicio, la sección "Nosotros" es donde un visitante
busca confirmar que hay una empresa real detrás: identidad, criterios y capacidad. Para una
empresa industrial, esa confirmación es parte de la confianza que lleva al contacto.

**Fuentes de contenido:** texto del folleto aprobado en
`specs/003-pagina-inicio/contenido-folleto.md` (sección "Versión para el sitio") y datos ya
existentes en `frontend/src/components/inicio/contenido.ts`. Esta spec no inventa datos de
negocio: sin cifras, años de fundación, número de clientes ni certificaciones que el folleto no
contenga.

## Usuarios

| Usuario | Descripción |
|---|---|
| **Visitante (cliente potencial)** | Persona que llegó por Inicio o por el menú y quiere confirmar la identidad, la seriedad y la capacidad técnica de la empresa antes de contactar. Mayoritariamente móvil. |
| **Cliente existente** | Persona que ya conoce la empresa y reutiliza la página para reconfirmar datos de contacto o compartir la presentación con un tercero. |

## Historias de usuario

**HU-1 — Conocer la empresa de un vistazo.**
Como visitante, quiero ver quién es Hidroemcol y qué defiende, para decidir si me inspiro
confianza antes de contactar.

**HU-2 — Ver la identidad de la empresa.**
Como visitante, quiero leer la misión, la visión y los valores, para entender el criterio con
el que la empresa trabaja.

**HU-3 — Confirmar la capacidad técnica.**
Como visitante técnico, quiero ver las capacidades destacadas (banco de pruebas, diagnóstico y
reparación, importación sobre pedido), para confirmar que la empresa puede resolver mi caso.
(Las marcas ya no se muestran en esta página: sección eliminada, ver RF-6.)

**HU-4 — Contactar sin buscar.**
Como visitante convencido, quiero un llamado a la acción claro al final de la página, para
contactar en el momento.

## Decisiones aprobadas

Todas las decisiones están aprobadas por el usuario y sustituyen a las propuestas anteriores
(D-1 a D-7).

| # | Decisión | Resolución aprobada |
|---|---|---|
| D-1 | Estilo del hero | **Aprobado: hero oscuro**, coherente con el de Inicio: imagen existente con velo/sombra oscura encima y texto central encima. Transmite capacidad industrial. |
| D-2 | Contenido institucional | **Aprobado: párrafo literal de "Quiénes somos"** (texto dado por el usuario, marcado PROVISIONAL en la spec) + Misión/Visión/Valores + **cita de Brad Henry SÍ incluida** junto a Valores. |
| D-3 | Capacidades destacadas | **Aprobado: reutilizar `CAPACIDADES_TECNICAS`** existentes pero en formato de **filas editoriales con icono lateral** (icono + título + descripción, separadores sutiles, sin tarjetas como en Inicio). |
| D-4 | CTA principal | **Aprobado: "Contactar por WhatsApp"** derivado de `config/sitio.ts` (mismo patrón que el CTA de Inicio). |
| D-5 | Imagen del hero | **Aprobado: `frontend/public/img/hydroemcol-nosotros.png`** (imagen existente, NO la del banco de pruebas; errata de extensión corregida: es PNG, no existe versión JPG de esta imagen). Solo imágenes existentes en `public/img/`. |
| D-6 | Mapa y ubicación | **Aprobado: SÍ incluir mapa/ubicación.** Dirección **Calle 6 # 27b-55**: Google Maps embebido (iframe accesible con `title`) + bloque de dirección; datos añadidos a `frontend/src/config/sitio.ts`. Ya NO está fuera de alcance. |
| D-7 | Secciones y orden | **Aprobado: 6 secciones** (reconciliación post-diseño externo, 18/10/2026) — (1) hero, (2) quiénes somos, (3) misión/visión/valores + cita Brad Henry, (4) capacidades técnicas (filas editoriales), (5) ubicación/mapa, (6) CTA final. **La sección de marcas fue eliminada de la página Nosotros por decisión de diseño del usuario (18/10/2026)** (ver RF-6). **La sección de "Proceso del servicio" fue eliminada de la página Nosotros por decisión del usuario**; no se reutiliza el bloque de pasos de Inicio en esta vista. Línea de tiempo con hitos sigue descartada: no hay hitos fechados aprobados. |

## Requisitos funcionales

### RF-1 — Estructura y orden de la página

- **RF-1.1** CUANDO un visitante abre la página Nosotros, EL SISTEMA muestra las secciones en
  este orden exacto: (1) hero, (2) quiénes somos, (3) misión, visión y valores con la cita,
  (4) capacidades técnicas (filas editoriales), (5) ubicación y mapa (Calle 6 # 27b-55),
  (6) llamado a la acción final.
- **RF-1.2** EL SISTEMA no muestra ninguna sección de contenido distinta de las seis de
  RF-1.1. No existe sección de proceso/pasos ni sección de marcas en esta página (la de marcas
  fue eliminada, ver RF-6). El encabezado y el pie compartidos del sitio son elementos
  estructurales permitidos.
- **RF-1.3** EL SISTEMA mantiene cada sección identificable mediante un encabezado propio y
  visible, y un único `h1` en la página.

### RF-2 — Hero (D-1 y D-5 aprobadas)

- **RF-2.1** CUANDO un visitante abre la página, EL SISTEMA muestra primero un hero oscuro
  coherente con el de Inicio: imagen existente `frontend/public/img/hydroemcol-nosotros.png`
  como fondo (NO la del banco de pruebas) con velo/sombra oscura encima, texto central encima
  y un llamado a la acción de WhatsApp.
- **RF-2.2** EL SISTEMA muestra el hero sin desplazamiento horizontal y con el mensaje legible
  sobre la imagen en todas las anchuras soportadas.
- **RF-2.3** SI la imagen del hero no carga, ENTONCES EL SISTEMA conserva el fondo oscuro y el
  mensaje legible, sin dejar un espacio roto.

### RF-3 — Quiénes somos (D-2 aprobada)

- **RF-3.1** EL SISTEMA presenta una sección "Quiénes somos" con el siguiente párrafo
  literal, marcado como PROVISIONAL en los comentarios del código hasta su validación:

  > "Hidroemcol es una empresa técnica e industrial especializada en sistemas hidráulicos y
  > electrohidráulicos. Nos dedicamos a brindar el mejor servicio técnico y a suministrar
  > repuestos de calidad, con experiencia, responsabilidad y rapidez, para asegurar que los
  > equipos de nuestros clientes mantengan su funcionamiento normal durante el desarrollo de
  > sus operaciones. Complementamos nuestra oferta con importación sobre pedido para casos de
  > referencias especiales, servicios técnicos de diagnóstico y reparación, banco de pruebas y
  > soluciones de control aplicadas a equipos de trabajo pesado. Nuestro enfoque se fundamenta
  > en el respeto, la honestidad y la responsabilidad, con una prioridad clara: el bienestar y
  > el amor por la familia."

- **RF-3.2** EL SISTEMA no publica en esa sección cifras, fechas de fundación, tamaño de
  equipo ni datos de negocio que el folleto no contenga.

### RF-4 — Misión, visión y valores (D-2 aprobada)

- **RF-4.1** EL SISTEMA muestra los textos de Misión, Visión y Valores en la versión para el
  sitio de `specs/003-pagina-inicio/contenido-folleto.md`, sin reescritura ni recorte que
  cambie el sentido.
- **RF-4.2** EL SISTEMA muestra la cita "Las familias son las brújulas que nos guían… — Brad
  Henry" como elemento diferenciado dentro de la sección de identidad.
- **RF-4.3** EL SISTEMA presenta misión, visión y valores como bloques escaneables (título y
  texto), no como un párrafo continuo único.

### RF-5 — Capacidades técnicas (D-3 aprobada)

- **RF-5.1** EL SISTEMA presenta una sección de capacidades que incluye al menos: pruebas en
  banco, diagnóstico y reparación, e importación sobre pedido, en formato de **filas
  editoriales con icono lateral** (icono + título + descripción, separadores sutiles), sin
  tarjetas como en Inicio.
- **RF-5.2** EL SISTEMA reutiliza los textos de `CAPACIDADES_TECNICAS` en
  `frontend/src/components/inicio/contenido.ts` sin duplicarlos en un módulo paralelo con
  redacción propia.

### RF-6 — Marcas — ELIMINADA

**ELIMINADA — decisión de diseño del usuario (18/10/2026).** La sección de marcas ya no existe
en la página Nosotros: el diseño aprobado (reconciliación post-diseño externo) deja la página
con las 6 secciones de RF-1.1 y sin bloque de marcas. El componente `BloqueMarcas.tsx` y su CSS
(`.seccion--marcas`, `.marcas-nosotros*`) quedan como código muerto y se eliminan en la tarea
T13. El título "Nuestros Aliados" que se había puesto a ese bloque queda **sin efecto** al
eliminarse la sección. La sección "Marcas que atendemos" permanece únicamente en Inicio, **fuera
del alcance de esta spec** (Inicio no se modifica).

Los requisitos que siguen quedan **sin vigencia** en esta página (se conservan solo como
constancia histórica; NO se renumeran los RF restantes):

- **RF-6.1** *(sin vigencia)* EL SISTEMA mostraba las marcas que atiende la empresa con los
  logotipos ya disponibles en `frontend/public/img/marcas/`, reutilizando la lista existente de
  Inicio.
- **RF-6.2** *(sin vigencia)* SI un logotipo no carga, ENTONCES EL SISTEMA mostraría el nombre
  de la marca como texto, sin dejar un hueco vacío. Este respaldo textual estaba previsto
  **dentro del componente `BloqueMarcas`** de esta vista (CSS/JS propio), **sin modificar**
  `frontend/src/components/inicio/ListaMarcas.tsx` ni ningún otro componente de Inicio.

### RF-7 — Llamado a la acción final (D-4 aprobada)

- **RF-7.1** EL SISTEMA muestra al final de la página un llamado a la acción de contacto por
  WhatsApp cuya URL se deriva de `frontend/src/config/sitio.ts`, sin duplicar el número.
- **RF-7.2** EL SISTEMA ofrece como acción secundaria el enlace a la solicitud de servicio
  (`/solicitar`), con jerarquía visual claramente diferenciada.
- **RF-7.3** EL SISTEMA marca el enlace de WhatsApp como que se abre en una pestaña nueva,
  con el aviso para lectores de pantalla ya usado en el resto del sitio.

### RF-8 — Identidad visual

- **RF-8.1** EL SISTEMA usa los tokens existentes de `frontend/src/index.css` (azul
  `#2e3192`, acento `#ffc908`, tipografía Montserrat) sin definir colores nuevos fuera de la
  paleta.
- **RF-8.2** EL SISTEMA no comunica información importante únicamente por medio del color.

### RF-9 — Animaciones

- **RF-9.1** EL SISTEMA aplica a las secciones la animación de aparición existente
  (`useAparecerAlEntrar`), con la misma línea visual que Inicio.
- **RF-9.2** MIENTRAS el dispositivo tenga activada la preferencia de reducir movimiento,
  EL SISTEMA muestra todas las secciones estáticas y completas.

### RF-10 — Ubicación y mapa (D-6 aprobada)

- **RF-10.1** EL SISTEMA muestra la sección de ubicación (sección 5 de RF-1.1) con la
  dirección **Calle 6 # 27b-55** en un bloque de dirección y un mapa de Google Maps embebido
  mediante iframe accesible con `title`.
- **RF-10.2** EL SISTEMA ofrece además un enlace alternativo a Google Maps (target en
  pestaña nueva con aviso para lectores de pantalla) por si el iframe no carga o el visitante
  prefiera abrirlo fuera del sitio.
- **RF-10.3** El mapa es responsive: sin desplazamiento horizontal en ninguna anchura
  soportada y con proporción estable en móvil, tablet y escritorio.
- **RF-10.4** EL SISTEMA no inventa coordenadas ni puntos de referencia: la dirección y la URL
  de embed provienen de `frontend/src/config/sitio.ts`.

### RF-11 — Contenido y validación

- **RF-11.1** EL SISTEMA muestra únicamente texto proveniente del folleto aprobado o de datos
  ya existentes en el frontend; cualquier texto nuevo queda marcado como provisional en los
  comentarios del código hasta su validación.
- **RF-11.2** CUANDO el usuario aporte dirección, imágenes nuevas o textos adicionales, EL
  SISTEMA permite incorporarlos sin alterar el orden de las secciones de RF-1.1.

## Requisitos no funcionales

- **RNF-1** La página debe diseñarse con enfoque móvil primero y ser usable en móvil, tablet y
  escritorio, sin desplazamiento horizontal en ninguna anchura soportada.
- **RNF-2** En pantallas pequeñas, los elementos interactivos deben tener al menos 44×44 px y
  los textos al menos 16 px de cuerpo.
- **RNF-3** La jerarquía de encabezados debe ser lógica: un solo `h1` por página y niveles
  subsiguientes sin saltos.
- **RNF-4** Toda imagen que aporte información debe tener texto alternativo significativo; las
  decorativas (fondos con velo) deben quedar fuera del árbol de accesibilidad.
- **RNF-5** Todos los elementos interactivos deben ser alcanzables y operables con teclado y
  mostrar foco visible.
- **RNF-6** El contraste mínimo debe ser 4.5:1 para texto normal y 3:1 para texto grande,
  incluida la combinación del texto sobre la imagen del hero con velo.
- **RNF-7** Con `prefers-reduced-motion: reduce` no debe reproducirse ninguna animación de
  aparición.
- **RNF-8** Si una imagen no carga, la página debe seguir siendo comprensible, sin espacios
  rotos ni saltos de posición.
- **RNF-9** Los textos visibles deben estar en español y usar la terminología de la empresa de
  forma consistente.
- **RNF-10** La página debe ser visual y funcionalmente consistente con Inicio (mismos tokens,
  misma línea de animación, mismos patrones de CTA).
- **RNF-11** La página es estática: no hace llamadas a la API, no debe quedar en blanco y no
  requiere estados de carga o error remotos.

## Casos límite

- El visitante abre la página en 320 px: sin desplazamiento horizontal ni recortes de texto.
- La imagen del hero no carga: fondo oscuro y mensaje legible se conservan.
- Sección de marcas eliminada: en esta página no se muestran logotipos de marca; cualquier
  referencia a marcas (incluido el respaldo textual de logos) queda sin efecto aquí. La carga de
  logos aplica solo a Inicio, fuera de alcance.
- El visitante tiene activada la preferencia de reducir movimiento: todas las secciones
  estáticas y completas.
- El sistema bloquea la apertura de WhatsApp: el enlace de llamada alternativo sigue
  disponible en la misma sección.
- El iframe del mapa no carga: el bloque de dirección y el enlace alternativo a Google Maps
  siguen disponibles en la misma sección.
- El visitante abre la página en una anchura móvil estrecha: el mapa se adapta sin provocar
  desplazamiento horizontal.
- El visitante navega solo con teclado: recorre todas las secciones y acciones con foco
  visible, incluido el iframe del mapa y el enlace alternativo.
- El visitante amplía la página al 200 %: el contenido sigue legible y no se pierde ninguna
  acción.
- El texto nuevo de "Quiénes somos" aún no está validado: se marca provisional y no afirma
  datos de negocio no verificados.

## Fuera de alcance

Esta versión **no** incluye:

- Cambios en el backend, la API, el modelo de datos o las rutas del servidor.
- La sección de "Proceso del servicio" (pasos del servicio) en esta página: eliminada por
  decisión del usuario; la página queda con 6 secciones.
- La sección de marcas en esta página: **ELIMINADA — decisión de diseño del usuario
  (18/10/2026)**, ver RF-6. No se implementa `BloqueMarcas` en esta vista y su código se
  elimina (T13). "Marcas que atendemos" permanece solo en Inicio (fuera de alcance) y el título
  "Nuestros Aliados" queda sin efecto.
- Línea de tiempo con hitos o cronología de la empresa (no hay hitos fechados aprobados).
- Fotografías del equipo, de instalaciones o nuevas imágenes: solo recursos existentes en
  `frontend/public/img/`.
- Las imágenes reservadas para la futura vista de Servicios (`reparacion-via.jpeg`,
  `transporte-elicoportado-villa-garzon-putumayo.jpeg`).
- Modificar Inicio, el Layout, el router o cualquier otra página del sitio.
- Integración con WhatsApp Business API, redes sociales nuevas o formularios de contacto.
- Contenido en idiomas distintos del español.
- Cualquier dato de negocio no contenido en el folleto aprobado.

## Criterios de aceptación

La página Nosotros está terminada cuando:

1. Las seis secciones aparecen en el orden de RF-1.1 (hero, quiénes somos, identidad + cita,
   capacidades, ubicación/mapa, CTA final), con un solo `h1` y encabezados propios por sección, y
   no hay sección de proceso/pasos ni sección de marcas.
2. El hero (D-1 y D-5 aprobadas) es oscuro, coherente con Inicio, usa la imagen existente
   `hydroemcol-nosotros.png` con velo oscuro y texto central, y conserva mensaje y CTA si la
   imagen falla.
3. Misión, visión, valores y la cita de Brad Henry coinciden literalmente con la versión para
   el sitio del folleto, presentados en bloques escaneables.
4. Las capacidades técnicas se muestran reutilizando `CAPACIDADES_TECNICAS` en formato de
   filas editoriales con icono lateral, con banco de pruebas, diagnóstico/reparación e
   importación sobre pedido visibles.
5. No queda código muerto de la sección de marcas eliminada: `BloqueMarcas.tsx` y su CSS
   (`.seccion--marcas`, `.marcas-nosotros*`) fueron eliminados de `frontend/` (T13) y ninguna
   página distinta de Inicio muestra una sección de marcas.
6. El CTA (D-4 aprobada) deriva WhatsApp de `config/sitio.ts`, marca "se abre en una pestaña
   nueva" y presenta la solicitud de servicio como acción secundaria.
7. La sección de ubicación muestra la dirección "Calle 6 # 27b-55" y el mapa de Google Maps
   embebido con `title` accesible, enlace alternativo a Google Maps, y es responsive sin
   desplazamiento horizontal en ninguna anchura soportada.
8. La página no tiene desplazamiento horizontal a 320, 375, 768 y 1024 px o más; textos desde
   16 px y targets desde 44×44 px.
9. Con `prefers-reduced-motion: reduce` no hay animaciones de aparición.
10. `tsc --noEmit` en `frontend/` termina sin errores y la ruta `/nosotros` renderiza la
     página completa sin errores de consola.

## Dudas abiertas

No quedan dudas abiertas: D-1 a D-7 están resueltas en la sección "Decisiones aprobadas".
El párrafo de "Quiénes somos" permanece marcado como PROVISIONAL hasta su validación final
(RF-11.1).
