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

// Mensaje principal del hero actualizado por solicitud del usuario: refuerza
// la venta de repuestos y el banco de pruebas, sin mencionar sistemas
// electrohidráulicos.
export const MENSAJE_HERO =
  "Venta de repuestos hidráulicos y banco de pruebas para una operación que no se detiene";

// Las tres tarjetas del hero. Acompañan el enfoque del mensaje principal:
// servicio hidráulico, repuestos y banco de pruebas.
export const TARJETAS_HERO: TarjetaServicio[] = [
  {
    titulo: "Servicio técnico hidráulico",
    descripcion: "diagnóstico, reparación y pruebas en banco",
  },
  {
    titulo: "Suministro de repuestos e importación sobre pedido",
    descripcion: "bombas, motores, válvulas, orbitroles y componentes especiales",
  },
  {
    titulo: "Banco de pruebas",
    descripcion:
      "motor de 190 caballos de fuerza e instrumentación de precisión",
  },
];

// Bloques de productos y servicios. La tarjeta de repuestos se actualizó con el
// enfoque de distribución mayorista solicitado por el usuario; la tarjeta de
// implementación de sistemas se retiró por decisión del mismo usuario.
export const SERVICIOS_DESTACADOS: ServicioDestacado[] = [
  {
    titulo: "Suministro de Repuestos",
    descripcion:
      "Distribución mayorista de repuestos OEM (fabricante original) para todas las marcas, a nivel nacional, como importadores directos.",
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
];

// Componentes que atiende la empresa. Por solicitud del usuario se retiraron
// cilindros y controles de esta lista.
export const COMPONENTES_ATENDIDOS: string[] = [
  "Bombas",
  "Motores",
  "Orbitroles",
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

export interface DatoBancoPruebas {
  etiqueta: string;
  valor?: string;
}

// Características del banco de pruebas confirmadas por el usuario. Se muestran
// en el hero tecnológico que precede a los videos del banco.
export const TITULO_BANCO_PRUEBAS =
  "Potencia e instrumentación para pruebas en condiciones reales";

export const TEXTO_BANCO_PRUEBAS =
  "Medimos presión, caudal, temperatura, revoluciones y respuesta eléctrica con instrumentación de precisión.";

export const DATOS_BANCO_PRUEBAS: DatoBancoPruebas[] = [
  { valor: "190 HP", etiqueta: "Motor del banco" },
  { etiqueta: "Manómetros digitales" },
  { etiqueta: "Flujómetros por ultrasonido" },
  { etiqueta: "Osciloscopio" },
  { etiqueta: "Revoluciones reales de trabajo" },
  { etiqueta: "Pruebas a altas temperaturas" },
  { etiqueta: "Fuente de voltaje DC" },
  { etiqueta: "Sistema de regulación de presiones" },
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
