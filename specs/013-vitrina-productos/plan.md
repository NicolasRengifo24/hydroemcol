# Plan — specs/013-vitrina-productos

**Estado: aprobado.**
**Fuente de verdad:** `specs/013-vitrina-productos/spec.md` (aprobada, actualización 2026-11-20).
Este plan no cambia requisitos: describe el estado objetivo y cómo alcanzarlo. La ejecución se
desglosa en `specs/013-vitrina-productos/tasks.md`.

## 0. Naturaleza del cambio

La vitrina ya está implementada. El cambio aprobado es acotado y se rige por la **Variante A**:

- **Se conserva** `HeroProductos` con sus cinco piezas estáticas (`piezasHero.ts`), su texto
  comercial, su CTA de WhatsApp, sus indicadores y su comportamiento de autoplay, transiciones,
  pausa por interacción/puntero/foco/pestaña oculta y `prefers-reduced-motion`.
- **Se conserva** el contrato público legado `ImagenCarrusel` / campo `carrusel`, de solo lectura.
  La página actual no lo renderiza.
- **Se elimina únicamente la administración del carrusel**: panel, ruta, menú, hooks, tipos,
  endpoints CRUD, serializer administrativo, tests administrativos y reglas de órdenes, posiciones
  libres, reactivación y límite.
- **No hay migración nueva.** No se borra el modelo `ImagenCarrusel`, sus campos ni sus
  restricciones ya aplicadas en `0010_producto_imagen_carrusel`.
- **No hay dependencias nuevas.** La vitrina conserva la administración de Producto, su API
  pública, `clave_publica_producto`, la medición, el SEO y el panel de productos.

Los huecos de numeración RF-VIT-16, RF-VIT-17, RF-VIT-18 y RF-VIT-21 son aceptados y **no se
renumeraliza** ningún otro requisito.

## 1. Arquitectura y autoridad (estado objetivo)

| Capa | Responsabilidad | No debe hacer |
|---|---|---|
| Modelo persistente (sin cambios) | Conservar `Producto` e `ImagenCarrusel`, campos, fechas, visibilidad y restricciones ya migradas. | Crear una migración, borrar entidades o cambiar relaciones. |
| `servicios/imagenes.py` | Validar MIME real, decodificar, redimensionar y comprimir imágenes de Producto. | Tocar la base de datos. |
| `servicios/almacenamiento.py` | Único punto que habla con `default_storage`; construir la URL pública o firmada. | Decidir visibilidad ni reglas de negocio. |
| Serializers y vista pública | Autorizar la forma, filtrar por `visible`, ordenar y publicar `carrusel` como solo lectura. | Exponer `id`, fechas ni campos internos. |
| API administrativa de productos | CRUD aprobado con autenticación, CSRF, validación y atomicidad. | Borrado definitivo; gestionar el carrusel. |
| Carrusel editorial (`HeroProductos`) | Mostrar cinco piezas estáticas del frontend con texto, CTA e indicadores. | Leer la API, la base de datos o el panel. |
| Contrato legado `carrusel` | Exponer imágenes visibles de `ImagenCarrusel` en la API pública. | Ser gestionado, reordenado ni renderizado por la página actual. |
| Panel | Formularios, previsualización, confirmaciones y errores del backend de Producto. | Ofrecer ruta, menú ni operación sobre el carrusel. |
| Medición y SEO | `ViewContent`, `Contact`, UTM, canonical y metadatos. | Enviar PII, precios, stock ni eventos del carrusel editorial. |

Patrón que se conserva: `models.py` → `serializers.py` → `views.py` → `urls.py` en backend, y
`services/` → `hooks/` → `pages/` / `components/` en frontend. Alternativa descartada: mover las
reglas de Producto a módulos nuevos por spec; rompería la organización por capas ya usada.

## 2. Inventario del cambio

### 2.1 Se retira (solo administración del carrusel)

