# Plan de implementación — Spec 005 Panel administrativo completo

## Estado del plan

Plan técnico derivado de `specs/005-panel-administrativo/spec.md`, aprobada por el
usuario y el reviewer. Este documento no implementa código ni autoriza por sí mismo
la escritura de tests; describe incrementos pequeños, sus contratos y su verificación.

## Límites y decisiones que se mantienen

- Se conserva Django/DRF, React/TypeScript, React Router, TanStack Query y la sesión de
  la Spec 004. No se agregan dependencias, roles, Redis, WebSockets, Channels, SSE ni
  almacenamiento acoplado a un proveedor.
- El backend sigue siendo la autoridad para autorización, filtros, estados, totales,
  acciones, visibilidad y conflictos. El frontend no asigna estados directamente.
- `Cotizacion.canal` ya existe y se reutiliza con `WEB`/`WHATSAPP`; no se crea una
  migración para ese campo. Sí se planifican migraciones para `RegistroTecnico` y para
  `Cotizacion.reemplaza_a`.
- La información técnica será texto libre, uno-a-uno con `Servicio`, creada bajo
  demanda. No se introducen parámetros rígidos de banco de pruebas.
- El almacenamiento de fotografías se invoca mediante `servicios/almacenamiento.py`;
  el panel no conoce si la referencia termina en almacenamiento local o Cloudflare.
- Los estados se modifican exclusivamente mediante las acciones backend existentes o
  las nuevas acciones que reutilicen `reglas.py` y `acciones.py`. No habrá selector
  libre de estado en el panel.

## Incrementos dependientes

### I0 — Contrato y diagnóstico (antes de tocar código)

Revisar la spec aprobada, la sesión de la Spec 004 y los contratos actuales. Documentar
qué endpoints existentes se conservan, cuáles se restringen a edición limitada y cuáles
son nuevos. La decisión de implementación de cada mutación debe quedar trazable a RF y
no debe esconder cambios de modelo en serializers o vistas.

#### Trazabilidad de contratos y responsables

La autorización indicada abajo es parte del contrato: toda ruta administrativa exige
autenticación válida y el rol `ADMINISTRATIVO` en backend. La protección de la interfaz
no sustituye esta autorización. Las rutas públicas son las únicas excepciones y
continúan limitadas por token/`AllowAny` según su contrato actual.

