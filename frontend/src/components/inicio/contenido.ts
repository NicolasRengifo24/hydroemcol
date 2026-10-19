// Datos estáticos de la página de inicio (decisión D-5 del plan).
//
// Este módulo separa el contenido de la presentación: los textos provienen del
// folleto transcrito en `specs/003-pagina-inicio/contenido-folleto.md` y de la
// spec `specs/003-pagina-inicio/spec.md`, que es la fuente de verdad. Ningún
// componente debe inventar contenido fuera de lo aquí definido (RF-11.1).
//
// Lo que aún no está confirmado se marca como PROVISIONAL en los comentarios.

export interface TarjetaServicio {
  titulo: string;
  descripcion: string;
}

export interface ServicioDestacado {
  titulo: string;
  descripcion: string;
}

export interface Marca {
  nombre: string;
  logo?: string;
}

export interface Paso {
  numero: number;
  titulo: string;
  descripcion?: string;
}

export interface ImagenFolleto {
  src: string;
  alt: string;
}

// PROVISIONAL (RF-2.1): mensaje principal del hero.
// Síntesis de las descripciones ya aprobadas de las tres tarjetas (RF-2.4–2.6).
// Pendiente de confirmación del cliente; se cambia aquí y en ningún otro sitio.
export const MENSAJE_HERO =
  "Servicio técnico hidráulico y electrohidráulico, repuestos e importación sobre pedido";

// Las tres tarjetas del hero (RF-2.3). Títulos y descripciones literales de
// RF-2.4, RF-2.5 y RF-2.6 de la spec.
export const TARJETAS_HERO: TarjetaServicio[] = [
  {
    titulo: "Servicio técnico hidráulico y electrohidráulico",
    descripcion: "diagnóstico, reparación y pruebas en banco",
  },
  {
    titulo: "Suministro de repuestos e importación sobre pedido",
    descripcion: "bombas, motores, cilindros, válvulas, orbitroles",
  },
  {
    titulo: "Implementación de sistemas electrohidráulicos a medida",
    descripcion:
      "control proporcional, control de marcha y velocidades, asesoría e implementación",
  },
];

// Los cuatro bloques de productos y servicios del folleto, en el orden fijo de
// RF-4.1 (RF-4.4). Títulos y descripciones literales de RF-4.1.
export const SERVICIOS_DESTACADOS: ServicioDestacado[] = [
  {
    titulo: "Suministro de Repuestos",
    descripcion:
      "repuestos de excelente calidad para bombas y motores hidráulicos.",
  },
  {
    titulo: "Importación Sobre Pedido",
    descripcion:
      "solución para equipos cuyos repuestos no son comunes o son de referencias especiales.",
  },
  {
    titulo: "Servicio técnico electrohidráulico",
    descripcion:
      "servicio en sistemas eléctricos de mando ligados a la hidráulica: control proporcional, control de marcha y velocidades, combinaciones valvulares y sistemas sensorizados.",
  },
  {
    titulo: "Implementación de sistemas",
    descripcion:
      "asesoría y ejecución de sistemas electrohidráulicos a la medida, por sustitución de un sistema obsoleto o por creación desde cero.",
  },
];

// Componentes que atiende la empresa, según RF-5.1. Se usan las denominaciones
// del folleto/spec; no se añaden componentes nuevos.
export const COMPONENTES_ATENDIDOS: string[] = [
  "Cilindros",
  "Bombas",
  "Motores",
  "Orbitroles",
  "Controles",
  "Válvulas",
  "Otros componentes hidráulicos y electrohidráulicos",
];

// Capacidad técnica real de la empresa, tomada del folleto y de la spec. Incluye
// explícitamente las pruebas en banco (RF-5.2). No se afirman cifras ni
// certificaciones que el folleto no contenga.
export const CAPACIDADES_TECNICAS: string[] = [
  "Pruebas en banco",
  "Diagnóstico y reparación de componentes hidráulicos y electrohidráulicos",
  "Control proporcional, control de marcha y velocidades, combinaciones valvulares y sistemas sensorizados",
  "Suministro de repuestos para bombas y motores hidráulicos",
  "Importación sobre pedido de repuestos no comunes o de referencias especiales",
  "Asesoría e implementación de sistemas electrohidráulicos a medida",
];

