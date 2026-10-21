# Tareas — Spec 012: Notificaciones de estado por WhatsApp (mensajes preparados)

**Spec:** `specs/012-notificaciones-whatsapp/spec.md` (aprobada completa; textos de interfaz de §4.2 aprobados)
**Plan:** `specs/012-notificaciones-whatsapp/plan.md`
**Formato:** tareas en orden. Cada una lista archivos, criterio de hecho y cómo verificarla.
**Límite:** 10 tareas (plantilla sdd). Cada tarea agrupa un único cambio coherente; no se mezclan backend y frontend en la misma tarea salvo T6, que solo toca la capa de datos y el formulario.
**Pruebas:** solo `manage.py test` con `django.test` en CA-02, CA-06, CA-12, CA-14, CA-15 y CL-24. El resto se verifica con el MCP chrome-devtools.
**Bloqueos:** no quedan bloqueos de aprobación. Los textos de CL-09 y RF-WA-18, la etiqueta "Cambio reciente" y los demás textos de §4.2 están aprobados.

---

- [ ] **T1. Documentar el formato de mensajes en `CONTEXTO_MAESTRO.md` §43.** RF-WA-26, CA-17
  - Archivos: `CONTEXTO_MAESTRO.md` (MOD, sección "43. DECISIONES PENDIENTES", línea ~1225).
  - Qué hacer: quitar "Formato definitivo de mensajes de WhatsApp" de pendientes y añadir una nota que remita a `specs/012-notificaciones-whatsapp/spec.md` §4.1 como fuente de los textos aprobados. No copiar los textos.
  - Hecho cuando: §43 ya no lista el formato como pendiente y referencia la spec 012.
  - Cómo verificar: `grep` sobre `CONTEXTO_MAESTRO.md` (no debe aparecer "Formato definitivo de mensajes" como pendiente); revisión visual del bloque.

- [x] **T2. Validador de celular colombiano.** RF-WA-02, CA-02 (validador), CL-01, CL-02
  - Archivos: `backend/servicios/validators.py` (MOD). `normalizar_telefono` no cambia. `backend/servicios/tests/test_whatsapp.py` (NUEVO, con `ValidarCelularTest`).
  - Qué hacer: añadir `validar_celular_colombiano(valor) -> str | None` según plan §3 (quita espacios, guiones, paréntesis; quita `+57` o `57` cuando quedan 12 dígitos; exige 10 dígitos y primero `3`).
  - Hecho cuando: `ValidarCelularTest` pasa con: `3001234567`, `+57 300 123 4567` y `57-300-123-4567` → `3001234567`; `6011234567`, 9 dígitos, 11 dígitos y primer dígito distinto de 3 → `None`. Las pruebas de `normalizar_telefono` siguen en verde.
  - Cómo verificar: `python manage.py test servicios.tests.test_whatsapp servicios.tests.test_t1_puras --noinput`.

- [x] **T3. Solicitud pública: WhatsApp obligatorio y no sobrescritura.** RF-WA-01, RF-WA-03, RF-WA-04, CA-01, CA-02 (HTTP), CA-23, CL-22, CL-24
  - Archivos: `backend/servicios/serializers.py` (MOD, `SolicitudPublicaSerializer`, líneas ~759-803); `backend/servicios/views.py` (MOD, `SolicitudPublicaCreateView.post`, líneas ~858-892); `backend/servicios/tests/test_whatsapp.py` (MOD: `SolicitudSinWhatsAppTest`, `NoSobrescribirTest`); `backend/servicios/tests/test_t2_serializer.py`, `test_t3_view.py`, `test_solicitudes_publicas.py` (MOD: añadir `whatsapp` válido a los payloads que solo tienen `telefono`; la aserción de la línea ~109 pasa a la clave `whatsapp`).
  - Qué hacer:
    1. `whatsapp` pasa a obligatorio, con `error_messages` con los textos aprobados de §4.2 y `validate_whatsapp` que usa `validar_celular_colombiano`.
    2. `validate()` deja de exigir "teléfono o WhatsApp"; `telefono` queda opcional.
    3. Si el cliente existe por correo y `whatsapp` está vacío, guardar el número validado con `save(update_fields=['whatsapp'])` dentro de la transacción. Si ya tiene número, no tocarlo.
  - Hecho cuando: (a) una solicitud sin WhatsApp o con uno inválido responde 400 con clave `whatsapp` y no crea cliente, servicio ni componentes (`SolicitudSinWhatsAppTest`); (b) cliente con A + solicitud con B válido → queda A (`NoSobrescribirTest`, CL-24); (c) cliente sin número + solicitud con B → queda B; (d) `manage.py test --noinput` completo pasa.
  - Cómo verificar: `python manage.py test servicios.tests.test_whatsapp --noinput`; luego `python manage.py test --noinput`.

