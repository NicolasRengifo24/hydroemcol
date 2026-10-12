# Plan — specs/001-solicitud-banco-pruebas

## Estado
La spec está aprobada. No tiene dudas abiertas relevantes (RF-10.1 queda anotado para la spec del panel administrativo). Se sigue el flujo SDD y la constitución de Hidroemcol.

## 1. Archivos a crear o modificar

| Archivo | Acción | Responsabilidad | RF cubiertos |
|---|---|---|---|
| `backend/servicios/validators.py` | Crear | Normalización y validación de correo/teléfono (normalizar_correo, normalizar_telefono). | RF-8.1 |
| `backend/servicios/reglas.py` | Modificar | Añadir `estados_cerrados()` y `tiene_solicitud_en_curso(hoy, *, correo_norm=None, telefono_norm=None)` (funciones puras). | RF-8.1, RF-8.6 |
| `backend/servicios/serializers.py` | Modificar | Crear `SolicitudPublicaSerializer`. Validación de contacto, componentes, fotos, duplicados e idempotencia. No pierde datos en errores. | RF-2.1–2.4, RF-3.3, RF-4.1–4.5, RF-5.1–5.3, RF-7.1–7.5, RF-8.1–8.6 |
| `backend/servicios/views.py` | Modificar | Crear `SolicitudPublicaCreateView` (POST, `AllowAny`). Creación en `transaction.atomic`, cliente/servicio/componentes/fotos, generación de token y código, manejo de duplicados + confirmar, soporte Idempotency-Key. | RF-6.1, RF-7.1–7.6, RF-8.1–8.6, RF-9.1–9.3 |
| `backend/servicios/urls.py` | Modificar | Añadir ruta pública `POST /api/solicitudes/`. No altera rutas existentes. | RF-1.1–1.2, RF-7.1, RF-9.1 |
| `backend/servicios/models.py` | Modificar | Sin cambio de esquema obligatorio. Se mantiene `Fotografia.url` (URLField). El serializer acepta archivos multipart y genera la URL tras subida. | RF-5 |
| `backend/servicios/tests/test_solicitudes_publicas.py` | Crear | Tests con `manage.py test` que cubren todos los RF de esta spec. | Todos RF |
| `frontend/src/services/api.ts` | Crear | Cliente HTTP con `fetch`, base desde `VITE_API_URL`, normalización de errores DRF, timeout. | RNF-3, RNF-6 |
| `frontend/src/services/solicitudes.ts` | Crear | `crearSolicitud(data, idempotencyKey)` → `POST /api/solicitudes/` (multipart o JSON según fotos). | RF-7.5–7.6 |
| `frontend/src/utils/idempotency.ts` | Crear | `generar_idempotency_key()` con `crypto.randomUUID()`. | RF-7.5 |
| `frontend/src/hooks/useCrearSolicitud.ts` | Crear | Mutación con React Query. Gestiona `isPending`, errores por campo, respuesta (código+enlace). | RF-7.6, RNF-5 |
| `frontend/src/pages/SolicitarServicio.tsx` | Modificar | Formulario responsive móvil-first. Componentes dinámicos, subida hasta 5 fotos (JPG/JPEG/PNG), aviso genérico de duplicados (Continuar/Cancelar), botón deshabilitado mientras envía, confirmación con código+enlace+copiar. Revisado con `web-design` y `web-design-guidelines`. | RF-1–RF-9, RNF-1, RNF-2, RNF-5 |
| `frontend/vite.config.ts` | Modificar | Proxy `/api` → `http://127.0.0.1:8000` para desarrollo. | Desarrollo |
| `frontend/.env.example` | Crear | `VITE_API_URL=/api`. | Config |
| `specs/001-solicitud-banco-pruebas/tasks.md` | Crear | Tareas pequeñas, verificables, ordenadas por dependencia. | Cobertura global |

## 2. Funciones puras de lógica (con "hoy" como parámetro)

