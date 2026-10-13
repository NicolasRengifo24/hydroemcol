# Plan — Spec 004: Login del panel administrativo

## Estado y fuente de verdad

La spec aprobada no está guardada físicamente: `specs/004-login-admin/spec.md` existe pero está
vacía. Este plan usa como fuente de verdad el contrato aprobado entregado por el usuario. Antes de
implementar, el usuario debe guardar la spec aprobada en `spec.md`; no se debe implementar contra
este documento como sustituto permanente. Este plan describe el cómo, sin añadir roles, reglas de
negocio ni dependencias.

La implementación usará únicamente Django/DRF, SimpleJWT, el caché ya disponible y las
dependencias presentes. No se introducen Redis, WebSockets, Channels, modelos de intentos ni
dependencias frontend nuevas.

## 1. Trazabilidad del contrato

Para hacer verificable el plan, se usan estas etiquetas operativas (deben conservarse al guardar la
spec):

| Etiqueta | Alcance |
|---|---|
| RF-01 | Login con username/password, rol ADMINISTRATIVO y autorización backend. |
| RF-02 | Access token en memoria, duración de 15 minutos y renovación. |
| RF-03 | Refresh en cookie host-only, `Path=/api/`, httpOnly, SameSite y Secure por entorno. |
| RF-04 | CSRF público y protección CSRF de login, refresh y logout. |
| RF-05 | Rotación, blacklist y revocación de reutilización/concurrencia. |
| RF-06 | Logout idempotente, 204 y eliminación de cookie. |
| RF-07 | Errores de autenticación genéricos y redirección frontend ante 401. |
| RF-08 | Throttling de login: cinco fallos por minuto e IP. |
| RF-09 | Logs de seguridad sin secretos ni datos sensibles. |
| RF-10 | Rutas `/admin/login` y protección del panel administrativo. |
| RF-11 | Cliente HTTP con credenciales, single-flight y recuperación ante 401. |
| RNF-01 | Configuración por entorno y producción segura (hosts, CORS, HTTPS/proxy). |
| RNF-02 | Sin exposición de password, tokens, cookies, Authorization ni CSRF en logs. |
| RNF-03 | Compatibilidad responsive, accesible y con feedback de carga/error. |
| RNF-04 | Sin dependencias nuevas ni tecnologías excluidas. |
| RNF-05 | Pruebas exclusivamente con `manage.py test` y `django.test`. |

## 2. Archivos y responsabilidades

### Backend

| Archivo | Responsabilidad | RF/RNF |
|---|---|---|
| `backend/config/settings.py` | Activar `rest_framework_simplejwt.token_blacklist`, configurar duraciones, rotación/blacklist, cookies, CSRF, CORS con credenciales, caché y variables de entorno para hosts/orígenes/HTTPS. | RF-02–05, RF-08, RNF-01, RNF-04 |
| `backend/config/urls.py` | Publicar exactamente `/api/login/`, `/api/refresh/`, `/api/logout/` y `/api/csrf/`; conservar las rutas de negocio sin modificar su contrato. | RF-01–06 |
| `backend/usuarios/views.py` | Vistas DRF para login, refresh, logout y CSRF; autenticar username/password, comprobar activo y rol, emitir cookies/tokens, devolver códigos y mensajes contractuales, y registrar eventos seguros. | RF-01–09 |
| `backend/usuarios/models.py` | Mantener `Usuario(AbstractUser)` y el único rol existente. No requiere cambio de modelo. | RF-01, RNF-04 |
| `backend/requirements.txt` | No cambiar: SimpleJWT, DRF, CORS y Django ya están instalados. | RNF-04 |
| `backend/usuarios/tests.py` | Tests `django.test` de vistas, cookies, CSRF, throttling, logs y revocación. | RF-01–09, RNF-02, RNF-05 |
| `backend/config/tests.py` (si se necesita crear módulo de tests) | Tests de configuración/contratos de endpoints sin duplicar pruebas de negocio. | RF-03–05, RNF-01, RNF-05 |
| `backend/usuarios/migrations/...` | No se crea migración de usuario. La única migración prevista es la estándar de `token_blacklist`, ejecutada después de añadir la app y antes de probar rotación/blacklist. | RF-05, RNF-04 |

