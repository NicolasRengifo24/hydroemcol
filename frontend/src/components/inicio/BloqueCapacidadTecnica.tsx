import { m } from "framer-motion";
import { BadgeCheck, Cog, Gauge } from "lucide-react";
import { SeccionEncabezado } from "./SeccionEncabezado";
import { ListaMarcas } from "./ListaMarcas";
import { BancoPruebasHero } from "./BancoPruebasHero";
import { BloqueVideo } from "./BloqueVideo";
import type { Marca } from "./contenido";
import {
  COMPONENTES_ATENDIDOS,
  CAPACIDADES_TECNICAS,
  MARCAS,
} from "./contenido";
import { useRevelar } from "../../hooks/useRevelar";
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
  const revelarEncabezado = useRevelar();
  const revelarComponentes = useRevelar({ direccion: "izquierda" });
  const revelarCapacidad = useRevelar({ direccion: "derecha", retraso: 0.06 });
  const revelarMarcas = useRevelar({ retraso: 0.1 });
  const revelarVideoIzquierda = useRevelar({ direccion: "izquierda" });
  const revelarVideoDerecha = useRevelar({ direccion: "derecha" });

  return (
    <section className="seccion seccion--capacidad" aria-labelledby={id}>
      <m.div {...revelarEncabezado}>
        <SeccionEncabezado
          id={id}
          nivel={2}
          titulo="Componentes y capacidad técnica"
        />
      </m.div>
      <div className="capacidad__contenido">
        <m.details className="capacidad__bloque" {...revelarComponentes}>
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
        </m.details>
        <m.details className="capacidad__bloque" {...revelarCapacidad}>
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
        </m.details>
        <m.section
          className="capacidad__marcas"
          aria-labelledby="marcas-titulo"
          {...revelarMarcas}
        >
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
        </m.section>
      </div>
      <BancoPruebasHero />
      <div className="inicio-videos" aria-label="Capacidad audiovisual">
        <m.section
          className="video-hero video-hero--izquierda"
          {...revelarVideoIzquierda}
        >
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
        </m.section>
        <m.section
          className="video-hero video-hero--derecha"
          {...revelarVideoDerecha}
        >
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
        </m.section>
      </div>
    </section>
  );
}
