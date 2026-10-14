# Tareas de implementación — Spec 005

Todas las tareas son incrementos de 20–30 minutos, en orden de dependencia. No
implementan esta fase ahora. Cada tarea debe detenerse si descubre una decisión no
aprobada y solicitar confirmación antes de ampliar el alcance. Los tests requieren la
autorización explícita indicada en `plan.md`.

## T1 — Preparar contrato y trazabilidad ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-01–04, RNF-ADM-01–03, RNF-ADM-07.

Revisar spec 005, spec 002, spec 004, sesión actual y endpoints existentes; registrar en
el cambio qué rutas se reutilizan, cuáles se limitan y cuáles se agregan. Confirmar que
`Cotizacion.canal` existente no genera migración y que no habrá selector libre de estados.

Resultado: la tabla de contratos, autorización y responsables quedó documentada en
`plan.md`. Se identificaron las rutas públicas existentes, las rutas administrativas que
se reutilizan/restringen y las nuevas rutas de dashboard, versionado y RegistroTecnico.
Las únicas adiciones de esquema autorizadas quedan explícitas para T2; `Cotizacion.canal`
se reutiliza sin migración y no se autoriza selector libre de estados.

**Hecho cuando:** existe una tabla de contratos y responsables de archivo en el plan; no
queda una modificación de modelo implícita ni una ruta administrativa sin autorización.

## T2 — Incorporar migraciones y modelos mínimos ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-24, RF-ADM-28–29, RF-ADM-30, RNF-ADM-06.

Añadir `RegistroTecnico` uno-a-uno opcional y `Cotizacion.reemplaza_a` opcional con
relaciones consultables. Generar una migración explícita dependiente de la última
migración existente; no crear registros históricos y no migrar `canal`.

**Hecho cuando:** `makemigrations --check` no propone cambios tras la migración, el
esquema conserva cotizaciones previas y se puede comprobar que no se generó ningún
RegistroTecnico automáticamente.

## T3 — Definir API de consulta y serializers administrativos ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-05–15A, RF-ADM-22, RF-ADM-26, RF-ADM-35; RNF-ADM-01, RNF-ADM-03, RNF-ADM-05.

Implementar el contrato de dashboard, listado paginado de 20 y detalle consolidado en
`serializers.py`, `views.py` y `urls.py`. La búsqueda debe normalizar mayúsculas/tildes
en backend; estado, orden y campos ordenables deben tener lista blanca. Incluir acciones
disponibles devueltas por backend, sin exponer token completo.

**Hecho cuando:** las respuestas tienen forma estable para dashboard/listado/detalle,
los desactivados quedan fuera del dashboard, y una consulta combinada de búsqueda,
estado, orden y página devuelve 20 elementos o el total restante.

Resultado: se agregaron los serializers administrativos de resumen, detalle, cotizaciones,
registro técnico, componentes y dashboard; `GET /api/admin/dashboard/` entrega indicadores
de servicios activos, recientes y pendientes; `GET /api/servicios/` aplica búsqueda sin
tildes, filtro de estado, ordenamiento con lista blanca y paginación fija de 20; y
`GET /api/servicios/{id}/` entrega el detalle consolidado sin exponer un campo de token.
Todas las rutas administrativas consultadas exigen usuario activo con rol
`ADMINISTRATIVO`. No se implementaron mutaciones de T4.

## T4 — Proteger acciones, cotizaciones y concurrencia ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-16–27, RF-ADM-36; RNF-ADM-06–07.

Extender `reglas.py`/`acciones.py` con snapshots `hoy` y tiempo explícito; conectar
iniciar trabajo, finalizar/corregir, cierre de servicio, respuesta externa, edición,
reenviar y aprobaciones. Cada mutación bloquea servicio y entidad específica dentro de
transacción, relee, valida y devuelve 409 si perdió vigencia. Registrar historial
automático salvo borrado físico de fotografía.

**Hecho cuando:** no existe mutación que acepte estado directo, una cotización respondida
es inmutable, reenviar crea cadena sin copiar aprobaciones y una simulación de conflicto
no sobrescribe ni deja cambios parciales.

Resultado: las acciones de proceso releen y bloquean servicio/componente dentro de
transacciones, las mutaciones administrativas exigen `ADMINISTRATIVO`, y los cambios de
estado ya no se aceptan como edición directa. Las cotizaciones pendientes se editan de
forma atómica; las respondidas son inmutables; el reenvío crea una versión pendiente con
número nuevo y `reemplaza_a`, sin copiar aprobaciones. Las aprobaciones externas separan
`medio` de `canal`, validan pertenencia y responden `409` ante conflictos o duplicados.
Se añadió historial automático para acciones y cambios administrativos; no se tocaron
RegistroTecnico ni el flujo completo de fotografías de T8.

## T5 — Completar cliente API y queries del panel ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-01–04, RF-ADM-07, RF-ADM-11, RF-ADM-21, RF-ADM-35–36; RNF-ADM-02–03.

Extender `frontend/src/services/api.ts` con tipos, llamadas y errores administrativos;
reutilizar access token en memoria, refresh, CSRF y logout de Spec 004. Crear claves de
TanStack Query para dashboard/listado/detalle y políticas de invalidación tras mutaciones.

**Hecho cuando:** una llamada administrativa usa la sesión existente, un 401 conduce al
login, un 409 invalida el recurso y solicita recarga, y no se persiste ningún token en
storage del navegador.

