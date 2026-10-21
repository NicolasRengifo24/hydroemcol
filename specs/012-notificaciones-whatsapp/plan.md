# Plan — Spec 012: Notificaciones de estado por WhatsApp (mensajes preparados)

**Spec:** `specs/012-notificaciones-whatsapp/spec.md` (aprobada completa; textos de interfaz de §4.2 aprobados)
**Estado:** aprobado junto con la spec. Las decisiones A1 a A7 están resueltas (§8).

> Este plan define el CÓMO a nivel de archivos, contratos y decisiones. El QUÉ y el POR QUÉ siguen en la spec.

---

## 0. Principios aplicados

- **El backend decide** (constitución 3, RNF-WA-03): texto, validez del número, elegibilidad de un evento,
  permisos y avisos (`aviso`) salen del backend. El frontend muestra, edita y abre el enlace.
- **Sin dependencias nuevas, sin migraciones, sin tablas nuevas** (RNF-WA-01, RNF-WA-02, constitución 1).
- **Pull, no push:** el texto se calcula al leer (endpoint de solo lectura). No hay historial de mensajes ni
  escritura de estado de envío (RF-WA-14, decisión 8 original).
- **Funciones puras:** la construcción de textos y la validación no tocan la base de datos ni el reloj.
  Por eso no llevan parámetro `hoy`: ningún texto aprobado disponible usa `{fecha}` (P4 excluye
  `FINALIZADO`). Si P4 cambia, la fecha se formateará en la vista con `zoneinfo` (stdlib) en
  `America/Bogota`, sin tocar `TIME_ZONE` (RF-WA-11, R13).
- **Tests:** solo `manage.py test` con `django.test` y solo para CA-02, CA-06, CA-12, CA-14, CA-15 y CL-24
  (R12). **No se escribe ninguna prueba JavaScript** (ni `node --test` ni otra librería): el frontend se
  verifica con el MCP chrome-devtools. Si se quisiera un test `node --test` para `services/whatsapp.ts`, se
  propone y se pide aprobación antes (constitución 4).

---

## 1. Inventario de archivos

Rutas verificadas con glob/grep el 2026-10-20. "MOD" = existe hoy y se modifica; "NUEVO" = no existe.

### 1.1 Backend (`backend/`)

| Archivo | Tipo | Cambio | RF / CA / CL |
|---|---|---|---|
| `backend/servicios/validators.py` | MOD | Añadir `validar_celular_colombiano(valor) -> str \| None`. **No se toca** `normalizar_telefono`. | RF-WA-02, CA-02, CL-01, CL-02 |
| `backend/servicios/serializers.py` | MOD | `SolicitudPublicaSerializer` (líneas ~759-803): `whatsapp` obligatorio, `validate_whatsapp` usa el validador nuevo, `validate()` ya no necesita la regla "teléfono o WhatsApp". `telefono` queda opcional. Mensajes de error en español (texto de spec §4.2). | RF-WA-02, RF-WA-03 |
| `backend/servicios/views.py` | MOD | (a) `SolicitudPublicaCreateView.post` (líneas ~858-892): si el cliente existe sin WhatsApp, guardar el de la solicitud. (b) NUEVO `ServicioWhatsAppView` (APIView, solo `get`, `EsAdministrativo`), junto a `CambiarEstadoComponenteView`. | RF-WA-04, RF-WA-20, RF-WA-30, CL-24 |
| `backend/servicios/urls.py` | MOD | Añadir `path('servicios/<int:servicio_pk>/whatsapp/', ServicioWhatsAppView.as_view(), name='servicio-whatsapp')`. | RF-WA-30 |
| `backend/servicios/mensajes.py` | NUEVO | Módulo puro: plantillas de §4.1 de la spec, `enlace_seguimiento`, `texto_componente`, `texto_servicio`, `construir_bloque_whatsapp`. Sin Django ni ORM. | RF-WA-05..13, RF-WA-19, RF-WA-21, RF-WA-28, RF-WA-29 |
| `backend/config/settings.py` | MOD | Leer `SEGUIMIENTO_BASE_URL` del entorno junto a las demás variables (después del bloque `CORS_ALLOWED_ORIGINS`, ~línea 204). Valor por defecto `''`. | RF-WA-29 |
| `backend/.env.example` | MOD | Documentar `SEGUIMIENTO_BASE_URL` (sin valor de producción). | RF-WA-29 |
| `docs/deployment.md` | MOD | Añadir la variable a la lista de variables de producción. | RF-WA-29 |
| `backend/servicios/tests/test_whatsapp.py` | NUEVO | Pruebas `django.test` de CA-02 (HTTP y validador), CL-24, CA-12, CA-14, CA-15 y CA-06. | ver §6 |
| `backend/servicios/tests/test_t2_serializer.py` | MOD | Sus payloads válidos solo envían `telefono`; deben añadir un `whatsapp` válido. Consecuencia de R6, no prueba nueva. | RF-WA-03 |
| `backend/servicios/tests/test_t3_view.py` | MOD | Igual que el anterior (líneas 14 y 28). | RF-WA-03 |
| `backend/servicios/tests/test_solicitudes_publicas.py` | MOD | Añadir `whatsapp` a los payloads válidos; `test_telefono_normalizado` (línea ~73) y la aserción `assertIn("telefono", resp.data)` (línea ~109) pasan a la clave `whatsapp`. | RF-WA-03 |

