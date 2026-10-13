import { SeccionEncabezado } from './SeccionEncabezado'
import { ListaMarcas } from './ListaMarcas'
import { BloqueVideo } from './BloqueVideo'
import type { Marca } from './contenido'
import {
  COMPONENTES_ATENDIDOS,
  CAPACIDADES_TECNICAS,
  MARCAS,
} from './contenido'
import './inicio.css'

interface BloqueCapacidadTecnicaProps {
  componentes?: string[] // por defecto COMPONENTES_ATENDIDOS
  capacidades?: string[] // por defecto CAPACIDADES_TECNICAS
  marcas?: Marca[] // por defecto MARCAS
  id?: string // por defecto 'capacidad-tecnica'
}

export function BloqueCapacidadTecnica({
  componentes = COMPONENTES_ATENDIDOS,
  capacidades = CAPACIDADES_TECNICAS,
  marcas = MARCAS,
  id = 'capacidad-tecnica',
}: BloqueCapacidadTecnicaProps) {
  return (
    <section className="seccion seccion--capacidad" aria-labelledby={id}>
      <SeccionEncabezado
        id={id}
        nivel={2}
        titulo="Componentes y capacidad técnica"
      />
      <div className="capacidad__contenido">
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">Componentes que atendemos</h3>
          <ul className="lista lista--componentes">
            {componentes.map((componente) => (
              <li key={componente} className="lista__item">
                {componente}
              </li>
            ))}
          </ul>
        </div>
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">Capacidad técnica</h3>
          <ul className="lista lista--capacidades">
            {capacidades.map((capacidad) => (
              <li key={capacidad} className="lista__item">
                {capacidad}
              </li>
            ))}
          </ul>
        </div>
        <div className="capacidad__bloque">
          <h3 className="capacidad__subtitulo">Marcas que atendemos</h3>
          <ListaMarcas marcas={marcas} />
        </div>
        <div className="capacidad__bloque">
          <BloqueVideo
            titulo="Pieza montada en el banco de pruebas"
            src="/vid/video-banco-prueba.mp4"
          />
        </div>
      </div>
    </section>
  )
}
