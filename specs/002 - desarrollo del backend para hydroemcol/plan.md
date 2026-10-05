# Plan — 002 - desarrollo del backend para hydroemcol

**Estado: aprobado**
**Spec:** `specs/002 - desarrollo del backend para hydroemcol/spec.md` (Estado: aprobada)

> Este plan describe **cómo** se implementa lo que la spec define como **qué**. No introduce
> reglas de negocio nuevas. Si al implementar aparece una regla que no está en la spec, se
> detiene el trabajo y se pregunta (skill `sdd`, constitución principio 2).

---

## 0. Desviaciones de la skill sdd (confirmadas por el usuario)

La skill `sdd` pide la estrategia de tests con `node --test`. El backend de este proyecto **no
es Node**: es Django 6.1.1 + DRF sobre Python, y la constitución (principio 4) fija
`manage.py test` con `django.test` como único runner permitido.

| Lo que pide la skill | Lo que se hace aquí | Por qué |
|---|---|---|
| Tests con `node --test` | Tests con `django.test.TestCase` sobre `manage.py test` | Constitución principio 4: *"Tests sin dependencias nuevas. Solo `manage.py test` con `django.test`."* Confirmado por el usuario. |
| Funciones puras con `hoy` como parámetro | Funciones puras con `hoy` como parámetro, en Python | Se mantiene la intención de la skill: lógica determinista, sin acceso a base de datos ni a `timezone.now()`, para poder verificar cada regla de la spec de forma aislada. |

**Interfaz:** el panel administrativo de React es un placeholder sin capa de API
(`MEMORY.md`, gaps transversales), así que la interfaz de esta spec se entrega por **Django
Admin** para poder probar los cambios contra la base de datos. No se toca `frontend/`.
Confirmado por el usuario.

---

## 1. Archivos y responsabilidades

### 1.1 Archivos que se crean

| Archivo | Responsabilidad |
|---|---|
| `backend/servicios/estados.py` | **Fuente única de verdad** de los catálogos de estado de componente y de las funciones de transición. Sin dependencias de base de datos. Importado por modelos, serializers, vistas y admin. |
| `backend/servicios/reglas.py` | **Funciones puras de decisión.** Contiene el algoritmo de cierre del servicio, la condición de posibilidad de continuar y el estado que un componente debe adoptar según sus cotizaciones. Todas reciben el estado actual (`hoy`) como parámetro y devuelven una decisión. Sin acceso a base de datos. |
| `backend/servicios/migrations/0003_componente_por_cotizacion.py` | Migración que agrega a `Componente` el campo `estado`, `trabajo_iniciado`, `fecha_finalizacion` y `motivo_finalizacion`; y a `Cotizacion` los campos `componente` (FK, nulable), `es_bloqueante` y `canal`. |
| `backend/servicios/tests/test_reglas.py` | Tests unitarios de las funciones puras de `reglas.py`. Sin base de datos. Cubre el criterio de cierre (RF-COT-11) y la posibilidad de continuar (RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07). |
| `backend/servicios/tests/test_modelos.py` | Tests de los cambios de modelo: valor por defecto de `Componente.estado`, y que `Cotizacion.es_bloqueante` no rompa las cotizaciones existentes. |
| `backend/servicios/tests/test_api.py` | Tests de las vistas: respuesta por componente, canales, transiciones de fase, finalización y las dos condiciones de cierre. |

### 1.2 Archivos que se modifican

| Archivo | Cambio | RF cubiertos |
|---|---|---|
| `backend/servicios/models.py` | Añadir `EstadoComponente`, `EstadoFaseComponente`, `CanalRespuesta`. Añadir campos a `Componente` y a `Cotizacion`. Registrar historial de corrección de estados de finalización. | RF-COT-02, RF-COT-03, RF-COT-05, RF-COT-08, RF-COT-09, RF-COT-10 |
| `backend/servicios/serializers.py` | Exponer el nuevo estado del componente y exponer `puede_continuar` y `puede_finalizar_servicio` como campos calculados (solo lectura), de modo que el frontend no replique la regla. | RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-11, RF-COT-13 |
| `backend/servicios/views.py` | Registrar la respuesta del componente con su canal y responsable; registrar el inicio de desmontaje; finalizar un componente; finalizar el servicio con las dos condiciones; corregir un estado de finalización. **Todo con validación server-side.** | RF-COT-03, RF-COT-04, RF-COT-05, RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11, RF-COT-12 |
| `backend/servicios/urls.py` | Rutas nuevas para responder una cotización de un componente, registrar inicio de trabajo, finalizar componente, corregir finalización y finalizar servicio. | RF-COT-03, RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11 |
| `backend/servicios/admin.py` | Mostrar el estado del componente, permitir registrar la respuesta por WhatsApp, y mostrar en el servicio si la acción de finalizar está habilitada y por qué. | RF-COT-03, RF-COT-11 |
| `MEMORY.md` | Bitácora del cambio y decisiones que implica, por constitución principio 2. | — |

### 1.3 Archivos que NO se tocan

| Archivo | Motivo |
|---|---|
| `frontend/` | La constitución principio 3 dice que el frontend muestra, no decide. Además el panel es un placeholder sin capa de API (`MEMORY.md`, gaps transversales). La interfaz de esta spec se entrega por **Django Admin**, que ya funciona. |
| `backend/usuarios/` | Esta spec no cambia usuarios ni roles. |
| `backend/config/` | No se toca ni autenticación ni permisos. |
| `backend/servicios/migrations/0001_initial.py` y `0002_initial.py` | Las migraciones existentes no se editan; se añade una tercera. |

