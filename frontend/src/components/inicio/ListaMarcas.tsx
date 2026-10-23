import { useEffect, useRef, useState } from "react";
import type { Marca } from "./contenido";
import "./inicio.css";

interface ListaMarcasProps {
  marcas: Marca[];
  className?: string;
}

export function ListaMarcas({ marcas, className = "" }: ListaMarcasProps) {
  const classNameFinal = className ? `marcas ${className}` : "marcas";
  const carruselRef = useRef<HTMLUListElement>(null);
  const [pausado, setPausado] = useState(false);

  useEffect(() => {
    const carrusel = carruselRef.current;
    if (!carrusel || marcas.length < 2) return;

    const reducirMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducirMovimiento) return;

    const temporizador = window.setInterval(() => {
      if (pausado) return;
      const limite = carrusel.scrollWidth - carrusel.clientWidth;
      if (carrusel.scrollLeft >= limite - 1) {
        carrusel.scrollLeft = 0;
        return;
      }
      carrusel.scrollLeft += 0.7;
    }, 30);

    return () => window.clearInterval(temporizador);
  }, [marcas.length, pausado]);

  return (
    <div
      className="marcas__carrusel"
      role="region"
      aria-label="Marcas con las que trabajamos"
      onMouseEnter={() => setPausado(true)}
      onMouseLeave={() => setPausado(false)}
      onFocus={() => setPausado(true)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setPausado(false);
      }}
    >
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
    </div>
  );
}
