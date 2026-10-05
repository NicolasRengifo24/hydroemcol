# 002 - desarrollo del backend para hydroemcol

**Especificación funcional · Hidroemcol**  
**Estado: aprobada**

## 1. Contexto y objetivo

El bloqueo actual de `specs/001-solicitud-banco-pruebas/spec.md` radica en que los modelos existentes no permiten manejar cotizaciones a nivel de componente. Hoy la cotización se entiende a nivel de servicio, lo que provoca que, al rechazar una cotización, se cierre o afecte todo el servicio, incluso cuando hay varios componentes con procesos independientes.

**Objetivo:** Corregir ese comportamiento para que cada componente pueda tener su propia cotización, su propio tipo (bloqueante o no bloqueante), su propio estado de aprobación/rechazo y su propio avance, sin que el rechazo de un componente cierre el servicio ni obligue a cancelar los demás componentes.

**Por qué:** El banco de pruebas atiende solicitudes con uno o varios componentes. Durante la ejecución pueden surgir costos extras (imprevistos, cambio de piezas, tornillos u otros elementos), lo que exige generar una cotización por componente cuando aplica. El sistema debe distinguir entre cotizaciones que impiden continuar la ejecución del componente (bloqueantes) y aquellas que no lo impiden (no bloqueantes), para que el efecto del rechazo sea acorde a ese tipo.

## 2. Usuarios afectados

| Usuario | Descripción |
|---|---|
| **Cliente** | Debe poder conocer, por componente cuando aplique, la cotización generada. Puede aprobarla o rechazarla, ya sea desde la página o por WhatsApp, según corresponda. Si solo se rechaza un componente, debe entender que el resto del servicio continúa. |
| **Administrativo / Técnico** | Debe poder gestionar cotizaciones por componente, definir si cada cotización es bloqueante o no bloqueante, registrar la respuesta del cliente cuando esta ocurre por WhatsApp, registrar las fases del trabajo de cada componente hasta su finalización, y finalizar el servicio cuando ya no queden componentes sin finalizar. |

## 3. Necesidad

**Por qué se requiere este ajuste:** El diseño actual asume "una cotización por solicitud". Esto contradice el requerimiento de que rechazar la cotización de un componente **no** cierre el servicio. Además, no distingue entre costos extras que **impiden continuar** (cotización bloqueante) y costos extras que **no impiden continuar** (cotización no bloqueante). Para sostener ese comportamiento sin romper la lógica existente, debe cambiarse el nivel al que se vinculan cotización, tipo, aprobación/rechazo y avance: pasar de "solicitud" a "componente".

## 4. Glosario

### 4.1 Cotizaciones

- **Cotización bloqueante**: cotización que **impide continuar** la ejecución del componente hasta que sea aprobada.
- **Cotización no bloqueante**: cotización que **no impide continuar** la ejecución del componente, independientemente de que esté pendiente, aprobada o rechazada. Ejemplos: tornillos nuevos, empaques desgastados u otros ajustes que pueden aceptarse o dejarse tal cual.

### 4.2 Estados de cotización

- `pendiente`: presentada al cliente y sin respuesta.
- `aprobada`: el cliente aceptó.
- `rechazada`: el cliente rechazó.

### 4.3 Estados de componente

- `pendiente`: componente recibido, sin trabajo iniciado y sin cotización bloqueante que lo detenga.
- `aprobado`: todas sus cotizaciones fueron aprobadas y puede continuar.
- `rechazado`: tiene al menos una cotización **no bloqueante** rechazada y puede continuar.
- `rechazado_bloqueante`: tiene al menos una cotización **bloqueante** rechazada. **No puede continuar.**
- `en_proceso`: tiene trabajo iniciado y su ejecución continúa.
- `finalizado_por_cliente`: el componente se da por terminado a solicitud del cliente.
- `finalizado_por_tecnico`: el componente se da por terminado por decisión del técnico.

### 4.4 Clasificación de componentes

- **Componente activo**: componente **no finalizado** sobre el que todavía puede ejecutarse trabajo. Es decir, en `pendiente`, `aprobado`, `rechazado` o `en_proceso`.
- **Componente no activo**: componente **no finalizado** sobre el que **no** puede ejecutarse trabajo porque una cotización bloqueante lo impide. Es decir, en `rechazado_bloqueante`, o en `pendiente` con cotización bloqueante sin aprobar.
- **Componente finalizado**: componente en `finalizado_por_cliente` o `finalizado_por_tecnico`.

### 4.5 Posibilidad de continuar

Un componente **tiene posibilidad de continuar** cuando **no** tiene ninguna cotización bloqueante en estado `pendiente` o `rechazada`. Por lo tanto:

- Un componente con cotizaciones **no bloqueantes** pendientes o rechazadas **mantiene** la posibilidad de continuar.
- Un componente con una cotización **bloqueante** pendiente o rechazada **pierde** la posibilidad de continuar.
- Un componente que ya alcanzó un estado de finalización **no** tiene posibilidad de continuar.

### 4.6 Trabajo iniciado

- **Trabajo iniciado**: momento en que el componente **inicia su desmontaje**, es decir, cuando el técnico pasa a manipularlo tras haber sido recibido y destapado.
- Un componente con trabajo iniciado **nunca se considera carente de trabajo realizado**, aunque ninguna fase posterior haya sido registrada.

### 4.7 Fases del componente

Las **fases** son las etapas por las que atraviesa el componente durante el ciclo normal de servicio, desde que se recibe hasta que se finaliza:

1. `recibido`: el componente fue recibido y destapado, y espera.
2. `desmontaje_iniciado`: se inició el desmontaje. **Marca el trabajo iniciado.**
3. `en_ejecucion`: el técnico está ejecutando el trabajo.
4. `finalizado_por_cliente` o `finalizado_por_tecnico`: cierre del componente.

Los estados `rechazado` y `rechazado_bloqueante` no son fases: son consecuencias de una respuesta del cliente y pueden presentarse en cualquier fase.

### 4.8 Criterio único de cierre del servicio

Un servicio permanece **abierto** mientras exista al menos un componente **no finalizado**, sin importar si ese componente es activo o no activo. El servicio solo puede finalizarse cuando **ningún** componente queda sin finalizar.

### 4.9 Acción de finalizar servicio

Acción **manual** del administrativo. El sistema **nunca** finalize un servicio de forma automática. La acción queda habilitada únicamente cuando se cumple alguna de las condiciones de RF-COT-11 o RF-COT-12.

## 5. Requisitos funcionales (EARS)

### RF-COT-01 — Cotización por componente

**WHEN** se determina que un componente requiere una cotización por costos extras  
**THEN** el sistema DEBE asociar esa cotización **únicamente** a ese componente.  
**AND** cada componente DEBE poder tener sus propias cotizaciones, independientes de las de los demás componentes de la misma solicitud.

**Por qué:** Permite aprobar o rechazar por separado sin afectar otros componentes. Es la corrección central del bloqueo.

### RF-COT-02 — Tipo de cotización

**WHEN** se genera una cotización asociada a un componente  
**THEN** el sistema DEBE registrar si esa cotización es `bloqueante` o `no_bloqueante`.  
**AND** ese tipo DEBE estar definido en el momento de presentar la cotización al cliente.

**Por qué:** El tipo determina si el rechazo detiene o no el componente.

### RF-COT-03 — Respuesta del cliente por componente

**WHEN** se presenta una cotización de un componente al cliente  
**THEN** el sistema DEBE poder registrar la respuesta de ese cliente como `aprobada` o `rechazada`.  
**AND** DEBE registrar el canal por el que se recibió la respuesta: `web` o `whatsapp`.  
**AND** DEBE registrar quién la registró y en qué fecha y hora se registró.  
**AND** el rechazo de la cotización de un componente NO DEBE afectar a ningún otro componente de la misma solicitud.

**Por qué:** La respuesta puede llegar por la página o por WhatsApp, y ambos canales son reales. El canal y el responsable permiten saber cómo se obtuvo la respuesta.

### RF-COT-04 — Una cotización bloqueante pendiente impide continuar

**WHEN** un componente tiene una cotización `bloqueante` en estado `pendiente`  
**THEN** ese componente NO DEBE poder pasar a `en_proceso`.  
**AND** el sistema DEBE mostrar que ese componente está detenido por la cotización pendiente.

**Por qué:** El trabajo sobre el componente no puede comenzar sin la aprobación de lo que cuesta.

### RF-COT-05 — Una cotización bloqueante rechazada detiene el componente

**WHEN** el cliente rechaza una cotización `bloqueante` de un componente  
**THEN** el sistema DEBE cambiar el estado de ese componente a `rechazado_bloqueante`.  
**AND** ese componente NO DEBE poder pasar a `en_proceso` mientras el rechazo no sea revertido.  
**AND** el técnico DEBE poder finalizarlo, y definir por WhatsApp la devolución de las piezas y el valor de la mano de obra aplicada hasta ese momento.  
**AND** los demás componentes de la solicitud NO DEBEN verse afectados.

**Por qué:** Un componente con cotización bloqueante rechazada no puede ejecutarse, pero eso no arrastra al resto del servicio.