---

## 2. Funciones puras de lógica

Todas viven en `backend/servicios/reglas.py`. Todas reciben el estado actual del servicio como
parámetro (`hoy`) y devuelven una decisión. **Ninguna consulta la base de datos ni lee la hora
del sistema.** Eso es lo que permite verificarlas de forma aislada.

### 2.1 `tiene_trabajo_iniciado(hoy, componente)` — RF-COT-08

```python
def tiene_trabajo_iniciado(hoy, componente):
    """¿Se inició el desmontaje de este componente?

    El único dato que manda es el booleano trabajo_iniciado, que se
    escribe cuando el técnico inicia el desmontaje. No depende de que
    después se hayan registrado más fases.
    """
    return bool(componente['trabajo_iniciado'])
```

**Por qué es pura:** `hoy` trae el componente ya leído. La función solo lee una clave. No
importa `timezone`, no toca la base de datos.

### 2.2 `puede_continuar(hoy, componente)` — RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07

```python
def puede_continuar(hoy, componente):
    """¿Este componente puede avanzar en su trabajo?

    Regla (glosario 4.5): se puede continuar si NO existe ninguna
    cotización bloqueante en estado pendiente o rechazada.

    - Sin bloqueo            -> True
    - Bloqueante pendiente   -> False  (RF-COT-04)
    - Bloqueante rechazada   -> False  (RF-COT-05)
    - No bloqueante rejected -> True   (RF-COT-06: nunca detiene)
    - Ya finalizado         -> False  (no hay nada que continuar)
    """
    if componente['estado'] in ESTADOS_FINALIZACION:
        return False

    cotizaciones = hoy['cotizaciones_por_componente'].get(componente['id'], [])

    for c in cotizaciones:
        if not c['es_bloqueante']:
            continue                      # RF-COT-06: nunca detiene
        if c['estado'] in ('PENDIENTE', 'RECHAZADA'):
            return False                  # RF-COT-04 y RF-COT-05
    return True                           # RF-COT-07: manda la bloqueante
```

**Por qué es pura:** recibe el diccionario `hoy` con las cotizaciones ya agrupadas por
componente. La función no consulta nada.

### 2.3 `estado_por_rechazo_bloqueante(hoy, componente)` — RF-COT-05

```python
def estado_por_rechazo_bloqueante(hoy, componente):
    """Devuelve 'RECHAZADO_BLOQUEANTE' si hay alguna bloqueante rechazada.

    Devuelve None si no aplica. La decisión de *cuándo* aplicar el
    cambio la toma la vista, no esta función: aquí solo se dice qué
    estado corresponde, para que sea verificable aislado.
    """
    cotizaciones = hoy['cotizaciones_por_componente'].get(componente['id'], [])
    tiene_bloqueante_rechazada = any(
        c['es_bloqueante'] and c['estado'] == 'RECHAZADA'
        for c in cotizaciones
    )
    return 'RECHAZADO_BLOQUEANTE' if tiene_bloqueante_rechazada else None
```

### 2.4 `componentes_no_finalizados(hoy)` — RF-COT-11, RF-COT-13

```python
def componentes_no_finalizados(hoy):
    """Criterio ÚNICO de estado del servicio (glosario 4.8).

    Devuelve los componentes que NO están en estado de finalización,
    sin importar si son activos o no activos.
    """
    return [
        c for c in hoy['componentes']
        if c['estado'] not in ESTADOS_FINALIZACION
    ]
```

### 2.5 `todos_rechazan_bloqueantes(hoy)` — RF-COT-11 caso 2

```python
def todos_rechazan_bloqueantes(hoy):
    """¿Todas las cotizaciones bloqueantes están rechazadas?

    Devuelve True solo si existe al menos una cotización bloqueante y
    todas están en RECHAZADA.

    - Sin cotizaciones bloqueantes -> False (nada que rechazar)
    - Alguna bloqueante PENDIENTE  -> False (RF-COT-12)
    - Todas bloqueantes RECHAZADA -> True
    """
    bloqueantes = [
        c for c in hoy['cotizaciones']
        if c['es_bloqueante']
    ]
    if not bloqueantes:
        return False
    return all(c['estado'] == 'RECHAZADA' for c in bloqueantes)
```

**Por qué `PENDIENTE` no habilita el cierre (RF-COT-12):** una cotización pendiente significa
que se está esperando al cliente, no que el trabajo se descartó.

### 2.6 `puede_finalizar_servicio(hoy)` — RF-COT-11

```python
def puede_finalizar_servicio(hoy):
    """¿Está habilitada la acción manual de finalizar el servicio?

    Criterio ÚNICO (glosario 4.8 y RF-COT-11): todos los componentes
    deben estar en estado de finalización.

    El "caso 2" de RF-COT-11 (todas las bloqueantes rechazadas y
    ningún componente con trabajo iniciado) NO habilita el cierre por
    sí solo: describe el motivo del cierre, no una condición
    independiente. Por eso no aparece como rama aparte aquí.

    NUNCA se finaliza de forma automática (glosario 4.9): esta función
    solo habilita. La ejecución es siempre una acción del administrativo.
    """
    return componentes_no_finalizados(hoy) == []
```

**Por qué el caso 2 excluye componentes con trabajo iniciado:** si el técnico ya desmontó una
pieza, hay trabajo real sobre ella; el servicio no puede cerrarse como si nada se hubiera
hecho (CL-03).

