import { m } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import {
  Activity,
  AudioWaveform,
  Cog,
  Gauge,
  RotateCw,
  SlidersHorizontal,
  Thermometer,
  Zap,
} from "lucide-react";
import type { DatoBancoPruebas } from "./contenido";
import {
  DATOS_BANCO_PRUEBAS,
  TEXTO_BANCO_PRUEBAS,
  TITULO_BANCO_PRUEBAS,
} from "./contenido";
import { useRevelar } from "../../hooks/useRevelar";
import "./inicio.css";

const ICONOS_BANCO: LucideIcon[] = [
  Cog,
  Gauge,
  AudioWaveform,
  Activity,
  RotateCw,
  Thermometer,
  Zap,
  SlidersHorizontal,
];

interface DatoBancoAnimadoProps {
  dato: DatoBancoPruebas;
  indice: number;
  Icono: LucideIcon;
}

function DatoBancoAnimado({ dato, indice, Icono }: DatoBancoAnimadoProps) {
  const revelar = useRevelar({ retraso: 0.16 + indice * 0.055 });

  return (
    <m.li className="banco-hero__dato" {...revelar}>
      <span className="banco-hero__numero" aria-hidden="true">
        {String(indice + 1).padStart(2, "0")}
      </span>
      <span className="banco-hero__icono" aria-hidden="true">
        <Icono size={20} strokeWidth={1.8} />
      </span>
      <span className="banco-hero__dato-texto">
        {dato.valor && (
          <strong className="banco-hero__dato-valor">{dato.valor}</strong>
        )}
        <span className="banco-hero__dato-etiqueta">{dato.etiqueta}</span>
      </span>
      <span className="banco-hero__luz" aria-hidden="true" />
    </m.li>
  );
}

// Hero tecnológico que resume la instrumentación del banco de pruebas antes de
// mostrar los videos del banco.
export function BancoPruebasHero() {
  const revelarEyebrow = useRevelar();
  const revelarTitulo = useRevelar({ retraso: 0.06 });
  const revelarTexto = useRevelar({ retraso: 0.12 });

  return (
    <section className="banco-hero" aria-labelledby="banco-pruebas-hero">
      <img
        className="banco-hero__fondo"
        src="/img/foto-banco-de-prueba-1.jpeg"
        alt=""
        aria-hidden="true"
        loading="lazy"
        decoding="async"
      />
      <div className="banco-hero__velo" aria-hidden="true" />
      <div className="banco-hero__rejilla" aria-hidden="true" />
      <div className="banco-hero__barrido" aria-hidden="true" />

      <div className="banco-hero__contenido">
        <m.p className="banco-hero__eyebrow" {...revelarEyebrow}>
          <span className="banco-hero__pulso" aria-hidden="true" />
          Banco de pruebas
        </m.p>
        <m.h2
          id="banco-pruebas-hero"
          className="banco-hero__titulo"
          {...revelarTitulo}
        >
          {TITULO_BANCO_PRUEBAS}
        </m.h2>
        <m.p className="banco-hero__texto" {...revelarTexto}>
          {TEXTO_BANCO_PRUEBAS}
        </m.p>

        <ul className="banco-hero__datos">
          {DATOS_BANCO_PRUEBAS.map((dato, indice) => (
            <DatoBancoAnimado
              dato={dato}
              indice={indice}
              Icono={ICONOS_BANCO[indice] ?? Gauge}
              key={dato.etiqueta}
            />
          ))}
        </ul>
      </div>
    </section>
  );
}