| Ruta/operación | Estado en Spec 005 | Contrato que se reutiliza o agrega | RF/RNF | Responsable principal |
|---|---|---|---|---|
| `POST /api/login/`, `POST /api/refresh/`, `POST /api/logout/`, `GET /api/csrf/` | Reutilizada | Sesión de Spec 004: access en memoria, refresh en cookie httpOnly, CSRF, rotación/revocación y redirección al login ante 401 | RF-ADM-01, RNF-ADM-01–02 | `backend/usuarios/views.py`; `frontend/src/services/api.ts`, `context/*`, `components/RutaAdministrativaProtegida.tsx` |
| `GET /api/servicios/` | Reutilizada y restringida | Listado administrativo sobre el recurso existente; búsqueda/filtro/orden/paginación de 20 y sin token | RF-ADM-05–12, RNF-ADM-01–03 | `backend/servicios/views.py`, `serializers.py`, `urls.py`; `frontend/src/services/api.ts` |
| `GET /api/servicios/{id}/` | Reutilizada y ampliada | Detalle administrativo consolidado; verifica pertenencia de relaciones y no muestra el token completo | RF-ADM-04, 13–15, RNF-ADM-03 | `backend/servicios/views.py`, `serializers.py`; páginas/componentes de `frontend/src/` |
| `PATCH /api/servicios/{id}/` | Reutilizada y restringida | Solo `observaciones_internas`; rechaza datos de servicio o cliente no permitidos | RF-ADM-15A, 27, RNF-ADM-06 | `backend/servicios/acciones.py`, `serializers.py`, `views.py`; detalle administrativo |
| `GET/POST/PATCH/DELETE /api/servicios/{id}/componentes/` | Existente parcial; ampliar y restringir | GET/POST ya existen; PATCH/DELETE son operaciones nuevas. CRUD descriptivo con pertenencia comprobada; nunca acepta `estado`/`fase`; eliminación solo si no hay trazabilidad | RF-ADM-16–17, 21 | `backend/servicios/acciones.py`, `serializers.py`, `views.py`, `urls.py`; detalle administrativo |
| `GET/POST /api/servicios/{id}/historial/` | Reutilizada y restringida | Consulta ordenada; creación con actor válido; no se elimina historial | RF-ADM-27, 34 | `backend/servicios/views.py`, `serializers.py`; detalle administrativo |
| `POST /api/servicios/{id}/componentes/{id}/iniciar-trabajo/`, `/finalizar/`, `/corregir-finalizacion/`, `/api/servicios/{id}/finalizar/` | Reutilizada y restringida | Acciones existentes, sin estado directo, con reglas de Spec 002, transacción, conflicto 409 e historial | RF-ADM-18–21, RNF-ADM-06 | `backend/servicios/acciones.py`, `views.py`, `reglas.py`; detalle administrativo |
| `POST /api/cotizaciones/` y `PATCH /api/cotizaciones/{id}/` | Reutilizada y restringida | Crear con detalles y total validado; editar únicamente `PENDIENTE`; sin subtotal/impuestos/vencimiento ni borrado | RF-ADM-22–23, 26, RNF-ADM-06 | `backend/servicios/acciones.py`, `serializers.py`, `views.py`; formularios de cotización |
| `POST /api/cotizaciones/{id}/reenviar/` | Nueva | Crea versión `PENDIENTE`, número nuevo, mismo componente/tipo y `reemplaza_a`; no copia aprobaciones ni altera la anterior | RF-ADM-24, 26, RNF-ADM-06 | `backend/servicios/acciones.py`, `serializers.py`, `views.py`, `urls.py`; detalle de cotizaciones |
| `GET/POST /api/cotizaciones/{id}/aprobaciones/` | Reutilizada y restringida | Consulta autorizada y registro externo con medio cerrado, actor, fecha, observación e IP; actualiza mediante acción | RF-ADM-25–26, RNF-ADM-01, 06 | `backend/servicios/acciones.py`, `views.py`, `serializers.py`; aprobación externa |
| `GET/POST/PATCH /api/servicios/{id}/registro-tecnico/` | Nueva | Registro interno uno-a-uno, bajo demanda, cinco textos libres, autoría y fechas; nunca seguimiento público | RF-ADM-28–29, RNF-ADM-03, 06 | `backend/servicios/models.py`, `acciones.py`, `serializers.py`, `views.py`, `urls.py`; detalle técnico |
| `GET/POST/PATCH/DELETE /api/servicios/{id}/fotografias/` | Existente parcial; ampliar y restringir | GET/POST ya existen; PATCH/DELETE son operaciones nuevas. Máximo 10 por servicio, visibilidad separada y borrado mediante adaptador; verifica pertenencia | RF-ADM-30–32, RNF-ADM-03, 06–07 | `backend/servicios/almacenamiento.py`, `acciones.py`, `serializers.py`, `views.py`; fotografías |
| `GET /api/admin/dashboard/` | Nueva | Indicadores de activos, recientes exactos (10), pendientes y definición aplicada; nunca token completo ni desactivados | RF-ADM-05–07, RNF-ADM-01–03 | `backend/servicios/views.py`, `serializers.py`, `urls.py`; dashboard administrativo |
| `GET /api/seguimiento/{token}/`, `POST /api/seguimiento/{token}/aprobar/` | Pública existente, no administrativa | Permanece `AllowAny`, exige token privado, filtra visibilidad y `activo`; no sirve para datos internos del panel | RNF-ADM-03, RF-ADM-31, 33 | `backend/servicios/views.py`, `serializers.py`, `urls.py`; sin ampliación del panel |
| `POST /api/solicitudes/` | Pública existente, no administrativa | Se conserva el contrato público; límite de 5 fotos cuenta dentro del máximo total de 10 del servicio | RF-ADM-30, modelo y reglas de Spec 001 | `backend/servicios/views.py`, `serializers.py`, `almacenamiento.py` |

