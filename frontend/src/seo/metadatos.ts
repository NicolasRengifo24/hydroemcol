export interface MetadatosPagina {
  titulo: string;
  descripcion: string;
}

export const METADATOS_INICIO: MetadatosPagina = {
  titulo:
    "Hydroemcol S.A.S | Sistemas hidráulicos y electrohidráulicos | Servicio técnico",
  descripcion:
    "Hydroemcol S.A.S brinda servicio técnico, diagnóstico, reparación, banco de pruebas, repuestos e importación sobre pedido de sistemas hidráulicos y electrohidráulicos en Colombia.",
};

const METADATOS_POR_RUTA: Record<string, MetadatosPagina> = {
  "/": METADATOS_INICIO,
  "/soluciones": {
    titulo: "Soluciones hidráulicas y electrohidráulicas | Hydroemcol S.A.S",
    descripcion:
      "Kits de reparación, componentes hidráulicos, repuestos sobre pedido y servicio técnico especializado para sistemas hidráulicos y electrohidráulicos.",
  },
  "/nosotros": {
    titulo: "Nosotros | Hydroemcol S.A.S",
    descripcion:
      "Conoce a Hydroemcol S.A.S., empresa especializada en sistemas hidráulicos, electrohidráulicos, repuestos y servicio técnico en Colombia.",
  },
  "/solicitar": {
    titulo: "Solicitar servicio técnico hidráulico | Hydroemcol S.A.S",
    descripcion:
      "Solicita diagnóstico, reparación o mantenimiento de sistemas hidráulicos y electrohidráulicos. Cuéntanos qué necesita tu equipo.",
  },
  "/seguimiento": {
    titulo: "Seguimiento de servicio | Hydroemcol S.A.S",
    descripcion:
      "Consulta el estado de tu servicio hidráulico con el enlace privado de seguimiento enviado por Hydroemcol S.A.S.",
  },
};

export function normalizarRuta(pathname: string): string {
  if (pathname.length > 1 && pathname.endsWith("/")) {
    return pathname.replace(/\/+$/, "") || "/";
  }

  return pathname;
}

export function metadatosDeRuta(pathname: string): MetadatosPagina {
  const rutaNormalizada = normalizarRuta(pathname);

  if (rutaNormalizada.startsWith("/seguimiento/")) {
    return METADATOS_POR_RUTA["/seguimiento"];
  }

  return METADATOS_POR_RUTA[rutaNormalizada] ?? METADATOS_INICIO;
}