### RF-COT-06 — Una cotización no bloqueante nunca detiene el componente

**WHEN** un componente tiene una cotización `no_bloqueante`, en cualquier estado (`pendiente`, `aprobada` o `rechazada`)  
**THEN** ese componente DEBE conservar la posibilidad de continuar.  
**AND** el rechazo de esa cotización NO DEBE cambiar el estado del componente a `rechazado_bloqueante` ni impedir su avance.

**Por qué:** Los ajustes no impedientes (tornillos nuevos, empaques desgastados) pueden aceptarse o dejarse tal cual sin frenar el servicio.

### RF-COT-07 — Prevalencia de la cotización bloqueante

**WHEN** un componente tiene más de una cotización  
**THEN** el sistema DEBE evaluar la posibilidad de continuar del componente(**RF-COT-05**) a partir de **cualquiera** de sus cotizaciones `bloqueantes`.  
**AND** la presencia de cotizaciones `no_bloqueantes` aprovadas o rechazadas NO DEBE compensar una cotización `bloqueante` pendiente o rechazada.

**Por qué:** Una cotización bloqueante no puede esquivarse: si el trabajo depende de algo que el cliente no aprobó, ese componente no avanza.

### RF-COT-08 — Registro de fases y del inicio de trabajo

**WHEN** el técnico inicia el desmontaje de un componente  
**THEN** el sistema DEBE registrar la fase `desmontaje_iniciado`.  
**AND** DEBE marcar ese componente como **con trabajo iniciado**.  
**WHEN** el técnico continúa la ejecución del componente  
**THEN** el sistema DEBE registrar el avance por fases del componente conforme al ciclo del glosario.  
**AND** el sistema DEBE mostrar las fases registradas del componente.

**Por qué:** El registro por fases es lo que permite saber si hubo trabajo real sobre el componente, lo cual a su vez determina si el servicio puede cerrarse por rechazo.

### RF-COT-09 — Finalización de un componente

**WHEN** el componente no tiene cotizaciones `bloqueantes` pendientes ni rechazadas  
**THEN** el técnico o el administrativo DEBE poder cambiar su estado a `finalizado_por_cliente` o a `finalizado_por_tecnico`.  
**AND** al finalizar un componente, ese componente DEBE dejar de contar como componente no finalizado.  
**AND** el sistema NO DEBE impedir que los demás componentes de la solicitud sigan avanzando.

**Por qué:** Cada componente se cierra por separado, con un motivo distinto según quién lo da por terminado.

### RF-COT-10 — Corrección de un estado de finalización

**WHEN** un componente ya se encuentra en `finalizado_por_cliente` o `finalizado_por_tecnico`  
**THEN** el técnico o el administrativo DEBE poder corregir ese estado **únicamente** cuando el motivo sea un error humano.  
**AND** el sistema DEBE registrar quién realizó la corrección, en qué fecha y hora, y cuál era el estado anterior.

**Por qué:** El cierre de un componente es una decisión operativa y puede corregirse si se registró mal.

### RF-COT-11 — Habilitar la acción de finalizar el servicio

**WHEN** el administrativo consulta un servicio abierto  
**THEN** el sistema DEBE habilitar la acción de finalizar el servicio en **cualquiera** de estos dos casos:

1. Todos los componentes del servicio se encuentran en estado de finalización (`finalizado_por_cliente` o `finalizado_por_tecnico`).
2. Todas las cotizaciones `bloqueantes` de todos los componentes están en estado `rechazada`, y **ningún** componente de la solicitud tiene trabajo iniciado.

**AND** en el caso 2, el sistema NO DEBE habilitar esa acción si al menos un componente del servicio sigue sin finalizar.

**Nota de interpretación:** como la condición 2 exige además que ningún componente tenga
trabajo iniciado, y el criterio único del glosario 4.8 exige que todos los componentes estén
finalizados, la acción **queda habilitada únicamente cuando todos los componentes están
finalizados**. El caso 2 no habilita el cierre por sí solo: describe el *por qué* del cierre
(todas las cotizaciones bloqueantes rechazadas y nada trabajado), que es el motivo que el
administrativo necesita ver en pantalla, no una condición independiente.

**AND** cuando la acción está habilitada, DEBE habilitarla **únicamente** para el administrativo.  
**AND** el sistema **NUNCA** DEBE finalizar un servicio de forma automática: la finalización requiere una acción manual del administrativo.  
**AND** al ejecutarse la acción, el sistema DEBE registrar quién la ejecutó y en qué fecha y hora.

