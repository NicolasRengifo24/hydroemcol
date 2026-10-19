# Plan — specs/009-vista-nosotros

## Estado y alcance

La spec `specs/009-vista-nosotros/spec.md` está en borrador y es la fuente de verdad. Este plan
cubre únicamente la página pública `/nosotros`, sin cambios en backend, API, modelo de datos,
router ni otras páginas. Se conserva el stack existente y no se añaden dependencias.

Este plan es ejecutable una vez aprobada la spec. Las decisiones D-1 a D-7 están aprobadas:
D-1 (hero oscuro), D-2 (párrafo literal de "Quiénes somos" + cita de Brad Henry), D-3
(capacidades en filas editoriales con icono), D-4 (CTA WhatsApp), D-5 (imagen
`hydroemcol-nosotros.png`), D-6 (SÍ incluir mapa: Calle 6 # 27b-55) y D-7 (orden de las 6
secciones, sin sección de proceso ni sección de marcas).

La página se compone en el orden de RF-1.1: hero, quiénes somos, misión/visión/valores +
cita, capacidades técnicas, ubicación/mapa, CTA final. **La sección de "Proceso del
servicio" fue eliminada de la página Nosotros por decisión del usuario y la sección de marcas
fue eliminada por decisión de diseño del usuario (18/10/2026): 6 secciones, sin pasos y sin
marcas.** No hay lógica con
fechas: la página es
estática, por lo que **no aplica ninguna función pura con parámetro `hoy`** (no se calcula
nada derivado del tiempo; si en el futuro se añade un dato fechado, deberá recibir `hoy` como
parámetro y salir de esta spec).

**Nota de reconciliación post-diseño externo (18/10/2026):** un agente externo modificó el
diseño de `/nosotros` y el usuario lo aprobó (6 secciones, sin sección de marcas; el título
"Nuestros Aliados" queda sin efecto). Este plan se actualiza a ese diseño y **no se rediseña
nada**: `BloqueMarcas.tsx` y el CSS de marcas (`.seccion--marcas`, `.marcas-nosotros*`) en
`nosotros.css` quedan como código muerto a eliminar en **T13**. "Marcas que atendemos"
permanece solo en Inicio, fuera de alcance.

## 1. Arquitectura

- Solo frontend React + TypeScript, montaje en la ruta ya existente `/nosotros`
  (`frontend/src/router.tsx:25`, sin modificar).
- Patrón idéntico a Inicio: `pages/Nosotros.tsx` ensambla bloques presentacionales; los
  bloques viven en `frontend/src/components/nosotros/`; los datos estáticos, en un
  `contenido.ts` propio; los estilos, en un CSS propio que importa los tokens globales.
- Los bloques reutilizables de Inicio se importan desde `components/inicio/` en lugar de
  duplicarlos: `SeccionEncabezado` es un componente con props genéricas (`nivel`, `id`).
  `ListaMarcas` **ya no se reutiliza** en esta vista: la sección de marcas fue eliminada
  (reconciliación post-diseño externo, 18/10/2026; RF-6). El bloque de pasos de Inicio **no se
  reutiliza** en esta vista (sección de proceso eliminada, D-7).
- Sin llamadas a la API, sin estado remoto, sin TanStack Query en esta página (RNF-11).

## 2. Impacto — archivos

### 2.1 Archivos nuevos