**Sin cambios:** `backend/servicios/models.py` (ningún campo nuevo; `Cliente.whatsapp` ya existe, línea 79),
`backend/servicios/migrations/` (sin migración), `backend/servicios/reglas.py`, `backend/servicios/acciones.py`
(no se añade ninguna acción ni transición), `backend/servicios/admin.py`, `backend/servicios/estados.py`.
`normalizar_telefono` y su uso en la comparación de duplicados (`tiene_solicitud_en_curso`) no cambian.

### 1.2 Frontend (`frontend/src/`)

| Archivo | Tipo | Cambio | RF / CA / CL |
|---|---|---|---|
| `services/api.ts` | MOD | Tipos `MensajeWhatsApp` y `RespuestaWhatsApp`; función `obtenerMensajesWhatsapp(servicioId)` con `apiRequest` (GET); clave `whatsapp(id)` dentro de `clavesAdministrativas.servicio(id)` (líneas ~588-610) para que la invalidación por prefijo existente la refresque. | RF-WA-30 |
| `hooks/useAdministrativo.ts` | MOD | `useMensajesWhatsapp(id)` con `useQuery`, `enabled` igual que `useServicioAdministrativo`. No añade mutaciones: la invalidación de `['administrativo','servicio']` ya cubre la clave nueva. | RF-WA-19, RF-WA-30 |
| `services/whatsapp.ts` | NUEVO | Dos funciones puras de presentación: `construirUrlWhatsApp(numeroDestino, texto)` (`https://wa.me/<numero>?text=` + `encodeURIComponent`) y `abrirWhatsApp(url): boolean` (ver D5). | RF-WA-17, RF-WA-23 |
| `components/AdminWhatsApp.tsx` | NUEVO | Sección "WhatsApp" del detalle: tarjetas, editor de una línea, botón, avisos, reintento, aviso de "no enviado". Sigue el patrón de `components/AdminEvidencia.tsx`. | RF-WA-15..18, 21..25 |
| `pages/AdminServicioDetalle.tsx` | MOD | Importar y renderizar `<AdminWhatsApp servicioId={id} />` después de la sección de Cotizaciones (línea ~54). No se cambia ninguna otra sección. El archivo ya es denso: no añadir lógica aquí, solo el montaje. | RF-WA-15 |
| `index.css` | MOD | Estilos `.admin-whatsapp*` con objetivos de 44 px, foco visible y sin desborde a 375 px. Reutiliza `admin-button`, `admin-panel`, `admin-feedback`. | RNF-WA-05 |
| `pages/SolicitarServicio.tsx` | MOD | Campo `whatsapp` con `required` (línea ~445-467). Quitar el texto "Indica al menos un teléfono o un WhatsApp" (línea 467) y poner la ayuda neutra de §4.2 cuando se apruebe. Mostrar el error que devuelve el backend en `errorCampos.whatsapp` (ya existe el mecanismo, línea ~246). **No se añade regex ni validación de número en el frontend.** | RF-WA-02, RF-WA-03 |
| `services/solicitudes.ts` | MOD | `whatsapp` deja de ser opcional en el tipo (líneas 16-17) y siempre se envía (línea 53). | RF-WA-01 |

