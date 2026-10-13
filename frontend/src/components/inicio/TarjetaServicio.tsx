import { Link } from 'react-router-dom'
import './inicio.css'

interface TarjetaServicioProps {
  titulo: string
  descripcion: string
  animada?: boolean               // por defecto false
  indice?: number                 // retardo de la animación escalonada
  variante?: 'hero' | 'destacado' // por defecto 'hero'
  to?: string                     // OPCIONAL y PREPARADA PARA EL FUTURO: si se indica, la tarjeta se renderiza como enlace; si no, como contenido informativo no navegable
  nivel?: 2 | 3                   // por defecto 3; el hero pasa 2 para no saltar niveles tras el h1 (RNF-4)
}

export function TarjetaServicio({
  titulo,
  descripcion,
  animada = false,
  indice,
  variante = 'hero',
  to,
  nivel = 3,
}: TarjetaServicioProps) {
  const clases = ['tarjeta']
  if (variante === 'hero') {
    clases.push('tarjeta--hero')
  } else {
    clases.push('tarjeta--destacado')
  }
  if (animada) {
    clases.push('tarjeta--animada')
  }

  const className = clases.join(' ')

  const Encabezado = nivel === 2 ? 'h2' : 'h3'

  const contenido = (
    <>
      <Encabezado className="tarjeta__titulo">{titulo}</Encabezado>
      <p className="tarjeta__descripcion">{descripcion}</p>
    </>
  )

  if (to) {
    return (
      <article
        className={className}
        style={
          animada && indice !== undefined
            ? { animationDelay: `${indice * 80}ms` }
            : undefined
        }
      >
        <Link to={to} className="tarjeta__enlace">
          {contenido}
        </Link>
      </article>
    )
  }

  return (
    <article
      className={className}
      style={
        animada && indice !== undefined
          ? { animationDelay: `${indice * 80}ms` }
          : undefined
      }
    >
      {contenido}
    </article>
  )
}
