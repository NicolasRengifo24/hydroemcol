Este documento contiene el contexto funcional, de negocio y arquitectónico aprobado hasta ahora.

El agente debe leerlo antes de modificar o crear código.

Regla principal: el agente NO debe asumir decisiones importantes que no estén definidas. Debe explicar, proponer alternativas y preguntar al usuario antes de implementar cambios que afecten arquitectura, seguridad, base de datos, flujo de negocio o integraciones.

1. OBJETIVO DEL PROYECTO

Se desarrollará una plataforma web para una empresa dedicada a:

suministro de repuestos;
importación sobre pedido;
servicios eléctricos relacionados con sistemas de mando hidráulicos;
sistemas de control proporcional;
sistemas de marcha;
control de velocidades;
asesoría e implementación de sistemas electrohidráulicos a la medida;
servicios técnicos hidráulicos mediante banco de pruebas;
diagnóstico, reparación y pruebas de componentes hidráulicos.

Entre los componentes atendidos pueden encontrarse:

cilindros;
bombas;
motores;
orbitroles;
controles;
válvulas;
otros componentes hidráulicos y electrohidráulicos.
Objetivo principal

La plataforma NO es inicialmente un e-commerce.

El núcleo del proyecto es:

Recibir solicitudes de servicio, administrar el proceso técnico y administrativo, generar cotizaciones, registrar aprobaciones, documentar el avance y permitir al cliente consultar únicamente su servicio sin crear una cuenta.

2. ALCANCE FUNCIONAL DEL MVP
   Sitio público

Debe contemplar:

Landing page.
Quiénes somos.
Servicios.
Soluciones.
Fotografías.
Presentación de productos/componentes sin convertirlos necesariamente en catálogo comercial.
Contacto.
Redes sociales.
Botón de WhatsApp.
Solicitud de servicio.
Seguimiento de servicio.
Panel administrativo

Debe permitir:

login;
consultar solicitudes;
consultar servicios;
revisar solicitudes;
aceptar/rechazar solicitudes;
crear cotizaciones;
agregar múltiples ítems a una cotización;
registrar aprobación;
registrar aprobaciones recibidas por medios externos;
cambiar estados;
registrar historial;
registrar información técnica;
subir fotografías;
decidir qué fotografías son visibles para el cliente;
generar/consultar enlace privado de seguimiento;
preparar mensajes de WhatsApp. 3. STACK TECNOLÓGICO
Frontend
React
Vite
TypeScript
React Router
TanStack Query
Lucide React u otra librería de iconos si se considera necesaria.
Backend
Python
Django
Django REST Framework
Base de datos
PostgreSQL
Neon como proveedor inicial.
Archivos
Cloudflare para almacenamiento de fotografías/archivos.
PostgreSQL NO almacenará directamente los archivos binarios.
PostgreSQL almacenará URL/referencia del archivo.
Despliegue previsto
Backend Django/DRF: Render.
Base de datos: Neon.
Imágenes/archivos: Cloudflare.
Frontend: infraestructura web compatible con el proyecto.

Actualmente se utilizan planes gratuitos y existe un sistema de ping para evitar que Render quede dormido, pero la arquitectura NO debe depender estructuralmente de que los servicios permanezcan gratuitos.

4. PRINCIPIOS DE ARQUITECTURA
   Simplicidad

Preferir una arquitectura sencilla, clara y mantenible.

Separación

Mantener separados:

frontend;
backend;
base de datos;
almacenamiento de archivos;
integraciones externas.
Seguridad

La seguridad y autorización deben resolverse en backend.

Nunca confiar en que React simplemente oculte información.

Trazabilidad

Las operaciones importantes deben dejar registro.

Evolución

La arquitectura debe permitir futuras integraciones sin complicar innecesariamente el MVP.

No sobreingeniería

No introducir tecnologías como:

microservicios;
Redis;
WebSockets;
Django Channels;
event sourcing;
CQRS;

sin una necesidad real y sin explicárselo al usuario.

5. REGLA DE TRABAJO DEL AGENTE

El usuario NO quiere delegar completamente las decisiones técnicas al agente.

El agente debe actuar como acompañante técnico.

Cuando exista una decisión importante:

Explicar el problema.
Explicar las alternativas.
Explicar ventajas y desventajas.
Recomendar una opción cuando sea apropiado.
Explicar las consecuencias.
Preguntar al usuario.
Esperar confirmación antes de implementar cuando sea una decisión estructural.

Esto aplica especialmente a:

arquitectura;
modelos;
relaciones;
autenticación;
seguridad;
endpoints;
integraciones;
almacenamiento;
despliegue.

El agente puede escribir código cuando la decisión ya esté clara.

6. USUARIOS ADMINISTRATIVOS

Por ahora existe un único rol:

ADMINISTRATIVO

Cualquier usuario administrativo puede cambiar estados del servicio.

No crear inicialmente:

Técnico;
Supervisor;
Gerente;
Cliente;
otros roles. 7. AUTENTICACIÓN

Se utilizará un usuario personalizado basado en:

AbstractUser

El login será mediante:

username + password

NO utilizar el correo como credencial principal.

Django debe administrar:

hash de password;
autenticación;
permisos básicos;
sesión/token según la estrategia que se defina.
Usuario conceptual

Campos definidos:

id
nombre
apellido
username
password
rol
activo
fecha_creacion
ultimo_acceso

El agente debe revisar qué campos ya proporciona AbstractUser antes de crear campos duplicados.

8. CLIENTE SIN CUENTA

El cliente NO tendrá cuenta.

No habrá inicialmente:

registro de cliente;
contraseña de cliente;
login de cliente.

El cliente accederá a su servicio mediante un enlace privado.

Ejemplo:

/seguimiento/<token>/

También existirá un código humano del servicio:

SRV-2026-00125
Diferencia importante
Código

Identifica el servicio para humanos:

SRV-2026-00125
Token

Permite acceder de manera privada al seguimiento.

NO utilizar el ID numérico interno de PostgreSQL como token de seguridad.

El endpoint público debe devolver únicamente información autorizada para ese servicio.

9. FLUJO PRINCIPAL DEL NEGOCIO

El flujo aprobado es:

Cliente solicita servicio
↓
Empresa revisa
↓
Cotiza
↓
Cliente recibe cotización
↓
Aprobación
↓
Trabajo
↓
¿Costo adicional?
├── NO → continuar
│
└── SÍ
↓
Nueva cotización
↓
Nueva aprobación
↓
Continuar
↓
Pruebas
↓
Finalización
↓
Listo para entrega
↓
Entrega 10. SOLICITUD DEL SERVICIO

El cliente podrá solicitar un servicio desde la página.

La solicitud debe permitir capturar información suficiente para que la empresa conozca inicialmente:

quién solicita;
información de contacto;
empresa si aplica;
tipo de servicio;
descripción;
información del componente;
referencias disponibles;
fotografías si se decide habilitarlas en el formulario.

El detalle exacto del formulario se definirá antes de implementarlo.

NO inventar campos comerciales o técnicos que el cliente no haya solicitado.

11. WHATSAPP
    Función en el MVP

WhatsApp será un puente de comunicación.

La información oficial del servicio estará en el sistema.

Flujo:

Cliente solicita
↓
Sistema registra información
↓
Administrativo revisa
↓
WhatsApp ayuda a coordinar
↓
Sistema conserva el proceso oficial

WhatsApp puede utilizarse para:

primer contacto;
coordinar recolección;
coordinar entrega;
solicitar información;
comunicar avances;
recibir una aprobación informal.
Aprobación por WhatsApp

Ejemplo:

Cliente:

"Sí, hagamos el trabajo."

El administrativo registra esa aprobación en el sistema.

Debe quedar:

cotización;
resultado;
medio;
fecha;
usuario administrativo que registró;
observación.

WhatsApp NO es la fuente oficial de datos.

12. WHATSAPP BUSINESS API

NO es requisito del MVP.

Inicialmente se puede utilizar una acción del panel:

Notificar cliente

que abra WhatsApp con un mensaje preparado.

El administrativo decide enviarlo.

El sistema NO debe asumir que el mensaje fue enviado solo porque se abrió WhatsApp.

Futuro

Se podrá integrar WhatsApp Business API para automatizar:

cambios de estado;
solicitudes de aprobación;
costos adicionales;
servicio finalizado;
servicio listo para entrega;
otras notificaciones.

