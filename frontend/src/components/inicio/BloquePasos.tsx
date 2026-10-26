// Cuarta sección de la página de inicio: "Cómo funciona el servicio" (RF-6).
//
// PROVISIONAL: el contenido de esta sección es provisional y debe validarse
// contra el folleto transcrito y el proceso de negocio aprobado antes de dar la
// página por terminada (RF-6.3). El aviso es solo para el equipo de desarrollo y
// no se muestra al visitante.
import { m } from 'framer-motion'
import { SeccionEncabezado } from './SeccionEncabezado'
import type { Paso } from './contenido'
import { PASOS } from './contenido'
import { useRevelar } from '../../hooks/useRevelar'
import './inicio.css'

interface BloquePasosProps {
  pasos?: Paso[]
  id?: string
}

function PasoAnimado({ paso, indice }: { paso: Paso; indice: number }) {
  const revelar = useRevelar({ retraso: indice * 0.06 })

  return (
    <m.li className="paso" {...revelar}>
      <span className="paso__numero">{paso.numero}</span>
      <h3 className="paso__titulo">{paso.titulo}</h3>
      {paso.descripcion && <p className="paso__descripcion">{paso.descripcion}</p>}
    </m.li>
  )
}

export function BloquePasos({ pasos = PASOS, id = 'como-funciona' }: BloquePasosProps) {
  const revelarEncabezado = useRevelar()

  return (
    <section className="seccion seccion--pasos" aria-labelledby={id}>
      <m.div {...revelarEncabezado}>
        <SeccionEncabezado id={id} nivel={2} titulo="Cómo funciona el servicio" />
      </m.div>
      <ol className="pasos">
        {pasos.map((paso, i) => (
          <PasoAnimado paso={paso} indice={i} key={paso.numero} />
        ))}
      </ol>
    </section>
  )
}