// Las 14 marcas de RF-5.5, en ese orden, usando los logotipos disponibles en
// public/img/marcas.
export const MARCAS: Marca[] = [
  { nombre: "Komatsu", logo: "/img/marcas/komatsu.png" },
  { nombre: "Bobcat", logo: "/img/marcas/Bobcat.png" },
  { nombre: "Ingersoll Rand", logo: "/img/marcas/Ingersoll_Rand.png" },
  { nombre: "Genie", logo: "/img/marcas/Genie.png" },
  { nombre: "Soilmeca", logo: "/img/marcas/Soilmec.jpg" },
  { nombre: "Link-Belt", logo: "/img/marcas/link-belt.png" },
  { nombre: "Eaton", logo: "/img/marcas/Eaton.png" },
  { nombre: "Bosch Rexroth", logo: "/img/marcas/bosch-rexroth.png" },
  { nombre: "Sauer Danfoss", logo: "/img/marcas/sauer-danfoss.png" },
  { nombre: "Kawasaki Hydraulics", logo: "/img/marcas/kawasaki.png" },
  { nombre: "Caterpillar", logo: "/img/marcas/caterpillar-white.jpg" },
  { nombre: "Kayaba", logo: "/img/marcas/kayaba.png" },
  { nombre: "Linde", logo: "/img/marcas/linde.png" },
  { nombre: "Denison", logo: "/img/marcas/denison.jpg" },
];

// Los cinco pasos del servicio aprobados por el usuario (RF-6.3, decisión D-9),
// numerados 1..5 y en ese orden. Cada paso se comprende por su título (RF-6.4);
// no se añaden descripciones para no inventar contenido de negocio.
export const PASOS: Paso[] = [
  { numero: 1, titulo: "Solicita tu servicio" },
  { numero: 2, titulo: "Revisión y diagnóstico" },
  { numero: 3, titulo: "Cotización y aprobación" },
  { numero: 4, titulo: "Ejecución con seguimiento en línea" },
  { numero: 5, titulo: "Entrega" },
];

// Imágenes de productos para el carrusel de Importación Sobre Pedido
// (RF-4.5, RF-4.6, RF-11.2 y RF-11.4).
export const IMAGENES_PRODUCTOS: ImagenFolleto[] = [
  {
    src: "/img/productos-1.jpeg",
    alt: "Kit de reparación de bomba hidráulica axial con bloque de cilindros, pistones, placas de válvulas, platos de empuje y sellos.",
  },
  {
    src: "/img/productos-2.jpeg",
    alt: "Conjunto de bloques de cilindros, placas de válvula y pistones de una bomba hidráulica axial.",
  },
  {
    src: "/img/productos-3.jpeg",
    alt: "Kit completo de despiece de bomba hidráulica axial con ejes, engranajes, bloque de cilindros, pistones, placas de válvula, rodamientos y tornillería.",
  },
];

// Imágenes reservadas para una futura vista Servicios. No se muestran en Inicio
// (RF-11.3 y RF-11.4), pero permanecen disponibles en public/img.
export const IMAGENES_RESERVADAS_SERVICIOS: ImagenFolleto[] = [
  {
    src: "/img/reparacion-via.jpeg",
    alt: "Aplanadora con obreros realizando trabajos de pavimentación.",
  },
  {
    src: "/img/transporte-elicoportado-villa-garzon-putumayo.jpeg",
    alt: "Cabina de maquinaria pesada transportada suspendida de un helicóptero.",
  },
];

// Unión conservada para compatibilidad con consumidores existentes. Las vistas
// deben seleccionar explícitamente la colección de imágenes que les corresponde.
export const IMAGENES_FOLLETO: ImagenFolleto[] = [
  ...IMAGENES_PRODUCTOS,
  ...IMAGENES_RESERVADAS_SERVICIOS,
];
