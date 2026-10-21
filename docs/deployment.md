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

## Throttling del login

El límite de cinco fallos por minuto y por IP usa el caché configurado de Django y no requiere
Redis. Con varias instancias de Render, el backend local `LocMemCache` mantiene un contador por
proceso; por tanto, el límite no es global entre instancias. Esta es una limitación operativa
conocida de la configuración actual y no debe interpretarse como coordinación distribuida.
