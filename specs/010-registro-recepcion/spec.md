# Spec 010 — Registro de recepción del servicio

**Especificación funcional · Hidroemcol**
**Estado: implementada y verificada**

> Convención: `[PROPUESTA]` marca una decisión que este borrador propone y que aún no está
> confirmada por el negocio. `[SUPUESTO]` marca una consecuencia deducida de las decisiones
> cerradas. Las decisiones cerradas no llevan marca.

## 1. Contexto y objetivo

El modelo `Servicio` tiene el campo `fecha_recepcion` desde el inicio (002), pero ninguna acción
lo escribía: era de solo lectura en el admin de Django. El flujo registraba el avance a nivel de
componente (`EN_REVISION`, `COTIZANDO`, …), pero no existía un hecho explícito que marque la
llegada física de los componentes al almacén a nivel de servicio.

Esto deja dos huecos:

- `fecha_recepcion` nunca se llena, así que el dato no sirve.
- El cliente, en el seguimiento, no ve cuándo llegó su equipo, aunque la recepción es justamente
  el hecho que arranca el trabajo.

**Objetivo:** agregar una acción explícita del ADMINISTRATIVO, **"Registrar recepción"**, que
marque que los componentes llegaron al almacén, escriba `fecha_recepcion`, deje el hecho visible
al cliente y, si el servicio seguía `SOLICITADO`, lo pase a `EN_CURSO`.

**Por qué:** formaliza el punto de entrada del trabajo, completa un dato de negocio que ya existía
en el modelo y da al cliente una señal real de que su equipo está en manos de Hidroemcol.

## 2. Relación con especificaciones anteriores

- **Spec 008 (flujo de estados simplificado):** se **añade** una transición de servicio no listada
  en su §4.2. `SOLICITADO → EN_CURSO` deja de tener como único disparador "el primer componente
  sale de `PENDIENTE`": también lo produce el registro de recepción (RF-REC-03). No se supera
  ninguna cláusula de 008; la tabla de transiciones del servicio se **amplía**.
- **Spec 002 (backend):** `fecha_recepcion` deja de ser un campo sin acción asociada. Se respeta
  su definición de "Recepción física".

## 3. Usuarios

- **ADMINISTRATIVO:** único rol. Ejecuta "Registrar recepción".
- **Cliente final:** no ejecuta la acción. Ve la fecha de recepción y el comentario en su
  seguimiento con token.
- **Visitante sin datos:** sin acceso.

## 4. Glosario

- **Recepción:** hecho de que los componentes de un servicio llegaron al almacén de Hidroemcol.
- **Servicio en curso:** servicio en `SOLICITADO` o `EN_CURSO` (spec 008 §4).
- **Servicio cerrado:** servicio en `FINALIZADO` o `CANCELADO`; no admite la acción.
- **Comentario de recepción:** texto libre opcional que el administrativo registra con la
  recepción y que queda visible al cliente.

## 5. Requisitos funcionales (EARS)

### RF-REC-01 — Acción explícita del administrativo

**WHEN** el ADMINISTRATIVO registra la recepción de un servicio **THEN** el sistema DEBE escribir
`fecha_recepcion` con la fecha de la operación y DEBE registrar el hecho en `HistorialServicio`.

**AND** la recepción NUNCA DEBE registrarse automáticamente: es una acción explícita del
administrativo.

### RF-REC-02 — Comentario opcional y visibilidad

**WHEN** el administrativo registra la recepción **THEN** DEBE poder incluir un comentario de
texto libre **opcional**.

**AND** el comentario DEBE quedar registrado con `visible_cliente=True` en `HistorialServicio`,
para que el cliente lo lea en su seguimiento.

### RF-REC-03 — Efecto sobre el estado del servicio

**WHEN** el servicio está en `SOLICITADO` **THEN** el sistema DEBE pasarlo a `EN_CURSO` en la misma
operación y DEBE registrar ese cambio de estado.

**AND** **WHEN** el servicio ya está en `EN_CURSO` **THEN** la recepción DEBE registrarse sin
cambiar el estado del servicio.

### RF-REC-04 — Unicidad

**WHEN** se intenta registrar la recepción de un servicio que ya tiene `fecha_recepcion` **THEN**
el backend DEBE responder `409 Conflict` sin modificar datos.

### RF-REC-05 — Estados cerrados

**WHEN** el servicio está en `FINALIZADO` o `CANCELADO` **THEN** el backend DEBE rechazar la
recepción sin modificar datos (estado cerrado, spec 008 RF-FLU-11).

### RF-REC-06 — Acción disponible en el panel

**WHEN** el panel administrativo consulta un servicio **THEN** `acciones_disponibles` DEBE incluir
`registrar_recepcion` si y solo si el servicio no tiene `fecha_recepcion`.

