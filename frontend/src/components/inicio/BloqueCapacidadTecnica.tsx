import { BadgeCheck, Cog, Gauge } from "lucide-react";
import { SeccionEncabezado } from "./SeccionEncabezado";
import { ListaMarcas } from "./ListaMarcas";
import { BloqueVideo } from "./BloqueVideo";
import type { Marca } from "./contenido";
import {
  COMPONENTES_ATENDIDOS,
  CAPACIDADES_TECNICAS,
  MARCAS,
} from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./inicio.css";

interface BloqueCapacidadTecnicaProps {
  componentes?: string[]; // por defecto COMPONENTES_ATENDIDOS
  capacidades?: string[]; // por defecto CAPACIDADES_TECNICAS
  marcas?: Marca[]; // por defecto MARCAS
  id?: string; // por defecto 'capacidad-tecnica'
}

export function BloqueCapacidadTecnica({
  componentes = COMPONENTES_ATENDIDOS,
  capacidades = CAPACIDADES_TECNICAS,
  marcas = MARCAS,
  id = "capacidad-tecnica",
}: BloqueCapacidadTecnicaProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion seccion--capacidad revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado
        id={id}
        nivel={2}
        titulo="Componentes y capacidad técnica"
      />
      <div className="capacidad__contenido">
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <Cog size={20} strokeWidth={1.9} />
            </span>
            Componentes que atendemos
          </h3>
          <ul className="lista lista--componentes">
            {componentes.map((componente) => (
              <li key={componente} className="lista__item">
                {componente}
              </li>
            ))}
          </ul>
        </div>
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <Gauge size={20} strokeWidth={1.9} />
            </span>
            Capacidad técnica
          </h3>
          <ul className="lista lista--capacidades">
            {capacidades.map((capacidad) => (
              <li key={capacidad} className="lista__item">
                {capacidad}
              </li>
            ))}
          </ul>
        </div>
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <BadgeCheck size={20} strokeWidth={1.9} />
            </span>
            Trabajamos Con Las Mejores Marcas Del Mercado
          </h3>
          <ListaMarcas marcas={marcas} />
        </div>
        <div className="capacidad__bloque">
          <BloqueVideo
            titulo="Nuestro Banco De Pruebas"
            src="/vid/video-banco-prueba.mp4"
            poster="/img/foto-banco-de-prueba-2.jpeg"
          />
          <BloqueVideo
            titulo="Motor de traslación en el banco de pruebas"
            src="/vid/motor-translasion-editado.mp4"
            poster="/img/foto-banco-de-prueba-3.jpeg"
          />
        </div>
      </div>
    </section>
  );
}
