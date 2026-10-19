// Datos estáticos de la página Nosotros (spec `specs/009-vista-nosotros/spec.md`).
//
// Este módulo separa el contenido de la presentación: los textos provienen del
// folleto aprobado en `specs/003-pagina-inicio/contenido-folleto.md` (versión
// para el sitio) y de la spec 009, que es la fuente de verdad. Ningún
// componente debe inventar contenido fuera de lo aquí definido (RF-11.1):
// sin cifras, fechas de fundación, número de clientes ni certificaciones que
// el folleto no contenga (RF-3.2).
//
// Lo que aún no está confirmado se marca como PROVISIONAL en los comentarios.

export interface BloqueIdentidad {
  titulo: string;
  texto: string;
}

export interface ImagenHero {
  src: string;
  alt: string;
}

// PROVISIONAL (RF-11.1): mensaje central del hero de la página Nosotros.
// Tono profesional coherente con la identidad industrial de la empresa;
// sin datos duros (años, cifras ni certificaciones). Pendiente de
// validación del cliente; se cambia aquí y en ningún otro sitio.
export const MENSAJE_HERO_NOSOTROS =
  "Empresa técnica e industrial especializada en sistemas hidráulicos y electrohidráulicos: servicio técnico, repuestos e importación sobre pedido";

// PROVISIONAL hasta su validación final (RF-3.1 y RF-11.1): párrafo literal
// de "Quiénes somos" tal como está fijado en la spec. No reescribir ni ampliar
// (riesgo R1 del plan). No afirma datos de negocio no verificados (RF-3.2).
export const TEXTO_QUIENES_SOMOS =
  "Hidroemcol es una empresa técnica e industrial especializada en sistemas hidráulicos y " +
  "electrohidráulicos. Nos dedicamos a brindar el mejor servicio técnico y a suministrar " +
  "repuestos de calidad, con experiencia, responsabilidad y rapidez, para asegurar que los " +
  "equipos de nuestros clientes mantengan su funcionamiento normal durante el desarrollo de " +
  "sus operaciones. Complementamos nuestra oferta con importación sobre pedido para casos de " +
  "referencias especiales, servicios técnicos de diagnóstico y reparación, banco de pruebas y " +
  "soluciones de control aplicadas a equipos de trabajo pesado. Nuestro enfoque se fundamenta " +
  "en el respeto, la honestidad y la responsabilidad, con una prioridad clara: el bienestar y " +
  "el amor por la familia.";

// Misión, Visión y Valores literales de la "Versión para el sitio" del folleto
// (`specs/003-pagina-inicio/contenido-folleto.md`), copiados tal cual sin
// parafrasear ni recortar (RF-4.1). Bloques escaneables título + texto
// (RF-4.3); la cita de Brad Henry va aparte, en CITA_BRAD_HENRY (RF-4.2).
export const IDENTIDAD: BloqueIdentidad[] = [
  {
    titulo: "Misión",
    texto:
      "Hydroemcol nace para brindar el mejor servicio técnico y en suministro de repuestos del mercado, con experiencia, responsabilidad y rapidez, para que nuestros clientes tengan un funcionamiento normal de los equipos en el desarrollo de sus operaciones, cuidando la integridad física y personal de nuestros allegados y colaboradores, además creando para ellos un entorno amigable y propicio para el mejoramiento en la calidad de vida, fundamentado en el propósito más importante de la vida, que es el bienestar y amor por la familia.",
  },
  {
    titulo: "Visión",
    texto:
      "Hydroemcol se proyecta en el futuro gracias a la ayuda de sus colaboradores, clientes y proveedores como la empresa número uno en la prestación de servicio técnico y suministro de repuestos del mercado en el país, destacándose por su excelente servicio y calidez humana con todas las personas que influyen en la compañía.",
  },
  {
    titulo: "Valores",
    texto:
      "Para Hydroemcol nada tendría sentido si no se tiene en cuenta a la familia como prioridad de una sociedad; esto hace al amor por la familia, junto con el respeto, la honestidad y la responsabilidad, los principales valores a tener en cuenta por nuestra compañía para el desarrollo de nuestras actividades.",
  },
];

// Cita literal de la "Versión para el sitio" del folleto (RF-4.2), como
// elemento diferenciado dentro de la sección de identidad.
export const CITA_BRAD_HENRY: { texto: string; autor: string } = {
  texto:
    "Las familias son las brújulas que nos guían, son la inspiración para llegar a grandes alturas y nuestro consuelo cuando ocasionalmente fallamos.",
  autor: "Brad Henry",
};

// Imagen existente del hero (D-5: `frontend/public/img/hydroemcol-nosotros.png`,
// verificada en `public/img/`; es PNG, no existe versión JPG). Solo imágenes
// existentes en `public/img/`.
//
// Nota de accesibilidad (RNF-4): el componente de hero la usa como FONDO
// DECORATIVO con velo oscuro encima, por lo que en el render se aplicará
// `alt=""` y `aria-hidden="true"` para dejarla fuera del árbol de
// accesibilidad. El `alt` de este registro documenta la imagen mientras el
// tipo `ImagenHero` (patrón de `components/inicio/contenido.ts`) exige un
// `alt` no vacío; se mantiene descriptivo y genérico para no afirmar
// detalles del contenido que no estén aprobados.
export const HERO_NOSOTROS: ImagenHero = {
  src: "/img/hydroemcol-nosotros.png",
  alt: "Imagen de presentación de Hidroemcol, empresa técnica e industrial especializada en sistemas hidráulicos y electrohidráulicos.",
};
