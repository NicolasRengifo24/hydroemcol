import { Cog, Factory, Ship, Zap } from "lucide-react";
import { SeccionEncabezado } from "./SeccionEncabezado";
import { TarjetaServicio } from "./TarjetaServicio";
import type { ServicioDestacado } from "./contenido";
import { SERVICIOS_DESTACADOS } from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./inicio.css";

// Iconos decorativos de los cuatro bloques, en el orden de SERVICIOS_DESTACADOS.
const ICONOS = [Cog, Ship, Zap, Factory];

interface BloqueServiciosDestacadosProps {
  servicios?: ServicioDestacado[];
  id?: string;
}

export function BloqueServiciosDestacados({
  servicios = SERVICIOS_DESTACADOS,
  id = "servicios-destacados",
}: BloqueServiciosDestacadosProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion seccion--servicios revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado id={id} nivel={2} titulo="Productos y servicios" />
      <div className="rejilla rejilla--destacados">
        {servicios.map((servicio, i) => {
          const Icono = ICONOS[i];
          return servicio.titulo === "Importación Sobre Pedido" ? (
            <article
              className="tarjeta tarjeta--destacado tarjeta--importacion"
              key={servicio.titulo}
            >
              <span className="tarjeta__icono" aria-hidden="true">
                <Icono size={22} strokeWidth={1.9} />
              </span>
              <h3 className="tarjeta__titulo">{servicio.titulo}</h3>
              <p className="tarjeta__descripcion">{servicio.descripcion}</p>
            </article>
          ) : (
            <TarjetaServicio
              key={servicio.titulo}
              titulo={servicio.titulo}
              descripcion={servicio.descripcion}
              variante="destacado"
              icono={Icono}
            />
          );
        })}
      </div>
    </section>
  );
}