| Función | Ubicación | Firma | Descripción | RF |
|---|---|---|---|---|
| `normalizar_correo` | `backend/servicios/validators.py` | `normalizar_correo(c: str) -> str` | `strip().lower()`. | RF-8.1 |
| `normalizar_telefono` | `backend/servicios/validators.py` | `normalizar_telefono(t: str) -> str` | Elimina espacios, guiones, paréntesis, `+`. Trata `+57` como opcional (nacional). No modifica dígitos restantes. | RF-8.1 |
| `estados_cerrados` | `backend/servicios/reglas.py` | `estados_cerrados() -> tuple[str,...]` | Fuente única: `(EstadoServicio.FINALIZADO, EstadoServicio.ENTREGADO, EstadoServicio.CANCELADO)`. | RF-8.6 |
| `tiene_solicitud_en_curso` | `backend/servicios/reglas.py` | `tiene_solicitud_en_curso(hoy, *, correo_norm=None, telefono_norm=None) -> bool` | Busca Servicios con estado NO incluido en `estados_cerrados()`. Usa OR entre correo y teléfono (si se proporcionan). No devuelve datos (solo booleano). | RF-8.1, RF-8.6 |
| `generar_idempotency_key` | `frontend/src/utils/idempotency.ts` | `generar_idempotency_key() -> string` | `crypto.randomUUID()`. | RF-7.5 |

## 3. Algoritmo en pseudocódigo

**SolicitudPublicaCreateView (POST `/api/solicitudes/`)**

```text
1. Leer header `Idempotency-Key` (opcional). Leer cuerpo (multipart si hay fotos, else JSON).
2. Validar con `SolicitudPublicaSerializer` (contacto, componentes >=1, fotos máx 5, formatos JPG/JPEG/PNG).
3. Normalizar: `correo_norm = normalizar_correo(correo)`, `tel_norm = normalizar_telefono(telefono o whatsapp)`.
4. Si existe `Idempotency-Key`:
   - Buscar respuesta previa asociada a ese key. Si existe → devolver 200 con mismo payload (código, enlace_seguimiento, servicio_id). (RF-7.5)
5. Detección de duplicados (tras validación básica, server-side):
   - Si `tiene_solicitud_en_curso(hoy, correo_norm=..., telefono_norm=...)` → responder 409 con `requiere_confirmacion=true` y mensaje genérico (sin exponer código/fecha) para mitigar enumeración. (RF-8.1–RF-8.5, Duda mitigación)
6. Si `requiere_confirmacion` es true y `confirmar != true` → NO crear. Queda a espera de confirmación (cliente continúa/cancela).
7. Si `confirmar == true` o no hay duplicado → ejecutar en `transaction.atomic()`:
   - Cliente: buscar por (correo_norm + tel_norm) o por OR. `get_or_create` sin fusionar solicitudes distintas (mantener independientes). (RF-7.4)
   - Servicio: crear con `tipo_servicio=TipoServicio.PRUEBA`, `estado=EstadoServicio.SOLICITADO`, `descripcion_solicitud`, generar `token_seguimiento = secrets.token_urlsafe(24)`, `codigo` autogenerado en `save()`. (RF-6.1, RF-7.1, RF-9.1)
   - Componentes: crear N. `tipo` obligatorio, `cantidad = 1` por defecto (>=1), `marca/referencia/descripcion` opcionales (descripción opcional permitido). (RF-4.1–RF-4.5)
   - Fotografías: para cada archivo válido, subir a almacenamiento (Cloudflare) vía helper interno, guardar `Fotografia.url` con URL devuelta. Máx 5, formatos aceptados. (RF-5)
   - (Opcional) HistorialServicio: estado SOLICITADO, `visible_cliente=False`.
8. Devolver 201: `{codigo, enlace_seguimiento, servicio_id}` donde `enlace_seguimiento = /seguimiento/<token_seguimiento>`. (RF-9.1–RF-9.3)
9. UI: botón deshabilitado mientras `isPending` (RF-7.6). Doble clic reutiliza Idempotency-Key → misma respuesta.
```

## 4. Cómo se pinta la interfaz

Usar **`web-design`** y **`web-design-guidelines`** para composición, jerarquía, accesibilidad y responsive.

**Página `SolicitarServicio.tsx` (mobile-first):**