### 2.7 `motivo_bloqueo(hoy, componente)` — RF-COT-04, RF-COT-05, RF-COT-06

```python
def motivo_bloqueo(hoy, componente):
    """Explica en español por qué un componente no puede continuar.

    Sirve para que la interfaz muestre el motivo sin que el frontend
    tenga que deducirlo (constitución principio 3).
    """
    if componente['estado'] in ESTADOS_FINALIZACION:
        return None

    cotizaciones = hoy['cotizaciones_por_componente'].get(componente['id'], [])
    for c in cotizaciones:
        if not c['es_bloqueante']:
            continue
        if c['estado'] == 'PENDIENTE':
            return 'Cotización bloqueante esperando aprobación del cliente'
        if c['estado'] == 'RECHAZADA':
            return 'Cotización bloqueante rechazada por el cliente'
    return None
```

### 2.8 `resumen_cierre(hoy)` — RF-COT-11

```python
def resumen_cierre(hoy):
    """Devuelve si la acción está habilitada y por qué, para la interfaz.

    La habilitación tiene un criterio único: todos los componentes
    finalizados. Los casos describes el motivo que ve el administrativo,
    para que sepa si cierra un trabajo terminado o una solicitud
    rechazada sin trabajo hecho.
    """
    pendientes = componentes_no_finalizados(hoy)

    if not pendientes:
        con_trabajo = [
            c for c in hoy['componentes'] if tiene_trabajo_iniciado(hoy, c)
        ]
        if todos_rechazan_bloqueantes(hoy) and not con_trabajo:
            return {
                'puede_finalizar': True,
                'caso': 'TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO',
                'detalle': (
                    'Todos los componentes están finalizados. Las cotizaciones '
                    'bloqueantes fueron rechazadas y no se inició trabajo en '
                    'ningún componente'
                ),
            }
        return {
            'puede_finalizar': True,
            'caso': 'TODOS_FINALIZADOS',
            'detalle': 'Todos los componentes están finalizados',
        }

    # Queda al menos un componente sin finalizar: no se habilita nunca.
    if todos_rechazan_bloqueantes(hoy):
        return {
            'puede_finalizar': False,
            'caso': 'BLOQUEANTES_RECHAZADAS_CON_TRABAJO_INICIADO',
            'detalle': (
                f'Quedan {len(pendientes)} componente(s) sin finalizar. '
                'Debe finalizarlos uno a uno antes de cerrar el servicio'
            ),
        }

    return {
        'puede_finalizar': False,
        'caso': 'SERVICIO_EN_CURSO',
        'detalle': f'Quedan {len(pendientes)} componente(s) sin finalizar',
    }
```

---

## 3. Algoritmo en pseudocódigo

### 3.1 Registrar la respuesta del cliente a una cotización de componente — RF-COT-03

```
ENTRADA: servicio, componente, cotización, resultado (APROBADA|RECHAZADA),
         canal (WEB|WHATSAPP), usuario_actual

SI la cotización NO pertenece al componente indicado:
    → 400 "La cotización no pertenece a ese componente"

SI la cotización NO es pendiente:
    → 400 "Esa cotización ya tiene respuesta"

CREAR aprobación con:
    cotizacion, resultado, canal, usuario_registro=usuario_actual,
    fecha=ahora, medio=canal

ACTUALIZAR estado de la cotización = resultado

// A partir de aquí se evalúa el efecto sobre el componente (RF-COT-05)
HOY = leer estado actual del servicio (componentes + cotizaciones)

nuevo_estado = estado_por_rechazo_bloqueante(HOY, componente)

SI nuevo_estado NO es nulo:
    actualizar estado del componente = nuevo_estado
    registrar historial del componente

// El estado del SERVICIO nunca se toca aquí (RF-COT-05, RF-COT-13)
responder 201
```

### 3.2 Registrar el inicio de trabajo (desmontaje) — RF-COT-08

```
ENTRADA: componente, usuario_actual

HOY = leer estado actual del servicio

SI puede_continuar(HOY, componente) es FALSO:
    → 409 "El componente no puede iniciar trabajo: " + motivo_bloqueo(HOY, componente)

actualizar componente:
    fase = DESMONTAJE_INICIADO
    trabajo_iniciado = VERDADERO
    fecha_inicio_trabajo = ahora

registrar historial del componente con la fase y el usuario

responder 200
```

**Por qué se valida aquí:** el backend decide (**RF-COT-04**). El botón del frontend puede
estar deshabilitado, pero la garantía real es que la API rechaza el inicio de trabajo.

### 3.3 Finalizar un componente — RF-COT-09

```
ENTRADA: componente, motivo (FINALIZADO_POR_CLIENTE|FINALIZADO_POR_TEÑICO), usuario_actual

HOY = leer estado actual del servicio

SI el componente YA está en estado de finalización:
    → 409 "El componente ya está finalizado"

// No se exige que pueda_continuar: un componente detenido por
// cotización bloqueante rechazada también se puede finalizar
// (RF-COT-05 y decisión D-7).
actualizar componente:
    estado = motivo
    fecha_finalizacion = ahora
    fecha_fin_motivo = ahora

registrar historial del componente

responder 200
```

### 3.4 Corregir un estado de finalización — RF-COT-10

```
ENTRADA: componente, estado_actual, nuevo_estado, usuario_actual

HOY = leer estado actual del servicio

SI el estado_actual NO es de finalización:
    → 409 "Solo se pueden corregir estados de finalización"

// Se acepta cualquier nuevo estado válido. La marca de "por error
// humano" la documenta la operación; el sistema solo garantiza el
// rastro.
CREAR registro en historial de corrección:
    componente, estado_anterior, estado_nuevo, usuario_actual, fecha=ahora

actualizar componente.estado = nuevo_estado
responder 200
```