| Archivo | Responsabilidad | RF/RNF |
|---|---|---|
| `frontend/src/components/nosotros/contenido.ts` | Datos estáticos de la página: mensaje del hero, párrafo de "Quiénes somos" (marcado PROVISIONAL hasta validación), textos de identidad referenciados, imagen del hero con `alt`, y re-export de lo que se toma de Inicio. | RF-2, RF-3, RF-4, RF-5, RF-11, RNF-4 |
| `frontend/src/components/nosotros/nosotros.css` | Estilos de la página: hero oscuro con velo, bloques de identidad, filas editoriales de capacidades con icono lateral, bloque de ubicación y mapa responsive, `revelar` y `prefers-reduced-motion`, reutilizando tokens de `index.css`. **Los bloques de marcas (`.seccion--marcas`, `.marcas-nosotros*`) son código muerto tras la eliminación de esa sección y se eliminan en T13.** | RF-1, RF-2.2–2.3, RF-5, RF-8, RF-9, RF-10.3, RNF-1, RNF-2, RNF-6, RNF-7 |
| `frontend/src/components/nosotros/HeroNosotros.tsx` | Sección 1: hero oscuro con imagen existente `hydroemcol-nosotros.png`, velo/sombra oscura, texto central, `h1` único y CTA WhatsApp. Imagen decorativa (`alt=""`, `aria-hidden`). | RF-1.1, RF-2, RF-7.1, RNF-3, RNF-4, RNF-6 |
| `frontend/src/components/nosotros/BloqueQuienesSomos.tsx` | Sección 2: párrafo breve de presentación, con `SeccionEncabezado`. | RF-1.1, RF-3 |
| `frontend/src/components/nosotros/BloqueIdentidad.tsx` | Sección 3: misión, visión y valores en tres bloques escaneables + cita de Brad Henry diferenciada. | RF-1.1, RF-4 |
| `frontend/src/components/nosotros/BloqueCapacidades.tsx` | Sección 4: capacidades técnicas reutilizando `CAPACIDADES_TECNICAS` de `components/inicio/contenido.ts` en **filas editoriales con icono lateral** (icono + título + descripción, separadores sutiles, sin tarjetas), con `useAparecerAlEntrar`. | RF-1.1, RF-5 |
| `frontend/src/components/nosotros/BloqueUbicacion.tsx` | Sección 5: bloque de dirección (Calle 6 # 27b-55) + iframe de Google Maps con `title` accesible + enlace alternativo a Google Maps en pestaña nueva. | RF-1.1, RF-10, RNF-5 |
| `frontend/src/components/nosotros/CTANosotros.tsx` | Sección 6: CTA final con WhatsApp (`config/sitio.ts`) como principal y `/solicitar` como secundaria. | RF-1.1, RF-7, RNF-5 |

Nota de reconciliación: `frontend/src/components/nosotros/BloqueMarcas.tsx` **no forma parte
del diseño aprobado** (la sección de marcas fue eliminada por decisión de diseño del usuario,
18/10/2026; RF-6). El archivo existe en el repo como código huérfano (nada lo importa) y se
**elimina en T13** junto con su CSS muerto; RF-6/D-P9 quedan sin efecto.

### 2.2 Archivos editados

| Archivo | Acción | Responsabilidad | RF/RNF |
|---|---|---|---|
| `frontend/src/pages/Nosotros.tsx` | Reescribir | Ensamblar las seis secciones en el orden de RF-1.1, con un solo `h1` proveniente del hero; importar `nosotros.css`. | RF-1.1–1.3, RNF-3 |
| `frontend/src/config/sitio.ts` | Editar (añadir, sin romper lo existente) | Añadir la dirección "Calle 6 # 27b-55" y la URL de embed de Google Maps siguiendo el patrón del archivo; el resto de exportaciones (WhatsApp, llamada) queda intacto. | RF-10, RF-7.1 |

### 2.3 Archivos que NO se tocan

`frontend/src/router.tsx` (la ruta ya monta `Nosotros`), `frontend/src/components/Layout.tsx`,
`frontend/src/components/inicio/*` (solo se importan, no se modifican),
`frontend/src/index.css` (los tokens ya existen), todo el backend.
`frontend/src/config/sitio.ts` **sí se edita** para añadir dirección y embed del mapa (ver
2.2), sin modificar las exportaciones existentes.

## 3. Interfaces y datos

Tipos en `components/nosotros/contenido.ts`:

```ts
export interface BloqueIdentidad { titulo: string; texto: string }
export interface ImagenHero { src: string; alt: string }
```

Contenido previsto:

```ts
export const MENSAJE_HERO_NOSOTROS: string   // PROVISIONAL hasta validar (RF-11.1)
export const TEXTO_QUIENES_SOMOS: string      // PROVISIONAL hasta validar (RF-3, D-2)
export const IDENTIDAD: BloqueIdentidad[]     // Misión, Visión, Valores (folio, versión sitio)
export const CITA_BRAD_HENRY: { texto: string; autor: string }
export const HERO_NOSOTROS: ImagenHero        // hydroemcol-nosotros.png (D-5)
```

Reutilizaciones (import, no copia):

```ts
import { SeccionEncabezado } from '../inicio/SeccionEncabezado'
import { CAPACIDADES_TECNICAS } from '../inicio/contenido'
import { urlWhatsApp, urlLlamada, direccion, urlMapaEmbed, urlMapa } from '../../config/sitio'
import { useAparecerAlEntrar } from '../../hooks/useAparecerAlEntrar'
```

`ListaMarcas` y `MARCAS` **ya no se importan**: la sección de marcas fue eliminada (RF-6;
reconciliación post-diseño externo, 18/10/2026).

En `frontend/src/config/sitio.ts` se añaden (siguiendo su patrón existente) la dirección
`Calle 6 # 27b-55`, la URL de embed de Google Maps para el iframe y la URL de Google Maps
para el enlace alternativo.

Decisión: la cita de Brad Henry y la misión/visión/valores se transcriben en
`contenido.ts` desde `specs/003-pagina-inicio/contenido-folleto.md` (versión para el sitio),
ya que `components/inicio/contenido.ts` no los contiene (spec 003 los reservó para Nosotros).

## 4. Decisiones del plan (con alternativa descartada)

- **D-P1. Carpeta propia `components/nosotros/` en vez de ampliar `components/inicio/`.**
  Descartado lo segundo: violaría la separación por página ya establecida y haría crecer
  innecesariamente un módulo con el alcance de otra spec.
- **D-P2. Reutilizar `SeccionEncabezado` importándolo de Inicio, no duplicarlo.** Descartado
  duplicar: dos copias del mismo comportamiento se
  desincronizan (mismo criterio que `reglas.py` en backend). *(Parcialmente sin efecto: la
  reutilización de `ListaMarcas` prevista aquí queda sin efecto porque la sección de marcas fue
  eliminada, RF-6.)* El bloque de pasos de Inicio **no
  se importa** en esta vista: la sección de proceso se eliminó por decisión del usuario (D-7).
  Si en el futuro se extraen a una carpeta compartida, será un refactor aparte.
- **D-P3. Hero con `<img>` + velo, mismo patrón que `Hero.tsx` de Inicio, sin librería.**
  Descartado CSS `background-image` solo: con `<img>` se controla `alt`/`aria-hidden` y el
  fallback de RF-2.3 es verificable. Descartado GSAP/Lottie del moodboard: dependencias nuevas
  (constitución, principio 1) y `useAparecerAlEntrar` ya cubre la línea visual.
- **D-P4. Datos separados en `contenido.ts` propio con marcas PROVISIONALES.** Descartado
  meter los textos directamente en los `.tsx`: RF-11.1 exige marcar lo provisional y así se
  cambia en un solo sitio.
- **D-P5. CTA final propio (`CTANosotros`) en vez de reutilizar `CTASection` de Inicio.**
  Descartado reutilizar: `CTASection` trae tres acciones fijas (solicitar, seguimiento,
  contacto) que contradicen D-4; el patrón y los estilos se replican mínimamente sobre los
  mismos tokens. Alternativa descartada: modificar `CTASection` con props extra — tocaría
  una spec ajena (003) sin necesidad.
- **D-P6. Bloque de ubicación propio (`BloqueUbicacion`) con mapa embebido y dirección
  aprobada (D-6).** Descartado omitir el mapa: la dirección "Calle 6 # 27b-55" está aprobada
  y la spec 003 reservó la ubicación para esta vista. Descartado usar solo un enlace a
  Google Maps sin iframe: se pidió el mapa embebido accesible con `title` y enlace
  alternativo.
- **D-P7. Sin dependencias nuevas, sin tests automáticos.** El frontend no tiene runner de
  tests (MEMORY.md) y la constitución exige preguntar antes de añadir cualquiera.
- **D-P8. Capacidades en filas editoriales con icono lateral, no en tarjetas como Inicio.**
  Descartado replicar las tarjetas de Inicio: la decisión D-3 aprobada pide un formato
  editorial (icono + título + descripción con separadores sutiles) que diferencia la página
  sin duplicar el estilo de Inicio. Los datos siguen siendo `CAPACIDADES_TECNICAS`.
- **D-P9. Respaldo de logos (RF-6.2, opción aprobada c) dentro del nuevo `BloqueMarcas`, sin
  tocar `components/inicio/`. — SIN EFECTO: sección de marcas eliminada** (decisión de diseño
  del usuario, 18/10/2026; RF-6). La página no muestra marcas, no se crea `BloqueMarcas` en el
  diseño aprobado y el archivo huérfano se elimina en T13. Se conserva solo como constancia:
  de haberse aplicado, habría descartado modificar `ListaMarcas.tsx` o cualquier componente
  de Inicio (lo prohíben RF-6.2 y la fuera de alcance); Inicio queda intacto.

## 5. Estrategia de verificación

No hay framework de tests frontend y no se instala ninguno. Verificación en este orden:

1. `npx tsc --noEmit` en `frontend/` → sin errores de tipos, imports ni rutas.
2. `npm run build` y `npm run lint` en `frontend/` → sin errores ni warnings nuevos.
3. Verificación visual con MCP de Chrome DevTools sobre `/nosotros`:
   - Viewports 320, 375, 768 y 1024 px o más: orden de las seis secciones (sin sección de
     proceso y sin sección de marcas), sin overflow horizontal, textos desde 16 px, targets
     desde 44×44 px.
   - Un solo `h1`; encabezados de sección visibles sin saltos de nivel.
   - Hero: imagen `hydroemcol-nosotros.png` con velo oscuro, mensaje legible (contraste),
     fallback si se bloquea la imagen.
   - Marcas: no hay bloque de marcas en la página (sección eliminada); verificar con grep que
     no queda código muerto de marcas (`BloqueMarcas.tsx` y `.seccion--marcas` /
     `.marcas-nosotros*` de `nosotros.css` eliminados en T13) sin tocar `components/inicio/`.
   - Reducir movimiento: secciones estáticas.
   - Teclado: recorrido completo con foco visible; CTA de WhatsApp con aviso de pestaña nueva.
   - Mapa: iframe con `title`, dirección "Calle 6 # 27b-55" visible, enlace alternativo a
     Google Maps y comportamiento responsive sin overflow.
4. Si el MCP de Chrome DevTools no está disponible, se documenta la limitación (precedente en
   MEMORY.md) y build + lint siguen siendo obligatorios; no se declara validación visual que
   no se haya hecho.

## 6. Matriz de cobertura

| Parte | Cobertura principal |
|---|---|
| `Nosotros.tsx` | RF-1, RNF-3 |
| `HeroNosotros.tsx` + estilos hero | RF-2, RF-7.1, RNF-4, RNF-6 |
| `BloqueQuienesSomos.tsx` + `contenido.ts` | RF-3, RF-11 |
| `BloqueIdentidad.tsx` | RF-4 |
| `BloqueCapacidades.tsx` (filas editoriales) | RF-5 |
| `BloqueUbicacion.tsx` + `config/sitio.ts` (edición) | RF-10, RNF-5 |
| `CTANosotros.tsx` + `config/sitio.ts` (import) | RF-7, RNF-5 |
| `nosotros.css` | RF-8, RF-9, RNF-1, RNF-2, RNF-7 |
| Todo el conjunto | RNF-9, RNF-10, RNF-11 |

## 7. Riesgos

- **R1 — Párrafo de "Quiénes somos" aún PROVISIONAL (D-2 aprobada con texto literal):** el
  texto está fijado en RF-3.1 pero debe conservarse la marca PROVISIONAL en `contenido.ts`
  hasta la validación final (RF-11.1); no ampliarlo ni reescribirlo.
- **R2 — Edición de `config/sitio.ts`:** añadir dirección y embed sin romper las exportaciones
  existentes (`urlWhatsApp`, `urlLlamada`) de las que dependen Inicio y el CTA. Mitigación:
  solo adiciones, verificación con `tsc --noEmit` y revisión de importadores.
- **R3 — Mapa embebido de terceros:** el iframe de Google Maps puede estar bloqueado, tardar o
  no ser navegable con teclado. Mitigación: `title` accesible, enlace alternativo a Google Maps
  visible y dirección en texto siempre presente (RF-10.1–10.3).
- **R4 — CSS duplicado** respecto de `inicio.css`. Mitigación: reutilizar clases globales
  existentes (`.seccion`, `.revelar`, `.sr-only`) y solo añadir reglas propias en
  `nosotros.css`.
- **R5 — Formato de capacidades:** el estilo editorial con icono lateral (D-P8) no debe
  convertirse en tarjetas de Inicio. Mitigación: reglas propias en `nosotros.css` con
  separadores sutiles y los datos de `CAPACIDADES_TECNICAS` sin copia local.
- **R6 — Reintroducción inadvertida de la sección de proceso o de la sección de marcas:** como
  Inicio sí tiene pasos y sí tiene marcas, existe el riesgo de copiarlos por inercia al
  ensamblar la página. Mitigación: RF-1.2 y el criterio 1 de la spec exigen exactamente 6
  secciones sin proceso y sin marcas; la verificación visual cuenta las secciones de RF-1.1 y
  T13 verifica que no queda código muerto de marcas.
- **R7 — Código muerto de marcas reintroduciéndose o quedando sin eliminar:** el componente
  `BloqueMarcas.tsx` y su CSS siguen existiendo en el repo pese a que la sección fue eliminada
  (RF-6). Mitigación: T13 los elimina y verifica con `tsc`, build, lint y revisión MCP que no
  queda resto de la sección; `components/inicio/*` solo se importa, nunca se modifica.