| Sección | Elementos | Reglas UX |
|---|---|---|
| Encabezado | Título + texto explicativo | "No requiere cuenta. Te daremos un código y un enlace para seguir tu solicitud." |
| Contacto | Nombre* (input), Empresa (opcional), Correo* (email), Teléfono* O WhatsApp* (tel). Al menos uno requerido. | Labels asociados, errores por campo, preservar input (RF-2.1–2.3) |
| Necesidad | Textarea descripción* (500 máx, contador caracteres). | Obligar mínimo, informar límite. (RF-2.4) |
| Componentes (dinámicos) | Tipo* (texto), Marca, Referencia, Descripción (500 máx opcional), Cantidad (number >=1, default 1). Botones + Añadir, - Quitar. | >=1 componente. Descripción opcional permitido. (RF-4.1–RF-4.5) |
| Fotos | Input múltiple `accept=".jpg,.jpeg,.png"`. Thumbnails + eliminar cada una. Límite 5. Mensajes de error claros (formato). | 0 permitido, máx 5, solo JPG/JPEG/PNG. (RF-5.1–RF-5.4) |
| Preferencias entrega | 3 checkboxes (opcional): entregar en banco, avisar para coordinar, recoger. | Opcional múltiple. (RF-3.1–RF-3.3) |
| Acciones/Estado | Botón "Enviar". Deshabilitado mientras `isPending`. Texto cambia a "Enviando...". Feedback loading. | RF-7.6, RNF-5 |
| Aviso duplicados | Inline/modal genérico: "Parece que tienes una solicitud en curso. ¿Quieres continuar o cancelar?" Botones "Continuar" / "Cancelar". Cancelar → formulario intacto, no envía. | RF-8.2–RF-8.3, mitigación enumeración (Duda 5) |
| Confirmación | Código, enlace `/seguimiento/<token>` con botón "Copiar". Texto: enlace privado, solo para esa solicitud. | RF-9.1–RF-9.3 |

**Responsive**: móvil 375–430, tablet >=768, desktop >=1024. Usa jerarquía clara, foco visible, contraste suficiente, HTML semántico (forms + labels). Loading/error/empty tratados. (RNF-1, RNF-2)

## 5. Decisiones técnicas justificadas (con alternativa descartada)

| Decisión | Justificación | Alternativa descartada |
|---|---|---|
| **D-1** Fotos: archivos → backend → Cloudflare. Modelo guarda `URLField`. | Coincide con `Fotografia.url` existente y con indicación del usuario (subida de archivos, almacenamiento en Cloudflare, guardar URL). Mantiene stack mínimo (principio 1). | Subida directa frontend a Cloudflare (signed upload): requiere worker/token y configuración adicional. Mayor complejidad para MVP. Descartado. |
| **D-2** Idempotencia con header `Idempotency-Key` + `crypto.randomUUID()` en frontend. | Garantiza RF-7.5 ante doble clic, recarga y apertura en otra pestaña. Backend devuelve misma respuesta. | Solo deshabilitar botón: insuficiente para recarga/pestañas distintas. Descartado. |
| **D-3** Duplicados con OR (correo O teléfono), normalización estricta correo, laxa teléfono. | RF-8.1 lo indica. Teléfono: quitar espacios/guiones/paréntesis/`+` (tratar `+57` opcional). Reduce falsos negativos. | AND: aumenta falsos negativos (teléfono fijo compartido). Descartado. |
| **D-4** Aviso de duplicados **genérico** (sin código/fecha). | Mitiga riesgo de enumeración (privacidad). Mensaje neutro: "Parece que tienes una solicitud en curso...". | Texto más específico (revelaría existencia/datos): riesgo innecesario. Descartado. |
| **D-5** Detección de duplicados **server-side** tras validación básica de formato. | Duda 7. Evita búsquedas con datos inválidos. Funciona con otra pestaña. | Predictiva por cambio de campo: carga extra, complejidad. Descartado. |
| **D-6** Creación con `transaction.atomic()`. | Garantiza atomicidad (cliente+servicio+componentes+fotos) o revierte todo. Evita solicitudes "a medias" ante corte/conexión. (caso límite). | Creación por pasos: riesgo de estado parcial. Descartado. |
| **D-7** Tipo obligatorio, cantidad `default=1` (>=1), descripción opcional. | Duda 8. Tipo identifica componente. Cantidad coherente. Descripción opcional cumple RF-4.5. | Tipo opcional: solicitudes poco útiles. Descartado. |
| **D-8** RF-10.1 queda **anotado**, no implementado en esta spec. | Respeta §7 (fuera de alcance interacción del panel). Pertenece a spec del panel administrativo. Evita añadir tiempo real aquí. | Implementar polling/SSE ahora: contradice fuera de alcance, añade complejidad. Descartado. |
| **D-9** Subida vía backend (multipart) con helper interno a Cloudflare. | Mantiene stack mínimo (principio 1). No añade dependencia nueva. Modelo sigue `URLField`. | SDK Cloudflare en frontend/backend con nueva dependencia: requiere aprobación explícita y config. Descartado para MVP. |
| **D-10** No modificar esquema innecesariamente. | Principio 2. Solo añadir validación/serializers/vistas/tests. Migración no necesaria ahora. | Añadir campos nuevos prematuramente: riesgo innecesario. Descartado. |
| **D-11** Garantía de unicidad (RF-7.5) **en backend** (Idempotency-Key) + UI deshabilitada. | Principio 3: backend decide. Botón ayuda UX (RF-7.6), backend garantiza integridad (race conditions, recarga, pestañas). | Solo UI: no garantiza servidor. Descartado. |

