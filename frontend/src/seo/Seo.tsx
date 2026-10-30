import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { URL_SITIO } from "../config/sitio";
import { metadatosDeRuta, normalizarRuta } from "./metadatos";

interface SeoProps {
  titulo?: string;
  descripcion?: string;
  ruta?: string;
  noindex?: boolean;
}

function actualizarMeta(
  atributo: "name" | "property",
  clave: string,
  contenido: string,
) {
  let etiqueta = document.head.querySelector<HTMLMetaElement>(
    `meta[${atributo}="${clave}"]`,
  );

  if (!etiqueta) {
    etiqueta = document.createElement("meta");
    etiqueta.setAttribute(atributo, clave);
    document.head.appendChild(etiqueta);
  }

  etiqueta.setAttribute("content", contenido);
}

function actualizarCanonical(href: string) {
  let enlace = document.head.querySelector<HTMLLinkElement>(
    'link[rel="canonical"]',
  );

  if (!enlace) {
    enlace = document.createElement("link");
    enlace.setAttribute("rel", "canonical");
    document.head.appendChild(enlace);
  }

  enlace.setAttribute("href", href);
}

function Seo({ titulo, descripcion, ruta, noindex = false }: SeoProps) {
  const location = useLocation();
  const rutaActual = normalizarRuta(ruta ?? location.pathname);
  const metadatos = metadatosDeRuta(rutaActual);
  const tituloFinal = titulo ?? metadatos.titulo;
  const descripcionFinal = descripcion ?? metadatos.descripcion;
  const esSeguimientoPrivado = rutaActual.startsWith("/seguimiento/");
  const robots =
    noindex || esSeguimientoPrivado ? "noindex, nofollow" : "index, follow";
  const canonical = `${URL_SITIO}${rutaActual === "/" ? "/" : rutaActual}`;

  useEffect(() => {
    document.title = tituloFinal;
    actualizarMeta("name", "description", descripcionFinal);
    actualizarMeta("property", "og:title", tituloFinal);
    actualizarMeta("property", "og:description", descripcionFinal);
    actualizarMeta("property", "og:url", canonical);
    actualizarMeta("name", "twitter:title", tituloFinal);
    actualizarMeta("name", "twitter:description", descripcionFinal);
    actualizarMeta("name", "robots", robots);
    actualizarCanonical(canonical);
  }, [canonical, descripcionFinal, robots, tituloFinal]);

  return null;
}

export default Seo;