La retirada afecta únicamente a la superficie administrativa del carrusel:

- **Backend:** el ViewSet y el registro de ruta de la API administrativa del carrusel; el serializer
  administrativo; las reglas de límite, posiciones y reactivación; y los tests que los cubrían.
- **Frontend:** la página del carrusel del panel, su ruta y su enlace de menú; los tipos y funciones
  de transporte administrativo; los hooks y la clave de caché; y las reglas de estilo que queden sin
  uso.

No se retira nada más: el carrusel editorial y el contrato público de solo lectura se conservan.

### 2.2 Se conserva sin cambios

- `ImagenCarrusel`, su migración y `backend/servicios/admin.py` (sin registro nuevo).
- `ImagenCarruselPublicoSerializer` y el campo `carrusel` de `/api/productos/`.
- `VitrinaPublicaView`, `ProductoAdminViewSet`, `_guardar_imagen_de_vitrina` y
  `_descartar_imagen_de_vitrina` (estos últimos siguen siendo usados por Producto).
- `clave_publica_producto`, `categorias_publicas` y los serializers públicos/administrativos de
  Producto.
- `HeroProductos.tsx`, `HeroProductos.css`, `heroProductos.ts`, `piezasHero.ts` y
  `CarruselVitrina.tsx`. `Productos.tsx` renderiza `HeroProductos`; `CarruselVitrina.tsx` permanece
  como archivo heredado sin uso y sin modificaciones.
- `AdminProductos.tsx`, el panel de productos, la API pública, la medición y el SEO.
- Las siete imágenes iniciales, ya cargadas y visibles según §2 de la spec.

## 3. Modelo persistente: decisión de no cambio

- La migración `0010_producto_imagen_carrusel` ya está aplicada. No se genera otra migración;
  `makemigrations --check --dry-run` debe seguir sin cambios.
- Las restricciones `carrusel_orden_entre_1_y_4` y `carrusel_orden_unico_visible` permanecen en la
  base de datos como patrimonio del modelo, pero ninguna regla de aplicación las invoca: no hay
  validación de posiciones, límite ni reactivación.
- `clave_publica_producto` sigue siendo la única función pura de `vitrina_reglas.py`.
- Alternativa descartada: eliminar `ImagenCarrusel` o sus columnas. Rompería el contrato público
  `carrusel`, exigiría una migración prohibida por la spec y por el principio 2 de la constitución.

## 4. Contratos de API (estado objetivo)

### 4.1 API pública — sin cambios

`GET /api/productos/` y `GET /api/productos/?categoria=<slug>`, `AllowAny`, sin paginación y con
`Cache-Control: no-store`. El sobre mantiene `categorias`, `categoria`, `carrusel` y `resultados`.

- `carrusel`: solo imágenes visibles de `ImagenCarrusel`, ordenadas por `orden`, con `url` y `alt`;
  sin `id`, `orden` ni `visible`. Es un contrato de solo lectura y la página no lo renderiza.
- `resultados`: solo `visible=True`, ordenados por `-fecha_creacion`, `-id`, sin `id`, fechas ni
  `visible`; `clave` opaca y estable.
- Categoría desconocida o repetida → `400` con el catálogo aprobado; sin filtro → `categoria: null`.
- Alternativa descartada: quitar el campo `carrusel` por no ser usado. La spec lo conserva como
  contrato legado y su serializer público sigue cubierto por tests.

### 4.2 API administrativa de productos — sin cambios

Prefijo `/api/admin/productos/`, permiso `EsAdministrativo` y `csrf_protect` en el `dispatch`.