**Por qué:** El servicio se cierra cuando ya no queda nada que ejecutar. En el caso 2, además, no hay trabajo hecho sobre ninguna pieza, así que no puede haber repuesto que devolver, solo la definición de la mano de obra que el técnico indique por WhatsApp.

### RF-COT-12 — Cotizaciones pendientes no forzan el cierre

**WHEN** una solicitud tiene componentes con cotizaciones `bloqueantes` en estado `pendiente`  
**THEN** esa condición NO DEBE habilitar por sí sola la acción de finalizar el servicio.  
**AND** el sistema DEBE mantener esos componentes visibles como detenidos por cotización pendiente.

**Por qué:** Una cotización pendiente significa que se está esperando al cliente, no que el trabajo se haya descartado.

### RF-COT-13 — Cotización pendiente no impide el avance de los demás

**WHEN** un componente está detenido por una cotización `bloqueante` pendiente o rechazada  
**THEN** los demás componentes de la misma solicitud DEBEN poder avanzar con normalidad.  
**AND** el sistema NO DEBE cerrar la solicitud mientras exista al menos un componente sin finalizar.

**Por qué:** Es el caso central que motiva esta especificación: un componente rechazado no cancela el servicio.

### RF-COT-14 — Coherencia con la especificación 001

**WHILE** se aplique este cambio  
**THE SYSTEM SHALL** mantener la independencia entre solicitudes (**RF-7.4** de la especificación 001).  
**AND** DEBE preservar la unicidad ante doble envío (**RF-7.5**).  
**AND** NO DEBE alterar el aviso de segundo intento (**RF-8**).  
**AND** una solicitud con varios componentes DEBE seguir siendo **una sola solicitud** que contiene todos sus componentes.

**Por qué:** Esta especificación corrige el nivel de la cotización y del estado, sin tocar el resto del proceso ya definido.

### RF-COT-15 - El cliente ve el estado de sus componentes

**WHEN** el cliente consulta el seguimiento público de su solicitud con su token privado  
**THEN** el sistema DEBE incluir en cada componente su `estado` actual y su `fase` actual.  
**AND** DEBE exponerlos como etiqueta legible en español, no como el valor interno del código.  
**AND** el valor DEBE reflejar el estado guardado en el momento de la consulta.  
**AND** NO DEBE exponer los campos que son de control interno: `trabajo_iniciado`, `fecha_inicio_trabajo`, `fecha_finalizacion`, `motivo_finalizacion`, `puede_continuar`, `motivo_bloqueo`, ni el historial de cambios del componente.

**Por qué:** El cliente tiene derecho a saber en qué estado está lo que envió. Sin esto, el seguimiento público solo informaba del tipo de pieza y obligaba a preguntar por teléfono. La visibilidad se limita al estado y la fase: los campos de control interno (por ejemplo `motivo_bloqueo`, que describe una regla interna de la empresa) no son información del cliente.

## 6. Casos límite

- **CL-01** Un componente requiere cotización `bloqueante`, otro `no_bloqueante` y otro no requiere cotización. Solo el primero queda detenido por su cotización; los otros dos avanzan con normalidad.
- **CL-02** Todos los componentes con cotización `bloqueante` son rechazados y **ninguno** tiene trabajo iniciado → cada componente detenido se cierra como `finalizado_por_tecnico` y, cuando **todos** los componentes están finalizados, se habilita la acción de finalizar el servicio (**RF-COT-11**). El técnico define por WhatsApp la devolución de las piezas y el valor de la mano de obra aplicada hasta ese momento.
- **CL-03** Todos los componentes con cotización `bloqueante` son rechazados y **al menos uno** ya tiene trabajo iniciado → **NO** se habilita la acción de finalizar el servicio, porque ese componente sigue sin finalizar y hay trabajo ya realizado sobre una pieza.
- **CL-04** Componentes con cotización `bloqueante` rechazada conviven con componentes `no_bloqueantes` o sin cotización que sí pueden avanzar → la solicitud permanece abierta y los que pueden avanzar continúan.
- **CL-05** Un componente con cotización `no_bloqueante` rechazada puede llegar a `finalizado_por_cliente` o `finalizado_por_tecnico` igual que cualquier otro.
- **CL-06** Una cotización `bloqueante` rechazada sigue siendo consultable y asociada al componente que la originó, junto con el canal por el que respondió el cliente.
- **CL-07** La solicitud tiene **un solo componente**: aplican las mismas reglas. Si se rechaza su cotización `bloqueante` y no tiene trabajo iniciado, el componente debe finalizarse y, una vez finalizado, se habilita finalizar el servicio; si tiene trabajo iniciado, se aplica la misma regla.
- **CL-08** El cliente responde por WhatsApp en lugar de usar la página → el sistema registra el canal `whatsapp`, quién registró la respuesta y cuándo, sin exigir ningún archivo adjunto ni referencia al mensaje.
- **CL-09** El técnico registra el desmontaje pero luego no registra fases posteriores → el componente conserva su condición de con trabajo iniciado.
- **CL-10** El componente tiene varias cotizaciones, una `bloqueante` pendiente y otra `no_bloqueante` aprobada → el componente sigue detenido.
- **CL-11** Una cotización bloqueante se rechaza y después el componente se corrige a `finalizado_por_tecnico` → el servicio solo se habilita a finalizar cuando todos los componentes estén finalizados.
- **CL-12** Un componente fue finalizado por error como `finalizado_por_cliente` y el técnico lo corrige a `en_proceso` → se registra quién hizo la corrección y cuándo.