### 3.5 Finalizar el servicio — RF-COT-11

```
ENTRADA: servicio, usuario_actual

HOY = leer estado actual del servicio
resumen = resumen_cierre(HOY)

SI resumen.puede_finalizar es FALSO:
    → 409 con resumen.detalle   (el mensaje va en español)

actualizar servicio:
    estado = FINALIZADO
    fecha_finalizacion = ahora

registrar en HistorialServicio:
    estado, comentario=resumen.detalle, usuario, visible_cliente=False

responder 200
```

**Por qué no hay ruta automática:** el pseudocódigo no tiene ninguna rama que finalice el
servicio sin una llamada HTTP del administrativo. El sistema nunca cierra solo (**glosario 4.9**).

---

## 4. Cómo se pinta en la interfaz

**Decisión de alcance:** el panel administrativo de React es un placeholder sin capa de API
(`MEMORY.md`, gaps transversales; `frontend/src/pages/Admin.tsx` no tiene cliente HTTP). Por
constitución principio 3 el frontend solo muestra, así que la interfaz de esta spec se entrega
por **Django Admin**, que ya está construido y es donde trabaja el administrativo hoy. No se
toca `frontend/`. Confirmado por el usuario para poder probar los cambios contra la base de
datos.

### 4.1 Lista de componentes dentro del servicio (inline en `ServicioAdmin`)

| Columna | Origen | Qué muestra |
|---|---|---|
| Tipo / Referencia | `Componente` | Sin cambios respecto a hoy |
| **Estado** | `Componente.estado` | Etiqueta en español del estado, con color: `rechazado_bloqueante` en ámbar (detenido, no es error), `finalizado_por_cliente` y `finalizado_por_tecnico` en verde |
| **Trabajo iniciado** | `trabajo_iniciado` | Sí / No. Es el dato que decide el caso 2 del cierre |
| **Puede continuar** | `puede_continuar()` de `reglas.py` | Sí / No |
| **Motivo** | `motivo_bloqueo()` | Texto en español: *"Cotización bloqueante rechazada por el cliente"* |

**Cubre:** RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-08.

### 4.2 Registro de la respuesta del cliente (dentro de `CotizacionAdmin`)

Botón **"Registrar respuesta del cliente"** sobre cada cotización. Abre un formulario con:

- **Resultado**: Aprobar / Rechazar (obligatorio)
- **Canal**: Web / WhatsApp (obligatorio, sin valor por defecto, para que la persona que
  registra elija conscientemente)
- **Observación**: texto libre, opcional
- **Fecha**: opcional, por defecto la hora actual

Al guardar, el sistema registra la aprobación, cambia el estado de la cotización y, si es
bloqueante y fue rechazada, marca el componente como `rechazado_bloqueante`. La línea bajo el
formulario muestra el resultado y el canal ya registrados, para que quede claro qué se
comunicó por WhatsApp.

**Cubre:** RF-COT-03, RF-COT-05.

### 4.3 Acciones sobre un componente (en `ServicioAdmin`, inline de componentes)

Botones disponibles según lo que devuelva el backend:

| Situación | Botón | Efecto |
|---|---|---|
| `puede_continuar` es No | *"Iniciar desmontaje"* deshabilitado, con el motivo al lado | **RF-COT-04, RF-COT-05** |
| Componente no finalizado | *"Registrar fase"* (desmontaje iniciado / en ejecución) | **RF-COT-08** |
| Componente no finalizado | *"Finalizar componente"* → elegir Finalizado por cliente / por técnico | **RF-COT-09** |
| Componente finalizado | *"Corregir finalización"* | **RF-COT-10** |

El botón se habilita o deshabilita con el campo calculado del serializer. **El backend vuelve a
validar la misma condición aunque el frontend permitiera el clic** (constitución principio 3).

**Cubre:** RF-COT-08, RF-COT-09, RF-COT-10.

### 4.4 Encabezado del servicio

Un bloque con el resultado de `resumen_cierre(HOY)`:

- Si `puede_finalizar` es verdadero: botón **"Finalizar servicio"** visible, con el `detalle`
  que devuelve `resumen_cierre` (*"Todos los componentes están finalizados"*, o el motivo de
  cierre por bloqueantes rechazadas sin trabajo).
- Si es falso: el `detalle` aparece como aviso informativo y **no** hay botón. Cuando lo que
  falta es cerrar un componente detenido, el aviso dice cuántos componentes faltan y que hay
  que finalizarlos uno a uno.

El botón nunca aparece por debajo y nunca se ejecuta solo.

**Cubre:** RF-COT-11, RF-COT-12.

### 4.5 Lo que el cliente ve

Esta spec **no toca la vista de seguimiento del cliente**: la interfaz de seguimiento es una
funcionalidad separada y su spec todavía no existe (sección 7 de la spec 001). Lo único que
cambia aquí es que la cotización lleva el componente asociado, para que cuando esa vista se
escriba pueda mostrar a qué pieza corresponde cada cotización.

**Cubre:** RF-COT-01.

---

## 5. Decisiones técnicas justificadas

### D-1 · La cotización apunta al componente, no solo al servicio

**Qué:** `Cotizacion` gana una FK `componente`, **nulable**.