| Método | Ruta | Cuerpo | Respuesta |
|---|---|---|---|
| `GET` | `/api/admin/productos/` | — | `{ "resultados": [ProductoAdmin...] }`, visibles y ocultos, `-fecha_creacion`, `-id`. |
| `POST` | `/api/admin/productos/` | `multipart/form-data` con `nombre`, `categoria`, `descripcion`, `visible`, `imagen`, `imagen_alt` | `201`. |
| `PATCH` | `/api/admin/productos/<id>/` | JSON o `multipart` si se reemplaza `imagen` | `200`. |
| `DELETE` | `/api/admin/productos/<id>/` | — | `204`; pone `visible=False` y conserva la fila. |

`nombre`, `categoria`, `descripcion`, `imagen` (en creación) y `imagen_alt` son obligatorios. Fechas
y referencias las fija el backend. Un fallo de validación no guarda archivo ni fila; un fallo de
almacenamiento responde `503` sin referencia residual.

### 4.3 API administrativa del carrusel — inexistente

No existe API administrativa del carrusel: ni ViewSet, ni serializer administrativo, ni reglas de
límite, posiciones o reactivación, ni tests de esa superficie. No se sustituye por una ruta oculta.

Alternativa descartada: conservar el ViewSet pero sin enlace en el menú. Dejaría un endpoint CRUD
accesible y reglas vivas, contradiciendo RF-VIT-15 y RF-VIT-33.

### 4.4 Seguridad y errores

- Autenticación, cuenta activa, rol `ADMINISTRATIVO` y CSRF se exigen en toda mutación de productos.
- `400`: validación de campos o categoría inválida. `401/403`: autenticación, rol o CSRF.
  `503`: fallo de almacenamiento. `500`: mensaje genérico, detalle solo en log.
- No hay `409` por límite o posición: ese código de conflicto desaparece con la administración del
  carrusel. El frontend sigue usando `mensajeDeError` para mostrar el mensaje del backend.
- No se registra auditoría ni usuario histórico (Opción A de la spec).

## 5. Secuencias

### 5.1 Carga o reemplazo de imagen de Producto

1. El serializer valida campos y `imagen_alt`.
2. `procesar_imagen` valida el MIME real y devuelve WEBP, sin tocar BD ni red.
3. `guardar_archivo` guarda bajo `vitrina/productos/`; un fallo responde `503`.
4. `transaction.atomic()` guarda la referencia y el resto de campos.
5. Si la BD falla después de subir, `eliminar_referencia(nueva)` y relanzar; la referencia anterior
   no se toca.
6. La publicación es inmediata: no hay caché de servidor que purgar.

### 5.2 Publicación y visibilidad

El backend filtra por `visible`, ordena y decide la publicación. El frontend consume `resultados` en
el orden recibido y pinta las categorías desde `categorias`; nunca oculta ni reordena por su cuenta.

### 5.3 Carrusel editorial (secuencia puramente frontend)

`Productos.tsx` monta `HeroProductos`, que lee `PIEZAS_HERO` de `piezasHero.ts` y el texto de
`heroProductos.ts`. Con 0 piezas no renderiza; con 1 muestra la pieza sin movimiento; con 2 o más
avanza con transición suave y se detiene ante interacción manual, puntero, foco, pestaña oculta o
`prefers-reduced-motion`. La navegación manual sigue disponible por teclado y gesto táctil. No hay
petición, mutación ni evento de medición en esta secuencia.

### 5.4 Orden del retiro (se corresponde con `tasks.md`)

1. Ajustar primero la suite backend: retirar los tests del carrusel administrativo y dejar en verde
   los tests de productos y del contrato público.
2. Retirar el ViewSet y la ruta; después el serializer administrativo y las reglas puras.
3. Retirar en frontend tipos/funciones, hooks/claves de caché, página/ruta/menú y estilos huérfanos.
4. Verificar con los comandos obligatorios y una búsqueda de referencias residuales.

Este orden evita dejar endpoints vivos sin interfaz y evita que el frontend rompa antes de que el
backend haya retirado su superficie.

## 6. Funciones puras y tratamiento de `hoy`

Backend:

| Función | Firma | Uso |
|---|---|---|
| `clave_publica_producto` | `clave_publica_producto(pk: int, secreto: str) -> str` | Clave opaca estable derivada de `pk`; la única función pura que queda en `vitrina_reglas.py`. |

Frontend:

| Función | Firma | Uso |
|---|---|---|
| `leerUtmDeUrl` | `leerUtmDeUrl(search: string) -> Utm` | Extrae solo las cinco claves UTM no vacías. |
| `fusionarUtm` | `fusionarUtm(previas: Utm, nuevas: Utm) -> Utm` | Conserva la primera atribución y completa claves ausentes. |
| `mensajeProducto` | `mensajeProducto(nombre: string) -> string` | Mensaje exacto aprobado en tarjetas (RF-VIT-23). |
| `parametrosContacto` | `parametrosContacto(producto, utm) -> Record<string, unknown>` | Parámetros no sensibles de `Contact`. |
| `parametrosViewContent` | `parametrosViewContent(utm) -> Record<string, unknown>` | URL canónica y UTM disponibles. |

Se retiran las reglas de posiciones y límite del carrusel: no tienen otro consumidor.

**Sobre `hoy`:** no existe ninguna función pura dependiente del reloj. Las fechas administrativas se
formatean como fechas absolutas con `Intl.DateTimeFormat('es-CO')`. Si en el futuro se mostrara
“hace X”, esa función debería recibir `hoy` como parámetro; no se introduce `new Date()` oculto en
reglas de negocio. Alternativa descartada: añadir esa función ahora (fuera de alcance y no
necesaria para la vitrina).

## 7. Interfaz

### 7.1 Página pública `/productos`

- `Productos.tsx` monta el carrusel editorial y la cuadrícula; lee `categoria` de `useSearchParams`
  y pinta filtros desde `categorias`.
- `HeroProductos` aporta las cinco piezas, el texto comercial, el CTA y los indicadores. Sus archivos
  no se tocan: el carrusel real ya existe y no depende del backend.
- `EstadoVitrina` cubre carga, error con reintento, vacío y filtro inválido. La cuadrícula respeta el
  orden del backend y es 1/2/3 columnas sin desplazamiento horizontal propio.
- `TarjetaProducto` y `BotonWhatsAppProducto` usan el mensaje aprobado, el número central y un aviso
  que no afirma envío. Sin precio, stock ni disponibilidad.
- `Seo` mantiene canonical `/productos`, `noindex` con `categoria`, Open Graph y sitemap.

### 7.2 Panel

- Solo `/control-operativo/productos` → `AdminProductos.tsx`: lista, formulario con imagen,
  previsualización, ocultar/mostrar y “eliminar” recuperable con `AdminConfirmDialog`.
- La navegación administrativa conserva Resumen, Productos, Servicios e Indicadores. Desaparecen la
  entrada Carrusel, su icono y su ruta.
- Los estilos de `adminVitrina.css` que quedan son los usados por el panel de productos.

### 7.3 Medición

Sin cambios: `ViewContent` al montar `/productos` y `Contact` solo en el WhatsApp de un Producto,
con UTM de sesión y parámetros no sensibles. El carrusel editorial no emite eventos; su CTA no crea
uno nuevo. Alternativa descartada: medir la navegación del carrusel (prohibido por RNF-VIT-07).

## 8. Inventario de archivos (estado objetivo)

### 8.1 Backend modificados por el cambio

| Archivo | Acción | RF |
|---|---|---|
| `backend/servicios/tests/test_vitrina_admin.py` | Quitar los bloques de tests del carrusel administrativo y sus imports; conservar los de categorías, modelo Producto y API de productos. | RF-VIT-08, 15, 33, 35 |
| `backend/servicios/views.py` | Quitar el ViewSet y los imports de reglas exclusivos del carrusel; conservar la vista pública y el ViewSet de productos. | RF-VIT-15, 33, 36 |
| `backend/servicios/urls.py` | Quitar el registro de la ruta administrativa del carrusel. | RF-VIT-15, 36 |
| `backend/servicios/serializers.py` | Quitar el serializer administrativo del carrusel; conservar el público. | RF-VIT-15, 32 |
| `backend/servicios/vitrina_reglas.py` | Conservar solo `clave_publica_producto`. | RF-VIT-03; RNF-VIT-01 |

