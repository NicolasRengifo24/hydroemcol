# Guía operativa — Meta Pixel de la vitrina

Documento interno para configurar y verificar la medición aprobada de la vitrina de productos.
No contiene credenciales y no debe incluirlas.

## 1. Meta Business y Pixel

1. Ingresar a Meta Business Suite con la cuenta institucional de la empresa.
2. En **Business Manager**, revisar que exista la cuenta publicitaria y la página de Meta que se
   usarán para la vitrina.
3. En **Eventos de negocio / Business Manager**, crear o localizar el **Pixel** existente.
4. Copiar el **Pixel ID** desde la configuración del Pixel. Es un identificador técnico; no es una
   credencial, pero tampoco debe publicarse en la interfaz ni pegarse en tickets o capturas.

No se debe crear un Pixel nuevo si la empresa ya tiene uno para su presencia digital; primero se
confirma cuál es el activo.

## 2. Configuración del identificador

El frontend lee la variable de entorno `VITE_META_PIXEL_ID` en tiempo de compilación.

- Copiar `.env.example` como `.env.local` en local, o definir la variable en la configuración del
  despliegue.
- Completar únicamente el valor del Pixel ID:

```env
VITE_META_PIXEL_ID=
```

- Si la variable está vacía o no existe, **no se carga el script de Meta**. La vitrina y sus
  enlaces de WhatsApp siguen funcionando con normalidad.
- Si la variable tiene valor, se carga el script una sola vez y se ejecuta `fbq('init', id)` una
  sola vez.

El valor debe configurarse en el entorno de despliegue, no en el código fuente ni en archivos
versionados.

## 3. Eventos permitidos

La implementación envía únicamente:

| Evento | Cuándo | Parámetros |
|---|---|---|
| `ViewContent` | Una vez al entrar a `/productos` | `content_url` canónico y UTM disponibles |
| `Contact` | Solo al pulsar **Consultar por WhatsApp** en un producto | `origen: 'producto'`, `content_category`, `content_ids: [clave]` y UTM disponibles |

No se envían `PageView`, `SelectContent`, eventos del carrusel, nombre, teléfono, correo, mensaje,
precio, stock, token ni datos de la conversación de WhatsApp.

## 4. UTM de sesión

Se conservan durante la sesión las cinco claves que lleguen en la URL:

- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`

Se guardan en `sessionStorage` bajo `hydroemcol:utm`. Si el navegador bloquea `sessionStorage`, se
mantiene una copia en memoria para la pestaña actual. La primera atribución gana: una visita nueva
solo completa las claves que aún no estaban guardadas; nunca se inventan valores ausentes.

Ejemplo de enlace interno con atribución:

```text
/productos?utm_source=whatsapp&utm_medium=referral&utm_campaign=vitrina
```

## 5. Prueba de eventos

1. Con la variable de entorno configurada, abrir la vitrina en el navegador.
2. En Meta, usar **Administrador de eventos → Probar eventos** y elegir el Pixel configurado.
3. Abrir `/productos` sin UTM. Debe aparecer **un solo `ViewContent`** con `content_url` canónico.
4. Abrir `/productos` con UTM de prueba. Debe aparecer **un solo `ViewContent`** con `content_url`
   y esas UTM.
5. Cambiar de categoría dentro de `/productos`. No debe aparecer otro `ViewContent`.
6. Pulsar **Consultar por WhatsApp** en un producto. Debe aparecer **un `Contact`** con los
   parámetros técnicos permitidos y las UTM disponibles.
7. Comprobar que no aparecen `PageView`, `SelectContent` ni eventos al recorrer el carrusel.
8. Si el Pixel está bloqueado por el navegador, la página no debe mostrar errores.

Para pruebas locales se puede usar un ID de prueba; no se debe usar un Pixel real de producción
durante la verificación.

## 6. Lectura de resultados

- Revisar en **Administrador de eventos** el volumen de `ViewContent` y `Contact` por día.
- Comparar `ViewContent` con visitas a `/productos` y `Contact` con clics en WhatsApp.
- Usar las UTM para separar el origen de cada campaña en los informes de Meta.
- Recordar que `Contact` mide el **clic**, no una conversación confirmada.

No se debe interpretar un `Contact` como un mensaje enviado ni como un cliente potencial calificado.

## 7. Campañas de mensajes y tráfico

- Priorizar campañas de **mensajes** dirigidas a WhatsApp: la intención comercial se confirma en la
  conversación, no en la página.
- Usar campañas de **tráfico** como apoyo para llevar visitantes a la vitrina y medir
  `ViewContent`.
- Mantener UTM distintas por campaña para poder leer cada origen por separado.
- No duplicar la misma campaña en ambos objetivos sin una razón medible.

## 8. Clic a `wa.me` y conversación confirmada

El botón de producto abre WhatsApp con un mensaje preparado. El evento `Contact` se registra en ese
clic. La interfaz avisa que WhatsApp se abrió en otra pestaña y **no afirma** que el mensaje se
envió, que la conversación comenzó o que alguien respondió.

La conversación confirmada debe verificarse en WhatsApp o en el canal comercial de la empresa, no
en Meta Pixel.

## 9. Presupuesto inicial y TikTok

- Comenzar con un presupuesto aproximado de **100.000 COP**, ajustable según resultados.
- Priorizar mensajes a WhatsApp; usar tráfico como campaña secundaria.
- Ampliar el presupuesto solo si los informes muestran clics y conversaciones útiles, no solo
  `ViewContent`.
- **TikTok queda aplazado**: no se configura ni se mide en esta entrega.

## 10. Publicación en producción

La publicación con Pixel real depende de la decisión legal de privacidad y consentimiento de la
empresa. Esta entrega **no implementa banner de consentimiento ni política de privacidad
inventada**. Hasta que esa decisión exista, se mantiene la medición desactivada en producción.