**Decisiones de modelo cerradas para esta trazabilidad:** `Cotizacion.canal` ya existe en
`backend/servicios/models.py`, usa el catálogo cerrado `WEB`/`WHATSAPP` de Spec 002 y se
reutiliza sin migración. Las únicas modificaciones de esquema autorizadas para T2 son
`RegistroTecnico` y la relación opcional `Cotizacion.reemplaza_a`, ambas mediante una
migración explícita sin datos históricos. No se permiten cambios implícitos en modelos,
serializers o vistas, ni campos para estados, origen de fotos, contadores o parámetros
rígidos de banco de pruebas.

**Estados:** no habrá selector libre de estados en frontend ni endpoint que acepte una
transición directa. Los estados solo cambian mediante las acciones de proceso autorizadas;
el backend vuelve a validar las reglas de Spec 002 y el panel muestra únicamente las
acciones devueltas por el backend. Cualquier ruta administrativa nueva deberá incorporarse
a esta tabla antes de implementarse y quedará protegida por el permiso administrativo.

### I1 — Modelo y migraciones

Incorporar `RegistroTecnico` opcional, uno-a-uno con `Servicio`, con los cinco textos,
autor de creación/actualización y fechas. Incorporar `Cotizacion.reemplaza_a` opcional,
auto-relacionado y consultable hacia antecedente y versiones posteriores. La migración
debe ser de esquema, sin crear registros técnicos históricos ni alterar cotizaciones
anteriores. `canal` no se migra.

### I2 — Núcleo puro, acciones y concurrencia

Extender las representaciones que alimentan `reglas.py` y mantener las decisiones puras
recibiendo `hoy` como parámetro; cualquier fecha usada por una regla o acción debe
recibirse como parámetro de tiempo cuando la operación lo necesite. Las acciones deben
validar dentro de una transacción y volver a leer tras bloquear la fila del servicio y
la entidad específica. Si la regla falla con el estado bloqueado, traducirlo a 409 sin
guardar cambios parciales. Las acciones relevantes deben producir historial automático,
excepto el borrado físico de una fotografía.

Pseudocódigo común de mutación:

```text
resolver servicio y entidad; comprobar que la entidad pertenece al servicio
iniciar transaction.atomic()
  bloquear servicio con select_for_update()
  bloquear entidad específica con select_for_update()
  volver a leer relaciones y estado persistido
  construir hoy y evaluar regla pura(hoy, ...)
  si la regla falla: lanzar conflicto 409 sin escribir
  aplicar cambio, actor y fecha recibidos
  crear historial si corresponde
  confirmar transacción
devolver representación actualizada
```

La implementación debe evitar depender de la instancia leída antes de la transacción,
especialmente para aprobar, reenviar o editar cotizaciones.

### I3 — API administrativa

Reutilizar ViewSets y vistas actuales cuando el contrato ya sea compatible, pero separar
serializers administrativos de representaciones públicas. Agregar dashboard, listado
con búsqueda/filtros/orden/paginación, detalle consolidado, RegistroTecnico, versionado
de cotizaciones y mutaciones protegidas. Todas las rutas administrativas deben exigir
autenticación válida y rol `ADMINISTRATIVO` mediante la configuración de permisos ya
aprobada por la Spec 004.

#### Contratos HTTP previstos

Los nombres son contractuales a nivel de comportamiento; se adaptarán a la convención
actual de `urls.py` sin crear una arquitectura paralela.

