# Tareas — Spec 006: Control de estados en el panel administrativo

**Spec:** `specs/006-control-estados-admin/spec.md` (aprobada)
**Plan:** `specs/006-control-estados-admin/plan.md` (aprobado)
**Formato:** una tarea a la vez, tests primero (en rojo), luego código; al terminar marca la tarea y detente.
**Límite:** 10 tareas; cada una ≤ 20-30 min.

---

- [x] **T1. Reglas puras de estados y ampliación de `construir_hoy`.** RF-EST-01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 13
  - En `backend/servicios/reglas.py`: `ESTADOS_SELECCIONABLES_COMPONENTE`, `ESTADOS_SERVICIO_NORMALES`, `ESTADOS_SERVICIO_CERRADOS`, `tiene_bloqueo_cotizacion`, `estados_componente_seleccionables`, `resolver_transicion_componente`, `estados_servicio_seleccionables`, `fecha_para_estado_servicio`, `puede_cancelar_servicio`, `resolver_transicion_servicio`; reescribir `puede_continuar` sobre `tiene_bloqueo_cotizacion`. En `serializers.py`, `construir_hoy` añade `'estado'` y `'activo'` del servicio.
  - Hecho cuando: `manage.py test servicios.tests.test_reglas` sigue en verde y existen pruebas puras nuevas en `test_estados_admin.py` que cubren seleccionables por estado, derivados rechazados, bloqueo pendiente/rechazada, `noop`, `PENDIENTE` tras iniciar (CL-03/04/05/13), servicio cerrado y cancelación sin comentario (CL-15/16/21) — todas en verde.

- [x] **T2. Acción `cambiar_estado_componente` y helper de inicio canónico.** RF-EST-03, 04, 05, 06, 07, 08
  - En `backend/servicios/acciones.py`: extraer `_aplicar_inicio_trabajo(componente)` y refactorizar `iniciar_trabajo` para usarlo; implementar `cambiar_estado_componente(*, servicio, componente_id, nuevo_estado, comentario, usuario)` con transacción, bloqueo de filas, reconstrucción de `hoy`, `resolver_transicion_componente`, no-op idempotente, ramas `pendiente`/`iniciar`/`finalizar`, `HistorialComponente` y `_historial_accion`; guard de servicio `FINALIZADO`/`ENTREGADO`/`CANCELADO` (CL-14).
  - Hecho cuando: pruebas nuevas demuestran que `EN_PROCESO` deja fase `DESMONTAJE_INICIADO`, `trabajo_iniciado=True`, fecha y historial; el bloqueo por cotización devuelve `409` sin cambios; `RECHAZADO_BLOQUEANTE` finaliza pero no pasa a `EN_PROCESO`; derivados y `PENDIENTE` tras iniciar se rechazan; y `iniciar_trabajo` previo sigue en verde.

- [x] **T3. Acciones de estado del servicio y cancelación.** RF-EST-09, 10, 11, 12, 13
  - En `backend/servicios/acciones.py`: implementar `cambiar_estado_servicio(*, servicio, destino, comentario, usuario)` (delega `FINALIZADO` en `finalizar_servicio` y `CANCELADO` en `cancelar_servicio`, aplica `fecha_para_estado_servicio`, escribe `HistorialServicio`, no borra fechas) y `cancelar_servicio(*, servicio, comentario, usuario)` (exige comentario, no toca `activo`, no finaliza componentes).
  - Hecho cuando: pruebas nuevas confirman que `ENTREGADO` escribe `fecha_entrega` y otros estados no escriben fecha; ninguna transición borra fechas previas; `FINALIZADO` exige todos los componentes y sin componentes se rechaza (CL-15); `CANCELADO` sin comentario se rechaza (CL-21), no cambia `activo` y no altera componentes.

- [x] **T4. Serializers administrativos del cambio de estado.** RF-EST-01, 03, 09, 12
  - En `backend/servicios/serializers.py`: `CambiarEstadoComponenteInputSerializer` (ChoiceField sobre `EstadoComponente` + `comentario` opcional) y `CambiarEstadoServicioInputSerializer` (ChoiceField sobre `EstadoServicio` + `comentario`); añadir `estados_seleccionables` a `ComponenteAdministrativoSerializer` y a `ServicioAdministrativoSerializer`; ampliar `acciones_disponibles` del servicio con `cancelar_servicio`.
  - Hecho cuando: pruebas de serializer verifican que `estados_seleccionables` del componente excluye derivados y, en `RECHAZADO_BLOQUEANTE`, solo ofrece finalizar; el del servicio devuelve los 9 estados normales y queda vacío si está cerrado/desactivado.