Resultado: `api.ts` conserva el cliente HTTP de Spec 004 y añade los tipos, consultas y
mutaciones administrativas. `useAdministrativo.ts` expone queries con claves estables y
mutaciones que invalidan dashboard, listado y detalle; los conflictos 409 quedan marcados
para solicitar recarga mediante `ErrorApi.requiereRecarga`. Se dejaron preparados los
contratos de RegistroTecnico y fotografías para los endpoints de T8, sin construir UI.

## T6 — Crear layout, dashboard y listado responsive ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-02, RF-ADM-05–12, RF-ADM-35–36; RNF-ADM-04–05.

Reemplazar el placeholder de `Admin.tsx`, añadir rutas/componentes administrativos y
construir navegación separada, contadores, recientes, pendientes, búsqueda, filtro,
orden y paginación. Usar tabla en escritorio y tarjetas en móvil; agregar estados de
carga, vacío y error accesibles.

**Hecho cuando:** dashboard y listado consumen servidor, muestran solo activos donde
corresponde, conservan filtros/página, funcionan sin scroll horizontal en móvil y cada
control tiene nombre/foco/feedback comprensible.

Resultado: `Admin.tsx` dejó de ser placeholder y ahora presenta el dashboard con indicadores,
recientes y pendientes provenientes de la API. Se añadió un layout administrativo separado,
logout, navegación protegida para `/admin` y `/admin/servicios`, y un listado responsive con
búsqueda, estado, orden whitelist y paginación URL de 20 registros. Se incluyeron estados de
carga, vacío, error y reintento accesibles, sin construir todavía el detalle ni sus mutaciones.

## T7 — Construir detalle y mutations operativas ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-13–27, RF-ADM-35–36; RNF-ADM-03–06.

Implementar detalle de servicio con cliente, componentes, estado/fase/bloqueo, acciones,
cotizaciones y cadena, aprobaciones, historial y seguimiento. Añadir formularios para
observaciones internas, componentes, cotización, respuesta externa, reenviar y acciones
de proceso; mostrar “En espera por cotización rechazada” sin crear estado nuevo.

**Hecho cuando:** el detalle no permite actuar sobre IDs de otro servicio, solo permite
editar cotizaciones pendientes, no ofrece selector de estado, confirma mutaciones con
datos recargados y comunica errores/409 sin fingir éxito.

Resultado: se añadió la ruta protegida `/admin/servicios/:id` con detalle responsive de
cliente, observaciones internas, componentes, cotizaciones/versiones, aprobaciones,
historial y seguimiento mediante copiar/abrir sin mostrar el token. Se conectaron las
mutaciones existentes para componentes, cotizaciones, respuestas externas y acciones de
proceso, con confirmaciones, invalidación/refetch y manejo explícito de errores y 409.
El registro técnico y las fotografías permanecen fuera de esta tarea para T8.

## T8 — Integrar RegistroTecnico y fotografías ✅ Completada (2026-10-13)

**RF/RNF:** RF-ADM-28–34, RF-ADM-36; RNF-ADM-03, RNF-ADM-06–07.

Conectar serializers/vistas/acciones y UI para RegistroTecnico bajo demanda y fotos:
cinco textos libres internos, autoría, fechas, visibilidad, tipos, máximo 10 contando
las cinco posibles del formulario público y borrado mediante almacenamiento abstracto.
Mantener el registro técnico al desactivar y filtrar fotos no visibles del seguimiento.

**Hecho cuando:** el registro técnico no aparece al cliente, se crea una sola vez y se
actualiza con último actor/fecha; la foto 11 se rechaza sin asociación, el fallo de
borrado físico conserva el registro y una referencia inexistente permite limpiar la
entidad según el contrato.

Resultado: se añadieron las mutaciones transaccionales y endpoints administrativos para el
RegistroTecnico y fotografías, con comprobación de pertenencia, límite de 10, carga mediante
el adaptador de almacenamiento, visibilidad pública filtrada y borrado físico seguro. El
detalle administrativo ahora incluye formularios accesibles de registro técnico y fotografías,
preview, edición, confirmación de borrado, estados de error/éxito y feedback del límite.

## T9 — Verificación autorizada y cierre de entrega ✅ Completada (2026-10-13)

**RF/RNF:** todos RF-ADM-01–36; RNF-ADM-01–07.

Solicitar autorización para escribir tests backend `django.test` y ejecutarlos con
`manage.py test --noinput`; cubrir permisos, normalización, paginación 20, migraciones,
versionado, acciones, 409, visibilidad y límite de fotos. Ejecutar build/lint/manual
responsive del frontend, y `node --test` solo si existe un helper JS puro aislable, sin
instalar runner. Revisar rutas, imports, contratos y diff.

**Hecho cuando:** `manage.py check`, tests autorizados, `npm run build`, `npm run lint`
y revisión manual pasan; se documentan explícitamente cualquier test no autorizado o
validación visual no disponible, sin declarar éxito no comprobado.

Resultado: se añadieron pruebas backend `django.test` para permisos, dashboard, búsqueda,
filtros, paginación, pertenencia, versionado, RegistroTecnico, fotografías, visibilidad,
acciones y conflictos. Se corrigió el bloqueo PostgreSQL de reenvíos con componente
opcional y se mantuvo el rechazo HTTP de mutaciones de estado directo. La suite completa
quedó en 273 tests verdes; `check`, `makemigrations --check`, build, lint y `git diff
--check` pasan. `node --test` no encontró pruebas JavaScript aplicables.
