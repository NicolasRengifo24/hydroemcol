# Spec 004 — Login del panel administrativo

Estado: aprobada

## Contexto y objetivo

El panel administrativo es la Fase 4 del proyecto. Hoy `/admin` es un placeholder y no
existe ninguna forma de iniciar sesión desde el frontend: no hay pantalla de acceso ni capa
de API que maneje credenciales. El backend ya emite credenciales con SimpleJWT
(`/api/token/` y `/api/token/refresh/`), pero el flujo por defecto devuelve ambos tokens en
el cuerpo de la respuesta, lo que obliga al navegador a guardarlos donde JavaScript puede
leerlos.

El objetivo es que un usuario **administrativo** (único rol del sistema) inicie sesión con
username + password y opere el panel, con estas garantías:

- el acceso lo autoriza siempre el backend, no la interfaz;
- la credencial de mayor valor (token de refresco) queda fuera del alcance de JavaScript;
- el cierre de sesión y la expiración **revocan de verdad** el acceso, no solo lo ocultan.

La seguridad se trata como requisito de primer nivel (`CONTEXTO_MAESTRO.md` §32: la
seguridad se resuelve en el backend).

## Usuarios

- **Administrativo** — único rol existente (§6). Es el único que inicia sesión y opera el
  panel. Cualquier administrativo puede hacer todo lo que permite el panel.
- **Cliente final** — no tiene cuenta, no inicia sesión y queda **fuera del alcance** de esta
  spec.

## Historias de usuario

- HU-1. Como administrativo, quiero iniciar sesión con mi usuario y mi contraseña para
  acceder al panel.
- HU-2. Como administrativo, quiero que mi sesión se renueve sola mientras trabajo, sin
  volver a escribir la contraseña.
- HU-3. Como administrativo, quiero cerrar sesión y que ese cierre sea efectivo, para dejar
  el panel inaccesible en ese navegador.
- HU-4. Como responsable del sistema, quiero que las credenciales no queden expuestas a un
  ataque de XSS y que los intentos de fuerza bruta estén limitados.
- HU-5. Como visitante sin sesión, no debo poder ver datos del panel: si intento abrirlo,
  debo terminar en la pantalla de acceso.

## Definiciones

- **Token de acceso:** credencial de vida corta que acompaña cada petición al panel.
- **Token de refresco:** credencial de vida más larga que permite obtener un nuevo token de
  acceso sin volver a introducir credenciales.
- **Cookie httpOnly:** cookie que el navegador envía automáticamente pero que JavaScript **no
  puede leer**.
- **Revocación (lista negra):** invalidación de un token de refresco para que no pueda
  reutilizarse aunque todavía no haya expirado.
- **Sesión válida:** el navegador del administrativo conserva un token de refresco vigente y
  no revocado.
- **Duración de credenciales:** el token de acceso dura **15 minutos** y el token de refresco
  dura **1 día**.

## Requisitos funcionales

### Inicio de sesión

- **RF-1.** CUANDO el administrativo envía un username y una password que coinciden con una
  cuenta activa, EL SISTEMA le concede el acceso al panel y da por iniciada su sesión.
- **RF-2.** CUANDO el inicio de sesión es válido, EL SISTEMA entrega el token de acceso en el
  cuerpo de la respuesta y establece el token de refresco en una cookie httpOnly.
- **RF-3.** EL SISTEMA mantiene el token de acceso únicamente en memoria del cliente y nunca
  lo persiste en un almacenamiento legible por JavaScript (no localStorage, no sessionStorage).
- **RF-4.** SI el username o la password no son correctos, ENTONCES EL SISTEMA responde con el
  mensaje genérico «Usuario o contraseña incorrectos», sin indicar cuál de los dos falló.
- **RF-5.** SI las credenciales corresponden a una cuenta inactiva (`is_active` falso),
  ENTONCES EL SISTEMA rechaza el acceso con el mismo mensaje genérico de RF-4, sin revelar que
  la cuenta existe.
- **RF-6.** CUANDO un inicio de sesión es válido, EL SISTEMA actualiza el último acceso del
  usuario.

### Renovación, rotación y expiración

- **RF-7.** MIENTRAS exista un token de acceso vigente, EL SISTEMA permite al administrativo
  consumir los endpoints administrativos.
- **RF-8.** CUANDO el token de acceso expira y el token de refresco sigue vigente, EL SISTEMA
  renueva la sesión sin volver a pedir credenciales.
- **RF-9.** CUANDO se emite un token de acceso nuevo por renovación, EL SISTEMA rota el token
  de refresco e invalida el anterior (lo revoca).
- **RF-10.** SI el token de refresco falta, está expirado o ha sido revocado, ENTONCES EL
  SISTEMA rechaza la renovación y la interfaz conduce al administrativo a la pantalla de
  acceso.
- **RF-11.** SI un token de refresco ya rotado se presenta de nuevo, ENTONCES EL SISTEMA lo
  rechaza (no se admite reutilización).

### Cierre de sesión

- **RF-12.** CUANDO el administrativo cierra sesión, EL SISTEMA revoca el token de refresco,
  elimina la cookie httpOnly y descarta el token de acceso.
- **RF-13.** MIENTRAS el cierre de sesión se completa, EL SISTEMA impide reutilizar cualquier
  credencial anterior para entrar al panel.

### Protección de rutas del panel

