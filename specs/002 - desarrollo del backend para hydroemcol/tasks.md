# Tareas — 002 - desarrollo del backend para hydroemcol

**Spec:** `specs/002 - desarrollo del backend para hydroemcol/spec.md` (Estado: aprobada)
**Plan:** `specs/002 - desarrollo del backend para hydroemcol/plan.md` (Estado: aprobado)

> Regla de `AGENTS.md` §11 y constitución principio 4: los tests se escriben **antes** del
> código, en rojo, y después se pasa a verde. Una tarea cada vez.

---

## Fase 1 — Catálogos de estado (sin base de datos)

- [x] **T1. Crear `servicios/estados.py` con los catálogos de estado del componente.**
  RF-COT-05, RF-COT-08, RF-COT-09
  - Añade `EstadoComponente` (`PENDIENTE`, `APROBADO`, `RECHAZADO`,
    `RECHAZADO_BLOQUEANTE`, `EN_PROCESO`, `FINALIZADO_POR_CLIENTE`,
    `FINALIZADO_POR_TECNICO`), `EstadoFaseComponente` (`RECIBIDO`,
    `DESMONTAJE_INICIADO`, `EN_EJECUCION`) y `CanalRespuesta` (`WEB`, `WHATSAPP`).
  - Define `ESTADOS_FINALIZACION` como la tupla de los dos estados de cierre.
  - No añadas dependencias ni lógica de negocio aquí: solo catálogos.
  - Hecho cuando: `python -c "from servicios.estados import ESTADOS_FINALIZACION"`
    no falla y `ESTADOS_FINALIZACION` contiene exactamente dos valores.
  - Verificado: 9 tests en `servicios/tests/test_estados.py` en verde con
    `manage.py test`; `ESTADOS_FINALIZACION` devuelve los dos estados de cierre.
    `servicios/tests.py` (stub vacío) se reemplazó por el paquete
    `servicios/tests/`.

- [x] **T2. Crear `servicios/reglas.py` con `tiene_trabajo_iniciado` y `puede_continuar`.**
  RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07
  - Ambas reciben `hoy` como primer parámetro y devuelven un valor.
  - Sin acceso a base de datos, sin `timezone.now()`, sin consultas.
  - Hecho cuando: se importan sin error y no contienen `objects` ni `timezone`.
  - Verificado: 17 tests de estas dos funciones en `servicios/tests/test_reglas.py`
    en verde con `manage.py test servicios` (26 tests en total). Sin coincidencias
    de `objects`, `timezone`, `save` ni `transaction` en `reglas.py`.

- [x] **T3. Añadir a `reglas.py` `estado_por_rechazo_bloqueante` y `motivo_bloqueo`.**
  RF-COT-04, RF-COT-05, RF-COT-06
  - `estado_por_rechazo_bloqueante` devuelve el estado o `None`.
  - `motivo_bloqueo` devuelve el texto en español o `None`.
  - Hecho cuando: ambas importan y devuelven `None` con un componente sin cotizaciones.
  - Verificado: 13 tests nuevos en `servicios/tests/test_reglas.py`
    (`TestEstadoPorRechazoBloqueante`, `TestMotivoBloqueo`), 39 en verde con
    `manage.py test servicios`. Sin cotizaciones ambas devuelven `None`. Helpers
    privados `_bloqueantes` y `_tiene_bloqueante_en`; el rechazo bloqueante tiene
    prioridad sobre la pendiente. Sin `objects`, `timezone`, `save` ni
    `transaction`.