La integración debe ser modular para no acoplar el núcleo del sistema a WhatsApp.

13. NOTIFICACIONES

La intención futura es que el cliente no tenga que estar permanentemente mirando la página.

En el MVP, el sistema puede generar mensajes preparados para WhatsApp.

La automatización completa de WhatsApp queda para una fase posterior.

El seguimiento web sigue siendo la fuente oficial.

14. ESTADOS DEL SERVICIO

Estados definidos inicialmente:

SOLICITADO
EN_REVISION
COTIZANDO
ESPERANDO_APROBACION
EN_REPARACION
EN_PRUEBAS
FINALIZADO
LISTO_PARA_ENTREGA
ENTREGADO
NO_APROBADO
CANCELADO

Cualquier usuario administrativo puede cambiar estados.

El agente debe considerar si conviene validar las transiciones permitidas en backend.

Si esa política aún no está definida, debe preguntarla antes de bloquear transiciones.

15. APROBACIONES

La aprobación NO será un booleano simple dentro de Servicio.

Un servicio puede tener múltiples cotizaciones.

Una cotización puede requerir una aprobación.

Puede haber:

aprobación inicial;
aprobación adicional;
rechazo;
nueva cotización.

Por eso existe:

AprobacionServicio

16. INFORMACIÓN TÉCNICA

El banco de pruebas puede tener muchos parámetros diferentes dependiendo del componente.

Por eso NO se crearán inicialmente campos rígidos como:

presión;
RPM;
caudal;
temperatura;
etc.

La información técnica se manejará inicialmente de forma flexible mediante texto libre cuando corresponda.

Ejemplos:

diagnóstico;
trabajo realizado;
resultado de pruebas;
observaciones;
recomendaciones.
Importante

Todavía no está decidido exactamente en qué entidad/campos se almacenarán todos esos textos.

Cuando el agente llegue a esa parte debe preguntar antes de inventar una estructura.

17. FOTOGRAFÍAS

Las fotografías son una mejora aceptada porque permiten documentar:

recepción;
estado inicial;
diagnóstico;
reparación;
pruebas;
estado final.

No almacenar físicamente las imágenes en PostgreSQL.

Utilizar Cloudflare para almacenamiento.

La BD guarda:

URL/referencia;
descripción;
tipo;
visibilidad;
fecha;
usuario que la cargó.

Debe existir una bandera:

visible_cliente

para decidir qué imágenes puede ver el cliente.

Los límites de tamaño/cantidad de fotografías todavía deben definirse.

18. MODELO DE BASE DE DATOS

Las entidades aprobadas son:

Usuario
Cliente
Servicio
Componente
Cotizacion
DetalleCotizacion
AprobacionServicio
HistorialServicio
Fotografia

NO existe Entrega en el MVP.

19. ENTIDAD Usuario

Modelo Django:

Usuario

Base:

AbstractUser

Campos conceptuales:

Campo Descripción
id Identificador
nombre Nombre
apellido Apellido
username Login
password Gestionado por Django
rol Administrativo
activo Permite bloquear
fecha_creacion Creación
ultimo_acceso Último acceso

Rol actual:

ADMINISTRATIVO

20. ENTIDAD Cliente

Campos aprobados:

Campo Descripción
id Identificador
nombre Nombre/contacto
empresa Empresa
telefono Teléfono
whatsapp WhatsApp
email Correo
direccion Dirección
ciudad Ciudad
fecha_creacion Registro

Relación:

Cliente 1 -> N Servicio 21. ENTIDAD Servicio

Entidad central.

Campos aprobados:

Campo Descripción
id Identificador
codigo Código único
cliente Cliente relacionado
tipo_servicio Tipo cerrado
estado Estado actual
descripcion_solicitud Solicitud
fecha_solicitud Fecha
fecha_recepcion Recepción física
fecha_finalizacion Finalización
fecha_entrega Entrega
token_seguimiento Token privado
observaciones_internas Información interna
activo Control
Tipo de servicio

Opciones cerradas:

DIAGNOSTICO
REPARACION
MANTENIMIENTO
PRUEBA
OTRO

NO crear una tabla independiente para tipos de servicio por ahora.

22. ENTIDAD Componente

Un servicio puede tener varios componentes.

