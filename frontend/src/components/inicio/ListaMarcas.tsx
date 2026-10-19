import type { Marca } from "./contenido";
import "./inicio.css";

interface ListaMarcasProps {
  marcas: Marca[];
  className?: string;
}

export function ListaMarcas({ marcas, className = "" }: ListaMarcasProps) {
  const classNameFinal = className ? `marcas ${className}` : "marcas";

  return (
    <ul className={classNameFinal}>
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
  );
}
