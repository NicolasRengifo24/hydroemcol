import { PARRAFOS_QUIENES_SOMOS } from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 2 de la página Nosotros (RF-1.1): presentación de la empresa con el
// texto literal de "Quiénes somos" (RF-3.1), tomado sin editar desde
// contenido.ts y marcado allí como PROVISIONAL hasta su validación (RF-11.1).
// No se añaden cifras, fechas ni datos de negocio no contenidos en el folleto
// (RF-3.2). El texto se presenta en una tarjeta sobre la imagen de la fachada,
// con un único h2 (RF-1.3).

interface BloqueQuienesSomosProps {
  id?: string;
}

export function BloqueQuienesSomos({
  id = "quienes-somos",
}: BloqueQuienesSomosProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion seccion--quienes revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <div className="quienes-hero">
        <img
          className="quienes-hero__fondo"
          src="/img/nosotros/fachada.jpg"
          alt=""
          aria-hidden="true"
          loading="lazy"
          decoding="async"
        />
        <div className="quienes-hero__velo" aria-hidden="true" />

        <div className="quienes-hero__contenido">
          <p className="quienes-hero__eyebrow">Nuestra empresa</p>
          <h2 id={id} className="quienes-hero__titulo">
            Quiénes somos
          </h2>
          {PARRAFOS_QUIENES_SOMOS.map((parrafo) => (
            <p className="quienes-somos__texto" key={parrafo}>
              {parrafo}
            </p>
          ))}
        </div>
      </div>
    </section>
  );
}