### 8.2 Frontend modificados o eliminados por el cambio

| Archivo | Acción | RF |
|---|---|---|
| Página del carrusel del panel | Eliminar el archivo completo. | RF-VIT-15, 33 |
| `frontend/src/router.tsx` | Quitar la ruta administrativa del carrusel. | RF-VIT-15, 22 |
| `frontend/src/components/AdminLayout.tsx` | Quitar el icono y el enlace del carrusel. | RF-VIT-15, 22 |
| `frontend/src/hooks/useAdministrativo.ts` | Quitar imports, clave de caché, invalidación y hooks del carrusel. | RF-VIT-09–12, 34 |
| `frontend/src/services/vitrina.ts` | Quitar tipos y funciones administrativas del carrusel; conservar el campo público de solo lectura. | RF-VIT-01, 15 |
| `frontend/src/pages/adminVitrina.css` | Quitar reglas huérfanas si no quedan usos. | RNF-VIT-03–05 |

### 8.3 Sin tocar

`HeroProductos.tsx`, `HeroProductos.css`, `heroProductos.ts`, `piezasHero.ts`, `CarruselVitrina.tsx`,
`Productos.tsx`, `AdminProductos.tsx`, `models.py`, `migrations/`, `imagenes.py`,
`almacenamiento.py`, `config/settings.py`, `requirements.txt` y la guía de Meta. No se escribe
código, test ni documentación fuera de `specs/013-vitrina-productos/` en esta fase de plan.

## 9. Matriz RF → implementación y verificación

| Parte | RF/RNF cubiertos | Verificación |
|---|---|---|
| Modelo y migración 0010 (sin cambios) | RF-VIT-08, 15, 35, 36; RNF-VIT-01, 09, 10 | Tests de modelo; `makemigrations --check --dry-run`. |
| `imagenes.py` + `almacenamiento.py` (sin cambios) | RF-VIT-13, 32; RNF-VIT-02 | `test_vitrina_imagenes.py`. |
| Vista pública `/api/productos/` | RF-VIT-01–07, 15; RNF-VIT-01 | `test_vitrina_publica.py`: visibles, orden, filtros, `carrusel` de solo lectura, sin `id`. |
| API administrativa de productos | RF-VIT-09–14, 33, 34, 36; RNF-VIT-06 | `ProductoAdminApiTest`: autorización, CSRF, CRUD, imagen, visibilidad. |
| Carrusel editorial `HeroProductos` | RF-VIT-19, 20, 32; RNF-VIT-03–05 | Revisión de archivos intactos; comprobación visual manual. |
| `AdminProductos.tsx` y `adminVitrina.css` | RF-VIT-09–13, 33–35; RNF-VIT-03–05 | `npm run build`, `npm run lint`, revisión del panel. |
| Router, `AdminLayout`, `useAdministrativo`, `vitrina.ts` | RF-VIT-15, 22, 34; RNF-VIT-05 | Búsqueda de referencias; build y lint. |
| Medición, SEO y navegación (sin cambios) | RF-VIT-22–32; RNF-VIT-07, 08 | Tests públicos, build, lint y revisión manual. |
| Siete imágenes iniciales | RF-VIT-14; RNF-VIT-02 | Tabla aprobada en spec §2; productos visibles con URL registrada. |

**Huecos de numeración:** RF-VIT-16, RF-VIT-17, RF-VIT-18 y RF-VIT-21 no existen. No se reasignan
sus números ni se renombra ningún requisito posterior.

## 10. Decisiones del plan (con alternativa descartada)

