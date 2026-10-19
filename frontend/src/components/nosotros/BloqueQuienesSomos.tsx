import { SeccionEncabezado } from "../inicio/SeccionEncabezado";
import { TEXTO_QUIENES_SOMOS } from "./contenido";
import { useAparecerAlEntrar } from "../../hooks/useAparecerAlEntrar";
import "./nosotros.css";

// Sección 2 de la página Nosotros (RF-1.1): presentación de la empresa con el
// párrafo literal de "Quiénes somos" (RF-3.1), tomado sin editar desde
// contenido.ts y marcado allí como PROVISIONAL hasta su validación (RF-11.1).
// No se añaden cifras, fechas ni datos de negocio no contenidos en el folleto
// (RF-3.2). Un solo h2 por sección, provisto por SeccionEncabezado (RF-1.3).

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
      <SeccionEncabezado id={id} nivel={2} titulo="Quiénes somos" />
      <p className="quienes-somos__texto">{TEXTO_QUIENES_SOMOS}</p>
    </section>
  );
}