**Por qué:** la spec exige que el rechazo aplique solo a su componente (**RF-COT-01**). Sin esa
FK el resultado del rechazo no tiene a qué pieza atribuirse.

**Alternativa descartada:** que cada línea de la cotización (`DetalleCotizacion`) apunte al
componente. Es la opción 1 de `MEMORY.md` §2. Se descarta porque obliga a que toda cotización
tenga al menos una línea con componente, y hoy una cotización puede incluir insumos que no son
componentes (fletes, viáticos). Con la FK en la cotización, una cotización de servicio sin
componente sigue siendo válida y no obliga a migrar los datos existentes.

### D-2 · `es_bloqueante` es un booleano, no un catálogo

**Qué:** `Cotizacion.es_bloqueante = BooleanField(default=False)`.

**Por qué:** la spec solo admite dos valores (glosario 4.1). Un `BooleanField` es la
representación más simple y no permite estados intermedios inventados.

**Alternativa descartada:** un `TextChoices` con `BLOQUEANTE` / `NO_BLOQUEANTE`. Se descarta
porque añade el texto en dos lugares (código y base de datos) para un dato que es sí o no, y
suma un valor más que mantener sincronizado sin ningún beneficio.

### D-3 · Las reglas van en funciones puras aparte, no dentro de los modelos

**Qué:** `reglas.py` con funciones que reciben `hoy` y devuelven decisiones.

**Por qué:** es lo que hace verificable cada RF de la spec sin levantar la base de datos, y es
lo que permite probar los casos límite (CL-01 a CL-12) de forma directa. También cumple la
constitución principio 3: la decisión vive en el backend y el frontend solo recibe el
resultado.

**Alternativa descartada:** `@property` en los modelos. Se descarta porque un `@property` no se
puede probar sin base de datos, y porque para `puede_finalizar_servicio` necesita ver **todos**
los componentes, lo que obligaría a consultas dentro de la propiedad y a repetir la regla en
las vistas.

### D-4 · `trabajo_iniciado` es un booleano, no una fase que se deduce

**Qué:** `Componente.trabajo_iniciado = BooleanField(default=False)`, que se escribe cuando el
técnico registra el desmontaje.

**Por qué:** **RF-COT-08** y el caso límite **CL-09** exigen que el componente conserve la
condición de con trabajo iniciado aunque después no se registre ninguna fase más. Un booleano
explícito lo garantiza; deducirlo de "tiene alguna fase registrada" haría que un registro de
fase perdido borrara el hecho.

**Alternativa descartada:** deducirlo de `fase != RECIBIDO`. Se descarta por CL-09: perder un
registro de fase no puede hacer desaparecer trabajo ya realizado.

### D-5 · La FK `componente` de `Cotizacion` es nulable

**Qué:** `componente = ForeignKey(Componente, null=True, blank=True, on_delete=CASCADE)`.

**Por qué:** hoy existen cotizaciones del servicio sin componente (las iniciales). Hacerla
obligatoria obligaría a inventar un componente o a migrar datos que no se pueden mapear.

**Alternativa descartada:** hacerla obligatoria con `null=False`. Se descarta porque rompe los
datos existentes y porque una cotización inicial legitimately cubre el servicio completo, no
una pieza.

### D-6 · Registrar el inicio de trabajo valida que el componente pueda continuar

**Qué:** `POST .../iniciar-trabajo/` responde 409 si `puede_continuar` es falso.

**Por qué:** **RF-COT-04** exige que un componente con cotización bloqueante pendiente no pase
a `en_proceso`. La garantía tiene que estar en la API, no solo en el botón.

**Alternativa descartada:** confiar solo en el botón deshabilitado en Django Admin. Se descarta
porque el admin de Django permite editar el campo directamente y porque un cliente de API
puede llamar al endpoint directamente.

### D-7 · `rechazado_bloqueante` es un estado del componente, no un subtipo de `rechazado`

**Qué:** valor propio en `EstadoComponente`.

**Por qué:** la spec (glosario 4.3 y decisión D-7 de la spec) lo define como estado distinto de
`rechazado`, porque `rechazado` significa "puede continuar" y `rechazado_bloqueante` significa
"no puede continuar". Fusionarlos obligaría a deducir el significado mirando las cotizaciones
en cada lectura.

**Alternativa descartada:** mantener un solo estado `rechazado` y deducir de las cotizaciones si
detiene o no. Se descarta porque distributed esa misma decisión en cada pantalla y cada
serializer.

### D-8 · El cierre tiene un criterio único de habilitación y varios motivos distinguibles

**Qué:** `puede_finalizar_servicio` usa una sola condición (todos los componentes finalizados).
`resumen_cierre` sí distingue varios motivos para explicarle al administrativo por qué puede
cerrar o qué le falta.

**Por qué:** el glosario 4.8 fija un criterio único de estado del servicio, y RF-COT-13 lo
reitera: no se cierra mientras exista un componente sin finalizar. El caso 2 de RF-COT-11
("bloqueantes rechazadas y nada trabajado") describe entonces el **motivo** del cierre, no una
condición que habilite por sí sola. Separar la condición del motivo permite que el 409 sea
legible sin abrir una vía de cierre que contradiga 4.8.

**Alternativa descartada:** tratar el caso 2 como condición independiente, que es lo que
sugería la primera redacción de CL-02. Se descarta porque obligaría al administrativo a cerrar
un servicio con componentes sin finalizar, lo que contradice RF-COT-13 y deja el motivo de
`rechazado_bloqueante` sin resolver.

