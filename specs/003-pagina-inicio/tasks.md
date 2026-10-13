# Tareas — specs/003-pagina-inicio

Derivadas de `spec.md` (fuente de verdad) y `plan.md`. No se marcan tareas como completadas en
esta fase. La verificación usa `npm run build`, `npm run lint` y MCP de Chrome DevTools; no se
añaden dependencias ni framework de tests.

- [ ] **T1. Tokens y estilos base de Inicio.** Archivos: `frontend/src/index.css`, `frontend/src/components/inicio/inicio.css`. RF-8.1, RF-8.2, RNF-1, RNF-7, RNF-13.
  - Hecho cuando: `--color-primary` es `#2E3192`, `--color-accent` es `#ffc908`, los estilos de Inicio reutilizan los tokens y existe base responsive sin overflow horizontal.
- [ ] **T2. Rehacer marca compartida.** Archivos: `frontend/src/components/brand/Logo.tsx`, `frontend/src/components/brand/marca.css`, `frontend/src/components/brand/Tuerca.tsx`. RF-2.2, RF-8.3, RNF-5, RNF-10.
  - Hecho cuando: `Logo.tsx` ya no importa `Tuerca`, usa los recursos reales, conserva sus props públicas, contempla fondo oscuro, `Tuerca.tsx` no existe y el build no tiene imports rotos.
- [ ] **T3. Configuración de contacto y pie.** Archivos: `frontend/src/config/sitio.ts`, `frontend/src/components/Layout.tsx`. RF-9.1–9.4, RF-10.1–10.3.
  - Hecho cuando: el número y las URLs derivadas viven en un único módulo, los datos temporales están marcados, y el pie muestra únicamente el enlace Facebook configurado con `target` y `rel` seguros sin alterar el encabezado.
- [ ] **T4. Datos estáticos y separación de imágenes.** Archivo: `frontend/src/components/inicio/contenido.ts`. RF-2.4–2.6, RF-4.1–4.4, RF-5.1–5.5, RF-6.1–6.4, RF-11.1–11.4, RNF-5, RNF-15.
  - Hecho cuando: se conservan los tipos y colecciones aprobados, `IMAGENES_FOLLETO` mantiene los `alt` confirmados de las cinco imágenes, los tres productos quedan identificables para el carrusel y las dos imágenes reservadas no quedan en ninguna colección que Inicio renderice.
- [ ] **T5. Componentes base de secciones y tarjetas.** Archivos: `frontend/src/components/inicio/SeccionEncabezado.tsx`, `frontend/src/components/inicio/TarjetaServicio.tsx`. RF-1.3, RF-2.4–2.6, RF-3, RF-4.1–4.2, RNF-3, RNF-4, RNF-6, RNF-8.
  - Hecho cuando: el encabezado soporta nivel e `id`, la tarjeta acepta las props previstas, el hero la usa como contenido informativo sin `to`, y los estados de animación, puntero, pulsación y foco no ocultan texto.
- [ ] **T6. Crear `CarruselProductos`.** Archivo: `frontend/src/components/inicio/CarruselProductos.tsx`; estilos en `frontend/src/components/inicio/inicio.css`. RF-4.5–4.8, RF-11.2, RF-11.4, RNF-2, RNF-5–6, RNF-8, RNF-10–11, RNF-14–15.
  - Hecho cuando: el componente recibe `ImagenFolleto[]`, mantiene internamente el índice activo, muestra una imagen a la vez, ofrece botones anterior/siguiente visibles con `aria-label` en español y targets/foco de al menos 44×44 px, permite teclado, anuncia el cambio de forma prudente, conserva el `alt` recibido, desactiva transición con reducir movimiento y muestra fallback sin overflow si falla la imagen.
- [ ] **T7. Implementar `Hero` sin logo grande.** Archivo: `frontend/src/components/inicio/Hero.tsx`. RF-1.1, RF-2.1–2.7, RF-3.1–3.4, RNF-4, RNF-8.
  - Hecho cuando: `Hero` no importa ni renderiza `Logo`, conserva el h1 provisional, el CTA hacia `/solicitar`, exactamente tres tarjetas con los textos aprobados, y con reducir movimiento las tarjetas aparecen completas y estáticas.
- [ ] **T8. Integrar servicios destacados y carrusel específico.** Archivo: `frontend/src/components/inicio/BloqueServiciosDestacados.tsx`. RF-1.1, RF-4.1–4.8, RF-5.11, RF-11.4.
  - Hecho cuando: se muestran los cuatro servicios en orden estable, sin enlaces, y solo el bloque titulado `Importación Sobre Pedido` contiene una instancia de `CarruselProductos` con `productos-1.jpeg`, `productos-2.jpeg` y `productos-3.jpeg`; no se crea una sexta sección ni una galería genérica.
- [ ] **T9. Capacidad técnica, marcas y video.** Archivos: `frontend/src/components/inicio/BloqueCapacidadTecnica.tsx`, `frontend/src/components/inicio/ListaMarcas.tsx`, `frontend/src/components/inicio/BloqueVideo.tsx`. RF-1.1, RF-5.1–5.11, RF-11.2–11.4, RNF-8, RNF-10.
  - Hecho cuando: la sección muestra componentes, pruebas en banco, las 14 marcas como texto, el video con control visible y degradación segura, y no renderiza ninguna de las tres imágenes de productos.
- [ ] **T10. Implementar pasos y CTA.** Archivos: `frontend/src/components/inicio/BloquePasos.tsx`, `frontend/src/components/inicio/CTASection.tsx`. RF-1.1, RF-6.1–6.4, RF-7.1–7.5, RF-9.1, RF-9.3–9.4.
  - Hecho cuando: los cinco pasos se muestran numerados y en orden como contenido provisional, y la sección final ofrece solicitar, seguimiento y contacto, con WhatsApp y llamada derivadas del único punto de configuración.
- [ ] **T11. Ensamblar la página de inicio.** Archivo: `frontend/src/pages/Inicio.tsx`. RF-1.1–1.3, RNF-3–4.
  - Hecho cuando: compone exactamente las cinco secciones en el orden de la spec, mantiene un solo h1 en el hero y no agrega una sección de galería o contenido adicional.
- [ ] **T12. Verificación responsive y accesible.** Archivos: `frontend/src/components/inicio/inicio.css` y componentes de Inicio afectados. RNF-1–8, RNF-10–15.
  - Hecho cuando: la revisión a 320, 375, 768 y 1024 px o más no muestra overflow; los textos mantienen al menos 16 px; controles tienen targets >=44×44 px; el foco es visible; la jerarquía, contraste, `alt`, teclado, carrusel, fallback y reducir movimiento cumplen la spec.
- [ ] **T13. Verificación final de build, lint y MCP.** Archivos: todo el frontend afectado por esta spec. RNF-1, RNF-2, RNF-9, RNF-13.
  - Hecho cuando: `npm run build` y `npm run lint` terminan sin errores, y MCP de Chrome DevTools verifica orden de secciones, hero sin logo, carrusel con solo productos, video, estados de error, reducir movimiento, navegación por teclado y enlaces del CTA.

## Nota de división

Las tareas quedan agrupadas en tres entregas verificables:

- **Entrega A — cimiento y marca:** T1–T3.
- **Entrega B — datos, componentes y bloques:** T4–T10.
- **Entrega C — integración y validación:** T11–T13.