**Sin cambios:** `pages/AdminLogin.tsx` (ya vuelve a `location.state.from.pathname`, ver §4 D9),
`components/RutaAdministrativaProtegida.tsx`, `components/AdminLayout.tsx`, `config/sitio.ts` (es el número
de la empresa, no el del cliente), `hooks/useCrearSolicitud.ts` (solo propaga errores), `router.tsx`.

### 1.3 Documentación (fuera de `specs/`, la ejecuta el implementador)

| Archivo | Tipo | Cambio | RF / CA |
|---|---|---|---|
| `CONTEXTO_MAESTRO.md` §43 | MOD | Quitar "Formato definitivo de mensajes de WhatsApp" de pendientes y referenciar los textos de la spec 012 §4.1. Es prerrequisito de la spec (RF-WA-26). | RF-WA-26, CA-17 |
| `MEMORY.md` | MOD | Entrada de bitácora con decisiones y resultado de verificación; actualizar §2 (WhatsApp deja de estar sin definir). | RF-WA-26, CA-17 |

> El planificador no escribe fuera de `specs/`. Estos cambios los hace el implementador en la tarea correspondiente.

---

## 2. Contrato del endpoint nuevo (solo lectura)

**Ruta:** `GET /api/servicios/<servicio_pk>/whatsapp/` (nombre `servicio-whatsapp`).
**Permiso:** `EsAdministrativo` (cuenta activa y `rol == 'ADMINISTRATIVO'`), igual que el resto de vistas
administrativas. Sin token o con cliente/cuenta inactiva: rechazo sin datos (RF-WA-20).
**Métodos:** solo `GET`. `POST`, `PUT`, `PATCH` y `DELETE` responden 405 (DRF, al no definirse).
**Errores:** 404 si el servicio no existe; 401/403 por permiso; 500 ante un fallo inesperado (el frontend
muestra RF-WA-22).

**Respuesta 200:**

```json
{
  "codigo": "SRV-2026-00009",
  "abierto": true,
  "numero_destino": "573001234567",
  "aviso": null,
  "mensajes": [
    {
      "clave": "servicio",
      "ambito": "SERVICIO",
      "etiqueta": "Servicio SRV-2026-00009",
      "estado": "EN_CURSO",
      "etiqueta_estado": "En curso",
      "texto": "Hidroemcol: su servicio SRV-2026-00009 está en curso. Siga el avance en: https://…/seguimiento/…",
      "aviso": null
    },
    {
      "clave": "componente-en_pruebas-0",
      "ambito": "COMPONENTE",
      "etiqueta": "Bomba hidráulica (REF-77)",
      "estado": "EN_PRUEBAS",
      "etiqueta_estado": "En pruebas",
      "texto": "Hidroemcol: Bomba hidráulica (REF-77) (servicio SRV-…) está en pruebas.",
      "aviso": null
    }
  ]
}
```

Las tarjetas exponen únicamente datos públicos necesarios para renderizar: `clave`, `ambito`
(tipo de tarjeta), `estado`, `etiqueta_estado`, `etiqueta` visible, `texto` vigente y `aviso`.
La `clave` del servicio es `servicio`; la de cada componente es estable dentro de la respuesta y
usa el formato `componente-{estado}-{posición}` (el estado en minúsculas y la posición empezando
en cero), sin incluir ningún ID interno. El borrador editado, si existe, pertenece al estado local
del frontend y no se devuelve en este contrato.

**Reglas del contrato (todas en `mensajes.py`, la vista solo reúne datos):**

| Situación | `abierto` | `numero_destino` | `aviso` (servicio) | `mensajes` |
|---|---|---|---|---|
| Servicio abierto, número válido, dominio configurado | true | `"57"+10 dígitos` | null | una tarjeta por componente con texto + la del servicio si su estado tiene texto |
| `activo=False` (RF-WA-28) | — | null | "Este servicio está desactivado. No se preparó el mensaje." | `[]` |
| Número inválido o vacío (RF-WA-21) | true | null | texto de spec §4.2 (caso cliente sin número) | `[]` |
| Servicio `FINALIZADO` o `CANCELADO` (P4) | false | `"57…"` (informativo) | texto de spec §4.2 (caso servicio cerrado) | `[]` |
| Dominio vacío y texto con `{enlace}` (RF-WA-29) | true | `"57…"` | texto de spec §4.2 (caso falta `SEGUIMIENTO_BASE_URL`) | solo los textos sin `{enlace}`; los demás `texto: null` |
| Componente `RECHAZADO` sin motivo (CL-13) | true | `"57…"` | null | ese componente `texto: null`, `aviso: "No se pudo preparar el mensaje. Inténtalo de nuevo."` |