Relación:

Servicio 1 -> N Componente

Campos:

Campo Descripción
id Identificador
servicio Servicio
tipo Tipo de componente
marca Marca
referencia Referencia
descripcion Descripción
cantidad Cantidad
IMPORTANTE

NO existe numero_serie.

23. ENTIDAD Cotizacion

Un servicio puede tener múltiples cotizaciones.

Campos:

Campo Descripción
id Identificador
servicio Servicio
numero Número de cotización
tipo Inicial / adicional
descripcion Descripción
total Total neto
estado Estado
fecha_creacion Creación
observaciones Observaciones
creada_por Usuario
Tipo
INICIAL
ADICIONAL
Estado
PENDIENTE
APROBADA
RECHAZADA
Precio

La empresa entrega un valor total neto.

NO utilizar:

subtotal;
impuestos;
fecha de vencimiento. 24. ENTIDAD DetalleCotizacion

Una cotización puede tener múltiples ítems.

Relación:

Cotizacion 1 -> N DetalleCotizacion

Campos:

Campo Descripción
id Identificador
cotizacion Cotización
descripcion Descripción del ítem
valor Valor
cantidad Cantidad

Ejemplo:

Cambio de sellos $200.000
Rectificación $300.000
Mano de obra $250.000
Prueba en banco $100.000

---

Total $850.000

No implementar impuestos ni subtotal.

El campo total representa el valor oficial presentado por la empresa.

25. ENTIDAD AprobacionServicio

Campos aprobados:

Campo Descripción
id Identificador
cotizacion Cotización
resultado Aprobada/Rechazada
medio Web/WhatsApp/etc.
fecha Momento
usuario_registro Administrativo
observacion Constancia
ip IP cuando aplique
fecha_registro Registro
Resultado
APROBADA
RECHAZADA
Medio
WEB
WHATSAPP
LLAMADA
PRESENCIAL
OTRO

Cuando la aprobación ocurre externamente, usuario_registro identifica al administrativo que la registra.

Cuando la aprobación ocurre por la web, debe registrarse como:

WEB

La implementación exacta de cómo representar usuario_registro para una acción pública debe analizarse antes de crear una solución improvisada.

26. ENTIDAD HistorialServicio

Campos:

Campo Descripción
id Identificador
servicio Servicio
estado Estado alcanzado
comentario Descripción
fecha Fecha/hora
usuario Usuario administrativo
visible_cliente Visible al cliente

El estado actual está en:

Servicio.estado

El historial conserva la trazabilidad.

Ejemplo:

25/09 — Servicio recibido
26/09 — Diagnóstico realizado
26/09 — Cotización enviada
27/09 — Cliente aprobó
27/09 — Reparación iniciada

No todo comentario interno debe ser visible al cliente.

27. ENTIDAD Fotografia

Campos:

Campo Descripción
id Identificador
servicio Servicio
url URL/referencia Cloudflare
descripcion Descripción
tipo Recepción/diagnóstico/etc.
visible_cliente Visibilidad
fecha Fecha
subida_por Usuario

Tipos inicialmente considerados:

RECEPCION
DIAGNOSTICO
REPARACION
PRUEBA
OTRO

Si el agente considera que falta un tipo importante, debe consultarlo antes de modificar la decisión.

28. RELACIONES COMPLETAS
    Usuario 1 -> N HistorialServicio
    Usuario 1 -> N Cotizacion
    Usuario 1 -> N Fotografia
    Usuario 1 -> N AprobacionServicio

Cliente 1 -> N Servicio

Servicio 1 -> N Componente
Servicio 1 -> N HistorialServicio
Servicio 1 -> N Fotografia
Servicio 1 -> N Cotizacion

Cotizacion 1 -> N DetalleCotizacion
Cotizacion 1 -> N AprobacionServicio

Visualmente:

Usuario
|
+----< HistorialServicio
|
+----< Cotizacion
|
+----< Fotografia
|
+----< AprobacionServicio

Cliente
|
+----< Servicio
|
+----< Componente
|
+----< HistorialServicio
|
+----< Fotografia
|
+----< Cotizacion
|
+----< DetalleCotizacion
|
+----< AprobacionServicio 29. REGLA IMPORTANTE SOBRE EL MODELO