### D-9 · No se toca `frontend/`

**Qué:** cero archivos del frontend.

**Por qué:** constitución principio 3 y `MEMORY.md` (el frontend no tiene capa de API, la fase 4
es un placeholder). Implementar aquí el panel en React exigiría resolver primero una brecha que
pertenece a otra fase.

**Alternativa descartada:** añadir el cliente HTTP y las vistas del panel en esta spec. Se
descarta porque mezclaría el cambio de modelo con una brecha de infraestructura de otra fase,
y porque la constitución exige instalar o definir cosas stepwise con aprobación.

### D-10 · Tests con `django.test`, no con `node --test`

**Qué:** `TestCase` de `django.test`, ejecutados con `manage.py test`.

**Por qué:** constitución principio 4. El backend es Django; no hay `package.json` en `backend/`.

**Alternativa descartada:** instalar un runner de Node o un script aparte para probar lógica
Python. Se descarta por el principio 4 y porque exigiría dependencias nuevas (principio 1).

### D-11 · `AprobacionServicio` se reutiliza en vez de crear un modelo de respuesta

**Qué:** la respuesta del cliente por componente se registra como `AprobacionServicio` con
`componente` resuelto a través de `Cotizacion.componente`.

**Por qué:** ese modelo ya tiene `resultado`, `medio` (Web / WhatsApp / …), `fecha`,
`usuario_registro` e `observacion`, que es exactamente lo que pide **RF-COT-03**. Crear un
modelo paralelo duplicaría esos campos y obligaría a elegir cuál manda.

**Alternativa descartada:** un modelo `RespuestaClienteCotizacion` nuevo. Se descarta por
duplicación: habría que migrar el histórico de aprobaciones o mantener las dos tablas en
paralelo.

### D-12 · `fecha_finalizacion_componente` y `motivo` se guardan en `Componente`

**Qué:** `fecha_finalizacion` (fecha) y `motivo_finalizacion` (catálogo
`FINALIZADO_POR_CLIENTE` / `FINALIZADO_POR_TEÑICO`).

**Por qué:** **RF-COT-09** exige poder distinguir los dos cierres, y **RF-COT-10** exige saber
el estado anterior al corregir. Guardarlo en el componente evita tener que reconstruirlo
leyendo el historial.

**Alternativa descartada:** deducirlo de las filas del historial. Se descarta porque el
historial es un registro de auditoría, no el estado actual; usarlo como fuente de verdad lo
convierte en algo que hay que recalcular y que puede quedar inconsistente.

---

## 6. Estrategia de tests con `manage.py test`

Razón de ser de los archivos: las reglas de negocio son funciones puras (**RF-COT-04** a
**RF-COT-07**, **RF-COT-11**, **RF-COT-12**), así que se prueban sin base de datos. Las vistas
se prueban con datos reales para confirmar que la API no permite lo que la spec prohíbe.

### 6.1 `tests/test_reglas.py` — funciones puras, sin base de datos

`SimpleTestCase` de `django.test`. Cubre **RF-COT-04, RF-COT-05, RF-COT-06, RF-COT-07,
RF-COT-11, RF-COT-12** y los casos límite **CL-01, CL-03, CL-04, CL-05, CL-07, CL-10**.

| Test | Qué verifica |
|---|---|
| `test_sin_cotizaciones_puede_continuar` | Componente sin cotizaciones → `puede_continuar` verdadero |
| `test_bloqueante_pendiente_no_puede_continuar` | **RF-COT-04**: bloqueante `PENDIENTE` → falso |
| `test_bloqueante_rechazada_no_puede_continuar` | **RF-COT-05**: bloqueante `RECHAZADA` → falso |
| `test_no_bloqueante_rechazada_si_puede_continuar` | **RF-COT-06**: no bloqueante `RECHAZADA` → verdadero |
| `test_no_bloqueante_pendiente_si_puede_continuar` | **RF-COT-06**: no bloqueante `PENDIENTE` → verdadero |
| `test_bloqueante_manda_sobre_no_bloqueante` | **RF-COT-07 / CL-10**: bloqueante pendiente + no bloqueante aprobada → falso |
| `test_componente_finalizado_no_puede_continuar` | Finalizado por cliente o por técnico → falso |
| `test_rechazo_bloqueante_devuelve_estado` | **RF-COT-05**: `estado_por_rechazo_bloqueante` devuelve `RECHAZADO_BLOQUEANTE` |
| `test_sin_bloqueante_rechazada_no_cambia_estado` | **RF-COT-06**: devuelve `None` |
| `test_cierre_caso_todos_finalizados` | **RF-COT-11** caso 1: `puede_finalizar_servicio` verdadero |
| `test_cierre_bloqueantes_rechazadas_sin_trabajo_permite_cierre_ya_finalizados` | **RF-COT-11** caso 2 como *motivo*: todos finalizados, todas bloqueantes rechazadas, sin trabajo → `puede_finalizar` verdadero y `caso = TODAS_BLOQUEANTES_RECHAZADAS_SIN_TRABAJO` |
| `test_cierre_bloqueantes_rechazadas_sin_finalizar_no_habilita` | **RF-COT-11** (AND final) y **RF-COT-13**: todas bloqueantes rechazadas y sin trabajo, pero con un componente `RECHAZADO_BLOQUEANTE` sin finalizar → falso |
| `test_cierre_bloqueantes_rechazadas_con_trabajo_no_habilita` | **CL-03**: un componente con `trabajo_iniciado` → falso |
| `test_cierre_bloqueante_pendiente_no_habilita` | **RF-COT-12**: una bloqueante pendiente → falso |
| `test_cierre_sin_bloqueantes_rechazadas_no_habilita` | Ninguna bloqueante rechazada → falso |
| `test_cierre_no_activo_sigue_contando_como_no_finalizado` | **Glosario 4.8**: componente `RECHAZADO_BLOQUEANTE` cuenta como no finalizado |
| `test_un_solo_componente_rechazado_requiere_finalizarlo_primero` | **CL-07**: servicio de un componente, bloqueante rechazada, sin trabajo → falso hasta que el componente se finalice |
| `test_motivo_bloqueo_pendiente_y_rechazada` | **RF-COT-04, RF-COT-05**: los dos mensajes distintos |
| `test_motivo_bloqueo_ninguno` | Sin bloqueo → `None` |

