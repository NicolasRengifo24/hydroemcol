# Tareas — specs/001-solicitud-banco-pruebas

- [x] **T1. Validadores y reglas puras** (RF-8.1, RF-8.6) - Hecho cuando: `normalizar_correo`, `normalizar_telefono`, `estados_cerrados`, `tiene_solicitud_en_curso(hoy, ...)` existen, son puras y sus tests unitarios pasan.
- [x] **T2. Serializer público de solicitud** (RF-2.1–RF-2.4, RF-3.3, RF-4.1–RF-4.5, RF-5.1–RF-5.3, RF-7.1–RF-7.5, RF-8.1–RF-8.6) — Hecho cuando: validaciones completas, duplicados (OR, genérico, tras validación), idempotencia y preservación de datos. Tests fallan primero (red).
- [x] **T3. Vista + URL pública** (RF-6.1, RF-7.1–RF-7.6, RF-8.1–RF-8.6, RF-9.1–RF-9.3) — Hecho cuando: `POST /api/solicitudes/` con `AllowAny`, `transaction.atomic`, manejo `Idempotency-Key`, flujo Continuar/Cancelar y respuesta con código + enlace `/seguimiento/<token>`.
- [x] **T4. Tests backend** (todos RF) - Hecho cuando: `manage.py test servicios.tests.test_solicitudes_publicas` pasa sin errores.
- [x] **T5. Capa API frontend + util idempotencia** (RF-7.5-RF-7.6) - Hecho cuando: `src/services/api.ts`, `src/services/solicitudes.ts`, `src/utils/idempotency.ts` compilan con `tsc -b`.
- [x] **T6. Hook + formulario SolicitarServicio** (RF-1.1–RF-1.2, RF-2–RF-5, RF-7–RF-9, RNF-1, RNF-2, RNF-5) — Hecho cuando: móvil-first, componentes dinámicos, hasta 5 fotos (JPG/JPEG/PNG), aviso genérico de duplicados (Continuar/Cancelar), botón deshabilitado mientras envía, confirmación con código+enlace+copiar. Revisado con `web-design` y `web-design-guidelines`.
- [x] **T7. Vite proxy + .env.example** (config desarrollo) — Hecho cuando: `vite.config.ts` con proxy `/api` → `http://127.0.0.1:8000` y `frontend/.env.example` con `VITE_API_URL=/api`.
- [x] **T8. Verificación final** — Hecho cuando: `tsc -b`, `oxlint`, `manage.py check` sin errores. Revisión móvil 375px con Chrome DevTools OK. RF-10.1 queda anotado (no implementado).




