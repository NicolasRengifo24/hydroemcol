# Tareas — specs/013-vitrina-productos

**Estado: implementación completada (2026-11-20).**
**Fuente de verdad:** `spec.md` y `plan.md` de esta misma carpeta. Estas tareas ejecutan el cambio
aprobado (Variante A): retirar únicamente la administración del carrusel. Cada tarea es pequeña y
verificable; este documento no contiene código.

## Reglas de ejecución

- Tests primero donde aplica: T1 ajusta la suite backend antes de tocar código de producción.
- Orden: backend (T1–T3) → frontend (T4–T7) → verificación y limpieza documental (T8).
- No se elimina `ImagenCarrusel`, su API pública ni `HeroProductos`. No se crea ninguna migración.
- No se añaden dependencias ni se usa `node --test`.
- No se inventan nombres, descripciones, textos alternativos, precios ni stock.
- Las siete imágenes iniciales ya están aprobadas, cargadas y visibles (spec §2): no hay tarea de
  aprobación editorial, seed ni fixtures.
- RF-VIT-16, RF-VIT-17, RF-VIT-18 y RF-VIT-21 no existen; no se renumeraliza ningún requisito.
- Si una tarea no puede completarse, se detiene y se reporta el bloqueo; no se adelanta otra.

---

## T1 — Retirar primero los tests de administración del carrusel

**Estado: completada (2026-11-20).** Retirados de `test_vitrina_admin.py` los bloques de tests del
carrusel administrativo y sus imports sin uso; el docstring ya no describe reglas de posiciones.
Conservados los tests de categorías, modelo de `Producto` y API administrativa de productos, en verde
antes de tocar código de producción.

**Objetivo:** dejar la suite backend reflejando el estado objetivo antes de eliminar producción.

**Archivos esperados:**
- `backend/servicios/tests/test_vitrina_admin.py`

**RF/RNF cubiertos:** RF-VIT-08, RF-VIT-15, RF-VIT-33, RF-VIT-35 (se conservan: modelo de
Producto, contrato legado y seguridad administrativa).

**Dependencias:** ninguna.

**Hecho cuando:**
- Desaparecen los bloques de tests del carrusel administrativo: los de modelo, los de reglas de
  posiciones y los de su API.
- Se retiran los imports que queden sin uso; se conservan los necesarios para categorías, `Producto`
  y sus pruebas.
- El docstring del módulo ya no describe reglas puras de posiciones del carrusel.
- Quedan los tests de categorías, modelo de `Producto` y API de productos, y la suite pasa en verde
  antes de tocar código de producción.

**Comandos de verificación:**
```bash
.\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios
```

**Aprobación adicional:** no.

---

## T2 — Retirar el ViewSet administrativo del carrusel y su ruta

**Estado: completada (2026-11-20).** Eliminados el ViewSet administrativo del carrusel y su registro
de ruta. Siguen intactos la vista pública, el ViewSet de productos, el guardado de imágenes y el
serializer público del carrusel. `manage.py check` y la suite de `servicios` pasan.

**Objetivo:** eliminar el endpoint CRUD del carrusel sin afectar la vista pública ni el CRUD de
productos.

**Archivos esperados:**
- `backend/servicios/views.py`
- `backend/servicios/urls.py`

**RF/RNF cubiertos:** RF-VIT-15, RF-VIT-33, RF-VIT-36.

**Dependencias:** T1.

**Hecho cuando:**
- No existe el ViewSet ni el bloque de API administrativa del carrusel.
- `urls.py` no registra ninguna ruta administrativa del carrusel.
- Siguen intactos la vista pública, el ViewSet de productos, el guardado de imágenes y el serializer
  público del carrusel; el sobre público mantiene su campo de solo lectura.
- Los imports de serializers y reglas exclusivos del carrusel desaparecen de `views.py` si no quedan
  usos.
- `manage.py check` y la suite de `servicios` pasan.

**Comandos de verificación:**
```bash
.\backend\.venv\Scripts\python.exe .\backend\manage.py check
.\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios
```

**Aprobación adicional:** no.

---

## T3 — Retirar el serializer administrativo y las reglas de posiciones

**Estado: completada (2026-11-20).** Eliminados el serializer administrativo del carrusel y las reglas
de límite, posiciones y reactivación. `vitrina_reglas.py` conserva únicamente `clave_publica_producto`.
No se editaron modelos ni migraciones; `makemigrations --check --dry-run` no detecta cambios.

**Objetivo:** cerrar la superficie backend sin tocar el modelo, las migraciones ni el serializer
público.

**Archivos esperados:**
- `backend/servicios/serializers.py`
- `backend/servicios/vitrina_reglas.py`

