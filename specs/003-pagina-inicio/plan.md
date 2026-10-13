# Plan — specs/003-pagina-inicio

## Estado y alcance

La spec `specs/003-pagina-inicio/spec.md` está aprobada y es la fuente de verdad. Este plan
cubre únicamente la página pública de inicio (`/`), sin cambios en backend, API, modelo de
datos ni otras páginas. Se conserva el stack existente y no se añaden dependencias.

La página se compone en el orden fijo de RF-1.1: (1) hero, (2) servicios destacados, (3)
componentes y capacidad técnica, (4) cómo funciona el servicio y (5) CTA final. El encabezado,
el pie y el acceso estructural a contacto se conservan como elementos compartidos.

Cambios aprobados que este plan debe reflejar:

- `Hero.tsx` conserva el h1 provisional, el CTA y exactamente tres tarjetas, pero deja de
  renderizar el `Logo` grande porque la marca ya aparece en el navbar.
- `productos-1.jpeg`, `productos-2.jpeg` y `productos-3.jpeg` se muestran exclusivamente en
  el bloque `Importación Sobre Pedido` de `BloqueServiciosDestacados`, mediante un carrusel
  accesible. No se crea una sexta sección ni una galería genérica.
- `reparacion-via.jpeg` y `transporte-elicoportado-villa-garzon-putumayo.jpeg` permanecen
  disponibles para una futura vista de Servicios y no se renderizan en Inicio.
- Los `alt` confirmados ya presentes en `contenido.ts` se mantienen sin reescritura ni
  inferencias nuevas.

## 1. Archivos y responsabilidades

### 1.1 Archivos nuevos

| Archivo | Responsabilidad | RF/RNF |
|---|---|---|
| `frontend/src/config/sitio.ts` | Único punto de configuración del contacto, URLs de WhatsApp/llamada y Facebook, con los datos de desarrollo marcados como temporales. | RF-9.1–9.4, RF-10.3 |
| `frontend/src/components/inicio/contenido.ts` | Datos estáticos y tipos de la página: tarjetas, servicios, componentes, capacidades, marcas, pasos e `ImagenFolleto`. `IMAGENES_FOLLETO` conserva los tres productos para el carrusel y las dos imágenes reservadas, sin que estas últimas se rendericen en Inicio. | RF-2.4–2.6, RF-4.1–4.7, RF-5.1–5.5, RF-6.1–6.4, RF-11.1–11.4 |
| `frontend/src/components/inicio/inicio.css` | Estilos de Inicio: layout responsive, animación de tarjetas, carrusel, estados de foco/error y reglas `prefers-reduced-motion`, reutilizando los tokens existentes. | RF-3, RF-4.5–4.8, RNF-1, RNF-2, RNF-7, RNF-8, RNF-11, RNF-14 |
| `frontend/src/components/inicio/SeccionEncabezado.tsx` | Encabezado reutilizable de sección con título, descripción opcional, nivel configurable e `id` para `aria-labelledby`. | RF-1.3, RNF-3, RNF-4 |
| `frontend/src/components/inicio/TarjetaServicio.tsx` | Bloque informativo reutilizable de título y descripción, con animación del hero y estados visuales de interacción. | RF-2.4–2.6, RF-3, RF-4.1–4.2, RNF-6, RNF-8 |
| `frontend/src/components/inicio/CarruselProductos.tsx` | Carrusel reutilizable que recibe `ImagenFolleto[]`, mantiene internamente el índice activo, ofrece anterior/siguiente, y opcionalmente indicadores si mejoran la orientación. Incluye semántica y controles en español, operación por teclado, soporte táctil mediante controles de tamaño adecuado, `aria-live` prudente, reducción de movimiento y fallback de imagen. | RF-4.5–4.8, RF-11.2, RF-11.4, RNF-2, RNF-5, RNF-6, RNF-8, RNF-10, RNF-11, RNF-14, RNF-15 |
| `frontend/src/components/inicio/Hero.tsx` | Primera sección: mensaje principal provisional en un único h1, CTA y exactamente tres tarjetas. No renderiza `Logo`. | RF-1.1, RF-2.1–2.7, RF-3.1–3.4 |
| `frontend/src/components/inicio/BloqueServiciosDestacados.tsx` | Segunda sección: cuatro servicios en orden estable, informativos y sin enlaces; asocia `CarruselProductos` únicamente al servicio `Importación Sobre Pedido`. | RF-1.1, RF-4.1–4.8, RF-11.4 |
| `frontend/src/components/inicio/ListaMarcas.tsx` | Lista textual de las 14 marcas, con soporte opcional de logo futuro sin dejar huecos. | RF-5.5, RF-11.2–11.3, RNF-5, RNF-10 |
| `frontend/src/components/inicio/BloqueCapacidadTecnica.tsx` | Tercera sección: componentes, capacidades, marcas y video del banco de pruebas. No recibe ni renderiza las imágenes del carrusel. | RF-1.1, RF-5.1–5.11 |
| `frontend/src/components/inicio/BloqueVideo.tsx` | Video con reproducción silenciosa, control visible, reducción de movimiento y degradación segura ante error. | RF-5.6–5.10, RNF-8, RNF-10 |
| `frontend/src/components/inicio/BloquePasos.tsx` | Cuarta sección con la secuencia provisional de cinco pasos aprobados. | RF-1.1, RF-6.1–6.4 |
| `frontend/src/components/inicio/CTASection.tsx` | Quinta sección con solicitar, seguimiento y contacto, incluida la alternativa de llamada. | RF-1.1, RF-7.1–7.5, RF-9.1–9.4 |

