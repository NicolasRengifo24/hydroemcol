# Tareas — specs/001-solicitud-banco-pruebas

> Reescrito tras la validación (`/sdd-validate`). `[x]` solo si el criterio se
> verificó en el código y los tests actuales. Las tareas antes marcadas como
> hechas se revalidaron una por una; las que no cumplían figuran pendientes.
>
> **Finalización 12/10/2026.** El reviewer validó RF por RF con veredicto
> `OK — spec 001 cumplida`, 0 RF incumplidos. T11, T12, T15, T19, T20, T23, T24,
> T25 y T26 se cerraron tras verificarse contra el código y los tests. La
> revisión móvil (T26) se hizo a 375px con Chrome DevTools MCP.

## Documentación

- [x] **T1. Actualizar plan y spec** — Hecho cuando: `plan.md` refleja RF-3 con migración, fotos en media local y RF-10.1/10.2 en §9; `spec.md §9` anota ambos.

## Backend

- [x] **T2. Validadores y reglas puras** (RF-8.1, RF-8.6) — Hecho cuando: `normalizar_correo`, `normalizar_telefono`, `estados_cerrados`, `tiene_solicitud_en_curso(hoy, ...)` existen, son puras y `test_t1_puras` pasa.
- [x] **T3. Serializer público base** (RF-2.2–RF-2.3, RF-4.2–RF-4.5, RF-5.1–RF-5.3) — Hecho cuando: valida contacto, 1..N componentes, campos opcionales y no pierde datos; `test_t2_serializer` pasa.
- [x] **T4. Vista + URL pública base** (RF-7.1, RF-9.1–RF-9.2) — Hecho cuando: `POST /api/solicitudes/` con `AllowAny`, `transaction.atomic`, genera `codigo` + `token_seguimiento` y responde `{codigo, enlace_seguimiento, servicio_id}`.
- [x] **T5. Contacto telefónico** (RF-2.1) — Hecho cuando: el serializer acepta `empresa` y `whatsapp`, los persiste en `Cliente` y exige al menos uno de (teléfono, whatsapp).
- [x] **T6. Topes de longitud** (RF-2.4, RF-4.1) — Hecho cuando: `descripcion_solicitud` y `descripcion` del componente se limitan a **500** caracteres validados server-side.
- [x] **T7. Preferencias de entrega** (RF-3.1–RF-3.3) — Hecho cuando: `Servicio` tiene 3 booleanos (`entregar_en_banco`, `avisar_para_coordinar`, `recoger`), migración `0004_preferencias_entrega` aplicada y el serializer las persiste (opcionales, combinables).
- [x] **T8. Tipo de servicio forzado** (RF-6.1) — Hecho cuando: la vista fuerza `tipo_servicio=PRUEBA` e ignora el valor enviado por el cliente.
- [x] **T9. Aviso de duplicados** (RF-8.2, RF-8.4, RF-8.5) — Hecho cuando: ante solicitud en curso responde `409 {requiere_confirmacion: true, detail genérico}`; acepta `confirmar`; `confirmar=true` crea, y sin confirmar/cancelar no crea.
- [x] **T10. Idempotencia** (RF-7.5) — Hecho cuando: la `Idempotency-Key` se persiste y un reintento con la misma clave devuelve el mismo payload sin crear otra solicitud.
- [x] **T11. Fotos** (RF-5.1–RF-5.4) — Hecho cuando: `MEDIA_URL`/`MEDIA_ROOT` configurados y media servida en dev; cada archivo válido se guarda con `default_storage.save` y crea `Fotografia` (`url=/media/...`, `tipo=RECEPCION`, `visible_cliente=False`); máx 5, formatos JPG/JPEG/PNG.
- [x] **T12. Tests backend de corrección** — Hecho cuando: `test_solicitudes_publicas.py` cubre T5–T11 (`test_preferencias_guardadas`, `test_tipo_servicio_prueba`, `test_duplicado_*`, `test_idempotencia_*`, `test_fotos_*`, topes 500) y pasa.

## Frontend

- [x] **T13. Capa API + util idempotencia** (RF-7.5-RF-7.6) — Hecho cuando: `services/api.ts`, `services/solicitudes.ts`, `utils/idempotency.ts` existen y compilan con `tsc -b`.
- [x] **T14. Formulario base funcional** (RF-1.1, RF-7.6, RF-9.1–RF-9.2, RNF-1) — Hecho cuando: contacto y componentes dinámicos, envío con botón deshabilitado mientras `isPending`, confirmación con código + enlace y sin desbordamiento a 375px.
- [x] **T15. Textos informativos** (RF-1.2, RF-9.3) — Hecho cuando: la página indica que no requiere cuenta y la confirmación dice que el enlace da acceso únicamente a esa solicitud.
- [x] **T16. Campo Empresa + WhatsApp** (RF-2.1) — Hecho cuando: el formulario incluye Empresa (opcional) y WhatsApp (alternativo al teléfono).
- [x] **T17. Topes y contador** (RF-2.4, RF-4.1) — Hecho cuando: ambas descripciones usan `maxLength=500` con contador (corregir el actual 255 del componente).
- [x] **T18. Preferencias de entrega** (RF-3.1) — Hecho cuando: 3 checkboxes (banco, coordinar, recoger) enviados con la solicitud.
- [x] **T19. Quitar componentes** (RF-4.4) — Hecho cuando: se puede quitar cualquier componente, incluido el primero, mientras quede al menos uno.
- [x] **T20. Subida de fotos** (RF-5.1–RF-5.4) — Hecho cuando: input múltiple `.jpg/.jpeg/.png`, máximo 5, thumbnails con eliminar y mensajes de error por formato/límite.
- [x] **T21. Quitar selector de tipo** (RF-6.1) — Hecho cuando: el formulario ya no pide tipo de servicio.
- [x] **T22. Aviso Continuar/Cancelar** (RF-8.2–RF-8.3) — Hecho cuando: ante duplicado se muestra un aviso genérico inline con **Continuar** y **Cancelar**; Cancelar conserva el formulario y no envía.
- [x] **T23. Confirmación con enlace** (RF-9.3) — Hecho cuando: la confirmación incluye botón "Copiar" y el texto de acceso privado.

## Verificación

- [x] **T24. Tests backend** — Hecho cuando: `manage.py test servicios.tests.test_solicitudes_publicas` pasa sin errores.
- [x] **T25. Estática** — Hecho cuando: `tsc -b`, `oxlint` y `manage.py check` sin incidencias.
- [x] **T26. Revisión móvil** — Hecho cuando: RF-1…RF-9 se recorren a 375px con Chrome DevTools MCP.

## Observaciones opcionales (no bloquean)

- Idempotency-Key solo en memoria (no persiste en recarga ni en otra pestaña); el 409 de duplicado evita el duplicado silencioso.
- RNF-5 se cumple dentro de la sesión; una recarga del navegador pierde el borrador.
- Faltan tests automáticos para multi-componente (RF-7.3), marca/referencia opcionales (RF-4.3) y estados ENTREGADO/CANCELADO (RF-8.3/8.6).
- `services/api.ts` no usa `VITE_API_URL` ni timeout (el plan §1 lo describía); en dev funciona por el proxy de Vite.
- Identificadores en inglés (`generateIdempotencyKey`, `ComponenteForm`, `idempotency_key`) frente al principio 6 de la constitución.