### Frontend

| Archivo | Responsabilidad | RF/RNF |
|---|---|---|
| `frontend/src/services/api.ts` | Cliente HTTP con base configurable, `credentials: include`, CSRF legible, access token solo en memoria, reintento coordinado single-flight y limpieza/redirección ante refresh 401. | RF-02–07, RF-11 |
| `frontend/src/pages/Admin.tsx` | Formulario accesible de login y estado protegido del panel; no decide permisos, solo muestra la respuesta backend. | RF-01, RF-07, RF-10, RNF-03 |
| `frontend/src/router.tsx` | Rutas `/admin/login` pública y `/admin` protegida por una guardia basada en el estado de memoria; la guardia no reemplaza autorización backend. | RF-07, RF-10 |
| `frontend/src/main.tsx` | Proveer el contexto mínimo de autenticación si se requiere para que router, cliente HTTP y página compartan el access token en memoria. | RF-02, RF-10, RF-11 |
| `frontend/package.json` | Sin dependencias nuevas; la verificación frontend será `npm run build` y `npm run lint`, no un runner de tests. | RNF-03, RNF-04 |

No se modifica `backend/usuarios/models.py` salvo que la implementación revele una contradicción
con el modelo existente; el contrato ya está cubierto por `is_active` y `rol`. No se agrega un
modelo de intentos de login.

## 3. Interfaces y contratos

### HTTP

- `GET /api/csrf/`: público; establece/renueva la cookie CSRF legible por JavaScript y devuelve un
  resultado mínimo. No devuelve access ni refresh token.
- `POST /api/login/`: recibe `{username, password}` y exige `X-CSRFToken`. En éxito devuelve el
  access token y establece `refresh_token`; el refresh no aparece en JSON. Credenciales inválidas,
  usuario inactivo o rol distinto devuelven `401` con el mensaje genérico aprobado.
- `POST /api/refresh/`: exige `X-CSRFToken` y toma el refresh exclusivamente de la cookie. Rota el
  refresh, invalida el anterior y establece la nueva cookie; un refresh inválido/reutilizado devuelve
  `401` y no entrega token.
- `POST /api/logout/`: exige CSRF; intenta invalidar el refresh y siempre elimina la cookie y
  responde `204`, incluso sin cookie, access o refresh válido.

La cookie `refresh_token` será httpOnly, sin `Domain`, `Path=/api/`, `SameSite=Lax` y `Secure=True`
en producción. Si frontend y backend terminan en sitios distintos, la configuración debe cambiarse
explícitamente a `SameSite=None` junto con `Secure=True`; no se infiere automáticamente.

### Estado frontend

```text
accessToken: string | null                 // memoria, nunca localStorage/sessionStorage
refreshEnCurso: Promise<string | null> | null
sesion: "anonima" | "autenticando" | "autenticada"
```

El módulo de API deberá exponer operaciones equivalentes a `obtenerCsrf`, `iniciarSesion`,
`refrescarSesion`, `cerrarSesion` y `apiRequest`. Sus nombres concretos quedan sujetos a las
convenciones existentes, pero no se debe exponer el refresh al código React.

## 4. Funciones puras y determinismo

La lógica que no necesita Django debe separarse y recibir `hoy` explícitamente, en vez de leer el
reloj del sistema. Puede vivir en un módulo de usuarios si la implementación lo considera útil:

```text
ventanaThrottling(hoy, fallosPrevios) -> fallosVigentes
debeBloquearLogin(hoy, fallosPrevios, maximo=5) -> boolean
usernameParcial(username) -> string
normalizarOrigen(origen) -> string
```

`hoy` es el instante de referencia para descartar fallos fuera de un minuto y verificar límites.
Estas funciones no consultan base de datos, caché, entorno ni `timezone.now()`. La vista aporta el
instante actual y persiste/consulta el estado en caché. La creación de mensajes de log debe recibir
datos ya saneados y nunca el request completo sin filtrar.

La coordinación single-flight del frontend es estado de ejecución, no una función pura: si varios

## 5. Algoritmos y pseudocódigo

### Login y throttling

