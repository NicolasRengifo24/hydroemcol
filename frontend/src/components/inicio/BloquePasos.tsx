// Cuarta sección de la página de inicio: "Cómo funciona el servicio" (RF-6).
//
// PROVISIONAL: el contenido de esta sección es provisional y debe validarse
// contra el folleto transcrito y el proceso de negocio aprobado antes de dar la
// página por terminada (RF-6.3). El aviso es solo para el equipo de desarrollo y
// no se muestra al visitante.
import { SeccionEncabezado } from './SeccionEncabezado'
import type { Paso } from './contenido'
import { PASOS } from './contenido'
import { useAparecerAlEntrar } from '../../hooks/useAparecerAlEntrar'
import './inicio.css'

interface BloquePasosProps {
  pasos?: Paso[]
  id?: string
}

export function BloquePasos({ pasos = PASOS, id = 'como-funciona' }: BloquePasosProps) {
  const { ref, visible } = useAparecerAlEntrar<HTMLElement>()

  return (
    <section
      ref={ref}
      className={`seccion seccion--pasos revelar${visible ? ' revelar--visible' : ''}`}
      aria-labelledby={id}
    >
      <SeccionEncabezado id={id} nivel={2} titulo="Cómo funciona el servicio" />
      <ol className="pasos">
        {pasos.map((paso) => (
          <li className="paso" key={paso.numero}>
            <span className="paso__numero">{paso.numero}</span>
            <h3 className="paso__titulo">{paso.titulo}</h3>
            {paso.descripcion && <p className="paso__descripcion">{paso.descripcion}</p>}
          </li>
        ))}
      </ol>
    </section>
  )
}
