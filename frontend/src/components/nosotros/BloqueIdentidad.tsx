import { SeccionEncabezado } from "../inicio/SeccionEncabezado";
import { CITA_BRAD_HENRY, IDENTIDAD } from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 3 de la página Nosotros (RF-1.1): Misión, Visión y Valores en tres
// bloques escaneables (título + texto, RF-4.3) con los textos literales del
// folleto (RF-4.1), más la cita de Brad Henry como elemento diferenciado en
// banda oscura (RF-4.2). Un solo h2 por sección, provisto por
// SeccionEncabezado (RF-1.3); los títulos de cada bloque son h3, sin salto de
// nivel (RNF-3).

interface BloqueIdentidadProps {
  id?: string;
}

export function BloqueIdentidad({ id = "identidad" }: BloqueIdentidadProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion seccion--identidad revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado id={id} nivel={2} titulo="Misión, visión y valores" />

      <div className="identidad__rejilla">
        {IDENTIDAD.map((bloque) => (
          <article className="identidad__bloque" key={bloque.titulo}>
            <h3 className="identidad__titulo">{bloque.titulo}</h3>
            <p className="identidad__texto">{bloque.texto}</p>
          </article>
        ))}
      </div>

      <blockquote className="identidad__cita">
        <p className="identidad__cita-texto">{CITA_BRAD_HENRY.texto}</p>
        <cite className="identidad__cita-autor">— {CITA_BRAD_HENRY.autor}</cite>
      </blockquote>
    </section>
  );
}