- Un componente cuyo estado no tiene texto aprobado no aparece en `mensajes`.
- Cada tarjeta corresponde al **estado vigente** (RF-WA-19). Con un cambio de estado, la tarjeta cambia en la siguiente lectura.
- Los textos aprobados se usan con la redacción de §4.1 de la spec, con `usted`. Los avisos del panel van en `tú` (R13).
- El campo `codigo` viene del servicio; el campo `numero_destino` nunca incluye `+`.
- La respuesta no incluye `id` interno del servicio, `observaciones_internas`, nombres de usuario ni el `token` fuera de `enlace` dentro del texto (CA-12).

---

## 3. Funciones puras (`backend/servicios/mensajes.py`)

Ninguna función accede a la base de datos, a `request` ni al reloj. Reciben datos ya leídos.

```python
PLANTILLAS_SERVICIO = {  # estado -> texto aprobado (spec §4.1) con {codigo} y {enlace}
    'SOLICITADO': 'Hidroemcol: recibimos su solicitud {codigo}. Siga el avance en: {enlace}',
    'EN_CURSO': 'Hidroemcol: su servicio {codigo} está en curso. Siga el avance en: {enlace}',
    # FINALIZADO y CANCELADO existen en el texto aprobado, pero P4 impide su botón: no se preparan.
}
PLANTILLAS_COMPONENTE = {  # estado -> texto aprobado con {componente}, {codigo}, {enlace}, {motivo}
    'PENDIENTE': 'Hidroemcol: el componente {componente} del servicio {codigo} fue recibido.',
    'EN_REVISION': 'Hidroemcol: el componente {componente} del servicio {codigo} está en revisión.',
    'COTIZANDO': 'Hidroemcol: estamos preparando la cotización de {componente} (servicio {codigo}).',
    'ESPERANDO_APROBACION': 'Hidroemcol: {componente} (servicio {codigo}) espera su aprobación. Revise la cotización en: {enlace}',
    'OPERARIO_TRABAJANDO': 'Hidroemcol: iniciamos el trabajo en {componente} (servicio {codigo}).',
    'EN_PRUEBAS': 'Hidroemcol: {componente} (servicio {codigo}) está en pruebas.',
    'LISTO_PARA_ENTREGA': 'Hidroemcol: {componente} (servicio {codigo}) está listo para entregar.',
    'RECHAZADO': 'Hidroemcol: {componente} (servicio {codigo}) fue rechazado. Motivo: {motivo}. Detalle: {enlace}',
}
ESTADOS_SERVICIO_CERRADOS = frozenset({'FINALIZADO', 'CANCELADO'})  # constante local; no se usa reglas.estados_cerrados() (consulta BD)
```

| Función | Entrada | Salida | Nota |
|---|---|---|---|
| `enlace_seguimiento(base, token) -> str \| None` | `base` (de settings), `token` | `f'{base}/seguimiento/{token}'` o `None` si `base` vacío o no empieza por `http://`/`https://` | Quita la barra final de `base`. Una base mal formada = "no configurado" (RF-WA-29, sin enlace parcial). |
| `etiqueta_componente(tipo, referencia) -> str` | strings | `"Bomba (REF-77)"`, o solo `"Bomba"` si no hay referencia (A3) | P1 opción b; A3 resuelta. |
| `texto_servicio(estado, codigo, enlace) -> str \| None` | | texto o `None` si no hay plantilla o falta `enlace` cuando se necesita | |
| `texto_componente(estado, etiqueta, codigo, enlace, motivo) -> str \| None` | | igual; para `RECHAZADO` exige `motivo` no vacío (CL-13) | `motivo` se usa tal cual (R1). Solo `RECHAZADO` lo incluye (P3). |
| `construir_bloque_whatsapp(servicio, componentes, base_url, numero_destino) -> dict` | dicts planos | la respuesta de §2 | Orquesta las reglas de la tabla de §2. Es la única función que la vista llama. |