- [x] **T4. Módulo puro de mensajes y variable de dominio.** RF-WA-05, RF-WA-06, RF-WA-10 a RF-WA-13, RF-WA-29, CA-12
  - Archivos: `backend/servicios/mensajes.py` (NUEVO); `backend/config/settings.py` (MOD: `SEGUIMIENTO_BASE_URL = os.getenv('SEGUIMIENTO_BASE_URL', '')` junto a `CORS_ALLOWED_ORIGINS`); `backend/.env.example` (MOD); `backend/servicios/tests/test_whatsapp.py` (MOD: añadir `ContenidoMensajeTest`).
  - Qué hacer: implementar en `mensajes.py` las plantillas de plan §3 (solo SOLICITADO, EN_CURSO y los 8 estados de componente), `enlace_seguimiento`, `etiqueta_componente` (solo tipo si no hay referencia, A3), `texto_servicio`, `texto_componente` (RECHAZADO exige `motivo` no vacío) y `construir_bloque_whatsapp`. No importar Django ni modelos. Sin logs con texto (RNF-WA-04).
  - Hecho cuando: `ContenidoMensajeTest` (`SimpleTestCase`) prueba que, con un servicio con `observaciones_internas`, un motivo de bloqueo de una cotización, un nombre de usuario y el id numérico, ningún texto generado contiene esos valores; que el enlace es `base/seguimiento/token` y ninguno se genera con base vacía o sin `http(s)://`; que `{motivo}` aparece solo en RECHAZADO; y que los textos coinciden exactamente con spec §4.1.
  - Cómo verificar: `python manage.py test servicios.tests.test_whatsapp --noinput`.

- [x] **T5. Endpoint de lectura del texto preparado.** RF-WA-14, RF-WA-15 (datos), RF-WA-19, RF-WA-20, RF-WA-21, RF-WA-22 (causa del backend), RF-WA-28, RF-WA-29 (aviso), RF-WA-30, CA-06, CA-14, CA-15
  - Archivos: `backend/servicios/views.py` (MOD: nueva clase `ServicioWhatsAppView(APIView)` con `permission_classes = [EsAdministrativo]` y solo `get`, junto a `CambiarEstadoComponenteView`); `backend/servicios/urls.py` (MOD: `path('servicios/<int:servicio_pk>/whatsapp/', ServicioWhatsAppView.as_view(), name='servicio-whatsapp')`); `backend/servicios/tests/test_whatsapp.py` (MOD: `WhatsAppPermisosTest`, `WhatsAppSoloLecturaTest`, `WhatsAppTrasRechazoTest`).
   - Qué hacer: la vista obtiene el servicio (404 si no existe), sus componentes y el número del cliente (validado con `validar_celular_colombiano`), llama a `construir_bloque_whatsapp` y devuelve el contrato de plan §2. No escribe nada. Con servicio inactivo, cerrado o sin número, devuelve `mensajes: []` y el aviso correspondiente. Las tarjetas no incluyen IDs internos; sus claves usan tipo, estado y posición.
   - Hecho cuando: (a) sin autenticación, con cliente sin rol y con cuenta inactiva → rechazo sin datos (CA-14); (b) `GET` no altera ninguna fila de `Servicio`, `Componente`, `Cotizacion`, `AprobacionServicio`, `HistorialServicio` ni `HistorialComponente`, y `POST` responde 405 (CA-15); (c) tras un cambio rechazado (409 o transición no válida) y tras pedir el mismo estado, el historial no cambia y el `texto` de cada tarjeta es el mismo (CA-06); (d) la respuesta JSON completa no contiene claves `componente_id`, `servicio_id` ni `id`, valores numéricos de IDs internos, `observaciones_internas` ni nombres de usuario (CA-12, reforzado).
  - Cómo verificar: `python manage.py test servicios.tests.test_whatsapp --noinput`; con el backend local, `GET /api/servicios/<id>/whatsapp/` con sesión administrativa devuelve el JSON de plan §2.

