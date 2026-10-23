import { useEffect, useState } from "react";
import { Clock, MapPin, Navigation } from "lucide-react";
import { SeccionEncabezado } from "../inicio/SeccionEncabezado";
import {
  DIRECCION,
  HORARIO,
  URL_GOOGLE_MAPS,
  URL_GOOGLE_MAPS_EMBED,
  estaDentroDelHorario,
} from "../../config/sitio";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 6 de la página Nosotros (RF-1.1): ubicación y mapa (RF-10, D-6
// aprobada). Muestra un bloque de dirección con la dirección aprobada
// "Calle 6 # 27b-55" y el mapa de Google Maps embebido en un iframe
// accesible con `title` y `loading="lazy"` (RF-10.1). Dirección y URLs se
// importan de config/sitio.ts (DIRECCION, URL_GOOGLE_MAPS_EMBED,
// URL_GOOGLE_MAPS): aquí no se duplican ni se inventan coordenadas ni
// puntos de referencia (RF-10.4).
//
// Resiliencia (caso límite "el iframe del mapa no carga"): el bloque de
// dirección y el enlace alternativo a Google Maps (RF-10.2) son elementos
// independientes del iframe y siguen disponibles en la misma sección.
//
// Accesibilidad (RNF-5, RF-10.2): el enlace alternativo se abre en pestaña
// nueva con rel="noopener noreferrer" y aviso para lectores de pantalla
// (mismo patrón que el resto del sitio); el foco visible lo definen
// .ubicacion__enlace:focus-visible y .ubicacion__iframe en nosotros.css
// (T3). Un solo h2 por sección, provisto por SeccionEncabezado (RF-1.3).
// Responsive sin overflow (RF-10.3): las clases .ubicacion__* de
// nosotros.css usan minmax(0, 1fr), width 100 % y aspect-ratio estable.
//
// Nota (RF-11.1): los textos visibles de esta sección (título "Ubicación",
// etiqueta "Dirección" y texto del enlace) son rótulos de interfaz, no datos
// de negocio; quedan marcados como PROVISIONALES hasta su validación.

interface BloqueUbicacionProps {
  id?: string;
}

export function BloqueUbicacion({ id = "ubicacion" }: BloqueUbicacionProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();
  const [abierto, setAbierto] = useState(() => estaDentroDelHorario());

  useEffect(() => {
    const intervalo = window.setInterval(
      () => setAbierto(estaDentroDelHorario()),
      60_000,
    );
    return () => window.clearInterval(intervalo);
  }, []);

  return (
    <section
      ref={ref}
      className={`seccion seccion--ubicacion revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado id={id} nivel={2} titulo="Ubicación" />

      <div className="ubicacion__panel">
        <div className="ubicacion__info">
          <p className="ubicacion__eyebrow">Visítanos</p>
          <h3 className="ubicacion__titulo">Nuestra sede</h3>

          <p className="ubicacion__linea">
            <MapPin size={20} aria-hidden="true" />
            <span>{DIRECCION}</span>
          </p>

          <p
            className={`ubicacion__estado ${
              abierto
                ? "ubicacion__estado--abierto"
                : "ubicacion__estado--cerrado"
            }`}
          >
            <span className="ubicacion__estado-punto" aria-hidden="true" />
            {abierto ? "Abierto ahora" : "Cerrado ahora"}
          </p>

          <p className="ubicacion__horario">
            <Clock size={20} aria-hidden="true" />
            <span>Horario: {HORARIO.texto}</span>
          </p>

          <a
            className="ubicacion__enlace"
            href={URL_GOOGLE_MAPS}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Navigation size={18} aria-hidden="true" />
            Abrir en Google Maps
            <span className="sr-only"> (se abre en una pestaña nueva)</span>
          </a>
        </div>

        <div className="ubicacion__mapa">
          <iframe
            className="ubicacion__iframe"
            src={URL_GOOGLE_MAPS_EMBED}
            title="Ubicación de Hidroemcol en Google Maps"
            loading="lazy"
          />
        </div>
      </div>
    </section>
  );
}
