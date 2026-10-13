// Configuración pública del sitio (única fuente de verdad — RF-9.2).
//
// Este módulo concentra los datos de contacto y enlaces públicos de Hidroemcol.
// Ningún componente debe duplicar el número ni la URL de Facebook: todos los
// accesos visibles (WhatsApp y llamada) se derivan de aquí. Cambiar el valor en
// este único punto actualiza todos los accesos a la vez.

// Número de contacto en formato apto para enlaces (`https://wa.me/...`, `tel:`).
// TEMPORAL de desarrollo: pendiente del número definitivo de producción (RF-9.2).
export const NUMERO_CONTACTO = '+573125967913'

// Número de contacto tal como se muestra al visitante (RF-9.1).
export const NUMERO_CONTACTO_MOSTRADO = NUMERO_CONTACTO.replace(
  /^(\+\d{2})(\d{3})(\d{7})$/,
  '$1 $2 $3',
)

// Mensaje inicial por defecto de la conversación de WhatsApp (aprobado por el usuario).
export const MENSAJE_WHATSAPP = 'Hola, quiero información sobre el servicio técnico de Hidroemcol.'

// Enlace a la página de Facebook de la empresa, única red social del sitio (RF-10.3).
// URL PROVISIONAL/TEMPORAL: pendiente de confirmar por el usuario.
export const URL_FACEBOOK = 'https://www.facebook.com/hidroemcol'

// Construye el enlace de WhatsApp hacia NUMERO_CONTACTO (RF-9.3).
// El número pierde los caracteres no numéricos y el texto se codifica con
// encodeURIComponent; si el mensaje queda vacío o solo con espacios, no se
// añade el parámetro `?text=`.
export function urlWhatsApp(mensaje: string = MENSAJE_WHATSAPP): string {
  const numero = NUMERO_CONTACTO.replace(/\D/g, '')
  const texto = mensaje.trim()
  const base = `https://wa.me/${numero}`
  return texto.length > 0 ? `${base}?text=${encodeURIComponent(mensaje)}` : base
}

// Enlace de llamada telefónica al mismo número (RF-9.4).
export function urlLlamada(): string {
  return `tel:${NUMERO_CONTACTO}`
}