- [x] **T6. Capa de datos del frontend y campo WhatsApp obligatorio en la solicitud.** RF-WA-01, RF-WA-02 (presentación), RF-WA-03, RF-WA-30; RNF-WA-03
  - Archivos: `frontend/src/services/api.ts` (MOD: tipos `MensajeWhatsApp` y `RespuestaWhatsApp`; `obtenerMensajesWhatsapp(servicioId)`; clave `whatsapp(id)` bajo `clavesAdministrativas.servicio`); `frontend/src/hooks/useAdministrativo.ts` (MOD: `useMensajesWhatsapp(id)`); `frontend/src/services/solicitudes.ts` (MOD: `whatsapp` obligatorio en el tipo y siempre enviado); `frontend/src/pages/SolicitarServicio.tsx` (MOD: `required` en el campo `f-whatsapp`; quitar el texto actual de la línea ~467 y poner la ayuda de §4.2; mostrar `errorCampos.whatsapp` que devuelve el backend).
  - Qué hacer: añadir solo la capa de datos y el formulario. **No añadir regex ni validación de número en el frontend**: el error viene del backend.
  - Hecho cuando: `npm run build` y `npm run lint` pasan sin errores ni warnings nuevos; el formulario no deja enviar sin WhatsApp (atributo `required`) y, con un número inválido, muestra el mensaje que devuelve el backend junto al campo.
  - Cómo verificar: `npm run build`, `npm run lint`; MCP en `localhost:5173/solicitar`: enviar con WhatsApp `6011234567` → aparece el mensaje del backend junto al campo; con `+57 300 123 4567` → el envío avanza. Comprobar en consola ausencia de errores y en 375/768/1280 px sin desplazamiento horizontal.

- [x] **T7. Sección WhatsApp del detalle: tarjetas, editor, abrir y avisos.** RF-WA-15, RF-WA-16, RF-WA-17, RF-WA-18, RF-WA-21, RF-WA-22, RF-WA-23, RF-WA-25; RNF-WA-05, RNF-WA-06; CA-07, CA-08, CA-09, CA-10, CA-11, CA-16; CL-08, CL-09, CL-10
  - Archivos: `frontend/src/services/whatsapp.ts` (NUEVO: `construirUrlWhatsApp`, `abrirWhatsApp`); `frontend/src/components/AdminWhatsApp.tsx` (NUEVO); `frontend/src/pages/AdminServicioDetalle.tsx` (MOD: solo montar `<AdminWhatsApp servicioId={id} />` después de la sección de Cotizaciones); `frontend/src/index.css` (MOD: estilos `.admin-whatsapp*`).
  - Qué hacer:
    1. `construirUrlWhatsApp` usa el número que devuelve el backend (`numero_destino`, ya con 57) y `encodeURIComponent(texto)`. El enlace se construye en el clic (RF-WA-17).
    2. `abrirWhatsApp` llama a `window.open(url, '_blank')` sin `await` antes; si devuelve `null`, retorna `false`; si no, asigna `win.opener = null` y retorna `true` (plan D5).
    3. `AdminWhatsApp` muestra una tarjeta por `mensajes`: etiqueta, estado, editor de una línea (`<input type="text">`, nombre accesible "Mensaje para {etiqueta}") y botón "Abrir WhatsApp". Si el texto editado está vacío, aviso junto al campo y no se abre (CL-09). Si `aviso` está presente, se muestra con `role="status"`. Si `texto` es `null`, no hay editor ni botón.
    4. Ventana bloqueada: mostrar el aviso de RF-WA-23 y conservar el texto editado.
    5. Tras abrir, mostrar el aviso de RF-WA-18 (sin "enviado").
    6. Error de lectura: mostrar "No se pudo preparar el mensaje. Inténtalo de nuevo." con botón "Reintentar" (RF-WA-22).
    7. Si el texto vigente cambia tras una recarga, el borrador de esa tarjeta se descarta (plan D11).
    8. Tras un cambio o una aprobación hechos desde el panel, marcar la tarjeta del estado de destino como "Cambio reciente" y enfocarla (plan D12). Un cambio automático, del cliente o desde Django Admin no marca nada. Una aprobación a mano marca `OPERARIO_TRABAJANDO` solo si cambió el estado del componente (A2).
  - Hecho cuando: en el MCP con el administrativo de prueba y un servicio abierto: (a) cada componente con estado con texto tiene su tarjeta, también si el cambio fue automático o del cliente (A1); (b) editar el texto y pulsar el botón abre una pestaña nueva con `wa.me/57…` y el texto editado legible con acentos y ñ (CA-07, CA-08, CL-10); (c) texto vacío → no abre y muestra el aviso (CA-10, caso vacío); (d) con la ventana bloqueada (desactivar popups en el perfil de prueba) → aparece el aviso de RF-WA-23 y el texto se conserva (CA-11); (e) servicio sin número → sin botón y con el aviso de §4.2 (CA-09); (f) error de red o 500 simulado → mensaje de RF-WA-22 y reintento sin abrir WhatsApp (CA-10); (g) foco visible, nombres accesibles y objetivos de 44 px; (h) sin errores de consola; (i) sin desplazamiento horizontal a 375, 768 y 1280 px; (j) el cambio hecho desde el panel marca la tarjeta "Cambio reciente" y uno automático no.
  - Cómo verificar: `npm run build`, `npm run lint`; MCP `localhost:5173/admin/servicios/<id>`. Usar un servicio de prueba y el administrativo de prueba. No usar datos de clientes reales.