**Validación (en `validators.py`, no en `mensajes.py`):**
`validar_celular_colombiano(valor: str) -> str | None`
1. Quita espacios, guiones, paréntesis.
2. Si empieza por `+57`, quita ese prefijo; si empieza por `57` y quedan 12 dígitos, quita `57`. **Caso ambiguo** resuelto así: un celular de 10 dígitos que empieza por `57` no puede existir (empiezan por 3), así que el prefijo solo se quita cuando hace falta.
3. Exige exactamente 10 dígitos y que el primero sea `3`. Devuelve los 10 dígitos o `None`.

Casos: `3001234567`, `+57 300 123 4567` y `57-300-123-4567` → `3001234567` (CL-01). `6011234567`, 9 u 11 dígitos, primer dígito distinto de 3 → `None` (CL-02).

---

## 4. Decisiones técnicas

**D1 — Endpoint único por servicio, no por recurso.**
Una sola llamada devuelve todas las tarjetas del detalle.
*Descartado:* (a) un endpoint por componente (N llamadas al abrir el detalle); (b) añadir `mensajes` a `ServicioAdministrativoSerializer` (mezcla lectura de texto con el detalle, y calcularía textos en cada `GET` del detalle y en el listado; el texto debe ser un recurso propio, RF-WA-30).

**D2 — Validador separado de `normalizar_telefono`.**
`normalizar_telefono` solo limpia y se usa en el aviso de duplicados (001 RF-8, spec §12). Mezclar validación y limpieza en esa función alteraría la comparación. Se crea `validar_celular_colombiano`, que devuelve el mismo valor normalizado para los casos válidos.
*Descartado:* reutilizar `normalizar_telefono` y comprobar después la longitud en el serializer (duplica la lógica de limpieza y deja el criterio disperso).

**D3 — Texto construido en backend, plantillas en código.**
Las plantillas viven en un diccionario de `mensajes.py`. El texto aprobado no es configurable (§11 de la spec).
*Descartado:* plantillas en BD o en `settings` (introduce un modelo o una configuración que la spec deja fuera de alcance).

**D4 — Texto al leer (pull), sin guardar nada.**
No hay tabla ni campo de mensaje. Consecuencia directa de RNF-WA-02 y de la decisión 8.
Con la decisión A1 (opción a) el botón del estado vigente se muestra siempre, así que el backend no necesita el origen del cambio: no hay campo nuevo ni migración.

**D5 — `wa.me` con `window.open` sin `noopener` y comprobación de `null`.**
Se llama a `window.open(url, '_blank')` dentro del clic, sin `await` antes. Si devuelve `null`, el navegador bloqueó la ventana (RF-WA-23). Si no, se asigna `win.opener = null` para mantener la seguridad de `noopener`.
*Descartado:* `<a target="_blank" rel="noopener">`: el navegador no informa si la ventana fue bloqueada, así que RF-WA-23 no se podría cumplir ni verificar.

**D6 — Captura del número y regla de no sobrescritura.**
En `SolicitudPublicaCreateView.post`, después de `get_or_create`: si el cliente ya existía y `cliente.whatsapp` está vacío, se guarda el número validado de la solicitud con `save(update_fields=['whatsapp'])`, dentro de la misma transacción. Si ya tenía número, aunque no cumpla RF-WA-02, no se toca (CL-22, CL-24). La corrección se hace en Django Admin.
*Descartado:* `update_or_create` (sobrescribe, prohibido por R2).
*Nota:* `tiene_solicitud_en_curso` ya recibía `whatsapp_norm`. Ahora siempre llega un valor válido. Esto amplía en la práctica la comparación de duplicados por WhatsApp. **Pendiente futuro (A7):** no se cambia en esta spec.

**D7 — Dominio del enlace en settings.**
`settings.SEGUIMIENTO_BASE_URL` (nombre decidido en A4) se lee con `os.getenv('SEGUIMIENTO_BASE_URL', '')` y se pasa a `enlace_seguimiento`. Sin valor, el sistema no inventa un dominio ni genera enlaces parciales (RF-WA-29, CA-21). El valor de producción no va en el código.

**D8 — Zona horaria.**
No se implementa conversión de fecha: ningún texto disponible usa `{fecha}` (P4). `TIME_ZONE` sigue en `UTC`.