El agente NO debe agregar automáticamente:

número de serie;
subtotal;
impuestos;
fecha de vencimiento;
entrega como entidad;
roles adicionales;
cuenta de cliente;
parámetros rígidos de banco de pruebas.

Si considera que alguna de estas cosas es necesaria técnicamente, debe explicar por qué y pedir autorización.

30. SEGUIMIENTO DEL CLIENTE

Ruta conceptual:

/seguimiento/<token>/

El cliente puede ver solamente SU servicio.

Ejemplo:

Servicio: SRV-2026-00125

Estado actual:
EN REPARACION

Componentes:

- Bomba hidráulica
- Válvula

Historial:
✓ Solicitud recibida
✓ Cotización enviada
✓ Cotización aprobada
✓ Reparación iniciada
○ Pruebas
○ Entrega

Si hay cotización pendiente:

Cotización pendiente de aprobación

Total: $850.000

[Ver cotización]
[Aprobar]
[No aprobar]

La aprobación web debe crear un registro en:

AprobacionServicio

31. API PÚBLICA VS ADMINISTRATIVA
    API administrativa

Requiere autenticación.

Ejemplos conceptuales:

/api/login/
/api/servicios/
/api/cotizaciones/
/api/aprobaciones/
/api/historial/
/api/fotografias/
API pública

No requiere login, pero requiere token privado.

Ejemplo:

/api/seguimiento/<token>/

La API pública debe usar una representación específica de los datos.

No exponer directamente todos los campos internos del modelo.

32. SEGURIDAD

El backend debe controlar:

autenticación;
permisos;
acceso administrativo;
acceso mediante token;
datos visibles al cliente.

No confiar en React para ocultar información.

El token de seguimiento debe ser suficientemente impredecible.

El ID interno de la BD no debe utilizarse como mecanismo de autorización.

El agente debe plantear medidas adicionales de seguridad antes de publicar el endpoint de seguimiento.

33. ACTUALIZACIÓN DEL SEGUIMIENTO

No implementar WebSockets inicialmente.

Se puede utilizar TanStack Query con polling/refetch periódico.

Conceptualmente:

Cliente abre seguimiento
↓
GET seguimiento
↓
muestra estado
↓
cada cierto intervalo
↓
GET nuevamente

El intervalo exacto se decidirá durante implementación.

34. FRONTEND

Estructura conceptual:

src/
├── pages/
│ ├── Inicio
│ ├── Nosotros
│ ├── Servicios
│ ├── SolicitarServicio
│ ├── Seguimiento
│ └── Admin
│
├── components/
│ ├── EstadoServicio
│ ├── TimelineServicio
│ ├── FormularioServicio
│ ├── Cotizacion
│ └── ...
│
├── services/
│ └── ...
│
├── hooks/
│ └── ...
│
└── ...

Esto es una propuesta conceptual, NO una estructura obligatoria.

El agente debe revisar el proyecto existente antes de reorganizar carpetas.

No destruir estructuras existentes sin autorización.

35. TANSTACK QUERY

Usar TanStack Query para datos provenientes del servidor cuando corresponda.

No duplicar innecesariamente en useState información que pertenece al estado del servidor.

El agente debe explicar al usuario:

query keys;
cache;
invalidación;
refetch;
mutations;

cuando estas partes entren en el proyecto.

36. PANEL ADMINISTRATIVO

Debe permitir como mínimo:

Login
↓
Dashboard
↓
Servicios
├── Solicitudes
├── En revisión
├── Cotizando
├── Esperando aprobación
├── En reparación
├── En pruebas
├── Finalizados
└── Entregados

Desde un servicio:

Información del cliente
Componentes
Cotizaciones
Aprobaciones
Historial
Fotografías
Estado
Seguimiento
WhatsApp 37. COTIZACIONES

Una cotización puede tener varios detalles.

Ejemplo:

Cotización #COT-001

Cambio de sellos $200.000
Rectificación $300.000
Mano de obra $250.000

TOTAL $750.000

No existen:

subtotal;
impuestos;
vencimiento.

Un servicio puede tener:

Cotización inicial
↓
Aprobada
↓
Trabajo
↓
Cotización adicional
↓
Aprobada 38. COSTOS ADICIONALES

