# Tareas — Spec 004: Login del panel administrativo

Derivadas del contrato aprobado y de `plan.md`. Cada tarea es incremental y está estimada entre
20 y 30 minutos. No implementan nada por sí mismas; son instrucciones de trabajo.

- [ ] **T1. Guardar la spec aprobada y fijar la matriz de trazabilidad (20 min).** RF-01–RF-11,
  RNF-01–RNF-05.
  - **Hecho cuando:** `specs/004-login-admin/spec.md` contiene el contrato aprobado con Estado:
    aprobada, las etiquetas RF/RNF usadas por el plan son comprobables y no existen requisitos
    adicionales inventados.

- [x] **T2. Preparar configuración JWT, cookies, CORS/CSRF y entornos (25 min).** RF-02–RF-05,
  RF-08, RNF-01, RNF-04.
  - **Hecho cuando:** settings define access 15 minutos, refresh 1 día, rotación/blacklist,
    credenciales CORS, orígenes por entorno, hosts/CSRF trusted origins y Secure de producción,
    sin wildcard inseguro ni dependencia nueva; `manage.py check` pasa.

- [x] **T3. Activar migración estándar de blacklist (20 min).** RF-05, RNF-04–RNF-05.
  - **Hecho cuando:** `token_blacklist` está instalado, se identifica/aplica su migración estándar,
    no se crea modelo de intentos ni se editan migraciones existentes, y la migración puede ejecutarse
    con `manage.py migrate`.

- [x] **T4. Implementar CSRF y los endpoints de login/refresh/logout (30 min).** RF-01–RF-07,
  RNF-01–RNF-02.
  - **Hecho cuando:** las cuatro rutas contractuales existen; login autoriza solo ADMINISTRATIVO,
    usa mensaje 401 genérico, refresh lee/rota cookie, logout es CSRF-protegido, idempotente, borra
    cookie y devuelve 204; ningún secreto aparece en respuestas o logs.

- [x] **T5. Añadir throttling, reutilización y logging seguro (30 min).** RF-05, RF-08–RF-09,
  RNF-01–RNF-02, RNF-05.
  - **Hecho cuando:** solo usuario inexistente/password incorrecta/inactivo cuentan como fallos,
    el límite es 5 por minuto/IP, el caché no requiere Redis, la reutilización revoca los refresh
    vigentes del usuario y los logs contienen únicamente los campos permitidos; la limitación
    multi-instancia queda documentada.

- [x] **T6. Crear pruebas backend de contrato y seguridad (30 min).** RF-01–RF-09,
  RNF-01–RNF-02, RNF-05.
  - **Hecho cuando:** tests con `django.test` cubren éxito/fallos, CSRF, cookies, expiración,
    rotación, blacklist, reutilización, logout 204, throttling y contenido de logs; pasan mediante
    `manage.py test` sin pytest, `node --test` ni paquetes nuevos.

- [x] **T7. Extender `api.ts` para sesión en memoria y single-flight (30 min).** RF-02–RF-07,
  RF-11, RNF-03–RNF-04.
  - **Hecho cuando:** todas las peticiones usan `credentials: include`, el access vive solo en
    memoria, se envía CSRF cuando corresponde, una sola renovación atiende 401 concurrentes, se
    reintenta una vez y un refresh 401 limpia memoria y dirige a `/admin/login`.

- [x] **T8. Construir login y protección de rutas (30 min).** RF-01, RF-07, RF-10–RF-11,
  RNF-03.
  - **Hecho cuando:** `/admin/login` muestra formulario accesible con carga/error, `/admin` exige
    sesión frontend sin sustituir la autorización backend, el router y `main.tsx` comparten el estado
    de memoria y login exitoso dirige al panel.

- [x] **T9. Verificación integrada y documentación de despliegue (25 min).** RF-01–RF-11,
  RNF-01–RNF-05.
  - **Hecho cuando:** pasan `manage.py check`, `manage.py test`, `npm run build` y `npm run lint`;
    la comprobación manual confirma login, logout, refresh, 401, CSRF, responsive y no persistencia
    del access; quedan documentados HTTPS/proxy, variables de producción, SameSite=None solo si los
    sitios finales son distintos y la limitación del throttling en Render.