**D9 — Sesión caducada y conservación del texto editado (A5).**
`AdminLogin.tsx` ya navega a `location.state.from.pathname` tras iniciar sesión, así que no hace falta cambiarlo. El borrador editado se guarda en `sessionStorage` con clave `hidroemcol.whatsapp.<servicioId>.<clave>` cada vez que cambia el campo; al montar, la sección lo recupera. El almacenamiento dura lo que la pestaña: se borra al cerrarla.
*Trade-off aceptado:* el texto incluye el enlace con token en el almacenamiento de esa pestaña (RNF-WA-04).
Cuando la lectura o la acción devuelve 401 y el refresco ya falló, `AdminWhatsApp` navega a `/admin/login` con `state: { from: location }` y muestra el aviso de sesión caducada (spec §4.2).

**D10 — Componente separado, no inline.**
`AdminServicioDetalle.tsx` ya tiene un tamaño que dificulta su mantenimiento. La sección vive en `AdminWhatsApp.tsx`, reutilizable y probable de revisar por separado.

**D11 — Cambio de estado vs. tarjeta.**
Tras cambiar un estado (mutación ya existente), la invalidación refresca la lectura de WhatsApp. El borrador editado de una tarjeta cuyo texto vigente cambió se descarta y se muestra el texto nuevo (RF-WA-19). Si el texto no cambió, se conserva.

**D12 — Dónde se nota la regla de "generar por evento" (A1 y A2).**
Con A1 (a) la tarjeta del estado vigente siempre existe, así que la diferencia entre "generar" y "mostrar" solo es visible en un momento: justo después de que el administrativo cambia un estado (o registra una aprobación) desde el panel. Implementación propuesta:
- La mutación de cambio de estado o de aprobación desde el panel marca, en el estado del componente de la sección (no en el backend y sin texto nuevo), la tarjeta del estado de destino: la enfoca y la resalta con borde y etiqueta visible de "Cambio reciente".
- Un cambio automático, del cliente o desde el Django Admin no marca nada: la tarjeta aparece igual, sin resaltado.
- A2: una aprobación registrada a mano marca la tarjeta de `OPERARIO_TRABAJANDO` solo si el estado del componente cambió. Si no cambió, no se marca.
- **Texto aprobado:** la etiqueta "Cambio reciente" es el texto de resaltado de D12 y queda aprobada para T7.
*Descartado:* guardar el origen en la base de datos (exigiría migración, RNF-WA-02, y la decisión A1 (a) no la necesita).

---

## 5. Estados de la interfaz (AdminWhatsApp)

| Estado | Qué se muestra |
|---|---|
| Cargando | "Preparando mensajes…" con `role="status"`. |
| Error de lectura (RF-WA-22) | "No se pudo preparar el mensaje. Inténtalo de nuevo." + botón "Reintentar" (`role="alert"`). Sin botón de WhatsApp. |
| 401 (RF-WA-31) | Redirección a `/admin/login` conservando `from` y el borrador en `sessionStorage`. Texto de §4.2. |
| `abierto=false` | Aviso de servicio cerrado (texto de §4.2). Sin tarjetas ni botones. |
| `aviso` de servicio | Texto de `aviso` con `role="status"`. Sin tarjetas. |
| Lista de tarjetas | Por tarjeta: etiqueta, estado, texto editable (`<input type="text">` una línea, nombre accesible "Mensaje para {etiqueta}"), botón "Abrir WhatsApp". Tarjeta "Cambio reciente" según D12. |
| Texto editado vacío (CL-09) | Mensaje aprobado junto al campo con `aria-describedby` y `aria-invalid`. No se abre WhatsApp. |
| Ventana bloqueada (RF-WA-23) | "El navegador bloqueó la ventana de WhatsApp. Permite las ventanas emergentes para este sitio y pulsa de nuevo el botón." El texto editado no se pierde. |
| Abierto correctamente | Aviso de RF-WA-18 (texto pendiente, A6). Sin estado de "enviado". |

Todos los avisos son texto (no color solo). Objetivos táctiles de 44 px. Foco visible. Sin desbordamiento horizontal a 375, 768 y 1280 px.

---

## 6. Estrategia de pruebas

**`django.test` (`backend/servicios/tests/test_whatsapp.py`), `manage.py test`:**