- **D-P1. Variante A: conservar `HeroProductos` y el campo `carrusel`.** Descartado conectar el hero
  al campo `carrusel` o a productos: crearía una dependencia del backend y administración editorial.
- **D-P2. El contrato legado sigue de solo lectura.** Descartado eliminar `ImagenCarrusel` y su
  serializer público: rompería la API pública y exigiría migración.
- **D-P3. No existe API administrativa del carrusel.** Descartado dejar el ViewSet sin menú: el
  endpoint CRUD y las reglas de posiciones seguirían vivos.
- **D-P4. Sin migración nueva.** Descartado borrar columnas o restricciones: cambiaría el modelo y
  violaría el principio 2 de la constitución.
- **D-P5. Tests primero, pero acotados.** Descartado reescribir la suite completa: se retira solo lo
  del carrusel administrativo para no perder cobertura de Producto y de la API pública.
- **D-P6. Backend antes que frontend.** Descartado retirar la interfaz primero: dejaría endpoints
  activos sin pantalla y una ventana de errores para el usuario.
- **D-P7. `clave` opaca derivada del `pk`.** Descartado exponer `id` (prohibido) y el índice
  (inestable como `key` y como identificador de `Contact`).
- **D-P8. Categoría inválida → `400` con catálogo.** Descartado devolver todos o una lista vacía:
  confundiría “sin resultados” con “filtro inválido”.
- **D-P9. Conservar validación de imagen y Pillow para Producto.** Descartado relajar el MIME real
  o el tamaño: incumpliría RF-VIT-13 y RNF-VIT-02.
- **D-P10. URL pública configurable con fallback firmado.** Descartado guardar URLs absolutas en la
  BD: acopla los datos al dominio.
- **D-P11. CSRF con `csrf_protect` y `csrf: true` explícito.** Descartado confiar solo en JWT o
  activar CSRF globalmente en endpoints ajenos.
- **D-P12. Sin `PageView` y sin eventos del carrusel.** Descartado el snippet estándar de Meta.
- **D-P13. Sin `node --test`.** Descartado añadir un runner JS: no existe en el repo y la
  constitución exige aprobación para dependencias de test.
- **D-P14. Sin funciones dependientes de `hoy`.** Descartado mostrar “hace X”: no aporta y añadiría
  un reloj no inyectable.
- **D-P15. Sin registro en Django Admin.** Descartado una segunda vía de escritura para Producto.
- **D-P16. Publicación inmediata sin caché de API.** Descartado caché CDN con purga.
- **D-P17. Limpieza de claves de caché y CSS huérfanos.** Descartado dejar constantes y reglas sin
  consumidor: dificultan futuras lecturas y revisiones.
- **D-P18. Siete imágenes ya cargadas.** Descartado generar seed, fixtures o inventar descripción y
  texto alternativo; la tabla aprobada vive en §2 de la spec.

## 11. Estrategia de verificación

### 11.1 Comandos obligatorios

Desde la raíz del repositorio:

```bash
.\backend\.venv\Scripts\python.exe .\backend\manage.py check
.\backend\.venv\Scripts\python.exe .\backend\manage.py makemigrations --check --dry-run
.\backend\.venv\Scripts\python.exe .\backend\manage.py test servicios
cd frontend && npm run build && npm run lint
```

### 11.2 Cobertura de tests

Solo `django.test` vía `manage.py test`; no se instalan dependencias nuevas (constitución 4). La
suite debe seguir cubriendo:

- **Público:** solo visibles; orden `-fecha_creacion`, `-id`; sin `id`; filtros exactos; categoría
  inválida → `400`; campo `carrusel` de solo lectura con `url` y `alt`, sin `id`/`orden`/`visible`;
  `Cache-Control: no-store`.
- **Administración de productos:** anónimo/inactivo/no administrativo → `401/403`; CSRF sin token →
  `403`; CRUD, fechas no aceptadas del cliente, `DELETE` recuperable y reemplazo de imagen.