- [x] **T5. Vistas, rutas y exclusión de `CANCELADO`.** RF-EST-03, 04, 09, 12, 13
  - En `backend/servicios/views.py`: `CambiarEstadoComponenteView` (hereda `_AccionDeComponente`) y `CambiarEstadoServicioView` bajo `EsAdministrativo`, traduciendo `ErrorDeAccion` a `{'detail', **extra}` con su `codigo`; en `ServicioViewSet.get_queryset`, `DashboardAdministrativoView`, `SeguimientoView` y `SeguimientoAprobarView`, excluir `estado=CANCELADO`. En `urls.py`, registrar `servicios/<int:servicio_pk>/componentes/<int:componente_pk>/estado/` y `servicios/<int:servicio_pk>/estado/`.
  - Hecho cuando: pruebas de endpoint (con `force_authenticate`) confirman `200` en cambios válidos, `400` derivado, `409` conflicto/bloqueo, `404` componente ajeno (CL-08) y `401/403` sin permiso (RNF-EST-01); un servicio `CANCELADO` desaparece del listado, del dashboard y del seguimiento público.

- [x] **T6. Suite de acciones y endpoints de estados.** RF-EST-01..13, RNF-EST-01, 02, 03
  - Completar `backend/servicios/tests/test_estados_admin.py` con el resto de casos de §7 del plan: fechas del servicio, `FINALIZADO`/`CANCELADO`, servicio desactivado (CL-09), mismo estado (CL-13), corrección (CL-05), doble cierre → `409` (CL-07/12) e historial no eliminable.
  - Hecho cuando: `python manage.py test` completo pasa en verde y cada RF-EST tiene al menos una prueba asociada.

- [x] **T7. Frontend: API y hooks.** RF-EST-01..12, 14, 15, RNF-EST-05
  - En `frontend/src/services/api.ts`: `bootstrapSesion()` single-flight sobre `refrescarSesion()` (reintento único ante `401`, fallo a `anonima`), `cambiarEstadoComponente`/`cambiarEstadoServicio`, tipo `CodigoEstadoComponente` y campos `estados_seleccionables` en las interfaces administrativas. En `frontend/src/hooks/useAdministrativo.ts`: mutaciones nuevas reutilizando `opcionesMutacion`.
  - Hecho cuando: `npm run build` y `npm run lint` pasan; las mutaciones invalidan dashboard, listado y detalle (incluido `409`).

- [x] **T8. Guard de sesión con bootstrap.** RF-EST-14, 15
  - En `frontend/src/components/RutaAdministrativaProtegida.tsx`: disparar `bootstrapSesion()` una sola vez cuando el estado es `'anonima'`; mientras `'autenticando'`/bootstrap en curso mostrar carga con `role="status"`; redirigir a `/admin/login` solo tras terminar el intento, conservando `from`. El bootstrap no se ejecuta en rutas públicas.
  - Hecho cuando: recargar `/admin/servicios/:id` con sesión válida restaura el panel sin pasar por login ni pedir credenciales; sin refresh válido muestra carga y luego login; cargar una ruta pública no dispara ninguna petición de refresh.

- [x] **T9. UI de selectores de estado y estilos.** RF-EST-01, 09, 11, RNF-EST-04, 05
  - En `frontend/src/pages/AdminServicioDetalle.tsx`: selector de estado del servicio desde `estados_seleccionables` (con botón de guardado, `textarea` obligatorio al elegir `CANCELADO` y confirmación), selector de estado por componente desde su `estados_seleccionables`, motivo de bloqueo visible y feedback de éxito/error pidiendo recargar ante `409`. En `frontend/src/index.css`: estilos del selector, del comentario y del estado de carga del guard, con foco visible y responsive.
  - Hecho cuando: en navegador el administrativo cambia estados con etiquetas en español, el selector no ofrece derivados ni `FINALIZADO`/`CANCELADO` libres, cancelar exige comentario y el flujo funciona en móvil, tablet y escritorio sin scroll horizontal.

- [x] **T10. Verificación manual y bitácora.** RNF-EST-07
  - Con frontend y `manage.py runserver` levantados, verificar con MCP los flujos de §7-C del plan; actualizar `MEMORY.md` con el cierre de la spec 006.
  - Hecho cuando: la lista de verificación manual queda completa (sin errores en consola, sin parpadeo a login, fechas correctas, `409` manejado) y `MEMORY.md` registra la spec 006 implementada y validada.
  - Verificado en MCP el 2026-10-14: guard sin sesión (carga + reintento + redirección a login), selector de componente (solo estados válidos; `PENDIENTE` desaparece tras iniciar; queda `EN_PROCESO`/`Desmontaje iniciado` y registra historial), selector de servicio (transición a `EN_REVISION`), obligatoriedad del comentario al elegir `CANCELADO`, `409` con mensaje del backend y botón "Recargar detalle" en servicio cerrado, sin errores de consola y sin desborde propio a 375/768. Bug de bootstrap de sesión corregido en `api.ts` (ver `MEMORY.md`).