**RF/RNF cubiertos:** RF-VIT-03, RF-VIT-15, RF-VIT-32; RNF-VIT-01.

**Dependencias:** T1, T2.

**Hecho cuando:**
- No existe el serializer administrativo del carrusel; el módulo de reglas queda reducido a la
  función de clave opaca.
- `vitrina_reglas.py` conserva únicamente `clave_publica_producto`: desaparecen las constantes y
  funciones de límite, posiciones y reactivación, y su docstring describe solo la clave opaca.
- El serializer público del carrusel, su campo en la API y el catálogo de categorías siguen
  presentes.
- No se editan `models.py` ni `migrations/`; `makemigrations --check --dry-run` no detecta cambios.
- Los tests públicos siguen pasando y verifican que `carrusel` es de solo lectura.

**Comandos de verificación:**
```bash
.\backend\.venv\Scripts\python.exe .\backend\manage.py check
.\backend\.venv\Scripts\python.exe .\backend\manage.py makemigrations --check --dry-run
.\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios
```

**Aprobación adicional:** no.

---

## T4 — Retirar tipos y funciones administrativas del carrusel en `vitrina.ts`

**Estado: completada (2026-11-20).** Eliminados los tipos y las funciones de transporte del carrusel
administrativo y el tratamiento del campo `orden` en los helpers de formulario. Conservados el campo
público de carrusel de solo lectura, los tipos de producto y las cuatro operaciones de
`/api/admin/productos/` con `csrf: true`. `npm run build` y `npm run lint` pasan.

**Objetivo:** eliminar el transporte del carrusel administrativo conservando el contrato público y
el de productos.

**Archivos esperados:**
- `frontend/src/services/vitrina.ts`

**RF/RNF cubiertos:** RF-VIT-01, RF-VIT-15; RNF-VIT-05.

**Dependencias:** T3.

**Hecho cuando:**
- Desaparecen los tipos y las funciones de transporte del carrusel administrativo: listado,
  creación, actualización y eliminación.
- Los helpers de formulario ya no tratan el campo `orden` propio del carrusel.
- Se conserva el campo público de carrusel como contrato de solo lectura, todos los tipos de
  producto y las cuatro funciones de `/api/admin/productos/` con `csrf: true`.
- No queda ninguna ruta de administración del carrusel en el archivo.
- `npm run build` y `npm run lint` pasan.

**Comandos de verificación:**
```bash
cd frontend && npm run build && npm run lint
```

**Aprobación adicional:** no.

---

## T5 — Retirar hooks y clave de caché del carrusel

**Estado: completada (2026-11-20).** Retirados de `useAdministrativo.ts` los seis imports del
carrusel administrativo, su clave de caché, su línea de invalidación y los dos hooks del carrusel
(consulta y mutaciones). Siguen intactos `useProductosAdministrativos`, `useMutacionesProductos`, la
invalidación de productos y de la vitrina pública (`['vitrina']`) y todos los hooks de servicios.
`npm run build` pasó de 6 errores `TS2305` a correcto; `npm run lint` pasa con 2 advertencias
preexistentes en `HeroProductos.tsx` (archivo intacto). Se ajustó además el comentario del manejo de
409, que todavía describía reglas del carrusel ya retirado. No se tocó CSS admin, backend ni la spec
funcional.

**Objetivo:** limpiar React Query sin romper la invalidación de productos ni de la vitrina pública.

**Archivos esperados:**
- `frontend/src/hooks/useAdministrativo.ts`

**RF/RNF cubiertos:** RF-VIT-09, RF-VIT-10, RF-VIT-11, RF-VIT-12, RF-VIT-15, RF-VIT-34;
RNF-VIT-05.

**Dependencias:** T4.

**Hecho cuando:**
- Desaparecen los imports, la clave de caché, su línea de invalidación y los hooks del carrusel
  administrativo.
- La invalidación sigue cubriendo los productos administrativos y la vitrina pública.
- Se conservan todos los hooks de servicios y `useProductosAdministrativos` /
  `useMutacionesProductos`.
- `npm run build` y `npm run lint` pasan.

**Comandos de verificación:**
```bash
cd frontend && npm run build && npm run lint
```

**Aprobación adicional:** no.

---

## T6 — Retirar la página, la ruta y el menú del carrusel