| Operación | Contrato de entrada | Respuesta y reglas |
|---|---|---|
| `GET /api/admin/dashboard/` | Sin cuerpo. | `total_activos`, contadores por los 11 estados oficiales, `recientes` exactos (10, `fecha_solicitud` descendente), `pendientes_atencion` y definición aplicada. Solo `activo=True`; nunca token completo. |
| `GET /api/servicios/` | `search`, `estado`, `page`, `page_size` fijado en 20, `ordering` dentro de una lista blanca. | Respuesta paginada con `count`, `next`, `previous`, `page`, `page_size`, `results`; búsqueda normalizada en backend sobre código, nombre, empresa y datos identificables autorizados. Predeterminado `-fecha_solicitud`. |
| `GET /api/servicios/{id}/` | Sin cuerpo. | Detalle administrativo consolidado: cliente, servicio, componentes con fase/bloqueo/acciones, cotizaciones y cadena, aprobaciones, historial, fotografías, `registro_tecnico` si existe, resumen de cierre y acciones disponibles. No expone token como texto. |
| `PATCH /api/servicios/{id}/` | Solo `observaciones_internas`. | Rechaza cualquier otro campo; responde servicio actualizado y crea historial/contexto cuando corresponda. |
| `POST/PATCH/DELETE /api/servicios/{id}/componentes/` | Campos descriptivos permitidos; las acciones son rutas separadas. | Valida pertenencia, conservación con trazabilidad y devuelve 409 en conflicto; nunca acepta `estado`/`fase` como transición libre. |
| `POST /api/servicios/{id}/componentes/{id}/iniciar-trabajo/` | Sin estado; actor de sesión. | Usa `iniciar_trabajo`, bloquea si existe cotización bloqueante pendiente/rechazada y registra historial de componente. |
| `POST .../finalizar/`, `POST .../corregir-finalizacion/`, `POST /api/servicios/{id}/finalizar/` | Motivo oficial o nuevo estado/comentario según acción. | Usa las acciones existentes, valida otra vez y devuelve detalle actualizado; el cierre de servicio es manual. |
| `POST /api/cotizaciones/` | Servicio, componente opcional para legado, tipo, bloqueante, descripción, observaciones y `detalles[]`. | Total calculado/validado en backend; cotización nueva con actor y número; no acepta subtotal, impuestos ni vencimiento. |
| `PATCH /api/cotizaciones/{id}/` | Solo cotización `PENDIENTE`; datos editables y detalles. | `APROBADA`/`RECHAZADA` son inmutables. La edición es atómica y no borra aprobaciones. |
| `POST /api/cotizaciones/{id}/reenviar/` | Nueva descripción/detalles/total conforme al contrato, sin aprobaciones. | Crea nueva versión `PENDIENTE`, mismo componente/tipo, número nuevo, `reemplaza_a` apuntando a la anterior; no altera la anterior. |
| `POST /api/cotizaciones/{id}/aprobaciones/` | `resultado`, `medio`, `fecha` opcional, `observacion`; IP del request. | Medios cerrados de `AprobacionServicio`; actor administrativo; actualiza cotización y componente mediante acción, no permite aprobar una versión ajena. |
| `GET/POST/PATCH /api/servicios/{id}/registro-tecnico/` | Los cinco textos libres; PATCH puede enviar cualquier subconjunto. | Crea bajo demanda, actualiza autor/fecha de última edición, uno-a-uno, interno y no visible en seguimiento. |
| `GET/POST/PATCH/DELETE /api/servicios/{id}/fotografias/` | Archivo/referencia mediante la interfaz de almacenamiento, descripción, tipo, `visible_cliente`. | Máximo 10 por servicio contando las públicas; 11 devuelve 409/validación y no crea registro. Borrado intenta archivo y referencia atómicamente según el adaptador; si falla el archivo, conserva registro. |

Los identificadores anidados siempre se verifican contra el servicio de la URL. Las
respuestas de error deben conservar `detail`, código de negocio y, para conflictos,
`409 Conflict` con indicación de recargar. Los listados no incluyen el token privado.

### I4 — Cliente API y consultas

Extender `frontend/src/services/api.ts` sin duplicar autenticación: el access token
permanece en memoria, refresh y CSRF siguen la Spec 004 y un 401 continúa delegando al
flujo existente. Definir tipos de respuesta, funciones de API y claves de TanStack Query
para dashboard, listado y detalle. Las mutaciones invalidan dashboard/listado/detalle
afectados y muestran el error del backend; un 409 invalida el detalle y pide recargar.

### I5 — Panel visual incremental