```text
POST login(request):
    validar CSRF antes de procesar credenciales
    ip = obtener IP del request según configuración de proxy confiable
    si debeBloquearLogin(hoy, cache[ip]): devolver 429 sin intentar autenticar
    usuario = autenticar(username, password)
    si usuario inexistente, password incorrecta o inactivo:
        registrar fallo en cache durante un minuto
        registrar evento sin secretos
        devolver 401 genérico
    si usuario.rol != ADMINISTRATIVO:
        no conceder acceso; registrar resultado sin revelar la razón al cliente; devolver 401 genérico
    limpiar fallos de ese IP según la política de ventana
    emitir access de 15 minutos y refresh rotado en cookie
    registrar éxito seguro
    devolver access
```

Solo los tres fallos indicados cuentan: usuario inexistente, password incorrecta e inactivo. Un rol
no autorizado no crea un nuevo rol ni debe revelar información del usuario. El throttling usa el
caché configurado sin Redis; su limitación multi-instancia en Render queda documentada como
limitación operativa, no se resuelve añadiendo infraestructura.

### Refresh, reutilización y logout

```text
refresh(request):
    validar CSRF
    leer refresh_token de cookie
    si falta, es inválido, está expirado o está blacklisteado: 401
    validar usuario activo y ADMINISTRATIVO
    rotar: blacklistear token usado y emitir nuevo access + refresh
    fijar cookie con atributos contractuales

si se detecta reutilización de refresh:
    blacklistear todos los refresh vigentes del usuario
    devolver 401

logout(request):
    validar CSRF
    si existe refresh válido, blacklistearlo; ignorar ausencia/invalidez
    borrar cookie con los mismos atributos de Path/SameSite/Secure
    responder 204
```

La detección de reutilización debe distinguir un token rotado ya invalidado de un token simplemente
expirado o malformado; ambos producen 401, pero solo el primero dispara la revocación global del
usuario. La operación debe ser segura ante repetición y no devolver secretos en ningún caso.

### Cliente HTTP y rutas

```text
apiRequest(request):
    adjuntar credentials: include y Authorization si accessToken existe
    si método mutante de auth: obtener cookie CSRF y adjuntar X-CSRFToken
    enviar petición
    si 401 y no es login/refresh/logout:
        si no existe refreshEnCurso: iniciar un único refresh
        esperar refreshEnCurso
        si access nuevo: repetir una sola vez la petición original
        si refresh falla: limpiar memoria y navegar a /admin/login
    propagar resultado/error al consumidor
```

La ruta `/admin/login` no debe quedar atrapada por la guardia. `/admin` y sus futuras rutas
administrativas se consideran protegidas visualmente por el router, pero toda API sigue protegida
por JWT y autorización server-side.

## 6. Decisiones justificadas y alternativas descartadas

1. **Refresh en cookie httpOnly, access en memoria.** Evita exponer el refresh a JavaScript y limita
   la persistencia del access. Alternativa descartada: guardar ambos en localStorage, porque amplía
   el impacto de XSS y contradice el contrato.
2. **Cookie host-only sin Domain.** Reduce el alcance a la autoridad que la emitió. Alternativa
   descartada: compartirla con subdominios mediante `Domain`.
3. **CSRF explícito más cookie httpOnly.** La cookie CSRF legible permite enviar el encabezado
   requerido mientras el refresh permanece protegido. Alternativa descartada: confiar solo en CORS o
   en SameSite, que no satisface el contrato de encabezado obligatorio.
4. **Vistas de autenticación propias sobre SimpleJWT.** Permite leer el refresh desde cookie,
   aplicar rol, logging, logout idempotente y reutilización. Alternativa descartada: exponer sin
   adaptación `TokenObtainPairView`/`TokenRefreshView`, porque esperan el contrato estándar en JSON
   y no cubren cookie, CSRF ni logout.
5. **Blacklist estándar de SimpleJWT.** Reutiliza la dependencia instalada y su migración oficial.
   Alternativa descartada: crear un modelo de tokens o de intentos, que duplica infraestructura y
   contradice el alcance.
6. **Caché local/configurado para throttling.** Cumple sin Redis y permite operar con una instancia.
   Alternativa descartada: introducir Redis o WebSockets; no son necesarios para login y están fuera
   del alcance. La debilidad multi-instancia se documenta para Render.