**Estado: completada (2026-11-20).** Ejecutada antes que T5 por decisión del coordinador para
desbloquear TypeScript. Eliminada la página administrativa del carrusel; retirados de `router.tsx` el
import y la ruta `/carrusel`, y de `AdminLayout.tsx` el icono `Images` y el `NavLink` al carrusel. `npm run lint` pasa
con 2 advertencias preexistentes en `HeroProductos.tsx` (archivo intacto). `npm run build` queda en
rojo solo por 6 errores `TS2305` en `useAdministrativo.ts`, pendientes de T5 y no corregidos aquí.
No se realizó comprobación visual con MCP de Chrome DevTools: la herramienta no está disponible en
esta sesión (limitación documentada según plan §11.4).

**Objetivo:** que el panel ya no ofrezca ni alcance la administración del carrusel.

**Archivos esperados:**
- Página del carrusel del panel (eliminar el archivo)
- `frontend/src/router.tsx`
- `frontend/src/components/AdminLayout.tsx`

**RF/RNF cubiertos:** RF-VIT-15, RF-VIT-22; RNF-VIT-03, RNF-VIT-04, RNF-VIT-05.

**Dependencias:** T5.

**Hecho cuando:**
- La página del carrusel del panel ya no existe.
- El router no declara la ruta administrativa del carrusel.
- El menú del panel no muestra el icono ni el enlace del carrusel; quedan Resumen, Productos,
  Servicios e Indicadores.
- `HeroProductos.tsx`, `HeroProductos.css`, `heroProductos.ts`, `piezasHero.ts` y
  `CarruselVitrina.tsx` quedan intactos.
- `npm run build` y `npm run lint` pasan; en el panel no aparece “Carrusel” y la ruta antigua cae en
  la vista de no encontrada.

**Comandos de verificación:**
```bash
cd frontend && npm run build && npm run lint
```

**Aprobación adicional:** no.

---

## T7 — Retirar estilos huérfanos del panel de carrusel

**Estado: completada (2026-11-20).** Retiradas de `adminVitrina.css` las dos reglas de estilo huérfanas del carrusel administrativo. La búsqueda previa confirmó que cada una solo aparecía en su propia definición dentro del CSS, sin usos en `AdminProductos.tsx`, `AdminLayout.tsx`, `router.tsx` ni en ningún otro archivo del frontend, tras la eliminación de la página del carrusel en T6. Quedan intactas todas las reglas consumidas por el panel de productos, incluido el bloque `@media (max-width: 599px)`. `npm run build` pasa y `npm run lint` pasa con 2 advertencias preexistentes en `HeroProductos.tsx` (archivo intacto). No se realizó comprobación visual con MCP de Chrome DevTools: la herramienta no está disponible en esta sesión (limitación documentada según plan §11.4); además, las reglas retiradas no tenían consumidores, por lo que no había elementos renderizados que cambiaran. No se tocó backend, router, AdminLayout, AdminProductos, vitrina pública ni la spec funcional.

**Objetivo:** dejar `adminVitrina.css` solo con las reglas que consume `AdminProductos`.

**Archivos esperados:**
- `frontend/src/pages/adminVitrina.css`

**RF/RNF cubiertos:** RNF-VIT-03, RNF-VIT-04, RNF-VIT-05.

**Dependencias:** T6.

**Hecho cuando:**
- Se retiran las reglas de estilo del carrusel administrativo, verificadas sin usos residuales tras
  eliminar su página.
- Los estilos del panel de productos quedan intactos.
- `npm run build` y `npm run lint` pasan.

**Comandos de verificación:**
```bash
cd frontend && npm run build && npm run lint
```

**Aprobación adicional:** no.

---

## T8 — Verificación integral y limpieza documental

**Estado: completada (2026-11-20).** Cuatro comandos obligatorios en verde; búsqueda de referencias
residuales sin resultados en código ni en los tres archivos de la spec; API pública con 7 productos
visibles y campo `carrusel` de solo lectura; sin ruta administrativa de carrusel; `HeroProductos`
intacto y sin eventos de medición nuevos; sin migración, seed ni fixture. Verificación visual con MCP
no disponible en esta sesión (plan §11.4). Detalle en la bitácora de cierre al final de este archivo.

**Objetivo:** confirmar el estado objetivo y dejar los tres archivos de la spec coherentes con él.

**Archivos esperados:**
- `specs/013-vitrina-productos/spec.md`
- `specs/013-vitrina-productos/plan.md`
- `specs/013-vitrina-productos/tasks.md`
- Correcciones puntuales solo si la verificación descubre una referencia residual.

**RF/RNF cubiertos:** todos los vigentes, con foco en RF-VIT-14, RF-VIT-15, RF-VIT-19, RF-VIT-20,
RF-VIT-33 y RF-VIT-36.

**Dependencias:** T1–T7.

**Hecho cuando:**
- Pasan los cuatro comandos obligatorios.
- La búsqueda de referencias residuales del plan (§11.3) no devuelve resultados en código ni en los
  tres archivos de la spec.
