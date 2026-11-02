# Notas de despliegue

## Variables de producción

Configura estas variables en Render sin subir valores secretos al repositorio:

- `SECRET_KEY`: clave privada generada para producción.
- `DEBUG=False`.
- `ALLOWED_HOSTS`: hosts del backend, separados por comas, sin `*`.
- `DATABASE_URL`: URL de PostgreSQL/Neon.
- `CORS_ALLOWED_ORIGINS`: orígenes exactos del frontend, separados por comas.
- `CSRF_TRUSTED_ORIGINS`: los mismos orígenes HTTPS que pueden enviar formularios al backend.
- `AUTH_COOKIE_SECURE=True`, `SECURE_SSL_REDIRECT=True` y `TRUST_PROXY_SSL=True`.
- `AUTH_COOKIE_SAMESITE=Lax` cuando frontend y backend están en el mismo sitio.
- `R2_ENABLED=True` en producción cuando el bucket privado de Cloudflare R2 esté listo.
- `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` y `R2_ENDPOINT_URL` para R2.
- `R2_URL_EXPIRATION_SECONDS` para la duración de las URLs firmadas, por defecto 900 segundos.

No uses `*` con credenciales CORS. `VITE_API_URL` debe apuntar al origen HTTPS del backend
cuando frontend y backend se despliegan separadamente.

## Usuario administrativo en Render

El plan gratuito de Render no ofrece shell, así que el usuario administrativo se crea con el
comando de gestión `usuarios/crear_usuario_admin.py` durante el build:

```env
HIDROEMCOL_ADMIN_USERNAME=user
HIDROEMCOL_ADMIN_PASSWORD=<contraseña>
HIDROEMCOL_ADMIN_EMAIL=admin@hydroemcol.com
```

Y el comando de build queda así:

```bash
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py crear_usuario_admin
```

El comando es idempotente: si el usuario ya existe solo verifica su rol y que siga activo, y
no vuelve a fijar la contraseña salvo que se ejecute con `--actualizar-clave`. La contraseña
solo es obligatoria la primera vez; después de verificar el acceso se puede retirar
`HIDROEMCOL_ADMIN_PASSWORD` del entorno. Si el usuario se borrara, el comando fallaría sin esa
variable: en ese caso quita también el comando del build.

El admin de Django (`/admin/`) solo se registra en `config/urls.py` cuando `DEBUG=True`. En
producción responde `404`: la única interfaz de operación es el panel propio del frontend. El
usuario se mantiene con `is_staff=True` porque no afecta a la API y permite usar el admin en
local cuando se necesite.

## Fotografías: fallos de almacenamiento

Si el almacenamiento no puede guardar una fotografía, la solicitud pública responde `503` con
un mensaje accionable y la transacción se revierte: no queda una solicitud a medias. El detalle
del proveedor (por ejemplo `AccessDenied` o `SignatureDoesNotMatch`) queda solo en el log del
servidor, en la línea `Fallo al guardar la fotografía en el almacenamiento`. Con `DEBUG=False`
el handler `console` de Django no escribe, por eso el proyecto registra esa línea y las
excepciones no controladas en `django.request` con su propio handler de consola.

Las referencias de fotografías en R2 se guardan internamente como `r2://...`; las respuestas
administrativas y públicas generan una URL firmada temporalmente. No se deben guardar URLs
firmadas en la base de datos porque expiran. Para este flujo privado se usa el endpoint S3 de
R2; no se configura `AWS_S3_CUSTOM_DOMAIN` para las URLs firmadas.

## HTTPS y proxy

Render debe terminar la conexión pública en HTTPS y reenviar `X-Forwarded-Proto: https` al
backend. `TRUST_PROXY_SSL=True` permite que Django reconozca ese esquema y
`SECURE_SSL_REDIRECT=True` redirige cualquier solicitud HTTP restante. La cookie de refresh
se emite con `Secure`, `HttpOnly`, `Path=/api/` y sin `Domain`.

Si los sitios finales del frontend y backend son distintos, cambia explícitamente
`AUTH_COOKIE_SAMESITE=None` y conserva `AUTH_COOKIE_SECURE=True`. No se cambia `SameSite`
automáticamente según el origen.

## SEO: cabeceras y redirecciones

El frontend es una SPA. Los metadatos por ruta se actualizan en el navegador con
`frontend/src/seo/Seo.tsx`; las páginas privadas además deben protegerse desde la
infraestructura.

### Render: cabeceras para rutas privadas

En Render Dashboard, abre el Static Site del frontend y entra a **Settings > Headers**.
Añade estas reglas:

| Request Path | Header Name | Header Value |
| --- | --- | --- |
| `/control-operativo` | `X-Robots-Tag` | `noindex, nofollow` |
| `/control-operativo/*` | `X-Robots-Tag` | `noindex, nofollow` |
| `/seguimiento/*` | `X-Robots-Tag` | `noindex, nofollow` |