- [x] **T4. Añadir a `reglas.py` `componentes_no_finalizados` y `todos_rechazan_bloqueantes`.**
  RF-COT-11, RF-COT-12
  - `todos_rechazan_bloqueantes` devuelve `False` si no hay cotizaciones bloqueantes.
  - Hecho cuando: `todos_rechazan_bloqueantes({'cotizaciones': []})` es `False`.
  - Verificado: 15 tests nuevos (`TestComponentesNoFinalizados`,
    `TestTodosRechazanBloqueantes`), 54 en verde con `manage.py test servicios`.
    `todos_rechazan_bloqueantes({'cotizaciones': []})` devuelve `False`. El helper
    `hoy()` de los tests ahora expone también `cotizaciones` en plano, que es la
    lectura que hace esta regla.
  - Nota: `rechazado_bloqueante` cuenta como **no finalizado** (glosario 4.8),
    por lo que un componente detenido por rechazo debe cerrarse explícitamente.

- [x] **T5. Añadir a `reglas.py` `puede_finalizar_servicio` y `resumen_cierre`.**
  RF-COT-11, RF-COT-12
  - `resumen_cierre` devuelve `puede_finalizar`, `caso` y `detalle` en español.
  - Ninguna función del archivo finaliza nada: solo habilita.
  - Hecho cuando: `puede_finalizar_servicio` es `True` con todos los componentes
    finalizados y `False` con una cotización bloqueante pendiente.
  - Verificado: 15 tests nuevos (`TestPuedeFinalizarServicio`, `TestResumenCierre`),
    69 en verde con `manage.py test servicios`. Ninguna función escribe ni consulta
    la base de datos.
  - **Decisión del usuario durante esta tarea:** el cierre exige que **todos** los
    componentes estén finalizados (literal de RF-COT-11 y RF-COT-13). Por eso el
    caso 2 de RF-COT-11 es el *motivo* del cierre y no una condición que lo
    habilite por sí sola. Se corrigieron `CL-02`, `CL-07`, la nota de
    interpretación de RF-COT-11, el pseudocódigo §2.6 y §2.8 del plan, la decisión
    D-8 y la tabla de tests §6.1, que expresaban la regla anterior.
  - `puede_finalizar_servicio` tiene un único criterio (`componentes_no_finalizados
    == []`); `resumen_cierre` distingue los motivos que ve el administrativo.

## Fase 2 — Tests de las funciones puras

- [x] **T6. Crear `servicios/tests/__init__.py` y `servicios/tests/test_reglas.py` con la batería de §6.1 del plan.**
  RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07, RF-COT-11, RF-COT-12
  - Los 18 tests listados en el plan, cubriendo CL-01, CL-03, CL-04, CL-05, CL-07, CL-10.
  - Hecho cuando: el archivo existe con los 18 tests.
  - Verificado: el archivo se fue escribiendo test-first durante T2 a T5 y quedó en
    **64 tests**, agrupados en `TestTieneTrabajoIniciado`, `TestPuedeContinuar`,
    `TestEstadoPorRechazoBloqueante`, `TestMotivoBloqueo`,
    `TestComponentesNoFinalizados`, `TestTodosRechazanBloqueantes`,
    `TestPuedeFinalizarServicio` y `TestResumenCierre`.
  - Los 19 tests de la tabla §6.1 del plan están cubiertos, más los RF y casos
    límite que faltaban. `CL-05` (una cotización `no_bloqueante` rechazada puede
    llegar a `finalizado_por_cliente` o `finalizado_por_tecnico`) no se prueba aquí
    porque no es una decisión de `reglas.py`: corresponde a `test_api.py` (T22).
  - Nombres propios de los tests: se verifies el comportamiento del RF, no el nombre
    literal de la tabla, que cambió al corregirse la regla de cierre.

- [x] **T7. Ejecutar la batería de reglas y confirmar que pasa.**
  RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07, RF-COT-11, RF-COT-12
  - Hecho cuando: `python manage.py test servicios.tests.test_reglas` reporta OK.
  - Si algún test falla, el fallo está en las reglas de `reglas.py`, no en el test.
  - Verificado: `manage.py test servicios.tests.test_reglas` → **OK, 64 tests**.
    Suite completa `manage.py test` → **OK, 73 tests**. `manage.py check` sin
    incidencias. Ningún test necesita base de datos (`SimpleTestCase`).