- [x] **T8. Sesión caducada y conservación del borrador.** RF-WA-31, RF-WA-20 (frontend), CL-23, CA-22
  - Archivos: `frontend/src/components/AdminWhatsApp.tsx` (MOD: guardar el borrador en `sessionStorage` al cambiar el campo; recuperarlo al montar; redirigir con 401) y `frontend/src/pages/AdminLogin.tsx` (MOD: consumir y mostrar de forma segura el aviso esperado, conservando `from`). `frontend/src/components/RutaAdministrativaProtegida.tsx`: sin cambios.
  - Qué hacer: al recibir 401 tras un refresco fallido, navegar a `/admin/login` con `state: { from: location, aviso }` y mostrar el texto de §4.2. El borrador se guarda en `sessionStorage` con clave `hidroemcol.whatsapp.<servicioId>.<clave>` (decisión A5) y se borra solo cuando el texto vigente cambia o cuando se abre WhatsApp correctamente.
  - Hecho cuando: con sesión caducada (cierre de sesión desde otra pestaña o expiración del token de refresco), el panel lleva a `/admin/login` con el aviso; tras volver a entrar, el usuario regresa al mismo detalle y el texto editado sigue en el campo (CL-23, CA-22).
  - Cómo verificar: MCP: (1) editar un mensaje; (2) invalidar la sesión (`/api/logout/` desde otra pestaña o borrar la cookie de refresco); (3) pulsar "Abrir WhatsApp" o recargar la lectura → redirección a login con el aviso; (4) volver a entrar → el texto editado sigue en el campo; (5) sin errores de consola fuera del 401 esperado.

 - [x] **Corrección responsive final de T7/T8.** RF-WA-15, RNF-WA-05, CA-16
   - Archivos: `frontend/src/index.css`.
   - Qué hacer: evitar que los tracks y elementos administrativos con ancho intrínseco expandan `admin-shell` en tablet; conservar el scroll interno de tablas y la sección WhatsApp.
   - Hecho cuando: el detalle `/admin/servicios/118` no tiene desbordamiento horizontal y WhatsApp permanece visible en 375, 768 y 1280 px.
 - [ ] **T9. Verificación manual con el número de prueba.** Verificación final de RF-WA-05 a RF-WA-09, RF-WA-19, RF-WA-27, RF-WA-28, CA-03, CA-04, CA-05, CA-13, CA-19, CA-20, CA-21
  - Archivos: ninguno (solo verificación). Anotar resultados en el registro de la tarea T10.
  - Número de prueba: `<NUMERO_PRUEBA_USUARIO>` (placeholder; el número real lo introduce el usuario a mano en WhatsApp y **no se escribe** en código, tests ni documentación).
  - Qué hacer, con el backend local y el frontend en marcha, `SEGUIMIENTO_BASE_URL` configurado a un dominio de prueba y un servicio con cliente cuyo WhatsApp es `<NUMERO_PRUEBA_USUARIO>`:
    1. Cambio manual de componente desde el panel → la tarjeta del nuevo estado aparece con su texto exacto y "Cambio reciente" (CA-03, D12).
    2. Cambio de servicio a EN_CURSO por "Registrar recepción" → texto de EN_CURSO (CA-04).
    3. Crear cotización → tarjeta ESPERANDO_APROBACION; editar o rechazar la cotización → no aparece "Cambio reciente" ni texto nuevo (CA-05).
    4. El enlace del texto abre el seguimiento del mismo servicio con solo sus datos (CA-13).
    5. Servicio `FINALIZADO` o `CANCELADO` → aviso de §4.2 sin tarjetas ni botones (CA-04 cerrados).
    6. Respuesta del cliente desde el seguimiento y cambio desde Django Admin → sin "Cambio reciente"; la tarjeta del estado vigente sigue visible (CA-19, A1).
    7. Servicio desactivado → aviso de RF-WA-28 y sin botón (CA-20).
    8. Sin `SEGUIMIENTO_BASE_URL` → aviso de §4.2 en las tarjetas con `{enlace}` y las demás tarjetas siguen (CA-21).
    9. Verificar el mensaje recibido en WhatsApp real con el número de prueba (cliente no real).
  - Hecho cuando: los 9 casos anteriores están marcados como correctos en el registro de T10, o tienen una incidencia documentada.
  - Cómo verificar: MCP chrome-devtools para los casos 1 a 8; WhatsApp en el teléfono del usuario para el caso 9.