## 6. Estrategia de tests

Tests con **`manage.py test`** (principio 4). Crear `backend/servicios/tests/test_solicitudes_publicas.py`.

| Test | Qué cubre | RF |
|---|---|---|
| `test_crear_solicitud_minima_ok` | Mínima válida: 1 componente, sin fotos, preferencias vacías. Devuelve código y enlace con token. | RF-1, RF-2, RF-4, RF-6, RF-7.1, RF-9.1–RF-9.3 |
| `test_varios_componentes_una_solicitud` | 2 componentes → misma solicitud. | RF-4.1, RF-7.3, Criterio 2 |
| `test_campos_obligatorios` | Faltan obligatorios → errores por campo, no pierde datos. | RF-2.2–2.3, RF-4.2 |
| `test_correo_invalido` | Correo inválido → error por campo. | RF-2.2 |
| `test_telefono_o_whatsapp_minimo` | Al menos uno requerido. Solo WhatsApp OK. Solo teléfono OK. Ninguno → error. | RF-2.1 |
| `test_descripcion_max_500` | >500 → error. ==500 → válido. | RF-2.4 |
| `test_componente_sin_descripcion_permitido` | Descripción vacía OK. Tipo obligatorio, cantidad default 1. | RF-4.5, Duda 8 |
| `test_marca_referencia_opcionales` | Vacías permitidas. | RF-4.3 |
| `test_requiere_al_menos_un_componente` | Lista vacía → error. | RF-4.2, RF-4.4 |
| `test_fotos_max_5` | 6 → error. 5 → OK. 0 → OK. | RF-5.1–RF-5.2, RF-5.4 |
| `test_fotos_formato_invalido` | .txt/.bmp → rechazado. | RF-5.3 |
| `test_preferencias_opcionales` | Ninguna/múltiples → válidas, se guardan como info. | RF-3.1–RF-3.3 |
| `test_duplicado_requiere_confirmacion` | Existe solicitud EN_REVISION con mismo correo O teléfono → `requiere_confirmacion=true`, no crea. Mensaje genérico. | RF-8.1–RF-8.5 |
| `test_duplicado_estados_cerrados_no_avisan` | CANCELADO/ENTREGADO/FINALIZADO → no avisa, crea nueva. | RF-8.6 |
| `test_duplicado_confirmar_crea_nueva` | `confirmar=true` → crea nueva solicitud (independiente). | RF-8.4 |
| `test_duplicado_cancelar_no_crea` | `confirmar=false` → no crea, datos intactos. | RF-8.3 |
| `test_idempotencia_mismo_key_devuelve_misma` | Mismo `Idempotency-Key` → misma respuesta, count inalterado. | RF-7.5 |
| `test_idempotencia_datos_distintos_no_reutiliza` | Mismo key + datos distintos → comportamiento coherente (no reutiliza). | RF-7.5 |
| `test_normalizacion_correo_telefono` | Normalización detecta duplicado correctamente. | RF-8.1 |
| `test_tipo_servicio_prueba` | Creada → `tipo_servicio=PRUEBA`. | RF-6.1 |
| `test_enlace_contiene_token` | `enlace_seguimiento` contiene `token_seguimiento`. | RF-9.1–RF-9.3 |
| `test_fotos_guardan_url` | Tras subida → `Fotografia.url` no vacío. | RF-5 |

**Frontend**: `tsc -b` sin errores, `oxlint` pasa, revisión visual con Chrome DevTools (móvil 375px). No se añaden dependencias de test (principio 4).

## 7. Criterios de finalización

1. Todos los tests backend pasan (`manage.py test servicios.tests.test_solicitudes_publicas`).
2. `POST /api/solicitudes/` acepta `multipart/form-data` y `application/json`.
3. Duplicados devuelven aviso genérico (sin exponer datos), con flujo Continuar/Cancelar.
4. Idempotency-Key devuelve la misma respuesta en envíos repetidos.
5. Formulario usable en móvil 375px, accesible, botón deshabilitado en envío, confirmación con código+enlace+copiar.
6. `tsc -b` OK, `oxlint` OK, `manage.py check` sin incidencias.
7. RF-10.1 queda anotado en spec (sin implementar). Todo lo demás de la spec está cubierto.

**Verificación de aprobación**: Spec `Estado: aprobada`, sin dudas abiertas relevantes. Plan cumple constitución y cubre todos los RF.