**Nota de las fases 1 y 2:** dos tests fallaron durante la redacción y ambos eran
tests mal planteados, no fallos de `reglas.py`: uno construía un componente en
`rechazado_bloqueante` sin cotización (estado imposible) y otro pedía que una
cotización pendiente bloquease un cierre cuyo único obstáculo real era otro
componente sin finalizar.

## Fase 3 — Modelos y migración

- [x] **T8. Añadir `EstadoComponente` y los campos del componente a `models.py`.**
  RF-COT-05, RF-COT-08, RF-COT-09
  - A `Componente`: `estado` (default `PENDIENTE`), `fase`, `trabajo_iniciado`,
    `fecha_inicio_trabajo`, `fecha_finalizacion`, `motivo_finalizacion`.
  - Reutiliza los catálogos de `estados.py`; no redeclares laschoices en `models.py`.
  - Hecho cuando: `python manage.py makemigrations --dry-run` no reporta cambios
    pendientes distintos de los de `Componente`.
  - Verificado: los seis campos añadidos; `estado` y `fase` toman sus `choices` de
    `estados.py` y `motivo_finalizacion` se limita a los dos estados de
    finalización (verificado en `test_modelos.py`).

- [x] **T9. Añadir `HistorialComponente` a `models.py`.**
  RF-COT-10
  - Campos: `componente`, `estado_anterior`, `estado_nuevo`, `fase_registrada`,
    `usuario`, `fecha`, `comentario`.
  - Permite registrar tanto las fases (RF-COT-08) como las correcciones (RF-COT-10).
  - Hecho cuando: `python manage.py check` no reporta errores.
  - Verificado: `componente` con `on_delete=CASCADE` (el rastro es del ciclo de
    vida del componente; el histórico que sobrevive al servicio es
    `HistorialServicio`), `usuario` con `SET_NULL` para que un cambio sin actor
    identificado no rompa el registro.

- [x] **T10. Añadir a `Cotizacion` los campos `componente`, `es_bloqueante` y `canal`.**
  RF-COT-01, RF-COT-02, RF-COT-03
  - `componente`: FK nulable a `Componente`, `on_delete=CASCADE`.
  - `es_bloqueante`: `BooleanField(default=False)`.
  - `canal`: `CharField` con `CanalRespuesta`, anulable y en blanco.
  - Hecho cuando: los tres campos existen y las cotizaciones existentes siguen siendo
    legibles con `es_bloqueante=False` y `componente=None`.
  - Verificado: los tres campos con esos valores por defecto; `canal` nace en `''`
    porque es `blank=True` y el modelo hereda el `''` de los demás campos de texto
    opcionales del proyecto.

- [x] **T11. Generar la migración y aplicarla en la base de datos de desarrollo.**
  RF-COT-01, RF-COT-02, RF-COT-03
  - Hecho cuando: `python manage.py makemigrations servicios` crea un único archivo
    nuevo y `python manage.py migrate` termina sin errores.
  - Si Django genera más de un archivo, para y avisa antes de aplicarlos.
  - Verificado: un único archivo,
    `servicios/migrations/0003_componente_por_cotizacion.py`, con 9 operaciones
    aditivas (todas con default o nulas, sin tocar datos existentes). Aplicada con
    `manage.py migrate servicios` → `OK` en el PostgreSQL local `hydroemcol`.
    `makemigrations --check --dry-run` → `No changes detected`.

- [x] **T12. Crear `servicios/tests/test_modelos.py` con la batería de §6.2 del plan.**
  RF-COT-02, RF-COT-08, RF-COT-09, RF-COT-14
  - Los 5 tests listados en el plan.
  - Hecho cuando: el archivo existe y `python manage.py test servicios.tests.test_modelos`
    reporta OK.
  - Verificado: escrito antes de los modelos (rojo por `ImportError`), **21 tests**,
    los 5 de §6.2 más los que exigían `HistorialComponente` y las `choices` de T8.
  - `manage.py test servicios` → **OK, 94 tests**.