- [ ] **T10. Registro de decisiones en `MEMORY.md` y cierre.** RF-WA-26, CA-17
  - Archivos: `MEMORY.md` (MOD: entrada nueva al final de la bitácora y actualizar el gap de WhatsApp en §1/§2); `docs/deployment.md` (MOD: variable `SEGUIMIENTO_BASE_URL` documentada, si no se hizo en T4).
  - Texto a añadir en `MEMORY.md` (completar los campos entre corchetes al cerrar):

    > ### [FECHA] — Spec 012: notificaciones de estado por WhatsApp (mensajes preparados)
    >
    > - Mensajes preparados en el panel: el backend genera el texto con las plantillas de la spec §4.1 y el administrativo lo edita y abre `wa.me` en pestaña nueva. **Sin API de WhatsApp, sin credenciales, sin envío automático, sin migraciones y sin dependencias nuevas.**
    > - Endpoint nuevo de solo lectura: `GET /api/servicios/<id>/whatsapp/` (EsAdministrativo). No escribe datos.
    > - Número de WhatsApp obligatorio en la solicitud (supera la regla "teléfono o WhatsApp" de la 001 para este campo). Validador `validar_celular_colombiano` separado de `normalizar_telefono`. Cliente existente sin número: se guarda el de la solicitud; con número, nunca se sobrescribe (corrección en Django Admin).
    > - Variable `SEGUIMIENTO_BASE_URL` para el enlace de seguimiento. Sin valor, no se generan enlaces parciales.
     > - Decisiones A1 a A7 de la spec §10.2 (A1: botón del estado vigente siempre visible; A7: duplicados sin cambios). Textos de §4.2 aprobados.
    > - Verificación: `manage.py test --noinput` [N tests OK, incluidos los de `test_whatsapp.py`]; `npm run build` y `npm run lint` OK; MCP: [resultado de T7, T8 y T9]. Número de prueba no registrado aquí.
     > - Pendiente: [lo que quede abierto, por ejemplo el dominio de producción].

  - Hecho cuando: `MEMORY.md` tiene la entrada con las decisiones reales (no el texto de plantilla) y la sección de WhatsApp de §1/§2 ya no figura como "sin definir"; `docs/deployment.md` documenta la variable; `CONTEXTO_MAESTRO.md` §43 coincide con T1.
  - Cómo verificar: revisión de `MEMORY.md` y `git diff --stat` (solo deben aparecer los archivos de esta spec, los de backend/frontend listados en `plan.md` §1 y la documentación).
