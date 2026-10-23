import type { LucideIcon } from "lucide-react";
import { Eye, HeartHandshake, Target } from "lucide-react";
import { SeccionEncabezado } from "../inicio/SeccionEncabezado";
import { CITA_BRAD_HENRY, IDENTIDAD } from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

const ICONOS_IDENTIDAD: LucideIcon[] = [Target, Eye, HeartHandshake];

const IMAGENES_IDENTIDAD = [
  "/img/nosotros/vitrina.jpg",
  "/img/soluciones/hero-servicios.png",
  "/img/nosotros/fachada.jpg",
];

const VARIANTES_IDENTIDAD = ["mision", "vision", "valores"];

// Sección 3 de la página Nosotros (RF-1.1): Misión, Visión y Valores en tres
// paneles tipo hero (título + texto, RF-4.3) con los textos literales del
// folleto (RF-4.1). La tarjeta de texto alterna de lado en cada panel y usa
// una imagen de fondo distinta. Se mantiene la cita de Brad Henry como elemento
// diferenciado en banda oscura (RF-4.2). Un solo h2 por sección, provisto por
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

      <div className="identidad__paneles">
        {IDENTIDAD.map((bloque, indice) => {
          const Icono = ICONOS_IDENTIDAD[indice] ?? Target;
          const variante = VARIANTES_IDENTIDAD[indice] ?? "mision";

          return (
            <article
              className={`identidad-hero identidad-hero--${variante}${
                indice % 2 === 1 ? " identidad-hero--derecha" : ""
              }`}
              key={bloque.titulo}
            >
              <img
                className="identidad-hero__fondo"
                src={IMAGENES_IDENTIDAD[indice]}
                alt=""
                aria-hidden="true"
                loading="lazy"
                decoding="async"
              />
              <div className="identidad-hero__velo" aria-hidden="true" />

              <div className="identidad-hero__contenido">
                <span className="identidad-hero__icono" aria-hidden="true">
                  <Icono size={22} strokeWidth={1.9} />
                </span>
                <h3 className="identidad-hero__titulo">{bloque.titulo}</h3>
                <p className="identidad-hero__texto">{bloque.texto}</p>
              </div>
            </article>
          );
        })}
      </div>

      <blockquote className="identidad__cita">
        <p className="identidad__cita-texto">{CITA_BRAD_HENRY.texto}</p>
        <cite className="identidad__cita-autor">— {CITA_BRAD_HENRY.autor}</cite>
      </blockquote>
    </section>
  );
}