### 1.2 Archivos editados

| Archivo | Acción | Responsabilidad | RF/RNF |
|---|---|---|---|
| `frontend/src/pages/Inicio.tsx` | Reescribir | Ensamblar las cinco secciones en el orden de RF-1.1, con un solo h1 proveniente del hero. | RF-1.1–1.3, RNF-3–4 |
| `frontend/src/components/Layout.tsx` | Editar mínimamente | Añadir el enlace único a Facebook en el pie sin alterar el comportamiento compartido. | RF-10.1–10.3 |
| `frontend/src/components/brand/Logo.tsx` | Reescribir | Usar los recursos reales de marca y conservar la interfaz existente; el componente seguirá en el navbar, no en `Hero`. | RF-2.2, RF-8.3, RNF-5, RNF-10 |
| `frontend/src/components/brand/marca.css` | Editar | Estilos del logo y resolución provisional sobre fondos oscuros. | RF-8.3, RNF-11 |
| `frontend/src/index.css` | Editar | Corregir el token de acento a `#ffc908`. | RF-8.2 |
| `frontend/src/components/brand/Tuerca.tsx` | Eliminar | Ya no se usa al rehacer `Logo.tsx`. | RF-2.2, RF-8.3 |

`frontend/src/router.tsx` no se modifica: la ruta `/` ya monta `Inicio` y las rutas existentes de
los CTA se reutilizan.

## 2. Interfaces y datos

Tipos compartidos en `contenido.ts`:

```ts
export interface TarjetaServicio { titulo: string; descripcion: string }
export interface ServicioDestacado { titulo: string; descripcion: string }
export interface Marca { nombre: string; logo?: string }
export interface Paso { numero: number; titulo: string; descripcion?: string }
export interface ImagenFolleto { src: string; alt: string }
```

La interfaz mínima del nuevo carrusel es:

```ts
interface CarruselProductosProps {
  imagenes: ImagenFolleto[]
  id?: string
  className?: string
}
```

El índice activo es estado interno del carrusel; no se agrega estado al padre ni se convierte
`BloqueServiciosDestacados` en una galería genérica. El carrusel recibe únicamente las tres
imágenes de producto, en el orden estable de `IMAGENES_FOLLETO`. Las imágenes reservadas se
mantienen disponibles en la colección de datos o en una colección futura claramente separada,
pero no se pasan al carrusel ni a ningún bloque de Inicio.

El `alt` de cada imagen se toma literalmente del objeto `ImagenFolleto` confirmado en
`contenido.ts`. No se sustituye por el nombre del archivo ni se inventan descripciones nuevas.

## 3. Decisiones técnicas

- **D-1. Hero sin logo grande.** El logo compartido del navbar es la única identificación visual
  de marca en el encabezado; `Hero` no importa ni renderiza `Logo`. Se conserva un único h1, el
  CTA y tres tarjetas.
- **D-2. Carrusel específico del bloque de importación.** `CarruselProductos` es reutilizable a
  nivel de componente, pero en esta entrega solo se instancia dentro del servicio cuyo título es
  `Importación Sobre Pedido`. Se descarta una sexta sección o una galería en capacidad técnica
  porque contradicen RF-1.2, RF-4.5 y RF-5.11.
- **D-3. Estado interno y controles explícitos.** El carrusel inicia en el primer elemento y
  cambia el índice con anterior/siguiente, con navegación circular o límites consistentes según
  el diseño existente; los botones siempre son visibles, tienen `aria-label` en español, foco
  visible y área mínima de 44×44 px. Si se usan indicadores, cada uno identifica su imagen y es
  operable por teclado.
- **D-4. Accesibilidad prudente.** La imagen activa se anuncia mediante una región `aria-live`
  no intrusiva, evitando anunciar cada detalle redundante. El carrusel se opera con teclado y no
  depende de swipe; el soporte táctil se garantiza por los targets y controles visibles. Los
  eventos de teclado no desplazan la página de forma inesperada.
- **D-5. Movimiento reducido.** Las transiciones del carrusel y la animación de entrada de las
  tarjetas se desactivan con `prefers-reduced-motion: reduce`; la imagen activa y sus controles
  permanecen disponibles. No se usa autoplay, por lo que el contenido no cambia sin una acción
  del visitante.
