// Configuración pública del sitio (única fuente de verdad — RF-9.2).
//
// Este módulo concentra los datos de contacto y enlaces públicos de Hidroemcol.
// Ningún componente debe duplicar el número ni la URL de Facebook: todos los
// accesos visibles (WhatsApp y llamada) se derivan de aquí. Cambiar el valor en
// este único punto actualiza todos los accesos a la vez.

// Origen canónico del sitio público. Se usa para construir canonical y og:url.
export const URL_SITIO = "https://www.hydroemcol.com";

// Número de contacto en formato apto para enlaces (`https://wa.me/...`, `tel:`).
// TEMPORAL de desarrollo: pendiente del número definitivo de producción (RF-9.2).
export const NUMERO_CONTACTO = "+573138343980";

// Número de contacto tal como se muestra al visitante (RF-9.1).
export const NUMERO_CONTACTO_MOSTRADO = NUMERO_CONTACTO.replace(
  /^(\+\d{2})(\d{3})(\d{7})$/,
  "$1 $2 $3",
);

// Mensaje inicial por defecto de la conversación de WhatsApp (aprobado por el usuario).
export const MENSAJE_WHATSAPP =
  "Hola, quiero información sobre el servicio técnico de Hidroemcol.";

// Enlace a la página de Facebook de la empresa, única red social del sitio (RF-10.3).
export const URL_FACEBOOK = "https://www.facebook.com/hidroemcolservice";

// Construye el enlace de WhatsApp hacia NUMERO_CONTACTO (RF-9.3).
// El número pierde los caracteres no numéricos y el texto se codifica con
// encodeURIComponent; si el mensaje queda vacío o solo con espacios, no se
// añade el parámetro `?text=`.
export function urlWhatsApp(mensaje: string = MENSAJE_WHATSAPP): string {
  const numero = NUMERO_CONTACTO.replace(/\D/g, "");
  const texto = mensaje.trim();
  const base = `https://wa.me/${numero}`;
  return texto.length > 0
    ? `${base}?text=${encodeURIComponent(mensaje)}`
    : base;
}

// Enlace de llamada telefónica al mismo número (RF-9.4).
export function urlLlamada(): string {
  return `tel:${NUMERO_CONTACTO}`;
}

// Dirección física de la empresa, aprobada por el usuario (RF-10.1, D-6 de
// specs/009-vista-nosotros). Única fuente de verdad de la dirección: no se
// inventan coordenadas ni puntos de referencia (RF-10.4).
export const DIRECCION = "Ac. 6 #27b-55";

// Horario de atención confirmado por el usuario. Única fuente de verdad del
// horario visible y del estado abierto/cerrado que se muestra en Nosotros.
export const HORARIO = {
  apertura: 8,
  cierre: 18,
  texto: "8:00 a.m. - 6:00 p.m.",
  zonaHoraria: "America/Bogota",
} as const;

// Devuelve true si la hora actual (en la zona horaria de la empresa) está dentro
// del horario de atención. Solo se evalúa el rango horario: los días de cierre
// no están definidos en el contexto del proyecto y no se inventan aquí.
export function estaDentroDelHorario(fecha: Date = new Date()): boolean {
  const partes = new Intl.DateTimeFormat("en-US", {
    timeZone: HORARIO.zonaHoraria,
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(fecha);

  const hora = Number(
    partes.find((parte) => parte.type === "hour")?.value ?? 0,
  );
  const minuto = Number(
    partes.find((parte) => parte.type === "minute")?.value ?? 0,
  );
  const minutosDelDia = hora * 60 + minuto;

  return (
    minutosDelDia >= HORARIO.apertura * 60 &&
    minutosDelDia < HORARIO.cierre * 60
  );
}

// URL de Google Maps para embeber el mapa de la dirección en un iframe
// accesible (RF-10.1). Se construye desde DIRECCION para no duplicarla; el
// parámetro output=embed devuelve la vista embebible sin API key.
export const URL_GOOGLE_MAPS_EMBED = `https://www.google.com/maps?q=${encodeURIComponent(DIRECCION)}&output=embed`;

// Enlace alternativo a Google Maps para abrir la ubicación fuera del sitio
// (RF-10.2): por si el iframe no carga o el visitante prefiere abrirlo en
// Google Maps directamente. Misma fuente (DIRECCION), sin datos inventados.
export const URL_GOOGLE_MAPS = `https://www.google.com/maps?q=${encodeURIComponent(DIRECCION)}`;