Las reglas antiguas de `/admin` pueden conservarse por bookmarks, pero ya no son la ruta del
panel. No agregues `Disallow` para estas rutas en `robots.txt`: si Google no puede rastrearlas,
tampoco puede leer el `noindex`.

### Cloudflare Access para el panel

El nombre de la ruta no es una medida de seguridad: el bundle público contiene todas las rutas.
La protección real es Cloudflare Access más la autenticación JWT de la API.

En **Zero Trust > Access > Applications**, crea una aplicación *Self-hosted*:

| Campo | Valor |
| --- | --- |
| Dominio | `www.hydroemcol.com` |
| Ruta | `control-operativo*` |
| Sesión | 8 a 24 horas |
| Política | `Allow` solo para los correos autorizados |
| Identidad | One-time PIN por correo o Google |

Access solo cubre la carga del documento. Si alguien entra por `/` y navega del lado del
cliente hacia el panel, no se vuelve a pedir el PIN; los datos siguen protegidos porque la API
exige JWT. Para bloquear también ese caso haría falta un hostname separado, que el plan free de
Render no permite añadir ahora.

### Rutas desconocidas

`frontend/src/router.tsx` redirige `/admin` y `/admin/*` al inicio para no romper bookmarks
antiguos. Cualquier otra ruta desconocida renderiza `NoEncontrada`, una página 404 con el logo
de la empresa y un acceso directo a WhatsApp. La página es estática (la SPA responde `200` por
el rewrite) y declara `noindex`, así que no debe usarse como sustituto de un `404` real en el
servidor.

### Render: rewrite de la SPA

En la pestaña **Redirects/Rewrites** debe existir una regla:

| Source Path | Destination Path | Action |
| --- | --- | --- |
| `/*` | `/index.html` | `Rewrite` |

No la dupliques. Las redirecciones de variantes de URL se resuelven en Cloudflare porque
Render no aplica reglas a rutas donde ya existe un archivo, como `/index.html`.

### Cloudflare: dominio canónico y barras finales

En la zona `hydroemcol.com`:

1. Activa **Always Use HTTPS**.
2. En **Rules > Redirect Rules**, crea una regla para el dominio sin `www`:
   - Nombre: `Apex a www`
   - Expresión: `(http.host eq "hydroemcol.com")`
   - Tipo: Dynamic
   - Expresión de destino: `concat("https://www.hydroemcol.com", http.request.uri.path)`
   - Código: `301`
   - Conservar query string: activado
3. Crea una regla para `/index.html`:
   - Expresión: `(http.host eq "www.hydroemcol.com" and http.request.uri.path eq "/index.html")`
   - Destino: `https://www.hydroemcol.com/`
   - Código: `301`
4. Crea una regla por cada ruta pública con barra final:
   - `/soluciones/` → `https://www.hydroemcol.com/soluciones`
   - `/nosotros/` → `https://www.hydroemcol.com/nosotros`
   - `/solicitar/` → `https://www.hydroemcol.com/solicitar`
   - `/seguimiento/` → `https://www.hydroemcol.com/seguimiento`

Después del despliegue, verifica con `curl -I` que las variantes respondan `301` y que las
URLs canónicas respondan `200`.

## Throttling del login

El límite de cinco fallos por minuto y por IP usa el caché configurado de Django y no requiere
Redis. Con varias instancias de Render, el backend local `LocMemCache` mantiene un contador por
proceso; por tanto, el límite no es global entre instancias. Esta es una limitación operativa
conocida de la configuración actual y no debe interpretarse como coordinación distribuida.

## Modo mantenimiento del frontend

El frontend es un sitio estático y sigue siendo navegable aunque la API esté suspendida. Para
evitar errores crudos, `frontend/src/services/disponibilidad.ts` mantiene un estado global que se
activa solo ante fallos de infraestructura:

- error de red al hacer `fetch`;
- `502`, `504` y respuestas `5xx` que no son JSON (páginas de error de Render o Cloudflare);
- sondeo fallido a `GET /healthz/`.

Los errores `4xx` (validación, credenciales, permisos o conflicto) y los `503` JSON del backend
(por ejemplo, fallo de R2) **no** activan el modo mantenimiento: son respuestas de una API que sí
está en línea.

Cuando el estado pasa a `no_disponible`:

- en el sitio público aparece un aviso no bloqueante (`AvisoServicio`) y los botones de envío se
  deshabilitan;
- en `/admin` se muestra un panel bloqueante con la opción de reintentar o volver al inicio;
- se sondea `/healthz/` con espera creciente (10, 20, 40 y 60 segundos), solo con la pestaña
  visible y durante un máximo de 10 minutos; después queda el reintento manual;
- al recuperarse la API, el aviso desaparece y React Query invalida las consultas.

El sondeo usa `VITE_API_URL` para construir la URL. En desarrollo, `vite.config.ts` redirige
`/healthz` al backend local para que el aviso también funcione sin esa variable.
