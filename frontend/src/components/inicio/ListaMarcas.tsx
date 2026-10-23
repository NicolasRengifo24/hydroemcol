import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import type { Marca } from "./contenido";
import "./inicio.css";

interface ListaMarcasProps {
  marcas: Marca[];
  className?: string;
}

export function ListaMarcas({ marcas, className = "" }: ListaMarcasProps) {
  const classNameFinal = className ? `marcas ${className}` : "marcas";
  const carruselRef = useRef<HTMLUListElement>(null);

  function desplazar(direccion: number) {
    carruselRef.current?.scrollBy({
      left: direccion * Math.max(carruselRef.current.clientWidth * 0.72, 220),
      behavior: "smooth",
    });
  }

  return (
    <div className="marcas__carrusel" role="region" aria-label="Marcas con las que trabajamos">
      <button className="marcas__control" type="button" onClick={() => desplazar(-1)} aria-label="Ver marcas anteriores">
        <ChevronLeft size={20} aria-hidden="true" />
      </button>
      <ul ref={carruselRef} className={classNameFinal}>
        {marcas.map((marca) => (
          <li key={marca.nombre} className="marcas__item">
            {marca.logo && (
              <img
                src={marca.logo}
                alt={marca.nombre}
                loading="lazy"
                decoding="async"
                className="marcas__logo"
              />
            )}
          </li>
        ))}
      </ul>
      <button className="marcas__control" type="button" onClick={() => desplazar(1)} aria-label="Ver marcas siguientes">
        <ChevronRight size={20} aria-hidden="true" />
      </button>
    </div>
  );
}
