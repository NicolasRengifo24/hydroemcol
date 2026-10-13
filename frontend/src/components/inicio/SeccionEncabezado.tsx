import './inicio.css'

interface SeccionEncabezadoProps {
  titulo: string
  descripcion?: string
  nivel?: 2 | 3            // por defecto 2
  id?: string              // se aplica al elemento de encabezado, para aria-labelledby
  className?: string
}

export function SeccionEncabezado({
  titulo,
  descripcion,
  nivel = 2,
  id,
  className = '',
}: SeccionEncabezadoProps) {
  const classNameFinal = className ? `seccion__encabezado ${className}` : 'seccion__encabezado'
  const Encabezado = nivel === 3 ? 'h3' : 'h2'

  return (
    <div className={classNameFinal}>
      <Encabezado className="seccion__titulo" id={id}>
        {titulo}
      </Encabezado>
      {descripcion && <p className="seccion__intro">{descripcion}</p>}
    </div>
  )
}