### 6.2 `tests/test_modelos.py` — modelo y migración

`TestCase`. Cubre **RF-COT-02, RF-COT-08, RF-COT-09, RF-COT-14** y la no regresión de las
cotizaciones que ya existían.

| Test | Qué verifica |
|---|---|
| `test_componente_nace_pendiente` | Componente nuevo con `estado = PENDIENTE` y `trabajo_iniciado = False` |
| `test_cotizacion_existente_no_se_rompe` | Una cotización creada antes de la migración sigue legible, con `es_bloqueante = False` y `componente = None` (**RF-COT-14**) |
| `test_cotizacion_puede_apuntar_a_componente` | FK nullable acepta componente y acepta `None` (D-5) |
| `test_finalizar_componente_guarda_motivo_y_fecha` | **RF-COT-09**: quedan `motivo_finalizacion` y `fecha_finalizacion` |
| `test_trabajo_iniciado_es_explicito` | **RF-COT-08 / CL-09**: el booleano es independiente de las fases (D-4) |

### 6.3 `tests/test_api.py` — vistas y permisos

`TestCase` con `APIClient` y un `Usuario` administrativo. Cubre **RF-COT-03, RF-COT-04,
RF-COT-08, RF-COT-09, RF-COT-10, RF-COT-11, RF-COT-13**.

| Test | Qué verifica |
|---|---|
| `test_registrar_respuesta_por_whatsapp` | **RF-COT-03**: crea la aprobación con `medio = WHATSAPP`, `usuario_registro` y `fecha` |
| `test_registrar_respuesta_por_web` | **RF-COT-03**: `medio = WEB` con el usuario que la registra |
| `test_respuesta_deja_registro_consultable` | **RF-COT-03**: la respuesta queda en la aprobación, con su canal visible |
| `test_rechazar_bloqueante_marca_componente` | **RF-COT-05**: el componente queda `RECHAZADO_BLOQUEANTE` |
| `test_rechazar_bloqueante_no_toca_otros_componentes` | **RF-COT-05 / RF-COT-13**: los demás siguen igual |
| `test_rechazar_bloqueante_no_cierra_el_servicio` | **RF-COT-13**: el estado del servicio no cambia |
| `test_rechazar_no_bloqueante_no_marca_componente` | **RF-COT-06**: el componente no pasa a `RECHAZADO_BLOQUEANTE` |
| `test_cotizacion_ajena_al_componente_responde_400` | Validación de pertenencia |
| `test_cotizacion_ya_respondida_responde_400` | No se responde dos veces |
| `test_iniciar_trabajo_bloqueado_responde_409` | **RF-COT-04**: la API rechaza el inicio de trabajo con el motivo |
| `test_iniciar_trabajo_permitido_registra_fase` | **RF-COT-08**: registra fase y marca `trabajo_iniciado` |
| `test_finalizar_componente_por_tecnico` | **RF-COT-09**: guarda motivo y fecha |
| `test_finalizar_componente_detenido_por_bloqueante` | **RF-COT-05 / D-7**: un componente `RECHAZADO_BLOQUEANTE` se puede finalizar |
| `test_finalizar_componente_ya_finalizado_responde_409` | **RF-COT-09** |
| `test_corregir_finalizacion_registra_anterior` | **RF-COT-10**: queda el estado anterior, el nuevo, el usuario y la fecha |
| `test_corregir_estado_no_finalizado_responde_409` | **RF-COT-10**: solo se corrigen estados de finalización |
| `test_finalizar_servicio_caso_todos_finalizados` | **RF-COT-11** caso 1: 200 y el servicio queda `FINALIZADO` con historial |
| `test_finalizar_servicio_caso_bloqueantes_rechazadas` | **RF-COT-11** caso 2: 200 |
| `test_finalizar_servicio_bloqueada_con_trabajo_responde_409` | **RF-COT-11 / CL-03**: 409 con el motivo |
| `test_finalizar_servicio_pendiente_no_habilita_ni_bloquea` | **RF-COT-12**: lo pendiente es neutro; con todos los componentes finalizados el cierre procede |
| `test_pendiente_deja_el_componente_detenido` | **RF-COT-12**: el componente sigue visible como detenido y el servicio abierto |
| `test_servicio_no_se_finaliza_solo` | **Glosario 4.9**: tras rechazar cotizaciones, sin llamar a la acción, el servicio sigue abierto |
| `test_accion_de_finalizar_exige_administrativo` | La acción no está disponible sin sesión |
| `test_serializer_expone_puede_continuar_y_motivo` | **RF-COT-04, RF-COT-05, RF-COT-06**: los campos calculados vienen del backend (constitución principio 3) |
| `test_serializer_expone_resumen_de_cierre` | **RF-COT-11**: el serializer expone `puede_finalizar`, `caso` y `detalle` |