| Prueba | CA / CL | Qué prueba |
|---|---|---|
| `ValidarCelularTest` | CA-02, CL-01, CL-02 | Tabla de entradas válidas e inválidas del validador. |
| `SolicitudSinWhatsAppTest` | CA-02, RF-WA-03 | POST con número inválido o sin número → 400 con la clave `whatsapp`, y el conteo de `Cliente`, `Servicio` y `Componente` no cambia. |
| `NoSobrescribirTest` | CL-24, CA-23 | Cliente con número A; solicitud con B válido → queda A. Cliente sin número → se guarda B. |
| `ContenidoMensajeTest` | CA-12 | `construir_bloque_whatsapp` con un servicio que tiene `observaciones_internas`, un motivo de bloqueo, un nombre de usuario y el id numérico: el texto no contiene ninguno de esos valores. Se usa `SimpleTestCase` (sin base de datos). |
| `WhatsAppPermisosTest` | CA-14 | Sin autenticación, cliente sin rol administrativo y cuenta inactiva → rechazo sin datos. Administrativo → 200. |
| `WhatsAppSoloLecturaTest` | CA-15 | Antes y después de `GET`, el conteo de filas de `Servicio`, `Componente`, `Cotizacion`, `AprobacionServicio`, `HistorialServicio` y `HistorialComponente` no cambia. `POST` → 405. |
| `WhatsAppTrasRechazoTest` | CA-06 | Un cambio de estado rechazado (409 o transición no válida) y un cambio al mismo estado no modifican el historial y devuelven el mismo `texto` en la siguiente lectura. |

Las pruebas usan `APIClient` con `force_authenticate` (igual que `test_flujo_estados.py`).

**Verificación del resto en el navegador (MCP chrome-devtools):**
CA-01, CA-03, CA-04, CA-05, CA-07 a CA-11, CA-13, CA-16, CA-19 a CA-22. El número de prueba del usuario se introduce a mano en la prueba final y nunca se escribe en el código ni en los tests.

**Comandos de verificación general:** `python manage.py check`, `python manage.py makemigrations --check --dry-run` (debe salir sin cambios), `python manage.py test --noinput`, `npm run build`, `npm run lint`. Tras cada cambio de frontend, comprobación visual con MCP.

---

## 7. Orden de implementación (resumen; detalle en `tasks.md`)

1. Documentación prerrequisita (RF-WA-26).
2. Validador de celular.
3. Solicitud pública: campo obligatorio y no sobrescritura.
4. Módulo `mensajes.py` y variable de dominio.
5. Endpoint de lectura.
6. Capa de datos del frontend y campo de la solicitud.
7. Sección WhatsApp (tarjetas, editor, abrir, avisos, D12).
8. Sesión caducada y borrador.
9. Verificación manual con el número de prueba.
10. Registro en `MEMORY.md`.

---

## 8. Decisiones resueltas y puntos abiertos

**Resueltas por el usuario** (detalle normativo en spec §10.2):

- **A1 (opción a).** El botón del estado vigente se muestra siempre, con independencia del origen. Solo los cambios del administrativo desde el panel generan mensaje de evento. Implementado en D4 y D12.
- **A2.** Una aprobación registrada a mano genera el texto de `OPERARIO_TRABAJANDO` solo si cambia el estado del componente. Implementado en D12.
- **A3.** Componente sin referencia: `{componente}` muestra solo el tipo. Implementado en `etiqueta_componente` (§3).
- **A4.** Variable `SEGUIMIENTO_BASE_URL`. Implementada en D7 y §1.1.
- **A5.** Borrador en `sessionStorage`, borrado al cerrar la pestaña. Implementado en D9.
- **A7.** No se modifica la comparación de duplicados por WhatsApp. Pendiente futuro (D6, spec §12).

**Decisiones aprobadas:**

- **A6.** Los dos textos de interfaz de §4.2 están aprobados: el aviso de CL-09 y el aviso de RF-WA-18.
- **Etiqueta "Cambio reciente"** (D12). Texto aprobado.

---

## 9. Qué NO cambia (resumen explícito)

- Sin migraciones ni campos nuevos. Sin tablas nuevas. Sin historial de mensajes.
- Sin dependencias nuevas (ni en `requirements.txt` ni en `package.json`). `zoneinfo` no se usa todavía.
- Sin integración con la API de WhatsApp, sin credenciales, sin envío automático.
- Sin cambios en transiciones, catálogos de estados ni `acciones.py`.
- Sin cambios en la regla de visibilidad del seguimiento público (`visible_cliente`).
- Sin cambios en `normalizar_telefono` ni en su uso para el teléfono.
- Sin tests de frontend. Sin nuevas pruebas fuera de las seis de §6.