Si durante el trabajo aparece un costo no contemplado:

El administrativo/técnico identifica el adicional.
Se genera una cotización adicional.
El cliente es notificado.
Se espera aprobación.
Si aprueba, se continúa.
Si rechaza, debe seguirse la política que se defina.

La política exacta para rechazo de adicionales todavía NO está definida.

Preguntar antes de implementarla.

39. CATÁLOGO / PRESENTACIÓN DE PRODUCTOS

La empresa no quiere necesariamente mostrar un catálogo completo con todas las referencias.

Cada pieza puede tener demasiadas referencias y mostrar toda esa información puede no ser conveniente para el negocio.

La web puede mostrar:

categorías;
marcas;
fotografías;
aplicaciones;
soluciones;
servicios;
ejemplos de productos.

No asumir que un componente mostrado públicamente está disponible para compra inmediata.

El proyecto principal es gestión de servicios, no e-commerce.

40. COSAS FUERA DEL MVP

No implementar inicialmente:

carrito;
pagos;
inventario público;
e-commerce;
cuenta de cliente;
app móvil;
chat interno;
WhatsApp Business API;
WebSockets;
Redis;
Django Channels;
Google Calendar obligatorio;
facturación electrónica;
sistema contable;
entidad Entrega;
parámetros estructurados de banco de pruebas;
múltiples roles administrativos. 41. INTEGRACIONES FUTURAS
WhatsApp Business API

Para automatizar comunicaciones.

Google Calendar

Para citas y coordinación.

Correo

Para notificaciones.

PDF

Para cotizaciones.

Firma digital

Para aprobaciones más formales.

Parámetros estructurados de pruebas

Si posteriormente se determina que los textos libres no son suficientes.

Estas integraciones no deben condicionar el MVP.

42. ORDEN DE DESARROLLO RECOMENDADO
    Fase 1 — Backend base
    Crear/revisar proyecto Django.
    Crear app usuarios.
    Configurar AUTH_USER_MODEL.
    Crear Usuario.
    Migraciones.
    Crear app servicios.
    Crear modelos.
    Revisar relaciones.
    Migraciones.
    Django Admin.
    Fase 2 — API
    Serializers.
    URLs.
    Views/ViewSets.
    Autenticación.
    Permisos.
    API pública de seguimiento.
    API de aprobación.
    API de aprobación externa.
    Historial.
    Fotografías.
    Fase 3 — Frontend público
    Landing.
    Nosotros.
    Servicios.
    Contacto.
    Solicitud.
    Seguimiento.
    Fase 4 — Panel
    Login.
    Dashboard.
    Servicios.
    Detalle.
    Estados.
    Cotizaciones.
    Aprobaciones.
    Historial.
    Fotografías.
    WhatsApp.
    Fase 5 — Pruebas

Probar el flujo completo:

Solicitud
→ revisión
→ cotización
→ aprobación
→ reparación
→ adicional
→ nueva aprobación
→ pruebas
→ finalización
→ entrega 43. DECISIONES PENDIENTES

El agente debe preguntar antes de llegar a estas implementaciones:

Formato exacto del token.
Longitud del token.
Formato automático del código de servicio.
Reglas de transición entre estados.
Qué ocurre cuando se rechaza una cotización.
Qué ocurre cuando se rechaza un costo adicional.
Campos definitivos para información técnica.
Límites de fotografías.
Configuración exacta de Cloudflare.
Estrategia concreta de autenticación de API.
Formato definitivo de mensajes de WhatsApp.
Qué información técnica se muestra al cliente.
Política de edición de cotizaciones.
Política de eliminación de servicios.
Si una cotización rechazada puede volver a enviarse.
Diseño visual definitivo. 44. POLÍTICA DE CAMBIOS DE BASE DE DATOS

Antes de cambiar un modelo:

Explicar qué problema resuelve.
Explicar qué campo/relación se agregaría.
Explicar el impacto sobre migraciones.
Explicar impacto en API.
Explicar impacto en frontend.
Preguntar si el usuario aprueba.

No modificar silenciosamente el esquema.

45. POLÍTICA DE CÓDIGO

El usuario quiere aprender.

Por eso, cuando se implemente una pieza importante:

explicar qué archivo se modifica;
explicar por qué;
explicar qué problema resuelve;
explicar cómo se conecta con las demás capas.

Evitar entregar grandes cantidades de código sin explicación cuando el usuario esté aprendiendo una parte nueva.

Si el usuario pide específicamente el código completo, entregarlo completo.

46. POLÍTICA SOBRE EL PROYECTO EXISTENTE

Antes de crear una estructura nueva:

inspeccionar la estructura actual;
identificar qué ya existe;
reutilizar código cuando sea adecuado;
no reemplazar archivos existentes sin entenderlos;
no cambiar estilos/layouts importantes sin autorización.

El usuario ya posee experiencia con:

React;
Vite;
TypeScript;
Django;
Django REST Framework;
TanStack Query;
despliegue en Render;
Neon;
Cloudflare.

Las explicaciones pueden partir de ese contexto, pero no asumir que conoce una tecnología nueva sin explicarla.

47. RESUMEN DE LA BASE DE DATOS
    USUARIO
    ├── id
    ├── nombre
    ├── apellido
    ├── username
    ├── password
    ├── rol
    ├── activo
    ├── fecha_creacion
    └── ultimo_acceso

CLIENTE
├── id
├── nombre
├── empresa
├── telefono
├── whatsapp
├── email
├── direccion
├── ciudad
└── fecha_creacion

SERVICIO
├── id
├── codigo
├── cliente
├── tipo_servicio
├── estado
├── descripcion_solicitud
├── fecha_solicitud
├── fecha_recepcion
├── fecha_finalizacion
├── fecha_entrega
├── token_seguimiento
├── observaciones_internas
└── activo

COMPONENTE
├── id
├── servicio
├── tipo
├── marca
├── referencia
├── descripcion
└── cantidad

COTIZACION
├── id
├── servicio
├── numero
├── tipo
├── descripcion
├── total
├── estado
├── fecha_creacion
├── observaciones
└── creada_por

DETALLE_COTIZACION
├── id
├── cotizacion
├── descripcion
├── valor
└── cantidad

APROBACION_SERVICIO
├── id
├── cotizacion
├── resultado
├── medio
├── fecha
├── usuario_registro
├── observacion
├── ip
└── fecha_registro

HISTORIAL_SERVICIO
├── id
├── servicio
├── estado
├── comentario
├── fecha
├── usuario
└── visible_cliente

FOTOGRAFIA
├── id
├── servicio
├── url
├── descripcion
├── tipo
├── visible_cliente
├── fecha
└── subida_por 48. RELACIÓN FINAL
Usuario
├──< Cotizacion
├──< AprobacionServicio
├──< HistorialServicio
└──< Fotografia

Cliente
└──< Servicio
├──< Componente
├──< Cotizacion
│ ├──< DetalleCotizacion
│ └──< AprobacionServicio
├──< HistorialServicio
└──< Fotografia 49. INSTRUCCIÓN FINAL PARA EL AGENTE

Este proyecto debe desarrollarse de forma incremental.

Antes de implementar una etapa importante:

Leer este documento.
Revisar el código existente.
Identificar qué decisiones ya están cerradas.
Identificar qué decisiones están pendientes.
Explicar la propuesta técnica.
Preguntar cualquier decisión importante que falte.
Esperar confirmación cuando corresponda.
Implementar.
Probar.
Explicar qué cambió.

No inventar reglas empresariales.

No modificar la base de datos por conveniencia técnica sin explicarlo.

No convertir el proyecto en un sistema más complejo de lo necesario.

La plataforma debe mantenerse alineada con este flujo:

CLIENTE
↓
SOLICITUD
↓
REVISIÓN
↓
COTIZACIÓN
↓
APROBACIÓN
↓
TRABAJO
↓
¿ADICIONAL?
↓
NUEVA COTIZACIÓN
↓
NUEVA APROBACIÓN
↓
PRUEBAS
↓
FINALIZACIÓN
↓
ENTREGA

La información oficial vive en el sistema.

WhatsApp es un canal de comunicación.

El cliente no necesita una cuenta.

El administrativo sí tiene cuenta.

El seguimiento se realiza mediante un token privado.

La base de datos definida en este documento es la referencia funcional actual y solo debe cambiarse después de discutir y aprobar el cambio.
