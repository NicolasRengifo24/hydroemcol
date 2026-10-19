import type { LucideIcon } from "lucide-react";
import { Cog, Cpu, Gauge, Globe, Package, Wrench } from "lucide-react";
import { SeccionEncabezado } from "../inicio/SeccionEncabezado";
import { CAPACIDADES_TECNICAS } from "../inicio/contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 4 de la página Nosotros (RF-1.1): capacidades técnicas reutilizadas
// desde components/inicio/contenido.ts SIN copia local (RF-5.2), en formato de
// filas editoriales con icono lateral (D-3 / D-P8): icono + título + descripción,
// separadores sutiles, sin bordes ni fondos de tarjeta como en Inicio (RF-5.1).
// Un solo h2 por sección, provisto por SeccionEncabezado (RF-1.3); los títulos
// de cada fila son h3, sin salto de nivel (RNF-3).
//
// Título y descripción: CAPACIDADES_TECNICAS es string[] y cada entrada es una
// frase única, no un par título/descripción. Para cumplir el formato editorial
// SIN alterar el texto (RF-5.2), cada string se parte en el render sobre el
// primer separador natural que encuentre, en este orden: ", ", " para ", " de ".
// El separador no se repite en la descripción porque título y descripción son
// elementos visuales distintos, no una frase continua: se conservan íntegras
// todas las palabras del string original, sin reescritura ni recorte de sentido.
// Si un string no contiene ningún separador (p. ej. "Pruebas en banco"), el
// string completo es el título y la fila se renderiza sin descripción.
//
// Iconos: lucide-react (dependencia ya instalada), decorativos (aria-hidden),
// de la misma identidad industrial que Inicio. El orden acompaña el orden de
// CAPACIDADES_TECNICAS; si la lista cambia, este mapa se ajusta en el mismo
// commit. Fallback Cog para índices fuera de rango.

const SEPARADORES = [", ", " para ", " de "];

function partirCapacidad(texto: string): {
  titulo: string;
  descripcion?: string;
} {
  for (const separador of SEPARADORES) {
    const corte = texto.indexOf(separador);
    if (corte > 0) {
      return {
        titulo: texto.slice(0, corte),
        descripcion: texto.slice(corte + separador.length),
      };
    }
  }
  return { titulo: texto };
}

const ICONOS_CAPACIDADES: LucideIcon[] = [
  Gauge, // Pruebas en banco
  Wrench, // Diagnóstico y reparación
  Cog, // Control proporcional y sistemas de control
  Package, // Suministro de repuestos
  Globe, // Importación sobre pedido
  Cpu, // Asesoría e implementación de sistemas
];

interface BloqueCapacidadesProps {
  id?: string;
}

export function BloqueCapacidades({
  id = "capacidades",
}: BloqueCapacidadesProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>();

  return (
    <section
      ref={ref}
      className={`seccion seccion--capacidades revelar${visible ? " revelar--visible" : ""}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado id={id} nivel={2} titulo="Capacidades técnicas" />

      <ul className="capacidades">
        {CAPACIDADES_TECNICAS.map((capacidad, indice) => {
          const { titulo, descripcion } = partirCapacidad(capacidad);
          const Icono = ICONOS_CAPACIDADES[indice] ?? Cog;

          return (
            <li key={capacidad} className="capacidad-fila">
              <span className="capacidad-fila__icono" aria-hidden="true">
                <Icono size={22} strokeWidth={1.9} />
              </span>
              <h3 className="capacidad-fila__titulo">{titulo}</h3>
              {descripcion && (
                <p className="capacidad-fila__texto">{descripcion}</p>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