- **Imágenes:** tamaño, formato, MIME real, extensión engañosa, fallo de almacenamiento y ausencia
  de referencia residual.
- **No se reintroducen** tests de límite, posiciones ni reactivación del carrusel administrativo.

`node --test` no se usa: el repositorio no tiene runner JavaScript. La verificación del frontend es
`npm run build` (incluye `tsc -b`), `npm run lint` y comprobación manual.

### 11.3 Búsqueda de referencias residuales

Tras los cambios no debe quedar ninguna referencia a la antigua administración del carrusel, ni en
el código ni en los tres archivos de la spec: ni ruta, ni ViewSet, ni serializer, ni hooks, ni tipos,
ni reglas de posiciones, ni tests, ni estilos de esa superficie.

Sí deben seguir presentes el serializer público del carrusel, su campo en la API, `HeroProductos` y
`clave_publica_producto`.

### 11.4 Verificación manual (MCP o navegador)

- Panel: `/control-operativo/productos` sigue operativo; no hay enlace “Carrusel” y la ruta antigua
  cae en la página de no encontrada.
- `/productos`: el carrusel editorial sigue con cinco piezas, autoplay/pausa, teclado, gesto táctil
  y `prefers-reduced-motion`; el campo `carrusel` de la API no se renderiza.
- Viewports 320, 375, 768, 1024 y 1440 px sin desplazamiento horizontal propio.
- Si el MCP no está disponible, se documenta la limitación; no se declara una validación visual no
  realizada.

## 12. Riesgos

- **R1 — Referencias colgantes:** símbolos eliminados aún importados. Mitigación: búsqueda de §11.3 y build.
- **R2 — Regresión del contrato público:** quitar de más en `serializers.py` o `views.py` podría
  borrar `carrusel`. Mitigación: tests públicos y lista de “conservar” de §2.2.
- **R3 — Hook o caché rota:** retirar la clave `carrusel` sin limpiar invalidaciones. Mitigación:
  T5 de `tasks.md` y build/lint.
- **R4 — Documentación desincronizada:** el plan o las tareas podrían seguir describiendo el panel
  del carrusel. Mitigación: búsqueda de §11.3 también sobre `specs/013-vitrina-productos/`.
- **R5 — Migración accidental:** `makemigrations` podría proponer cambios al tocar reglas.
  Mitigación: no editar `models.py` ni `migrations/` y ejecutar `--check --dry-run`.
- **R6 — Validación visual no disponible:** se documenta en lugar de inventarse.

## 13. Carga editorial de las siete imágenes

Ya realizada y aprobada: los siete productos están cargados y visibles con la correspondencia de §2
de la spec. No hay tarea pendiente de aprobación, no se crean seed, fixtures ni ejemplos y no se
inventan marcas, referencias, precios ni stock.

## 14. Definición de terminado

1. `manage.py check`, `makemigrations --check --dry-run` y `manage.py test servicios` pasan, sin
   migración nueva.
2. `npm run build` y `npm run lint` pasan sin errores de tipos, imports ni rutas.
3. No existe API, página, ruta, menú, hooks, tipos ni estilos de administración del carrusel; la
   búsqueda de §11.3 no devuelve resultados.
4. `/api/productos/` sigue exponiendo `carrusel` de solo lectura y `ImagenCarrusel` sigue en el
   modelo, sin gestión desde la aplicación.
5. `HeroProductos` y sus cinco piezas estáticas siguen intactos y visibles en `/productos`.
6. La administración de Producto, su API, `clave_publica_producto`, la medición, el SEO y el panel
   de productos funcionan como antes.
7. Las siete imágenes iniciales siguen cargadas y visibles según §2 de la spec.
8. Los tres archivos de `specs/013-vitrina-productos/` describen el estado objetivo sin
   administración del carrusel y con la carga editorial ya resuelta.
