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
        <details className="capacidad__bloque">
          <summary className="capacidad__subtitulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <Cog size={20} strokeWidth={1.9} />
            </span>
            Componentes que atendemos
          </summary>
          <ul className="lista lista--componentes">
            {componentes.map((componente) => (
              <li key={componente} className="lista__item">
                {componente}
              </li>
            ))}
          </ul>
        </details>
        <details className="capacidad__bloque">
          <summary className="capacidad__subtitulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <Gauge size={20} strokeWidth={1.9} />
            </span>
            Capacidad técnica
          </summary>
          <ul className="lista lista--capacidades">
            {capacidades.map((capacidad) => (
              <li key={capacidad} className="lista__item">
                {capacidad}
              </li>
            ))}
          </ul>
        </details>
        <section className="capacidad__marcas" aria-labelledby="marcas-titulo">
          <div className="capacidad__subtitulo" id="marcas-titulo">
            <span
              className="tarjeta__icono tarjeta__icono--linea"
              aria-hidden="true"
            >
              <BadgeCheck size={20} strokeWidth={1.9} />
            </span>
            Trabajamos Con Las Mejores Marcas Del Mercado
          </div>
          <ListaMarcas marcas={marcas} />
        </section>
      </div>
      <div className="inicio-videos" aria-label="Capacidad audiovisual">
        <section className="video-hero video-hero--izquierda">
          <BloqueVideo
            titulo="Nuestro banco de pruebas"
            descripcion="Diagnóstico y pruebas técnicas para validar el comportamiento de componentes hidráulicos."
            src="/vid/video-banco-prueba.mp4"
            poster="/img/foto-banco-de-prueba-2.jpeg"
          />
          <div className="video-hero__texto">
            <p className="video-hero__eyebrow">Precisión en cada diagnóstico</p>
            <h3>Probamos antes de entregar</h3>
            <p>Un proceso técnico orientado a encontrar fallas, validar reparaciones y entregar información clara.</p>
          </div>
        </section>
        <section className="video-hero video-hero--derecha">
          <div className="video-hero__texto">
            <p className="video-hero__eyebrow">Control y desempeño</p>
            <h3>Capacidad para sistemas exigentes</h3>
            <p>Evaluamos componentes hidráulicos para apoyar decisiones de mantenimiento con evidencia técnica.</p>
          </div>
          <BloqueVideo
            titulo="Motor de traslación en el banco de pruebas"
            descripcion="Observación del funcionamiento del componente durante la prueba."
            src="/vid/motor-translasion-editado.mp4"
            poster="/img/foto-banco-de-prueba-3.jpeg"
          />
        </section>
      </div>
    </section>
  );
}