**Notas de la fase 3:**

- **Base de datos de test:** `hydroemcol_user` no tiene `CREATEDB`, así que Django no puede
  crear `test_hydroemcol` y los `TestCase` fallaban con *se ha denegado el permiso para crear
  la base de datos*. Decisión del usuario: ejecutar los tests con `DATABASE_URL` apuntando a un
  SQLite temporal, sin tocar `config/settings.py`. Consecuencia asumida: los tests de modelo no
  verifican el comportamiento de PostgreSQL. Para volver a probar sobre PostgreSQL hace falta
  una base de test dedicada o darle `CREATEDB` al usuario.
- Un test falló al redactarlo y era del test: `test_el_historial_sobrevive_al_componente` pedía
  que el historial sobreviviera al componente, pero el modelo lo borra en cascada a propósito.
  Reescrito como `test_el_historial_se_borra_con_el_componente`.

## Fase 4 — Serializers

- [x] **T13. Exponer los campos nuevos en `ComponenteSerializer` y `CotizacionSerializer`.**
  RF-COT-01, RF-COT-02
  - Componente: `estado`, `fase`, `trabajo_iniciado`, `fecha_finalizacion`,
    `motivo_finalizacion`.
  - Cotización: `componente`, `es_bloqueante`, `canal`.
  - `estado`, `fase`, `trabajo_iniciado`, `es_bloqueante` y `canal` son de solo lectura
    en escritura: los cambia el backend, no el cliente.
  - Hecho cuando: los serializers devuelven los campos y no aceptan escribirlos.
  - Verificado: los campos aparecen en la respuesta y todos están en
    `read_only_fields`. Comprobado con tests que un `PATCH` con `estado`,
    `trabajo_iniciado`, `motivo_finalizacion`, `es_bloqueante` o `canal` no cambia
    el valor guardado.

- [x] **T14. Añadir los campos calculados `puede_continuar` y `motivo_bloqueo`.**
  RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-13
  - Se calculan con `reglas.py` a partir del servicio ya serializado.
  - Solo lectura. El frontend no replica la regla (constitución principio 3).
  - Hecho cuando: ambos aparecen en la respuesta del serializer.
  - Verificado: ambos en `ComponenteSerializer`, calculados con `reglas.py`. Se
    añadió `construir_hoy(servicio)` en `serializers.py` como **único** punto que
    traduce modelos a las llaves que esperan las reglas, para que `reglas.py`
    siga sin tocar la base de datos.

- [x] **T15. Añadir el campo calculado `resumen_cierre` en `ServicioSerializer`.**
  RF-COT-11, RF-COT-12
  - Devuelve `puede_finalizar`, `caso` y `detalle`.
  - Solo lectura. No añade ninguna acción de finalizar al serializer.
  - Hecho cuando: aparece en la respuesta del serializer.
  - Verificado: `resumen_cierre` en la respuesta con las tres claves, en
    `read_only_fields`, y sin ninguna acción de cierre en el serializer.

**Notas de la fase 4:**

- **`views.py` y `urls.py` siguen sin tocar.** Es lo esperado: en esta fase solo se
  añaden campos a la respuesta de los serializers existentes.
- **Se evitó una regresión en el endpoint público.** `ServicioPublicoSerializer`
  anidaba `ComponenteSerializer`, así que al añadirle campos internos el
  seguimiento del cliente habría empezado a ver `estado`, `trabajo_iniciado` y
  los calculados. Se creó `ComponentePublicoSerializer` con los campos que el
  público tenía antes, de modo que **el contrato público no cambia**, y se añadió
  `TestElPublicoNoVeCamposInternos` para que no vuelva a ocurrir al añadir campos.
  **Decidido:** el cliente **sí** ve el estado y la fase de su componente, como
  etiqueta en español (**RF-COT-15**). Los campos de control interno
  (`trabajo_iniciado`, `puede_continuar`, `motivo_bloqueo`, etc.) siguen
  ocultos. Implementado en `ComponentePublicoSerializer`.
