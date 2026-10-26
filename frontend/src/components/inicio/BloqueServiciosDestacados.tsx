import { Cog, Ship, Zap } from "lucide-react";
import { m } from "framer-motion";
import { TarjetaServicio } from "./TarjetaServicio";
import { SeccionEncabezado } from "./SeccionEncabezado";
import type { ServicioDestacado } from "./contenido";
import { SERVICIOS_DESTACADOS } from "./contenido";
import { useRevelar } from "../../hooks/useRevelar";
import "./inicio.css";

// Iconos decorativos de los bloques, en el orden de SERVICIOS_DESTACADOS.
const ICONOS = [Cog, Ship, Zap];

interface BloqueServiciosDestacadosProps {
  servicios?: ServicioDestacado[];
  id?: string;
}

export function BloqueServiciosDestacados({
  servicios = SERVICIOS_DESTACADOS,
  id = "servicios-destacados",
}: BloqueServiciosDestacadosProps) {
  const revelarCabecera = useRevelar({ direccion: "arriba" });

  return (
    <section className="seccion seccion--servicios" aria-labelledby={id}>
      <m.div className="servicios-destacados__cabecera" {...revelarCabecera}>
        <div>
          <p className="servicios-destacados__eyebrow">
            Repuestos · Importación · Servicio técnico
          </p>
          <SeccionEncabezado
            id={id}
            nivel={2}
            titulo="Productos y servicios"
            descripcion="Repuestos OEM, importación sobre pedido y servicio técnico electrohidráulico para mantener tu operación activa."
          />
        </div>
        <ul className="servicios-destacados__datos" aria-hidden="true">
          <li>
            <strong>03</strong>
            <span>Líneas integradas</span>
          </li>
          <li>
            <strong>OEM</strong>
            <span>Repuestos originales</span>
          </li>
          <li>
            <strong>Nacional</strong>
            <span>Cobertura</span>
          </li>
        </ul>
      </m.div>
      <div className="rejilla rejilla--destacados rejilla--bento">
        {servicios.map((servicio, i) => {
          const Icono = ICONOS[i];
          return (
            <TarjetaServicio
              key={servicio.titulo}
              titulo={servicio.titulo}
              descripcion={servicio.descripcion}
              variante="destacado"
              animada
              indice={i}
              icono={Icono}
              claseExtra={
                servicio.titulo === "Importación Sobre Pedido"
                  ? "tarjeta--importacion"
                  : undefined
              }
            />
          );
        })}
      </div>
    </section>
  );
}