7. **Guardia mínima en React + autorización backend.** Evita mostrar `/admin` a una sesión ausente,
   pero conserva una única fuente de autorización en Django. Alternativa descartada: confiar solo en
   ocultar la ruta frontend.
8. **Sin dependencia de frontend.** Se reutilizan `fetch`, React Router y el código de `api.ts`.
   Alternativa descartada: instalar librería de autenticación o de formularios.

## 7. Configuración y migraciones

### Configuración requerida

- `SIMPLE_JWT`: access 15 minutos, refresh 1 día, rotación y blacklist activadas.
- `INSTALLED_APPS`: app estándar de blacklist; ejecutar su migración oficial.
- `CORS_ALLOW_CREDENTIALS=True` y lista explícita de orígenes autorizados; nunca `*` con credenciales.
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS` desde entorno para producción.
- `DEBUG=False` en producción, proxy HTTPS configurado y `Secure=True` en producción.
- Caché disponible sin Redis (por ejemplo, backend ya existente o configuración local adecuada); no
  se promete consistencia global entre instancias.
- Logging con logger dedicado, sin incluir body, cookies, headers sensibles, tokens ni password.

### Migraciones

No hay migración de `Usuario` ni modelo de intentos. Sí es necesaria la migración estándar de
`rest_framework_simplejwt.token_blacklist`, que debe identificarse y ejecutarse antes de validar
rotación, logout y revocación. No se editan migraciones existentes.

## 8. Mapa de RF/RNF por parte

| Parte | Cobertura |
|---|---|
| Settings + migración blacklist | RF-02–05, RF-08, RNF-01, RNF-04 |
| URLs y vistas de auth | RF-01–09, RNF-01–02 |
| Funciones puras/throttling | RF-08–09, RNF-02, RNF-05 |
| `api.ts` | RF-02–07, RF-11, RNF-03 |
| `Admin.tsx` | RF-01, RF-07, RF-10, RNF-03 |
| Router y main | RF-02, RF-07, RF-10–11, RNF-03 |
| Tests backend | RF-01–11, RNF-01–05 |

## 9. Estrategia de tests y verificación

La única estrategia automatizada permitida es `python manage.py test`/`manage.py test` con
`django.test`; no se usa `node --test`, pytest ni dependencias nuevas. Los tests backend cubrirán:

1. login correcto, usuario inexistente, password incorrecta, inactivo y rol no autorizado;
2. mensaje genérico y códigos 401/429, incluyendo que solo los tres fallos definidos cuentan;
3. CSRF ausente/inválido en los cuatro flujos relevantes y `/api/csrf/` público;
4. atributos exactos de cookie, expiración, host-only y eliminación en logout;
5. access de 15 minutos, refresh de un día, rotación, blacklist, refresh inválido y reutilización
   con revocación de todos los refresh vigentes;
6. logout repetido y logout sin credenciales válidas, ambos 204;
7. logs: presencia de fecha, resultado, username parcial/anonimizado, IP y user-agent, y ausencia
   de password, tokens, cookies, Authorization y CSRF;
8. funciones puras con `hoy` fijo y ventanas de un minuto, sin depender del reloj real.

Verificación adicional de integración: `manage.py check`, migraciones aplicadas y peticiones con
`django.test.Client`/`APIClient` en los endpoints. Para frontend se ejecutará `npm run build` y
`npm run lint`; no se inventa un runner frontend. Se comprobará manualmente con MCP/navegador cuando
esté disponible: `/admin/login`, errores, carga, teclado, redirección 401, no persistencia del
access y bloqueo de `/admin` sin sesión. Si el MCP no encuentra Chrome, se documentará la limitación
y se conservarán las comprobaciones de build y tests backend.

## 10. Riesgos y límites documentados

- El throttling basado en caché sin Redis no ofrece un contador global fuerte entre varias instancias
  de Render; la limitación debe quedar en documentación de despliegue.
- La configuración de sitios distintos cambia deliberadamente SameSite a None y requiere Secure;
  no se debe ocultar ese cambio dentro del frontend.
- La spec física debe guardarse antes de implementar para que las etiquetas RF/RNF y el estado de
  aprobación sean auditables.
