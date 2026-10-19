# Tareas — specs/009-vista-nosotros

Derivadas de `spec.md` (fuente de verdad) y `plan.md`. Las decisiones D-1 a D-7 están
aprobadas (hero oscuro con `hydroemcol-nosotros.png`, párrafo literal PROVISIONAL, cita de
Brad Henry, capacidades en filas editoriales con icono, CTA WhatsApp, mapa Calle 6 # 27b-55,
orden de 6 secciones, sin sección de proceso ni sección de marcas — esta última eliminada por
decisión de diseño del usuario el 18/10/2026, ver RF-6 y T13). Sin dependencias nuevas y sin
tests automáticos
(el frontend no tiene
runner); verificación con `tsc --noEmit`, build, lint y MCP de Chrome DevTools.

- [x] **T1. Leer fuentes y contexto.** Archivos: `specs/009-vista-nosotros/spec.md`,
  `specs/009-vista-nosotros/plan.md`, `specs/003-pagina-inicio/contenido-folleto.md`,
  `frontend/src/pages/Nosotros.tsx`, `frontend/src/pages/Inicio.tsx`,
  `frontend/src/components/inicio/{contenido.ts,SeccionEncabezado.tsx,ListaMarcas.tsx,Hero.tsx,CTASection.tsx}`,
  `frontend/src/config/sitio.ts`, `frontend/src/index.css`,
  `frontend/src/components/inicio/inicio.css`. RF-11.
  - Hecho cuando: se conoce el orden de RF-1.1, el texto literal de misión/visión/valores/cita
    del folleto, las props de los componentes reutilizados y los tokens disponibles, sin
    escribir aún ningún archivo.

- [x] **T2. Contenido estático de la página.** Archivo nuevo:
  `frontend/src/components/nosotros/contenido.ts`. RF-3, RF-4, RF-5, RF-11.
  - Hecho cuando: exporta `MENSAJE_HERO_NOSOTROS`, `TEXTO_QUIENES_SOMOS` (marcado
    PROVISIONAL), `IDENTIDAD` con Misión/Visión/Valores literales del folleto,
    `CITA_BRAD_HENRY` y `HERO_NOSOTROS` con la imagen existente `hydroemcol-nosotros.png` de
    `public/img/` (NO la del banco de pruebas; errata corregida: es PNG, no JPG) y `alt`
    significativo; ningún texto afirma
    datos no contenidos en el folleto.

- [x] **T3. Estilos base de Nosotros.** Archivo nuevo:
  `frontend/src/components/nosotros/nosotros.css`. RF-2.2, RF-8, RF-9, RNF-1, RNF-2, RNF-6,
  RNF-7.
  - Hecho cuando: reutiliza los tokens de `index.css` y las clases globales `.seccion` y
    `.revelar` sin redefinir colores de marca, define el hero oscuro con velo legible, tiene
    base mobile-first sin overflow horizontal y las animaciones quedan anuladas bajo
    `prefers-reduced-motion: reduce`.

- [x] **T4. Hero de la página.** Archivo nuevo:
  `frontend/src/components/nosotros/HeroNosotros.tsx`. RF-1.1, RF-2, RNF-3, RNF-4.
  - Hecho cuando: muestra la imagen existente con velo y `alt=""`/`aria-hidden`, contiene el
    único `h1` de la página, el CTA definido en T7 y conserva fondo oscuro y mensaje legible
    si la imagen no carga.

- [x] **T5. Quiénes somos e identidad.** Archivos nuevos:
  `frontend/src/components/nosotros/BloqueQuienesSomos.tsx`,
  `frontend/src/components/nosotros/BloqueIdentidad.tsx`. RF-1.1, RF-3, RF-4, RNF-10.
  - Hecho cuando: el primero muestra el párrafo provisional con `SeccionEncabezado`; el
    segundo presenta Misión, Visión y Valores en tres bloques escaneables con la cita de Brad
    Henry diferenciada, textos literales del folleto, ambos con `useAparecerAlEntrar`.

- [x] **T6. Capacidades y marcas.** Archivos nuevos:
  `frontend/src/components/nosotros/BloqueCapacidades.tsx`,
  `frontend/src/components/nosotros/BloqueMarcas.tsx`. RF-1.1, RF-5, RF-6, RNF-8.
  - Hecho cuando: las capacidades se renderizan desde `CAPACIDADES_TECNICAS` reimportado de
    `components/inicio/contenido.ts` (sin copia local) en formato de filas editoriales con
    icono lateral (icono + título + descripción, separadores sutiles, sin tarjetas como en
    Inicio); y las marcas usan `ListaMarcas` con
    `MARCAS` existentes, con el **respaldo textual si un logo falla implementado dentro de
    `BloqueMarcas.tsx` (CSS/JS propio), sin modificar `components/inicio/ListaMarcas.tsx` ni
    ningún componente de Inicio**. No se crea ningún componente de proceso ni se reutiliza el
    bloque de pasos de Inicio (sección eliminada, D-7).
  - **Nota de reconciliación (18/10/2026):** la sección de marcas fue eliminada del diseño
    aprobado (RF-6 ELIMINADA). `BloqueMarcas.tsx` quedó huérfano y su CSS quedó muerto: se
    eliminan en T13. La parte de capacidades sigue vigente y verificada.