- Un test falló al redactarlo y era del test: pedía que un servicio **sin**
  componentes no se pudiera cerrar. El "por qué" de RF-COT-11 dice que el servicio
  se cierra cuando no queda nada que ejecutar, y con cero componentes eso se
  cumple. Reescrito como `test_sin_componentes_queda_nada_por_ejecutar`.
- Tests: `manage.py test` → **OK, 121 tests** (94 + 27 de serializers).
  `manage.py check` sin incidencias y `makemigrations --check` sin cambios.

## Fase 5 — Vistas y rutas

- [x] **T16. Añadir la vista para registrar la respuesta del cliente a una cotización.**
  RF-COT-03, RF-COT-05, RF-COT-06, RF-COT-13
  - Recibe `componente_id`, `cotizacion_id`, `resultado` y `canal`.
  - Valida que la cotización pertenezca al componente y que esté `PENDIENTE`.
  - Crea la `AprobacionServicio` con `usuario_registro` y `fecha`.
  - Actualiza la cotización y, si aplica, marca el componente
    `RECHAZADO_BLOQUEANTE`. **Nunca toca el estado del servicio.**
  - Registra la fase o el cambio de estado en `HistorialComponente`.
  - Hecho cuando: rechaza con 400 la cotización ajena y la ya respondida.

- [x] **T17. Añadir la vista para registrar el inicio de trabajo (desmontaje).**
  RF-COT-04, RF-COT-08
  - Responde 409 con `motivo_bloqueo` si `puede_continuar` es falso.
  - Marca `trabajo_iniciado`, `fecha_inicio_trabajo` y `fase=DESMONTAJE_INICIADO`.
  - Hecho cuando: el componente bloqueado devuelve 409 y el permitido registra la fase.

- [x] **T18. Añadir la vista para finalizar un componente.**
  RF-COT-09
  - Exige `motivo` de tipo `FINALIZADO_POR_CLIENTE` o `FINALIZADO_POR_TECNICO`.
  - Responde 409 si ya está finalizado.
  - No exige que el componente pueda continuar: un `RECHAZADO_BLOQUEANTE` se puede
    finalizar.
  - Hecho cuando: guarda motivo y fecha, y rechaza el doble cierre.

- [x] **T19. Añadir la vista para corregir un estado de finalización.**
  RF-COT-10
  - Responde 409 si el estado actual no es de finalización.
  - Registra `estado_anterior`, `estado_nuevo`, `usuario` y `fecha` en el historial.
  - Hecho cuando: el historial conserva el estado anterior.

- [x] **T20. Añadir la vista para finalizar el servicio.**
  RF-COT-11, RF-COT-12
  - Es **manual**: solo se ejecuta cuando el administrativo la llama.
  - Responde 409 con `resumen_cierre` si `puede_finalizar` es falso.
  - Pone el servicio en `FINALIZADO` y escribe en `HistorialServicio` con
    `visible_cliente=False`.
  - No hay ninguna ruta ni tarea que finalice el servicio de forma automática.
  - Hecho cuando: los dos casos válidos devuelven 200 y el resto devuelve 409.

- [x] **T21. Registrar las rutas nuevas en `servicios/urls.py`.**
  RF-COT-03, RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11
  - Cinco rutas bajo `/api/`, siguiendo el patrón anidado que ya usa el archivo.
  - Todas bajo el permiso global `IsAuthenticated`.
  - Hecho cuando: `python manage.py check` no reporta errores y las rutas responden.

- [x] **T22. Crear `servicios/tests/test_api.py` con la batería de §6.3 del plan.**
  RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11, RF-COT-12, RF-COT-13
  - Los 26 tests listados en el plan.
  - Hecho cuando: el archivo existe con los 26 tests.