Sustituir el placeholder de `Admin.tsx` por un layout administrativo separado, con
navegación al dashboard/listado, logout y salida accesible para carga, vacío y error.
El listado usa tabla en escritorio y tarjetas en móvil; búsqueda/filtro/orden/página
son parámetros de URL o estado de consulta, no una copia manual de datos del servidor.
El dashboard muestra contadores calculados por backend, recientes y pendientes con
enlaces al detalle. No se mezclan componentes del sitio público ni se oculta seguridad
solo mediante CSS.

### I6 — Detalle y mutaciones

Implementar el detalle en secciones reutilizables: cliente, resumen, componentes,
cotizaciones/versiones, aprobaciones, historial, técnico y fotografías. Las acciones
se renderizan solo según la respuesta backend; no se infieren transiciones. Formularios
de cotización calculan una previsualización si se desea, pero el total oficial es el
que devuelve el servidor. Las aprobaciones externas muestran medio separado de
`Cotizacion.canal`.

### I7 — Evidencia y verificación

Completar límites de fotografías, visibilidad y borrado a través del almacenamiento
abstracto; integrar RegistroTecnico en el detalle. Verificar seguridad de rutas,
pertenencia, 409, no exposición del token y que el seguimiento público siga filtrando
fotografías/historial por visibilidad.

## Responsabilidades de archivos

### Backend

- `backend/servicios/models.py`: solo las adiciones de esquema de `RegistroTecnico` y
  `Cotizacion.reemplaza_a`, sus restricciones y relaciones; no duplicar `canal`.
- `backend/servicios/migrations/`: migración nueva dependiente de `0005`, con ambas
  adiciones, sin datos históricos generados. El nombre final lo decide Django.
- `backend/servicios/estados.py`: fuente única de catálogos; únicamente reutilizar o
  extender catálogos ya aprobados, sin estados nuevos de interfaz.
- `backend/servicios/reglas.py`: funciones puras para indicadores, bloqueo, cierre y
  disponibilidad; reciben snapshot `hoy` y tiempo explícito cuando proceda. No duplicar
  la excepción heredada de acceso a datos documentada en MEMORY.
- `backend/servicios/acciones.py`: mutaciones transaccionales, acciones de proceso,
  respuesta/versionado, técnica, observaciones y fotos; bloqueo de servicio + entidad,
  relectura, 409 e historial.
- `backend/servicios/serializers.py`: serializers administrativos separados de los
  públicos, validación de campos permitidos, total de detalles, cadena de versiones,
  acciones disponibles y omisión del token completo.
- `backend/servicios/views.py`: dashboard, filtros, búsqueda normalizada, paginación,
  ordenamiento, detalle y traducción HTTP de acciones/errores; no reglas duplicadas.
- `backend/servicios/urls.py`: rutas administrativas y anidadas, sin cambiar la ruta
  pública ni su contrato de visibilidad salvo lo estrictamente necesario para el límite
  de fotografías.
- `backend/servicios/almacenamiento.py`: operaciones abstractas de guardar/eliminar y
  manejo de fallo físico; ninguna vista conoce el proveedor.
- `backend/servicios/admin.py`: mantener coherencia con las acciones backend existentes;
  no convertir Django Admin en un segundo conjunto de reglas ni habilitar estados libres.

### Frontend

- `frontend/src/services/api.ts`: tipos y funciones HTTP administrativas, reutilizando
  sesión, CSRF, refresh y manejo de 401.
- `frontend/src/context/*` y `frontend/src/components/RutaAdministrativaProtegida.tsx`:
  conservar sesión y protección; solo ampliar logout/estado de carga si el contrato lo
  requiere.
- `frontend/src/router.tsx`: rutas internas de dashboard, servicios y detalle bajo la
  protección existente; no duplicar layout público.
- `frontend/src/pages/Admin.tsx` y páginas/componentes administrativos nuevos: composición
  de dashboard, listado y detalle, estados de UI y acciones.
- `frontend/src/index.css` y estilos administrativos acotados: responsive, foco,
  contraste, tabla/tarjetas y etiquetas industriales en español, sin reescribir el
  sitio público innecesariamente.