- **D-6. Error de imagen.** Si la imagen activa falla, el carrusel conserva el marco y muestra
  un mensaje alternativo comprensible con los controles disponibles; no muestra un icono roto,
  no genera overflow y el texto del servicio sigue siendo suficiente para entenderlo.
- **D-7. Datos separados.** `IMAGENES_FOLLETO` conserva los tres productos y las dos imágenes
  reservadas con sus `alt` confirmados. La integración filtra explícitamente los productos o usa
  una colección de productos separada para evitar que las imágenes futuras lleguen al Inicio.
- **D-8. Sin dependencias nuevas.** Se usan React, TypeScript, CSS y las dependencias ya instaladas.
  No se incorpora una librería de carrusel ni de accesibilidad.
- **D-9. Tokens y marca.** Se mantienen `#2E3192` como azul principal y `#ffc908` como acento;
  el texto no depende solo del color y el logo compartido no se deforma ni recolorea.

## 4. Pseudocódigo del carrusel

```text
imagenes = solo los tres productos
indiceActivo = 0
hayError = false

al pulsar Anterior:
    indiceActivo = índice anterior dentro de imagenes
    hayError = false

al pulsar Siguiente:
    indiceActivo = índice siguiente dentro de imagenes
    hayError = false

al cambiar imagen activa:
    renderizar una sola imagen con src y alt del elemento activo
    anunciar de forma no intrusiva "Producto X de 3" en aria-live

si la imagen activa falla:
    hayError = true
    mostrar fallback textual dentro del mismo marco
    conservar servicio, controles y ausencia de overflow

si prefers-reduced-motion = reduce:
    no aplicar transición
si no:
    aplicar transición breve solo al cambio iniciado por el visitante
```

## 5. Matriz de cobertura

| Parte | Cobertura principal | Criterios de finalización |
|---|---|---|
| `Inicio.tsx` y `Hero.tsx` | RF-1, RF-2, RF-3, RNF-3, RNF-4 | 1–4 |
| `BloqueServiciosDestacados.tsx` + `CarruselProductos.tsx` | RF-4.1–4.8, RF-11.2, RF-11.4, RNF-2, RNF-5–6, RNF-8, RNF-10–11, RNF-14–15 | 2, 9, 12, 13, 15, 16 |
| `contenido.ts` | RF-2.4–2.6, RF-4.1, RF-5.1–5.5, RF-6, RF-11 | 3, 12, 13, 15, 16 |
| `BloqueCapacidadTecnica` + `ListaMarcas` + `BloqueVideo` | RF-5.1–5.11 | 12, 13, 14 |
| `BloquePasos` | RF-6.1–6.4 | 12 |
| `CTASection` + `config/sitio.ts` | RF-7, RF-9 | 6, 7 |
| `Logo.tsx` + estilos + `Layout.tsx` | RF-8, RF-10, RNF-5, RNF-11 | 2, 5 |
| Todo el conjunto | RNF-1, RNF-2, RNF-7, RNF-12, RNF-13 | 8, 9, 10, 11 |

## 6. Verificación

No hay framework de tests frontend y no se instalan dependencias de prueba. La verificación será:

1. Ejecutar `npm run build` en `frontend/` para detectar errores de TypeScript, imports y rutas.
2. Ejecutar `npm run lint` en `frontend/` sin incidencias.
3. Servir la aplicación y comprobar con MCP de Chrome DevTools:
   - 320 px, 375 px, 768 px y 1024 px o más: orden de secciones, ausencia de overflow,
     tarjetas completas y targets interactivos de al menos 44×44 px.
   - Hero sin logo grande, un solo h1, CTA y exactamente tres tarjetas.
   - Carrusel dentro de `Importación Sobre Pedido`, solo con las tres imágenes de productos;
     controles visibles, foco, teclado, cambio de imagen, `aria-live` prudente y `alt` confirmado.
   - Preferencia `prefers-reduced-motion: reduce`: tarjetas estáticas y carrusel sin transición.
   - Fallo de una imagen: fallback comprensible sin espacio roto ni desplazamiento horizontal.
   - Componentes y capacidad técnica sin ninguna de las tres imágenes de productos.
   - Navegación por teclado, contraste, jerarquía de encabezados y enlaces del CTA.
   - Video con control de reproducción/pausa, sin sonido automático y con degradación segura.

Si Chrome DevTools no está disponible, se documenta y se usa el navegador disponible; el build y
el lint siguen siendo obligatorios.

## 7. Decisiones pendientes antes de implementar

La solicitud aprobada define la arquitectura suficiente para implementar el carrusel y no requiere
una nueva aprobación de alcance. Se mantienen como pendientes de producto ya documentados en la
spec, pero no bloquean este ajuste de plan: número definitivo de producción, URL real de Facebook,
variantes del logo sobre fondos oscuros y validación final del contenido provisional de pasos y
del h1. Los `alt` de las cinco imágenes no son una decisión pendiente para esta implementación:
los tres de productos y los dos recursos reservados ya están confirmados en `contenido.ts`.