- Siguen presentes el serializer público del carrusel, su campo en la API, `HeroProductos` y
  `clave_publica_producto`.
- No hay migración nueva, seed ni fixture; las siete imágenes siguen cargadas y visibles según
  spec §2.
- Comprobación manual: panel sin enlace ni ruta de carrusel; `/productos` muestra el carrusel
  editorial con cinco piezas, autoplay/pausa, teclado, gesto y `prefers-reduced-motion`, sin eventos
  de medición nuevos.
- La bitácora de `MEMORY.md` se actualizó al cerrar la implementación (2026-11-20).

**Comandos de verificación:**
```bash
.\backend\.venv\Scripts\python.exe .\backend\manage.py check
.\backend\.venv\Scripts\python.exe .\backend\manage.py makemigrations --check --dry-run
.\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios
cd frontend && npm run build && npm run lint
```

**Aprobación adicional:** no.

---

## Registro histórico

Las tareas T1–T10 de la implementación original de la vitrina se completaron entre 2026-11-09 y
2026-11-17. No se reproducen aquí: el cambio aprobado es el retiro de la administración del
carrusel y la documentación del carrusel editorial y de las siete imágenes ya cargadas.

---

## Bitácora de cierre (2026-11-20)

**Comandos obligatorios (raíz del repo, salvo el bloque frontend):**

- `.\backend\.venv\Scripts\python.exe .\backend\manage.py check` → `System check identified no issues (0 silenced).`
- `.\backend\.venv\Scripts\python.exe .\backend\manage.py makemigrations --check --dry-run` → `No changes detected`.
- `$env:R2_ENABLED='False'; .\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios` → `Ran 202 tests` / `OK` (74.022 s en la primera ejecución, 71.076 s en la reverificación final).
- `cd frontend; npm run build; npm run lint` → `✓ built` (3.92 s en la primera ejecución, 2.08 s en la reverificación final); `oxlint` termina con 2 advertencias
  preexistentes `react(preserve-manual-memoization)` en `HeroProductos.tsx` (archivo intacto), sin errores.
- Complementario, según decisión del plan D-P13: `node --test` → `1..0`, `# tests 0`, `# fail 0`.
  El repo no tiene runner JavaScript y no se añadió ninguno.

**Búsqueda de referencias residuales (§11.3):** búsqueda de identificadores de administración del
carrusel sin resultados; citas de RF eliminados (`RF-VIT-17`, `RF-VIT-18`, `RF-VIT-21`) en docstrings
y comentarios de código corregidas en la revisión posterior, por lo que solo permanecen en las
declaraciones históricas del hueco de `plan.md`, este `tasks.md` y `MEMORY.md`. Las menciones de las
tareas T5–T7 se reformularon como declaraciones de retiro sin reproducir los identificadores. Se
conservan `ImagenCarruselPublicoSerializer`, el campo `carrusel`, `HeroProductos` y
`clave_publica_producto`.

**Corrección puntual descubierta por la verificación:** `frontend/src/pages/AdminProductos.tsx`
todavía omitía en `erroresDeCampo` una clave de posiciones del carrusel; esa lista solo procesa
errores del formulario de productos. Se retiró la clave: no puede ser devuelta por la API de productos
y era un resto del contrato de errores del carrusel ya eliminado. Sin cambio de comportamiento para
Producto.

**Verificaciones adicionales:**

- `GET /api/productos/` → `200`, claves `categorias`, `categoria`, `carrusel`, `resultados`;
  `Cache-Control: no-store`; 7 resultados visibles con `imagen_referencia` registrada.
- `ImagenCarruselPublicoSerializer` expone solo `url` y `alt`, ambos de solo lectura; la vista pública
  es `APIView` con único método `get`.
- No resuelve ninguna de las antiguas rutas administrativas del carrusel, ni en la API ni en el
  panel: las cuatro rutas comprobadas devuelven `Resolver404`.
- `HeroProductos` sigue montado en `/productos`, con 5 piezas en `piezasHero.ts`, autoplay/pausa,
  teclado, gesto y `prefers-reduced-motion`, sin importar el módulo de medición.
- Medición sin cambios: solo `ViewContent` y `Contact`, sin eventos para el carrusel editorial.
- Sin migración nueva (la última sigue siendo `0010_producto_imagen_carrusel`), sin directorio
  `fixtures`, sin semillas ni scripts de carga; los 7 archivos de imagen aprobados siguen en
  `frontend/public/img/productos/`.

**Limitación:** no hubo comprobación visual con Chrome DevTools MCP (herramienta no disponible en
esta sesión); no se declara validación visual de los viewports del plan §11.4.