- [x] **T7. CTA final.** Archivo nuevo:
  `frontend/src/components/nosotros/CTANosotros.tsx`. RF-1.1, RF-7, RNF-5.
  - Hecho cuando: el principal es WhatsApp derivado de `urlWhatsApp()` sin duplicar el número,
    abre en pestaña nueva con `rel="noopener noreferrer"` y aviso `sr-only`, la solicitud de
    servicio (`/solicitar`) es acción secundaria con jerarquía diferenciada, y todo es
    operable con teclado con foco visible.

- [x] **T8. Ensamblar la página.** Archivo: `frontend/src/pages/Nosotros.tsx`. RF-1.1–1.3,
  RNF-3.
  - Hecho cuando: compone exactamente las **6 secciones** en el orden de RF-1.1 (hero,
    quiénes somos, identidad, capacidades, ubicación/mapa, CTA final), sin sección de
    proceso ni pasos y sin sección de marcas (eliminada por decisión de diseño del usuario,
    18/10/2026), importa `nosotros.css`, mantiene un solo `h1` (del hero), no añade
    secciones extra e
    incluye la sección de ubicación con mapa y dirección (RF-10).
  - **Nota de reconciliación:** el diseño externo aprobado dejó la página con 6 secciones; el
    comentario obsoleto de `Nosotros.tsx` que aún decía "7 secciones" se corrige en T13 sin
    tocar el diseño.

- [x] **T9. Verificación de tipos, build e imports.** Archivos: todo el frontend afectado.
  RF-1.1, RNF-9, RNF-10, RNF-11.
  - Hecho cuando: `npx tsc --noEmit`, `npm run build` y `npm run lint` en `frontend/` terminan
    sin errores ni warnings nuevos, la ruta `/nosotros` renderiza sin errores de consola y
    `router.tsx`, `Layout.tsx` y `components/inicio/` no fueron modificados.

- [x] **T10. Revisión visual responsive y accesible.** Archivos:
  `frontend/src/components/nosotros/nosotros.css` y componentes afectados. RNF-1–8, RF-2.3,
  RF-9.2, RF-10.3.
  - Hecho cuando: MCP de Chrome DevTools verifica `/nosotros` a 320, 375, 768 y 1024 px sin
    overflow, textos desde 16 px y targets desde 44×44 px, **exactamente 6 secciones en el
    orden de RF-1.1, sin sección de proceso/pasos y sin sección de marcas** (esta última
    eliminada por decisión de diseño, RF-6; el chequeo de logos/RF-6.2 quedó sin efecto),
    un solo `h1`, contraste del hero,
    foco visible en teclado, secciones estáticas con reducir movimiento, fallback de imagen de
    hero; y verifica el mapa: iframe con `title`, enlace alternativo a Google Maps,
    dirección "Calle 6 # 27b-55" correcta y comportamiento responsive sin overflow; si el MCP
    no está disponible, queda documentado sin declarar validación visual.

- [x] **T11. Bloque de ubicación y datos en config.** Archivos nuevo:
  `frontend/src/components/nosotros/BloqueUbicacion.tsx`; editado:
  `frontend/src/config/sitio.ts`. RF-1.1, RF-10.
  - Hecho cuando: `config/sitio.ts` exporta la dirección "Calle 6 # 27b-55" y la URL de embed
    de Google Maps (patrón del archivo, sin romper `urlWhatsApp`/`urlLlamada`) y
    `BloqueUbicacion.tsx` renderiza el bloque de dirección + el mapa embebido (iframe con
    `title` accesible) + el enlace alternativo a Google Maps en pestaña nueva con aviso
    `sr-only`.

- [x] **T12. Párrafo provisional y validación de contenido final.** Archivos:
  `frontend/src/components/nosotros/contenido.ts` y `spec.md` (contraste). RF-3.1, RF-11.
  - Hecho cuando: `TEXTO_QUIENES_SOMOS` en `contenido.ts` coincide literalmente con el
    párrafo de RF-3.1 de la spec, está marcado PROVISIONAL, y la revisión final confirma que
    no hay datos inventados (sin cifras, fechas ni certificaciones no aprobadas).

- [ ] **T13. Reconciliación post-diseño externo (código muerto de marcas).** Archivos:
  `frontend/src/pages/Nosotros.tsx` (solo comentario), `frontend/src/components/nosotros/BloqueMarcas.tsx`
  (eliminar), `frontend/src/components/nosotros/nosotros.css` (solo bloques de marcas).
  RF-6 (ELIMINADA), RF-1.1, RF-1.2, criterio 5.
  - (i) Corregir el comentario obsoleto de `Nosotros.tsx` ("7 secciones" → 6 secciones, con el
    orden actual) **sin tocar su diseño**.
  - (ii) Eliminar `frontend/src/components/nosotros/BloqueMarcas.tsx` y el CSS huérfano de
    marcas en `nosotros.css` (`.seccion--marcas`, `.marcas-nosotros*` y sus bloques `@media`;
    NO tocar ningún otro estilo).
  - (iii) Verificar `npx tsc --noEmit`, `npm run build` y `npm run lint` en `frontend/` sin
    errores.
  - (iv) Revisión MCP en `/nosotros`: 6 secciones, sin overflow, consola limpia.
  - Hecho cuando: todo verificado y sin código muerto (grep confirma que no quedan
    `BloqueMarcas`, `.seccion--marcas` ni `.marcas-nosotros` en `frontend/src`).

## Nota de división

- **Entrega A — lectura y cimiento:** T1–T3.
- **Entrega B — secciones:** T4–T7.
- **Entrega C — integración y validación:** T8–T12.
- **Entrega D — reconciliación post-diseño externo:** T13.