- **RF-14.** SI un visitante sin sesión válida intenta abrir cualquier ruta del panel,
  ENTONCES EL SISTEMA lo redirige a la pantalla de acceso.
- **RF-15.** MIENTRAS no exista una sesión válida, EL SISTEMA no muestra en el cliente ningún
  dato del panel.
- **RF-16.** EL SISTEMA garantiza que las rutas administrativas solo devuelven datos cuando la
  petición está autenticada, con independencia de lo que haga el cliente.
- **RF-17.** SI una cuenta se desactiva mientras tiene sesión abierta, ENTONCES EL SISTEMA
  rechaza sus siguientes peticiones aunque su token de acceso todavía no haya expirado.

### Protección contra fuerza bruta

- **RF-18.** SI se superan los intentos de inicio de sesión fallidos permitidos desde el mismo
  origen dentro de una ventana de tiempo, ENTONCES EL SISTEMA responde rechazando la petición
  sin evaluar las credenciales, e informa al usuario de que debe esperar. El límite es de **5
  fallos por minuto y por IP**, y solo contabiliza credenciales inválidas o correspondientes a
  cuentas inactivas; los inicios de sesión válidos y las peticiones a otros endpoints NO
  consumen el límite.
- **RF-19.** EL SISTEMA aplica la limitación de intentos **únicamente** al inicio de sesión, y
  no al resto de endpoints del panel.

### Trazabilidad

- **RF-20.** EL SISTEMA deja constancia de los intentos de inicio de sesión (correctos y
  fallidos) con su fecha y su resultado, como parte del principio de trazabilidad, mediante
  logs de aplicación. Esta trazabilidad NO requiere un modelo persistente de intentos ni una
  migración adicional.

## Requisitos no funcionales

- **RNF-1.** La cookie del token de refresco es httpOnly, `Secure` y con `SameSite` restrictivo,
  de modo que JavaScript no puede leerla y solo se envía por HTTPS en producción.
- **RNF-2.** Las rutas que dependen de la cookie httpOnly (renovación y cierre de sesión) están
  protegidas contra CSRF.
- **RNF-3.** En producción el sistema opera con `DEBUG` desactivado, `SECRET_KEY` provista por
  entorno y la conexión servida por HTTPS.
- **RNF-4.** En producción CORS queda restringido al dominio real del frontend.
- **RNF-5.** Ninguna credencial, secreto ni contraseña se expone en el frontend ni se registra
  en claro en los registros.
- **RNF-6.** Las contraseñas se almacenan siempre con el hash de Django y nunca se devuelven ni
  se muestran.
- **RNF-7.** Los mensajes de error de autenticación son genéricos y no distinguen usuario
  inexistente de contraseña incorrecta ni de cuenta inactiva (verificable en los tres casos).

## Casos límite

- **Recarga de la página:** al recargar, el token de acceso en memoria se pierde; el sistema
  debe recuperar la sesión con el token de refresco sin pedir credenciales, o llevar al login
  si el refresco ya no es válido.
- **Varias pestañas:** el token de acceso es por pestaña; el token de refresco es compartido.
  Cerrar sesión en una pestaña debe dejar inutilizable la sesión en las demás.
- **Token de refresco agotado tras una ausencia larga:** el sistema conduce al login sin
  mostrar un error técnico.
- **`is_active` cambiado a falso con la sesión abierta:** la siguiente petición se rechaza
  (RF-17) y la interfaz vuelve al login.
- **Origen limitado por fuerza bruta:** el límite de 5 fallos por minuto aplica por IP y solo
  cuenta credenciales inválidas o cuentas inactivas, de modo que un atacante no puede inferir
  la existencia de un usuario por el tipo de respuesta.

## Fuera de alcance

- Recuperación / restablecimiento de contraseña.
- Alta y gestión de usuarios administrativos (se sigue haciendo por el administrador de Django).
- Segundo factor de autenticación (2FA) y cualquier inicio de sesión social.
- Roles adicionales o permisos diferenciados (§6, §29).
- Cuenta, login o registro para el cliente final (§8).
- Cambios en el modelo de datos distintos de los que exija, si acaso, la revocación de tokens.

## Criterios de finalización

1. Un administrativo con credenciales válidas entra al panel; las credenciales inválidas
   reciben siempre el mensaje genérico.
2. Una cuenta inactiva no puede entrar y su rechazo es indistinguible del de una contraseña
   errónea.
3. El token de acceso no es accesible a JavaScript; el de refresco viaja en cookie httpOnly.
4. La sesión se renueva sin pedir credenciales mientras el refresco sea válido, y la renovación
   rota el refresco.
5. Cerrar sesión revoca el refresco: reutilizarlo no da acceso.
6. Una ruta del panel abierta sin sesión termina en la pantalla de acceso.
7. Existe un límite de intentos de login verificable y solo afecta al login.
8. Los intentos de login quedan registrados con fecha y resultado.
9. Los casos límite anteriores están cubiertos.

## Decisiones cerradas

- Las duraciones aprobadas son 15 minutos para el token de acceso y 1 día para el token de
  refresco.
- El throttling permite como máximo 5 fallos por minuto y por IP, y solo contabiliza
  credenciales inválidas o cuentas inactivas. Los logins válidos no consumen el límite.
- RF-20 se implementa mediante logs de aplicación de los intentos correctos y fallidos; no se
  crea un modelo de intentos ni una migración para esta trazabilidad.