## 7. Fuera de alcance para esta versión

- El envío automático de la cotización al cliente por WhatsApp, y cualquier integración con el proveedor de mensajería.
- La definición del valor de la mano de obra: lo determina el técnico y se acuerda con el cliente por WhatsApp. El sistema no lo calcula ni lo registra como monto.
- La vista de seguimiento del cliente.
- El transporte, la recepción física y la entrega de componentes.
- El registro técnico detallado, los resultados de prueba y la documentación del trabajo.
- La eliminación de datos personales a solicitud del cliente.
- Cualquier modificación del catálogo de servicios o de los tipos de servicio.
- La lógica de asignación de técnicos y la gestión de personal.

## 8. Criterios de finalización

1. Cada componente tiene sus propias cotizaciones, con tipo `bloqueante` o `no_bloqueante`, y su propio estado (`pendiente`, `aprobado`, `rechazado`).
2. Una cotización `bloqueante` pendiente impide que su componente pase a `en_proceso`.
3. Una cotización `bloqueante` rechazada deja su componente en `rechazado_bloqueante`, sin posibilidad de continuar, y sin afectar a ningún otro componente.
4. Una cotización `no_bloqueante` en cualquier estado no impide que su componente continúe ni cambie su estado por esa causa.
5. La respuesta del cliente se registra con su canal (`web` o `whatsapp`), con quién la registró y con fecha y hora.
6. El registro de fases permite distinguir un componente con trabajo iniciado (desmontaje) de uno que no lo tiene.
7. Cada componente puede finalizarse como `finalizado_por_cliente` o `finalizado_por_tecnico`, y ese estado puede corregirse por error humano dejando rastro de la corrección.
8. La acción de finalizar el servicio solo se habilita al administrativo, nunca se ejecuta sola, y solo en los dos casos definidos en **RF-COT-11**.
9. Una solicitud con varios componentes sigue siendo una sola solicitud, y el rechazo de uno no cancela a los demás.
10. El recorrido completo se verifica manualmente en un teléfono móvil real, según el criterio de **RNF-1** de la especificación 001.

## 9. Decisiones tomadas

| # | Decisión | Motivo |
|---|---|---|
| D-1 | La cotización se asocia al **componente**, no a la solicitud. | Es el bloqueo que motiva esta especificación. |
| D-2 | Cada cotización declara su tipo: `bloqueante` o `no_bloqueante`. | Permite distinguir lo que frena el trabajo de lo que no. |
| D-3 | El componente tiene estados propios y su clasificación activa / no activa / finalizado. | Sin estados en el componente no hay forma de representar un rechazo granular. |
| D-4 | El trabajo se considera iniciado cuando el técnico **inicia el desmontaje**. | Es el punto en que la pieza deja estar en manos de la empresa. |
| D-5 | El criterio de cierre del servicio es **único**: no hay componente sin finalizar. | Evita reglas de cierre contradictorias entre sí. |
| D-6 | La finalización del servicio es **manual** y solo del administrativo. | La decisión de cerrar es del administrativo, no del sistema. |
| D-7 | Un componente con cotización bloqueante rechazada se considera **no activo** y no finalizado. | Puede cerrarse, pero no cuenta como trabajo pendiente de ejecución. |
| D-8 | Los estados de finalización son corregibles por **error humano**, con rastro. | Un cierre mal registrado debe poder corregirse. |
| D-9 | La respuesta del cliente se registra con canal, responsable y fecha; **sin** referencia ni archivo adjunto. | El registro por WhatsApp es la vía real de la empresa. |
| D-10 | El valor de la mano de obra **no** lo define el sistema; lo acuerda el técnico con el cliente por WhatsApp. | El sistema no tiene información para calcularlo. |

## 10. Dudas abiertas

Ninguna. Las decisiones tomadas en §9 cubren los puntos que quedaban abiertos.