### 6.4 Verificación manual (no automatizable)

| Recorrido | Resultado esperado |
|---|---|
| Servicio con 2 componentes: se rechaza la cotización bloqueante de uno | Ese componente queda `RECHAZADO_BLOQUEANTE`, el otro sigue avanzando, el servicio queda abierto (**RF-COT-05, RF-COT-13**) |
| Se registra el desmontaje de un componente y luego se rechaza su cotización bloqueante | El servicio no se puede cerrar hasta que ese componente se finalice (**CL-03**) |
| Se rechazan todas las bloqueantes sin haber iniciado trabajo | El botón **no** aparece hasta finalizar el componente detenido; después aparece con el texto del motivo del caso 2 (**RF-COT-11**) |
| Un solo componente con bloqueante rechazada y sin trabajo | El botón aparece cuando el componente queda finalizado (**CL-07**) |

---

## 7. Trazabilidad RF → plan

| RF | Dónde se implementa | Qué lo prueba |
|---|---|---|
| RF-COT-01 | `models.py` (FK `Cotizacion.componente`) | `test_cotizacion_puede_apuntar_a_componente`, `test_cotizacion_existente_no_se_rompe` |
| RF-COT-02 | `models.py` (`es_bloqueante`) | `test_cotizacion_existente_no_se_rompe` |
| RF-COT-03 | `views.py` (registro de respuesta), `serializers.py` | `test_registrar_respuesta_por_whatsapp`, `test_registrar_respuesta_por_web`, `test_respuesta_deja_registro_consultable` |
| RF-COT-04 | `reglas.py` (`puede_continuar`), `views.py` (validación de inicio) | `test_bloqueante_pendiente_no_puede_continuar`, `test_iniciar_trabajo_bloqueado_responde_409` |
| RF-COT-05 | `reglas.py` (`estado_por_rechazo_bloqueante`), `models.py` (`EstadoComponente`) | `test_rechazo_bloqueante_devuelve_estado`, `test_rechazar_bloqueante_marca_componente`, `test_rechazar_bloqueante_no_toca_otros_componentes` |
| RF-COT-06 | `reglas.py` (`puede_continuar`, rama no bloqueante) | `test_no_bloqueante_rechazada_si_puede_continuar`, `test_rechazar_no_bloqueante_no_marca_componente` |
| RF-COT-07 | `reglas.py` (`puede_continuar`, prevalencia) | `test_bloqueante_manda_sobre_no_bloqueante` |
| RF-COT-08 | `models.py` (`trabajo_iniciado`, fases), `views.py`, `reglas.py` (`tiene_trabajo_iniciado`) | `test_trabajo_iniciado_es_explicito`, `test_iniciar_trabajo_permitido_registra_fase` |
| RF-COT-09 | `views.py` (finalizar componente), `models.py` (`motivo_finalizacion`) | `test_finalizar_componente_por_tecnico`, `test_finalizar_componente_ya_finalizado_responde_409` |
| RF-COT-10 | `views.py` (corregir finalización), `models.py` (historial de corrección) | `test_corregir_finalizacion_registra_anterior`, `test_corregir_estado_no_finalizado_responde_409` |
| RF-COT-11 | `reglas.py` (`puede_finalizar_servicio`, `resumen_cierre`), `views.py` (acción manual) | `test_cierre_caso_todos_finalizados`, `test_cierre_caso_bloqueantes_rechazadas_sin_trabajo`, `test_finalizar_servicio_caso_todos_finalizados`, `test_finalizar_servicio_caso_bloqueantes_rechazadas`, `test_servicio_no_se_finaliza_solo` |
| RF-COT-12 | `reglas.py` (`todos_rechazan_bloqueantes`) | `test_cierre_bloqueante_pendiente_no_habilita`, `test_finalizar_servicio_bloqueada_por_pendiente_responde_409` |
| RF-COT-13 | `views.py` (respuesta no toca el servicio), `reglas.py` | `test_rechazar_bloqueante_no_cierra_el_servicio`, `test_rechazar_bloqueante_no_toca_otros_componentes` |
| RF-COT-14 | Sin cambios en lo existente | `test_cotizacion_existente_no_se_rompe` |

**Casos límite:** CL-01 → `test_bloqueante_manda_sobre_no_bloqueante`; CL-03 →
`test_cierre_bloqueantes_rechazadas_con_trabajo_no_habilita`; CL-04 →
`test_rechazar_bloqueante_no_toca_otros_componentes`; CL-05 →
`test_no_bloqueante_rechazada_si_puede_continuar`; CL-07 →
`test_un_solo_componente_rechazado_habilita_cierre`; CL-09 → `test_trabajo_iniciado_es_explicito`;
CL-10 → `test_bloqueante_manda_sobre_no_bloqueante`.

---

## 8. Verificación posterior a la implementación

La constitución y `AGENTS.md` §11 fijan la verificación con el MCP, no con tests automáticos
solos:

1. `python manage.py makemigrations --check --dry-run` — confirma que los modelos y las
   migraciones están alineados.
2. `python manage.py check` — validaciones de Django.
3. `python manage.py test` — la batería de §6.
4. Migración en base de datos de desarrollo y recorrido manual en Django Admin con los cuatro
   casos de §6.4.
5. Actualizar `MEMORY.md`: migración nueva, decisiones D-1 a D-12 aplicadas, y confirmación de
   que la especificación 001 sigue intacta.