- [x] **T23. Ejecutar la batería de API y confirmar que pasa.**
  RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11
  - Hecho cuando: `python manage.py test servicios` reporta OK en los tres archivos de
    test.

## Fase 6 — Interfaz en Django Admin

- [x] **T24. Mostrar el estado del componente en el inline del servicio.**
  RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-08
  - Columnas: estado, `trabajo_iniciado`, `puede_continuar` y motivo.
  - `estado`, `trabajo_iniciado`, `motivo_finalizacion` y las fechas en solo lectura,
    para que se cambien por las vistas y quede rastro.
  - Hecho cuando: el inline muestra las cuatro columnas.

- [x] **T25. Añadir la acción de registrar la respuesta del cliente en la cotización.**
  RF-COT-03
  - Formulario con resultado, canal sin valor por defecto y observación opcional.
  - Reutiliza la vista de T16, no escribe directo en el modelo.
  - Muestra debajo el resultado y el canal ya registrados.
  - Hecho cuando: registrar una respuesta por WhatsApp cambia el estado de la
    cotización y del componente cuando corresponde.

- [x] **T26. Añadir las acciones de componente en el inline del servicio.**
  RF-COT-08, RF-COT-09, RF-COT-10
  - Iniciar desmontaje, finalizar componente y corregir finalización.
  - Los botones se habilitan con el campo calculado del serializer, y el backend
    vuelve a validar.
  - Hecho cuando: las tres acciones funcionan contra la base de datos de desarrollo.

- [x] **T27. Añadir el resumen de cierre en el encabezado del servicio.**
  RF-COT-11, RF-COT-12
  - Muestra el `detalle` siempre; el botón "Finalizar servicio" solo cuando
    `puede_finalizar` es verdadero.
  - Hecho cuando: con todos los componentes finalizados aparece el botón, y con
    algún componente sin finalizar no aparece.

    **Nota (RF-COT-12).** La redacción original de este criterio pedía que una
    cotización bloqueante *pendiente* dejara el botón oculto. Choca con la regla
    ya decidida: lo pendiente es neutro para el cierre y lo que lo bloquea es que
    quede algún componente sin finalizar. Se corrige el criterio. El botón se
    ofrece solo con componentes sin finalizar; una pendiente sin responder no lo
    impide. Cubierto por `test_una_bloqueante_pendiente_no_impide_que_se_ciegue_si_todo_esta_finalizado`
    y `test_un_componente_sin_finalizar_impide_el_cierre`.

## Fase 7 — Cierre

- [x] **T28. Verificar los cuatro recorridos manuales de §6.4 del plan.**
  RF-COT-05, RF-COT-11, RF-COT-13
  - Rechazo bloqueante de un componente con otro avanzando.
  - Desmontaje registrado y luego rechazo, con el cierre bloqueado.
  - Todas las bloqueantes rechazadas sin trabajo: el botón **no** aparece hasta
    finalizar el componente detenido.
  - Servicio de un solo componente rechazado: tras finalizarlo, el cierre queda
    habilitado.
  - Hecho cuando: los cuatro se comportan como dice la especificación.

- [x] **T29. Actualizar `MEMORY.md`.**
  - Registro: migración nueva, decisiones D-1 a D-12 aplicadas, beneficio de la
    lógica pura en `reglas.py`, interfaz entregada por Django Admin, tests creados y
    confirmación de que la especificación 001 sigue intacta.
  - Confirmar que la sección "No hacer (fuera del MVP)" sigue intacta.
  - Hecho cuando: la bitácora tiene la entrada y el archivo mantiene su estructura.

---

## Orden de dependencia

```
T1 → T2 → T3 → T4 → T5
              ↓
             T6 → T7
              ↓
      T8 → T9 → T10 → T11 → T12
              ↓
     T13 → T14 → T15
              ↓
 T16 → T17 → T18 → T19 → T20 → T21 → T22 → T23
              ↓
     T24 → T25 → T26 → T27
              ↓
        T28 → T29
```

**Total: 29 tareas.**