**AND** la interfaz NO DEBE decidir la disponibilidad: solo presenta la acción que el backend
entrega (spec 008, RNF-FLU-01).

### RF-REC-07 — Presentación pública

**WHEN** el seguimiento público muestra un servicio **THEN** DEBE mostrar la fecha de recepción
cuando exista y DEBE incluir el comentario de recepción entre las actualizaciones visibles al
cliente.

**AND** el comentario de recepción DEBE entrar en la línea de tiempo por paso según el mapeo de
la spec 008 §4.3.

### RF-REC-08 — Trazabilidad y permisos

**WHEN** se registra la recepción **THEN** DEBE quedar en `HistorialServicio` con el estado
alcanzado, el usuario administrativo, la fecha y el comentario cuando aplique.

**AND** la acción DEBE exigir un ADMINISTRATIVO autenticado y activo (spec 008, RF-FLU-14).

### RF-REC-09 — Concurrencia

**WHEN** se registra la recepción **THEN** la operación DEBE ejecutarse en una transacción que
bloquee el servicio, consulte de nuevo `fecha_recepcion` y decida con el valor persistido.

**IF** otra operación ya registró la recepción **THEN** el backend DEBE responder `409 Conflict`
sin cambios parciales (spec 008, RF-FLU-13 y RNF-FLU-02).

## 6. Requisitos no funcionales (EARS)

#### RNF-REC-01 — Sin dependencias ni arquitectura nueva

La implementación DEBE operar con la arquitectura, las dependencias y la sesión aprobadas. La
verificación del backend se hace con `django.test` (`manage.py test`) y la del frontend con Chrome
DevTools MCP.

#### RNF-REC-02 — Idioma y feedback

Las etiquetas visibles DEBEN estar en español. La acción DEBE confirmar su resultado y ofrecer
recarga ante `409`.

## 7. Casos límite

- **CL-REC-01 — Servicio solicitado:** al registrar recepción, `fecha_recepcion` queda escrita y
  el servicio pasa a `EN_CURSO`.
- **CL-REC-02 — Servicio ya en curso:** al registrar recepción, `fecha_recepcion` queda escrita y
  el servicio conserva `EN_CURSO`.
- **CL-REC-03 — Recepción repetida:** un segundo intento responde `409` y no sobrescribe la
  recepción confirmada.
- **CL-REC-04 — Servicio cerrado:** registrar recepción en un servicio `FINALIZADO` o `CANCELADO`
  se rechaza sin modificar datos.
- **CL-REC-05 — Comentario vacío:** el administrador registra la recepción sin comentario; la
  operación es válida y `fecha_recepcion` queda escrita.
- **CL-REC-06 — Sin autenticación:** una petición sin ADMINISTRATIVO autenticado se rechaza.
- **CL-REC-07 — Disponibilidad:** cuando el servicio ya tiene `fecha_recepcion`,
  `registrar_recepcion` deja de aparecer en `acciones_disponibles`.

## 8. Criterios de aceptación

1. Existe una acción explícita "Registrar recepción" disponible solo mientras el servicio no tenga
   `fecha_recepcion`.
2. Registrar la recepción escribe `fecha_recepcion`, registra el hecho en `HistorialServicio` con
   usuario y fecha y, si el servicio estaba `SOLICITADO`, lo pasa a `EN_CURSO`.
3. La recepción repetida responde `409` sin sobrescribir; un servicio cerrado la rechaza sin
   cambios.
4. El comentario de recepción es opcional y, si existe, queda visible al cliente.
5. La acción exige un ADMINISTRATIVO autenticado y activo.
6. La verificación del backend se hace con `django.test` y la del frontend con Chrome DevTools MCP,
   sin dependencias nuevas.

## 9. Fuera de alcance

- Recepción a nivel de componente: la recepción es una sola por servicio.
- Edición o eliminación de una recepción ya registrada.
- Notificaciones automáticas al cliente por la recepción.
- Reapertura de servicios cerrados.

## 10. Trazabilidad de la implementación

- **Backend:** `registrar_recepcion()` en `servicios/acciones.py`; `RegistrarRecepcionInputSerializer`
  y `get_acciones_disponibles` en `servicios/serializers.py`; `RegistrarRecepcionView` en
  `servicios/views.py`; ruta `servicios/<int:servicio_pk>/recepcion/` (`name='servicio-recepcion'`)
  en `servicios/urls.py`.
- **Frontend:** `registrarRecepcion` en `services/api.ts`; mutación en `hooks/useAdministrativo.ts`;
  panel "Recepción" y fila "Recepción" en `pages/AdminServicioDetalle.tsx`.
- **Pruebas:** casos HTTP en `servicios/tests/test_flujo_estados.py` (fecha, transición,
  visibilidad pública, `409`, servicio en curso, permisos, disponibilidad). 91 tests OK.