- `frontend/src/main.tsx`: reutilizar el `QueryClient` ya montado; no crear otro ni
  añadir una librería de estado.

## Decisiones justificadas y alternativas descartadas

1. **ViewSets/vistas existentes + endpoints anidados**, en vez de una API administrativa
   paralela o GraphQL: reduce cambios de contrato, conserva autorización DRF y encaja con
   `urls.py` actual.
2. **Snapshot `hoy` + reglas puras**, en vez de reglas en React o consultas dispersas:
   una misma decisión sirve para API, acciones y presentación; evita que la interfaz
   invente estados.
3. **`transaction.atomic()` + `select_for_update()`**, en vez de Redis, WebSockets o un
   campo de versión: satisface la política aprobada, no añade infraestructura y devuelve
   409 cuando el estado bloqueado invalida la operación.
4. **Auto-relación `reemplaza_a`**, en vez de sobrescribir cotizaciones o crear una tabla
   de versiones separada: conserva el modelo aprobado, permite cadena completa y deja
   aprobaciones por versión.
5. **RegistroTecnico uno-a-uno bajo demanda**, en vez de añadir textos a `Servicio` o
   crear parámetros rígidos: mantiene el modelo flexible y evita filas vacías históricas.
6. **TanStack Query**, en vez de duplicar servidor en `useState`: cachea e invalida por
   recurso y hace explícita la coherencia tras mutaciones.
7. **Tabla escritorio + tarjetas móvil**, en vez de tabla horizontal en todos los
   dispositivos: cumple la accesibilidad y el uso operativo responsive de la spec.

## Estrategia de verificación y tests

- Conforme a `docs/constitution.md`, primero se propone cada bloque de tests y se solicita
  autorización explícita antes de escribirlo. No se instala pytest, runner frontend ni
  dependencia nueva.
- Backend autorizado: tests con `django.test` ejecutados por `manage.py test`; cubrir
  permisos/rol, dashboard activo, búsqueda sin tildes, filtros, paginación 20,
  pertenencia, inmutabilidad/versionado, RegistroTecnico, máximo 10 fotos, visibilidad,
  acciones y respuestas 409. Las reglas nuevas se prueban además con snapshots `hoy`
  deterministas y tiempo inyectado.
- Frontend: `npm run build`, `npm run lint` y verificación manual responsive de login,
  dashboard, listado, detalle, estados de carga/vacío/error, expiración, mutaciones y
  409. No se instala runner.
- `node --test`: se reserva para helpers JavaScript puros que, si se crean y se autoriza
  su test, puedan ejecutarse sin bundler ni dependencias; no sustituye `manage.py test`
  ni obliga a crear una suite frontend. Si no existe un helper JS aislable, se documenta
  que no aplica.
- Verificación final: `manage.py check`, migraciones aplicadas en base de prueba,
  `manage.py test --noinput`, build/lint, revisión de rutas y `git diff --check`.

## Mapa RF/RNF por incremento

| Incremento | Cobertura principal |
|---|---|
| I0 | RF-ADM-01–04, RNF-ADM-01–03, RNF-ADM-07 |
| I1 | RF-ADM-24, RF-ADM-28–29, RF-ADM-30, RF-ADM-33–34; RNF-ADM-06 |
| I2 | RF-ADM-03, RF-ADM-15–21, RF-ADM-23–27, RF-ADM-29, RF-ADM-32; RNF-ADM-06 |
| I3 | RF-ADM-05–11, RF-ADM-13–15A, RF-ADM-22–27, RF-ADM-30–34; RNF-ADM-01–03, RNF-ADM-05–06 |
| I4 | RF-ADM-01–04, RF-ADM-07, RF-ADM-11, RF-ADM-21, RF-ADM-35–36; RNF-ADM-02–03 |
| I5 | RF-ADM-02, RF-ADM-05–12, RF-ADM-35–36; RNF-ADM-04–05 |
| I6 | RF-ADM-13–27, RF-ADM-35–36; RNF-ADM-04–06 |
| I7 | RF-ADM-28–34, RF-ADM-36; RNF-ADM-03–07 |
